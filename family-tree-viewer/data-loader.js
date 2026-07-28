import { load as parseYaml } from "https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/+esm";

const ENTITY_TYPES = {
  people: { directory: "people" },
  families: { directory: "families" },
  events: { directory: "events" },
  places: { directory: "places" },
  sources: { directory: "sources" },
};

const DATA_ROOT = "../data";
const INDEX_PATH = "./entity-index.json";

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
      const entity = await fetchYaml(`${DATA_ROOT}/${directory}/${id}.yaml`);
      if (!entity || entity.id !== id) {
        throw new Error(`Entity ${id} is missing or does not match its indexed identifier.`);
      }
      return [id, entity];
    }),
  );
  return Object.fromEntries(entries);
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
  for (const note of person.notes || []) {
    for (const id of note?.source_ids || []) if (typeof id === "string") ids.add(id);
  }
  return ids;
}

export async function loadTreeData() {
  const [people, families, events, places, sources] = await Promise.all(
    Object.entries(ENTITY_TYPES).map(([kind, config]) => loadEntityType(kind, config)),
  );

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
      personEvents[personId].push(eventView);
      for (const sourceId of eventView.sourceIds) personSourceIds[personId].add(sourceId);
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

  const sourceView = Object.fromEntries(
    Object.entries(sources).map(([sourceId, source]) => [sourceId, {
      id: sourceId,
      title: source.title || sourceId,
      recordType: source.record_type || "Source",
      private: Boolean(source.private),
    }]),
  );

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
      nameVariants: living ? [] : variants,
      events: [...(personEvents[personId] || [])].sort((a, b) =>
        `${a.type}${JSON.stringify(a.date)}`.localeCompare(`${b.type}${JSON.stringify(b.date)}`),
      ),
      sourceCount: sourceIds.length,
      sources: living ? [] : sourceIds.map((id) => sourceView[id]).filter(Boolean),
      notes,
      hasConflict: conflictTerms.some((term) => conflictText.includes(term)),
    };
  }

  return {
    schemaVersion: 1,
    people: peopleView,
    parentsByChild,
    sources: sourceView,
    familyCount: Object.keys(families).length,
  };
}
