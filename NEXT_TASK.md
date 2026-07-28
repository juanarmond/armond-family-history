# Next task

## Objective

Add controlled parent-child relationship types and event participant roles.

## Why this is next

The current family model cannot distinguish biological, adoptive, foster or
other parent-child relationships, and participant roles are arbitrary strings.
No live entity exists, so the vocabulary can be corrected without migrating
research data.

## Completion criteria

- Require a controlled relationship type on every child-parent assertion.
- Use a controlled event-participant role vocabulary with an explicit escape
  hatch for exceptional roles.
- Update templates, schemas, documentation and tests atomically.
- Run the complete repository check before committing.

## External blocker

Actual document cataloguing still requires authorised, privacy-reviewed copies
of the certificates and screenshots described in `CURRENT_STATE.md`.
