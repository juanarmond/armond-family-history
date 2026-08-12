# 2026-08-12 — Muniz collateral children: 11 Mãe de Deus records as documented_children

## Context

The retrieval agent synced a new drop (2026-08-12) with 11 new Nossa Senhora Mãe de
Deus (Povoação, São Miguel) register images — siblings of the modelled Manoel Muniz
Bytancourt (P-0042), daughters of Manoel × Francisca (siblings of the emigrant João
P-0019), and a sister of João Francisco (P-0048). Owner approved the full batch.

Value-gated by three parallel subagents over disjoint image sets (PAR-0038–0041,
0042–0044, 0045–0048); each read its images, transcribed verbatim, verified the parents
named against the expected couple, wrote the source record, and copied the scan. The
main agent verified sha256/dims/links, then did all family, inventory, validation and
commit work centrally. Per the collateral rule these are `documented_children`, not
person entities — so no new person entities and no events.

## Promotions (11 new sources; all PRIMARY Culturaçores CDN parish images)

- **F-0023** (João Francisco Muniz Bitancourt P-0048 × Maria Jacintha de Medeiros P-0049)
  — 7 siblings of Manoel (P-0042): a son of illegible given name (b.1831, **PAR-0038**),
  Michaelina (1833, **PAR-0039**), Rosa (1834, **PAR-0040**; mother written "de Silveiros",
  a scribal variant), Damaso (1836, **PAR-0041**), Francisco (1839, **PAR-0042**), **José
  (1841, PAR-0043)**, Agostinho (1843, **PAR-0044**).
- **F-0020** (Manoel Muniz Bytancourt P-0042 × Francisca Roza P-0047) — 3 daughters,
  sisters of the emigrant João (P-0019): Maria (1842, **PAR-0045**), Francisca (1849,
  **PAR-0046**), Maria (1851, **PAR-0047** — a distinct within-sibship namesake of the 1842
  Maria).
- **F-0040** (Manoel Muniz elder P-0082 × Tereza do Amaral P-0083) — **Maria Jacintha de
  Medeiros ⚭ Manoel Cabral** (m. 1818, **PAR-0048**), a sister of P-0048.

## Findings / adjudications

- **The "José brother" question is settled** (PAR-0043): the couple did have a son José
  (b. 23 May 1841). He is a *candidate* for the José who emigrated with João to Sapucaia,
  but this baptism does not prove that identity — recorded as a hypothesis, not fact.
- **Namesake trap resolved** (PAR-0048): the 1818 bride "Maria Jacintha de Medeiros" is a
  *distinct* namesake of the spine ancestor P-0049 — her parents are Manoel Muniz elder ×
  Tereza do Amaral (F-0040), not P-0049's parents (João de Medeiros Brandão × Maria
  Eugenia). Never merge.
- **Grandparent corroboration:** PAR-0044 (Agostinho's 1843 baptism) independently names
  both grandparent couples — added as a second source on F-0040 and F-0041, which
  previously rested only on the 1819 marriage (PAR-0037).
- **P-0047 name variant** "Francisca Roza de Pimentel" (PAR-0046) recorded.
- Uncertain readings preserved verbatim and bracketed (PAR-0038 given name illegible;
  PAR-0040 "de Silveiros"; PAR-0043 godfather surname); book-range codes left generic
  where the folio sequence was ambiguous.

## Outcome

`make check` green (315 entities, 69 tests + 24 JS). All 11 sources inventoried
(DOC-0079–0089), cited by their families, and their `documented_children` resolve. Index
+ GEDCOM (4040 lines) regenerated. Committed.

## Not done (flagged)

- Two further known siblings of Manoel (João b.~1823, Maria b.1825) have held images from
  an earlier drop but were not in this batch — a small follow-up to complete F-0023's
  sibship if wanted.
- The queued newspaper searches (Aristão 1957 "Armand"; Simplício 1875–1913) still need
  the owner's live CAPTCHA-present Hemeroteca session.
