# Research log: 1777 Piracatu baptism — Toledo line extended to Portugal

**Date:** 2026-08-07 (third session this date)
**Researcher:** Claude Code (AI assistant, value-gate operator)
**Session type:** Discovery summary — retrieval drop value-gate (PAR-0025, PAR-0026)

---

## 1. PAR-0025: 1777 Piracatu baptism (primary source — LINE EXTENSION)

**Image:** `rec-armond-maria-umbelina-da-silva-baptism-gen-1.jpg` (1600×1120 px,
18th-century Portuguese cursive parish register)

**What the record shows:** An original parish baptism entry at the Minas do Piracatu
(Manga parish, Bispado de Pernambuco), 23 August 1777. The baptised child is "Maria",
born 12 August 1777, legitimate daughter of Amaro da Silva Xavier (P-0059) and Ignez
Francisca de Lima (P-0060). The entry names all four grandparents:

- **Paternal:** [uncertain rank: Sargento/Tenente?] Amaro da Silva Barreto (P-0064),
  "natural da Villa de Guimaraes, Arcebispado de Braga" (Guimarães, Portugal)
  × Perpétua da Silva (P-0065), "natural da Cidade de S. Paulo"
- **Maternal:** João Rodrigues de Mello (P-0066), "natural da Villa de Vianna,
  Arcebispado de Braga" (Viana, Portugal — almost certainly Viana do Castelo)
  × Maria Francisca Cordeira (P-0067), "natural da Villa de Ouru [Ouro?], Bispado
  de S. Paulo"

**Significance:** This is a primary source that simultaneously:
1. Extends the direct Toledo line by two generations on both Amaro's and Ignez's sides
2. Confirms two Portuguese immigrant ancestors: Amaro da Silva Barreto from Guimarães
   and João Rodrigues de Mello from Viana — both in the Arcebispado de Braga (northern
   Portugal)
3. Establishes Amaro da Silva Xavier's birthplace as Meia Ponte (Goiás) — a material
   conflict with PAR-0023 (1810) which states both he and Ignez as "naturais e batizados
   da Freguesia de Barbacena"

**Child name flag:** The image labels the child "Maria" only. The retrieval agent's
working filename "rec-armond-maria-**umbelina**-da-silva-baptism-gen-1.jpg" is the
agent's hypothesis; "Umbelina" does not appear in the visible text. Any connection to
"Umbelina" requires a separate source.

**Material conflict (preserved):** PAR-0025 (1777, primary) says Amaro is "natural da
frequesia de Nossa Senhora do Rio de Meia Ponte, comarca do Goyas"; PAR-0023 (1810)
says both Amaro and Ignez are "naturais e batizados da Freguesia de Barbacena." Both
versions preserved in P-0059 and PAR-0025 notes. The 1777 record is more specific and
earlier; the 1810 description likely reflects long-term Barbacena domicile.

## 2. PAR-0026: 1838 São José del-Rei certidão (derivative — corroboration)

**Image:** `rec-armond-cezario-jose-da-silva-lim-baptism-gen-1.jpg` (1252×1241 px,
typed 2019 diocesan certidão)

**What the record shows:** Typed 2019 certified ecclesiastical transcript from the
Diocese de São João del-Rei of an 1838 baptism at the Matriz de Santo Antônio de
São José del-Rei (today Tiradentes). Child: Carolina, born 28 February 1838, daughter
of "Capitão Cezario Jose da Silva Lima" and "Dona Joanna Umbelina de Jesus." Paternal
grandparents (verbatim): "**Capitão Amaro da Silva Xavier** e Dona **Ignez Francisca
de Lima**" — independently corroborating the F-0029 union.

**Significance:** A second independent source (besides PAR-0023) confirming the
Amaro × Ignez parentage. Also confirms Capitão Cezário José da Silva Lima as a son
of Amaro × Ignez — consistent with his role as a familial witness at the 1810
Ladisláo × Mathilde marriage (PAR-0023, "Furriel Cezário José da Silva alias Cezário
José da Silva Lima").

## 3. PRB-0006 correction: Eliza Balbina's parentage

A review of the primary evidence (deployed in parallel with this cataloguing work)
confirmed that PRB-0006.yaml's title, abstract, and reliability fields contained the
old misread: "Eliza Balbina de Toledo is JC's daughter." The transcription correctly
reads "5º Simplicio José Ferreira Armond, cazado com D. Eliza Balbina de Tolledo"
— Eliza is named as Simplício's wife, not as a listed representante/child.

**Correction applied to PRB-0006:** title, abstract, reliability, and notes updated.
The "JC's daughter" hypothesis is now REJECTED by two independent 1867 primary sources
(PRB-0008, PRB-0009 both list JC's children without Eliza). Eliza's actual parentage
remains unresolved (STATUS.md conflict #14 updated).

## 4. Transcription audit fixes (PRB-0008, PRB-0009, PAR-0026)

- **PRB-0008:** Corrected p6 status — p6 was NOT catalogued (catalogue_reference and
  transcription header incorrectly said "Nine pages: gen1, p2–p6, p8, p9"). Correct:
  eight pages (gen1, p2–p5, p8, p9). p6 is critical: it contains the year of JC's
  death (p5 breaks off after "dois de Setembro"). Updated limitations to acknowledge
  pp 2–4 as catalogued but untranscribed.
- **PRB-0008 + PRB-0009:** Flagged Simplício's middle name discrepancy: PRB-0008 p8
  reads "Simplicio José"; PRB-0009 p4 reads "Simplicio Jaci." Added to limitations
  in both records; requires image comparison.
- **PAR-0026:** Added unread certidão issuance date and archivist name to limitations.

---

## Entity changes this session

| Entity | Change |
|---|---|
| PAR-0025 | NEW: 1777 Piracatu baptism of Maria (primary source, line extension to Portugal) |
| PAR-0026 | NEW: 1838 São José del-Rei certidão (derivative corroboration) |
| P-0064 | NEW: Amaro da Silva Barreto (from Guimarães, Portugal) |
| P-0065 | NEW: Perpétua da Silva (from São Paulo) |
| P-0066 | NEW: João Rodrigues de Mello (from Viana, Portugal) |
| P-0067 | NEW: Maria Francisca Cordeira (from Villa de Ouro) |
| F-0031 | NEW: Amaro Barreto × Perpétua da Silva (parents of Amaro da Silva Xavier) |
| F-0032 | NEW: João Rodrigues × Maria Francisca (parents of Ignez Francisca de Lima) |
| P-0059 | Updated: F-0031 added to family_ids; birthplace conflict note added |
| P-0060 | Updated: F-0032 added to family_ids; parents confirmed note added |
| F-0029 | Updated: PAR-0025/0026 added to partner sources; Maria + Cezário added as documented_children |
| PRB-0006 | CORRECTED: title, abstract, reliability, notes — Eliza parentage misread fixed |
| PRB-0008 | CORRECTED: p6 page count fixed (eight, not nine); limitations updated |
| PRB-0009 | Updated: Jaci/José discrepancy added to limitations |
| PAR-0026 | Updated: limitations expanded |
| record-coverage.yaml | P-0059/0060 notes updated; P-0064–P-0067 entries added |
| document-inventory.yaml | DOC-0061 (PAR-0025) and DOC-0062 (PAR-0026) added |
| STATUS.md | Counts updated; Toledo line note updated to reflect Portugal extension |

## Open leads from this session

- Two confirmed Portuguese immigrant branches: Guimarães (Amaro Barreto) and Viana
  do Castelo (João Rodrigues de Mello) — both Arcebispado de Braga; requires
  Portugal archive access for further research
- JC's death year: p6 not catalogued; year "1866" remains a contextual inference
- PRB-0008 pp 2–4: catalogued but untranscribed (lower priority)
- Simplício's middle name Jaci vs. José: requires image comparison of PRB-0008 p8
  and PRB-0009 p4
- "Maria" → "Umbelina" link: requires a separate source
- Remaining ~85 `rec-armond-*-doc-gen2/gen3` collateral images: owner direction needed
  on FAN/privacy scope for Simplício × Eliza descendants
