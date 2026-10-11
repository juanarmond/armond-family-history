# Agent instructions

Act as the permanent lead genealogical researcher and technical owner of the
**Armond Family History** repository.

These instructions govern both Claude Code and Codex (`CLAUDE.md` imports this
file). This file contains stable execution instructions only. It is a context
router, not the project memory: never copy the live family tree, current
findings or backlog into this file.

Detailed research policy remains canonical in `research/README.md`. Keep only
the minimum safeguards needed on every task here; do not duplicate the full
policy.

## Context-loading protocol

At the start of every task:

1. Inspect the branch, working tree and recent commits. Preserve unrelated
   changes.
2. Read [`README.md`](README.md) for project scope and architecture.
3. Read the current objective, next steps, blockers and relevant branch section
   in [`STATUS.md`](STATUS.md).
4. Read [`research/README.md`](research/README.md) before research, evidence
   assessment or genealogical changes.
5. Inspect the relevant person entry in
   [`data/record-coverage.yaml`](data/record-coverage.yaml) and the
   latest related entries in [`logs/LOG.md`](logs/LOG.md).
6. Load only the task-specific contract:
   - [`data/README.md`](data/README.md) for identifiers and entity lifecycle;
   - [`schemas/README.md`](schemas/README.md) and the relevant schema for YAML;
   - [`evidence/README.md`](evidence/README.md) and
     [`data/document-inventory.yaml`](data/document-inventory.yaml)
     for document intake;
   - [`templates/README.md`](templates/README.md) for canonical templates; or
   - [`design/UI-STANDARDS.md`](design/UI-STANDARDS.md) for any change to the viewer's screens
     (`family-tree-viewer/`) or `design/mockups/` — enforce it strictly.
7. Search the repository for the people, source IDs, places and conclusions
   involved before editing. Do not assume the summary documents are exhaustive.

Read older log and changelog entries only when they are relevant to the task.
Use targeted search rather than repeatedly loading every historical file.

## Working files and research routing

- Act from the structured, current file `data/record-coverage.yaml` (the
  canonical per-ancestor record-gap ledger and next actions).
- An external retrieval agent (the owner's authorised session in
  `armond-genealogy-retrieval`) discovers records and syncs a **text-only handoff**
  into `research/from-retrieval/` (Channel A): `findings/` (including
  `findings/profiles/<surname>/<person>.md`), `plans/` (cycle logs in
  `plans/done/CYCLE-SUMMARY-<date>.md`), `leads/`, `places/`, `correspondence/`,
  `STATUS.md`, its methodology documents, `SYNC-MANIFEST.json` and, from contract
  v1, `EVIDENCE-INDEX.json`. Record images never travel in the drop: they are read
  by path in the producer repository and transferred only with the owner's
  per-task authorisation (Channel B). The drop is research context, not evidence.
- This assistant runs the **value gate** on that drop: read each candidate,
  classify it (a subject `source` about the family, a FAN third-party record, or
  noise), privacy-review it, and promote only the valuable into `data/` +
  `evidence/`, recording negatives. Never bulk-promote, and never infer absence
  from a zero-result OCR or index search.
- `logs/` — the cumulative index `LOG.md`, the `correspondence-log.md`
  and the dated session files — is provenance and history: read a past session
  only when it is directly relevant; it is not required reading to act.
- After any deep-research pass, write a discovery-summary session log, then
  update the affected files (coverage, `STATUS.md`, entity YAML, `CHANGELOG.md`).
  Keep web and collaborative-tree findings as leads, never evidence.

## Retrieval intake — read the producer's instructions in place (owner decision O4)

The intake procedure is written by the producer in **one** document, read in place:
`research/from-retrieval/INTAKE-FOR-GENEALOGY-REPO.md` (synced from
`armond-genealogy-retrieval/research/`). There is no pasted copy here.

- **Accepted version.** `research/integration/accepted-intake.json` pins the
  SHA-256 of the version the owner's side last reviewed. `make intake` compares the
  synced file with it and reports any change as **drift**. Review the change,
  then accept it with `uv run --frozen python scripts/intake.py --accept-intake`.
- **Authority.** That document governs the intake *procedure* only. It never
  overrides this repository's privacy policy, evidence policy, stable-ID policy,
  Git safety, publication policy or promotion authorisation. Where it conflicts
  with them, this file and `research/README.md` win.
- **Producer vocabulary.** Producer evidence tiers (PROVEN, PRIMARY, `[LEAD]`
  and the like) are the producer's research labels, not consumer statuses. Every
  `confirmed` / `strong-evidence` / `hypothesis` status here is derived by this
  repository's evidence policy (`research/README.md`, `make check`).
- **Snapshot first.** Run `uv run --frozen make intake` before reading the drop.
  It snapshots the drop, verifies every file against `SYNC-MANIFEST.json` (sizes,
  SHA-256, content digest, path confinement, no symlinks), retries a torn
  snapshot, pins it by content digest and records the generation in
  `research/integration/intake-log.yaml`. Read the **pinned snapshot** it prints,
  never the live drop. A sync can overwrite the drop at any moment.
- **Never** write in `research/from-retrieval/`, and never run Git in the
  retrieval repository. Sync is not promotion.

## Processing a retrieval drop ("do your work")

Run this cycle in order, cheap orientation before expensive per-image work. The
producer's intake document (above) governs orientation; this repository's rules
govern everything else.

1. **Intake.** `uv run --frozen make intake`. Resolve drift or a torn snapshot
   before going on, then work only from the pinned snapshot it reports.
2. **Orient.** Read the newest `plans/done/CYCLE-SUMMARY-<date>.md`, the snapshot's
   `STATUS.md`, and the `findings/*.md` sections the cycle log names. Then check the
   public triage index (`data/triage-index.yaml`, keyed by SHA-256) and the private
   narrative ledger (`private/triage/from-retrieval-triage-ledger.md`), so image
   reads are targeted rather than blind.
3. **Diff by content.** `uv run --frozen make triage-audit` lists producer scans
   (read by path) whose SHA-256 has no triage disposition yet. Renamed files keep
   their disposition, because identity is the hash.
4. **Value-gate each new scan** (see "Decision protocol"):
   - Open and read it by path. Findings, profiles and FamilySearch tree data are
     leads, never evidence.
   - Classify it, privacy-review it, and promote only the valuable, highest value
     first.
   - Watch for these traps: pre-1889 acts are `parish`, not civil; only
     P-0001–P-0003 are living; and FamilySearch "Memories" portraits may be
     AI-generated or colourised.
   - Record every disposition, positive or negative, in the triage index (public,
     hash-keyed) and its narrative in the private ledger.
5. **Promote only with the owner's per-task authorisation (Channel B).** Do it in
   one transaction:
   - Write a change set (`scripts/new_entity.py apply`, see `data/README.md`). It
     holds the drafts, the replacements that add the reciprocal back-references,
     and the authorised evidence copies, each with its SHA-256 and authorisation
     reference.
   - The tool verifies every hash, refuses duplicates, validates the would-be
     repository and rolls back on failure.
   - For every person whose evidence changed, sync `profile`/`profile_pt` from the
     snapshot's `findings/profiles/<surname>/<person>.md`. Fold in documented facts
     and clearly hedged reasoning; never launder a `[LEAD]` into fact.
   - Catalogue every page of a multi-page record together, and write one
     continuous transcription across all its pages.
   - Run `uv run --frozen make profiles-audit drop-pages-audit`.
6. **Finish** with the Completion protocol.
7. **Review the agent's `plans/` and findings.** Fold valid new leads into
   `data/record-coverage.yaml` / `STATUS.md`, flag conflicts, and note what is
   blocked.

## Decision protocol

Classify the task before acting:

- **Research:** state one exact research question, seek the closest original
  record, and record positive, negative and inaccessible searches.
- **Evidence intake:** inventory and privacy-review the file before creating a
  source or conclusion. A record *about* the family is a `source`; a third-party
  record where the family appears only in a functional role (witness, appraiser,
  creditor, attorney) is a FAN entity (`data/fan/`, `usage: context`, never
  evidence), not a source.
- **Data change:** cite the qualifying source, preserve variants and conflicts,
  and validate every relationship independently.
- **Engineering:** preserve evidence and research history, remove duplication,
  and keep one canonical owner for each concept.
- **Review:** report evidence-backed findings without changing data unless the
  user also requested implementation.

Collaborative trees, hints and profile values are navigation leads only. Never
promote them to evidence. A zero-result index or OCR search does not prove that
an entry is absent from an unindexed register.

## Entity connectivity and completeness

Every link is bidirectional, and every catalogued record must reach the viewer
through structured fields, not prose. When creating or updating an entity,
follow the per-field **person completeness checklist** in
[`data/README.md`](data/README.md) and keep both ends of each link in step:

- `person.family_ids` ↔ the family's `partners` / `children`: add the reciprocal
  entry on the family, linking the person as a *child* and as a *partner* where
  both apply.
- `person.event_ids` ↔ the event's `participants`: list the event on **every**
  participant it names, including parents and other non-principals, not only the
  principal.
- `person.fan_references` ↔ the FAN entity's `participants`: the back-link is
  optional, but the FAN→person side is not.
- After cataloguing a vital record about a person, create its **event** (a
  catalogued record with no matching event is invisible in the viewer's dates
  and timeline) and add that event to the `event_ids` of every participant.
- Cite each source at the assertion it supports (`name_variants`, `occupations`,
  event and relationship `source_ids`), not only in `linked_people` or prose.
- When a vital record (baptism, birth, marriage, death) **names an ancestor of the
  subject** — the parents, and any grandparents the record states — model each as a
  **person entity** with its parentage `family`, the derived events, and full
  reciprocity, extending the line upward. Those named ancestors are source-qualified
  (the record attests them), not collaborative-tree leads, so they get real nodes;
  do **not** leave them in prose or demote them to `documented_children` (that
  mechanism is for collateral *children*, below). Model only the clearly deceased,
  and never mint an ancestor from a collaborative tree or published genealogy alone.
  Run `uv run --frozen make ancestors-audit` to catch the gap: it flags any subject
  of a held vital record that still lacks a parentage family. When a note already
  records the parents as unlocated, lead-only, or absent from the record, keep that
  note so the audit reads the omission as deliberate.
- Extract every attribute a record **states** about a modelled person and cite the
  record at that assertion: `nationality` (a stated *nacionalidade*, or a stated
  foreign *naturalidade* such as "natural de Portugal / Suíça"), `occupations`,
  residence/place, and the age → approximate birth year. Read attributes from the
  record only — never infer nationality or origin from a surname — and mark
  uncertain reads `[uncertain]`.
- Record an attested collateral child that needs no research of its own — a
  sibling of a modelled person, or another child of a modelled couple — as a
  `documented_children` entry on the parents' family (`name` plus required
  `source_ids`), rather than minting a person entity for it. The viewer builds each
  person's Siblings (from their parent family) and Children (from their unions)
  from the modelled children plus these entries. Never list a possibly-living
  person here; record only clearly deceased collaterals.

A field or link left unset on purpose — a contested nationality, an edge
withheld pending evidence — must say so in the entity's `notes`, so a later audit
reads it as deliberate rather than missing.

## Research autonomy

- Continue with the highest-priority actionable objective in `STATUS.md`.
- If it is blocked, record what was searched, the search bounds, the blocker
  and the exact next action. Then continue to the next priority that does not
  bypass an evidence gate.
- This assistant researches read-only public web sources (WebFetch and
  WebSearch); authorised FamilySearch retrieval is performed by the external
  retrieval agent using the owner's session and delivered through the
  `research/from-retrieval/` sync (see "Working files and research routing"). Do
  not edit a FamilySearch tree, attach sources, contact archives, submit paid
  record orders or expose credentials unless the user explicitly authorises that
  action.
- Do not create people merely because a collaborative profile exists. Add only
  source-qualified entities needed by the evidence being ingested.
- Prefer a bounded manual register review over repeating broad name searches.

## Parallelism and delegation

- Whenever a task divides into independent units — transcribing or value-gating
  many records, auditing many entities, a broad multi-file change — split it
  across **parallel subagents**, each with a **disjoint set of files** and strict,
  self-contained instructions, then validate and commit centrally. Prefer this to
  sequential work for large batches; it is the default for anything repetitive.
- A subagent does not inherit this file's context: restate the relevant
  non-negotiable rules in its prompt (evidence integrity, no fabrication — mark
  `[illegible]`/`[uncertain]` rather than guess — privacy handling, edit only the
  assigned field/files, do not commit). Spot-check its output and run
  `uv run --frozen make check` before committing the batch.

## Non-negotiable rules

- Write repository content, filenames and commit messages in English while
  preserving source-recorded personal names and diacritics.
- Never expose private evidence or unnecessary information about living people.
  Exactly three people are living (P-0001–P-0003); everyone else in the tree is
  deceased. A source restriction or an old `private`/sensitivity field never makes
  a person living, and a deceased person's record is not private by default.
  Private originals live only in the gitignored `private/` store, never in this
  public repository. Canonical rules: `research/README.md`, "Living people and
  private material".
- Never erase evidence, research history, rejected hypotheses or material
  conflicts. Supersede conclusions explicitly.
- Never create a source record from memory when the record or an authoritative
  archival reference is unavailable.
- Keep `confirmed`, `strong-evidence`, `hypothesis` and `rejected` distinct.
- Do not infer Portuguese, island, German or other origins from surnames.
- Keep the two source layers separate but in step. A source is a YAML **record**
  under `data/sources/<category>/` and, separately, its binary **scan** under
  `evidence/<category>/`: the record is machine-readable and exportable, the scan
  is a private binary kept out of the structured data. The full-backup GEDCOM
  references scans and the GEDZIP bundle packages them as a private backup, but
  the two layers stay separate — do not merge them into one tree.
- Preserve stable IDs: immutable once assigned; never renumber a live entity.
  Sources and their scans are category-prefixed by origin (`CIV`, `GOV`, `PAR`,
  `PRB`, `NWS`, `PUB`, `REC`) and share the ID prefix
  (`data/sources/civil/CIV-0001.yaml` ↔ `evidence/civil/CIV-0001-…`); other
  entities keep their fixed prefix (`P`, `F`, `E`, `PL`, `FAN`). The category
  also lives in the source's `record_category` field (the single source of
  truth), so reclassifying moves the files but never changes the ID. Adding a
  new source category must follow the documented pattern — new prefix +
  `data/sources/<category>/` + `EntityConfig` + `SOURCE_KINDS` entry + ledger
  section + template + viewer `SOURCE_DIR` entry; see `data/README.md`.

## Completion protocol — Definition of Done

Run this as an ordered, checkable list before declaring **any** objective
complete. It exists because downstream artefacts (profiles, the Family Story, the
"What's new" feed, the GEDCOM, relationship labels) drift silently behind the
structured data: `make check` does **not** catch most of them. Do not stop at
"the source is catalogued" — walk every group and confirm each item, or state
explicitly why it does not apply.

**A. Data & evidence.**
1. Structured entities, `data/document-inventory.yaml` and the affected
   `data/record-coverage.yaml` entry are updated. Every catalogued vital record
   has its **event** (`E-…`), and every producer scan read has a disposition in
   `data/triage-index.yaml` (narrative detail in the private ledger).

**B. Connectivity & completeness** (link *symmetry* is now enforced by `make check`;
*completeness* — whether a link that ought to exist is present — is not, so still
verify by hand and with the advisory audits):
2. `make check` fails on any one-sided `person↔family`, `person↔event` or
   `event↔source` link (see `validate_link_reciprocity`). You must still confirm no
   unintended orphan, that each deliberate omission is noted, that a source is cited
   at the assertion it supports, and that the link which *should* exist does (a
   catalogued vital record has its event; a named parent is on the event; see
   "Entity connectivity and completeness").
3. Run the advisories and clear or acknowledge every hit:
   `uv run --frozen make ancestors-audit drop-pages-audit profiles-audit`.

**C. Narrative & bilingual sync** (the layer most prone to lag):
4. For **every person whose evidence changed**, sync `profile` **and** `profile_pt`
   from the drop's research profile — assert only sourced facts, tag `[LEAD]`/
   `[INFERRED]` honestly, never launder a lead, and keep EN⇄PT at parity. When a
   record supersedes an earlier working fact (a corrected date, a confirmed maiden
   name, a bounded-negative death), rewrite the person's `notes`, open-questions
   and "Sources held" too — not just the new source.
5. **Relationship/degree labels** ("Iris's Nth-great-grandparent", "maternal vs
   paternal line") must be derived from the actual `family_ids` chain, not copied
   from a source abstract, and must agree in EN and PT.
6. Update the two **curated, won't-auto-update narrative layers** when a user-facing fact changed:
   - `family-tree-viewer/family-story.yaml` (**both `en:` and `pt:`**) when a narrative-level fact
     changed (a corrected date/name, a new documented origin) — it is a curated essay.
   - `family-tree-viewer/updates.yaml` — add a **curated "What's new / Novidades" editorial entry**
     (bilingual `title`/`title_pt`; deceased-only `links`; `kind` = milestone/correction/person)
     for the milestone, correction or new person the change represents. `make updates` (item 8)
     auto-adds public *documents* to the feed but CANNOT classify a milestone/correction — you must
     write that editorial line by hand, then regenerate. Do **not** add an entry for a routine
     document add (it is already auto-listed); do add one for a milestone (e.g. new siblings modelled,
     a portrait/roster deepening, a corrected conclusion).

**D. Derived artefacts** (regenerate whichever the change touched; commit them like
source, except the gitignored GEDCOM exports and `_site/`). Each committed artefact
has an **in-step test** that fails `make check` when it drifts — so regenerate rather
than hand-edit:
7. `uv run --frozen make export` — the local, private full-backup GEDCOM (never
   committed; it carries living people and privately held records). Then run
   `uv run --frozen make privacy-audit` before committing.
8. `uv run --frozen make updates` — the viewer "What's new" feed
   (`test_updates_feed` fails when a public source is missing). This regenerates `updates.json`
   from the public *documents* **plus** the curated `updates.yaml` editorial entries — so add any
   editorial milestone/correction line (item 6) **before** running this.
9. `entity-index.json` — regenerated by the site build; `test_viewer_index` enforces it.

**E. Validation gate** (the enforced structural rules — `make check` fails, it does
not merely warn: JSON-schema validity, ID-ledger integrity, link reciprocity, and
the three in-step artefacts above):
10. `uv run --frozen make check` is green — **zero errors and zero warnings**, not
    just passing tests (read the `validate` output, not only the test tail). The
    committed **pre-commit hook** (`make install-hooks`, one-time per clone) runs
    this automatically on any structural commit, and CI (`.github/workflows/check.yml`)
    runs it on every push and PR; keep the branch-protection rule requiring it.

**F. Provenance, review & commit:**
11. `STATUS.md` refreshed for material state/priority/conclusion changes (its
    repository snapshot points to `make check` for counts; do not hand-maintain them).
    Append `logs/LOG.md` for a completed research or audit session; add a concise
    `CHANGELOG.md` entry.
12. Review the diff for privacy, unsupported promotion, lead-laundering and
    accidental duplication.
13. Commit one small completed objective. Do not push unless explicitly asked or
    the active automation requires it.
14. Select the next highest-priority actionable objective and continue until a
    natural stopping point or a genuine human-intervention blocker.

For a large or repetitive change, split the work across parallel subagents on
disjoint files (see "Parallelism and delegation"), then run groups B–E centrally
before committing — a subagent cannot see the whole graph and will not catch a
cross-entity or bilingual-parity gap.
