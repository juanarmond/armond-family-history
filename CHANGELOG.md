# Changelog

All notable repository changes are recorded here. Genealogical conclusions must
also remain traceable through source records and research logs.

## Unreleased

### Added

- Define the initial YAML entity model and JSON Schemas for people, families,
  events, places and sources.
- Add entity and research templates, evidence-handling guidance and the initial
  document-cataloguing plan.
- Add an ID allocation ledger and automated validation for schemas, references,
  evidence quality, privacy, duplicate identities and parent-child chronology.
- Document the local workflow, implementation roadmap and policies for derived
  timelines and exports.
- Establish permanent research principles and a cumulative research log, and
  record that the source documents are absent from the worktree and Git history.
- Consolidate repository governance, remove obsolete foundation and placeholder
  documentation, and allow empty entity directories to remain untracked.
- Add a versioned document-inventory schema and validation for file integrity,
  privacy review, duplicate handling and source-allocation state.
- Version every structured entity and replace the overloaded evidence class
  with separate record category, source form, information quality and evidence
  type fields.
- Model each parent-child assertion as a separately typed and cited edge, and
  constrain event participant roles with explicit exceptional-role details.
- Split the validator into focused model, inventory, reference and genealogical
  rule modules while preserving its command-line and imported interfaces.
- Replace stored next-ID counters with derived allocation and add atomic,
  recoverable entity reservation and draft generation with dry-run support.
- Add staged validation and recoverable batch promotion for mutually dependent
  entity drafts, including rollback and interrupted-transaction recovery.
- Add a least-privilege, concurrency-cancelled GitHub Actions matrix that runs
  the frozen local repository check with pinned action and tool versions.
- Consolidate the older duplicate remote validation workflow into the canonical
  pinned, multi-version repository-health workflow.
- Consolidate project scope and operating principles into `README.md`, current
  state and planning into `STATUS.md`, and research policy and history under
  `research/`; add checks for root-document ownership and broken local Markdown
  links.
- Remove the duplicate document-cataloguing plan after retaining its unique
  source-processing order in `STATUS.md`; keep research policy, inventory and
  reproducible history as separate canonical artifacts.
- Audit the original ChatGPT genealogy conversation against the repository,
  preserve previously omitted leads and superseded interpretations without
  promoting them, and identify its 24 unavailable image attachments as the
  primary transfer gap; downgrade Aristão's proposed parentage to `hypothesis`
  because collaborative-tree support alone cannot establish `strong-evidence`.
- Recover and catalogue the first authorised record from FamilySearch
  Memories: the certified 1916 marriage of Deocleciano Muniz Bittencourt and
  Luiza Fernandes de Azevedo; add its private reconstructed image, inventory
  provenance, checksum and six directly required linked entities.
- Fix prospective entity promotion so the default command-line workflow uses
  the repository schemas, and cover the previously untested path.
- Recover and catalogue three alternate photographs of the damaged 1952
  marriage certificate of Geraldo Paz Armond and Cidalia Engracio Guimarães as
  one source; add its private evidence files, inventory provenance, retained
  birth-date conflict and six directly required linked entities.
- Consolidate `SRC-0002` to the clearest photograph under one canonical
  filename; keep the two omitted alternate views recoverable in Git history and
  preserve their FamilySearch provenance in the research record.
- Migrate the initial person block to Ahnentafel order, add privacy-minimised
  roster records for direct-ancestor positions 1–15, remap all existing
  references, and document that the identifiers remain immutable after this
  low-cost migration.
- Recover and catalogue Geraldo Paz Armond's original 1991 civil death
  registration; preserve the FamilySearch archival citation, private
  reconstructed register image, record-number conflict and source-qualified
  parentage of Aristão Ferreira Armond and Liliosa Paz Armond.
- Review the data model against three real records: distinguish reported
  co-parents from sourced partners, enforce inventory-to-source file checksum
  consistency, and add a validated missing-record coverage ledger for deceased
  direct ancestors.
