# Project Status

> This file is the present operational snapshot. It contains the current
> objective, blockers, material conflicts and strategic priorities only.
> Research history belongs in `research/LOG.md` and its detailed logs;
> engineering history belongs in `CHANGELOG.md`; genealogical conclusions
> belong in structured YAML and source records.

## Current objective

Test whether the Vicente José de Carvalho Guimarães named in an 1866 Vila do
Rio Claro power of attorney is the same person as the documented father of
Francisco, and locate Vicente's marriage or death record with a Portuguese
locality.

### Objective completion signal

- A record links Vicente to Maria Tertuliana, Francisco or another
  source-qualified family member, or the 1866 candidate is rejected with a
  documented reason.
- Vicente's own marriage, death or burial series is searched in Rio Claro and
  Carangola with exact and documented name variants.
- Any Portuguese locality is preserved at the precision actually stated; the
  nationality in `SRC-0010` is not converted into an island or parish.
- Any retained image uses the highest resolution authorised by the provider.

## Next steps

This is the immediate execution queue, in order:

1. **Now:** inspect the 1866 Vila do Rio Claro power-of-attorney context and
   test its chronology against Francisco and Maria Tertuliana.
2. Search Rio Claro and Carangola marriage and death collections for Vicente
   and Maria Tertuliana.
3. If a record identifies a Portuguese locality, map its archive and parish
   series before searching Portugal.
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
- Liliosa's reported 16 April 1946 death cannot yet be tested in the identified
  Volta Redonda register because the accessible series begins in November.
- FamilySearch exposes João and Susanna's 1882 marriage provision but no
  separate ceremony entry. The provision was re-read as directed to the Santo
  Antônio de Sapucaia parish (not Espírito Santo); the surviving Sapucaia
  marriage-book series and the exact archival request require identification
  and explicit authorisation before submission.
- Requiring the repository-health workflow in GitHub branch rules requires
  repository-administrator access.

None of these dependencies prevents the current Vicente source-recovery work.

## Repository snapshot

| Item | Current state |
| --- | --- |
| Structured people | 26 |
| Structured families | 12 |
| Structured events | 18 |
| Structured places | 9 |
| Structured sources | 16 |
| Inventoried retained documents | 15 |
| Validation | 81 entities; zero errors or warnings at the last check |
| Automated tests | 56 passing at the last check |

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
  Susanna Rita Brondão; and
- `SRC-0010` — certified full-content copy of the 1915 Carvalho Guimarães
  collective birth registration;
- `SRC-0011` — private certified birth record for the living repository
  subject, with two byte-identical FamilySearch Memories deduplicated to one
  preservation file;
- `SRC-0012`–`SRC-0015` — four distinct private civil manifestations of the
  repository subject's 2003 marriage; and
- `SRC-0016` — a 2018 academic dissertation retained as a research lead for
  the historical Ferreira Armond group, not proof of this family's descent.

Source details, archival references, transcriptions, limitations and
conclusion links are canonical in `data/sources/`. Record-by-record gaps are
canonical in `research/record-coverage.yaml`.

## Research snapshot

| Area | Strongest current position | Strategic gap |
| --- | --- | --- |
| Armond and Paz | Aristão's death is confirmed; a second original government record independently names Liliosa Paz Armond and reports the couple as José Olavo's parents; a secondary academic study supplies historical context but no line linkage | Birth or baptism of Aristão; marriage to Liliosa; Liliosa's own vital records and parents |
| Muniz Bittencourt and Azevedo | The 1916 marriage reports Deocleciano's parents; an original 1882 provision names João and Susanna and the intended Santo Antônio de Sapucaia parish | Completed ceremony entry in the Sapucaia registers; João and Susanna's own vital records; test rather than assume island origin |
| Engracio, Souza and Guimarães | The 1915 collective registration documents Maria Amora, her parents and all four grandparents | Locate Vicente's family-linked marriage or death record and resolve Maria Amora/Aurora |
| Bohrer | Iris's 1949 marriage directly reports João Gonçalves Bohrer and Selina Bohrer | Catalogue their own vital records and verify the next generation |
| Portuguese origins | `SRC-0010` directly reports Vicente as Portuguese; an 1866 Rio Claro record is an unlinked identity lead | Identify a district, municipality and parish before searching Portugal |

The direct-line working roster follows Ahnentafel order from `P-0001` through
`P-0017`. These are immutable repository identifiers, not proof of
relationships. Collaborative profiles remain navigation leads only.

## Material unresolved conflicts

1. Cidalia's birth date: 15 September or 15 November 1930; and the recorded
   `Engracio`, `Igracio` and married-name forms require source-by-source
   preservation rather than silent normalisation.
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
10. Maria Amora Guimarães in the 1915 birth registration versus Maria Aurora
    Guimarães in later family information.
11. Whether the 1866 Vila do Rio Claro power of attorney names the same
    Vicente José de Carvalho Guimarães documented as Francisco's father.

Do not resolve a conflict by deleting the weaker version. Preserve every
material interpretation with its source and confidence.

## Strategic research priorities

1. Test the 1866 Vicente identity and locate a family-linked record that gives
   his Portuguese locality while the three higher-priority lines remain
   access-blocked.
2. Obtain the João–Susanna ceremony entry from the Santo Antônio de Sapucaia
   parish registers and their earlier records.
3. Locate Liliosa's own death, burial, birth or marriage record.
4. Obtain authorised access to Aristão's identified baptism and marriage
   register targets.
5. Catalogue João Gonçalves Bohrer and Selina Bohrer's own vital records.
6. Extend the Engracio/Souza, Guimarães and Azevedo lines one documented
   generation at a time.

The canonical person-by-record actions and last-reviewed dates are maintained
only in `research/record-coverage.yaml`.

## Engineering state

- **Active:** test the 1866 Vicente lead and locate his Portuguese locality;
  reassess assertion-level citation quality after 5–10 varied records.
- **External:** require the frozen repository-health check in GitHub branch
  rules.
- **Deferred until schema stability:** generated person pages and a
  privacy-filtered GEDCOM export.
- **Complete:** versioned schemas, evidence inventory, stable ID allocation,
  recoverable batch promotion, validation, tests and GitHub Actions.

Completed engineering work is recorded only in `CHANGELOG.md`.
