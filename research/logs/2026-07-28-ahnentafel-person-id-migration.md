# Ahnentafel person-ID migration

## Date

28 July 2026

## Objective

Align the initial direct-ancestor person identifiers with the repository
owner's requested Ahnentafel order while the live dataset is still small.

## Decision

The first direct-ancestor block now uses:

| Person ID | Ahnentafel position | Person |
| --- | ---: | --- |
| `P-0001` | 1 | Juan Carlos Muniz Armond |
| `P-0002` | 2 | Luis Carlos Igracio Armond |
| `P-0003` | 3 | Lucinea Aparecida Muniz Armond |
| `P-0004` | 4 | Geraldo Paz Armond |
| `P-0005` | 5 | Cidalia Engracio Guimarães |
| `P-0006` | 6 | Antenor Muniz |
| `P-0007` | 7 | Iris Bohrer Muniz |
| `P-0008` | 8 | Aristão Ferreira Armond |
| `P-0009` | 9 | Liliosa Paz Armond |
| `P-0010` | 10 | Antonio Engracio Filho |
| `P-0011` | 11 | Maria Aurora Guimarães |
| `P-0012` | 12 | Deocleciano Muniz Bittencourt |
| `P-0013` | 13 | Luiza Fernandes de Azevedo |
| `P-0014` | 14 | João Gonçalves Bohrer |
| `P-0015` | 15 | Selina Bohrer |

## Remapped live entities

- Deocleciano: `P-0001` to `P-0012`.
- Luiza: `P-0002` to `P-0013`.
- Geraldo: `P-0003` to `P-0004`.
- Cidalia: `P-0004` to `P-0005`.
- Reserved death-record drafts: Aristão `P-0005` to `P-0008` and Liliosa
  `P-0006` to `P-0009`.

Every affected source, event, family, draft and detailed research-log reference
was migrated with the person file.

## Evidence boundary

`SRC-0003` records the owner's direct-ancestor roster and preferred-name
spellings. It does not confirm unsourced vital events or relationships.
Existing document-backed conclusions retain their original sources.

## Stability rule

These IDs are stable after this migration. A future parentage correction must
change the cited relationship rather than silently moving an existing person
to a new number. The initial numbering reflects Ahnentafel order at allocation
time; it is not itself evidence.

## Migration effort and impact

- Migration effort: low because only four live person entities and two drafts
  existed before the change.
- Long-term maintenance: neutral if identifiers remain immutable; harmful if
  later agents repeatedly renumber people to preserve visual order.
- Historical integrity: Git retains the pre-migration identifier state.
