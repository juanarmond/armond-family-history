// Family branches — "the four rivers". The subject's four grandparents each head a branch:
// their own ancestors plus the deceased children of every couple in that line (siblings of
// an ancestor, aunts and uncles). A viewer can follow one branch, several, or everything,
// and the app scopes search, the home screen, What's new and the Family Story to that
// choice. Pure functions over the projected tree data (no DOM), so they are unit-tested
// under Node (tests/js/branches.test.mjs).

export const SUBJECT_ID = "P-0001";

// The four branches, in the order the Family Story tells them (`river`). Each `rootId` is a
// grandparent of the subject; which parent's side it is on is derived from the tree. The
// colours are kept clear of the evidence-tier colours (confirmed / strong / hypothesis).
export const BRANCHES = [
  { key: "armond", rootId: "P-0004", label: "Armond", colour: "#2f5d43", river: 1 },
  { key: "engracio", rootId: "P-0005", label: "Engracio", colour: "#b07d2b", river: 2 },
  { key: "muniz", rootId: "P-0006", label: "Muniz", colour: "#3d6b8c", river: 3 },
  { key: "bohrer", rootId: "P-0007", label: "Bohrer", colour: "#8c4a5a", river: 4 },
];

// A person's parents on every link that is not rejected (each parent once).
export const visibleParents = (parentsByChild, personId) => [...new Set(
  (parentsByChild[personId] || [])
    .filter((relationship) => relationship.status !== "rejected")
    .map((relationship) => relationship.parentId),
)];

// The year of a structured date ({ kind: exact | month | year | approximate | … }).
export function yearOfDate(date) {
  if (!date || typeof date !== "object") return null;
  if (date.kind === "exact" && typeof date.value === "string") return Number(date.value.slice(0, 4)) || null;
  if (Number.isFinite(date.year)) return date.year;
  if (Number.isFinite(date.earliest)) return date.earliest;
  const match = String(date.text || date.original_text || "").match(/\b(1[5-9]\d{2}|20\d{2})\b/);
  return match ? Number(match[1]) : null;
}

// The earliest year an original record documents a person: one of their own events that is
// confirmed or strong evidence and rests on at least one record the validator would let confirm
// a conclusion — an original or a faithful copy (never an authored narrative such as a published
// genealogy) outside the weak categories. Mirrors scripts/validation/rules.py
// (CONFIRMING_SOURCE_FORMS, WEAK_STANDALONE_CATEGORIES); keep the two in step.
const CONFIRMING_SOURCE_FORMS = new Set(["original", "derivative"]);
const WEAK_STANDALONE_CATEGORIES = new Set(["collaborative_tree", "family_recollection"]);
const PROVEN = new Set(["confirmed", "strong-evidence"]);
const isOriginalRecord = (source) => Boolean(source)
  && CONFIRMING_SOURCE_FORMS.has(source.sourceForm) && !WEAK_STANDALONE_CATEGORIES.has(source.recordCategory);
function earliestRecordYear(person, sources = {}) {
  const years = (person?.events || [])
    .filter((event) => PROVEN.has(event.status) && (event.sourceIds || []).some((id) => isOriginalRecord(sources[id])))
    .map((event) => yearOfDate(event.date))
    .filter(Number.isFinite);
  return years.length ? Math.min(...years) : null;
}

// ---------- Surnames ----------
// A browsable surname index. Portuguese and colonial German names carry devotional and second
// given names ("Maria de Jesus", "Anna Clara"), so a word counts as a surname only when it ends
// someone's name, never starts anyone's name, and is not on the short list below. Spellings that
// differ only by a silent h, y/i or a doubled letter share one entry ("Bohrer / Borer").
const PARTICLES = new Set(["de", "da", "do", "dos", "das", "e", "d'", "del", "della", "van", "von", "der", "zu"]);
const SUFFIXES = new Set(["filho", "filha", "junior", "jr", "sr", "neto", "neta", "sobrinho", "velho", "moco"]);
const NOT_SURNAMES = new Set([
  // devotional names
  "jesus", "conceicao", "santo", "espirito", "deus", "anjos", "luz", "paixao", "assumpcao", "assuncao",
  "piedade", "gloria", "rosario", "dores", "natividade", "trindade", "nazare", "graca", "gracas",
  // second given names that end some women's names in this archive
  "eugenia", "clara", "angelica", "caroline", "margaretha", "francisca", "luiza", "thereza", "tereza",
]);

const fold = (text) => text.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

export function nameTokens(name) {
  return String(name || "")
    .replace(/\(.*?\)|\[.*?\]/g, " ")
    .split(/\s+/)
    .map((token) => token.replace(/[^\p{L}'-]/gu, ""))
    .filter(Boolean);
}

export function surnameKey(token) {
  return fold(token).replace(/h/g, "").replace(/y/g, "i").replace(/(.)\1+/g, "$1");
}

// Tokens after the given name, without particles or generational suffixes.
function tailTokens(name) {
  return nameTokens(name)
    .slice(1)
    .filter((token) => !PARTICLES.has(fold(token)) && !SUFFIXES.has(fold(token)));
}

// The set of surname keys known to the archive, built from every person's name.
export function surnameVocabulary(people) {
  const givenNames = new Set();
  const lastWords = new Set();
  for (const person of Object.values(people)) {
    if (person.privacy === "living") continue;
    const tokens = nameTokens(person.name);
    if (tokens[0]) givenNames.add(fold(tokens[0]));
    const tail = tailTokens(person.name);
    if (tail.length) lastWords.add(tail[tail.length - 1]);
  }
  const vocabulary = new Set();
  for (const word of lastWords) {
    const folded = fold(word);
    if (givenNames.has(folded) || NOT_SURNAMES.has(folded)) continue;
    vocabulary.add(surnameKey(word));
  }
  return vocabulary;
}

// Surname entries for a set of person ids: [{ key, label, spellings, ids }], most people first.
export function surnameIndex(people, ids, vocabulary = surnameVocabulary(people)) {
  const groups = new Map();
  for (const id of ids) {
    const person = people[id];
    if (!person || person.privacy === "living") continue;
    const seen = new Set();
    for (const token of tailTokens(person.name)) {
      const key = surnameKey(token);
      if (!vocabulary.has(key) || seen.has(key)) continue;
      seen.add(key);
      const group = groups.get(key) || { key, spellings: new Map(), ids: [] };
      group.spellings.set(token, (group.spellings.get(token) || 0) + 1);
      group.ids.push(id);
      groups.set(key, group);
    }
  }
  return [...groups.values()]
    .map((group) => {
      const spellings = [...group.spellings.entries()]
        .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
        .map(([spelling]) => spelling);
      return {
        key: group.key,
        label: spellings.slice(0, 2).join(" / "),
        spellings,
        ids: group.ids.sort((a, b) => (people[a]?.name || "").localeCompare(people[b]?.name || "")),
      };
    })
    .sort((a, b) => b.ids.length - a.ids.length || a.label.localeCompare(b.label));
}

// ---------- Branch membership ----------
export function computeBranches({ people, parentsByChild, sources = {} }, config = BRANCHES) {
  // A branch's side is the subject's parent it descends through — found from the tree alone,
  // since the public site withholds a living parent's sex.
  const subjectParents = visibleParents(parentsByChild, SUBJECT_ID);
  const sideParentOf = (rootId) =>
    subjectParents.find((id) => visibleParents(parentsByChild, id).includes(rootId)) || null;
  const vocabulary = surnameVocabulary(people);
  const list = [];
  const personBranches = {};
  const surnameEntries = new Map();
  for (const branch of config) {
    if (!people[branch.rootId]) continue;
    const ancestors = new Set([branch.rootId]);
    const queue = [branch.rootId];
    while (queue.length) {
      for (const parentId of visibleParents(parentsByChild, queue.shift())) {
        if (ancestors.has(parentId) || !people[parentId]) continue;
        ancestors.add(parentId);
        queue.push(parentId);
      }
    }
    const members = new Set(ancestors);
    const collaterals = new Set();
    for (const id of ancestors) {
      for (const child of people[id]?.children || []) {
        if (child.type !== "person" || !child.id || members.has(child.id) || child.id === SUBJECT_ID || !people[child.id]) continue;
        collaterals.add(child.id);
      }
    }
    // A collateral's spouse is part of the family story too (a great-aunt by marriage).
    for (const id of collaterals) {
      members.add(id);
      for (const spouse of people[id]?.spouses || []) if (people[spouse.id]) members.add(spouse.id);
    }
    const years = [...members].map((id) => earliestRecordYear(people[id], sources)).filter(Number.isFinite);
    list.push({
      ...branch,
      name: people[branch.rootId].name,
      sideParentId: sideParentOf(branch.rootId),
      members: [...members].sort(),
      earliestYear: years.length ? Math.min(...years) : null,
    });
    surnameEntries.set(branch.key, surnameIndex(people, members, vocabulary));
    for (const id of members) (personBranches[id] ||= []).push(branch.key);
  }
  // The few surnames that identify each branch on its card: its own commonest surnames,
  // preferring those found in no other branch (Silva and Ferreira recur everywhere).
  for (const branch of list) {
    const ownSurname = surnameKey(branch.label);
    const elsewhere = new Set(list.filter((other) => other !== branch).flatMap((other) => surnameEntries.get(other.key).map((entry) => entry.key)));
    const candidates = surnameEntries.get(branch.key).filter((entry) => entry.key !== ownSurname);
    branch.surnames = [
      ...candidates.filter((entry) => !elsewhere.has(entry.key)),
      ...candidates.filter((entry) => elsewhere.has(entry.key)),
    ].slice(0, 4).map((entry) => entry.spellings[0]);
  }
  return { list, byKey: Object.fromEntries(list.map((branch) => [branch.key, branch])), personBranches, vocabulary };
}

// The branches grouped by side (the two grandparents of each parent), in branch order; a
// branch whose side cannot be traced sits in a group of its own at the end.
export function branchSides(info) {
  const groups = [];
  for (const branch of info.list) {
    const group = branch.sideParentId && groups.find((entry) => entry.parentId === branch.sideParentId);
    if (group) group.branches.push(branch);
    else groups.push({ parentId: branch.sideParentId, branches: [branch] });
  }
  return [...groups.filter((group) => group.parentId), ...groups.filter((group) => !group.parentId)];
}

// ---------- Scope (the viewer's choice of branches) ----------
// The chosen branches in branch order; an empty scope (everything) means all of them.
export const chosenBranches = (info, scope) =>
  scope.size ? info.list.filter((branch) => scope.has(branch.key)) : info.list;
// A scope is a Set of branch keys; the empty set means "everything". Choosing every branch is
// the same as everything, so it normalises to the empty set.
export function normaliseScope(keys, info) {
  const valid = new Set([...keys].filter((key) => info.byKey[key]));
  return valid.size === info.list.length ? new Set() : valid;
}

export function parseScope(text, info) {
  if (typeof text !== "string" || !text.trim() || text.trim() === "all") return new Set();
  return normaliseScope(text.split(",").map((key) => key.trim().toLowerCase()), info);
}

// Branch order, so a shared link reads the same however the boxes were ticked.
export function serialiseScope(scope, info) {
  if (!scope.size) return "all";
  return chosenBranches(info, scope).map((branch) => branch.key).join(",");
}

export function inScope(info, scope, personId) {
  if (!scope.size) return true;
  return (info.personBranches[personId] || []).some((key) => scope.has(key));
}

// Where a scoped tree starts: one grandparent; for both grandparents on one side, their child
// (the subject's parent); anything wider starts at the subject, as the full tree does.
export function scopeRoot(info, scope) {
  if (!scope.size) return SUBJECT_ID;
  const chosen = chosenBranches(info, scope);
  if (chosen.length === 1) return chosen[0].rootId;
  const parents = new Set(chosen.map((branch) => branch.sideParentId));
  return parents.size === 1 && !parents.has(null) ? [...parents][0] : SUBJECT_ID;
}

// How many people the chosen branches hold; everything is all the branches together — the living
// subject and parents belong to none, so they are never counted as traced.
export function scopeSize(info, scope) {
  return new Set(chosenBranches(info, scope).flatMap((branch) => branch.members)).size;
}

// What a shared link's message says: which families, how many people, and the earliest year an
// original record reaches (null when none of them has one). The app turns this into words.
export function shareSummary(info, scope) {
  const chosen = chosenBranches(info, scope);
  const years = chosen.map((branch) => branch.earliestYear).filter(Number.isFinite);
  return {
    everything: !scope.size,
    lines: info.list.length,
    labels: chosen.map((branch) => branch.label),
    people: scopeSize(info, scope),
    year: years.length ? Math.min(...years) : null,
  };
}

// ---------- What's new ----------
// The branches an update touches: through the people it links, and the people linked to the
// records it links. An update that touches no branch (a site-wide note) belongs to every scope.
export function entryBranches(entry, info, sources = {}) {
  const ids = [...(Array.isArray(entry?.links) ? entry.links : []), entry?.primary].filter((id) => typeof id === "string");
  const keys = new Set();
  for (const id of ids) {
    const people = /^P-\d+$/.test(id) ? [id] : sources[id]?.linkedPeople || [];
    for (const personId of people) for (const key of info.personBranches[personId] || []) keys.add(key);
  }
  return keys;
}

export const keysInScope = (keys, scope) => !scope.size || !keys.size || [...keys].some((key) => scope.has(key));

export const entryInScope = (entry, info, scope, sources) =>
  keysInScope(entryBranches(entry, info, sources), scope);

// Curated entries (milestones, corrections, new people) drive the unread badge — the same rule
// that sends a notification. Routine document additions never count.
export const isCurated = (entry) => Boolean(entry) && (entry.kind || "document") !== "document";
export const updateKey = (entry) => `${entry.date || ""}|${entry.title || ""}`;

// ---------- Family Story ----------
// The story is written as four "## RIVER …" chapters (in Portuguese "## RIO …"). For a scoped
// reader: the opening, the chosen rivers, the closing chapters, then the other rivers.
const RIVER_NUMBERS = { one: 1, two: 2, three: 3, four: 4, um: 1, dois: 2, tres: 3, quatro: 4 };
const RIVER_HEADING = /^##\s+(?:RIVER|RIO)\s+(\p{L}+)/iu;

export function storyChapters(text) {
  const chapters = [];
  let current = null;
  for (const line of String(text || "").split("\n")) {
    if (/^## /.test(line) || !current) {
      current = { lines: [], river: null };
      chapters.push(current);
      const match = line.match(RIVER_HEADING);
      if (match) current.river = RIVER_NUMBERS[fold(match[1])] || null;
    }
    current.lines.push(line);
  }
  return chapters.map((chapter) => ({ river: chapter.river, text: chapter.lines.join("\n").replace(/\s+$/, "") }));
}

export function reorderStory(text, rivers) {
  if (!rivers.length) return text;
  const chapters = storyChapters(text);
  const first = chapters.findIndex((chapter) => chapter.river);
  if (first < 0) return text;
  const tail = chapters.slice(first);
  return [
    ...chapters.slice(0, first),
    ...tail.filter((chapter) => chapter.river && rivers.includes(chapter.river)),
    ...tail.filter((chapter) => !chapter.river),
    ...tail.filter((chapter) => chapter.river && !rivers.includes(chapter.river)),
  ]
    .map((chapter) => chapter.text)
    .filter(Boolean)
    .join("\n\n");
}
