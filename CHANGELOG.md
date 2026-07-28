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
