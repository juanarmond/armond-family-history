# 2026-07-31 — Carangola parish marriages: Deocleciano's religious marriage + two sisters

## Question

A new `research/from-retrieval/` sync added 4 images — the Santa Luzia de Carangola
**parish (religious) marriage** cluster of 1916-1918. Which are valuable to the direct
line?

## Read and ingested (all confirmed against the images)

- **PAR-0012 — Deocleciano Muniz Bittencourt ⚭ Luiza Fernandes de Azevedo** (acto nº 35,
  21 Oct 1916): the religious counterpart of the civil 1916 marriage (CIV-0001, same
  date) → added as a source on event E-0001. It **primary-confirms Luiza's parents**
  (Secundino Maria de Azevedo P-0038 + Thereza Fernandes de Azevedo P-0039) and
  **RESOLVES material conflict 12** — her father is Secundino (Maria) de Azevedo, so the
  2019 civil inteiro-teor's "Sebastião" (CIV-0006) was a misread. Records the
  birthplaces: Deocleciano born/baptized Sapucaia (RJ), Luiza born/baptized Bom Jesus de
  Cachoeira Alegre (São Paulo do Muriaé, MG; her birth E-0033).
- **PAR-0013 — Joventina Muniz Bittencourt ⚭ Nestor Lopes Barbosa** (acto nº 34, 21 Oct
  1916) and **PAR-0014 — Mercedes Maria Bittencourt ⚭ João Monteiro de Azevedo** (acto nº
  23, 10 Sep 1917): both name the bride as a legitimate daughter of João Muniz
  Bittencourt (P-0019) and Suzana Rita Brandão (P-0020) → two more **sisters of
  Deocleciano**, added as documented children on F-0007. Both were born (~1898-1899) and
  baptized in Carangola — dating the family's move from Sapucaia (RJ) to Carangola (MG)
  to between Deocleciano's 1892 Sapucaia birth and ~1898.

## Leads recorded (not minted)

- **Isaltino Linhares de Mendonça ⚭ Maria Clelia Migliori** (1918) — the groom is a son
  of the collateral Maria José (Muniz) Bittencourt ⚭ José Linhares de Mendonça branch
  (witness Manoel Muniz Bittencourt); a cousin-level collateral, not a direct sibling.

## Result

`uv run --frozen make check` green (69 tests; **182 entities**, up from 179);
reciprocity audit 0 issues. STATUS conflict 12 resolved; snapshot and F-0007/P-0038/
P-0039/P-0013 updated. New evidence DOC-0043–0045.
