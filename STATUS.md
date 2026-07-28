# Project Status

> This document is the canonical current-state summary and prioritised backlog.
> It is not a substitute for source records. Statements are classified by
> present confidence and must be revised when better evidence is added.

## Current objective

Recover, privacy-review and catalogue one more of the clearest original records
from the authorised FamilySearch account, then review the schema against the
three-record evidence sample.

The former human-intervention blocker is partially resolved. Two certified
marriage records have been recovered from FamilySearch Memories and catalogued,
but the original ChatGPT conversation still refers to 24 image attachments
whose binaries and metadata were not carried into the imported transcript.
The exact one-to-one attachment mapping cannot be reconstructed from the
transcript alone.

### Completion criteria

- Add each authorised file to the versioned document inventory with checksum,
  provenance and cleared privacy review.
- Reconcile recovered files against the conversation-transfer audit without
  trusting earlier assistant transcriptions.
- Catalogue one additional distinct original record as a structured source
  with exact citations, abstracts, reliability assessments and retained
  conflicts.
- Create only the people, events, families and places directly required by
  those records.
- Use reserved drafts and validated batch promotion.
- Review the schema against the resulting real data before wider ingestion.
- Run the complete repository check before committing.

### Candidate processing order

Subject to image quality and privacy review, begin with:

1. the marriages of Geraldo Paz Armond and Cidalia Engracio Guimarães, and of
   Antenor Muniz and Iris Bohrer Muniz;
2. the clearest relevant death registrations;
3. the civil registration naming the parents of Francisco José de Carvalho
   Guimarães and Emmerenciana Maria de Jesus; and
4. identity documents and screenshots only after explicit privacy review.

This order reflects evidential value; it does not promote any uncatalogued
claim to confirmed.

## Repository status

- 28 July 2026 FamilySearch intake: recovered a certified copy of the 21
  October 1916 marriage record for Deocleciano Muniz Bittencourt and Luiza
  Fernandes de Azevedo from FamilySearch Memories. It is inventoried as
  `DOC-0001`, catalogued as `SRC-0001`, and retained as a private reconstructed
  PNG with checksum and provenance.
- A second intake reviewed three alternate photographs of the damaged 31 May
  1952 marriage certificate for Geraldo Paz Armond and Cidalia Engracio
  Guimarães. The clearest view is retained as `DOC-0002` and catalogued as
  `SRC-0002`; the two omitted views remain recoverable from Git history.
- The second record provides direct evidence of the marriage and Cidalia's
  married-name form. Its report of `15 September 1930` for her birth is
  secondary information and does not resolve the existing September-versus-
  November conflict.
- The retained file is a derivative reconstructed from the complete Deep Zoom
  tile set rather than the originally uploaded JPEG. The marriage and partner
  relationship are therefore `strong-evidence`, not `confirmed`, under the
  repository's evidence-status policy.
- The intake created the first live entities: two people, one family, one
  marriage event, one place and one source.
- FamilySearch attaches only a 1983 civil record concerning a child as a formal
  source to each spouse. The 1916 certificate was stored as a Memory and had
  not been attached as a source.
- The intake exposed and fixed the promotion command's failure to locate
  repository schemas during default command-line prospective validation.
- The versioned YAML model, evidence intake contract, controlled relationship
  vocabularies, modular validator, recoverable ID allocation and batch
  promotion workflow are complete.
- Root documentation has four canonical files; research policy and session
  history live together under `research/`.
- The source-intake sequence is maintained with the active objective rather
  than in a separate task-specific plan.
- The frozen repository check runs locally and in GitHub Actions. Requiring it
  in branch rules remains an external repository-administration task.
- Two structured source records and their ten directly required linked
  entities are live.
- The initial direct-ancestor person block now follows Ahnentafel order:
  `P-0001` is the repository subject, `P-0002` and `P-0003` are his parents,
  and positions through `P-0015` cover the known grandparents and
  great-grandparents. These IDs are now immutable; the ordering is not
  genealogical evidence.
- `SRC-0003` records the owner's privacy-minimised working roster. It supports
  names and person allocation only; unsourced events and relationships remain
  pending.
- The original ChatGPT conversation has been audited. Its direct-ancestor
  conclusions were largely preserved, and missing transcript-only leads and
  correction history are now recorded without being promoted to evidence.

## Subject

### Juan Carlos Muniz Armond

- Born: 22 June 1982.
- Place: Rio de Janeiro, Rio de Janeiro, Brazil.
- Status: confirmed by family information; primary source not yet catalogued in this repository.

## Parents

### Luis Carlos Igracio Armond

- Born: 1957.
- Parents: Geraldo Paz Armond and Cidalia Engracio Armond.
- Name spelling: preserve exactly as `Luis Carlos Igracio Armond`.
- Status: confirmed by family information; source catalogue pending.

### Lucinea Aparecida Muniz Armond

- Born: 1957.
- Parents: Antenor Muniz and Iris Bohrer Muniz.
- Status: confirmed by family information; source catalogue pending.

## Paternal grandparents

### Geraldo Paz Armond

- Born: 30 January 1915.
- Birthplace: Rosário da Limeira, Minas Gerais, Brazil, according to the strongest current evidence.
- Died: 18 February 1991.
- Deathplace: Volta Redonda, Rio de Janeiro, Brazil.
- Spouse: Cidalia Engracio Guimarães, later Cidalia Engracio Armond.
- Marriage: 31 May 1952 in Eugenópolis, Minas Gerais, Brazil.
- Parents: Aristão Ferreira Armond and Liliosa Paz Armond.
- Status: the marriage is supported by catalogued direct evidence in
  `SRC-0002`; birth and death facts still require their own records.

### Cidalia Engracio Guimarães / Cidalia Engracio Armond

- Born: 1930 in Alvorada, then associated with Carangola, Minas Gerais, Brazil.
- Exact birth date conflict: 15 September versus 15 November. The original civil record must be re-examined before resolution.
- Died: 17 April 2023 in Volta Redonda, Rio de Janeiro, Brazil.
- Parents: Antonio Engracio Filho and Maria Aurora Guimarães.
- Status: the marriage and married-name form are supported by catalogued direct
  evidence in `SRC-0002`; the exact birth date remains unresolved.

## Maternal grandparents

### Antenor Muniz

- Also associated with the fuller family form `Antenor Muniz Bittencourt` in online trees; official identity document shown in the conversation used `Antenor Muniz`.
- Born: 2 November 1923 in Minas Gerais, Brazil.
- Died: 17 October 2014.
- Parents: Deocleciano Muniz Bittencourt and Luiza Fernandes de Azevedo.
- Spouse: Iris Bohrer Muniz.
- Marriage: 7 December 1949 in Alvorada, Minas Gerais, Brazil.
- Status: confirmed by family documents; source catalogue pending.

### Iris Bohrer Muniz

- Born: 27 February 1929 in Minas Gerais, Brazil.
- Died: 2021.
- Parents: João Gonçalves Bohrer and Selina Bohrer.
- Status: confirmed by family documents; full dates and places require source cataloguing.

## Great-grandparents and earlier lines

### Aristão Ferreira Armond

- Born: about 1879.
- Died: 1957.
- Spouse: Liliosa Paz Armond.
- Parents: current **hypothesis**: Simplício Ferreira Armond and Elizia Balbina
  Toledo.
- Evidence issue: public collaborative trees and sibling groupings support the relationship, but the decisive birth, baptism, marriage or death record for Aristão has not yet been catalogued.

### Liliosa Paz Armond

- Also appears in some material with `Ferreira Armond`; the original surname form and parentage remain unresolved.
- Born: approximately 1885–1887.
- Died: 15 November 1946, according to a death record previously examined.
- Spouse: Aristão Ferreira Armond.
- Parents: unknown. She is **not** to be recorded as a daughter of Simplício Ferreira Armond and Elizia Balbina Toledo without new primary evidence.

### Antonio Engracio Filho

- Born: approximately 1889–1890 in Minas Gerais, Brazil, inferred from age at death.
- Died: 21 June 1964.
- Spouse: Maria Aurora Guimarães.
- Parents: Antonio Engracio de Souza and Luzia Pinheiro da Conceição.
- Occupation in death record: merchant.
- Status: parentage supported by death record previously examined; source catalogue pending.

### Maria Aurora Guimarães

- Born: about 1904.
- Died: 15 September 1991.
- Spouse: Antonio Engracio Filho.
- Parents: Francisco José de Carvalho Guimarães and Emmerenciana Maria de Jesus.
- Status: confirmed by death and family records previously examined; source catalogue pending.

### Francisco José de Carvalho Guimarães

- Spouse: Emmerenciana Maria de Jesus.
- Parents: Vicente José de Carvalho Guimarães and Maria Tertuliana da Conceição.
- Status: confirmed by a civil birth registration of his children previously examined.

### Emmerenciana Maria de Jesus

- Spouse: Francisco José de Carvalho Guimarães.
- Parents: Antonio Francisco da Silva and Maria Paula de Jesus.
- Status: confirmed by a civil birth registration of her children previously examined.

### Vicente José de Carvalho Guimarães

- Described as Portuguese in a descendant's civil record.
- Spouse: Maria Tertuliana da Conceição.
- Died in Carangola, Minas Gerais, according to the same descendant record.
- Exact Portuguese parish: unknown and a high-priority research question.
- Status: identity and Portuguese origin strongly supported; birthplace unproved.

### Maria Tertuliana da Conceição

- Natural of Vila do Rio Claro, according to a descendant record.
- Spouse: Vicente José de Carvalho Guimarães.
- Status: confirmed relationship; exact vital records not yet located.

### Deocleciano Muniz Bittencourt

- Born: about 1892 in Sapucaia, Rio de Janeiro, Brazil.
- Died: 1959.
- Married Luiza Fernandes de Azevedo on 21 October 1916 in Carangola, Minas Gerais, Brazil.
- Parents: João Muniz Bittencourt and Suzana Ritta Brandão.
- Status: confirmed by marriage record previously examined.

### Luiza Fernandes de Azevedo

- Born: about 1898 in Bom Jesus da Cachoeira Alegre, then in the municipality of São Paulo do Muriaé, Minas Gerais, Brazil.
- Died: 1 July 1986, according to the family tree currently used as a lead.
- Parents: Secundino Maria de Azevedo and Theresa Fernandes de Azevedo.
- Status: parentage confirmed by marriage record; exact birth and death facts require primary-source cataloguing.

### João Muniz Bittencourt

- Spouse: Suzana Ritta Brandão.
- Parent of Deocleciano Muniz Bittencourt.
- A possible Azorean or other island origin appears in collaborative trees but remains unproved.
- Status: confirmed as Deocleciano's father; origin hypothesis unresolved.

### Suzana Ritta Brandão

- Spouse: João Muniz Bittencourt.
- Parent of Deocleciano Muniz Bittencourt.
- Status: confirmed by Deocleciano's marriage record; earlier ancestry unknown.

### João Gonçalves Bohrer

- Born: approximately 1903–1904 in Minas Gerais, Brazil.
- Died: 3 August 1970 in Volta Redonda, Rio de Janeiro, Brazil.
- Spouse: Selina Bohrer.
- Parents: the death record was read as Valentim Martinho Bohrer and Carolina Bohrer, but both names require a fresh high-resolution transcription before final confirmation.
- Occupation: merchant.
- Status: identity and spouse confirmed; parental transcription provisional.

### Selina Bohrer

- Born: approximately 1889–1890.
- Died: 11 February 1987.
- Spouse: João Gonçalves Bohrer.
- Parents: Joaquim José Bohrer and Lucinda Ferreira da Silva Bohrer.
- Status: supported by death record previously examined; source catalogue pending.

### Joaquim José Bohrer

- Spouse: Lucinda Ferreira da Silva.
- Parent of Selina Bohrer.
- Public trees suggest Francisco José Bohrer and Rosa Eugênia de Lemos as parents, but this remains a hypothesis pending an original record.

## Known collateral relatives

Collateral relatives have been mentioned in family trees and documents, including siblings of Geraldo, Cidalia, Antenor and other ancestors. They should not yet be treated as complete sibling sets. Each must receive a source-based person record before inclusion in a definitive family group.

## Major unresolved conflicts

1. Exact birth date of Cidalia: 15 September or 15 November 1930.
2. Original surname and parents of Liliosa Paz Armond.
3. Direct primary proof of Aristão Ferreira Armond's parents.
4. Exact transcription of the parents of João Gonçalves Bohrer.
5. Portuguese parish of Vicente José de Carvalho Guimarães.
6. Whether João Muniz Bittencourt had an Azorean, Madeiran or other Portuguese island origin.
7. Whether collaborative-tree dates for several nineteenth-century people correspond to the same individuals found in the family documents.

## Prioritised backlog

### Priority 0 — Preserve and catalogue existing evidence

> In progress: the authenticated FamilySearch audit and privacy-reviewed
> recovery workflow are active.

- [ ] Assign source IDs to every certificate, identity document and screenshot
  already supplied.
- [ ] Export or download the 24 attachments referenced by ChatGPT conversation
  `6a67aee6-f6d0-83eb-b4b8-26e9b19abc72`, preserving available provenance and
  withholding unnecessary living-person material.
- [ ] Store a clean image filename and an English abstract for each document.
- [ ] Re-transcribe ambiguous handwritten fields at full resolution.
- [x] Create initial person IDs and family IDs only after the source catalogue
  begins.

### Priority 1 — Armond and Paz lines

- [ ] Locate the birth or baptism of Aristão Ferreira Armond, approximately
  1879.
- [ ] Locate the marriage of Aristão Ferreira Armond and Liliosa Paz Armond.
- [ ] Locate Aristão's 1957 death registration.
- [ ] Confirm or reject Simplício Ferreira Armond and Elizia Balbina Toledo as
  Aristão's parents using a primary record.
- [ ] Identify Liliosa's parents and original surname from her birth, baptism,
  marriage or death records.
- [ ] Search Rosário da Limeira, Muriaé, Carangola, São Francisco do Glória,
  Piacatuba and Leopoldina collections as appropriate.

### Priority 2 — Muniz Bittencourt and Brandão lines

- [x] Catalogue the 21 October 1916 marriage of Deocleciano Muniz Bittencourt
  and Luiza Fernandes de Azevedo.
- [ ] Locate Deocleciano's birth or baptism in Sapucaia, Rio de Janeiro,
  approximately 1892.
- [ ] Locate the marriage of João Muniz Bittencourt and Suzana Ritta Brandão.
- [ ] Locate João's birth, death, immigration or naturalisation records.
- [ ] Test the claimed Azorean or other island origin without assuming it.
- [ ] Identify Suzana Ritta Brandão's parents from an original record.

### Priority 3 — Portuguese origin of Vicente José de Carvalho Guimarães

- [ ] Locate Vicente's marriage to Maria Tertuliana da Conceição.
- [ ] Locate Vicente's death registration in Carangola or the relevant
  district.
- [ ] Search naturalisation, foreigner registration, passport and passenger
  records.
- [ ] Identify district, municipality and parish in Portugal.
- [ ] Once the parish is known, search the relevant parish books generation by
  generation.

### Priority 4 — Bohrer lines

- [ ] Catalogue the deaths of João Gonçalves Bohrer and Selina Bohrer.
- [ ] Re-transcribe João's parents from the original death record.
- [ ] Locate João's marriage to Selina.
- [ ] Locate Selina's birth or baptism and confirm Joaquim José Bohrer and
  Lucinda Ferreira da Silva as parents.
- [ ] Locate Joaquim's marriage or death record.
- [ ] Test the proposed parents Francisco José Bohrer and Rosa Eugênia de
  Lemos.
- [ ] Determine the first documented immigrant generation; do not infer
  Germany from the surname alone.

### Priority 5 — Engracio, Souza and Guimarães lines

- [ ] Catalogue the death of Antonio Engracio Filho.
- [ ] Locate Antonio Engracio Filho's birth or baptism, approximately
  1889–1890.
- [ ] Locate his marriage to Maria Aurora Guimarães.
- [ ] Locate the marriage of Antonio Engracio de Souza and Luzia Pinheiro da
  Conceição.
- [ ] Catalogue Maria Aurora's death and the civil registration listing her
  sibling group.
- [ ] Extend Francisco José de Carvalho Guimarães and Emmerenciana Maria de
  Jesus only through original records.

### Priority 6 — Azevedo line

- [ ] Locate Luiza Fernandes de Azevedo's birth or baptism, approximately 1898.
- [ ] Confirm the exact locality and name variants.
- [ ] Locate the marriage of Secundino Maria de Azevedo and Theresa Fernandes
  de Azevedo.
- [ ] Identify their parents.

## Engineering backlog

| Priority | Outcome | Migration effort | Maintenance impact | Status |
| --- | --- | --- | --- | --- |
| P1 | Catalogue and model the first three original records | Requires source-image access | Tests the model before scale | In progress; two catalogued |
| P1 | Review the model and ingest remaining existing evidence | Depends on first-source findings | Establishes a stable structured base | Pending |
| P2 | Require the health check in GitHub branch rules | Low; administrator access | Prevents invalid merges | External |
| P3 | Generate person pages from structured YAML | Medium | Reproducible human-readable views | Deferred until real data |
| P4 | Add privacy-filtered GEDCOM export | Medium to high | Interoperability without exposing living people | Deferred until schema stability |

Completed engineering work is recorded in
[`CHANGELOG.md`](CHANGELOG.md). Architecture changes should be driven by real
records now that the foundation is stable.

## Definition of done for a research task

A task is complete only when:

1. the searched collections and date/place range are documented;
2. positive or negative results are logged;
3. the record image or archival reference is preserved where legally
   permitted;
4. a transcription or abstract is included;
5. all affected people, events and relationships are updated;
6. the confidence level and remaining conflicts are explicit.
