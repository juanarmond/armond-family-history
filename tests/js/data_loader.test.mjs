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
      name_variants: [{ value: "Ann Alpha" }, { value: "Anna Alpha" }],
      occupations: [{ value: "lavrador", source_ids: ["S-1"], note: "test note" }],
      notes: [{ text: "Possible conflict with the civil record." }],
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
      name_variants: [{ value: "A Real Living Name" }],
      occupations: [{ value: "secret job", source_ids: ["S-1"] }],
      notes: [{ text: "Sensitive living-person note." }],
    },
    "P-4": { id: "P-4", preferred_name: "Cara Gamma", privacy: "deceased" },
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

  return { people, families, events, places, sources };
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
});
