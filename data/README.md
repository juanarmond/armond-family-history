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
| `sources/civil/` | `CIV-0001` | `schemas/source.schema.json` |
| `sources/government/` | `GOV-0001` | `schemas/source.schema.json` |
| `sources/parish/` | `PAR-0001` | `schemas/source.schema.json` |
| `sources/probate/` | `PRB-0001` | `schemas/source.schema.json` |
| `sources/newspapers/` | `NWS-0001` | `schemas/source.schema.json` |
| `sources/publications/` | `PUB-0001` | `schemas/source.schema.json` |
| `sources/family-recollection/` | `REC-0001` | `schemas/source.schema.json` |
| `fan/` | `FAN-0001` | `schemas/fan.schema.json` |

`fan/` holds FAN references (Friends / Associates / Neighbours): records where
one of the family's people appears only in a functional role — witness,
appraiser (louvado), creditor, attorney, party. They are context, never
evidence: their `usage` is always `context`, they carry no conclusion status,
and each names the people it involves under `participants` (with a role). People
link back through an optional `fan_references` list. Use a FAN entity for a
third-party record; catalogue a record *about* the family as a `source` instead.

Alongside the per-entity files, `data/` holds three validated **control ledgers**
(aggregate files, not entities, so they sit at the `data/` root): `id-ledger.yaml`
(ID reservations), `document-inventory.yaml` (evidence intake, provenance and
privacy audit) and `record-coverage.yaml` (the per-ancestor missing-record plan).
Each is schema-validated; their schemas live in `schemas/`.

## Source categories

Sources are one concept split into category subfolders by the record's origin,
mirroring the `evidence/` layout. Each category is its own entity kind with an
immutable ID prefix:

| Category | Prefix | Typical `record_category` |
| --- | --- | --- |
| `sources/civil/` | `CIV` | `civil_registration` |
| `sources/government/` | `GOV` | `government_record`, `official_index` |
| `sources/parish/` | `PAR` | `parish_register` |
| `sources/probate/` | `PRB` | `court_or_probate` |
| `sources/newspapers/` | `NWS` | `newspaper` |
| `sources/publications/` | `PUB` | `published_genealogy` |
| `sources/family-recollection/` | `REC` | `family_recollection` |

The finer record type stays in the source's `record_category` field (the single
source of truth); the prefix is the coarse origin. The evidence file for a source
carries the same prefix (for example `evidence/civil/CIV-0001-...jpg`). IDs are
immutable: reclassifying a record moves its file but never renumbers it, so the
`source_ids` references elsewhere never break.

To add a new source category, follow the pattern end to end:

1. Add an `EntityConfig` in `scripts/validation/identifiers.py` (its prefix and
   `sources/<category>/` directory, sharing `source.schema.json`) and list the
   kind in `SOURCE_KINDS`.
2. Add a reserved and a retired section for it in `data/id-ledger.yaml`.
3. Add a `templates/entities/<singular>.yaml` with the `<PFX>-NNNN` placeholder.
4. Add the prefix to `SOURCE_DIR` in `family-tree-viewer/data-loader.js`.
5. Allow the prefix in `common.schema.json`'s `sourceId` pattern.

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
python3 scripts/new_entity.py materialize CIV-0001
```

Do not hand-edit an ID to reuse it. If an allocated entity is permanently
abandoned, preserve its identifier in `retired_ids`.

Promote completed, mutually dependent drafts as one validated batch:

```console
python3 scripts/new_entity.py promote P-0001 CIV-0001 --dry-run
python3 scripts/new_entity.py promote P-0001 CIV-0001
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

## Person completeness checklist

When creating **or updating** a person, populate every field the evidence
supports and re-check them on each edit. Dates and places in the viewer come from
**event entities**, not from a person's prose, so a catalogued vital record
without a matching event is a gap (this is how P-0014/P-0015 came to show "Dates
not established"). For each `P-NNNN`:

1. **preferred_name** — the fullest documented form.
2. **privacy** — `living` / `deceased` / `unknown`; treat possibly-living people
   as `living`, never `deceased` on assumption.
3. **nationality** — from birthplace (Brazilian by *jus soli*) or a record's
   stated *nacionalidade*; assert a foreign nationality only where a record says
   so, and leave it unset only when genuinely contested. Never infer it from a
   surname.
4. **name_variants** — every recorded spelling with its `source_ids`; keep maiden
   and married forms distinct.
5. **events** — create a **birth and a death event** for every deceased person
   whose date is evidenced, even when the date is approximate (e.g. inferred from
   the age at death) or the place is only state-level. Cite the source, link the
   person as `principal`, and give every event a place (`place_id` or
   `place_text`). After cataloguing any vital record, create its event.
6. **family_ids** — link the person both as a *child* (their parents' family) and
   as a *partner* (their own union), and add the reciprocal entry in the family
   entity. For an attested collateral child that needs no entity of its own (a
   sibling, or another child of the couple), add a `documented_children` entry on
   the family — `name` plus required `source_ids` — instead of a full person, and
   list only clearly deceased collaterals. The viewer's **Siblings** and
   **Children** sections are built from a family's modelled children plus its
   `documented_children`, omitting possibly-living people.
7. **occupations** / **fan_references** — where a record supports them, each with
   `source_ids`.
8. **notes** — record conflicts, variant spellings, the basis for any inferred
   field, and the next research action.
