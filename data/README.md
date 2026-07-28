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
`P-0001.yaml`. Files in this directory are conclusions and catalogue records,
not working notes. Record incomplete searches and tentative reasoning under
`research/`.

Allocate every identifier through `id-ledger.yaml`. Advance the corresponding
`next_ids` value in the same commit as a new entity. If an allocated entity is
removed, add its identifier to `retired_ids`; never fill the gap with a
different entity.

Source evidence policy is defined in `RESEARCH_RULES.md`; this file defines only
storage and identifier mechanics.
