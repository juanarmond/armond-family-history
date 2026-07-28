# Cumulative research log

This is the append-only index of completed research and repository-audit
sessions. Detailed reproducible notes live under `research/logs/` using
`YYYY-MM-DD-short-question.md`. Later corrections must identify the earlier
entry they amend; they must not erase it.

## 2026-07-28 — Repository evidence availability audit

- Outcome: no source document, source entity or historical binary/LFS object was
  found; Priority 0 requires authorised copies before cataloguing can begin.
- Detailed log:
  [`logs/2026-07-28-repository-evidence-availability-audit.md`](logs/2026-07-28-repository-evidence-availability-audit.md).

## 2026-07-28 — Governance and architecture consolidation

- Outcome: established canonical sprint governance, removed obsolete foundation
  instructions and placeholder documentation, and changed validation so empty
  entity directories are created only with their first substantive record.
- Genealogical conclusions changed: none.
- Next action: validate the document inventory contract.

## 2026-07-28 — Document inventory contract

- Outcome: added a strict versioned contract and automated checks for inventory
  IDs, file paths and checksums, privacy review, duplicates and proposed source
  allocation.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: version every entity schema and correct the evidence taxonomy
  before the first source record is created.

## 2026-07-28 — Entity versioning and evidence taxonomy

- Outcome: required schema version 1 on every entity and separated record
  category, source form, information quality and evidence type in source
  records.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: add controlled parent-child relationship types and event
  participant roles before ingesting people.

## 2026-07-28 — Relationship and participant semantics

- Outcome: modelled each parent-child relationship as a separately typed,
  sourced and confidence-rated edge; added controlled participant roles with an
  explicit exceptional-role detail field.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: reduce validator maintenance risk by separating its loading,
  schema and cross-entity concerns without changing the public command.

## 2026-07-28 — Validator modularisation

- Outcome: reduced the stable validator façade from more than 1,100 lines to
  fewer than 500 and isolated inventory, reference, shared-model and
  genealogical policy concerns without duplicating functions.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: add an atomic ID allocation and entity-skeleton command so
  record creation cannot desynchronise filenames and the ledger.

## 2026-07-28 — Identifier reservation and draft automation

- Outcome: removed redundant next-ID counters, added explicit reservations and
  a dry-run-capable command that atomically reserves the next ID before
  creating a recoverable non-live draft.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: add validated batch promotion so mutually dependent completed
  drafts can enter the live data model without a transient invalid state.

## 2026-07-28 — Validated batch promotion

- Outcome: added prospective whole-repository validation, dry-run, rollback and
  interrupted-transaction recovery for promoting mutually dependent drafts.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: enforce the complete repository check on GitHub pushes and pull
  requests so invalid changes cannot silently bypass the local workflow.

## 2026-07-28 — Continuous repository health enforcement

- Outcome: added a read-only GitHub Actions workflow for Python 3.11 and 3.13,
  pinned all executable actions and uv, cancelled superseded runs, and tested
  the workflow contract locally. Merge blocking still requires an external
  GitHub branch-rule setting.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: obtain authorised, privacy-reviewed copies of the previously
  supplied documents and catalogue the first three original records.

## 2026-07-28 — Remote workflow reconciliation

- Outcome: rebased the sprint commits onto the independently added remote
  validation workflow, preserved that commit in history and removed the
  obsolete duplicate from the worktree in favour of the pinned canonical
  workflow.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: unchanged; obtain authorised, privacy-reviewed document copies
  for the first three source records.

## 2026-07-28 — Documentation ownership consolidation

- Outcome: reduced root Markdown to four canonical documents by merging stable
  project guidance into `README.md`, active state and priorities into
  `STATUS.md`, and research policy and cumulative history under `research/`.
  Added automated checks against broken local links and renewed root-document
  fragmentation.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: unchanged; obtain authorised, privacy-reviewed document copies
  for the first three source records.

## 2026-07-28 — Research workspace consolidation

- Outcome: reviewed every file under `research/`, retained the distinct policy,
  intake-inventory, cumulative-history and detailed-session responsibilities,
  and removed the task-specific cataloguing plan after moving its unique record
  order into `STATUS.md`.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: unchanged; obtain authorised, privacy-reviewed document copies
  for the first three source records.

## 2026-07-28 — Original conversation transfer audit

- Outcome: compared the complete original ChatGPT research conversation with
  the repository, preserved transcript-only leads and the correction chain at
  hypothesis level, and identified 24 unavailable attachments as the principal
  provenance gap.
- Detailed log:
  [`logs/2026-07-28-chatgpt-conversation-transfer-audit.md`](logs/2026-07-28-chatgpt-conversation-transfer-audit.md).
- Research evidence added: none.
- Genealogical conclusions changed: Aristão's proposed parentage remains
  recorded but is downgraded from `strong-evidence` to `hypothesis` because the
  available support is limited to collaborative-tree and transcript leads.
- Next action: recover and privacy-review the original attachments before
  creating source or person entities.

## 2026-07-28 — First FamilySearch document ingestion

- Outcome: recovered the certified 21 October 1916 marriage record of
  Deocleciano Muniz Bittencourt and Luiza Fernandes de Azevedo from
  FamilySearch Memories, reconstructed the complete viewer image, completed
  privacy and provenance review, and promoted the first six linked entities.
- Detailed log:
  [`logs/2026-07-28-familysearch-marriage-record-ingestion.md`](logs/2026-07-28-familysearch-marriage-record-ingestion.md).
- Genealogical conclusions changed: the marriage, spouses' ages and
  birthplaces, and their four named parents now have catalogued direct evidence;
  the marriage remains `strong-evidence` because the retained image is a
  derivative.
- Negative result: neither spouse has the 1916 record attached as a formal
  FamilySearch source; each has only a 1983 record concerning a child.
- Next action: recover and catalogue two additional original records before
  reviewing the schema against the evidence sample.
