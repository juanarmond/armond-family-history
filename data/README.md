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
| `fan/` | `FAN-0001` | `schemas/fan.schema.json` |

`fan/` holds FAN references (Friends / Associates / Neighbours): records where
one of the family's people appears only in a functional role — witness,
appraiser (louvado), creditor, attorney, party. They are context, never
evidence: their `usage` is always `context`, they carry no conclusion status,
and each names the people it involves under `participants` (with a role). People
link back through an optional `fan_references` list. Use a FAN entity for a
third-party record; catalogue a record *about* the family as a `source` instead.

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

The initial direct-ancestor person block follows Ahnentafel order for the
repository subject: `P-0001` is Juan Carlos Muniz Armond, `P-0002` and
`P-0003` are his father and mother, and each later direct ancestor initially
follows the standard father `2n` and mother `2n+1` positions. These remain
stable person identifiers after assignment. A later parentage correction must
not silently renumber an existing person; record the corrected relationship
and any resulting divergence from Ahnentafel order explicitly. Collateral
relatives and later additions continue from the next available person ID.

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
abandoned, preserve its identifier in `retired_ids`.

Promote completed, mutually dependent drafts as one validated batch:

```console
python3 scripts/new_entity.py promote P-0001 SRC-0001 --dry-run
python3 scripts/new_entity.py promote P-0001 SRC-0001
```

The command validates a staged prospective repository before touching live
data. Live promotion uses a recoverable transaction and rolls back on failure.
If the process is forcibly interrupted and leaves
`.entity-promotion-transaction/`, run:

```console
python3 scripts/new_entity.py recover
```

Source evidence policy is defined in `research/README.md`; this file defines only
storage and identifier mechanics.
