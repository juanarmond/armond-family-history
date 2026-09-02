import { load as parseYaml } from "./vendor/js-yaml.mjs";

const ENTITY_TYPES = {
  people: { directory: "people" },
  families: { directory: "families" },
  events: { directory: "events" },
  places: { directory: "places" },
  sources: { directory: "sources" },
  fan: { directory: "fan" },
};

const DATA_ROOT = "../data";
// evidence/ lives at the repository root; the viewer is one level below it. The
// Pages build rewrites this (and DATA_ROOT) to "." since it serves the viewer from
// the site root with evidence/ beside it.
const EVIDENCE_ROOT = "..";
const INDEX_PATH = "./entity-index.json";

// Sources live in category subfolders (data/sources/<category>/); map the ID
// prefix back to its folder so the viewer fetches the right file.
const SOURCE_DIR = {
  CIV: "civil",
  GOV: "government",
  PAR: "parish",
  PRB: "probate",
  NWS: "newspapers",
  PUB: "publications",
  REC: "family-recollection",
};

function entityPath(kind, directory, id) {
  if (kind === "sources") {
    const sub = SOURCE_DIR[id.slice(0, 3)];
    if (!sub) throw new Error(`Unknown source category for ${id}`);
    return `${DATA_ROOT}/sources/${sub}/${id}.yaml`;
  }
  return `${DATA_ROOT}/${directory}/${id}.yaml`;
}

async function fetchYaml(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Unable to read ${path}: HTTP ${response.status}`);
  }
  const parsed = parseYaml(await response.text());
  return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : null;
}

async function loadEntityIndex() {
  const response = await fetch(INDEX_PATH, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Unable to read ${INDEX_PATH}: HTTP ${response.status}`);
  }
  const index = await response.json();
  if (!index || typeof index !== "object" || Array.isArray(index)) {
    throw new Error("The entity index is invalid.");
  }
  return index;
}

async function loadEntityType(kind, { directory }) {
  const index = await loadEntityIndex();
  const ids = index[kind];
  if (!Array.isArray(ids)) {
    throw new Error(`The entity index does not contain a valid ${kind} list.`);
  }

  const entries = await Promise.all(
    ids.map(async (id) => {
      const entity = await fetchYaml(entityPath(kind, directory, id));
      if (!entity || entity.id !== id) {
        throw new Error(`Entity ${id} is missing or does not match its indexed identifier.`);
      }
      return [id, entity];
    }),
  );
  return Object.fromEntries(entries);
}

export function evidenceHref(path) {
  if (typeof path !== "string") return null;
  const clean = path.trim();
  // Only expose genuine preserved evidence files, never internal repository
  // documents referenced as a source's repository_path (e.g. STATUS.md).
  if (!/^evidence\//.test(clean)) return null;
  // Stored paths are repository-root relative; resolve them against EVIDENCE_ROOT.
  return `${EVIDENCE_ROOT}/${clean}`;
}

// Project research notes as bilingual pairs { en, pt }. `text` is the English
// base (always present); `text_pt` is the optional Portuguese translation. The
// viewer resolves which to show from the active locale. A bare string note (or a
// note without a translation) yields { en, pt: null }.
function noteTexts(notes) {
  if (!Array.isArray(notes)) return [];
  return notes
    .map((note) => {
      if (typeof note === "string") return { en: note.trim(), pt: null };
      if (note && typeof note.text === "string") {
        const pt =
          typeof note.text_pt === "string" && note.text_pt.trim()
            ? note.text_pt.trim()
            : null;
        return { en: note.text.trim(), pt };
      }
      return { en: "", pt: null };
    })
    .filter((note) => note.en);
}

function sourceIdsFromPerson(person) {
  const ids = new Set();
  for (const variant of person.name_variants || []) {
    for (const id of variant?.source_ids || []) if (typeof id === "string") ids.add(id);
  }
  for (const occupation of person.occupations || []) {
    for (const id of occupation?.source_ids || []) if (typeof id === "string") ids.add(id);
  }
  for (const note of person.notes || []) {
    for (const id of note?.source_ids || []) if (typeof id === "string") ids.add(id);
  }
  return ids;
}

export async function loadTreeData() {
  const [people, families, events, places, sources, fan] = await Promise.all(
    Object.entries(ENTITY_TYPES).map(([kind, config]) => loadEntityType(kind, config)),
  );
  return projectTreeData({ people, families, events, places, sources, fan });
}

// Pure projection from parsed entities to the viewer's presentation model.
// Side-effect free (no fetch, no DOM) so it can be unit-tested under Node.
export function projectTreeData({ people, families, events, places, sources, fan = {} }) {
  const personEvents = {};
  const personSourceIds = {};
  const personSourceRank = {};
  const parentsByChild = {};

  for (const personId of Object.keys(people)) {
    personEvents[personId] = [];
    personSourceIds[personId] = sourceIdsFromPerson(people[personId]);
  }

  for (const [sourceId, source] of Object.entries(sources)) {
    for (const personId of source.linked_people || []) {
      if (personSourceIds[personId]) personSourceIds[personId].add(sourceId);
    }
  }

  for (const [eventId, event] of Object.entries(events)) {
    const place = event.place_id ? places[event.place_id] : null;
    const placeName = place?.preferred_name || event.place_text || null;
    const eventView = {
      id: eventId,
      type: event.event_type || "other",
      date: event.date || null,
      place: placeName ? { id: event.place_id || null, name: placeName } : null,
      status: event.status || "unknown",
      sourceIds: (event.source_ids || []).filter((value) => typeof value === "string"),
    };

    for (const participant of event.participants || []) {
      const personId = participant?.person_id;
      if (!personEvents[personId]) continue;
      // Anyone named in the event keeps its sources...
      for (const sourceId of eventView.sourceIds) personSourceIds[personId].add(sourceId);
      // ...but the event only belongs on a person's own timeline when they are
      // its subject: the principal (birth, death, baptism, burial) or a
      // spouse/partner (marriage). A "parent", "witness" or "informant" role
      // means they are merely referenced — e.g. named as a parent in a child's
      // death record — not that it is their own event.
      const role = participant?.role;
      // The event is the person's OWN when they are its principal, or a spouse/partner in a
      // shared/couple event (marriage, a marriage provision typed "other", residence, …). But
      // a single-subject vital (death, birth, baptism, burial) has exactly one subject: the
      // principal. A spouse's role in one — e.g. the widow named in her late husband's death —
      // is context (its source stays linked to her above), and must NOT appear as her own
      // event, or she reads as having died (or been born) twice.
      const singleSubjectVital =
        event.event_type === "death" ||
        event.event_type === "birth" ||
        event.event_type === "baptism" ||
        event.event_type === "burial";
      const isOwn =
        role === "principal" ||
        ((role === "spouse" || role === "partner") && !singleSubjectVital);
      if (isOwn) {
        personEvents[personId].push({ ...eventView, role });
        // Per-person source ordering: a person's OWN vital records (birth/baptism,
        // marriage, death) rank first, by vital type. Every other record — one that
        // only mentions them (a child's or relative's event) — falls back in the
        // sort to the source's own vital rank + 10.
        const typeRank = { birth: 0, baptism: 1, marriage: 2, death: 3, burial: 4 }[event.event_type] ?? 5;
        const rankMap = (personSourceRank[personId] ||= {});
        for (const sourceId of eventView.sourceIds) {
          if (typeRank < (rankMap[sourceId] ?? 999)) rankMap[sourceId] = typeRank;
        }
      }
    }
  }

  for (const [familyId, family] of Object.entries(families)) {
    for (const child of family.children || []) {
      const childId = child?.person_id;
      if (!childId) continue;
      if (!parentsByChild[childId]) parentsByChild[childId] = [];

      const relationships = child.parent_relationships || [];
      if (relationships.length) {
        for (const relationship of relationships) {
          const parentId = relationship?.parent_id;
          if (!parentId) continue;
          const sourceIds = (relationship.source_ids || []).filter((id) => typeof id === "string");
          parentsByChild[childId].push({
            familyId,
            parentId,
            type: relationship.relationship_type || "unknown",
            status: relationship.status || "unknown",
            sourceIds,
          });
          if (personSourceIds[parentId]) {
            for (const sourceId of sourceIds) personSourceIds[parentId].add(sourceId);
          }
          if (personSourceIds[childId]) {
            for (const sourceId of sourceIds) personSourceIds[childId].add(sourceId);
          }
        }
      } else {
        const sourceIds = (child.source_ids || []).filter((id) => typeof id === "string");
        for (const parentId of child.parent_ids || []) {
          parentsByChild[childId].push({
            familyId,
            parentId,
            type: "unknown",
            status: child.status || "unknown",
            sourceIds,
          });
        }
      }
    }
  }

  // Marriage events by family, and each person's spouses, so the viewer can
  // present couples rather than a bare pedigree of individuals.
  const marriageEvents = Object.values(events).filter((event) => event.event_type === "marriage");
  const marriageByFamily = {};
  const spousesByPerson = {};
  for (const personId of Object.keys(people)) spousesByPerson[personId] = [];

  for (const [familyId, family] of Object.entries(families)) {
    const partnerIds = (family.partners || [])
      .map((partner) => partner?.person_id)
      .filter((id) => typeof id === "string");

    for (const partnerId of partnerIds) {
      if (!spousesByPerson[partnerId]) continue;
      for (const otherId of partnerIds) {
        if (otherId !== partnerId) spousesByPerson[partnerId].push({ spouseId: otherId, familyId });
      }
    }

    if (partnerIds.length < 2) continue;
    const marriage = marriageEvents.find((event) => {
      const spouseIds = (event.participants || [])
        .filter((participant) => participant?.role === "spouse")
        .map((participant) => participant.person_id);
      return spouseIds.length >= 2 && partnerIds.every((id) => spouseIds.includes(id));
    });
    if (marriage) {
      const place = marriage.place_id ? places[marriage.place_id] : null;
      marriageByFamily[familyId] = {
        date: marriage.date || null,
        place: place?.preferred_name || marriage.place_text || null,
        status: marriage.status || "unknown",
        sourceIds: (marriage.source_ids || []).filter((id) => typeof id === "string"),
      };
    }
  }

  const fileKind = (p) => {
    if (typeof p !== "string") return null;
    const ext = p.split("?")[0].split(".").pop().toLowerCase();
    if (ext === "pdf") return "pdf";
    if (["jpg", "jpeg", "png", "tif", "tiff", "gif", "webp"].includes(ext)) return "image";
    return "other";
  };
  // Sort multi-page document scans into reading order regardless of which page is the
  // primary `digital_file`: pad every run of digits so "p2" < "p10" and "page-01" <
  // "page-02" sort numerically (e.g. gen1 < p2 < p10; 1867-p5 < 1881-embargos).
  const naturalPageKey = (p) => (typeof p === "string" ? p : "").replace(/\d+/g, (n) => n.padStart(6, "0"));
  // A source is flagged as an "uncertain reading" only when a CORE genealogical
  // fact could not be read — recorded explicitly per source as
  // `reading_reliability: partial`. Peripheral gap markers (a witness's bairro, an
  // attesting doctor's initial, an ID digit, a spelling variant) stay inline in the
  // transcript but do NOT brand the whole record; those sources are `complete`.
  const sourceView = Object.fromEntries(
    Object.entries(sources).map(([sourceId, source]) => {
      const rawPath = source.digital_file?.path || source.repository?.repository_path || null;
      const url = source.repository?.url;
      const limitation = source.reliability?.limitations;
      const pagePaths = [
        ...(source.digital_file?.path ? [source.digital_file.path] : []),
        ...(source.additional_pages || []).map((p) => p?.path).filter((p) => typeof p === "string"),
      ].sort((a, b) => naturalPageKey(a).localeCompare(naturalPageKey(b)));
      return [sourceId, {
        id: sourceId,
        title: source.title || sourceId,
        titlePt:
          typeof source.title_pt === "string" && source.title_pt.trim()
            ? source.title_pt.trim()
            : null,
        recordType: source.record_type || "Source",
        recordCategory: typeof source.record_category === "string" ? source.record_category : null,
        sourceForm: typeof source.source_form === "string" ? source.source_form : null,
        quality: typeof source.information_quality === "string" ? source.information_quality : null,
        limitation: typeof limitation === "string" && limitation.trim() ? limitation.trim() : null,
        private: Boolean(source.private),
        involvesLiving: (source.linked_people || []).some(
          (pid) => (people[pid]?.privacy) === "living",
        ),
        uncertain: source.reading_reliability === "partial",
        transcription:
          typeof source.transcription === "string" && source.transcription.trim()
            ? source.transcription.trim()
            : null,
        transcriptionPt:
          typeof source.transcription_pt === "string" && source.transcription_pt.trim()
            ? source.transcription_pt.trim()
            : null,
        abstract:
          typeof source.abstract === "string" && source.abstract.trim()
            ? source.abstract.trim()
            : null,
        abstractPt:
          typeof source.abstract_pt === "string" && source.abstract_pt.trim()
            ? source.abstract_pt.trim()
            : null,
        file: evidenceHref(rawPath),
        fileType: fileKind(rawPath),
        pages: pagePaths.map((p) => ({ url: evidenceHref(p), fileType: fileKind(p) })),
        url: typeof url === "string" && url.trim() ? url.trim() : null,
      }];
    }),
  );

  // FAN / context references: records where a person appears only in a
  // functional role (witness, appraiser, creditor, attorney, party, co-owner).
  // Projected per person from each reference's participants.
  const trimmedText = (value) =>
    typeof value === "string" && value.trim() ? value.trim() : null;
  const fanByPerson = {};
  const fanView = Object.fromEntries(
    Object.entries(fan).map(([fanId, ref]) => {
      const view = {
        id: fanId,
        title: ref.title || fanId,
        titlePt: trimmedText(ref.title_pt),
        recordType: ref.record_type || "Reference",
        recordCategory: typeof ref.record_category === "string" ? ref.record_category : null,
        date: ref.event_date || null,
        place: trimmedText(ref.event_place_text),
        transcription: trimmedText(ref.transcription),
        transcriptionPt: trimmedText(ref.transcription_pt),
        abstract: trimmedText(ref.abstract),
        abstractPt: trimmedText(ref.abstract_pt),
        file: evidenceHref(ref.digital_file?.path || null),
        fileType: fileKind(ref.digital_file?.path || null),
        pages: [
          ...(ref.digital_file?.path ? [ref.digital_file.path] : []),
          ...(ref.additional_pages || []).map((p) => p?.path).filter((p) => typeof p === "string"),
        ].sort((a, b) => naturalPageKey(a).localeCompare(naturalPageKey(b))).map((p) => ({ url: evidenceHref(p), fileType: fileKind(p) })),
        url: trimmedText(ref.repository?.url),
      };
      for (const participant of ref.participants || []) {
        const personId = participant?.person_id;
        if (!personId) continue;
        (fanByPerson[personId] ||= []).push({
          ...view,
          role: trimmedText(participant.role),
          note: trimmedText(participant.note),
        });
      }
      return [fanId, view];
    }),
  );

  // Siblings and children, per person, from each family's child roster: modelled
  // children (P- entities) plus documented_children (attested but not modelled).
  // Children come from the families where a person is a partner; siblings from the
  // family where they are a child (the roster minus themselves). Possibly-living
  // people are omitted entirely — only clearly deceased people appear.
  const siblingsByPerson = {};
  const childrenByPerson = {};
  for (const personId of Object.keys(people)) {
    siblingsByPerson[personId] = [];
    childrenByPerson[personId] = [];
  }
  for (const family of Object.values(families)) {
    const partnerIds = (family.partners || [])
      .map((partner) => partner?.person_id)
      .filter((id) => typeof id === "string");
    const modelledChildIds = (family.children || [])
      .map((child) => child?.person_id)
      .filter((id) => typeof id === "string");
    const documented = (family.documented_children || [])
      .filter((entry) => entry && typeof entry.name === "string" && entry.name.trim())
      .map((entry) => ({
        type: "documented",
        name: entry.name.trim(),
        lifespan: trimmedText(entry.lifespan),
        note: trimmedText(entry.note),
        sourceIds: (entry.source_ids || []).filter((id) => typeof id === "string"),
      }));
    // The family's child roster: deceased modelled children plus documented ones.
    const childRoster = [];
    for (const childId of modelledChildIds) {
      const child = people[childId];
      if (!child || (child.privacy || "unknown") !== "deceased") continue;
      childRoster.push({ type: "person", id: childId, name: child.preferred_name || childId });
    }
    for (const entry of documented) childRoster.push({ ...entry });
    // Children: each partner gets the whole roster.
    for (const partnerId of partnerIds) {
      if (!childrenByPerson[partnerId]) continue;
      for (const child of childRoster) childrenByPerson[partnerId].push({ ...child });
    }
    // Siblings: each modelled child gets the roster minus themselves.
    for (const meId of modelledChildIds) {
      if (!siblingsByPerson[meId]) continue;
      for (const child of childRoster) {
        if (child.type === "person" && child.id === meId) continue;
        siblingsByPerson[meId].push({ ...child });
      }
    }
  }

  // Life-event ordering for a person's sources: rank by the earliest life event
  // the source documents (birth → baptism → marriage → death → burial → other
  // direct), then supporting/contextual records last; ties broken by year then ID.
  const EVENT_RANK = {
    birth: 1, baptism: 2, marriage: 3, death: 4, burial: 5,
    residence: 6, immigration: 6, naturalisation: 6, occupation: 6, probate: 6, other: 6,
  };
  const CATEGORY_RANK = {
    cemetery: 5, census: 6, court_or_probate: 6, government_record: 6,
    official_index: 6, immigration: 6, naturalisation: 6, military: 6,
    institutional_record: 6, other: 6,
    newspaper: 7, published_genealogy: 7, collaborative_tree: 7, family_recollection: 7,
  };
  const yearOf = (date) => {
    if (!date || typeof date !== "object") return null;
    if (date.kind === "exact" && typeof date.value === "string") return Number(date.value.slice(0, 4));
    if ((date.kind === "month" || date.kind === "year") && date.year) return Number(date.year);
    if (date.earliest) return Number(date.earliest);
    return null;
  };
  const eventsBySource = {};
  for (const event of Object.values(events)) {
    for (const sid of event.source_ids || []) {
      if (typeof sid === "string") (eventsBySource[sid] ||= []).push(event);
    }
  }
  const sourceRank = {};
  const sourceYear = {};
  for (const [sid, source] of Object.entries(sources)) {
    let rank = null;
    let year = null;
    for (const event of eventsBySource[sid] || []) {
      const r = EVENT_RANK[event.event_type] ?? 6;
      if (rank === null || r < rank) rank = r;
      const y = yearOf(event.date);
      if (y && (year === null || y < year)) year = y;
    }
    if (rank === null) rank = CATEGORY_RANK[source.record_category] ?? 6;
    if (year === null) year = yearOf(source.event_date) ?? yearOf(source.registration_date);
    sourceRank[sid] = rank;
    sourceYear[sid] = year ?? 9999;
  }

  // A person is flagged only for genuine, localisable signals: a source whose
  // transcription carries an unresolved reading, or a note that explicitly
  // records a conflict. Name variants alone are not a conflict.
  const conflictTerms = ["conflict", "unresolved"];

  // Derived biography: a structured, language-agnostic summary of a person built
  // purely from their vital events, relationships and occupations, so the viewer
  // can render a narrative that never drifts from the data and never fabricates.
  const yearOfDate = (d) => {
    if (!d || typeof d !== "object") return null;
    if (d.kind === "exact" && typeof d.value === "string") return Number(d.value.slice(0, 4));
    if ((d.kind === "month" || d.kind === "year") && d.year) return Number(d.year);
    // Prefer the year stated in the text (e.g. "about 1847") over the range bound.
    const m = String(d.text || "").match(/\b(\d{4})\b/);
    if (m) return Number(m[1]);
    if (d.earliest) return Number(d.earliest);
    return null;
  };
  const isBrazil = (place) => typeof place === "string" && /brazil|brasil/i.test(place);
  const isCertainKind = (d) => d && (d.kind === "exact" || d.kind === "month" || d.kind === "year");

  // Kinship shortest path from the repository subject (Ahnentafel 1) to each
  // person, so a detail card can show "how this person connects to me". Because
  // the tree is the subject's ancestry, these paths are almost always a clean
  // upward parent chain.
  const SUBJECT_ID = "P-0001";
  const adjacency = {};
  const addEdge = (a, b, kind) => {
    (adjacency[a] ||= []).push({ id: b, kind });
  };
  for (const [childId, parentRels] of Object.entries(parentsByChild)) {
    for (const rel of parentRels) {
      addEdge(childId, rel.parentId, "parent"); // child → parent
      addEdge(rel.parentId, childId, "child"); // parent → child
    }
  }
  for (const [pid, list] of Object.entries(spousesByPerson)) {
    for (const s of list) addEdge(pid, s.spouseId, "spouse");
  }
  const pred = {};
  const predEdge = {};
  if (people[SUBJECT_ID]) {
    const queue = [SUBJECT_ID];
    const seen = new Set([SUBJECT_ID]);
    while (queue.length) {
      const cur = queue.shift();
      for (const nb of adjacency[cur] || []) {
        if (seen.has(nb.id)) continue;
        seen.add(nb.id);
        pred[nb.id] = cur;
        predEdge[nb.id] = nb.kind; // relation from pred[nb.id] → nb.id
        queue.push(nb.id);
      }
    }
  }
  const father = new Set(
    (parentsByChild[SUBJECT_ID] || [])
      .filter((r) => people[r.parentId]?.sex === "male")
      .map((r) => r.parentId),
  );
  const mother = new Set(
    (parentsByChild[SUBJECT_ID] || [])
      .filter((r) => people[r.parentId]?.sex === "female")
      .map((r) => r.parentId),
  );
  const lineageOf = (targetId) => {
    if (targetId === SUBJECT_ID || !(targetId in pred)) return null;
    const rev = [];
    let cur = targetId;
    while (cur !== SUBJECT_ID) {
      rev.push({ id: cur, edge: predEdge[cur] });
      cur = pred[cur];
    }
    rev.reverse();
    const ids = [SUBJECT_ID, ...rev.map((r) => r.id)];
    const edges = rev.map((r) => r.edge); // edges[i]: ids[i] → ids[i+1]
    let relationship;
    if (edges.every((e) => e === "parent")) {
      const side = father.has(ids[1]) ? "paternal" : mother.has(ids[1]) ? "maternal" : null;
      relationship = { kind: "ancestor", degree: edges.length, side };
    } else {
      relationship = { kind: "related" };
    }
    return { ids, relationship };
  };

  const buildBiography = (personId) => {
    const person = people[personId];
    const evs = personEvents[personId] || [];
    const principal = (types) =>
      evs.find((e) => types.includes(e.type) && e.role === "principal");
    const birthEv = principal(["birth"]) || principal(["baptism"]);
    const deathEv = principal(["death"]) || principal(["burial"]);
    const parents = [
      ...new Set(
        (parentsByChild[personId] || [])
          .map((p) => people[p.parentId]?.preferred_name)
          .filter(Boolean),
      ),
    ];
    const marriages = (spousesByPerson[personId] || [])
      .map((s) => {
        const m = marriageByFamily[s.familyId] || null;
        return {
          spouse: people[s.spouseId]?.preferred_name || null,
          date: m?.date || null,
          place: m?.place || null,
        };
      })
      .filter((m) => m.spouse);
    const children = (childrenByPerson[personId] || []).map((c) => c.name).filter(Boolean);
    const occupations = (person.occupations || [])
      .map((o) => (typeof o.value === "string" ? o.value.trim() : ""))
      .filter(Boolean);

    let birth = null;
    if (birthEv) {
      const place = birthEv.place?.name || null;
      let emigratedToBrazil = false;
      if (place && !isBrazil(place)) {
        emigratedToBrazil = evs.some((e) => e !== birthEv && isBrazil(e.place?.name));
      }
      birth = {
        date: birthEv.date || null,
        place,
        parents,
        emigratedToBrazil,
        fromBaptism: birthEv.type === "baptism",
      };
    }
    let death = null;
    if (deathEv) {
      const by = birthEv ? yearOfDate(birthEv.date) : null;
      const dy = yearOfDate(deathEv.date);
      let age = null;
      if (by && dy && dy >= by && dy - by < 120) {
        age = { years: dy - by, approx: !(isCertainKind(birthEv.date) && isCertainKind(deathEv.date)) };
      }
      death = { date: deathEv.date || null, place: deathEv.place?.name || null, age };
    }

    const empty =
      !birth && !death && marriages.length === 0 && children.length === 0 && occupations.length === 0;
    if (empty) return { sparse: true, parents };
    return {
      sex: person.sex || "unknown",
      birth,
      // parentsOnly drives the "recorded as the parent of …" lead when there is no
      // birth event but the person is known only through their children.
      parentsOnly: !birth && marriages.length === 0 && children.length > 0,
      marriages,
      children,
      occupations,
      death,
    };
  };

  const peopleView = {};

  for (const [personId, person] of Object.entries(people)) {
    const privacy = person.privacy || "unknown";
    const living = privacy === "living";
    const variants = (person.name_variants || [])
      .map((variant) => variant?.value)
      .filter((value) => typeof value === "string");
    const notes = living ? [] : noteTexts(person.notes || []);
    const ownRank = personSourceRank[personId] || {};
    // FONTES ordering rule (owner-defined): a person's OWN records first
    // (birth/baptism, then marriage, then death), then the birth/baptism/marriage/
    // death certificates (civil/parish) that only MENTION them (e.g. a child's),
    // and finally everything else — probate, published genealogy (PUB), government
    // (GOV), newspaper, … that is not the person's own record — LAST.
    //   0–4    own record, by vital type (birth/baptism, marriage, death)
    //   11–16  a civil/parish vital certificate that only mentions them, by vital type
    //   30     non-vital context not about the person (probate, PUB, GOV, press, …)
    const VITAL_CATS = new Set(["civil_registration", "parish_register"]);
    const orderRank = (sid) => {
      if (ownRank[sid] !== undefined) return ownRank[sid];
      const cat = (sources[sid] || {}).record_category;
      return VITAL_CATS.has(cat) ? 10 + (sourceRank[sid] ?? 6) : 30;
    };
    const sourceIds = [...(personSourceIds[personId] || [])].sort(
      (a, b) =>
        orderRank(a) - orderRank(b) ||
        (sourceYear[a] ?? 9999) - (sourceYear[b] ?? 9999) ||
        a.localeCompare(b),
    );
    const conflictText = notes
      .map((note) => `${note.en} ${note.pt || ""}`)
      .join(" ")
      .toLocaleLowerCase();
    const personSources = living ? [] : sourceIds.map((id) => sourceView[id]).filter(Boolean);

    peopleView[personId] = {
      id: personId,
      name: person.preferred_name || personId,
      privacy,
      sex: person.sex || "unknown",
      biography: living ? null : buildBiography(personId),
      lineage: living ? null : lineageOf(personId),
      nationality: typeof person.nationality === "string" && person.nationality.trim()
        ? person.nationality.trim()
        : null,
      nameVariants: living ? [] : variants,
      events: living
        ? []
        : [...(personEvents[personId] || [])].sort((a, b) =>
            `${a.type}${JSON.stringify(a.date)}`.localeCompare(`${b.type}${JSON.stringify(b.date)}`),
          ),
      sourceCount: sourceIds.length,
      sources: personSources,
      spouses: living ? [] : (spousesByPerson[personId] || []).map((entry) => ({
        id: entry.spouseId,
        name: people[entry.spouseId]?.preferred_name || entry.spouseId,
        marriage: marriageByFamily[entry.familyId] || null,
      })),
      occupations: living ? [] : (person.occupations || [])
        .filter((occupation) => occupation && typeof occupation.value === "string" && occupation.value.trim())
        .map((occupation) => ({
          value: occupation.value.trim(),
          note: typeof occupation.note === "string" && occupation.note.trim() ? occupation.note.trim() : null,
          sourceIds: (occupation.source_ids || []).filter((id) => typeof id === "string"),
        })),
      notes,
      profile: living || typeof person.profile !== "string" || !person.profile.trim()
        ? null
        : person.profile.trim(),
      profilePt: living || typeof person.profile_pt !== "string" || !person.profile_pt.trim()
        ? null
        : person.profile_pt.trim(),
      siblings: living ? [] : (siblingsByPerson[personId] || []),
      children: living ? [] : (childrenByPerson[personId] || []),
      fanReferences: living
        ? []
        : (fanByPerson[personId] || []).slice().sort((a, b) => a.id.localeCompare(b.id)),
      hasConflict:
        conflictTerms.some((term) => conflictText.includes(term)),
    };
  }

  return {
    schemaVersion: 1,
    people: peopleView,
    parentsByChild,
    marriageByFamily,
    sources: sourceView,
    fan: fanView,
    familyCount: Object.keys(families).length,
  };
}
