# Cumulative research log

This is the append-only index of completed research and repository-audit
sessions. Detailed reproducible notes live under `research/logs/` using
`YYYY-MM-DD-short-question.md`. Later corrections must identify the earlier
entry they amend; they must not erase it.

## 2026-07-28 — Repository evidence availability audit

- Outcome: no source document, source entity or historical binary/LFS object was
  found; Priority 0 requires authorised copies before cataloguing can begin.
- Detailed log:
  [`research/logs/2026-07-28-repository-evidence-availability-audit.md`](research/logs/2026-07-28-repository-evidence-availability-audit.md).

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
