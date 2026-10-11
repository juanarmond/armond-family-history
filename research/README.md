# Research policy and workspace

This is the canonical research, evidence and citation policy. The directory
contains reproducible research notes rather than settled entity data.

- `from-retrieval/` is the **text-only handoff** synced from the retrieval agent
  (`armond-genealogy-retrieval`) — Channel A: `findings/` (and
  `findings/profiles/`), `plans/`, `leads/`, `places/`, `correspondence/`, its
  `STATUS.md` and methodology, `SYNC-MANIFEST.json` and, from contract v1,
  `EVIDENCE-INDEX.json`. It is **research context, not evidence**, and it is
  overwritten on every sync. Never read it live: `make intake` snapshots and
  verifies it and prints the pinned snapshot to read. Record images never travel
  in it; they are read by path in the producer repository and transferred only
  with the owner's per-task authorisation (Channel B). Nothing is catalogued until
  it clears the value gate — read → classify → privacy-review → promote only the
  valuable, recording negatives and never inferring absence from a zero-result
  search.
- `integration/` holds the consumer side of the retrieval contract: the
  vendored contract schemas (`schemas/`), the accepted intake-instruction hash
  (`accepted-intake.json`), the public intake log (`intake-log.yaml`) and the
  refactor's execution record.
- Value-gate dispositions are kept by content identity in the public triage index
  `data/triage-index.yaml` (SHA-256 keyed, no record content); the narrative
  detail is in the private repository at `private/triage/` (see "Living people
  and private material").
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
genealogies cannot confirm a conclusion. A "coherent body of primary evidence"
means several independent primary records consistently attesting the conclusion
with no material conflict — for example a union shown by a child's marriage act
plus a grandchild's baptism — which can support *confirmed* even without the
single ideal direct record; whereas a lone indirect or informant-reported
record (a death or marriage naming parents, a single grandchild baptism, a
probate spouse-mention) is *strong-evidence*, not a coherent body.

### Strong evidence

A conclusion supported by several consistent records or close-relative
records, but lacking the ideal direct record. At least one of them must be a
record (an original or a faithful copy): a published genealogy or other
authored narrative may corroborate it, but alone — like a collaborative tree or
a family recollection — supports at most a *hypothesis*. `make check` enforces
this.

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
- A surname negative must state the variants searched. Scribes swap L and R
  (Armond → Almond-, Almend-), so include those forms; a negative searched
  with R-forms only is recorded as an R-form negative.

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

## Baptism as a birth record

Before Brazil's general civil registration (from 1889), the parish **baptism is
the birth record** — a contemporaneous primary source at the same evidentiary
level as a later civil birth certificate. A baptism establishes the **birth
date** (stated explicitly, "nascido a …") and the **birthplace** (the stated
"natural de …" if given, otherwise the baptizing freguesia/district). So when a
person's birth is documented only by a baptism, create a **birth event** from it
(confirmed, citing the baptism) in addition to the baptism event — the birth
(one date/place) and the baptism (a later date, at the church) are distinct
events, both sourced from the one record. Keep the distinction honest: a baptism
directly attests the baptism and *reports* the birth, and the birthplace is the
baptizing parish unless the record names a different birth locality.

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
  appear, and transcribe **every person the record names** — principals,
  declarants, informants, witnesses, officiants, physicians — with their stated
  data. Do **not** self-redact a deceased person's record. The only exceptions
  are the three living people's sensitive details and incidental private
  information about people outside the tree; these go to the private store, and
  a living person's own document is held privately as a citation stub (see
  "Living people and private material" below).
- Do not use OCR as the sole authority for handwritten records: a machine reading
  of cursive is a draft to verify against the image, never the final transcript.
- If the original is unavailable and only a legible copy remains, transcribe the
  copy and say so; never reconstruct a transcript from memory.
- For a published or authored secondary work (a book, thesis or article),
  "full" means **every line of each cited page transcribed verbatim** — other
  people's entries, footnotes and the printed page number included — with page
  markers, not the entire publication; the `abstract` carries the summary. The
  owner's reason (2026-10-09): read a page once, then research from the
  transcription without reopening a large PDF. List those pages in the file's
  `show_pages` so the viewer shows the same pages the transcription covers.

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

## Living people and private material

Owner decisions of 2026-10-08 and 2026-10-11. This section is the single
authority for privacy; agents must not infer it from old fields or tags.

**The repository and its site are public.** Everything tracked — files, Git
history, LFS objects, filenames, logs — is published, whatever the site filter
does. Four kinds of privacy apply, and they must not be confused:

1. **Living-person privacy.** Exactly three people in the tree are living: the
   owner (P-0001) and his parents (P-0002, P-0003). Their person records and
   relationships stay in the data where the tree needs them. Their own civil
   documents, those documents' transcriptions and their sensitive personal data
   (identity numbers, addresses, birth details, ages, professions, signatures) are
   never tracked or published. The site and the assistant reduce the three to
   stubs and scrub their names. Everyone else in the tree is deceased. Never
   infer that someone is living from a missing death date, a recent record, a
   `private: true` field, an old privacy or sensitivity tag, or a record's past
   in a private-repository workflow.
2. **Incidental private information.** People outside the tree who appear in the
   owner's own documents — his spouse, officiants, notary clerks — are not
   modelled and not treated as tree members, but their personal information is
   private and is never tracked or published.
3. **Source and evidence restrictions.** A source may restrict its evidence — for
   example, a scan "authorised for this private repository only". That
   restricts the evidence, not the people: the people stay deceased, and the
   record's genealogical facts and transcription may stay in the repository.
   The restricted scan lives in the private store, and the record carries
   `withhold_from_site: true`.
4. **Deceased-person genealogy** is public, in full, unless a specific source
   restriction applies. A deceased person's record is not private merely because
   an old field says `private: true` (that field does not gate publication); do
   not remove such a classification mechanically either — find its purpose first.

How this is held:

- A living person's own document, or one carrying incidental private
  information, is **held privately** (`held_privately: true`). Its full original,
  transcription and scan live in the private store (`private/data/`,
  `private/evidence/`, with neutral filenames that carry no names, dates or
  places). The tracked record is a citation stub with no transcription, dates or
  places, its scan path under `private/evidence/` and `withhold_from_site: true`.
- A deceased person's record that merely names a living person (an informant,
  a declarant) stays in the repository. The living person's sensitive details
  are withheld from the tracked transcription and kept in the private store, and
  its scan, which shows them, lives in the private store.
- The full-backup GEDCOM is generated locally (`make export`) and never committed;
  where the private store is present it includes the privately held originals.
- `make check` enforces these rules. `make privacy-audit` checks tracked files
  and the built site against the private list of strings that must never be
  published (`private/redaction-terms.txt`).
- The private store needs a durable private backup. The owner's chosen
  mechanism is Git/GitHub; the public repository can never hold that backup. A
  separate private repository is proposed and needs his approval before it is
  created.
