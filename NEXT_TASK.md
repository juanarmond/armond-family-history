# Next task

## Objective

Add safe ID allocation and entity-skeleton automation.

## Why this is next

Creating an entity currently requires coordinated manual edits to the ID
ledger, filename and YAML identifier. That is error-prone at scale and can
leave a partially allocated ID if interrupted.

## Completion criteria

- Provide one command that selects the current `next_ids` value, creates the
  correctly named entity from the canonical template and advances the ledger.
- Refuse to overwrite files or allocate from an invalid repository state.
- Write the entity and ledger atomically enough to recover safely from failure.
- Support a dry-run that performs no writes.
- Add tests for success, dry-run, collision and invalid-ledger paths.
- Run the complete repository check before committing.

## External blocker

Actual document cataloguing still requires authorised, privacy-reviewed copies
of the certificates and screenshots described in `CURRENT_STATE.md`.
