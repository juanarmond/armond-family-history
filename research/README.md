# Research policy and workspace

This is the canonical research, evidence and citation policy. The directory
contains reproducible research notes rather than settled entity data.

- `LOG.md` is the append-only index of completed research and repository-audit
  sessions.
- `logs/` holds detailed sessions named `YYYY-MM-DD-short-question.md`.
- `document-inventory.yaml` stages authorised evidence before source
  cataloguing.
- `record-coverage.yaml` is the sole operational ledger for missing vital
  records of deceased direct ancestors. `STATUS.md` retains strategic branch
  priorities and must not duplicate this person-by-record matrix.
- Historical searches and superseded interpretations stay in `LOG.md`,
  detailed logs, structured conclusions and Git history. They must not be
  accumulated in `STATUS.md`.
- Regional or unresolved folders should be created only with their first
  substantive note.

## Evidence hierarchy

Use the following order of preference:

1. Original or high-quality images of civil and parish records.
2. Contemporary government, court, probate, immigration, military and cemetery
   records.
3. Contemporary newspapers and institutional records.
4. Official indexes or archival catalogues without images.
5. Published genealogies with citations.
6. Collaborative family trees and unsourced online profiles.
7. Family recollection.

Lower-ranked evidence can guide a search but must not silently override
higher-ranked evidence.

## Confidence statuses

### Confirmed

A conclusion directly supported by a reliable primary record — an original
register image or a certified copy that faithfully reproduces an official
civil, parish or government record — or by a coherent body of primary evidence
with no material unresolved conflict. Family recollection and published
genealogies cannot confirm a conclusion.

### Strong evidence

A conclusion supported by several consistent records or close-relative
records, but lacking the ideal direct record.

### Hypothesis

A plausible proposition requiring further evidence.

### Rejected

A proposition investigated and found incompatible with stronger evidence.
Preserve the reason for rejection.

## Name handling

- Record the name exactly as written in each source.
- Maintain a preferred display name separately from source-specific variants.
- Do not assume `Engracio`, `Ingracio` and `Ingrácio` are interchangeable for
  every individual.
- Do not assume `Muniz` and `Muniz Bittencourt` were always used as the same
  legal name.
- Preserve Portuguese diacritics where supported by the source.

## Date handling

- Exact date: `YYYY-MM-DD` in structured data.
- Month/year only: preserve the known precision.
- Approximate date: use an explicit qualifier.
- Inferred date: state the calculation and source, for example age 74 at death.
- Conflicting dates: retain all variants and explain which source is stronger.

## Place handling

Record both the historical jurisdiction and the current place where useful.
Administrative boundaries and municipality names may have changed. Never
replace a historical place with a modern name without documenting the
equivalence.

## Source citation minimum

Every source entry should capture, when available:

- source ID;
- record type and title;
- archive, registry, parish or publisher;
- collection and series;
- book, volume, page, image and record number;
- event date and registration date;
- locality and historical jurisdiction;
- stable URL or catalogue reference;
- access date;
- transcription or abstract;
- language;
- evidence assessment; and
- linked person, family and event IDs.

## Transcription rules

- Transcribe what is visible, not what is expected.
- Use `[illegible]`, `[uncertain]` or a question mark for uncertain readings.
- Preserve original spelling and punctuation in full transcriptions.
- Put expansions, translations and interpretations in separate notes.
- Do not use OCR as the sole authority for handwritten records.

## Collaborative trees

A FamilySearch or other collaborative-tree relationship is not evidence by
itself. Record its profile identifier and cited sources as a research lead.
Inspect the underlying record image whenever possible.

## Portugal workflow

1. Establish the ancestor's Portuguese district, municipality and parish from
   Brazilian records, naturalisation, foreigner registration, passport or
   passenger evidence.
2. Determine whether the relevant period belongs to a civil registry or
   district archive.
3. Search official archives and parish books before relying on surname
   distributions.
4. For the Azores and Madeira, identify the island, municipality and parish
   before extending the line.
5. Record archive codes, book dates and image numbers, including negative
   searches.

## Brazil workflow

Prioritise civil registration, parish collections, diocesan archives, Arquivo
Nacional, state and municipal archives, Hemeroteca Digital, probate and
cemetery records. Account for historical municipality and district changes.

## Conflict resolution

For every material conflict:

1. list each claim and source;
2. evaluate informant knowledge, temporal proximity and record purpose;
3. search for an independent record;
4. state the current conclusion and residual uncertainty; and
5. retain superseded claims in the research history.

## Session logging

Every session must record:

- date;
- research question;
- repositories and collections searched;
- names, variants, places and date ranges used;
- results found;
- negative results;
- access restrictions;
- conclusions; and
- next action.

Later corrections must identify the earlier entry they amend; they must never
overwrite it.

## Missing-record coverage

Each deceased direct ancestor may have one coverage row per record type. The
allowed states are:

- `unsearched`: no documented search has begun;
- `lead_only`: a recollection, transcript or collaborative profile points to a
  record or event but no qualifying record is catalogued;
- `located`: a qualifying record has been found but not fully ingested;
- `catalogued`: the record has a linked structured source;
- `negative_search`: a defined collection, place and date range was searched
  without a result;
- `inaccessible`: the identified collection requires human, archival or access
  intervention; and
- `not_applicable`: the record type does not apply.

FamilySearch profile identifiers in this ledger are navigation leads only.
They do not support any genealogical conclusion. Living people are excluded
from the ledger.

## Living people

Minimise data for living people. Do not store identity numbers, full addresses,
signatures, financial information or unnecessary certificate images. The
repository is private, but privacy-by-design still applies.
