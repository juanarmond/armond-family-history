# Research policy and workspace

This is the canonical research, evidence and citation policy. The directory
contains reproducible research notes rather than settled entity data.

- `from-retrieval/` is the **sync drop from the external FamilySearch retrieval
  agent**: its raw pulls (`output/` — Full-Text/Records record images plus ranked
  CSV/JSON), the third-party reference documents it used (`resources/`), its
  active research plans (`plans/`) and its working synthesis (`FINDINGS.md`). It
  is **raw, not evidence**: nothing there is catalogued until it clears the value
  gate — read → classify → privacy-review → promote only the valuable into
  `data/` + `evidence/` (as a `source` or a FAN entity), recording negatives and
  never inferring absence from a zero-result search. See `from-retrieval/README.md`.
  Value-gate dispositions per pulled image are tracked in
  `from-retrieval-triage-ledger.md` (a resume ledger, kept outside `from-retrieval/`
  so a wholesale re-sync cannot clobber it).
- `entity-drafts/` holds reserved-but-unpromoted entity skeletons (transient;
  created by `scripts/new_entity.py reserve`).
- The validated ledgers this policy governs live in `data/` (with
  `id-ledger.yaml`), not here: `data/document-inventory.yaml` stages authorised
  evidence before source cataloguing, and `data/record-coverage.yaml` is the sole
  operational record-gap ledger for deceased direct ancestors. `STATUS.md`
  retains strategic branch priorities and must not duplicate that matrix.
- Research history lives in the top-level `logs/` directory (the index
  `logs/LOG.md`, the `logs/correspondence-log.md` outreach record, and dated
  session files). Historical searches and superseded interpretations stay there,
  never in `STATUS.md`.
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

- **Transcribe the record in full and verbatim.** Capture the whole document —
  headings, boilerplate, legal formulae, observations, marginalia and signatures —
  not only the genealogically interesting clauses. Do not silently elide legible
  text; completeness is the default.
- Transcribe what is visible, not what is expected.
- Reserve gaps for text that is genuinely unreadable, and say why with an explicit
  marker: `[torn]`, `[stain]`, `[illegible]`, `[uncertain: …]` or a question mark.
  Never fill a gap with a guess, and never drop legible text behind a bare `[...]`.
- Preserve original spelling, punctuation and diacritics. Put expansions,
  translations and interpretations in separate notes, not inline.
- Transcribe identifiers (record, book/folio, RG/CPF and dossier numbers) as they
  appear. This is a private repository; the full backup is not shared.
- Do not use OCR as the sole authority for handwritten records: a machine reading
  of cursive is a draft to verify against the image, never the final transcript.
- If the original is unavailable and only a legible copy remains, transcribe the
  copy and say so; never reconstruct a transcript from memory.

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

Custody and access: civil registration began 1 April 1911, and records 100+
years old migrate from the conservatória to the district's Arquivo Distrital,
where they are largely free and digitised on DigitArq (`digitarq.arquivos.pt`).
The Torre do Tombo (ANTT) is the Arquivo Distrital for the Lisbon district only,
plus national collections (notarial, judicial, passaportes/emigração). Azores
parish images are free at the GEA (`culturacores.azores.gov.pt/ig`), browsable by
island, concelho, freguesia and série. Prefer these free images to paid
certidões; use `civilonline.mj.pt` (post-1911) or an ANTT certidão
(`crav.arquivos.pt`) only when the record is not freely available.

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

Sequence record retrieval to minimise cost. Exhaust the free and
already-authorised routes first — authorised record images (e.g. FamilySearch)
and name-searchable public databases — and catalogue their results before
submitting any paid order or archive-contact request. Paid and human-contact
requests (paid curia or parish certidões, archive enquiries) come last, once
the free routes are exhausted and ingested, and still require explicit owner
authorisation.

## Living people

Minimise data for living people. Do not store identity numbers, full addresses,
signatures, financial information or unnecessary certificate images. The
repository is private, but privacy-by-design still applies.
