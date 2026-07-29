# FamilySearch Geraldo Paz Armond death-record ingestion

## Date

28 July 2026

## Research question

Can Geraldo Paz Armond's original 1991 civil death registration be located in
the authorised FamilySearch account, preserved with complete archival
provenance, and used to document his death and reported parentage without
relying on the collaborative tree?

## Profiles and path inspected

- Geraldo Paz Armond: FamilySearch profile `GQJ1-RVK`.
- Access path: Geraldo's Sources and Memories tabs, the indexed record page and
  the authenticated original-image viewer.
- Access date: 28 July 2026.

Profile conclusions and collaborative-tree values were not used as evidence.

## Search path and results

1. Geraldo's Sources tab contained one formal source titled `Geraldo Paz
   Armand, “Brasil, Rio de Janeiro, Registro Civil, 1804-2013”`.
2. The indexed record is FamilySearch ARK `1:1:77DD-TX6Z`. Its original image
   is ARK `3:1:S3HT-DYSS-YKV`, image group `#004366687`, image 300 of 324 in
   `Registros de óbito: Volta Redonda, September 1990–March 1991`.
3. The original page was inspected in the authenticated viewer. The storage
   identifier is `TH-266-11612-78888-32`, and the entry appears on page 557.
4. The viewer's controlled JPG download dialog was exercised, but no
   downloadable file was exposed to the Codex browser. This negative result is
   retained so the same failed path is not repeated without a browser change.
5. Geraldo's Memories gallery contained the identical page as a Memory titled
   `Certidao de obito`, uploaded on 24 February 2020 as `record-image_.jpg`;
   storage identifier `TH-904-96969-238-86`.
6. All twenty level-11 Deep Zoom tiles for that Memory were exported. Their
   one-pixel overlaps were removed and the decoded pixels stitched into a
   1196×868 PNG. No crop, enhancement, transcription overlay or content change
   was applied.

## Retained file

- Inventory: `DOC-0003`.
- Source: `CIV-0003`.
- Path:
  `evidence/civil/CIV-0003-death-geraldo-paz-armond-1991-reconstructed.png`.
- SHA-256:
  `f0b8db131c7aa448e711ef6c5222d80deedbd0506801830d52e751c165bdc7e3`.
- Rights: private research.
- Privacy review: cleared for this private repository.
- Sensitive content: address, signature, medical information and an unrelated
  person's death entry on the same page.
- Public-export rule: exclude the image.

## Transcription findings

The legible core of the right-hand register entry states:

- Geraldo Paz Armond died on 18 February 1991;
- death occurred at Hospital Santa Margarida;
- he was male, recorded as white, aged 76 and natural of Minas Gerais;
- he was married to Cidalia Engracio Armond and was retired;
- his parents were reported as Aristão Ferreira Armond and Liliosa Paz Armond;
  and
- the observations report no will, property requiring inventory and five
  children.

The declarant, complete address, cause, burial text and some surrounding
handwriting are not transcribed because they are not safely legible from the
retained image.

## Record-number conflict

The FamilySearch index reports certificate number `39006`. The handwritten
number on the image appears to read `39005`. The source record preserves both
readings and does not resolve the conflict by convenience.

## Evidence assessment

The original register entry provides direct evidence of Geraldo's death, its
date and location. His spouse and parents are secondary information supplied
at death, but they are directly stated in the record. The death event is
`confirmed`; the reported parent-child relationships are `strong-evidence`
pending vital or marriage records closer to those relationships.

The record establishes joint reported parentage of Geraldo. It does not prove
that Aristão and Liliosa married, so no marriage event is created for them.

## Structured data

The validated batch prepares:

- `P-0008` — Aristão Ferreira Armond;
- `P-0009` — Liliosa Paz Armond;
- `F-0003` — the family group containing their reported parentage of Geraldo;
- `E-0003` — Geraldo's death;
- `PL-0003` — Volta Redonda, Rio de Janeiro, Brazil; and
- `CIV-0003` — the original civil death register entry.

The existing `P-0004` and `P-0005` records are linked to the death event. No
birth, marriage or parentage conclusion beyond what this record directly
reports is added.

## Next action

Review the entity and inventory model against the completed three-document
sample before wider FamilySearch ingestion. In particular, determine whether a
family group can represent two reported parents without implying a partner
relationship.
