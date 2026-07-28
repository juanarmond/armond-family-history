# FamilySearch Armond–Guimarães marriage-record ingestion

## Date

28 July 2026

## Research question

Can the marriage evidence for Geraldo Paz Armond and Cidalia Engracio
Guimarães be recovered from the authorised FamilySearch account, preserved
without conflating alternate photographs, and catalogued while retaining every
illegible or conflicting field?

## Profiles and path inspected

- Geraldo Paz Armond: FamilySearch profile `GQJ1-RVK`.
- Cidalia Engracio Armond: FamilySearch profile `GQJ1-K3M`.
- Access path: Geraldo's Memories gallery and the authenticated image viewer.
- Access date: 28 July 2026.

Profile conclusions and collaborative-tree values were not used as evidence.

## Search path and result

1. Geraldo's Memories gallery contained one death-certificate image and three
   images titled `Certidao de Casamento`.
2. Each marriage image was opened separately. The viewer identified upload
   filenames `IMG_5917.JPG`, `IMG_2871.JPG` and `IMG_2211.JPG`, all uploaded on
   24 February 2020.
3. Visual comparison established that they are alternate photographs of one
   damaged and taped certificate, not three pages.
4. The ordinary viewer download did not yield a controlled-browser file. For
   each Memory, all twelve level-10 Deep Zoom tiles were exported, their
   one-pixel overlaps removed, and the decoded pixels stitched into a
   756×1008 PNG.
5. All three views were retained because the differences in exposure and
   framing make different text legible. No crop or enhancement replaced the
   preservation files.

## FamilySearch memory identifiers

| Upload filename | Storage identifier | Repository role |
| --- | --- | --- |
| `IMG_5917.JPG` | `TH-904-96968-1121-80` | Alternate detail view |
| `IMG_2871.JPG` | `TH-904-96968-1120-79` | Alternate detail view |
| `IMG_2211.JPG` | `TH-904-96968-1122-81` | Primary catalogue view |

## Transcription findings

The readable portions identify:

- marriage register number 898, book 13-B, apparently page 21 verso;
- Geraldo Paz Armond and Cidalia Engracio Guimarães as the spouses;
- marriage in Eugenópolis on 31 May 1952;
- Geraldo reported as born in Limeira on 30 January 1915;
- Cidalia reported as born in Alvorada on 15 September 1930;
- Cidalia's occupation as domestic worker;
- Cidalia's married signature form as `Cidalia Engracio Armond`; and
- parentage lines that are partly hidden by tape.

The source record transcribes only text that can be read across the three
views. Brackets mark uncertainty or physical obstruction.

## Conflict retained

This certificate supports the `15 September 1930` version of Cidalia's birth
date. The repository also preserves a `15 November 1930` version derived from
earlier material. A marriage certificate supplies secondary information for a
birth, so this record does not resolve the conflict. Cidalia's original birth
registration remains required.

## Evidence assessment

The certificate gives direct evidence of the marriage and the name adopted by
the bride. It gives secondary information about both births. Because this is a
certificate derived from the civil register, the document is badly damaged,
and the retained PNGs are technical derivatives reconstructed from viewer
tiles, the marriage and partner relationship are classified
`strong-evidence`, not `confirmed`.

## Privacy and preservation

- Inventory: `DOC-0002`.
- Source: `SRC-0002`.
- Rights: private research.
- Privacy review: cleared; both spouses are deceased.
- Sensitive content: signatures.
- Public-export rule: exclude the images.

## Structured data

The validated batch prepares:

- `P-0003` — Geraldo Paz Armond;
- `P-0004` — Cidalia Engracio Guimarães;
- `F-0002` — their spouse relationship;
- `E-0002` — their 31 May 1952 marriage;
- `PL-0002` — Eugenópolis, Minas Gerais, Brazil; and
- `SRC-0002` — the marriage certificate and its three alternate views.

No parents or children are created from this source. Parentage is partly
obscured, and those people should enter the live model only with an adequately
transcribed supporting source.

## Next action

Inspect Geraldo's attached source and death-certificate Memory, then recover the
clearest distinct marriage or death record needed to complete the three-record
schema sample.

## Post-ingestion file consolidation

After the initial ingestion commit, the repository owner reviewed the three
preservation files and selected the `IMG_2211.JPG` reconstruction as the
clearest view. It is now retained under the canonical filename
`SRC-0002-marriage-geraldo-paz-armond-cidalia-engracio-guimaraes-1952-reconstructed.png`.
The two less-readable alternates were removed from the current worktree to
avoid redundant evidence files. They remain recoverable from Git commit
`3dc9c5e`, and the inventory continues to preserve the provenance of all three
FamilySearch Memories.
