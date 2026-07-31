# YAML data model

The repository stores entities as UTF-8 YAML and validates them with JSON
Schema Draft 2020-12. JSON Schema is used because it has mature validators while
remaining independent of the YAML parser.

`document-inventory.schema.json` separately validates the evidence-intake
staging file. Inventory entries are observations about available files, not
genealogical conclusions.

`fan.schema.json` validates FAN references (Friends / Associates / Neighbours):
third-party records where a family member appears only in a functional role
(witness, appraiser, creditor, attorney). They are context (`usage: context`),
never evidence, and never carry a conclusion status.

## Design principles

- One entity per file, with the identifier repeated in the filename.
- Every entity declares `schema_version: 1`; future migrations must increment
  and explicitly transform this value.
- `data/id-ledger.yaml` preserves reserved and retired identifiers; the next
  sequential identifier is derived rather than stored as duplicated state.
- Relationships and events carry confidence and source citations.
- Source-specific name spellings remain distinct from the preferred display
  name.
- Exact dates use `YYYY-MM-DD`. Partial, approximate, inferred and conflicting
  dates retain their actual precision instead of receiving invented dates.
- Historical place names remain distinct from current equivalents.
- Collaborative trees are catalogued as research leads, never as confirming
  evidence by themselves.
- Cross-file rules that JSON Schema cannot express are enforced by
  `scripts/validate_data.py`.

## Date examples

```yaml
date:
  kind: exact
  value: 1916-10-21
```

```yaml
date:
  kind: approximate
  text: about 1879
  earliest: 1878
  latest: 1880
```

```yaml
date:
  kind: conflicting
  text: 15 September or 15 November 1930
```

YAML parsers may convert an unquoted exact date into a date object. Entity
files should therefore quote date-like values:

```yaml
value: "1916-10-21"
```

## Evidence-bearing conclusions

The allowed statuses are `confirmed`, `strong-evidence`, `hypothesis` and
`rejected`. Every event and relationship must cite at least one source. The
source model keeps four different questions separate:

- `record_category`: what kind of record or narrative it is;
- `source_form`: original, derivative or authored narrative;
- `information_quality`: whether the recorded information is primary,
  secondary, mixed or not yet determined;
- `evidence_type`: whether the source currently provides direct, indirect,
  negative or undetermined evidence for its linked conclusions.

Evidence type is assertion-dependent. The source-level value is therefore a
conservative repository-wide assessment: use `undetermined` when one source
plays materially different evidentiary roles for different linked conclusions,
and explain the distinction in `reliability`. A future citation-level model may
refine this after real records expose the required granularity.

The cross-file validator requires a `confirmed` conclusion either to cite
direct primary or mixed information from an original source, or to cite at
least two original sources that provide indirect primary or mixed information.
This is a minimum mechanical gate, not a substitute for source correlation,
conflict resolution or a written proof argument.

## Relationships and participant roles

Each child entry contains separate `parent_relationships`. Every parent-child
edge has its own parent ID, relationship type, confidence, citations and notes.
This avoids falsely applying one relationship type or evidence assessment to
both parents. The controlled types are `biological`, `adoptive`, `step`,
`foster`, `guardian`, `social`, `unknown` and `other`; `other` requires a
specific `relationship_detail`.

The `partners` array is the stable family-member container retained by schema
version 1. A member with role `parent` may be included solely so a
parent-child edge can be represented; that role does not assert a marriage or
partnership. Roles `spouse` and `partner` require two members and a sourced
`partner_relationship`. This distinction prevents a record that merely names
two parents from silently proving a relationship between them. Renaming the
container would require a schema-version migration and is deferred until a
broader model change justifies that cost.

Event participant roles use a controlled vocabulary covering principals,
spouses, parents, children, witnesses, informants, officiants, godparents,
sponsors, executors, beneficiaries and household members. Exceptional roles
use `other` and require `role_detail`. Birth and death events must have exactly
one `principal`.

## Minimal entity examples

These examples demonstrate shape only and are not claims about real people:

```yaml
schema_version: 1
id: P-9001
preferred_name: Example Person
privacy: unknown
sex: unknown
name_variants:
  - value: Example Person
    type: source
    source_ids: [CIV-9001]
event_ids: [E-9001]
family_ids: []
notes: []
```

```yaml
schema_version: 1
id: E-9001
event_type: birth
date:
  kind: year
  year: 1900
place_text: Example locality
participants:
  - person_id: P-9001
    role: principal
status: hypothesis
source_ids: [CIV-9001]
notes: []
```

See `templates/entities/` for copyable YAML skeletons.

## Validation

Install the local tooling and run all checks:

```console
uv sync
uv run --frozen make check
```

The validator checks schema rules, filename and identifier agreement, the ID
ledger, cross-file references, evidence quality behind confirmed conclusions,
collaborative-tree usage, evidence-file checksums, living-person privacy,
document-inventory privacy, duplicate and preservation state, encoded image
dimensions, possible duplicate identities and parent-child chronology.
Duplicate-identity findings are warnings because distinct people can share a
name and date; they require human review rather than automatic merging.

### Validator architecture

`scripts/validate_data.py` is the stable command and import façade. Focused
modules under `scripts/validation/` own shared models and YAML loading,
identifier definitions, document-inventory checks, reference resolution and
cross-entity genealogical rules. New rules belong in the narrowest existing
module; the façade should remain orchestration-only.
