# FamilySearch direct-line Memories audit

## Research question

Which FamilySearch Memories are attached to the repository's current direct
line, which contain qualifying genealogical records, which are duplicates, and
which require privacy or preservation action?

## Scope and method

The authenticated FamilySearch Memories tab was reviewed read-only for every
current direct-line person with a known profile identifier, beginning with the
repository subject and proceeding in Ahnentafel order from `P-0001` through
`P-0015`. `P-0016` and `P-0017` are source-derived working identities without
known collaborative profiles and therefore had no Memories page to audit.

Each card was opened when its title did not establish its type. Documents were
distinguished from photographs, newspapers, academic material and tree
screenshots. Repeated tagging of one artifact to two people was treated as one
Memory, not two independent sources. No Family Tree values were used as
evidence, and no FamilySearch profile, tag, source or visibility setting was
changed.

## Results by person

| Person | Profile | Memories | Result |
| --- | --- | ---: | --- |
| `P-0001` | `GQJ1-N2D` | 7 | Six personal civil PDFs concerning living people and one academic article; none retained |
| `P-0002` | `GQJ1-KSS` | 0 | No Memories |
| `P-0003` | `GQJ1-V1L` | 0 | No Memories |
| `P-0004` | `GQJ1-RVK` | 4 | `SRC-0004` plus the three alternate `SRC-0002` photographs |
| `P-0005` | `GQJ1-K3M` | 4 | One unsourced genealogical display plus the three `SRC-0002` photographs |
| `P-0006` | `GQVM-HXH` | 1 | Existing `SRC-0005` certificate |
| `P-0007` | `GQJ1-HG4` | 1 | Same Memory as `SRC-0005`; not a second source |
| `P-0008` | `GW4P-R9Z` | 1 | Shared 1975 newspaper issue already rejected as vital-record evidence |
| `P-0009` | `GQJ1-ZNC` | 1 | Same 1975 newspaper issue, Memory `120876994` |
| `P-0010` | `GNZY-KT4` | 0 | No Memories |
| `P-0011` | `GQVR-167` | 0 | No Memories |
| `P-0012` | `GQVM-3QD` | 5 | One portrait, `SRC-0001`, and a newly catalogued three-page certificate |
| `P-0013` | `GQVM-4YJ` | 5 | Same five Memories as `P-0012`; no duplicate sources created |
| `P-0014` | `GQJ1-J6P` | 6 | Historical family/house photographs and duplicate crops; no civil or parish record |
| `P-0015` | `G7PC-6K5` | 3 | Three photographs shared with `P-0014`; no civil or parish record |

## Living-person privacy finding

All seven Memories attached to `P-0001` display `Public`. Six are civil
documents involving living people, including two separately stored birth PDFs
and four marriage-related PDFs. The visible storage identifiers are:

- `TH-7781-105179-4633-99`;
- `TH-7781-105179-4634-2`;
- `TH-7783-105179-4791-76`;
- `TH-7782-105179-4564-90`;
- `TH-7782-105179-4562-84`; and
- `TH-7783-105179-4793-62`.

The seventh Public Memory is an academic article rather than a personal
record. No living-person PDF was downloaded or copied into the repository.
Changing Memory visibility is an external mutation and requires explicit owner
authorisation.

## New qualifying source

Three Memories form one full-content civil marriage certificate issued in
Carangola on 15 July 2019:

- `89626504`, page 1, uploaded as `20190724_170232~2.jpg`;
- `89626465`, page 2, uploaded as `IMG-20190724-WA0293~2.jpeg`; and
- `89626366`, page 3, uploaded as `IMG-20190724-WA0295~2.jpeg`.

The certificate identifies book 8-B, page 118 and record 62 for the 21 October
1916 marriage of Deocleciano Muniz Bittencourt and Luiza Fernandes de Azevedo.
It is catalogued once as `SRC-0007`, not as three sources. All three authorised
original-upload JPEGs were retained at their encoded resolutions.

## Preservation upgrades

Normal FamilySearch downloads became available during this audit. Five
existing technical reconstructions were superseded in the current worktree by
authorised original-file or original-image downloads:

| Source | Previous pixels | Retained pixels | Retained form |
| --- | ---: | ---: | --- |
| `SRC-0001` | 718×1205 | 718×1205 | originally uploaded JPEG |
| `SRC-0002` | 756×1008 | 3024×4032 | originally uploaded JPEG |
| `SRC-0004` | 1196×868 | 4783×3469 | original-image `JPG Only` download |
| `SRC-0005` | 612×816 | 2448×3264 | originally uploaded JPEG |
| `SRC-0006` | 1093×835 | 4372×3340 | original-image `JPG Only` download |

The superseded reconstructions remain recoverable from Git history. No
genealogical conclusion changed because each new file depicts the same
previously catalogued record.

## Photographic Memories

The six `P-0014` Memories and three `P-0015` Memories contain overlapping
historical group, house and portrait photographs, including `João Bohrer..jpg`,
`Rua Dr. Paulo Mendes, 205.jpg`, `IMG_1615.jpg`, `IMG_1612.jpg` and duplicate
portrait crops. They may support future family-history context, but they are
not substitutes for vital records and were not added to the evidence
catalogue. A separate media archive should be designed only when photographic
identity, rights and duplicate handling become an active objective.

## Conclusion

The currently mapped direct-line Memories pages are fully audited. The only
new qualifying record is `SRC-0007`; all other document Memories were already
catalogued, duplicated an existing source, concerned living people, or were not
genealogical records. The six Public living-person civil PDFs require an owner
privacy decision.

## Next action

1. Ask the repository owner whether the six Public civil Memories on `P-0001`
   may be changed to Private or Private to Group.
2. Complete a diplomatic transcription of `SRC-0007` pages 2–3 when useful.
3. Resume the search for Liliosa's own 1946 death or burial record.

## Later amendment

The owner subsequently authorised private-repository retention of the
`P-0001` civil PDFs. On reinspection later on 28 July 2026, all seven Memories
displayed `Private`; no visibility setting was changed by the research agent.
Six unique files were catalogued as `SRC-0011` through `SRC-0016`. The two
birth Memory entries yielded one byte-identical PDF and were deduplicated to a
single preservation file. See
`2026-07-28-familysearch-living-profile-download-and-article-review.md`.
