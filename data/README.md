# Structured data

This directory is the machine-readable layer of the repository. Each YAML file
represents one stable entity and must validate against the corresponding schema
in `schemas/`.

| Directory | Identifier | Schema |
| --- | --- | --- |
| `people/` | `P-0001` | `schemas/person.schema.json` |
| `families/` | `F-0001` | `schemas/family.schema.json` |
| `events/` | `E-0001` | `schemas/event.schema.json` |
| `places/` | `PL-0001` | `schemas/place.schema.json` |
| `sources/` | `SRC-0001` | `schemas/source.schema.json` |

Entity directories are created only with their first YAML record. A missing
empty directory is valid and must not be preserved with placeholder files.

Use one entity per file and name the file after its identifier, for example
`P-0001.yaml`. Every entity must declare the schema version required by its
schema. Files in this directory are conclusions and catalogue records, not
working notes. Record incomplete searches and tentative reasoning under
`research/`.

## Identifier lifecycle

`id-ledger.yaml` stores only explicit reservations and retired identifiers.
The next identifier is derived from entity, reserved and retired IDs, so there
is no duplicated counter to drift out of sync.

Reserve an ID and create its editable, non-live skeleton with:

```console
python3 scripts/new_entity.py reserve source --dry-run
python3 scripts/new_entity.py reserve source
```

Kinds are `person`, `family`, `event`, `place` and `source`. Drafts live under
`research/entity-drafts/` and are checked only for reservation and identifier
integrity; they are not genealogical conclusions and do not satisfy the entity
schemas until completed. If a process stops after reserving an ID but before
creating the draft, recover it with:

```console
python3 scripts/new_entity.py materialize SRC-0001
```

Do not hand-edit an ID to reuse it. If an allocated entity is permanently
abandoned, preserve its identifier in `retired_ids`. Promotion of completed
drafts into `data/` must remove their reservations and pass the complete
validator; validated batch promotion is the next automation objective.

Source evidence policy is defined in `RESEARCH_RULES.md`; this file defines only
storage and identifier mechanics.
