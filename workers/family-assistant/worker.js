// Family-history AI assistant for the Four Rivers site (juanarmond.github.io).
//
// A Cloudflare Worker that answers natural-language questions about the family
// tree using Google Gemini, grounded ONLY in this repository's data. It is a
// stateless RAG proxy — the Gemini API key lives here as a Worker secret and is
// never exposed to the browser.
//
// Per request (POST /  body: { question, lang }):
//   1. Load the knowledge base + name index from the public Pages site (edge-cached).
//   2. Resolve the people/documents the question mentions to IDs.
//   3. For a two-person "how are X and Y related?" question, compute the exact
//      relationship path deterministically (BFS over the family graph) so the model
//      narrates a verified path instead of hallucinating one.
//   4. Fetch the full Tier B records (profiles + document transcriptions) for just
//      those entities.
//   5. Ask Gemini (2.5 Flash, falling back to 2.0 Flash-Lite on quota) and stream
//      the answer back as plain text.
//
// Privacy: the knowledge base is built with the same living-person filter as the
// public site (P-0001/2/3 and their documents are excluded), so nothing private is
// reachable here. The system prompt additionally forbids speculation about the living.

const ALLOW_ORIGIN = "https://juanarmond.github.io";
const KB_BASE = "https://juanarmond.github.io/armond-family-history/kb/";

// Default model first, quota fallback second. Verify these IDs remain on the free
// tier at ai.google.dev/gemini-api/docs/rate-limits — Google rotates them.
const MODELS = ["gemini-2.5-flash", "gemini-2.0-flash-lite"];

const MAX_QUESTION_CHARS = 2000;
const MAX_PEOPLE = 6; // Tier B person files fetched per query
const MAX_SOURCES = 8; // Tier B source files fetched per query
const AMBIGUOUS_TOKEN_MAX = 4; // skip a name token shared by more than this many people

function corsHeaders(request) {
  const origin = request.headers.get("Origin") || "";
  return {
    "Access-Control-Allow-Origin": origin === ALLOW_ORIGIN ? origin : ALLOW_ORIGIN,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

function normalize(text) {
  return text
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();
}

// Edge-cached GET: Cloudflare caches the Pages response at the edge for an hour, so
// the ~230KB knowledge base is not refetched from GitHub on every question.
function cachedFetch(url) {
  return fetch(url, { cf: { cacheTtl: 3600, cacheEverything: true } });
}

async function fetchJson(url) {
  const res = await cachedFetch(url);
  if (!res.ok) return null;
  try {
    return await res.json();
  } catch {
    return null;
  }
}

// Resolve the people a question refers to, in priority order:
// explicit P-IDs → exact indexed name phrases → single-word name tokens.
function resolvePeople(question, nameIndex) {
  const ordered = [];
  const seen = new Set();
  const push = (pid) => {
    if (pid && !seen.has(pid)) {
      seen.add(pid);
      ordered.push(pid);
    }
  };

  for (const m of question.matchAll(/\bP-\d{4}\b/g)) push(m[0]);

  const norm = normalize(question);

  // Exact full-name / variant phrases (highest confidence). Longest names first so
  // "iris bohrer muniz" wins over the bare "iris" token.
  const names = Object.keys(nameIndex.names || {}).sort((a, b) => b.length - a.length);
  for (const name of names) {
    if (name.length >= 4 && norm.includes(name)) {
      for (const pid of nameIndex.names[name]) push(pid);
    }
  }

  // Single-word tokens (given names / surnames). Skip very ambiguous ones.
  const words = norm.split(/[^a-z0-9]+/).filter((w) => w.length >= 3);
  const tokenScore = new Map();
  for (const w of words) {
    const pids = (nameIndex.tokens || {})[w];
    if (pids && pids.length <= AMBIGUOUS_TOKEN_MAX) {
      for (const pid of pids) tokenScore.set(pid, (tokenScore.get(pid) || 0) + 1);
    }
  }
  for (const [pid] of [...tokenScore.entries()].sort((a, b) => b[1] - a[1])) push(pid);

  return ordered;
}

function resolveSources(question) {
  const ids = new Set();
  for (const m of question.matchAll(/\b(?:CIV|GOV|PAR|PRB|NWS|PUB|REC)-\d{4}\b/g)) {
    ids.add(m[0]);
  }
  return [...ids];
}

// Build an undirected relationship graph from the family records and BFS the shortest
// path between two people. Nodes that are not public people (i.e. living) are not
// traversable, so a path never runs through or exposes a living person.
function buildAdjacency(kb) {
  const adj = new Map();
  const link = (a, b, rel) => {
    if (!kb.people[a] || !kb.people[b]) return; // skip living / unknown
    if (!adj.has(a)) adj.set(a, []);
    adj.get(a).push({ to: b, rel });
  };
  for (const fam of Object.values(kb.families || {})) {
    const partners = fam.partners || [];
    const children = fam.children || [];
    for (let i = 0; i < partners.length; i++) {
      for (let j = i + 1; j < partners.length; j++) {
        link(partners[i], partners[j], "spouse");
        link(partners[j], partners[i], "spouse");
      }
    }
    for (const child of children) {
      for (const parent of partners) {
        link(parent, child, "parent-of");
        link(child, parent, "child-of");
      }
    }
  }
  return adj;
}

function relationshipPath(kb, startId, goalId) {
  const adj = buildAdjacency(kb);
  const queue = [[startId]];
  const seen = new Set([startId]);
  while (queue.length) {
    const path = queue.shift();
    const node = path[path.length - 1];
    if (node === goalId) {
      // Annotate each hop as "Name —rel→ Name".
      const parts = [];
      for (let i = 0; i < path.length; i++) {
        const p = kb.people[path[i]];
        const name = p ? p.name : path[i];
        if (i > 0) {
          const edge = (adj.get(path[i - 1]) || []).find((e) => e.to === path[i]);
          parts.push(` --${edge ? edge.rel : "?"}--> `);
        }
        parts.push(`${name} (${path[i]})`);
      }
      return parts.join("");
    }
    for (const { to } of adj.get(node) || []) {
      if (!seen.has(to)) {
        seen.add(to);
        queue.push([...path, to]);
      }
    }
  }
  return null;
}

const RELATIONAL_RE =
  /\b(related|relation|relationship|connected|descend|ancestor|parente|parentes|relacionad|relaç[aã]o|conex[aã]o)\b/i;

const SYSTEM_PROMPT = `You are the genealogy assistant for the Armond ("Four Rivers") family history project.
Answer strictly from the FAMILY DATA and FULL RECORDS provided in the user message — this is a
documented family history, not general knowledge.

Rules:
- Never invent people, dates, places or relationships. If the data does not answer the question,
  say so plainly and suggest what record would settle it.
- Do not reveal or speculate about living people. Living relatives are deliberately absent from the
  data; if asked about someone not present, say you only cover documented (deceased) family members.
- Cite the record ID when you assert a fact from a document (e.g. "per PAR-0076").
- When a COMPUTED RELATIONSHIP PATH is given, it was derived deterministically from the records —
  treat it as authoritative and put it into plain words; never recompute or contradict it.
- Answer in the user's language (Portuguese or English). Be clear and complete but not padded.`;

function buildUserContent(kb, question, lang, path, people, sources) {
  const blocks = [];
  blocks.push(
    "--- FAMILY DATA (every person summary, document descriptor, family and event) ---",
  );
  blocks.push(JSON.stringify(kb));
  blocks.push("\n--- COMPUTED RELATIONSHIP PATH ---");
  blocks.push(path || "(not a two-person relationship question — use the family graph above)");
  blocks.push("\n--- FULL RECORDS RELEVANT TO THIS QUESTION ---");
  blocks.push("People:");
  blocks.push(people.length ? JSON.stringify(people) : "(none resolved)");
  blocks.push("Documents:");
  blocks.push(sources.length ? JSON.stringify(sources) : "(none resolved)");
  blocks.push(`\n--- QUESTION (${lang === "pt" ? "Portuguese" : "English"}) ---`);
  blocks.push(question);
  return blocks.join("\n");
}

// Stream Gemini's SSE response, extracting only the text deltas, and pipe them to the
// browser as plain UTF-8 text. Tries each model in turn; a 429/503 falls through to the
// next (2.5 Flash → 2.0 Flash-Lite) before any bytes are streamed.
async function streamGemini(apiKey, userContent) {
  const body = JSON.stringify({
    system_instruction: { parts: [{ text: SYSTEM_PROMPT }] },
    contents: [{ role: "user", parts: [{ text: userContent }] }],
    generationConfig: { temperature: 0.2, maxOutputTokens: 2048 },
  });

  let upstream = null;
  for (const model of MODELS) {
    const url =
      `https://generativelanguage.googleapis.com/v1beta/models/${model}:streamGenerateContent` +
      `?alt=sse&key=${apiKey}`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });
    if (res.ok) {
      upstream = res;
      break;
    }
    if (res.status !== 429 && res.status !== 503) {
      const detail = await res.text();
      throw new Error(`Gemini ${model} error ${res.status}: ${detail.slice(0, 300)}`);
    }
    // else: quota/overload — try the next model
  }
  if (!upstream) throw new Error("All models rate-limited (429). Try again shortly.");

  const encoder = new TextEncoder();
  const decoder = new TextDecoder();
  const reader = upstream.body.getReader();
  let buffer = "";

  return new ReadableStream({
    async pull(controller) {
      const { done, value } = await reader.read();
      if (done) {
        controller.close();
        return;
      }
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("data:")) continue;
        const payload = trimmed.slice(5).trim();
        if (!payload || payload === "[DONE]") continue;
        try {
          const json = JSON.parse(payload);
          const parts = json.candidates?.[0]?.content?.parts || [];
          for (const part of parts) {
            if (part.text) controller.enqueue(encoder.encode(part.text));
          }
        } catch {
          // ignore keep-alives / partial JSON
        }
      }
    },
    cancel() {
      reader.cancel();
    },
  });
}

// Named exports for offline unit testing of the deterministic retrieval/BFS logic.
// The Cloudflare runtime only ever calls the default export's fetch(); these are inert there.
export { normalize, resolvePeople, resolveSources, buildAdjacency, relationshipPath };

export default {
  async fetch(request, env) {
    const cors = corsHeaders(request);
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });
    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405, headers: cors });
    }
    if (!env.GEMINI_API_KEY) {
      return new Response(JSON.stringify({ error: "Assistant not configured." }), {
        status: 503,
        headers: { ...cors, "Content-Type": "application/json" },
      });
    }

    let question = "";
    let lang = "en";
    try {
      const data = await request.json();
      question = typeof data.question === "string" ? data.question.trim() : "";
      if (data.lang === "pt") lang = "pt";
    } catch {
      question = "";
    }
    if (!question) {
      return new Response(JSON.stringify({ error: "Empty question." }), {
        status: 400,
        headers: { ...cors, "Content-Type": "application/json" },
      });
    }
    if (question.length > MAX_QUESTION_CHARS) question = question.slice(0, MAX_QUESTION_CHARS);

    const [kb, nameIndex] = await Promise.all([
      fetchJson(`${KB_BASE}knowledge-base.json`),
      fetchJson(`${KB_BASE}name-index.json`),
    ]);
    if (!kb || !nameIndex) {
      return new Response(JSON.stringify({ error: "Knowledge base unavailable." }), {
        status: 502,
        headers: { ...cors, "Content-Type": "application/json" },
      });
    }

    // Resolve entities and (for a two-person relationship question) the exact path.
    const peopleIds = resolvePeople(question, nameIndex).slice(0, MAX_PEOPLE);
    let path = null;
    if (RELATIONAL_RE.test(question) && peopleIds.length >= 2) {
      path = relationshipPath(kb, peopleIds[0], peopleIds[1]);
    }

    // Documents to load in full: those named in the question, plus those linked to the
    // resolved people (bounded).
    const sourceIds = new Set(resolveSources(question));
    for (const pid of peopleIds) {
      for (const sid of kb.people[pid]?.source_ids || []) {
        if (sourceIds.size >= MAX_SOURCES) break;
        sourceIds.add(sid);
      }
    }

    const [peopleRecords, sourceRecords] = await Promise.all([
      Promise.all(peopleIds.map((id) => fetchJson(`${KB_BASE}${id}.json`))),
      Promise.all([...sourceIds].slice(0, MAX_SOURCES).map((id) => fetchJson(`${KB_BASE}${id}.json`))),
    ]);

    const userContent = buildUserContent(
      kb,
      question,
      lang,
      path,
      peopleRecords.filter(Boolean),
      sourceRecords.filter(Boolean),
    );

    try {
      const stream = await streamGemini(env.GEMINI_API_KEY, userContent);
      return new Response(stream, {
        headers: {
          ...cors,
          "Content-Type": "text/plain; charset=utf-8",
          "Cache-Control": "no-store",
        },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: String(err.message || err) }), {
        status: 502,
        headers: { ...cors, "Content-Type": "application/json" },
      });
    }
  },
};
