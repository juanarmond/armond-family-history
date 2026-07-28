# Research Backlog

## Priority 0 — Preserve and catalogue existing evidence

> Blocked as of 28 July 2026: no source image or document exists in the
> worktree, Git history or Git LFS. Authorised, privacy-reviewed copies must be
> added before these tasks can be completed.

- [ ] Assign source IDs to every certificate, identity document and screenshot already supplied.
- [ ] Store a clean image filename and an English abstract for each document.
- [ ] Re-transcribe ambiguous handwritten fields at full resolution.
- [ ] Create initial person IDs and family IDs only after the source catalogue begins.

## Priority 1 — Armond and Paz lines

- [ ] Locate the birth or baptism of Aristão Ferreira Armond, approximately 1879.
- [ ] Locate the marriage of Aristão Ferreira Armond and Liliosa Paz Armond.
- [ ] Locate Aristão's 1957 death registration.
- [ ] Confirm or reject Simplício Ferreira Armond and Elizia Balbina Toledo as Aristão's parents using a primary record.
- [ ] Identify Liliosa's parents and original surname from her birth, baptism, marriage or death records.
- [ ] Search Rosário da Limeira, Muriaé, Carangola, São Francisco do Glória, Piacatuba and Leopoldina collections as appropriate.

## Priority 2 — Muniz Bittencourt and Brandão lines

- [ ] Catalogue the 21 October 1916 marriage of Deocleciano Muniz Bittencourt and Luiza Fernandes de Azevedo.
- [ ] Locate Deocleciano's birth or baptism in Sapucaia, Rio de Janeiro, approximately 1892.
- [ ] Locate the marriage of João Muniz Bittencourt and Suzana Ritta Brandão.
- [ ] Locate João's birth, death, immigration or naturalisation records.
- [ ] Test the claimed Azorean or other island origin without assuming it.
- [ ] Identify Suzana Ritta Brandão's parents from an original record.

## Priority 3 — Portuguese origin of Vicente José de Carvalho Guimarães

- [ ] Locate Vicente's marriage to Maria Tertuliana da Conceição.
- [ ] Locate Vicente's death registration in Carangola or the relevant district.
- [ ] Search naturalisation, foreigner registration, passport and passenger records.
- [ ] Identify district, municipality and parish in Portugal.
- [ ] Once the parish is known, search the relevant parish books generation by generation.

## Priority 4 — Bohrer lines

- [ ] Catalogue the deaths of João Gonçalves Bohrer and Selina Bohrer.
- [ ] Re-transcribe João's parents from the original death record.
- [ ] Locate João's marriage to Selina.
- [ ] Locate Selina's birth or baptism and confirm Joaquim José Bohrer and Lucinda Ferreira da Silva as parents.
- [ ] Locate Joaquim's marriage or death record.
- [ ] Test the proposed parents Francisco José Bohrer and Rosa Eugênia de Lemos.
- [ ] Determine the first documented immigrant generation; do not infer Germany from the surname alone.

## Priority 5 — Engracio, Souza and Guimarães lines

- [ ] Catalogue the death of Antonio Engracio Filho.
- [ ] Locate Antonio Engracio Filho's birth or baptism, approximately 1889–1890.
- [ ] Locate his marriage to Maria Aurora Guimarães.
- [ ] Locate the marriage of Antonio Engracio de Souza and Luzia Pinheiro da Conceição.
- [ ] Catalogue Maria Aurora's death and the civil registration listing her sibling group.
- [ ] Extend Francisco José de Carvalho Guimarães and Emmerenciana Maria de Jesus only through original records.

## Priority 6 — Azevedo line

- [ ] Locate Luiza Fernandes de Azevedo's birth or baptism, approximately 1898.
- [ ] Confirm the exact locality and name variants.
- [ ] Locate the marriage of Secundino Maria de Azevedo and Theresa Fernandes de Azevedo.
- [ ] Identify their parents.

## Repository engineering

- [x] Create YAML schemas for people, families, events, places and sources.
- [x] Add validation for identifiers, dates, relationships and source references.
- [x] Add stable entity, person-profile, source-record and research-log templates.
- [x] Add a privacy-aware ingestion plan for existing documents.
- [x] Establish permanent project principles and an append-only cumulative research log.
- [x] Consolidate obsolete foundation instructions and placeholder documentation.
- [x] Add a versioned schema and validation for the document inventory.
- [x] Add explicit entity schema versions before ingesting the first source.
- [x] Separate source form, information quality and evidence type in the evidence model.
- [x] Add controlled relationship types and event participant roles before scaling.
- [x] Refactor the validator into focused modules without changing its public command.
- [ ] Add safe ID allocation and entity-skeleton automation.
- [ ] Add a script to generate human-readable person pages from YAML.
- [ ] Add a GEDCOM export only after the core schema and evidence model are stable.
- [x] Add automated checks preventing unsupported `confirmed` relationships.

## Definition of done for a research task

A task is complete only when:

1. the searched collections and date/place range are documented;
2. positive or negative results are logged;
3. the record image or archival reference is preserved where legally permitted;
4. a transcription or abstract is included;
5. all affected people, events and relationships are updated;
6. the confidence level and remaining conflicts are explicit.
