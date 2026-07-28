# Three-record structured-model review

## Date

28 July 2026

## Objective

Review the schema, validator, templates and operational research state after
cataloguing three real documents, then correct low-risk defects before wider
FamilySearch ingestion.

## Evidence sample

The review used:

1. `SRC-0001`, a derivative certified marriage record naming two spouses and
   four reported parents;
2. `SRC-0002`, a damaged derivative marriage certificate containing a birth-
   date conflict and a married-name form; and
3. `SRC-0004`, an original death-register entry directly documenting a death
   and secondarily reporting a spouse and two parents.

`SRC-0003` is an owner-supplied roster source, not part of the three-document
record sample.

## Finding 1 — Co-parentage falsely implied partnership

### Problem

Schema version 1 required every adult in a family group to have role `spouse`
or `partner`, and required a sourced `partner_relationship` whenever two were
present. `SRC-0004` names Aristão Ferreira Armond and Liliosa Paz Armond as
Geraldo's parents but does not document any relationship between those two
people. The old shape therefore forced a conclusion the source did not prove.

### Decision

Add a conservative `parent` member role. Two `parent` members may support
independent parent-child edges without a `partner_relationship`. Roles `spouse`
and `partner` still require two members and a sourced relationship.

The container remains named `partners` in schema version 1. Renaming it would
touch every family, validator rule, template and downstream consumer and would
require an explicit schema migration. That migration is not justified by three
records. The semantic distinction is now enforced even though the legacy
container name is imperfect.

### Estimates and impact

- Migration effort implemented: low; one live family, one schema, one template,
  documentation and tests.
- Long-term maintenance impact: positive; prevents false unions while
  preserving current identifiers and file shapes.
- Future rename effort: medium; defer until a broader schema-version change.

## Finding 2 — Inventory and source files could drift

### Problem

The document inventory and final source record both store the retained evidence
path and SHA-256 checksum for different reasons: chain-of-custody intake versus
genealogical citation. Validation previously checked each independently but did
not prove they described the same retained file.

### Decision

For every `catalogued` inventory entry, require the linked source's
`digital_file` path and checksum to match one inventoried file exactly.

### Estimates and impact

- Migration effort implemented: low; all three catalogued documents already
  matched.
- Long-term maintenance impact: positive; duplicated integrity fields cannot
  silently diverge.

The inventory and source records are not merged. They serve distinct purposes:
the inventory records acquisition, privacy review, duplicate handling and
rights; the source records archival citation, transcription, evidence
assessment and linked conclusions.

## Finding 3 — Missing-record work had no canonical operational state

### Problem

`STATUS.md` correctly prioritised branches, but it could not distinguish for
each deceased ancestor whether a birth, marriage or death record was
unsearched, only a lead, located, catalogued, negatively searched or
inaccessible. Repeating that matrix in prose would not scale or support the
weekly research automation.

### Decision

Add `research/record-coverage.yaml` as the sole person-by-record operational
ledger. Its schema and validator:

- exclude living people;
- require catalogued coverage to cite a linked structured source;
- prohibit source IDs on non-catalogued states;
- reject duplicate people and duplicate record types; and
- preserve FamilySearch profile identifiers as navigation leads only.

`STATUS.md` remains the canonical strategic backlog. It must not duplicate the
coverage matrix.

### Estimates and impact

- Migration effort implemented: low; twelve deceased direct ancestors and
  their birth, marriage and death coverage were initialised.
- Long-term maintenance impact: strongly positive; weekly research can select
  unresolved records deterministically and record negative or inaccessible
  searches without creating duplicate task documents.

## Deferred architecture issue — Assertion-level citation quality

The source model conservatively labels a record's overall information quality
as `mixed` when it supplies primary information for one conclusion and
secondary information for another. `SRC-0004` demonstrates this: the death is
primary information, while spouse and parentage are reported information.
Statuses and reliability notes currently preserve the distinction, but the
machine model does not yet assign information quality per source-to-assertion
citation.

- Estimated migration effort: medium; it would introduce citation entities or
  citation objects across events, relationships and possibly names.
- Long-term maintenance impact: positive at scale, but premature before more
  source patterns are observed.
- Decision: evaluate again after five to ten additional heterogeneous records
  and implement before bulk ingestion if the repeated need is confirmed.

## Validation

The revised repository validated with zero errors and zero warnings. New tests
cover co-parentage without partnership, partner-role requirements,
inventory-to-source file integrity, living-person exclusion and coverage-source
linkage.

## Next action

Resume the authorised FamilySearch evidence audit using
`research/record-coverage.yaml`, beginning with the highest-priority available
record: the 1949 marriage of Antenor Muniz and Iris Bohrer Muniz, followed by
clear death registrations if that record cannot be recovered.
