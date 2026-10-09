// Unit tests for the family-branch logic in family-tree-viewer/branches.js.
// Run directly with `node --test tests/js/`, or via tests/test_data_loader_js.py
// inside `make check`.

import test from "node:test";
import assert from "node:assert/strict";

import {
  branchSides,
  computeBranches,
  entryBranches,
  entryInScope,
  inScope,
  isCurated,
  normaliseScope,
  parseScope,
  reorderStory,
  scopeRoot,
  scopeSize,
  serialiseScope,
  storyChapters,
  surnameIndex,
  surnameKey,
  updateKey,
  yearOfDate,
} from "../../family-tree-viewer/branches.js";

const born = (year) => [{ type: "birth", role: "principal", date: { kind: "exact", value: `${year}-01-01` } }];
const person = (id, name, sex, extra = {}) => ({ id, name, sex, privacy: "deceased", events: [], children: [], spouses: [], ...extra });
const parent = (parentId, status = "confirmed") => ({ parentId, status });

// The subject and both parents are living; each grandparent heads a branch.
const people = {
  "P-0001": person("P-0001", "Private living person", "male", { privacy: "living" }),
  "P-0002": person("P-0002", "Private living person", "male", { privacy: "living" }),
  "P-0003": person("P-0003", "Private living person", "female", { privacy: "living" }),
  "P-0004": person("P-0004", "Geraldo Paz Armond", "male", { events: born(1915) }),
  "P-0005": person("P-0005", "Cidalia Engracio Guimarães", "female", { events: born(1930) }),
  "P-0006": person("P-0006", "Antenor Muniz", "male", { events: born(1923) }),
  "P-0007": person("P-0007", "Iris Bohrer Muniz", "female", { events: born(1929) }),
  "P-0014": person("P-0014", "João Gonçalves Bohrer", "male", { events: born(1894) }),
  "P-0015": person("P-0015", "Celina Borer", "female", { events: born(1899) }),
  "P-0016": person("P-0016", "Maria de Jesus", "female", { events: born(1870) }),
  "P-0020": person("P-0020", "Aristão Ferreira Armond", "male", {
    events: born(1880),
    children: [{ type: "person", id: "P-0004", name: "Geraldo Paz Armond" }, { type: "person", id: "P-0018", name: "José Olavo Armond" }],
  }),
  "P-0018": person("P-0018", "José Olavo Armond", "male", { spouses: [{ id: "P-0030" }] }),
  "P-0030": person("P-0030", "Anna Clara", "female"),
  "P-0099": person("P-0099", "Rejected Father Bohrer", "male", { events: born(1700) }),
  // Unconnected, but her name makes Ferreira a known surname.
  "P-0040": person("P-0040", "Rosa Ferreira", "female"),
};
const parentsByChild = {
  "P-0001": [parent("P-0002"), parent("P-0003")],
  "P-0002": [parent("P-0004"), parent("P-0005")],
  "P-0003": [parent("P-0006"), parent("P-0007")],
  "P-0004": [parent("P-0020")],
  "P-0007": [parent("P-0014"), parent("P-0015")],
  "P-0014": [parent("P-0099", "rejected"), parent("P-0016", "hypothesis")],
};
const info = computeBranches({ people, parentsByChild });

test("a branch is a grandparent's line: ancestors, plus collaterals and their spouses", () => {
  assert.deepEqual(info.byKey.bohrer.members, ["P-0007", "P-0014", "P-0015", "P-0016"]);
  assert.deepEqual(info.byKey.armond.members, ["P-0004", "P-0018", "P-0020", "P-0030"]);
  assert.equal(info.byKey.bohrer.generations, 3);
  assert.equal(info.byKey.bohrer.earliestYear, 1870);
  assert.ok(!info.personBranches["P-0099"], "a rejected parentage edge is not followed");
  for (const id of ["P-0001", "P-0002", "P-0003"]) assert.ok(!info.personBranches[id], "the living subject and parents are in no branch");
});

test("sides come from the tree alone, even when a living parent's sex is withheld", () => {
  const unsexed = { ...people, "P-0002": { ...people["P-0002"], sex: "unknown" }, "P-0003": { ...people["P-0003"], sex: "unknown" } };
  const sides = branchSides(computeBranches({ people: unsexed, parentsByChild }));
  assert.deepEqual(sides.map((side) => side.parentId), ["P-0002", "P-0003"]);
  assert.deepEqual(sides.map((side) => side.branches.map((branch) => branch.key)), [["armond", "engracio"], ["muniz", "bohrer"]]);
});

test("a scoped tree starts at the grandparent, the shared child, or the subject", () => {
  assert.equal(scopeRoot(info, new Set()), "P-0001");
  assert.equal(scopeRoot(info, new Set(["bohrer"])), "P-0007");
  assert.equal(scopeRoot(info, new Set(["muniz", "bohrer"])), "P-0003");
  assert.equal(scopeRoot(info, new Set(["armond", "bohrer"])), "P-0001");
});

test("scopes parse, normalise and serialise in branch order; all four is everything", () => {
  assert.equal(serialiseScope(parseScope("bohrer,muniz", info), info), "muniz,bohrer");
  assert.equal(parseScope("all", info).size, 0);
  assert.equal(parseScope("", info).size, 0);
  assert.deepEqual([...parseScope("bohrer,nonsense", info)], ["bohrer"]);
  assert.equal(normaliseScope(["armond", "engracio", "muniz", "bohrer"], info).size, 0);
  assert.equal(serialiseScope(new Set(), info), "all");
});

test("people are in scope through their branch; everything includes everyone", () => {
  const bohrer = new Set(["bohrer"]);
  assert.ok(inScope(info, bohrer, "P-0015"));
  assert.ok(!inScope(info, bohrer, "P-0004"));
  assert.ok(!inScope(info, bohrer, "P-0001"));
  assert.ok(inScope(info, new Set(), "P-0001"));
  assert.equal(scopeSize(info, bohrer, 14), 4);
  assert.equal(scopeSize(info, new Set(), 14), 14);
});

test("surnames: spellings merge, and devotional or given names are not surnames", () => {
  assert.equal(surnameKey("Bohrer"), surnameKey("Borer"));
  const index = surnameIndex(people, info.byKey.bohrer.members, info.vocabulary);
  const bohrer = index.find((entry) => entry.key === surnameKey("Bohrer"));
  assert.deepEqual(bohrer.ids, ["P-0015", "P-0007", "P-0014"]);
  assert.equal(bohrer.label, "Bohrer / Borer");
  assert.ok(!index.some((entry) => entry.key === surnameKey("Jesus")), "“de Jesus” is devotional");
  const armond = surnameIndex(people, info.byKey.armond.members, info.vocabulary);
  assert.ok(!armond.some((entry) => entry.key === surnameKey("Clara")), "“Anna Clara” has no surname");
  assert.ok(armond.some((entry) => entry.key === surnameKey("Ferreira")), "a middle word counts once it ends someone's name");
  assert.ok(!armond.some((entry) => entry.key === surnameKey("Olavo")), "a second given name does not");
});

test("an update belongs to the branches of the people and records it links", () => {
  const sources = { "CIV-1": { linkedPeople: ["P-0015", "P-0001"] } };
  assert.deepEqual([...entryBranches({ links: ["P-0004"] }, info, sources)], ["armond"]);
  assert.deepEqual([...entryBranches({ primary: "CIV-1" }, info, sources)], ["bohrer"]);
  assert.ok(entryInScope({ primary: "CIV-1" }, info, new Set(["bohrer"]), sources));
  assert.ok(!entryInScope({ links: ["P-0004"] }, info, new Set(["bohrer"]), sources));
  assert.ok(entryInScope({ title: "A site-wide note" }, info, new Set(["bohrer"]), sources), "no branch means every scope");
});

test("only curated entries count as news, keyed by date and title", () => {
  assert.ok(isCurated({ kind: "milestone" }));
  assert.ok(isCurated({ kind: "correction" }));
  assert.ok(!isCurated({ kind: "document" }));
  assert.ok(!isCurated({}));
  assert.equal(updateKey({ date: "2026-10-08", title: "News" }), "2026-10-08|News");
});

test("the story puts the chosen rivers first and the other rivers last, in either language", () => {
  const story = [
    "## Prologue", "Opening.", "",
    "## RIVER ONE — the Armond", "### A house", "One.", "",
    "## RIVER TWO — the Guimarães", "Two.", "",
    "## RIVER THREE — the Muniz", "Three.", "",
    "## RIVER FOUR — the Bohrer", "Four.", "",
    "## THE CONFLUENCE", "Together.",
  ].join("\n");
  assert.deepEqual(storyChapters(story).map((chapter) => chapter.river), [null, 1, 2, 3, 4, null]);
  const reordered = reorderStory(story, [3, 4]);
  assert.deepEqual(storyChapters(reordered).map((chapter) => chapter.river), [null, 3, 4, null, 1, 2]);
  assert.ok(reordered.includes("### A house\nOne."), "sub-chapters move with their river");
  assert.equal(reorderStory(story, []), story);
  const pt = "## Prólogo\nAbertura.\n\n## RIO UM — os Armond\nUm.\n\n## RIO TRÊS — os Muniz\nTrês.";
  assert.deepEqual(storyChapters(reorderStory(pt, [3])).map((chapter) => chapter.river), [null, 3, 1]);
});

test("years come from any recorded date shape", () => {
  assert.equal(yearOfDate({ kind: "exact", value: "1892-06-25" }), 1892);
  assert.equal(yearOfDate({ kind: "month", year: 1892, month: 6 }), 1892);
  assert.equal(yearOfDate({ kind: "approximate", text: "about 1898", earliest: 1897, latest: 1898 }), 1897);
  assert.equal(yearOfDate({ kind: "approximate", text: "c.1894 (aged 76)" }), 1894);
  assert.equal(yearOfDate(null), null);
});
