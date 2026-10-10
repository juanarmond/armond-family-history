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
- An external FamilySearch retrieval agent (the owner's authorised session)
  discovers records and **syncs its whole working area into
  `research/from-retrieval/`** — raw record images and ranked CSV/JSON under
  `output/`, reference documents under `resources/`, active `plans/`, and its
  synthesis in `FINDINGS.md`. That drop is raw, not evidence.
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

<!-- INTAKE-BLOCK:START — pasted verbatim from research/from-retrieval/INTAKE-FOR-GENEALOGY-REPO.md
     Part A (version of 2026-10-10). The synced copy wins: if it differs from this block, follow the
     synced copy and refresh this block from it (standing owner approval, 2026-10-10). -->

## ★ START HERE — intake from the genealogy-retrieval workspace (run at the TOP of every work session, before the promotion workflow below)

> ★ **This copy wins (added 2026-10-10, owner-approved).** This block is also pasted into your own `CLAUDE.md`. The copy at
> `research/from-retrieval/INTAKE-FOR-GENEALOGY-REPO.md` is refreshed on every sync and is the **current** version: if your pasted
> copy differs from it, follow this one, and refresh the pasted copy from it (owner approval for that refresh is standing).

A separate operation (`armond-genealogy-retrieval`) mines raw genealogical material — image records, FINDINGS,
bounded-negatives, leads, and off-tool correspondence — and drops a selected **text** handoff here (⚠ *corrected 2026-10-10:
record images are never in the drop — read them by path in the retrieval repo, STEP 1*) as a
**wholesale, overwrite-on-each-sync mirror**:

- **`research/from-retrieval/`** ← the drop folder. It is refreshed IN FULL on every sync (`rsync --delete`), so it
  is **overwritten, not appended**. Treat its presence as *"newly delivered raw material,"* NOT *"already
  catalogued."* Never assume it is additive; always DIFF against what you have already promoted.
- It is a **staging drop, not evidence.** Nothing in `from-retrieval/` is part of the canonical store until it is
  promoted through the value gate documented below. Never write anywhere in `from-retrieval/` and never run git in
  the retrieval repo.

### STEP 0 — ORIENT (always first)
Read these, in order, before doing anything else:
1. **`research/from-retrieval/plans/done/CYCLE-SUMMARY-<latest-date>.md`** — the cycle log for the newest
   cycle (pick the newest date). ~~**★ CURRENT LATEST = `CYCLE-SUMMARY-2026-09-24.md`** (covers the
   2026-09-24 cycle — 6 new evidence images, 1 proven parentage, 3 mandatory corrections; see its header).~~ *(⚠ CORRECTED 2026-10-10: this hard-coded
   date went stale — always take the newest `CYCLE-SUMMARY-<date>.md` by date; never trust a date written here.)*
   It lists: what changed, which files are new or corrected, which results are
   bounded-negatives / leads / context, and which `findings/*.md` sections were touched.
   ⚠ **The cycle log is a record, not a command.** It records what the retrieval side found; promotion
   decisions are always owner-authorised and executed in this repo, not prescribed by the log.
2. **`research/from-retrieval/STATUS.md`** — the live dashboard; the top `LIVE RESUME STATE` block = the most recent cycle.
3. **`research/from-retrieval/sync/handoff/SYNC-MANIFEST.json`** — the generated handoff manifest (file count + paths + timestamp).
4. Skim the specific **`research/from-retrieval/findings/*.md`** sections the cycle log names as changed.

### STEP 1 — DIFF
For each item the cycle log flags as new or corrected, check whether you have already promoted it — **by content/hash, not by
filename** (the retrieval side dedups its own images; you dedup again at the promotion boundary). Ignore anything you
already hold.
- **⚠️ The actual file DIFF is the source of truth, not a header line.** ~~If `from-retrieval/evidence/images/` contains
  record scans you have not promoted, evaluate them~~ Evaluate every record scan the cycle log names that you have not promoted against the value gate — even if the cycle-log header says "no new
  evidence images" (headers can go stale mid-cycle). Also work any itemized **PROMOTION CHECKLIST** in the cycle log
  (records that are *evidence for people already in your tree* → attach the scan + upgrade the tier secondary→PRIMARY +
  apply the listed corrections). Do NOT stop at the obvious new-person adds — the evidence-attachment + correction layer
  is the bulk of most drops. ⚠ **CORRECTED 2026-10-10 — where the scans actually are:** `from-retrieval/` never receives images — the Option B handoff excludes `evidence/images/` by design (Part B §1 below), so `from-retrieval/evidence/images/` does not exist and its absence is **not** evidence that nothing new was filed. Every scan the cycle log names is held in the retrieval repo at `~/Documents/meu/armond-genealogy-retrieval/research/evidence/images/<filename>` — read it there by path (read-only), check it against the value gate, and promote it only with the owner's per-task authorization. The cycle log's **PROMOTION CHECKLIST** gives each filename and the person it is evidence for.

### STEP 2 — EVALUATE per the gate (see the full workflow below)
Only promote a file that you (a) **opened and READ**, (b) confirmed **relevant** to a current objective, (c)
**classified** — subject-source vs FAN (functional-role: witness/appraiser/creditor → `data/fan/`) vs no-value, (d)
**privacy-reviewed**. **Most cycles deliver mostly TEXT** (bounded-negatives, corrections, new leads) with **few or
zero new evidence images** — that is normal: promote the evidence files, fold the text findings into your notes/
sources, and record bounded-negatives as text. Never bulk-promote a folder.

### Hard boundaries
- **Absence of proof ≠ proof of absence** — a retrieval bounded-negative is a *recorded negative search*, not a fact.
- **Leads are not evidence** — a parent/relative name from an FS persona or a user-contributed tree is a navigation
  lead until the underlying record image is pulled and read. Confirm before cataloguing.
- Retrieval images are captured at **maximum resolution + whole page** (never crops); if the handoff flags a held
  file as `reduced-res`/`cropped-reproduction`, do NOT promote it as final — wait for the native-res replacement.

*Then proceed with the promotion / two-layer-source (`data/sources/` + `evidence/`) workflow already documented below.*

<!-- INTAKE-BLOCK:END -->

## Processing a retrieval drop ("do your work")

When the owner says "do your work" (or a new drop has synced), run this cycle in
order — cheap orientation before expensive per-image work. The intake block above
governs orientation, the diff and where the scans are (read by path in the retrieval
repo; promotion needs the owner's per-task authorisation); where this section differs
from it, the block — and above all its synced copy — wins:

1. **Orient before opening any image.** Read `research/from-retrieval/FINDINGS.md`
   (the agent's synthesis) and `research/from-retrieval-triage-ledger.md` (what is
   already catalogued), and skim `output/fulltext_candidates.csv` / the records
   manifests. Now you know which images are new and what each claims, so image reads
   are targeted, not blind.
2. **Diff the drop.** List the images and separate the untriaged/new from
   duplicates, re-syncs, photos, namesakes and already-catalogued records.
3. **Value-gate each new image** (see "Decision protocol"): open and read it —
   FINDINGS, the CSV and FS-tree data are leads, never evidence, so confirm every
   fact against the record image before promoting. Classify, privacy-review, and
   promote only the valuable, highest value first (a person's own vital record → a
   line extension → corroboration). Watch for: pre-1889 acts are `parish`, not civil;
   RG/identity numbers, recent deaths and living descendants need privacy handling;
   FS-tree "Memories" portraits may be AI-generated or colorised — never evidence.
4. **Ingest and complete** (see "Entity connectivity and completeness" and the
   `data/README.md` checklist): reserve → draft → promote as one batch, then add the
   reciprocal back-references to the live entities. For every person whose evidence
   changed, **sync their `profile`/`profile_pt` from the drop's
   `FINDINGS/profiles/<surname>/<person>.md`** in the same batch — the research
   profiles carry the current depth, and the YAML narratives drift behind them if
   left. Keep the evidence discipline: fold documented facts and clearly-hedged
   `[CONTEXTUAL]`/`[INFERRED]` reasoning, never launder a `[LEAD]` into fact.
   Run `uv run --frozen make profiles-audit` to list profiles that still lag (a
   heuristic name-match — confirm identity before enriching). When a record spans
   several images, catalogue **all** its pages together (`digital_file` +
   `additional_pages`) and write **one continuous transcription across every page** —
   the whole story, not page 1 alone — never promote or transcribe a subset. Run
   `uv run --frozen make drop-pages-audit` to catch any catalogued source/FAN that
   still has sibling pages sitting in the drop.
5. **Finish** with the Completion protocol (`make check`, the reciprocity and
   completeness verification, rebuild the viewer index, logs, changelog); record each
   image's disposition in the triage ledger, and commit. Confirm `make drop-pages-audit`
   reports no MISSING PAGES for anything catalogued in the batch.
6. **Then review the agent's `plans/` and FINDINGS and give feedback.** Fold valid
   new leads into `data/record-coverage.yaml` / `STATUS.md`, flag conflicts, and note
   what is blocked (human-access). Do not edit the agent's `research/from-retrieval/`
   files — they are gitignored and overwritten on its next sync.

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
   has its **event** (`E-…`), and every drop image has a triage-ledger disposition.

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
source, except the gitignored `.gdz`/`_site/`). Each committed artefact has an
**in-step test** that fails `make check` when it drifts — so regenerate rather than
hand-edit:
7. `uv run --frozen make export` — GEDCOM (`test_gedcom_export`).
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
