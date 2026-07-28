# Project Status

> This file is the present operational snapshot. It contains the current
> objective, blockers, material conflicts and strategic priorities only.
> Research history belongs in `research/LOG.md` and its detailed logs;
> engineering history belongs in `CHANGELOG.md`; genealogical conclusions
> belong in structured YAML and source records.

## Current objective

Recover the underlying original record that describes Vicente José de Carvalho
Guimarães as Portuguese, then identify his Portuguese district, municipality
and parish before searching Portuguese archives or conservatories.

### Objective completion signal

- The transcript-only claim is traced to its original civil or parish image.
- The image is retained at the highest resolution authorised by the provider.
- Vicente's identity and relationship to Francisco José de Carvalho Guimarães
  are evaluated from the record rather than assumed from a collaborative tree.
- Any Portuguese locality is preserved at the precision actually stated; a
  surname or nationality alone is not converted into an island or parish.

## Next steps

This is the immediate execution queue, in order:

1. **Now:** identify the FamilySearch profile and attached source behind the
   transcript naming Vicente José de Carvalho Guimarães as Portuguese.
2. Recover and inspect the original record at the highest authorised
   resolution.
3. Search Vicente's marriage and death records for a Portuguese locality if
   the first record gives only a nationality.
4. **Human-access tasks:** request the João–Susanna ceremony entry from the
   Cúria and review Aristão's restricted parish registers when authorised.

Keep this queue short and actionable. Detailed person-by-record actions remain
canonical in `research/record-coverage.yaml`; strategic branch order remains
under **Strategic research priorities** below.

## Current blockers and dependencies

- The imported ChatGPT conversation refers to 24 image attachments whose
  binaries and metadata were not transferred. Their descriptions remain
  preserved in the conversation-transfer audit, but exact document matching
  requires the original attachments.
- FamilySearch image groups `004640627` and `004640632` contain the best
  baptism and marriage targets for Aristão, but the relevant original images
  display `Image Restricted`. Manual review requires authorised access through
  a FamilySearch Center or Library, or the record custodian.
- Archive enquiries, paid certificates and conservatory or parish requests
  require explicit user authorisation before submission.
- Six civil-record PDFs concerning living people are attached as `Public`
  Memories to `P-0001`. No copies were retained; changing their visibility is
  an external FamilySearch mutation requiring the owner's authorisation.
- Liliosa's reported 16 April 1946 death cannot yet be tested in the identified
  Volta Redonda register because the accessible series begins in November.
- FamilySearch exposes João and Susanna's 1882 marriage provision but no
  separate ceremony entry or Espírito Santo parish film series. The exact
  Cúria Metropolitana request is documented and requires explicit
  authorisation before submission.
- Requiring the repository-health workflow in GitHub branch rules requires
  repository-administrator access.

None of these dependencies prevents the current Vicente source-recovery work.

## Repository snapshot

| Item | Current state |
| --- | --- |
| Structured people | 20 |
| Structured families | 7 |
| Structured events | 6 |
| Structured places | 5 |
| Structured sources | 9 |
| Inventoried retained documents | 8 |
| Validation | 47 entities; zero errors or warnings at the last check |
| Automated tests | 53 passing at the last check |

Catalogued evidence currently includes:

- `SRC-0001` — 1916 marriage of Deocleciano Muniz Bittencourt and Luiza
  Fernandes de Azevedo;
- `SRC-0002` — 1952 marriage of Geraldo Paz Armond and Cidalia Engracio
  Guimarães;
- `SRC-0003` — privacy-minimised owner-supplied working roster;
- `SRC-0004` — 1991 death registration of Geraldo Paz Armond;
- `SRC-0005` — 1949 marriage of Antenor Muniz and Iris Bohrer; and
- `SRC-0006` — 1957 death registration of Aristão Ferreira Armond;
- `SRC-0007` — three-page 2019 full-content certificate of the 1916
  Deocleciano–Luiza marriage; and
- `SRC-0008` — March 1973 government driver-dossier index naming José Olavo
  Armond and his parents; and
- `SRC-0009` — original 1882 marriage provision for João Monis Bittencourt and
  Susanna Rita Brondão.

Source details, archival references, transcriptions, limitations and
conclusion links are canonical in `data/sources/`. Record-by-record gaps are
canonical in `research/record-coverage.yaml`.

## Research snapshot

| Area | Strongest current position | Strategic gap |
| --- | --- | --- |
| Armond and Paz | Aristão's death is confirmed; a second original government record independently names Liliosa Paz Armond and reports the couple as José Olavo's parents | Birth or baptism of Aristão; marriage to Liliosa; Liliosa's own vital records and parents |
| Muniz Bittencourt and Azevedo | The 1916 marriage reports Deocleciano's parents; an original 1882 provision names João and Susanna and the intended Espírito Santo parish | Completed ceremony entry; João and Susanna's own vital records; test rather than assume island origin |
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
8. Whether the 1871 naturalisation link attached to João's profile concerns the
   same person; the unproved 1864 birth would make the chronology unusually
   early and requires the original record.
9. FamilySearch's index table displays `1633` for the provision catalogued as
   `SRC-0009`; the original image and citation state 23 December 1882.

Do not resolve a conflict by deleting the weaker version. Preserve every
material interpretation with its source and confidence.

## Strategic research priorities

1. Recover the record describing Vicente José de Carvalho Guimarães as
   Portuguese, then identify his parish before searching Portugal while the
   three higher-priority lines remain access-blocked.
2. Obtain the João–Susanna ceremony entry from the Cúria and their earlier
   records.
3. Locate Liliosa's own death, burial, birth or marriage record.
4. Obtain authorised access to Aristão's identified baptism and marriage
   register targets.
5. Catalogue João Gonçalves Bohrer and Selina Bohrer's own vital records.
6. Extend the Engracio/Souza, Guimarães and Azevedo lines one documented
   generation at a time.

The canonical person-by-record actions and last-reviewed dates are maintained
only in `research/record-coverage.yaml`.

## Engineering state

- **Active:** recover Vicente's underlying record and Portuguese locality;
  reassess assertion-level citation quality after 5–10 varied records.
- **External:** require the frozen repository-health check in GitHub branch
  rules.
- **Deferred until schema stability:** generated person pages and a
  privacy-filtered GEDCOM export.
- **Complete:** versioned schemas, evidence inventory, stable ID allocation,
  recoverable batch promotion, validation, tests and GitHub Actions.

Completed engineering work is recorded only in `CHANGELOG.md`.
