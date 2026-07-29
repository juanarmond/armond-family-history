# Projeto Compartilhar crawl and Azores source survey

## Research question

Exhaustively survey the owner-supplied source sites for our families and for the
Azorean Ferreira Armonde leads: projetocompartilhar.org (full crawl),
myportuguesegen.blogspot.com (Azores resource directory + family posts), and the
Scribd copy of Forjaz & Mendes, "Genealogias da Ilha Terceira".

## Method and access

Three read-only agents plus direct fetches; public sources only; WebSearch
budget exhausted, so `curl`/`pdftotext`/Wayback only. Everything is a lead; no
conclusion changed; no entity was created.

## Projeto Compartilhar (full crawl)

- **Scope:** São Paulo captaincy + migration to southern Minas, to mid-19th c.
  Covers Barbacena/Curral Novo/Borda do Campo well; does **not** cover
  Leopoldina/Piacatuba/Além Paraíba/Zona da Mata lowlands, nor Rio de
  Janeiro/Espírito Santo, nor German families. This explains the zero results for
  our RJ/ES lines and for Aristão's Piacatuba.
- **New Armond hits (census):**
  - **Manoel Antonio de Armond** — João Gomes (Termo de Barbacena), 1831 census,
    fogo 22: branco, livre, 30, casado, tropeiro; wife Barbara Maria (22); son
    Camillo Antonio (7); 2 cativos. A **married** Armond branch near Barbacena — a
    more plausible source of a later "Simplício" namesake than the celibate
    Curral Novo brothers. Lead only. (Preserved: `resources/projetocompartilhar-1831-joao-gomes-censo.pdf`.)
  - Anastacio Ferreira Ormondes — Candeias 1831, carpinteiro, parda; different
    profile, low priority.
  - Bernardo Muniz Azevedo — Meia Pataca/Cataguases 1831, lavrador; a "Muniz +
    Azevedo" coincidence in the Zona da Mata, probably unrelated to our RJ line.
- **1751 will/inventory of the patriarch** (`DocsMgAF/FranciscoFerreiraArmond1751.htm`,
  preserved): declares him "natural da Ilha Terceira, freguesia da Vila de São
  Sebastião, filho de Gaspar do Souto Maior e Margarida das Candeias" —
  corroborates the Azorean origin from the will itself. Wealth ~1:480$000 + 119
  oitavas de ouro + ≥4 slaves; illiterate. More testamento leads on the site:
  Manoel Ferreira Armond (Fazenda dos Moinhos, 1775), Vicente Ferreira Armond
  (1756).
- **Genealogy pages** (`BentoFaleiro`, `AnaMariadeJesus...`, `FortesdeBustamante`)
  confirm the tree and its Rio Novo/Juiz de Fora elite branch (Mariano José
  Ferreira Armond †1844 → Mariano Procópio Ferreira Lage).
- **Method caveat:** the agent searched the name-titled indexes and fetched the
  Armond sub-pages; it did not body-search all ~1,300 sub-pages, so the surname
  may appear as witnesses/kin inside other Barbacena/Borda-do-Campo entries.

## My Portuguese Gen (Azores)

- The index page is a **curated directory** of Portugal/Azores archives — a
  search map, not a page of names: GEA registos + **passaportes**, culturacores
  bd, arquivos.azores (Archeevo), BPARLSR "fontes genealógicas", DigitArq/Tombo,
  CEPESE, BN Digital, UMinho GHP, and a Scribd "Genealogias de São Miguel e Santa
  Maria" (Rodrigo Rodrigues) — the last relevant to the São Miguel João lead.
- Family posts + comment threads discuss the São Sebastião "Ferreira
  Armonde/Drummond" family. New dated leads (amateur transcriptions): Ângela
  Maria da Conceição = daughter of Bento Francisco Faleiro & Francisca Nunes,
  bapt. 29 Apr 1700, m. Angra do Heroísmo 27 Nov 1721, d. 2 Apr 1747 (a death-year
  conflict with the ASBRAP "1746" — preserve both); emigrant sons José (m.1772)
  and Manoel (m.1759, to a Ponta Delgada/São Miguel widow), both "naturais de São
  Sebastião, Terceira".
- Two competing, **unsourced** surname-origin myths: French-via-Madeira (Senra)
  vs. Scottish Drummond-via-Madeira (John Drummond / "Joam Escórcio", Funchal
  1470). The blog owner concedes "no primary record at all" pre-1600. Leads only.

## Scribd — Forjaz & Mendes, "Genealogias da Ilha Terceira"

- Scribd is fully bot-walled (a "Client Challenge" JS interstitial); no content
  readable by curl. The authoritative Terceira genealogy (vols 1-9, uploader
  Joao-Henrique-F-Vieira) is a **browser/human** target. It is a secondary
  compilation; the correct evidence route is the **primary parish registers of
  São Sebastião / Angra (1541-1911), free at the GEA** (culturacores.azores.gov.pt/ig),
  once a freguesia is fixed. Recorded in `resources/README.md`.

## Per-locality FamilySearch catalogue (target-prep)

MG Civil `3479702`, MG Catholic `2177275`, RJ Civil `1582573`, RJ Catholic
`1719212`. Leopoldina parish `345430` (1852-1924, covers Piacatuba); Barra Mansa
civil `516378`; Sapucaia civil `385592`/`4135303`; Barbacena parish `21641`;
Paraíba do Sul `336216`/`385607`; Valença `336328`/`564682`. Carangola/Tombos
have **no** local catalog (statewide + full-text only). Iris Bohrer's 1929 birth
sits in `3479702` (search under Alto Jequitibá and Manhuaçu).

## Other refined leads

- **João Bittencourt naturalisation:** not in the 1871 Coleção das Leis
  (negative); the correct source is the Arquivo Nacional (SIAN) "Cartas de
  Naturalização". The naturalisation supports (not contradicts) the São Miguel
  origin.
- **Sapucaia parish books custody:** Diocese de Valença (1925) **or** Diocese de
  Petrópolis — confirm both; Niterói ruled out.
- **Elisa Balbina Tolledo origin:** a same-parish Toledo family in Piacatuba
  (Clementino José de Toledo; Francisca Emília de Toledo) — navigation lead.
- **Inventários/testamentos (wealth):** for the historical Barbacena family,
  documented (1751 Francisco; 1775 Manoel; 1756 Vicente; 1845 monte-mor ~£90k) —
  context, kept in `resources/`. For our own line, the actionable probate target
  is Vicente's Carangola inventário.

## Contacts made

Outreach recorded in `logs/correspondence-log.md`: Mauro Senra (sent
2026-07-29), Nilza Cantoni (sent 2026-07-29), Paróquia N. Sra. da Piedade de
Piacatuba (sent 2026-07-29, email + contact form) — all about the decisive
Simplício × Elisa marriage.

## Conclusions

- No new evidence, no promotions. Strongest result: a firmer negative — the
  documented Armonde tree does not reach Piacatuba, and the 1831 census confirms
  the anti-merge on a primary document. The married Manoel Antonio de Armond
  (João Gomes 1831) is a new candidate for a later namesake, but unlinked.
- The decisive open test stays the Piacatuba marriage of Simplício × Elisa.

## Next actions

1. Codex: Piacatuba marriage + baptisms 1879+ (catalog 345430); Barra Mansa
   death (516378); Sapucaia civil (385592); Iris 1929 birth (3479702).
2. Await replies from Mauro Senra / Nilza Cantoni; send the parish request after
   the free FamilySearch attempt.
3. Populate person `occupations` from held-source transcriptions (a focused pass).
