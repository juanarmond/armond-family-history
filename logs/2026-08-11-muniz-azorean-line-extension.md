# 2026-08-11 — Muniz Bittencourt Azorean line: +1 generation and a marriage-record correction

## Context

Processing the 11 August retrieval drop (BPARPD Ponta Delgada reply SE/2026/1583e,
reconciled by the retrieval agent against the free Culturacores CDN register images).
This assistant value-gated the drop and verified every promoted fact against the
actual register images before cataloguing.

## Records verified from the images

1. **SMG-PV-MAEDEDEUS-C-1841-1854, folio 32r — 17 February 1842.** Marriage of
   **Manoel Muniz Bitancourt (P-0042) × Francisca Roza do Espírito Santo (P-0047)**,
   dispensed from a 4th-degree consanguinity impediment. Legibly names the groom's
   parents **João Muniz Bitancourt × Maria Euginia[/Jacintha] de Medeiros** (= F-0023)
   and the bride's parents **Manoel de Motta [var. Mello] mancebo × Anna de Souza**.
2. **SMG-PV-MAEDEDEUS-C-1801-1822, folio 161v — 7 October 1819** (scribe corrected
   "Setembro"→"Outubro"). Marriage of **João Francisco Muniz Bitancourt (P-0048) ×
   Maria Jacintha de Medeiros (P-0049)**, naming the groom's parents **Manoel Muniz
   Bitancourt × Tereza do Amaral (já defunta)** and the bride's parents **João de
   Medeiros Brandão × Maria Eugenia**.
3. **Folio 73r** (the image previously bound to PAR-0024): re-read on the CDN as a
   **different couple** — a late-1845 "Manoel × Roza de Jesus" whose groom's father is
   "António". This was a namesake mis-identification.

## Correction

- **PAR-0024** was re-pointed from the mis-identified folio 73r (dated 1 Feb 1845,
  parents illegible under a watermark) to the true **folio 32r, 17 Feb 1842**. Event
  **E-0053** date corrected 1845-02-01 → 1842-02-17. The two folio-73r scans were
  removed from `evidence/parish/` (a different family). The superseded reading is
  preserved in PAR-0024's notes, E-0053's note, F-0020's note and P-0042's profile.

## Promotions (all PRIMARY, direct maternal line of P-0001)

- **PAR-0037** (new source) — the 1819 grandparents' marriage.
- **E-0074** (new event) — the 1819 marriage of P-0048 × P-0049; F-0023 now has a
  direct marriage record (was only inferred from a "filho legitimo" statement).
- **New people:** Manoel Muniz Bitancourt the elder (**P-0082**) × Tereza do Amaral
  (**P-0083**) = **F-0040**, parents of P-0048; João de Medeiros Brandão (**P-0084**) ×
  Maria Eugenia (**P-0085**) = **F-0041**, parents of P-0049; Manoel de Motta [var.
  Mello] (**P-0086**) × Anna de Souza (**P-0087**) = **F-0042**, parents of P-0047.
- **P-0048** gains the fuller forename "João Francisco Muniz Bitancourt" (PAR-0037),
  his parents (F-0040) and his marriage (E-0074). **P-0049** gains her parents (F-0041)
  and marriage. **P-0047** gains her parents (F-0042), upgrading her earlier "parents
  [LEAD]" to [PROVEN]. **F-0023** gains PAR-0037 + E-0074.

## Adjudications carried from the BPARPD reconcile (verified consistent with the images)

- **Jacintha vs Eugenia (P-0049):** same woman. "Jacintha" in 5 acts (1819 marriage,
  1821/1823/1825 baptisms, 1845 twins); "Eugenia" only in the 1841/1842 acts, where the
  scribe wrote the *mother's* name (Maria Eugenia = P-0085). The 1819 marriage is the
  resolver.
- **Motta vs Mello (P-0086):** "Motta" adopted as primary (1842 marriage + an 1847
  collateral) over "Mello" (1845 twins' baptism); variant preserved.

## Outcome

`uv run --frozen make check` green (302 entities, 69 tests). Reciprocity verified for
all new links. Index + GEDCOM regenerated. Committed.

## Open / next

- Anna de Souza's (P-0087) devotional-surname certainty and the 1847 collateral
  paternal-grandmother reading remain [VERIFY] items in the retrieval agent's receipt
  (not blocking).
- The line's next reachable step above (P-0082–P-0087) needs the pre-1818 Mãe de Deus
  books, which are not digitised online.
