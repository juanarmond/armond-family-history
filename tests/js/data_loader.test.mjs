// Unit tests for the pure projection logic in family-tree-viewer/data-loader.js.
// Run directly with `node --test tests/js/`, or via tests/test_data_loader_js.py
// inside `make check`.

import test from "node:test";
import assert from "node:assert/strict";

import { projectTreeData, evidenceHref } from "../../family-tree-viewer/data-loader.js";

function fixtures() {
  const people = {
    "P-1": {
      id: "P-1",
      preferred_name: "Ann Alpha",
      privacy: "deceased",
      nationality: "Brazilian",
      name_variants: [{ value: "Ann Alpha" }, { value: "Anna Alpha" }],
      occupations: [{ value: "lavrador", source_ids: ["S-1"], note: "test note" }],
      profile: "## Identity\nAnn's English portrait.",
      profile_pt: "## Identidade\nRetrato de Ann em português.",
      notes: [
        {
          text: "Possible conflict with the civil record.",
          text_pt: "Possível conflito com o registo civil.",
        },
        { text: "A note with no translation." },
      ],
    },
    "P-2": {
      id: "P-2",
      preferred_name: "Bob Beta",
      privacy: "deceased",
      name_variants: [{ value: "Bob Beta" }],
      notes: [],
    },
    "P-3": {
      id: "P-3",
      preferred_name: "Private living person",
      privacy: "living",
      nationality: "Brazilian",
      name_variants: [{ value: "A Real Living Name" }],
      occupations: [{ value: "secret job", source_ids: ["S-1"] }],
      profile: "Secret living portrait.",
      notes: [{ text: "Sensitive living-person note." }],
      event_ids: ["E-4"],
    },
    "P-4": { id: "P-4", preferred_name: "Cara Gamma", privacy: "deceased" },
    "P-5": { id: "P-5", preferred_name: "Dan Delta", privacy: "deceased" },
  };

  const families = {
    "F-1": {
      id: "F-1",
      partners: [
        { person_id: "P-1", role: "parent" },
        { person_id: "P-2", role: "parent" },
      ],
      children: [
        {
          person_id: "P-4",
          parent_relationships: [
            { parent_id: "P-1", relationship_type: "unknown", status: "confirmed", source_ids: ["S-1"] },
            { parent_id: "P-2", relationship_type: "unknown", status: "hypothesis", source_ids: ["S-1"] },
          ],
        },
        { person_id: "P-5" },
        { person_id: "P-3" },
      ],
      documented_children: [
        { name: "Baby Delta", source_ids: ["S-1"], lifespan: "1878–1879", note: "died young" },
      ],
    },
  };

  const events = {
    "E-1": {
      id: "E-1",
      event_type: "marriage",
      date: { kind: "exact", value: "1900-05-01" },
      place_id: "PL-1",
      participants: [
        { person_id: "P-1", role: "spouse" },
        { person_id: "P-2", role: "spouse" },
      ],
      status: "strong-evidence",
      source_ids: ["S-1"],
    },
    "E-2": {
      id: "E-2",
      event_type: "birth",
      date: { kind: "year", year: 1875 },
      place_id: "PL-1",
      participants: [{ person_id: "P-4", role: "principal" }],
      status: "confirmed",
      source_ids: ["S-2"],
    },
    "E-3": {
      id: "E-3",
      event_type: "death",
      date: { kind: "year", year: 1950 },
      participants: [
        { person_id: "P-4", role: "principal" },
        { person_id: "P-1", role: "parent" },
      ],
      status: "confirmed",
      source_ids: ["S-2"],
    },
    "E-4": {
      id: "E-4",
      event_type: "birth",
      date: { kind: "year", year: 1990 },
      participants: [{ person_id: "P-3", role: "principal" }],
      status: "confirmed",
      source_ids: [],
    },
  };

  const places = { "PL-1": { id: "PL-1", preferred_name: "Rio de Janeiro, Brazil" } };

  const sources = {
    "S-1": {
      id: "S-1",
      title: "Civil marriage record",
      record_type: "Civil marriage register entry",
      source_form: "original",
      information_quality: "primary",
      reliability: { limitations: "The ink is faded in places." },
      transcription: "Marriage entry text.",
      transcription_pt: "Texto do assento de casamento.",
      abstract: "A civil marriage.",
      abstract_pt: "Um casamento civil.",
      repository: { url: "https://example.org/s1", repository_path: "evidence/civil/S-1.jpg" },
      digital_file: { path: "evidence/civil/S-1.jpg" },
      private: true,
      linked_people: ["P-1", "P-2", "P-4"],
    },
    "S-2": {
      id: "S-2",
      title: "Owner-supplied recollection",
      record_type: "Family recollection",
      repository: { repository_path: "STATUS.md" },
      private: true,
      linked_people: ["P-4"],
    },
  };

  const fan = {
    "FAN-1": {
      id: "FAN-1",
      title: "1900 deed witnessed by Ann",
      record_type: "Escritura",
      record_category: "notarial",
      usage: "context",
      event_date: { kind: "year", year: 1900 },
      event_place_text: "Muriaé, Minas Gerais, Brazil",
      transcription: "… Ann Alpha, testemunha …",
      abstract: "A deed Ann witnessed.",
      repository: { url: "https://example.org/fan1" },
      digital_file: { path: "evidence/references/FAN-1.jpg" },
      participants: [{ person_id: "P-1", role: "testemunha", note: "witness" }],
    },
    "FAN-2": {
      id: "FAN-2",
      title: "A living person's context record",
      record_type: "Inventário",
      record_category: "court_or_probate",
      usage: "context",
      digital_file: { path: "evidence/references/FAN-2.jpg" },
      participants: [{ person_id: "P-3", role: "credor" }],
    },
  };

  return { people, families, events, places, sources, fan };
}

test("evidenceHref only exposes files under evidence/", () => {
  assert.equal(evidenceHref("evidence/civil/x.jpg"), "../evidence/civil/x.jpg");
  assert.equal(evidenceHref("evidence/parish/y.pdf"), "../evidence/parish/y.pdf");
  assert.equal(evidenceHref("STATUS.md"), null, "internal docs must not become file links");
  assert.equal(evidenceHref(null), null);
  assert.equal(evidenceHref(""), null);
});

test("parent relationships are grouped by child with status and family", () => {
  const data = projectTreeData(fixtures());
  const parents = data.parentsByChild["P-4"];
  assert.equal(parents.length, 2);
  const byId = Object.fromEntries(parents.map((p) => [p.parentId, p]));
  assert.equal(byId["P-1"].status, "confirmed");
  assert.equal(byId["P-2"].status, "hypothesis");
  assert.equal(byId["P-1"].familyId, "F-1");
});

test("a marriage event is matched to its family by spouse participants", () => {
  const data = projectTreeData(fixtures());
  const marriage = data.marriageByFamily["F-1"];
  assert.ok(marriage, "F-1 should have a matched marriage");
  assert.equal(marriage.date.value, "1900-05-01");
  assert.equal(marriage.place, "Rio de Janeiro, Brazil");
  assert.equal(marriage.status, "strong-evidence");
});

test("spouses are paired both ways with their marriage", () => {
  const data = projectTreeData(fixtures());
  const spouses = data.people["P-1"].spouses;
  assert.equal(spouses.length, 1);
  assert.equal(spouses[0].id, "P-2");
  assert.equal(spouses[0].name, "Bob Beta");
  assert.equal(spouses[0].marriage.date.value, "1900-05-01");
  assert.equal(data.people["P-2"].spouses[0].id, "P-1");
});

test("conflict is detected from notes and variants", () => {
  const data = projectTreeData(fixtures());
  assert.equal(data.people["P-1"].hasConflict, true);
  assert.equal(data.people["P-2"].hasConflict, false);
});

test("occupations are projected for the deceased and stripped for the living", () => {
  const data = projectTreeData(fixtures());
  const occ = data.people["P-1"].occupations;
  assert.equal(occ.length, 1);
  assert.equal(occ[0].value, "lavrador");
  assert.equal(occ[0].note, "test note");
  assert.deepEqual(occ[0].sourceIds, ["S-1"]);
  assert.deepEqual(data.people["P-3"].occupations, []);
});

test("source view gates files and carries citation metadata", () => {
  const data = projectTreeData(fixtures());
  const s1 = data.sources["S-1"];
  assert.equal(s1.file, "../evidence/civil/S-1.jpg");
  assert.equal(s1.url, "https://example.org/s1");
  assert.equal(s1.sourceForm, "original");
  assert.equal(s1.quality, "primary");
  assert.equal(s1.limitation, "The ink is faded in places.");
  assert.equal(s1.private, true);

  const s2 = data.sources["S-2"];
  assert.equal(s2.file, null, "a repository_path of STATUS.md must not become a file link");
  assert.equal(s2.url, null);
});

test("a deceased person aggregates sources from links, events and relationships", () => {
  const data = projectTreeData(fixtures());
  const p4 = data.people["P-4"];
  assert.equal(p4.sourceCount, 2, "P-4 should gather S-1 (link/relationship) and S-2 (event)");
  const ids = p4.sources.map((s) => s.id).sort();
  assert.deepEqual(ids, ["S-1", "S-2"]);
});

test("an event lands only on its subject, not on people it merely references", () => {
  const data = projectTreeData(fixtures());
  // P-1 is only a "parent" in P-4's death (E-3), so E-3 must not be on P-1's timeline.
  assert.deepEqual(
    data.people["P-1"].events.map((e) => e.type).sort(),
    ["marriage"],
  );
  // P-4 is the principal of both its birth (E-2) and death (E-3).
  assert.deepEqual(
    data.people["P-4"].events.map((e) => e.type).sort(),
    ["birth", "death"],
  );
});

test("living people are minimised", () => {
  const data = projectTreeData(fixtures());
  const p3 = data.people["P-3"];
  assert.deepEqual(p3.nameVariants, []);
  assert.deepEqual(p3.sources, []);
  assert.deepEqual(p3.spouses, []);
  assert.deepEqual(p3.notes, []);
  assert.deepEqual(p3.occupations, []);
  assert.deepEqual(p3.fanReferences, []);
  assert.deepEqual(p3.siblings, []);
  assert.deepEqual(p3.children, []);
  assert.deepEqual(p3.events, [], "a living person's own events (birth/death PII) are redacted");
});

test("children include modelled deceased and documented children of a person's unions, omitting the living", () => {
  const data = projectTreeData(fixtures());
  const kids = data.people["P-1"].children;
  const persons = kids.filter((s) => s.type === "person").map((s) => s.id).sort();
  assert.deepEqual(persons, ["P-4", "P-5"], "deceased modelled children appear; the living P-3 is omitted");
  const documented = kids.filter((s) => s.type === "documented");
  assert.equal(documented.length, 1);
  assert.equal(documented[0].name, "Baby Delta");
  // P-2 is the other partner of F-1 and shares the same children.
  const p2 = data.people["P-2"].children.filter((s) => s.type === "person").map((s) => s.id).sort();
  assert.deepEqual(p2, ["P-4", "P-5"]);
});

test("siblings include modelled deceased and documented children, omitting the living", () => {
  const data = projectTreeData(fixtures());
  const sibs = data.people["P-4"].siblings;
  const persons = sibs.filter((s) => s.type === "person").map((s) => s.id);
  assert.ok(persons.includes("P-5"), "a deceased modelled sibling appears");
  assert.ok(!persons.includes("P-3"), "a possibly-living modelled sibling is omitted");
  const documented = sibs.filter((s) => s.type === "documented");
  assert.equal(documented.length, 1);
  assert.equal(documented[0].name, "Baby Delta");
  assert.equal(documented[0].lifespan, "1878–1879");
  assert.deepEqual(documented[0].sourceIds, ["S-1"]);
});

test("FAN references are projected per person with role, place and transcription", () => {
  const data = projectTreeData(fixtures());
  const refs = data.people["P-1"].fanReferences;
  assert.equal(refs.length, 1);
  assert.equal(refs[0].id, "FAN-1");
  assert.equal(refs[0].role, "testemunha");
  assert.equal(refs[0].recordCategory, "notarial");
  assert.equal(refs[0].place, "Muriaé, Minas Gerais, Brazil");
  assert.equal(refs[0].transcription, "… Ann Alpha, testemunha …");
  assert.equal(refs[0].file, "../evidence/references/FAN-1.jpg");
  assert.equal(data.people["P-2"].fanReferences.length, 0);
});

test("nationality is projected, defaults to null, and is kept for the living", () => {
  const data = projectTreeData(fixtures());
  assert.equal(data.people["P-1"].nationality, "Brazilian");
  assert.equal(data.people["P-4"].nationality, null, "absent nationality projects as null");
  assert.equal(
    data.people["P-3"].nationality,
    "Brazilian",
    "nationality is low-sensitivity and is not redacted for living people",
  );
});

test("source view carries transcription and abstract", () => {
  const data = projectTreeData(fixtures());
  assert.equal(data.sources["S-1"].transcription, "Marriage entry text.");
  assert.equal(data.sources["S-1"].abstract, "A civil marriage.");
  assert.equal(data.sources["S-2"].transcription, null);
});

test("source view carries Portuguese translations of transcription and abstract", () => {
  const data = projectTreeData(fixtures());
  assert.equal(data.sources["S-1"].transcriptionPt, "Texto do assento de casamento.");
  assert.equal(data.sources["S-1"].abstractPt, "Um casamento civil.");
  // A source with no Portuguese translation projects null (viewer falls back to EN).
  assert.equal(data.sources["S-2"].transcriptionPt, null);
  assert.equal(data.sources["S-2"].abstractPt, null);
});

test("research notes project as bilingual { en, pt } pairs", () => {
  const data = projectTreeData(fixtures());
  assert.deepEqual(data.people["P-1"].notes, [
    {
      en: "Possible conflict with the civil record.",
      pt: "Possível conflito com o registo civil.",
    },
    { en: "A note with no translation.", pt: null },
  ]);
});

test("the per-person profile (Portrait) projects with its Portuguese variant, gated for the living", () => {
  const data = projectTreeData(fixtures());
  assert.equal(data.people["P-1"].profile, "## Identity\nAnn's English portrait.");
  assert.equal(data.people["P-1"].profilePt, "## Identidade\nRetrato de Ann em português.");
  // A deceased person without a profile projects null (not undefined).
  assert.equal(data.people["P-2"].profile, null);
  assert.equal(data.people["P-2"].profilePt, null);
  // Living people are minimised — no profile leaks even if the source file has one.
  assert.equal(data.people["P-3"].profile, null);
  assert.equal(data.people["P-3"].profilePt, null);
});

test("source view carries a file type for image vs pdf", () => {
  const input = {
    people: {},
    families: {},
    events: {},
    places: {},
    sources: {
      "CIV-1": { title: "img", linked_people: ["P-1"], digital_file: { path: "evidence/civil/x.jpg" } },
      "CIV-2": { title: "pdf", linked_people: ["P-1"], digital_file: { path: "evidence/civil/y.pdf" } },
    },
    fan: {},
  };
  const data = projectTreeData(input);
  assert.equal(data.sources["CIV-1"].fileType, "image");
  assert.equal(data.sources["CIV-2"].fileType, "pdf");
});

test("a person's sources are ordered by life event, supporting records last", () => {
  const input = {
    people: {
      "P-1": {
        id: "P-1", preferred_name: "Test Person", privacy: "deceased",
        name_variants: [], event_ids: ["E-b", "E-m", "E-d"], family_ids: [], notes: [],
      },
    },
    families: {},
    events: {
      "E-b": { id: "E-b", event_type: "birth", date: { kind: "year", year: 1900 }, participants: [{ person_id: "P-1", role: "principal" }], source_ids: ["CIV-b"], status: "confirmed" },
      "E-m": { id: "E-m", event_type: "marriage", date: { kind: "year", year: 1925 }, participants: [{ person_id: "P-1", role: "principal" }], source_ids: ["CIV-m"], status: "confirmed" },
      "E-d": { id: "E-d", event_type: "death", date: { kind: "year", year: 1970 }, participants: [{ person_id: "P-1", role: "principal" }], source_ids: ["CIV-d"], status: "confirmed" },
    },
    places: {},
    sources: {
      "CIV-d": { title: "death", record_category: "civil_registration", linked_people: ["P-1"] },
      "CIV-m": { title: "marriage", record_category: "civil_registration", linked_people: ["P-1"] },
      "CIV-b": { title: "birth", record_category: "civil_registration", linked_people: ["P-1"] },
      "PUB-1": { title: "thesis", record_category: "published_genealogy", linked_people: ["P-1"] },
    },
    fan: {},
  };
  const data = projectTreeData(input);
  const order = data.people["P-1"].sources.map((s) => s.id);
  assert.deepEqual(order, ["CIV-b", "CIV-m", "CIV-d", "PUB-1"]);
});

test("an uncertain transcription flags the source but not the person; only explicit conflict notes flag hasConflict", () => {
  const input = {
    people: {
      "P-1": { id: "P-1", preferred_name: "A", privacy: "deceased", name_variants: [], event_ids: [], family_ids: [], notes: [] },
      "P-2": { id: "P-2", preferred_name: "B", privacy: "deceased", name_variants: [], event_ids: [], family_ids: [], notes: [{ text: "unresolved conflict in birth date" }] },
      "P-3": { id: "P-3", preferred_name: "C", privacy: "deceased", name_variants: [], event_ids: [], family_ids: [], notes: [] },
    },
    families: {},
    events: {},
    places: {},
    sources: {
      "CIV-1": { title: "x", transcription: "compareceu [uncertain: Fulano] de tal", linked_people: ["P-1"] },
      "CIV-2": { title: "y", transcription: "a clean, fully legible reading", linked_people: ["P-3"] },
    },
    fan: {},
  };
  const data = projectTreeData(input);
  // Uncertain transcription is flagged on the source itself.
  assert.equal(data.sources["CIV-1"].uncertain, true);
  assert.equal(data.sources["CIV-2"].uncertain, false);
  // An uncertain transcription does NOT flag hasConflict on the person card —
  // illegible words are a source-quality note, already shown in the detail panel.
  assert.equal(data.people["P-1"].hasConflict, false);
  // An explicit conflict/unresolved note in the person's notes DOES flag hasConflict.
  assert.equal(data.people["P-2"].hasConflict, true);
  // No conflict note and no uncertain source → not flagged.
  assert.equal(data.people["P-3"].hasConflict, false);
});

test("biography summarises birth, parents, marriage, children, emigration and death", () => {
  const input = {
    people: {
      "P-1": { id: "P-1", preferred_name: "João Bittencourt", privacy: "deceased", sex: "male", name_variants: [], event_ids: ["E-b", "E-d"], family_ids: ["F-1"], notes: [] },
      "P-2": { id: "P-2", preferred_name: "Manoel Bittencourt", privacy: "deceased", sex: "male", name_variants: [], event_ids: [], family_ids: ["F-0"], notes: [] },
      "P-3": { id: "P-3", preferred_name: "Susana Brandão", privacy: "deceased", sex: "female", name_variants: [], event_ids: ["E-m"], family_ids: ["F-1"], notes: [] },
      "P-4": { id: "P-4", preferred_name: "Deocleciano", privacy: "deceased", sex: "male", name_variants: [], event_ids: [], family_ids: ["F-1"], notes: [] },
    },
    families: {
      "F-0": { id: "F-0", partners: [{ person_id: "P-2", role: "parent" }], children: [{ person_id: "P-1", parent_relationships: [{ parent_id: "P-2", status: "confirmed", source_ids: ["S-1"] }] }] },
      "F-1": {
        id: "F-1",
        partners: [{ person_id: "P-1", role: "spouse" }, { person_id: "P-3", role: "spouse" }],
        partner_relationship: { status: "confirmed", source_ids: ["S-1"] },
        children: [{ person_id: "P-4", parent_relationships: [{ parent_id: "P-1", status: "confirmed", source_ids: ["S-1"] }] }],
        event_ids: ["E-m"],
      },
    },
    events: {
      "E-b": { id: "E-b", event_type: "birth", date: { kind: "approximate", text: "about 1847", earliest: 1847 }, place_text: "Ilha de São Miguel, Açores, Portugal", participants: [{ person_id: "P-1", role: "principal" }], source_ids: ["S-1"], status: "confirmed" },
      "E-d": { id: "E-d", event_type: "death", date: { kind: "exact", value: "1915-09-12" }, place_text: "Carangola, Minas Gerais, Brazil", participants: [{ person_id: "P-1", role: "principal" }], source_ids: ["S-1"], status: "confirmed" },
      "E-m": { id: "E-m", event_type: "marriage", date: { kind: "year", year: 1882 }, place_text: "Sapucaia, Rio de Janeiro, Brazil", participants: [{ person_id: "P-1", role: "spouse" }, { person_id: "P-3", role: "spouse" }], source_ids: ["S-1"], status: "confirmed" },
    },
    places: {},
    sources: { "S-1": { title: "x", linked_people: ["P-1"] } },
    fan: {},
  };
  const data = projectTreeData(input);
  const bio = data.people["P-1"].biography;
  assert.equal(bio.birth.place, "Ilha de São Miguel, Açores, Portugal");
  assert.deepEqual(bio.birth.parents, ["Manoel Bittencourt"]);
  assert.equal(bio.birth.emigratedToBrazil, true); // foreign birth + Brazilian death
  assert.equal(bio.marriages[0].spouse, "Susana Brandão");
  assert.deepEqual(bio.children, ["Deocleciano"]);
  assert.equal(bio.death.place, "Carangola, Minas Gerais, Brazil");
  assert.equal(bio.death.age.years, 68); // 1915 - 1847
  assert.equal(bio.death.age.approx, true); // approximate birth year
  // A person known only through a child is not sparse; it drives the "parent of" lead.
  const manoel = data.people["P-2"].biography;
  assert.equal(manoel.parentsOnly, true);
  assert.deepEqual(manoel.children, ["João Bittencourt"]);
});

test("living people get no biography", () => {
  const input = {
    people: { "P-1": { id: "P-1", preferred_name: "Living Person", privacy: "living", sex: "male", name_variants: [], event_ids: [], family_ids: [], notes: [] } },
    families: {}, events: {}, places: {}, sources: {}, fan: {},
  };
  const data = projectTreeData(input);
  assert.equal(data.people["P-1"].biography, null);
});

test("lineage traces the direct line from the subject (P-0001) to each person", () => {
  const input = {
    people: {
      "P-0001": { id: "P-0001", preferred_name: "Juan", privacy: "living", sex: "male", name_variants: [], event_ids: [], family_ids: ["F-1"], notes: [] },
      "P-2": { id: "P-2", preferred_name: "Luis", privacy: "deceased", sex: "male", name_variants: [], event_ids: [], family_ids: ["F-1", "F-2"], notes: [] },
      "P-3": { id: "P-3", preferred_name: "Cidalia", privacy: "deceased", sex: "female", name_variants: [], event_ids: [], family_ids: ["F-2"], notes: [] },
    },
    families: {
      "F-1": { id: "F-1", partners: [{ person_id: "P-2", role: "parent" }], children: [{ person_id: "P-0001", parent_relationships: [{ parent_id: "P-2", status: "confirmed", source_ids: ["S-1"] }] }] },
      "F-2": { id: "F-2", partners: [{ person_id: "P-3", role: "parent" }], children: [{ person_id: "P-2", parent_relationships: [{ parent_id: "P-3", status: "confirmed", source_ids: ["S-1"] }] }] },
    },
    events: {}, places: {}, sources: { "S-1": { title: "x", linked_people: ["P-2"] } }, fan: {},
  };
  const data = projectTreeData(input);
  const cidalia = data.people["P-3"].lineage;
  assert.deepEqual(cidalia.ids, ["P-0001", "P-2", "P-3"]); // Juan → Luis → Cidalia
  assert.equal(cidalia.relationship.kind, "ancestor");
  assert.equal(cidalia.relationship.degree, 2);
  assert.equal(cidalia.relationship.side, "paternal"); // via Juan's father Luis
  // The subject has no lineage to itself; living people are not given one.
  assert.equal(data.people["P-0001"].lineage, null);
});
