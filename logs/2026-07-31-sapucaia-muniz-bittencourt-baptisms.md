# 2026-07-31 — Sapucaia Muniz Bittencourt baptisms (retrieval drop value-gate)

## Question

A new `research/from-retrieval/` sync added a ~25-image **Santo Antônio de Sapucaia
(RJ) parish-register cluster** (from the Familiaridade online gallery of the
Sapucaia books) for the Muniz Bittencourt line. Which are new and valuable, and
what do they establish?

## Method

Oriented first (FINDINGS.md + the triage ledger + the descriptive `rec-*` list):
everything except the Sapucaia cluster was already dispositioned (CIV-0002/03/04/06/
16–23, PAR-0001/02/03, photos, namesakes). Dispatched **3 parallel read-only
classification subagents** over the collateral cluster (José-Muniz children;
other-couple baptisms; marriages) and read the **two direct-ancestor vitals**
myself; verified every promoted source against the image (agents' reads are leads).

## Promoted (one batch)

- **PAR-0004 — Deocleciano's own 1892 baptism** (Sapucaia, fl. 314): baptized 25
  Jun 1892, *filho legítimo de João Muniz Bitencourt e Suzana Rita Brandão*. His
  earliest vital record → **upgraded his parentage (F-0007) to confirmed** and
  **settled the father's name as "João"** (the 1882 provisão's "José" was the
  error). Event E-0034.
- **PAR-0005 — Susanna (Suzana) Rita Brandão's 1866 baptism** (1882 register
  transcript): born 11 Aug 1865, *filha legítima de José do Rego Brandão e de Rita
  Ignacia de Jesus*; padrinho Antonio Castro Machado, *avô materno*. → **new direct
  ancestors P-0040 (José do Rego Brandão) + P-0041 (Rita Ignacia de Jesus) and
  family F-0019**; settles Susanna's parentage over the "Manoel Soares Brandão"
  lead. Event E-0035.
- **PAR-0006 — Anna's 1885 baptism**: *filha legítima de João Muniz Betencourt e
  Suzana Rita Brandão*, godparents José do Rego Brandão + Rita Ignacia de Jesus. →
  **Anna Muniz Bittencourt is a confirmed sibling of Deocleciano**, recorded as a
  `documented_children` on F-0007 (very likely the "Ana ⚭ dos Santos Ferreira"
  1908 lead). Her godparents = Susanna's parents, corroborating F-0019.

## Leads recorded (not promoted)

- **Collateral Muniz Bittencourt sibling-cluster** of Sapucaia/Bemposta (Manoel,
  Maria José, Altina, Maria Eugenia, Elvira Muniz Bittencourt) — likely Deocleciano's
  aunts/uncles; the path to João's parents, but no record names them (P-0019 coverage).
- A separate **José Muniz Bettencourt ⚭ Anna Barbara de Jesus** couple (José
  *Portuguese*; 6 Sapucaia baptisms) — distinct collateral line, not modelled.
- A non-Muniz **"Antônio Firmino Bittencourt ⚭ Anna Maria Bittencourt"** family of
  Bemposta — namesake caution.
- **Antonio Castro Machado** = Rita Ignacia de Jesus's father (a note on P-0041).

## Result

`uv run --frozen make check` green (69 tests; **155 entities**, up from 147);
reciprocity verified (E-0034/E-0035 ↔ participants; F-0019 ↔ P-0040/P-0041/P-0020;
PAR↔event). New evidence: DOC-0035/0036/0037. STATUS/coverage updated.
