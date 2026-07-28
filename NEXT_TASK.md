# Next task

## Objective

Add explicit schema versions to every structured entity and separate source
form, information quality and evidence type in the source model.

## Why this is next

No live entity exists, so this is the lowest-risk point to correct the data
contract. After hundreds of records, the same migration would require a
repository-wide rewrite and version detection.

## Completion criteria

- Require `schema_version` on people, families, events, places and sources.
- Replace the overloaded `evidence_class` field with distinct source-form,
  information-quality and evidence-type fields.
- Preserve the rule that collaborative trees are lead-only.
- Update templates, validators and tests atomically.
- Run the complete repository check before committing.

## External blocker

Actual document cataloguing still requires authorised, privacy-reviewed copies
of the certificates and screenshots described in `CURRENT_STATE.md`.
