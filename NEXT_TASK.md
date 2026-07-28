# Next task

## Objective

Refactor the monolithic validator into focused modules without changing its
public command or validation behaviour.

## Why this is next

The validator now exceeds 1,300 lines and mixes schema loading, inventory
validation, evidence policy, chronology, privacy and command-line concerns.
Further rules will increase review risk and make isolated testing harder.

## Completion criteria

- Preserve `python3 scripts/validate_data.py` and
  `scripts.validate_data.validate_repository`.
- Separate cohesive concerns without duplicating constants or helper logic.
- Keep all current tests passing and add an interface regression test if useful.
- Avoid changing genealogy or schema semantics during the move.
- Run the complete repository check before committing.

## External blocker

Actual document cataloguing still requires authorised, privacy-reviewed copies
of the certificates and screenshots described in `CURRENT_STATE.md`.
