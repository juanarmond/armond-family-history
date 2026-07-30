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
  // Stored paths are repository-root relative; the viewer lives one level down.
  return `../${clean}`;
}

function noteTexts(notes) {
  if (!Array.isArray(notes)) return [];
  return notes
    .map((note) => {
      if (typeof note === "string") return note.trim();
      if (note && typeof note.text === "string") return note.text.trim();
      return "";
    })
    .filter(Boolean);
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
      if (role === "principal" || role === "spouse" || role === "partner") {
        personEvents[personId].push({ ...eventView, role });
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

  const sourceView = Object.fromEntries(
    Object.entries(sources).map(([sourceId, source]) => {
      const rawPath = source.digital_file?.path || source.repository?.repository_path || null;
      const url = source.repository?.url;
      const limitation = source.reliability?.limitations;
      return [sourceId, {
        id: sourceId,
        title: source.title || sourceId,
        recordType: source.record_type || "Source",
        sourceForm: typeof source.source_form === "string" ? source.source_form.replaceAll("_", " ") : null,
        quality: typeof source.information_quality === "string" ? source.information_quality : null,
        limitation: typeof limitation === "string" && limitation.trim() ? limitation.trim() : null,
        private: Boolean(source.private),
        transcription:
          typeof source.transcription === "string" && source.transcription.trim()
            ? source.transcription.trim()
            : null,
        abstract:
          typeof source.abstract === "string" && source.abstract.trim()
            ? source.abstract.trim()
            : null,
        file: evidenceHref(rawPath),
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
        recordType: ref.record_type || "Reference",
        recordCategory:
          typeof ref.record_category === "string"
            ? ref.record_category.replaceAll("_", " ")
            : null,
        date: ref.event_date || null,
        place: trimmedText(ref.event_place_text),
        transcription: trimmedText(ref.transcription),
        abstract: trimmedText(ref.abstract),
        file: evidenceHref(ref.digital_file?.path || null),
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

  // Siblings, per person, computed from their parent family's other children:
  // modelled children (other P- entities) plus documented_children (attested
  // siblings not modelled as entities). Possibly-living siblings are omitted
  // entirely — only clearly deceased people appear.
  const siblingsByPerson = {};
  for (const personId of Object.keys(people)) siblingsByPerson[personId] = [];
  for (const family of Object.values(families)) {
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
    for (const meId of modelledChildIds) {
      if (!siblingsByPerson[meId]) continue;
      for (const otherId of modelledChildIds) {
        if (otherId === meId) continue;
        const sib = people[otherId];
        if (!sib || (sib.privacy || "unknown") !== "deceased") continue;
        siblingsByPerson[meId].push({ type: "person", id: otherId, name: sib.preferred_name || otherId });
      }
      for (const entry of documented) siblingsByPerson[meId].push({ ...entry });
    }
  }

  const conflictTerms = ["conflict", "uncertain", "unresolved", "variant", "pending"];
  const peopleView = {};

  for (const [personId, person] of Object.entries(people)) {
    const privacy = person.privacy || "unknown";
    const living = privacy === "living";
    const variants = (person.name_variants || [])
      .map((variant) => variant?.value)
      .filter((value) => typeof value === "string");
    const notes = living ? [] : noteTexts(person.notes || []);
    const sourceIds = [...(personSourceIds[personId] || [])].sort();
    const conflictText = [...notes, ...variants.slice(1)].join(" ").toLocaleLowerCase();

    peopleView[personId] = {
      id: personId,
      name: person.preferred_name || personId,
      privacy,
      nationality: typeof person.nationality === "string" && person.nationality.trim()
        ? person.nationality.trim()
        : null,
      nameVariants: living ? [] : variants,
      events: [...(personEvents[personId] || [])].sort((a, b) =>
        `${a.type}${JSON.stringify(a.date)}`.localeCompare(`${b.type}${JSON.stringify(b.date)}`),
      ),
      sourceCount: sourceIds.length,
      sources: living ? [] : sourceIds.map((id) => sourceView[id]).filter(Boolean),
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
      siblings: living ? [] : (siblingsByPerson[personId] || []),
      fanReferences: living
        ? []
        : (fanByPerson[personId] || []).slice().sort((a, b) => a.id.localeCompare(b.id)),
      hasConflict: conflictTerms.some((term) => conflictText.includes(term)),
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
