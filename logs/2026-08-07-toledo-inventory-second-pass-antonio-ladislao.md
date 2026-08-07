# Research log: Toledo inventário second pass + António Ladislão death + Lemos siblings

**Date:** 2026-08-07 (second session this date)
**Researcher:** Claude Code (AI assistant, value-gate operator)
**Session type:** Discovery summary — retrieval drop value-gate continuation

---

## 1. PRB-0008 p5 read: JC's death date confirmed

The previously unread PRB-0008 page 5 ("Termo de juramento e declaração de inventariante",
7 March 1867) was read by the retrieval agent and confirmed by this session. Claudina
Brandina de Jesus appeared in person as inventariante, swearing "seu marido fallecera
no dia dois de Setembro" (her husband died on the 2nd of September).

**Result:** E-0054 updated from `kind: before, text: 1867-03-04` to `kind: exact, value:
1866-09-02`. The year 1866 is contextually inferred (page 6, which would contain the
year, was not catalogued). PRB-0008 transcription updated with p5 content.

**Correction:** P-0055 (Claudina) notes previously stated she "died before 4 March 1867"
— this was wrong. Claudina was physically present and taking the oath on 7 March 1867.
She died after 7 March 1867 and before 1879 (PRB-0006). P-0055 corrected.

**Secondary correction:** The PRB-0009-p2 text "é viúva, cuja [morte] falleceu depois
do Inventariado" was misread in the previous session. Correct reading: "JC (Claudina's
husband) died after Ladisláo" — a statement about JC's death ORDER, not about Claudina
being deceased. PRB-0009 abstract and notes corrected.

## 2. PRB-0009 pp 3-5 read: new leads, Eliza not mentioned

Pages 3–5 of Ladisláo's inventário were read in detail:

- **p3 — herdeiros citation list:** Names adult heirs summoned. New lead:
  "Marciano Cesário José de Toledo" — unrecognised adult heir with "Cesário" in the
  name; possibly an adult son of José Cezário de Toledo Lima (P-0054) not yet in the
  repository. Requires further investigation.
- **p4 — citation list + Termo de Louvaçao (10 March 1867):** Simplício Jaci Ferreira
  de Toledo (P-0016) is identified as **curator of orphaned minors** in Ladisláo's
  estate. This supports the hypothesis that Francisco Leocádio (P-0061), who predeceased
  Ladisláo, left minor children whose shares Simplício manages.
- **p5 — Termo de Louvaçao signatures:** Mathilde Maria de Jesus (P-0027) signed in
  person at the 10 March 1867 proceedings — confirming she was alive in March 1867.
  "Umbilina de Toledo" appears in the proxy signatures (signed by Narciso Marques Braz)
  — a distinct person from Eliza Balbina de Toledo (P-0017).

**Critical negative:** Eliza Balbina de Toledo is NOT mentioned anywhere in PRB-0009
pp 3–5. Francisco Leocádio's children are not individually named in these pages.

PRB-0009 transcription, abstract, limitations and notes all updated.

## 3. JC's 1813 baptism image: illegible (PAR-0025 not created)

The image `rec-toledo-jose-cesario-baptism-1813-sjdrei.jpg` (São João del Rei baptism
register, March 1813, folio 54) was read but found too illegible at the delivered
resolution (dense 19th-century cursive + ink bleed-through) to confirm the child's name,
parents, or parish. Pre-allocated IDs PAR-0025 and E-0055 remain unused (retired in
id-ledger). A higher-resolution scan or in-person reading is required.

## 4. António Ladislão de Toledo (P-0063): civil death catalogued

CIV-0024 (two-page certidão, 1909, Thebes/Leopoldina) was read and promoted. Key facts:
- Death: 11 February 1909 at 9pm (not 12th as FINDINGS.md had it — declarant said
  "hontem", i.e. yesterday), Fazenda da Concórdia, Thebes district, Leopoldina MG.
- Condition: cor branca, carpinteiro, ~70 years (estimated), viúvo de Maria Euphronyza
  de Jesus.
- Father: "Ladislao Igidio Ferreira de Toledo" = P-0056. ✓
- Mother: "Mathilde Luiza de Toledo" — new name variant for P-0027 (Mathilde Maria de
  Jesus); a non-family informant's simplification. Added to P-0027 name_variants.
- Four adult children named (Francisco Themotheo, José Ladislao, Amélia, Mathilde
  solteira) — not modelled as entities.

António Ladislão was previously a documented_child in F-0027 (noted as "surdo e mudo").
Promoted to person entity P-0063. F-0027 updated: removed from documented_children,
added to structured children. E-0058 created for the death event. DOC-0060 created.

The 1839 Bonfim census image (page 1) shows a child "Antonio ~5" in what appears to be
Ladisláo's household, consistent with António Ladislão born c.1834 — making him ~74–75
at death, slightly older than the informant's estimate of ~70.

## 5. Lemos siblings (F-0025): four baptisms read-confirmed

Four Itaborahy baptism images were read by the retrieval agent (parents confirmed in each):
- Maria: baptized 14 July 1832
- Anna: baptized 11 February 1834
- Thomaz de Lemos Pereira: baptized June 1836
- Polidoro: baptized c.15 March 1838

All confirm parents Manoel de Lemos Pereira × Maria Thereza de Jesus (F-0025). Added as
documented_children on F-0025. Individual source cataloguing pending (images held in
research/from-retrieval/output/images/).

## 6. Francisco Leocádio (P-0061) added to F-0027 structured children

P-0061 was previously a documented_child entry in F-0027 (note said "now modelled as
P-0061") — this was a consistency error. Corrected: P-0061 added to F-0027 structured
children list; documented_children entry removed.

## 7. Toledo direct ancestors added to record-coverage.yaml

Entries added for P-0054 (JC), P-0055 (Claudina), P-0027 (Mathilde), P-0056 (Ladisláo),
P-0057 (João José), P-0058 (Ritta Angélica), P-0059 (Alferes Amaro), P-0060 (Ignez
Francisca) — all direct ancestors not previously in the ledger. JC's baptism recorded
as `negative_search` (image illegible at delivered resolution).

---

## Entity changes this session

| Entity | Change |
|---|---|
| E-0054 | Date updated: before 1867-03-04 → exact 1866-09-02 (year inferred) |
| P-0055 | Note corrected: alive 7 March 1867 (was: deceased before 4 March 1867) |
| PRB-0008 | Transcription updated with p5 (Claudina's oath, death date) |
| PRB-0009 | Transcription updated with pp 3–5; abstract/notes corrected |
| P-0027 | Name variant added: "Mathilde Luiza de Toledo" (CIV-0024) |
| P-0027 | Note added: alive March 1867 (PRB-0009 p5 signature) |
| F-0027 | P-0061 and P-0063 added to structured children; documented_children updated |
| P-0063 | NEW: António Ladislão de Toledo (child #7 of Ladisláo × Mathilde) |
| CIV-0024 | NEW: 1909 death certidão for P-0063 |
| E-0058 | NEW: Death event for P-0063 |
| F-0025 | Four Lemos siblings added as documented_children |
| record-coverage.yaml | Toledo direct ancestors P-0054 through P-0060 and P-0027 added |
| id-ledger.yaml | E-0055/E-0056/E-0057 retired (pre-allocated but never used) |

## Open leads

- "Marciano Cesário José de Toledo" in PRB-0009 p3 — unrecognised adult heir, possibly JC's son
- "Umbilina de Toledo" in PRB-0009 p5 — distinct person, possibly Ladisláo's heir
- António Ladislão de Toledo's probable birth year c.1834 (not ~1839) per 1839 census
- JC's 1813 baptism: image held, too illegible — needs higher resolution
- Lemos sibling baptisms: images read, individual source cataloguing pending
- Eliza Balbina's parentage: NOT resolved by PRB-0009 pp 3–5
