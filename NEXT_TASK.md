# Next task

## Objective

Add a versioned schema and automated validation for
`research/document-inventory.yaml`.

## Why this is next

Priority 0 evidence cataloguing is blocked because no source images are
available. The safest useful work is to make the intake contract deterministic
before those files arrive. This does not bypass the gate against extending
uncatalogued ancestry.

## Completion criteria

- Define required inventory fields and controlled statuses without encoding
  genealogical conclusions.
- Validate document IDs, paths, privacy review, checksum state, duplicate
  references and proposed source IDs.
- Add positive and negative automated tests.
- Update the canonical data-model and intake documentation.
- Run the complete repository check before committing.

## External blocker

Actual document cataloguing still requires authorised, privacy-reviewed copies
of the certificates and screenshots described in `CURRENT_STATE.md`.
