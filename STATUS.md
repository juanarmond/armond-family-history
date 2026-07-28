# Project Status

> This document is the canonical current-state summary and prioritised backlog.
> It is not a substitute for source records. Statements are classified by
> present confidence and must be revised when better evidence is added.

## Current objective

Manually review the 1878–1888 baptism sequence in São Sebastião de Leopoldina
image group `004640627`, beginning with Item 3 images 234–497 and its internal
indexes, for Aristão Ferreira Armond's reported 1879 birth. Indexed and
full-text searches returned no qualifying record. His original 1957 death
registration is catalogued, but its reported parent names do not establish the
fuller collaborative forms `Simplício Ferreira Armond` and `Elizia Balbina
Toledo`. A birth, baptism or marriage record closer to the relationships is
required to resolve those names and may also identify Liliosa's original
surname and parents.

The former human-intervention blocker is partially resolved. Three civil
marriage certificates and two original death-register entries have been
recovered from the authorised FamilySearch account and catalogued. The
original ChatGPT conversation still refers to 24 image attachments whose
binaries and metadata were not carried into the imported transcript. The exact
one-to-one attachment mapping cannot be reconstructed from the transcript
alone.

### Completion criteria

- Inspect the relevant FamilySearch Sources and Memories without treating
  collaborative-profile assertions as evidence.
- Preserve the closest available original image or authorised derivative with
  archival citation, checksum, rights and privacy review.
- Update `research/record-coverage.yaml` from `lead_only` to the correct
  resulting state.
- Record positive, negative and inaccessible searches in a detailed log.
- Create only source-qualified entities and preserve every conflict.
- Run the complete repository check before committing.

### Candidate processing order

After the model review, continue the authorised evidence audit in this order:

1. Aristão Ferreira Armond's birth, baptism or marriage record;
2. the death registration or burial record of Liliosa Paz Armond and other
   high-priority deceased direct ancestors;
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
- `AGENTS.md` is the stable context-loading and decision protocol. Volatile
  research state remains in `STATUS.md`, the coverage ledger and research logs
  so agent instructions do not become a duplicated project-memory file.
- The source-intake sequence is maintained with the active objective rather
  than in a separate task-specific plan.
- The frozen repository check runs locally and in GitHub Actions. Requiring it
  in branch rules remains an external repository-administration task.
- The third intake located Geraldo Paz Armond's original 18 February 1991
  death entry in the Volta Redonda civil register. It is inventoried as
  `DOC-0003`, catalogued as `SRC-0004`, and linked to the original FamilySearch
  record and image ARKs.
- The death entry directly supports Geraldo's death and gives secondary,
  directly stated evidence that Cidalia Engracio Armond was his spouse and
  Aristão Ferreira Armond and Liliosa Paz Armond were his parents.
- The handwritten death-entry number appears to be `39005`, while the
  FamilySearch index reports `39006`; both readings remain recorded.
- Three document source records, one owner-supplied roster source and their
  directly required linked entities are live. The planned three-record model
  review is complete.
- The family model now represents two reported parents without asserting a
  marriage or partnership between them. The previously modelled
  `partner_relationship` between Aristão and Liliosa was removed; their
  independent parent-child edges to Geraldo remain `strong-evidence`.
- Catalogued inventory files must now match their structured source's retained
  path and checksum, preventing silent provenance drift.
- `research/record-coverage.yaml` is the canonical operational matrix for
  missing vital records of deceased direct ancestors. FamilySearch profile IDs
  in that file are navigation leads only, and living people are excluded.
- The fourth document intake recovered the damaged 7 December 1949 marriage
  certificate of Antenor Muniz and Iris Bohrer. It is inventoried as
  `DOC-0004`, catalogued as `SRC-0005`, and retained as a private reconstructed
  PNG.
- That certificate supplies direct evidence of the marriage and Iris's
  married-name form, and directly states the parents of both spouses. The
  conclusions remain `strong-evidence` because the certificate and repository
  image are derivatives.
- Antenor's FamilySearch profile had the certificate attached as a user-created
  source; Iris's profile had no attached sources when reviewed.
- Liliosa Paz Armond's sole attached FamilySearch source was audited and found
  to be a person-level extraction from Geraldo's 1991 death registration. It
  proves only that she was reported as his mother; it is not her 1946 death
  registration.
- Liliosa's sole Memory, artifact `120876994`, is an eight-page February 1975
  issue of the newspaper *O Processo*. Its extracted text and rendered pages
  yielded no identifiable Liliosa, Aristão or Armond reference. It was not
  catalogued as genealogical evidence, and the negative result remains in the
  research log.
- Liliosa's death date is unresolved. The collaborative profile displays 16
  April 1946, while the imported conversation reports an earlier reading of 15
  November 1946 from an unavailable attachment. Neither date has a retained
  primary record.
- Aristão Ferreira Armond's original 1 November 1957 Volta Redonda death entry
  is inventoried as `DOC-0005`, catalogued as `SRC-0006`, and retained as a
  private reconstructed PNG. It confirms the death and age 78 and reports his
  parents as `Simplicio Armand` and `Eliza Ferreira Armand`.
- The reported parent-child relationships are `strong-evidence`, not
  `confirmed`, because the parent names are secondary information supplied at
  death. The record does not establish a relationship between the two reported
  parents.
- FamilySearch's index corrupts Aristão's name as `Axstai Ferreira Armand
  Armand` and duplicates part of his mother's surname. Those transcription
  defects are preserved as limitations rather than copied into preferred
  names.
- Aristão's sole Memory is the same 1975 issue of *O Processo* already audited
  under Liliosa. It adds no identifiable vital-record evidence and was not
  catalogued again.
- Indexed, spouse-linked, parent-linked and full-text FamilySearch searches
  found no qualifying birth, baptism or marriage record for Aristão. The
  negative result does not establish absence from unindexed register images.
- FamilySearch catalog `345430` identifies São Sebastião de Leopoldina baptism
  image group `004640627`; Item 3 images 234–497 includes 1878–1888 coverage
  and is the current bounded manual-review target.
- The identified Leopoldina marriage series in image group `004640631` ends in
  July 1897, when Aristão would have been approximately eighteen. A later
  marriage volume should be located before that branch is scanned manually.
- The initial direct-ancestor person block now follows Ahnentafel order:
  `P-0001` is the repository subject, `P-0002` and `P-0003` are his parents,
  and source-qualified positions now extend through `P-0017`. These IDs are
  immutable; the ordering is not genealogical evidence.
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
  `SRC-0002`; death is confirmed by the original register entry in `SRC-0004`;
  the birth still requires its own record.

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
- Status: marriage and reported parentage are supported by catalogued direct
  evidence in `SRC-0005`; birth and death records remain pending.

### Iris Bohrer Muniz

- Born: 27 February 1929 in Minas Gerais, Brazil.
- Died: 2021.
- Parents: João Gonçalves Bohrer and Selina Bohrer.
- Status: marriage, married-name form and reported parentage are supported by
  catalogued direct evidence in `SRC-0005`; birth and death records remain
  pending.

## Great-grandparents and earlier lines

### Aristão Ferreira Armond

- Born: about 1879.
- Died: 1 November 1957 in Volta Redonda, Rio de Janeiro, Brazil.
- Spouse: Liliosa Paz Armond.
- Parents: his death registration reports `Simplicio Armand` and `Eliza
  Ferreira Armand`, giving `strong-evidence` for those two parent-child
  relationships. The fuller forms `Simplício Ferreira Armond` and `Elizia
  Balbina Toledo` remain unresolved leads.
- Child: the 1991 death entry for Geraldo reports Aristão as his father, giving
  `strong-evidence` for that parent-child relationship.
- Evidence issue: the death is confirmed by `SRC-0006`, but the decisive birth,
  baptism or marriage record is still required to verify fuller parental names,
  maiden surname and the relationship to Liliosa.

### Liliosa Paz Armond

- Also appears in some material with `Ferreira Armond`; the original surname form and parentage remain unresolved.
- Born: approximately 1885–1887.
- Died: in 1946, according to conflicting uncatalogued leads. FamilySearch
  displays 16 April; the imported conversation reports 15 November from an
  unavailable attachment. The exact date remains unconfirmed.
- Spouse: Aristão Ferreira Armond.
- Parents: unknown. She is **not** to be recorded as a daughter of Simplício Ferreira Armond and Elizia Balbina Toledo without new primary evidence.
- Child: the 1991 death entry for Geraldo reports Liliosa as his mother, giving
  `strong-evidence` for that parent-child relationship.
- Evidence issue: FamilySearch source `SJBH-LL3` is a derivative reference to
  Geraldo's death registration, and Memory `120876994` is a 1975 newspaper
  issue. Neither is Liliosa's death or burial record.

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
- Status: his own marriage is supported by `SRC-0001`; Antenor's 1949 marriage
  certificate reports him as Antenor's father in `SRC-0005`.

### Luiza Fernandes de Azevedo

- Born: about 1898 in Bom Jesus da Cachoeira Alegre, then in the municipality of São Paulo do Muriaé, Minas Gerais, Brazil.
- Died: 1 July 1986, according to the family tree currently used as a lead.
- Parents: Secundino Maria de Azevedo and Theresa Fernandes de Azevedo.
- Status: her parentage is supported by `SRC-0001`; Antenor's 1949 marriage
  certificate reports her as Antenor's mother in `SRC-0005`. Exact birth and
  death facts require primary-source cataloguing.

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
- Status: Iris's 1949 marriage certificate reports him as her father in
  `SRC-0005`; his own vital events and parental transcription remain pending.

### Selina Bohrer

- Born: approximately 1889–1890.
- Died: 11 February 1987.
- Spouse: João Gonçalves Bohrer.
- Parents: Joaquim José Bohrer and Lucinda Ferreira da Silva Bohrer.
- Status: Iris's 1949 marriage certificate reports her as Iris's mother in
  `SRC-0005`; Selina's own death record remains to be catalogued.

### Joaquim José Bohrer

- Spouse: Lucinda Ferreira da Silva.
- Parent of Selina Bohrer.
- Public trees suggest Francisco José Bohrer and Rosa Eugênia de Lemos as parents, but this remains a hypothesis pending an original record.

## Known collateral relatives

Collateral relatives have been mentioned in family trees and documents, including siblings of Geraldo, Cidalia, Antenor and other ancestors. They should not yet be treated as complete sibling sets. Each must receive a source-based person record before inclusion in a definitive family group.

## Major unresolved conflicts

1. Exact birth date of Cidalia: 15 September or 15 November 1930.
2. Exact death date, original surname and parents of Liliosa Paz Armond.
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
- [x] Locate Aristão's 1957 death registration.
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
| P1 | Catalogue and model the first three original records | Requires source-image access | Tests the model before scale | Completed |
| P1 | Review the model and add canonical missing-record coverage | Low | Establishes a stable base for systematic research | Completed |
| P1 | Ingest remaining existing evidence | Depends on model review | Expands the source-qualified tree reproducibly | In progress |
| P2 | Re-evaluate assertion-level citation quality after 5–10 more varied records | Medium | Avoids conservative source-wide evidence labels at scale | Deferred pending evidence |
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
