# Online gap-and-resource research: record sources, Portuguese origins, tooling

## Research question

While FamilySearch API access is pending, what online resources (record
repositories, archives, certificate portals, published scholarship, software)
can advance the open direct-line gaps and blockers, and how should each specific
target record be pursued?

## Method

Four parallel web-research passes (search + fetch), then consolidation. No
authenticated FamilySearch, Ancestry or MyHeritage session was available; only
public pages were read. All findings below are navigation leads or resource
identifications, not evidence. Nothing here changes a genealogical conclusion.

## Discoveries (new, verified where noted)

- **FamilySearch "Image Restricted" scans are unlockable for free at a
  FamilySearch affiliate library / center** (locator: locations.familysearch.org)
  — the same images, location-locked by contract, not deleted. This is the primary
  route to the restricted Minas Gerais parish images. Do not use VPN/proxy tricks
  (ToS violation).
- **Aristão's family = the "Ferreira Armond" of Piacatuba / Leopoldina, MG.** A
  confirmed sibling, **Marfisa Ferreira Armond, baptised 15 Feb 1873 at Nossa
  Senhora da Piedade, Piacatuba** (parents Simplício Ferreira Armond & Elisa
  Balbina Toledo), fixes the parish for Aristão's ~1879 baptism.
- **The Azorean origin is documented for the historical Ferreira Armonde family
  but NOT linked to Aristão.** Primary chain (Lacerda, UFF 2010,
  historia.uff.br/stricto/teses/Tese-2010_Antonio_Henrique_Lacerda-S.pdf):
  **Francisco Ferreira Armonde, b. Ilha Terceira, freguesia de São Sebastião**,
  per his 1751 will (Museu Regional de São João del-Rei). Chagas (UFMG 2018
  repositorio.ufmg.br/handle/1843/BUOS-B2YP8Y; 2024 …/68111) builds it via
  Barbacena parish books and Mariana marriage habilitações, and explicitly warns
  that a shared surname only suggests kinship. The link to Aristão must be built
  from primary records, not assumed. The "French origin" motif in blogs is
  uncited family tradition.
- **"Presidente Soares" (Iris Bohrer's reported 1929 birthplace) = present-day
  Alto Jequitibá, MG** (IBGE: povoado → district 1923 → município "Presidente
  Soares" 1953 → renamed Alto Jequitibá 1991). It is NOT Raul Soares. Zona da
  Mata / Caparaó, the same broad region as Carangola.
- **Volta Redonda was a district of Barra Mansa until 1954** — so Liliosa's ~1946
  civil death sits in the Volta Redonda / Barra Mansa registry.
- **Sapucaia was under the Rio archdiocese until the Diocese de Valença was
  created (1925)** — so the 1882 João–Susanna marriage book may be at the **Cúria
  do Rio archive** (confirmed open in 2025–26, paid by form: catedral.com.br/arquivo),
  not the local diocese.
- **Two historians cover our exact families:** Mauro Luiz Senra Fernandes
  (Ferreira Armond AND Sapucaia histories) and a GeneaMinas collaborator.

## Resources by gap

- Aristão baptism / siblings / Aristão×Liliosa marriage: FamilySearch catalog
  345430; films 004640627 (Leopoldina baptisms 1878–88) and 004640632 (Piacatuba
  baptisms 1870–1905; Leopoldina marriages 1898–1920). Full agent task-spec in
  `research/familysearch-image-targets.md`.
- Liliosa 1946 death: Volta Redonda / Barra Mansa cartório; registrocivil.org.br
  (locator transparencia.registrocivil.org.br).
- Sapucaia 1882 marriage: FamilySearch catalog place "Sapucaia"; Cúria do Rio;
  Paróquia Santo Antônio de Sapucaia; also freguesias de Aparecida and São José
  do Vale do Rio Preto.
- Vicente's Portuguese origin (bridge-first): his Carangola marriage/habilitação
  (FamilySearch MG Catholic, collection 2177275) → naturalidade; Arquivo Nacional
  "Entrada de Estrangeiros – Rio 1875–1910" (name-searchable); APM (Juiz de Fora
  hostel); Carangola inventário via TJMG "Memória do Judiciário"; then the
  Portuguese parish via DigitArq (digitarq.arquivos.pt), tombo.pt, or CEPESE
  (name-searchable emigration DB).
- Azores/Madeira origin verification: GEA parish images 1541–1911 and GEA
  Passaportes 1770–1939 (culturacores.azores.gov.pt/ig), Madeira ABM
  (arquivo-abm.madeira.gov.pt) — all free.
- Tooling / prior art: no MCP reads YAML (build a thin one over our own entities
  later; pattern from airy10/GedcomMCP); GEDCOM export is lossy vs our evidence
  model (python-gedcom7); viewers topola / family-chart; closest design twin
  genealogix/glx (too new to depend on). FamilySearch API has no hobbyist tier and
  its terms favour cite-and-link over storing images.

## Could not verify

- Whether Aristão's line connects to the Azorean Ferreira Armonde tree (must be
  built from Barbacena/Mariana/MRSJDR records).
- Whether the 1866 "Vila do Rio Claro" Vicente (likely Rio Claro, RJ) is our
  Vicente who died in Carangola (geographically strained).
- Any newspaper (Hemeroteca) or cemetery (Find a Grave/BillionGraves) hit — the
  search apps are login/JavaScript-walled.
- Existence of a separate Piacatuba or Santo Antônio de Sapucaia FamilySearch film
  (catalog needs login); confirmed only the Leopoldina catalog 345430.

## Next actions

1. Via a FamilySearch affiliate library, retrieve Aristão's baptism and the
   Aristão × Liliosa marriage from films 004640627 / 004640632.
2. Order Liliosa's 1946 death and (owner's own) 1982 birth via registrocivil.org.br.
3. Locate Vicente's Carangola marriage and inventário; then chase the Portuguese
   parish. 4. Contact Mauro Senra. Execution details in
   `research/familysearch-image-targets.md`.

## Follow-up: Ferreira Armonde bridge analysis (thesis text-mining, 29 Jul 2026)

Text-mined the Lacerda thesis (UFF 2010) and our PUB-0001 (Chagas 2018) to test
whether Aristão connects to the documented Azorean Ferreira Armonde family.

- Documented root (primary): **Francisco Ferreira Armonde**, b. 1691, Ilha
  Terceira, freguesia de São Sebastião, × Felizarda Maria Francisca de Assis,
  settled at **Fazenda dos Moinhos, freguesia de N. Sra. da Piedade de
  Barbacena** (Curral Novo). Twelve children (1831 Curral Novo census).
- **Anti-merge (negative result):** the first-generation **"Simplício José
  Ferreira Armonde" died *solteiro* (unmarried)** — he is NOT Aristão's father.
  "Simplício" recurs as a family given name; do not conflate. Chagas's "Simplício
  José Ferreira da **Fonseca**" is the allied Fonseca family, also not ours.
- **Geographic bridge:** in the Imperial period several members migrated to the
  **Zona da Mata, specifically Além Paraíba** (fazenda Barra do Peixe; inventory
  at the Fórum Nelson Hungria de Além Paraíba; óbito in the Além Paraíba matriz) —
  adjacent to Piacatuba/Leopoldina, where Aristão's branch is by 1873.
- **Hypothesis (unproven):** Aristão's father — a *later* Simplício Ferreira
  Armond, in Piacatuba by 1873, married to Elisa Balbina Toledo — descends from
  the Barbacena Azorean Armonde family via the Além Paraíba migration. To prove
  it, find Simplício's marriage (names both spouses' parents) and his baptism,
  then link his parent to the Lacerda tree.
- **Concrete record targets surfaced (for Codex / archives):**
  - Barbacena baptisms — **Livro de Batismos da Freguesia de N. Sra. da Piedade
    de Barbacena, 1828–1872** (Chagas cites p.71 for a Fonseca).
  - Armonde patriarch inventory — **AHMPAJS (São João del-Rei), caixa 385, ordem
    20, 1845**.
  - Além Paraíba inventories/óbitos — **Fórum Nelson Hungria, Além Paraíba**.
  - **Projeto Compartilhar** (projetocompartilhar.org) — cited by Lacerda;
    confirmed to hold Barbacena/Armonde transcriptions; browser-accessible.

All of the above are leads/hypotheses from secondary scholarship, not evidence.
