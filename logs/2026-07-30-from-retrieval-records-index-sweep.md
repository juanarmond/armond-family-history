# 2026-07-30 — retrieval drop: Records-index sweep + new Amaro image (value gate)

## Objective

Value-gate the 2026-07-30 retrieval-agent re-sync of `research/from-retrieval/`:
find what is new since the prior read pass, read/classify each item, promote the
valuable, and record leads and negatives. The re-sync followed the expanded
`people.txt` roster (the maternal/other lines added earlier on 2026-07-30).

## What was new

- **New manifests:** `output/records_candidates.csv` / `records.json` — the
  FamilySearch Records/personas index mode — plus an expanded Full-Text set.
- **One new image:** `ft_3-1-3QHV-L3VN-5KKJ.jpg`.
- Every other image in `output/images/` was already dispositioned in the prior
  read pass (tracked in the from-retrieval triage ledger).

## Findings

### New image — read, NOT ingested (titled/collateral)

`3:1:3QHV-L3VN-5KKJ` is another page of **Dr. Amaro Ferreira das Neves Armond's**
1944 Rio estate: the óbito certidão (livro 39 de óbitos, fl. 81, nº 3.177) —
Amaro, médico, natural do Espírito Santo, 91, solteiro, *filho de Manoel Ferreira
das Neves e Rosa Maria da Conceição Neves*, d. 7 March 1944 at the Santa Casa da
Misericórdia, Rio; buried São João Batista; left a will. Same titled/collateral
Neves-Armond branch (Espírito Santo / Rio) already read in the prior pass — a
genuine Ferreira Armond, but with no established link to the owner's Zona da Mata
line. Not ingested; the owner decision on the titled branch is still pending.

### Records-index sweep of the roster — one lead, otherwise negative

The agent ran the FS Records (personas) index over all 18 active roster names.

- **Geraldo Paz Armond (P-0004) — real hit / lead:** ARK **77DD-TX6Z**, a 1915
  Rio de Janeiro civil **birth** entry, parents **Aristão Ferreira Armond** and
  **Liliosa Paz Armond**, spouse **Cidalia Engracio**. Index-only (no image). It
  matches P-0004; his marriage (CIV-0002, 1952) and death (CIV-0003, 1991)
  already document the same parentage. Recorded as a birth lead on P-0004; no new
  entity or source was created from index data.
- **The other 17 names — negative (namesakes only):** Antenor Muniz, Antonio
  Engracio Filho, Antonio Francisco da Silva, Cidalia Engracio Guimarães,
  Deocleciano Muniz Bittencourt, Emmerenciana Maria de Jesus, Francisco José de
  Carvalho Guimarães, Iris Bohrer Muniz, João Gonçalves Bohrer, João Muniz
  Bittencourt, Luiza Fernandes de Azevedo, Maria Amora Guimarães, Maria Paula de
  Jesus, Maria Tertuliana da Conceição, Selina Bohrer, Susanna Rita Brandão,
  Vicente José de Carvalho Guimarães. Every returned row is an unrelated person
  (Paraná / São Paulo / RJ / US civil or Find-a-Grave indexes, with different
  parents, places and dates).

## Disposition and conclusions

- No new evidence and no new entities: the one image is collateral (not ours);
  the Geraldo hit is an index lead for an already-documented person; the rest are
  namesakes.
- **Soft negative, not proof of absence:** a Records-index miss does not prove
  these records do not exist. Per policy, unindexed parish/civil registers are
  not covered by the personas index. The maternal/other lines (Muniz Bittencourt,
  Engracio/Guimarães, Bohrer, Azevedo) must be pursued in **unindexed registers /
  local archives**, not the FS Records index, which is now exhausted for them.
- Because the negative is a soft index-miss spread across many people, it is
  recorded here (research history) rather than as 17 near-identical per-person
  coverage rows; only the Geraldo birth lead was added to
  `data/record-coverage.yaml` (P-0004).

## Next action

- Retrieve the Geraldo Paz Armond 1915 RJ civil birth image (77DD-TX6Z) when
  convenient — the earliest primary record of his filiation.
- Take the maternal/other lines off-tool: local civil registries and parishes,
  not the FS Records index.
- The 18 searched names were moved to DONE ([Records]) in `people.txt` so re-runs
  skip them; re-enable only to catch newly-indexed records.
