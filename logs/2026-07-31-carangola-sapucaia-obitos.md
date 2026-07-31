# 2026-07-31 — Carangola/Sapucaia óbitos: João's São Miguel origin + the maternal Brandão/Machado lines

## Question

A new `research/from-retrieval/` sync added the Sapucaia (RJ) and Santa Luzia de
Carangola (MG) **death registers** (44 new `rec-*` images). Which are new and
valuable, and what do they establish for the Muniz Bittencourt / Brandão lines?

## Method

Oriented on the fresh FINDINGS §9 (rewritten 18:44) + the triage ledger, diffed the
drop (44 untriaged), then value-gated: I read the **five load-bearing death records
myself** (confirmed against the images) and fanned the collateral/lead cluster to
**three parallel read-only classifier subagents** (disjoint sets). All subagent reads
are leads; every promoted fact was confirmed on the image.

## Promoted (one batch; 5 óbito sources, 5 ancestors, 3 families, 5 death events)

- **PAR-0007 — João Muniz Bittencourt's 1915 Carangola death** (P-0019): "natural da
  Ilha de São Miguel" (Açores, Portugal), †12 Sep 1915, age 68 (b.~1847), ⚭ Suzana
  Rita Brandão, 11 children, **filho legitimo de Manoel Luiz Bittencourt**. →
  **RESOLVES material conflict 6**: João was himself the Azorean immigrant (nationality
  set to Portuguese), which explains the Sapucaia 1856-77 "born-abroad" negative. Adds
  his father **Manoel Luiz Bittencourt (P-0042)**, family F-0020, death event E-0036.
- **PAR-0008 — José do Rego Brandão's 1912 Carangola death** (P-0040): †3 Oct 1912,
  age 79 (b.~1833), brasileiro, widower of Rita; **filho de José do Rego Brandão [o
  velho] e de Maria de Mendonça**. → adds his parents **P-0043 + P-0044**, family
  F-0021, event E-0037; nationality Brazilian.
- **PAR-0009 — Rita do Rego Brandão's 1898 Carangola death** (P-0041): †4 Jan 1898,
  age 51 (b.~1847), wife of José do Rego Brandão. → her death event E-0038 (a namesake
  1906 "Rita Brandão", wife of João de Souza Freitas, is a different woman).
- **PAR-0010 — Antonio Caetano Machado's 1868 Sapucaia death** (P-0045): married, age
  70 (b.~1798). → **resolves the flagged "Antonio [Castro/Caetano] Machado" reading to
  Caetano**; he is Rita's father (P-0041's, per Susanna's baptism avô-materno), event
  E-0039.
- **PAR-0011 — Ignacia Maria de Jesus's 1878 Sapucaia death** (P-0046): "viuva de
  Antonio Caetano Machado", age 65 (b.~1813). → adds Rita's probable mother (name
  pattern Rita **Ignacia** ← **Ignacia** Maria de Jesus); couple F-0022; event E-0040.

## Leads recorded (not minted)

- **Damazio Muniz Bitencourt** (†1881 Sapucaia, "natural da Ilha de São Miguel", ~40)
  — probable brother of João (P-0019 coverage/STATUS).
- **Infant Maria d'Azevedo** (1913 Carangola, "filha de José [Secundino] d'Azevedo",
  mother unnamed) — corroborates P-0038's Carangola residence; a lead on P-0038.
- **"José Armond"** parenting a child in Carangola 1913 — a rare-surname lead with no
  modelled match (triage ledger).
- **Lino Caetano Machado** (1869), a distinct-family Sapucaia Muniz cluster (1856-69),
  the "da Silva Brandão" and Antônio Firmino Bittencourt namesakes — collateral/namesake
  (triage ledger).

## Result

`uv run --frozen make check` green (69 tests; **173 entities**, up from 155);
reciprocity audit 0 issues. STATUS conflict 6 resolved; snapshot, coverage
(P-0019/P-0040/P-0041 + the five new ancestors) and the triage ledger updated. New
evidence DOC-0038–0042.
