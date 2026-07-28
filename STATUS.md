# Project Status

> This file is the present operational snapshot. It contains the current
> objective, blockers, material conflicts and strategic priorities only.
> Research history belongs in `research/LOG.md` and its detailed logs;
> engineering history belongs in `CHANGELOG.md`; genealogical conclusions
> belong in structured YAML and source records.

## Current objective

Manually review São Sebastião de Leopoldina baptism image group `004640627`
for Aristão Ferreira Armond's reported 1879 birth.

Start with Item 3, images 234–497:

1. identify its internal title pages, volume boundaries and indexes;
2. locate the 1879 sequence;
3. inspect variants of `Armond`, `Armand` and `Ferreira Armond`, including
   entries naming Simplicio and Eliza; and
4. record the exact images reviewed, including a negative result if no
   qualifying entry is found.

Indexed and full-text searches returned no qualifying record. That does not
establish absence from the unindexed images. Aristão's 1957 death registration
is catalogued as `SRC-0006`; it reports `Simplicio Armand` and `Eliza Ferreira
Armand` as his parents but does not establish their fuller collaborative-tree
name forms.

### Objective completion signal

- The relevant internal index and 1879 image range are identified and reviewed.
- Positive, negative and inaccessible results are reproducibly logged.
- Any qualifying image is inventoried, privacy-reviewed and source-catalogued.
- Aristão's coverage entry and affected conclusions are updated without
  promoting collaborative-tree assertions.

## Current blockers and dependencies

- The imported ChatGPT conversation refers to 24 image attachments whose
  binaries and metadata were not transferred. Their descriptions remain
  preserved in the conversation-transfer audit, but exact document matching
  requires the original attachments.
- The identified São Sebastião de Leopoldina marriage volume ends in July
  1897, probably before Aristão and Liliosa married. A later volume must be
  identified before a bounded marriage review.
- Archive enquiries, paid certificates and conservatory or parish requests
  require explicit user authorisation before submission.
- Requiring the repository-health workflow in GitHub branch rules requires
  repository-administrator access.

None of these dependencies prevents the current baptism-register review.

## Repository snapshot

| Item | Current state |
| --- | --- |
| Structured people | 17 |
| Structured families | 6 |
| Structured events | 5 |
| Structured places | 4 |
| Structured sources | 6 |
| Inventoried retained documents | 5 |
| Validation | 38 entities; zero errors or warnings at the last check |
| Automated tests | 51 passing at the last check |

Catalogued evidence currently includes:

- `SRC-0001` — 1916 marriage of Deocleciano Muniz Bittencourt and Luiza
  Fernandes de Azevedo;
- `SRC-0002` — 1952 marriage of Geraldo Paz Armond and Cidalia Engracio
  Guimarães;
- `SRC-0003` — privacy-minimised owner-supplied working roster;
- `SRC-0004` — 1991 death registration of Geraldo Paz Armond;
- `SRC-0005` — 1949 marriage of Antenor Muniz and Iris Bohrer; and
- `SRC-0006` — 1957 death registration of Aristão Ferreira Armond.

Source details, archival references, transcriptions, limitations and
conclusion links are canonical in `data/sources/`. Record-by-record gaps are
canonical in `research/record-coverage.yaml`.

## Research snapshot

| Area | Strongest current position | Strategic gap |
| --- | --- | --- |
| Armond and Paz | Aristão's death is confirmed; his reported parents and his parentage of Geraldo have strong evidence | Birth or baptism of Aristão; marriage to Liliosa; Liliosa's identity and parents |
| Muniz Bittencourt and Azevedo | The 1916 and 1949 marriages directly report two generations of parents | Earlier records for João Muniz Bittencourt and Suzana Ritta Brandão; test island origin |
| Engracio, Souza and Guimarães | Cidalia's 1952 marriage directly reports Antonio Engracio Filho and Maria Aurora Guimarães | Recover and catalogue the older death, marriage and collective registration images |
| Bohrer | Iris's 1949 marriage directly reports João Gonçalves Bohrer and Selina Bohrer | Catalogue their own vital records and verify the next generation |
| Portuguese origins | Vicente José de Carvalho Guimarães is a transcript-only lead described as Portuguese | Recover the underlying record and identify a district, municipality and parish |

The direct-line working roster follows Ahnentafel order from `P-0001` through
`P-0017`. These are immutable repository identifiers, not proof of
relationships. Collaborative profiles remain navigation leads only.

## Material unresolved conflicts

1. Cidalia's birth date: 15 September or 15 November 1930.
2. Liliosa's exact death date, original surname and parents.
3. The fuller names and identities of Aristão's reported parents.
4. The exact transcription of João Gonçalves Bohrer's parents.
5. Vicente José de Carvalho Guimarães's Portuguese parish.
6. Whether João Muniz Bittencourt had an Azorean, Madeiran or other Portuguese
   island origin.
7. Whether several nineteenth-century collaborative profiles refer to the same
   people documented in the family records.

Do not resolve a conflict by deleting the weaker version. Preserve every
material interpretation with its source and confidence.

## Strategic research priorities

1. Complete the current Aristão baptism review, then identify the later
   marriage series for Aristão and Liliosa.
2. Locate Liliosa's own death, burial, birth or marriage record.
3. Locate João Muniz Bittencourt and Suzana Ritta Brandão's marriage and
   earlier records.
4. Recover the record describing Vicente José de Carvalho Guimarães as
   Portuguese, then identify his parish before searching Portugal.
5. Catalogue João Gonçalves Bohrer and Selina Bohrer's own vital records.
6. Extend the Engracio/Souza, Guimarães and Azevedo lines one documented
   generation at a time.

The canonical person-by-record actions and last-reviewed dates are maintained
only in `research/record-coverage.yaml`.

## Engineering state

- **Active:** ingest remaining authorised evidence and reassess
  assertion-level citation quality after 5–10 varied records.
- **External:** require the frozen repository-health check in GitHub branch
  rules.
- **Deferred until schema stability:** generated person pages and a
  privacy-filtered GEDCOM export.
- **Complete:** versioned schemas, evidence inventory, stable ID allocation,
  recoverable batch promotion, validation, tests and GitHub Actions.

Completed engineering work is recorded only in `CHANGELOG.md`.
