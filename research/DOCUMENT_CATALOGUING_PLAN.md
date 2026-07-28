# Existing document cataloguing plan

## Objective

Catalogue every certificate, identity document and screenshot already supplied
without converting provisional statements in `CURRENT_STATE.md` into
unsupported structured facts.

## Order of work

Start with the clearest, highest-value records:

1. the 21 October 1916 marriage of Deocleciano Muniz Bittencourt and Luiza
   Fernandes de Azevedo;
2. marriage records for Geraldo Paz Armond and Cidalia Engracio Guimarães, and
   for Antenor Muniz and Iris Bohrer Muniz;
3. death records for Liliosa Paz Armond, Antonio Engracio Filho, João Gonçalves
   Bohrer, Selina Bohrer and Maria Aurora Guimarães;
4. the civil registration naming the parents of Francisco José de Carvalho
   Guimarães and Emmerenciana Maria de Jesus;
5. identity documents and screenshots, after privacy review.

The order reflects evidential value and the unresolved questions in
`CURRENT_STATE.md`; it does not imply that any uncatalogued claim is confirmed.

## Phase 1 — Inventory without interpretation

For each file already available:

1. Add one entry to `research/document-inventory.yaml` using the fields below.
2. Assign a temporary inventory key such as `DOC-0001`; this is not a source ID.
3. Record the current filename, format, apparent record type, people visible,
   likely event, image quality and present location.
4. Mark whether living people, identity numbers, addresses, signatures or other
   sensitive content are visible.
5. Record duplicate, cropped, low-resolution and inaccessible items.

An inventory entry represents one source candidate and may contain multiple
files:

```yaml
- inventory_id: DOC-0001
  status: intake
  added_date: "2026-07-28"
  apparent_record_type: civil marriage registration
  apparent_people:
    - Name exactly as visible
  apparent_event: marriage
  image_quality: unreviewed
  provenance: Family-held copy; exact custody to be documented
  rights_status: unknown
  files:
    - path: evidence/civil/example-image.jpg
      sha256: 64-lowercase-hexadecimal-characters
      media_type: image/jpeg
      role: primary
      privacy_review: pending
      sensitive_content: []
  duplicate_of: null
  proposed_source_id: null
  notes: []
```

The canonical field contract is
`schemas/document-inventory.schema.json`. The inventory is a staging tool:
apparent names and events are observations, not structured conclusions.

## Phase 2 — Privacy and file integrity

1. Review every image before committing it.
2. Exclude unnecessary records about living people; redact sensitive fields
   where a derivative meets the research need.
3. Calculate SHA-256 for retained files.
4. Identify duplicates by checksum before assigning multiple source IDs.
5. Record access or custody information when a family member supplied the copy.

## Phase 3 — Allocate and describe sources

For each distinct retained source:

1. Reserve the next source ID with
   `python3 scripts/new_entity.py reserve source`; complete the generated draft
   before promotion to `data/sources/`.
2. Rename the evidence file according to `evidence/README.md`.
3. Create `data/sources/SRC-NNNN.yaml` from the source template.
4. Create a detailed Markdown source record when a full transcription or
   extended reliability analysis is required.
5. Enter archive, collection, book, page, image and record number whenever they
   are visible or can be verified.
6. Preserve uncertain readings with explicit markers; do not complete names
   from expectation.

## Phase 4 — Link entities conservatively

Create person, family, event and place IDs only after the first relevant source
is catalogued. Link the source in both directions, run validation and use:

- `confirmed` only when a qualifying primary or contemporary record directly
  supports the conclusion and no material conflict remains;
- `strong-evidence` when the evidence is consistent but indirect or the ideal
  record is missing;
- `hypothesis` for collaborative-tree claims and other unresolved leads;
- `rejected` for investigated claims incompatible with stronger evidence.

Do not structure the possible parents of Aristão Ferreira Armond, the parents
of Liliosa Paz Armond, the ambiguous parents of João Gonçalves Bohrer or an
island origin for João Muniz Bittencourt as confirmed.

## Phase 5 — Record the search trail

For every cataloguing session:

1. Create a research log from `templates/research-log.md`.
2. Record unreadable fields, missing pages, failed lookups and access barriers.
3. Update the affected entity files.
4. Update `CURRENT_STATE.md` only if a conclusion materially changes.
5. Add a concise `CHANGELOG.md` entry and run the repository checks.

## First review checkpoint

Stop after cataloguing the first three high-quality records. Review whether the
schemas preserve all citations, conflicts, name variants, historical places and
date precision before processing the remaining documents or generating
Markdown views.
