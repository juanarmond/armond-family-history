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
     for document intake; or
   - [`templates/README.md`](templates/README.md) for canonical templates.
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

## Processing a retrieval drop ("do your work")

When the owner says "do your work" (or a new drop has synced), run this cycle in
order — cheap orientation before expensive per-image work:

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
   heuristic name-match — confirm identity before enriching).
5. **Finish** with the Completion protocol (`make check`, the reciprocity and
   completeness verification, rebuild the viewer index, logs, changelog); record each
   image's disposition in the triage ledger, and commit.
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

## Completion protocol

Before declaring an objective complete:

1. Update the relevant structured entities, inventory and coverage entry.
2. Add a reproducible detailed research log when a search was performed.
3. Update `STATUS.md` only for material state, priority or conclusion changes.
4. Append `logs/LOG.md` for completed research or repository-audit sessions.
5. Add a concise `CHANGELOG.md` entry for notable repository changes.
6. Run `uv run --frozen make check` and fix every error and warning.
7. When structured data changed, regenerate the committed GEDCOM full backup with
   `uv run --frozen make export` so `export/armond-family-history.ged` stays in
   step with the data. (The `.gdz` bundle is on-demand and gitignored.)
8. Verify link reciprocity and per-entity completeness, which `make check` does
   not yet enforce (see "Entity connectivity and completeness"): both ends of
   every family, event and FAN link resolve, no entity is an unintended orphan,
   and each deliberate omission is noted.
9. Review the diff for privacy, unsupported promotion and accidental
   duplication.
10. Commit one small completed objective. Do not push unless explicitly asked or
    the active automation explicitly requires it.
11. Select the next highest-priority actionable objective and continue until a
    natural stopping point or a genuine human-intervention blocker.
