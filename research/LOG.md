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

## 2026-07-28 — Armond–Guimarães marriage-record ingestion

- Outcome: recovered and privacy-reviewed three alternate photographs of the
  damaged 31 May 1952 marriage certificate of Geraldo Paz Armond and Cidalia
  Engracio Guimarães, and treated them as one source rather than three pages.
- Detailed log:
  [`logs/2026-07-28-familysearch-armond-guimaraes-marriage-ingestion.md`](logs/2026-07-28-familysearch-armond-guimaraes-marriage-ingestion.md).
- Genealogical conclusions changed: the marriage and Cidalia's married-name
  form now have catalogued direct evidence. The certificate's report of 15
  September 1930 is retained as secondary birth information and does not
  resolve the existing date conflict.
- Preservation limitation: physical damage and opaque tape obscure material
  text; all uncertainty remains marked rather than supplied from the
  collaborative tree.
- Next action: inspect Geraldo's attached source and death-certificate Memory,
  then recover one distinct record to complete the three-record schema sample.

## 2026-07-28 — SRC-0002 evidence-file consolidation

- Outcome: retained the clearest of the three reviewed photographs of the
  Armond–Guimarães marriage certificate under one canonical filename and
  removed the two less-readable alternates from the current worktree.
- Preservation: the omitted files remain recoverable from Git commit
  `3dc9c5e`; source provenance still records all three FamilySearch Memories.
- Genealogical conclusions changed: none.

## 2026-07-28 — Ahnentafel person-ID migration

- Outcome: aligned the initial direct-ancestor person block with Ahnentafel
  order, created privacy-minimised roster entries for positions 1–15, and
  migrated every existing person cross-reference.
- Detailed log:
  [`logs/2026-07-28-ahnentafel-person-id-migration.md`](logs/2026-07-28-ahnentafel-person-id-migration.md).
- Evidence boundary: `SRC-0003` is owner-supplied family information and
  supports the working roster and spellings only; it does not replace vital or
  relationship records.
- Engineering decision: person IDs remain immutable after this one low-cost
  migration, even if later evidence changes a pedigree relationship.

## 2026-07-28 — Geraldo Paz Armond death-record ingestion

- Outcome: located the original 18 February 1991 Volta Redonda civil death
  entry through Geraldo's attached FamilySearch source, reconciled it with the
  identical Memory image, and preserved a privacy-reviewed reconstruction with
  archival citation and checksum.
- Detailed log:
  [`logs/2026-07-28-familysearch-geraldo-death-record-ingestion.md`](logs/2026-07-28-familysearch-geraldo-death-record-ingestion.md).
- Genealogical conclusions changed: Geraldo's death is now supported by
  catalogued direct evidence; the record supplies strong evidence that Aristão
  Ferreira Armond and Liliosa Paz Armond were his parents.
- Conflict retained: the handwritten entry number appears to be `39005`, while
  the FamilySearch index reports certificate `39006`.
- Negative result: the original-image viewer's controlled JPG download did not
  yield a file, so the identical Memory page was reconstructed from its full
  Deep Zoom tile set.
- Next action: review the model against the completed three-document sample
  before wider ingestion.

## 2026-07-28 — Three-record structured-model review

- Outcome: corrected the family model so reported co-parents do not imply an
  unsupported partnership; enforced inventory-to-source file integrity; and
  added a validated missing-record coverage ledger for all deceased direct
  ancestors currently numbered `P-0004` through `P-0015`.
- Detailed log:
  [`logs/2026-07-28-three-record-model-review.md`](logs/2026-07-28-three-record-model-review.md).
- Genealogical conclusions changed: the unsupported partner relationship
  between Aristão Ferreira Armond and Liliosa Paz Armond was removed. Their
  separately sourced parent-child relationships to Geraldo remain
  `strong-evidence`.
- Architecture decision: defer assertion-level citation objects until five to
  ten more varied records show whether the added complexity is justified.
- Next action: resume evidence ingestion with the 1949 Antenor–Iris marriage.

## 2026-07-28 — Antenor–Iris marriage-record ingestion

- Outcome: recovered and catalogued the damaged 7 December 1949 civil marriage
  certificate of Antenor Muniz and Iris Bohrer from Antenor's user-created
  FamilySearch source.
- Detailed log:
  [`logs/2026-07-28-familysearch-antenor-iris-marriage-ingestion.md`](logs/2026-07-28-familysearch-antenor-iris-marriage-ingestion.md).
- Genealogical conclusions changed: the marriage, Iris's married-name form and
  both spouses' reported parents now have catalogued direct evidence; each
  relationship is `strong-evidence` because the retained document is a
  derivative.
- Negative result: Iris's FamilySearch profile had no attached sources.
- Preservation limitation: folds, tape, stains and low contrast obscure
  register details and several vital fields, which remain untranscribed.
- Next action: inspect Liliosa Paz Armond's 1946 death evidence.
