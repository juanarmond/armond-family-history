# Next task

## Objective

Add validated batch promotion for completed reserved entity drafts.

## Why this is next

The first source and the people or events it documents can reference each other,
so promoting one completed draft at a time may be invalid. Promotion must test
the whole prospective batch before changing live data and must preserve every
reserved ID if validation fails.

## Completion criteria

- Accept one or more reserved draft identifiers.
- Validate the prospective batch, including cross-references, before live
  mutation.
- Refuse collisions, incomplete drafts and unreserved IDs.
- On success, move drafts to their canonical entity directories and remove the
  reservations as one recoverable transaction.
- On any failure, leave live data and reservations unchanged.
- Add tests for mutually dependent entities, dry-run, schema failure and
  rollback.
- Run the complete repository check before committing.

## External blocker

Actual document cataloguing still requires authorised, privacy-reviewed copies
of the certificates and screenshots described in `CURRENT_STATE.md`.
