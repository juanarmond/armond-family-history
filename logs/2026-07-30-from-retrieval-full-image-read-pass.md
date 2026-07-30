# 2026-07-30 — from-retrieval drop: full per-image read pass

## Objective

Honestly complete the value-gate on the `research/from-retrieval/` FamilySearch
retrieval drop: open and read **every** pulled image (not classify by CSV
metadata), transcribe the genuinely direct-line records, catalogue new
maternal-line evidence into `data/` + `evidence/`, and record the disposition of
every image so nothing is re-read. Scope set by the owner: direct line first,
then "make sure all the finds are fully analysed, transcribed, stored and linked".

## Method

Read each `output/images/ft_3-1-*.jpg` individually. Cross-read the Toledo
Concórdia deeds against the already-catalogued PRB-0001/0002/0003. Classified
each image as direct-line/maternal-Toledo, titled-branch collateral, namesake,
privacy-excluded, or negative-proof. Full disposition table kept in the
(gitignored) `research/from-retrieval-triage-ledger.md`.

## Findings

### Direct line — catalogued
- **PRB-0004** (ARK 3:1:3QHJ-1QWB-7BYX): a Toledo notarial sale continuation
  folio (Fazenda da Concórdia / Ribeirão de São Bento, Leopoldina) stating the
  grantor grandchildren inherited from *"seus finados avós Dona Mathilde Maria de
  Jesus e Ladisláo Egydio Ferreira de Toledo e seus paes e sogros Antonio Zeferino
  de Toledo e Dona Maria Perpétua"*. This names, for the first time, Mathilde's
  husband (Ladisláo Egydio Ferreira de Toledo) and a parent couple below them
  (Antonio Zeferino de Toledo × Maria Perpétua). Linked to P-0027; image stored at
  `evidence/probate/PRB-0004-toledo-deed-sao-bento-concordia-leopoldina-page-01.jpg`;
  inventory DOC-0021.

### Direct line — hypothesis raised (no edge created)
- Cross-reading PRB-0004 with PRB-0001 (which lists Eliza + siblings Maria
  Bulandina, Ladisláo Egydio, Geraldo Augusto, Josepha Olympia as Mathilde's
  grandchild-heirs) makes **Antonio Zeferino de Toledo × Maria Perpétua a strong
  candidate for Eliza's (P-0017) own parents** — the long-missing intervening
  generation. Recorded as a hypothesis with an explicit next action; not modelled
  as a parent-child edge pending confirmation.

### Direct line — conflict flagged
- PRB-0003 (1877) has a **living** grantor "Ladisláo Egydio Ferreira de Toledo",
  while PRB-0004 and `BQW1-FS9G-R` treat "Ladisláo Egydio Ferreira de Toledo" as a
  **deceased grandfather**. Most likely an elder/grandson name-pair; must be
  resolved from the full Concórdia inventory before any Toledo ancestor entities
  are created.

### Maternal-Toledo — read, deferred (not catalogued)
- `BQW1-FS9G-R`: Leopoldina Juiz de Órfãos *mandado* in the estate of the deceased
  Ladisláo Egydio Ferreira de Toledo (widow D. Ignez Umbelina de Toledo; heir set
  incl. Geraldo Augusto Toledo Simões, Marianna Claudina, Carolina Baldoina,
  Josepina Cherubina, Amélia Balbina). Not catalogued: names no existing entity
  and depends on the unresolved two-Ladisláo identity.

### Titled branch — read, NOT ingested (collateral, connection unproven)
- ~25 images are the Ferreira Armond noble circle: **Barão / Baroneza de Pitangui**
  (Honorio, Marciano, Clotilde, Leonor, Alice, Maria Antonietta, Henriqueta,
  Godofredo, Abelard, Adalberto, Henrique, Maria José Ferreira Armond; Mar de
  Espanha / Rio / Penha Longa, 1876–1893), the **Baroneza de Juiz de Fora /
  Fonseca-Armond** matter, and the **1944–45 estate of Dr. Amaro Ferreira das Neves
  Armond** (Rio). Genuine Armonds but collateral; no record connects them to the
  owner's own line, so none were promoted. See the "Decision pending" note.

### Namesake / privacy / negative — recorded, not ingested
- Namesake traps: a Uruguayan Toledo civil register (CS24-SQP5-V); a Rio dairy
  account of "Manoel Ferreira Armond" (D3CD-Q9VQ-V); and critically a **different
  "Mathilde Maria de Jesus"**, widow of Generoso Fernandes de Moura (QQ2X-VS4Y) —
  explicitly flagged in P-0027 as a do-not-conflate.
- Privacy-excluded (20th-c., possibly-living): a 1947 police *prontuário* (Denise
  Armond Ferreira Ribeiro) and a 1980 infant death (Daniel de Almeida Armond
  Ferreira). Not ingested.

## Decision pending (for the owner)

Whether to build a **documented collateral Ferreira Armond branch** (Barão de
Pitangui / Amaro) as entities + sources, or leave it as read-and-recorded context.
Ingesting it means creating a sizeable noble sub-tree whose link to the owner's own
Armond line is not yet evidenced — which the current scope ("direct line") and the
evidence gates argue against without a connecting record.

## Repository changes

- Catalogued PRB-0004 (+ evidence image, DOC-0021).
- Updated P-0027 (husband + parent couple documented; two-Ladisláo conflict;
  Moura namesake caution) and P-0017 record-coverage (parents hypothesis + next
  action).
- Gitignored the retrieval working files (`research/from-retrieval/output/`,
  `from-retrieval-triage-ledger.md`, `research/from-retrieval/README.md`) per owner
  request.
