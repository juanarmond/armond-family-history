# FamilySearch marriage-record ingestion

## Date

28 July 2026

## Research question

Can an authorised copy of the previously reviewed 21 October 1916 marriage
record of Deocleciano Muniz Bittencourt and Luiza Fernandes de Azevedo be
recovered from FamilySearch, privacy-reviewed and catalogued without relying on
the collaborative tree as evidence?

## Account and profiles inspected

- Authenticated FamilySearch Family Tree account authorised by the repository
  owner.
- Deocleciano Muniz Bittencourt: FamilySearch profile `GQVM-3QD`.
- Luiza Fernandes de Azevedo: FamilySearch profile `GQVM-4YJ`.
- Access path: each profile's Sources and Memories tabs.
- Access date: 28 July 2026.

No FamilySearch profile assertion was treated as evidence in its own right.

## Search path and results

1. Inspected Deocleciano's Sources tab. It contained one attached source: a
   1983 Rio de Janeiro civil record concerning a child.
2. Inspected Luiza's Sources tab. It likewise contained one 1983 Rio de
   Janeiro civil record concerning a child.
3. Recorded the negative result that the 1916 marriage certificate was not
   attached as a formal source to either spouse.
4. Inspected Deocleciano's five Memories. The gallery contained a Memory titled
   `Certidão de Casamento Deocleciano e Luiza`.
5. Opened the authenticated image viewer. FamilySearch identified the uploaded
   filename as `IMG-20181224-WA0155~2.jpg`, upload date 24 July 2019, and
   storage identifier `TH-904-91822-179-82`.
6. The viewer's ordinary download action was not exposed to the controlled
   browser as a downloadable file. The complete level-11 Deep Zoom tile set was
   therefore exported: fifteen JPEG tiles covering columns 0–2 and rows 0–4.
7. Removed the standard one-pixel tile overlaps and stitched the decoded pixels
   into a 718×1205 PNG. No crop, enhancement, rotation, transcription overlay or
   content alteration was applied.

## Retained file

- Inventory: `DOC-0001`.
- Source: `SRC-0001`.
- Path:
  `evidence/civil/SRC-0001-marriage-deocleciano-muniz-bittencourt-luiza-fernandes-de-azevedo-1916-reconstructed.png`.
- SHA-256:
  `3444e92ef729f2e76a54ea7ace3f5611cd4509457a9ffb4dee59f537bc46c248`.
- Rights: private research.
- Privacy review: cleared for this private repository.
- Sensitive content retained: the issuing registrar's signature and office
  contact details, which authenticate the certificate. The image must not be
  included in public exports.
- Limitation: this is a pixel-preserving reconstruction from viewer tiles, not
  the originally uploaded JPEG and not an image of the 1916 register page.

## Transcription findings

The certified copy states:

- register book 8, page 118-v, record 62;
- marriage on 21 October 1916 in Carangola, Minas Gerais;
- Deocleciano Muniz Bittencourt, single, born in Sapucaia, Rio de Janeiro,
  aged 24, son of João Muniz Bittencourt and Suzana Ritta Brandão;
- Luiza Fernandes de Azevedo, single, born in Bom Jesus da Cachoeira Alegre in
  the municipality of São Paulo do Muriaé, aged 18, daughter of Secundino Maria
  de Azevedo and Theresa Fernandes de Azevedo;
- community-of-property regime; and
- certified copy issued in Carangola on 6 January 2004.

The full Portuguese transcription is retained in `SRC-0001`.

## Evidence assessment

The record directly supports the marriage event and provides contemporary
information about the spouses' names, ages, birthplaces and reported parents.
The 2004 certificate is a certified derivative of the 1916 register entry, and
the repository file is a further technical derivative reconstructed from
viewer tiles. Repository policy therefore permits `strong-evidence`, not
`confirmed`, for conclusions based solely on this retained file.

## Structured data

The validated batch created:

- `P-0012` — Deocleciano Muniz Bittencourt;
- `P-0013` — Luiza Fernandes de Azevedo;
- `F-0001` — their spouse relationship;
- `E-0001` — their 21 October 1916 marriage;
- `PL-0001` — Carangola, Minas Gerais, Brazil; and
- `SRC-0001` — the certified marriage record.

No children or parents were created as entities because this first record
requires only the two spouses, their relationship, the marriage event and its
place. The four parents remain source-text assertions until a later
source-linked entity batch requires them.

## Engineering finding

The first live promotion revealed that `scripts/new_entity.py` did not pass the
repository schema directory into its temporary prospective validation when
called through the normal command-line path. The defect was fixed by resolving
the default schema directory before staging, and a regression test now covers
that path.

## Next action

Recover and catalogue two additional original records from FamilySearch
Memories, prioritising the clearest marriage and death registrations. After the
third record, review the entity and inventory schemas against real evidence
before wider ingestion.
