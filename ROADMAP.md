# Repository roadmap

## Milestone 0 — Evidence-led foundation

Status: complete.

- Define the YAML model and entity schemas.
- Provide stable entity, person-profile, source-record and research-log
  templates.
- Establish privacy-aware evidence handling and document inventory.
- Enforce identifiers, references, evidence statuses, chronology and duplicate
  review with local automated checks.

This milestone contains no new genealogical conclusion.

## Milestone 1 — First-source checkpoint

Status: next.

1. Inventory the documents already supplied without interpreting them.
2. Catalogue the first three clear, high-value original records in the order
   defined by `research/DOCUMENT_CATALOGUING_PLAN.md`.
3. Create only the people, family, event and place records directly needed to
   describe those sources.
4. Review whether the model preserves name variants, conflicts, date precision,
   historical jurisdictions, transcription uncertainty and source reliability.
5. Revise the schema before wider ingestion if the real records expose a gap.

## Milestone 2 — Existing-evidence catalogue

Status: pending Milestone 1.

- Catalogue the remaining certificates and privacy-approved images.
- Re-transcribe ambiguous handwritten fields at full resolution.
- Record duplicates, inaccessible material and negative searches.
- Update `CURRENT_STATE.md` only where catalogued evidence materially changes a
  conclusion.

## Milestone 3 — Priority research

Status: pending the existing-evidence catalogue.

Proceed through `TASKS.md` in priority order, beginning with primary proof for
Aristão Ferreira Armond and Liliosa Paz Armond. Internet trees may identify
collections or profile IDs, but their relationships remain leads until the
underlying records are examined.

## Milestone 4 — Derived views and exchange

Status: deferred until the entity model is stable.

- Generate human-readable person pages from YAML.
- Generate source-linked timelines and maps.
- Add GEDCOM export with documented loss and privacy rules.
- Prepare any publication output only after a separate living-person and
  copyright review.
