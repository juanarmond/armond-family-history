# YAML data model

The repository stores entities as UTF-8 YAML and validates them with JSON
Schema Draft 2020-12. JSON Schema is used because it has mature validators while
remaining independent of the YAML parser.

## Design principles

- One entity per file, with the identifier repeated in the filename.
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
cross-file validator additionally requires a `confirmed` conclusion to cite at
least one source whose evidence class is `original_record` or
`contemporary_record`. This is a minimum mechanical gate, not a substitute for
genealogical analysis.

## Minimal entity examples

These examples demonstrate shape only and are not claims about real people:

```yaml
id: P-9001
preferred_name: Example Person
privacy: unknown
name_variants:
  - value: Example Person
    type: source
    source_ids: [SRC-9001]
event_ids: [E-9001]
family_ids: []
notes: []
```

```yaml
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
source_ids: [SRC-9001]
notes: []
```

See `templates/entities/` for copyable YAML skeletons.
