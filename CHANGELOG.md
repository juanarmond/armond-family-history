# Changelog

All notable repository changes are recorded here. Genealogical conclusions must
also remain traceable through source records and research logs.

## Unreleased

### Changed — Sources list is compact and ordered person-first (2026-08-13)

- The Sources ("Fontes") list no longer prints the full **transcript inline** — the transcript stays in the document reader ("Ler documento"), shown beside the scan image. The list keeps the concise abstract and the limitation note, so each source is far more compact. (Same for the FAN references list.)
- **Per-person ordering:** a person's **own vital records** (birth/baptism, then marriage, then death) now sort **first**, in that vital order; records that only **mention** them (a child's or relative's baptism/marriage/death) follow, ordered by the source's own vital type. Previously the list was ordered by a global source rank that did not distinguish the person's own records from records that merely named them.

### Fixed — the Sources ("Fontes") section is now fully bilingual (2026-08-13)

- Each document's **title** and **meta line** in the person panel's Sources (and FAN) lists rendered in English even in PT mode — only the abstract/transcription were localized. Now:
  - **Added `title_pt` to all 94 sources and 13 FAN records** (a Brazilian-Portuguese translation of each free-text title, with names, dates, places, folio/record numbers and entity IDs preserved verbatim), produced via 5 parallel agents over disjoint sets. The viewer renders `localeText(title, titlePt)`, so titles switch with the language toggle and fall back to English if a PT title is ever missing.
  - **The meta line (record category · source form · information quality) is now localized via new viewer vocab tables** — no data change; unmapped values fall back to English.
  - **Schema:** added the optional `title_pt` to the source and FAN schemas; the data-loader projects `titlePt` and the raw enum values (for vocab). The renamed viewer already reads these.
- `make check` green (69 + JS tests, incl. i18n key parity and schema validation); the viewer index and GEDCOM are unaffected (neither carries source titles).

### Changed — Renamed the site to "Four Rivers"; narrative moved to YAML; reflow fix (2026-08-13)

- **Renamed** the site from "Armond Family History" to **"Four Rivers"** (PT: **"Quatro Rios"**), with a new subtitle — *"Four family lines, from four continents — every ancestor traced to an original record."* (PT: *"Quatro linhas familiares, de quatro continentes — cada ancestral rastreado até um registro original."*). The Armond-only title undersold the maternal (Muniz/Bohrer) and in-married lines and contradicted the narrative's own convergence thesis; "Four Rivers" names the four grandparent lines that flow into one person. (`index.html`, `i18n.js`; the repository name is unchanged.)
- **Narrative moved to repo-standard YAML.** The convergence story now lives in `family-tree-viewer/family-story.yaml` as `en`/`pt` **literal (`|-`) block scalars** instead of raw `.md` files, so it matches how every `profile` is stored. Fixed the rendering bug this surfaced: `renderPortrait` turned each hard wrap into a forced `<br>` (~290 of them) because the raw markdown was fetched verbatim; it now **joins wrapped lines with a space** (safe — profiles are folded YAML and never carry multi-line paragraphs), so the text reflows to the reading column. PT fidelity fix: "*fazendeiro*" (estate-owner) → "*lavrador*" for Antenor, matching the landless-baseline thesis.

### Fixed — Audit remediation: tier consistency, partilha links/coverage, source→person gaps (2026-08-13)

- Four-agent read-only audit of the 2026-08-13 work; every finding verified before fixing.
- **1716 marriage tier consistency:** the marriage was `[PROVEN]`/`confirmed` (P-0080/P-0081 profiles, F-0039, E-0072) while the parentage from the *same record and identity* was `strong-evidence`. Downgraded the marriage to **strong-evidence** with the identity caveat, so the whole Ruivais attachment is consistent. Removed a stale "higher-resolution ADB" claim missed on **P-0089** (the ADB copy is lower-resolution) and in the session log.
- **1919 partilha (PRB-0011):** recorded the ~1919+ death-bound in Simplício's **death** coverage block (was only in the birth note); added PRB-0011 to **P-0017**'s Sources-held (EN+PT); refreshed the now-stale **F-0006** note ("does not assert a marriage" → the union is documented by PRB-0001/PRB-0011); softened the abstract's "Toledo estate" to an inference; and transcribed the land unit as the visible "**ares**" instead of the implausible "[alqueires]" guess.
- **Two source→person link gaps closed** (verified real, not namesakes): **PUB-0003 → P-0028** (the published genealogy is P-0028's own parentage source yet omitted him) and **REC-0001 → P-0004, P-0005, P-0008, P-0017** (the owner's ancestor roster linked the maternal branch but omitted the whole paternal branch it names). The audit dismissed ~40 substring false positives (namesakes/contextual).
- 324 entities; `make check` green (69 + JS tests, incl. i18n key parity); index + GEDCOM regenerated.

### Changed — Family Story mobile polish; 1716 scan kept as the sharpest (2026-08-13)

- Fully adapted the Family Story page to mobile: full-screen sheet, a **floating, always-reachable close button** (fixed top-right, larger touch target) so a long read can be dismissed without scrolling back up, plus word-wrap, reading padding and momentum scrolling.
- Duplicate-scan review on the 1716 Ruivais marriage: the **held FS-tree scan (3825×2677) is sharper and more complete** (both spouses + all four parents on one page) than the drop's ADB copy (2144×1500/page), so it is **kept** as the best version. Corrected the notes that had called the ADB copy "better/higher-resolution", and set **"já defunto"** (parallel to the bride's father, not the synthesis's "de Frades") as the preferred reading of Gonçalo's clause on P-0088/PAR-0036/F-0043.

### Added — "Family Story" reading page: the bilingual convergence narrative (2026-08-13)

- A new **Family Story** button (toolbar, and a "Read the family story →" link on the living-person panels — i.e. on Juan's own node) opens a centered reading overlay (full-screen on mobile) rendering **"How I Came To Be"** — the long-form narrative of Juan's four grandparent lines (Armond/Toledo, Guimarães/Engrácio, Muniz/Azevedo, Bohrer) converging in the Zona da Mata and the Volta Redonda steel city. It is grounded entirely in records already held in this archive; a header note frames it as a narrative synthesis (not evidence), and living people appear by first name only.
- **Bilingual:** it follows the existing EN/PT language toggle, fetching `family-tree-viewer/family-story.en.md` / `family-story.pt.md`; the Portuguese translation was produced via four parallel agents over disjoint sections and reassembled. Rendered with the portrait light-markdown renderer (`renderPortrait`), now extended to render `*italic*` as well as `**bold**` and the evidence-tier chips. Viewer-only; no genealogical data change.

### Added — Ruivais G10 ancestors; Simplício's 1919 Toledo partilha; Cordeira/Leme lead (2026-08-13)

- Value-gated the 2026-08-13 retrieval sync (6 images), verifying each against the scan.
- **Portugal G10 extension.** The four parents named in the 1716 Ruivais marriage (PAR-0036),
  previously held as deliberate *leads*, were promoted to modelled entities: **P-0088 Gonçalo
  Rodrigues × P-0089 Elebia Francisca** (family **F-0043**, parents of João Rodrigues P-0080)
  and **P-0090 Domingos Gonçalves × P-0091 Maria Fernandes** (family **F-0044**, parents of
  Joanna Gonçalves P-0081) — Juan's four 8×-great-grandparents at São Martinho de Ruivais,
  Braga. Status **strong-evidence** (parentage stated directly in PAR-0036, but resting on the
  identification of the 1716 couple with P-0080/P-0081). The "lead, not modelled" notes on
  PAR-0036/F-0039/P-0080/P-0081 were superseded, and the "já defunto" vs "de Frades" reading of
  Gonçalo's clause is preserved on P-0088. The drop's "1716 marriage" image is a **duplicate**
  of PAR-0036 (a better ADB 2-page scan; no re-catalogue).
- **New source PRB-0011** — a Leopoldina Toledo estate-division "pagamento ao herdeiro" folio,
  allotting a fazenda share to the heir Simplício José Ferreira Armond (P-0016), "casado com
  Dona Eliza Balbina de Toledo" (P-0017). Attached to both; corroborates his heir-by-marriage
  standing (previously only PRB-0001/PRB-0002) and, if the retrieval agent's 1919 dating holds,
  extends his documented presence from "after 1902" (NWS-0003) toward c.1919. It does **not**
  name his Armond parents; the parentage keystone stays open. The retained folio bears no date,
  place or decedent — those are the agent's identification, recorded as such.
- **Cordeira/Leme (3 São Paulo images) recorded as a lead on P-0067, not promoted** — no primary
  bridges the 1737 Itu "Maria dau. of Francisco Leme do Prado × Francisca Cordeira" to our Ignez,
  and the "Itu" premise conflicts with PAR-0025, which reads her origin "Villa de Ouru [Ouro?]".
- 324 entities (+4 people, +2 families, +1 source, +1 inventory); `make check` green (69 + JS
  tests); reciprocity verified; index + GEDCOM (7.0, 4115 lines) regenerated.

### Changed — removed redundant `transcription_pt` from 33 Portuguese-language records (2026-08-12)

- Follow-up to the field-validation audit. For a Portuguese-language record the verbatim `transcription` is already Portuguese, so a `transcription_pt` that merely re-localizes the **bracketed editorial notes** (e.g. "Marginal note:" → "Nota à margem:", "[FamilySearch Full-Text extract:]" → "[Extrato … do FamilySearch:]") duplicates the whole record body for no benefit — the viewer already falls back to `transcription` in PT mode (`localeText`). Removed the field from **33 records** verified byte-identical except editorial framing, via 4 parallel agents over disjoint sets, each confirming no unique record data was lost before deleting: **20 sources** (CIV-0005/0008/0013/0017/0018/0020/0022/0024, GOV-0001, PAR-0001/0005/0006/0010/0017/0018/0019/0023/0025/0026, PRB-0006) and **13 FANs** (FAN-0001…FAN-0013).
- **Kept (not redundant):** the Italian (CIV-0010/0011/0012) and Latin (PAR-0027/0028/0029) originals, where the PT rendering translates the foreign record; and **5 records whose `transcription_pt` translates substantive editorial/summary prose, not just brackets** (PRB-0008, PRB-0009, PUB-0001, PUB-0002, PUB-0003 — for PUB-0003 the `transcription` is itself an English summary), so its removal would strip real bilingual content.
- Pure deletion (410 lines, 0 insertions); every `transcription` left intact. `make check` green; viewer index and GEDCOM unchanged (neither reads `transcription_pt`).

### Fixed — audit remediation: relationship labels, F-0016 double-count, source→person links (2026-08-12)

- **Relationship-label corrections** (prose only, no structural change), from the 4-agent field-validation audit: **P-0004** called Simplício (P-0016) Geraldo's *great-grandfather/bisavô* — he is his **grandfather/avô** (Geraldo ← Aristão ← Simplício). **P-0059 (Amaro)** & **P-0060 (Ignez)** were labelled Eliza's *maternal* great-grandparents — they are on **her father's maternal line** (Eliza ← father José Cezário ← his mother Mathilde ← Amaro/Ignez). **P-0040 (José do Rego Brandão)** was "Antenor's *maternal* great-grandfather" — he is Antenor's **paternal** great-grandfather (via Antenor's father Deocleciano → his mother Susanna); the "*maternal* grandfather of Deocleciano" half was correct and left. **P-0032** prose "P-0010 b. c.1895" → **1894** (his proven birth, E-0024/CIV-0002). All lineages re-verified against the family graph.
- **F-0016 double-count fixed:** "Joaquim José Bohrer" was listed both as the modelled child **P-0030** and as a `documented_children` entry, so the viewer showed him **twice** in both parents' Children and listed **P-0030 as his own sibling** (the roster builder appends documented_children with no de-dup). Removed the redundant entry; its evidence (PRB-0005 names "Joaquim") is already carried on P-0030's parent-relationship and the family notes. The other 3 documented children (Laura, Guilherme, Fernando — never modelled) remain.
- **8 source→person link gaps closed** (records that named a modelled person but omitted them from `linked_people`, so the viewer could not surface the source on that person's page): **PRB-0009**+P-0063, **PRB-0002**+P-0027 (the decedent), **PRB-0004**+P-0056, **CIV-0014**+P-0015 (surviving spouse), **PAR-0005**+P-0045, **PAR-0018**+P-0078/P-0079 (bride's parents, now modelled — stale note corrected), **CIV-0006**+P-0019/P-0020/P-0039, **NWS-0001**+P-0009 (mother in the banns), **PAR-0045**+P-0048/P-0049/P-0086/P-0087, **PAR-0044**+P-0086/P-0087.
- **CIV-0006 name conflict preserved (not erased):** its 2019 full-content reproduction reads Luiza's father as "Sebastião [uncertain: Manoel] de Azevedo" vs "José Secundino de Azevedo" (P-0038) in CIV-0001 — same 1916 record; P-0038 deliberately left unlinked to this derivative with a note, pending resolution.
- 317 entities; `make check` green (69 + JS tests); reciprocity verified; index (unchanged) + GEDCOM (7.0, 4053 lines) regenerated. Audit confirmed the rest of the graph clean (full family/event reciprocity, chronology, citations, bilingual profiles/notes).

### Fixed — panel header lifespan falls back to baptism/burial; mobile marriage date; living-event redaction (2026-08-12)

- Follow-up to the birthplace fix, from a 4-agent field-validation audit. The detail-panel **header lifespan** (`lifespan()`) read *only* `birth`/`death` events, so the same baptism-only ancestors showed "Dates not established" or "?–YYYY" in the header while the biography prose right below printed the baptism year. It now falls back to **baptism** for the start year and **burial** for the end year — matching the biography and the fact rows. Restores headers for Ladisláo (P-0056 → 1787–), Rosa Eugenia de Lemos (P-0035 → 1835–), João Rodrigues Valle (P-0078 → 1728–), Johann Jacob Wehrli (P-0072 → 1751–1827), Elisabetha Borer (P-0073 → 1760–1832).
- **Mobile spouse row** passed the whole marriage object to `bioWhen()` (which expects a date), so the marriage year never showed on mobile; now uses `spouse.marriage.date` like the desktop panel.
- **Living-person events are now redacted at the data layer** (`data-loader.js`): a living person's own birth/death events (sensitive PII) no longer project to the viewer, closing a latent leak if an event were ever attached (the 3 living people have none today). Locked in with a data-loader test. Nationality is *deliberately* kept for the living (low-sensitivity, already tested) and was left unchanged. Viewer-only; no data change.

### Fixed — birthplace/death-place fall back to baptism/burial in the person panel (2026-08-12)

- The detail panel's **"Local de nascimento"** read *only* `birth`-type events, so ancestors held via a baptism record (no separate birth event) showed "Não estabelecido" even though the baptism names the parish — 5 people currently (Ladisláo P-0056, Rosa Eugenia de Lemos P-0035, Johann Jacob Wehrli P-0072, Elisabetha Borer P-0073, João Rodrigues Valle P-0078). Birthplace now falls back to the person's **own baptism place**, and death-place to a **burial place**, when the primary event is absent. Safe because `person.events` is already role-filtered to the subject (principal/spouse/partner), so a parent named in a child's baptism never leaks in. Viewer-only (app.js); no data change.

### Fixed — generation labels on the deep Toledo line, relative to Eliza (2026-08-12)

- Prose-only correction (no structural change): several profiles/notes labelled Eliza's (P-0017) Toledo ancestors one generation too deep — counting from her son Aristão rather than from Eliza. Corrected against the F-0026/F-0027 chain: **Ladisláo (P-0056) & Mathilde (P-0027) are Eliza's grandparents** (P-0027 had been written "great-great-grandmother"/*trisavó*, off by two, and her husband "great-grandfather"/*bisavô*); **Joaquim José (P-0057), Rita (P-0058), Amaro da Silva Xavier (P-0059) & Ignez (P-0060) are Eliza's great-grandparents** (had been "great-great-grandparent"/*trisavô/ó*). PAR-0018's "Ladisláo — Eliza's great-grandfather" → grandfather. 14 phrase fixes across 6 files (EN + PT), count-asserted. Labels relative to Aristão (P-0056) and the true great-great-grandparents (P-0064/65/78/79) were already correct and left unchanged. `make check` green (317 entities).

### Added — Rita Angélica's 1764 baptism (Rodrigues-Valle link → primary); Honório 1845 negative (2026-08-12)

- **New source `PAR-0049`** — Ritta Angélica Rodrigues's (P-0058) own **1764 Barbacena baptism** (FamilySearch coll 2177275; a two-page termo), with **new birth event `E-0076`** (born 3 March 1764, baptized 9 March 1764, Capela de São José do Ribeirão). Upgrades the **F-0038** parent edge (P-0058 ↔ João Rodrigues Valle P-0078 × Isabel Ribeira P-0079) from **strong-evidence to primary**, **resolves the "José vs João" doubt** on her father's forename → **João**, and primary-confirms the Ruivães/Braga origin. P-0058's birth goes [LEAD]→[PROVEN]. New lead (kept as lead): her maternal grandparents as a **Pestana couple of N.S. do Rosário, Ilha de São Jorge (Açores)** — a possible Azorean origin on Isabel's paternal side.
- **Honório José Ferreira Armonde's 1845 inventário** (LAMPEH Mariana, 19 pages): a **bounded negative** — his heirs are exclusively legitimate siblings/a nephew line, **no natural son**, so he is ruled out as Simplício's (P-0016) father. Recorded on P-0016's coverage; no entities created (collateral, connection unproven — anti-merge). Live childless-brother candidates remain Antônio José (d.1852) and Lino José (d.1870), off-tool at Barbacena.
- 317 entities; `make check` green (69 + 24 tests); reciprocity verified; index + GEDCOM (7.0, 4063 lines) regenerated; STATUS snapshot refreshed.

### Added — Muniz collateral children: 11 Mãe de Deus records as documented_children (2026-08-12)

- Value-gated the 11 new 2026-08-12 Nossa Senhora Mãe de Deus (Povoação, São Miguel) register images via three parallel subagents over disjoint sets (each read + transcribed + verified parentage), integrated centrally. Per the collateral rule these are `documented_children`, not person entities (no new persons, no events).
- **11 new PRIMARY parish sources `PAR-0038`–`PAR-0048`** (DOC-0079–0089). **F-0023** gains 7 siblings of Manoel Muniz Bytancourt (P-0042): a son of illegible name (1831), Michaelina (1833), Rosa (1834), Damaso (1836), Francisco (1839), **José (1841)**, Agostinho (1843). **F-0020** gains 3 daughters of Manoel × Francisca (sisters of the emigrant João P-0019): Maria (1842), Francisca (1849), Maria (1851). **F-0040** gains Maria Jacintha de Medeiros ⚭ Manoel Cabral (1818), a sister of P-0048.
- **The "José brother" question is settled** (PAR-0043) — the couple had a son José (b.1841), a *hypothesis-level* candidate for the José who emigrated to Sapucaia (not proven). The **1818 namesake trap is resolved** (PAR-0048 bride ≠ spine ancestor P-0049; parents differ). PAR-0044 independently names both grandparent couples → added as a **second source** on F-0040/F-0041. P-0047 gains a "de Pimentel" name-variant (PAR-0046).
- 315 entities; `make check` green (69 + 24 tests); all 11 inventoried + cited; index + GEDCOM (7.0, 4040 lines) regenerated.

### Added — Toledo: the 1833 Barbacena inventory of Rita Angélica Rodrigues (2026-08-11)

- Value-gated the six-page 1833 Barbacena inventário (read directly from the images).
- **New source `PRB-0010`** — the estate inventory of the deceased **Rita Angélica Rodrigues (P-0058)**, whose widower and inventariante is Capitão **Joaquim José Ferreira de Toledo (P-0057)** (confirming him alive and a captain in 1833). It records Rita's death (**9 February 1832, intestate**; new event **E-0075**) and names **all thirteen children of the couple, headed by Ladisláo Egídio Ferreira (P-0056)** — upgrading the F-0028 parent edge from strong-evidence to **direct**.
- The twelve non-Ladisláo children (incl. **José Anastácio** and **Antonio Zeferino**, the collaterals the FINDINGS flagged) are recorded as `documented_children` on **F-0028**; "Anna" (⚭ Antonio Dias Ladeira) reconciled to the existing Anna Belizaria.
- **Not promoted:** Joaquim José's own parents (Gaspar Ferreira × Gertrudes Maria, Vila Rica) are *not* named in this inventory and remain an unmodelled lead — the retrieval FINDINGS' "PRIMARY-ATTESTED" claim rests on the ink-bled PAR-0018 and awaits a legible read.
- 304 entities; `make check` green; reciprocity verified; index + GEDCOM (7.0, 3768 lines) regenerated.

### Added / Fixed — Muniz Azorean line +1 generation, and a marriage-record correction (2026-08-11)

- Value-gated the 2026-08-11 retrieval drop (BPARPD Ponta Delgada reply SE/2026/1583e, reconciled against the Culturacores CDN register images), verifying every promoted fact against the images.
- **Correction:** `PAR-0024` was mis-catalogued to folio 73r — a *different* late-1845 "Manoel × Roza de Jesus" couple (namesake). The true marriage of Manoel Muniz Bitancourt (P-0042) × Francisca Roza (P-0047) is **folio 32r, 17 February 1842** (with a 4th-degree consanguinity dispensation). PAR-0024 re-pointed (scan + date + full legible transcription); event **E-0053** corrected 1845-02-01 → 1842-02-17; the two folio-73r scans removed. Superseded reading preserved in notes.
- **New source `PAR-0037`** — the 7 October 1819 grandparents' marriage (folio 161v), giving family F-0023 a direct marriage record (new event **E-0074**) and both spouses' parents.
- **+1 generation, all PRIMARY:** Manoel Muniz Bitancourt "the elder" (**P-0082**) × Tereza do Amaral (**P-0083**) = **F-0040** (parents of P-0048); João de Medeiros Brandão (**P-0084**) × Maria Eugenia (**P-0085**) = **F-0041** (parents of P-0049); Manoel de Motta [var. Mello] (**P-0086**) × Anna de Souza (**P-0087**) = **F-0042** (parents of P-0047 — upgrades her earlier "parents [LEAD]" to [PROVEN]). P-0048 gains the fuller forename "João Francisco Muniz Bitancourt".
- 302 entities; `make check` green (69 + 24 tests); reciprocity verified; index + GEDCOM (7.0, 3634 lines) regenerated.

### Added — per-person "Portrait / Retrato" via a "More details" layer (pilot: Simplício, 2026-08-11)

- New optional bilingual person fields `profile` (EN) + `profile_pt` (PT) in the person schema — an evidence-tiered narrative portrait (`[PROVEN]`/`[INFERRED]`/`[LEAD]`/`[OPEN]`/`[CONTEXTUAL]`), synthesised from held sources and cited to this repo's IDs.
- Viewer: a **"More details / Mais detalhes"** link *inside* the biography section opens the full portrait as its **own panel docked at the right edge**, pushing the details panel left so both stay visible side by side (no modal overlay / no dimming). Closes on ✕, Escape, language toggle, or selecting another person. A light markdown renderer (headings, bullets, bold, `---`, styled evidence-tier chips); locale-aware via the PT/EN toggle, gated for living people, with English fallback.
- **Rolled out to all 78 deceased modelled people** (P-0004–P-0081; the 3 living are gated out). Written by five parallel agents over disjoint P-ID ranges, each **reconciled to our own sources/IDs and evidence tiers** (our data wins over the retrieval-agent drafts; unsupported draft claims dropped or tagged `[LEAD]`), bilingual EN + PT. Depth scales to the evidence (full portraits for well-documented ancestors, short stubs for thinly-attested ones).
- data-loader projects `profile`/`profilePt`; JS test covers projection + living-person gating. 291 entities; 69 tests + 24 JS tests pass.
- Portrait panel's close button now matches the person-detail panel's close button exactly (round `.detail-head button` styling — same size, border, colours, gold/green hover, and the "×" glyph) instead of the square lightbox-reader style; the image lightbox keeps its own button.
- Portrait section headings (`## `) now match the detail panel's section headings — gold `var(--gold)`, `.68rem`, weight 700, `.14em` uppercase — with a dividing rule between sections (mirrors `.detail-section` borders); `### ` sub-headings render as a subordinate muted variant.
- Mobile: the Portrait had no responsive treatment (it kept its desktop `min(30rem,50vw)` side-dock, rendering as a cramped half-width strip over the bottom-sheet). At `≤700px` it now opens **full-screen** (`inset: 0`) over the detail sheet, with the same `sheet-up` animation as the sheet; the header is pinned and the body scrolls (`flex`/`min-height:0`, momentum scroll) so long profiles no longer clip. No JS change.

### Fixed — resolve two evidence conflicts by re-reading the record images (2026-08-11)

- **P-0020 Susanna Rita Brandão — birth/baptism year.** Direct re-read of her baptism image (PAR-0005) settles the decade as *sessenta*: **born 20 August 1865, baptized 22 March 1866** (not the 1875/1876 a 7 Aug 2026 edit had produced by reading *setenta*). The 1875 reading was chronologically impossible — corroborated by PAR-0001 (marriage provisão, Dec 1882) and PAR-0006 (daughter Anna born 19 Nov 1884), which would have made her 7 and 9. Normalised across PAR-0005 (event_date, transcription, abstract EN/PT), events E-0035/E-0041, P-0020/P-0040/P-0041 (notes + profiles, the birth-year `[OPEN]` now resolved) and record-coverage; the day was also corrected from the older *onze* (11) to *vinte* (20). Reading history preserved.
- **P-0057 — forename Joaquim vs João.** Re-reading all five of his documents inverts the repository's prior choice: the clean, legible 1810 marriage (PAR-0023) reads **"Capitão Joaquim José Ferreira de Toledo"**, matching his own 1786 marriage (PAR-0018) and son's 1787 baptism (PAR-0019); "João José" appears only in the two *faded* daughters' marriages (PAR-0020 1812, PAR-0021 1816). Preferred name changed **João José → Joaquim José Ferreira de Toledo** (which also makes P-0057 consistent with the connected entities that already used Joaquim); "João José" kept as a source variant. Source records keep their as-recorded forms. Superseded choice preserved in the note.
- GEDCOM + viewer index regenerated (291 entities); 69 tests + 24 JS tests pass.

### Fixed — reconcile stale relationship notes to the settled lineage (2026-08-11)

- Writing the portraits surfaced pre-existing notes that still carried superseded readings and now contradicted the structured data. Corrected, with the superseded reading preserved (not erased):
  - **P-0054 / P-0055** notes (and their `record-coverage` entries) said Simplício José Ferreira Armond (P-0016) was JC × Claudina's son. Settled position (F-0026, P-0016, P-0017): **Eliza Balbina de Toledo (P-0017)** is their direct-line child; Simplício Armond is the son-in-law (parents unidentified); JC's own son "Simplício José Ferreira de Toledo" (14 in 1867) is a distinct person, a `documented_child` on F-0026. Removed the stale, internally-inconsistent Ahnentafel path `P-0001 → P-0004 → P-0016 → P-0054`; the line runs JC → Eliza (P-0017) → Aristão (P-0008) → Geraldo (P-0004).
  - **P-0064 / P-0065** notes called themselves "paternal grandfather/grandmother of P-0059"; PAR-0025 + F-0031 + P-0059's own note make them the **parents** of Alferes Amaro da Silva Xavier (P-0059) and grandparents of the 1777-baptised Maria.
  - **P-0027** `record-coverage` note: Mathilde is Eliza's paternal grandmother through JC (dropped the stale "grandmother of Simplício P-0016" clause).

### Changed — occupation audit: capture documented professions across the tree (2026-08-10)

- Audited every source's transcription against its linked people (three read-only agents over disjoint person-sets) and filled in occupations that a document states but that were not yet captured:
  - P-0011 Maria Aurora Guimarães → do lar (CIV-0018); P-0012 Deocleciano Muniz Bittencourt → lavrador (CIV-0006); P-0013 Luiza Fernandes de Azevedo → doméstica (CIV-0006); P-0015 Celina Bohrer → doméstica (CIV-0015); P-0029 Carolina Bohrer → doméstica (CIV-0014); P-0030 Joaquim José Bohrer → negociante (CIV-0019/0020); P-0042 Manoel Muniz Bytancourt → proprietário (PAR-0015); P-0048 João Muniz Bytancourt → proprietário (PAR-0015); P-0049 Maria Jacintha de Medeiros → doméstica (PAR-0015); P-0059 Amaro da Silva Xavier → Alferes (PAR-0023) + Capitão (PAR-0026).
  - P-0057 Capitão gained a second attestation (PAR-0023). P-0016's delegado occupation note removed (detail lives in his bilingual note).
- Rejected attribution traps (elder-Simplício "Juiz de Paz/Alferes" in GOV-0002/PUB-0002; land-possession vs. profession; illegible "[agricultora?]" for Iris left uncaptured per no-guess).
- GEDCOM regenerated (7.0, 3540 lines); viewer index regenerated (291 entities).

### Added — Simplício 1902 "delegado" press mention, attached to P-0016 (2026-08-10)

- **NWS-0003** (newspaper; O Pharol, Juiz de Fora, 13 Sept 1902): names Simplício José Ferreira Armond (P-0016) as 3rd substitute police delegate of São Paulo do Muriaé (act of 10 Sept 1902). Verbatim Portuguese transcription + bilingual (EN/PT) abstract.
- **P-0016** gains a structured `occupation` ("3.º supplente do delegado de polícia de São Paulo do Muriaé", source NWS-0003) and a bilingual note — a public role not previously recorded. **DOC-0076**.
- Applies the owner's rule: newspaper/image documents naming a person in the tree are transcribed and attached to that person, not skipped as "corroboration". The 1881 heir-list FS scan is a duplicate of PRB-0001 (already attached).
- GEDCOM regenerated (7.0, 3501 lines); viewer index regenerated (291 entities).

### Added — A Sentinella (Nova Friburgo) Bohrer/Lemos notices (2026-08-10)

- **NWS-0002** (newspaper; three A Sentinella clippings, 1898–1899): the death of Manoel Pereira de Lemos (20 Jan 1898, aged 72) — a new brother of Rosa Eugenia de Lemos (P-0035); the death of Antonio José Bohrer (2 Apr 1899, aged 13) — a son of Joaquim José Bohrer (P-0030); and Joaquim José's 16 December birthday.
- **F-0025** documented_child added: Manoel Pereira de Lemos. **F-0014** documented_child added: Antonio José Bohrer. Bilingual corroboration notes on **P-0030** (birthday 16 Dec; alive 1898–99) and **P-0035** (alive Jan 1898). **DOC-0075**.
- Value-gated the rest of a large Azorean-focused drop: the Terceira/São Sebastião Armond-Ermonde-Souto Maior trunk (`cal-*` register + Gaspar/Margarida crops + ASBRAP/Lacerda) recorded as unverified **leads**, explicitly NOT merged to our direct-line Simplício (P-0016); Brazilian Armond press classified FAN.
- GEDCOM regenerated (7.0, 3481 lines); viewer index regenerated (290 entities).

### Added — 1856 Fazenda da Concórdia land registry (2026-08-10)

- **GOV-0003** (government_record / original / primary / direct): 1856 Lei de Terras land registry, Curato do Rio Pardo, Município de Villa Leopoldina — entries Nº 144 (Francisco Leocádio de Toledo, P-0061) and Nº 145 (José Cesário de Toledo Lima, P-0054) for the Fazenda da Concórdia. Nº 145 confirms José Cesário alive in April 1856 and his mother (Mathilde, P-0027) then living.
- **E-0073** (residence, Fazenda da Concórdia, Apr 1856; principals P-0054 + P-0061); **DOC-0073**. P-0054 and P-0061 gained a GOV-0003 name-variant, E-0073, and a sourced note.
- Read but not promoted: 1885 tutela cover (low value); 1881 Ladisláo estate audiência (deferred pending two-Ladisláo file resolution).
- GEDCOM regenerated (7.0, 3416 lines); viewer index regenerated (288 entities).

### Added — Maternal Toledo/Valle line extended to 1700s Portugal (2026-08-10)

- **PAR-0034** (Arquivo da Arquidiocese de Mariana certidão): 22 Feb 1751 Borda do Campo marriage of João Rodrigues Valle × Isabel Ribeiro; derivative/primary/direct. Names both spouses' parents; corrects groom's origin to Ruivais, Braga, Portugal.
- **PAR-0035** (São Martinho de Ruivais, Braga, Portugal — original): baptism of João Rodrigues Valle, b. 15 Apr 1728. PRIMARY.
- **PAR-0036** (Ruivais — original): 13 May 1716 marriage of João Rodrigues × Joanna Gonçalves. PRIMARY.
- **P-0078** João Rodrigues Valle (b.15 Apr 1728 Ruivais, Portuguese), **P-0079** Isabel Ribeiro (Borda do Campo, Brazilian), **P-0080** João Rodrigues (Ruivais), **P-0081** Joanna Gonçalves (Ruivais); **F-0038** (P-0078 × P-0079, child P-0058), **F-0039** (P-0080 × P-0081, child P-0078); **E-0070/0071/0072**.
- **P-0058** (Ritta Angélica Rodrigues) updated: parents now modelled (F-0038); the PAR-0018 parent-lead is resolved. Child links strong-evidence; marriages/baptism confirmed.
- **DOC-0070–0072** added to document inventory. The 1716-named grandparents and Isabel Ribeiro's parents are recorded as leads, not modelled.
- GEDCOM regenerated (7.0, 3381 lines); viewer index regenerated (286 entities).

### Added — Lemos siblings: four baptism records promoted (2026-08-10)

- **PAR-0030** (Itaboraí 1832): PRIMARY baptism of Maria de Lemos (14 Jul 1832), daughter of Manoel de Lemos Ferreira × Maria Nunes de Jesus; sister of Rosa Eugenia de Lemos (P-0035).
- **PAR-0031** (Itaboraí 1834): PRIMARY baptism of Anna de Lemos (12 Feb 1834), same parents; godparents José Antonio + Anna Roza de Guimarães.
- **PAR-0032** (Itaboraí c.Jun 1836): PRIMARY baptism of Thomaz de Lemos (c. June 1836), mother recorded as "Maria Thereza de Jesus" (matching PAR-0016); godparents illegible.
- **PAR-0033** (Itaboraí c.Nov 1838): PRIMARY baptism of Polídoro de Lemos (c. November 1838); father Manoel de Lemos Ferreira confirmed; mother illegible (severe page damage). Date corrected from retrieval-agent initial read of "15 March 1838".
- **F-0025** documented_children updated: individual source IDs, corrected dates and godparents; mother-name discrepancy note added (scribal variant "Maria Nunes de Jesus" vs. preferred "Maria Thereza de Jesus").
- **P-0053** name_variants updated: "Maria Nunes de Jesus" added as source variant (PAR-0030/0031).
- **DOC-0063–0069** added to document inventory (backfills PAR-0027–0029 and adds PAR-0030–0033).
- GEDCOM regenerated (7.0, 3249 lines); viewer index regenerated (274 entities).

### Added — Bohrer Swiss parish primaries: three new generations confirmed (2026-08-09)

- **PAR-0027** (Grindel 1751–1753 Catholic baptism register): PRIMARY evidence for Johann Jacob Wehrli's (P-0072) birth on 17 January 1751 in Grindel. Parents confirmed as Johannes Wehrli (P-0074) and Barbara Alleman (P-0075). Also documents sibling Johann Joseph Wehrli (b. 23 June 1752, documented_child on F-0036).
- **PAR-0028** (Erschwil 1760 Catholic baptism register, church book #68): PRIMARY evidence for Elisabetha Borer's (P-0073) birth on 17 June 1760 in Erschwil. Parents confirmed as Joseph Borer (P-0076) and Anna Maria Borer (P-0077).
- **PAR-0029** (Grindel 1782 Catholic marriage register, page 71): PRIMARY image archived for the 27 January 1782 marriage of Johann Jacob Wehrli × Elisabetha Borer (ARK 3:1:3Q9M-CSVK-NSXR-C, FHC-restricted). Upgrades E-0065 and F-0035 from strong-evidence to confirmed.
- **P-0074** Johannes Wehrli (JJ Wehrli's father) and **P-0075** Barbara Alleman (JJ Wehrli's mother): new person entities, confirmed by PAR-0027. **F-0036** (Johannes × Barbara family entity).
- **P-0076** Joseph Borer (Elisabetha's father) and **P-0077** Anna Maria Borer (Elisabetha's mother): new person entities, confirmed by PAR-0028. **F-0037** (Joseph × Anna Maria family entity).
- **E-0068** (JJ Wehrli baptism event, 17 Jan 1751) and **E-0069** (Elisabetha Borer baptism event, 17 Jun 1760).
- F-0033 notes updated with internal PUB-0003 date conflicts (Vicente's ordinal 6th vs. 7th; Thereza's birth 1838 vs. 1836).
- GEDCOM regenerated (7.0, 3181 lines); viewer index regenerated (270 entities).

### Added — Bohrer/Borer line extended to 1819 Swiss immigrants (2026-08-08)

- **PUB-0003** (new source): Imigrantes de Nova Friburgo (Henrique Bon, compiler),
  pp.300-303 and Casa Suíça DB entries; category published_genealogy, strong-evidence
  for BORER I and BORER II genealogies.
- **P-0068 Laurent Borer** (b.27/02/1797, Grindel, Soleure, CH; Heureux Voyage 1819),
  **P-0069 Anna Maria Werhly** (b.~1793, Grindel), **F-0033** (Laurent × Anna Maria
  marriage 03/07/1820 NF); BORER II line grandparent generation of Valentim.
- **P-0070 Vicente Borer** (b.06/09/1828, NF, Brazil), **P-0071 Maria Heggendorn**
  (daughter of Joseph Heggendorn × Maria Freese), **F-0034** (Vicente × Maria
  marriage 11/04/1864); Valentim's parent family now modelled.
- **P-0072 Johann Jacob Wehrli** (b.17/01/1751, Grindel; d.NF 28/05/1827),
  **P-0073 Elisabetha Borer** (d.NF 10/10/1832), **F-0035** (married 27/01/1782,
  Grindel, confirmed by Swiss Catholic marriage register primary image); Anna Maria's
  parent family.
- **E-0060–E-0067**: birth and marriage events for Laurent, Anna Maria, Vicente,
  Maria Heggendorn (marriage), Valentim (birth), Johann Jacob × Elisabetha (marriage),
  Johann Jacob death, Elisabetha death.
- **P-0028 (Valentim)**: birth date confirmed (14/11/1868, E-0064), parent family
  F-0034 added; **P-0034 (Francisco José)**: exact death date (06/07/1888) and
  causa mortis (insuficiência mitral e dilatação aórtica) added from PUB-0003;
  **P-0050 (Jacob Bohrer)**: Casa/Lote 70/56 (distinct from Laurent's 73/86) added.
- GEDCOM regenerated (7.0, 3054 lines); viewer index regenerated (259 entities).

### Added — Mathilde death event, Armond leads, FL conflict flag (2026-08-08 fourth pass)

- **E-0059** (new): Mathilde Maria de Jesus death, 12 March 1879, confirmed from
  PRB-0006 folio 6 juramento; record-coverage for P-0027 death updated to `catalogued`.
- **P-0027**: added death date note (12 March 1879) and Capitão Manoel Rodrigues de
  Lima uncle relationship (from certidão pp. 154–155 of the inventário transcript);
  corroborates Ignez Francisca de Lima (P-0060) as Mathilde's mother.
- **Material conflict #15** flagged (STATUS.md, P-0061, F-0027): 1882 embargos judgment
  (p. 383) places Maria Joaquina as Ladisláo's daughter and Francisco Leocádio as
  son-in-law — contradicts PRB-0009-gen1 item 4. Image verification pending.
- **P-0016 record-coverage**: two critical Armond leads added from 2026-08-08 transcripts:
  "Ladislao Egidio [?Armonde]" signature (p. 150, 1873) and "[Philos?] José Ferreira
  Armond" as FL's daughter's husband (p. 258, 1880).
- **Test fix**: `test_relative_markdown_links_resolve` now skips `research/from-retrieval/`
  (gitignored retrieval-agent working area whose OCR transcripts contain link-like artifacts).
- GEDCOM regenerated (7.0, 2704 lines).

### Corrected — two-Simplícios error and CIV-0013 transcription (2026-08-07 third pass)

The second pass of 2026-08-07 introduced a systematic error by misidentifying
"Simplício José Ferreira de TOLEDO, solteiro, quatorze annos" (item 6 in the
1867 JC inventário, PRB-0008 p8) as our Simplício José Ferreira ARMOND (P-0016).
These are DIFFERENT people: JC's own son has the Toledo surname and died before
1879; P-0016 (Eliza's husband) has the Armond surname and is NOT JC's son. The
second pass propagated this error across seven files; the third pass reverses it.

**The correct, evidence-backed conclusion (restored this pass):**
Eliza Balbina de Toledo (P-0017) IS the daughter of José Cezário de Toledo Lima
(P-0054) × Claudina Brandina de Jesus (P-0055), family F-0026. Evidence: PRB-0006
(1879 Matilde inventário, Film 2 triage), which lists "5º Simplicio José Ferreira
Armond, cazado com D. Eliza Balbina de Tolledo" as representante #5 under heir #4
(JC × Claudina). Under 19th-century Brazilian inheritance law, a married woman
appeared through her husband as legal representative; Simplício is named first as
Eliza's legal actor — Eliza is the heir.

**CHANGELOG entries affected by this error** (from the second pass — now reversed):
- "PRB-0006 corrected: ...remove the misread that Eliza is JC's daughter..." (WRONG)
- "PRB-0008: PRIMARY source confirming Simplício (P-0016) as son of JC..." (WRONG)
- "PRB-0009: independently confirms Simplício as JC's representante..." (WRONG)
- "Data correction (F-0026, P-0016, P-0017): Simplício added as child, Eliza removed" (WRONG)

Files corrected this pass: `F-0026` (P-0017 reinstated as structured child, P-0016
removed), `P-0016` (F-0026 removed from family_ids), `P-0017` (F-0026 reinstated,
notes corrected), `PRB-0006` (abstract/notes corrected to affirm Eliza's parentage),
`PRB-0008` (title/notes corrected — item 6 = JC's son, NOT P-0016), `P-0061`
(Francisco Leocádio corrected — alive as herdeiro #2 in 1879; "falleceu antes da
morte" refers to his wife, not him), `F-0027` (Francisco Leocádio note corrected).

**CIV-0013 transcription corrected** from higher-quality image re-read: declarant
is "Silvio/Goistos Barrozo" (not "[Gustavo?] Barroso"); death time is 3:30 AM (not
1:30 PM); doctor is "Carlos Antonio Rodrigues" (not "Deslandes"); address is
"Rua Pres. de Azevedo 100" (not "[Paes de Azevedo]"); city Itaperuna confirmed.

**PRB-0009 (Ladisláo inventário) clarifications:** the p4 curator "Simplicio Jaci
Ferreira de Toledo" has the Toledo surname, not Armond — the prior identification of
this person as P-0016 is marked unconfirmed. Two-Simplícios note added to distinguish
JC's son (item 6, b.~1853, de Toledo surname) from P-0016 (Armond surname).

**P5b data noted** in PRB-0006 and F-0027: heir #5's representantes (Carolina
Leopoldina Marques's six named children) and heir #6 (Aureliano de Salles Tolledo ×
Marianna Euphragia de Tolledo) recorded. Conflict with F-0027 Aureliano note
("Marciana Espro[n?]de") flagged for re-check of PRB-0009.

### Added

- Catalogue **PAR-0025** (1777 original parish baptism, Minas do Piracatu, Manga
  parish, Bispado de Pernambuco) — the baptism of "Maria", daughter of Amaro da Silva
  Xavier (P-0059) × Ignez Francisca de Lima (P-0060). Primary source naming all four
  grandparents and extending the Toledo line to Portugal. New entities: `P-0064`
  (Amaro da Silva Barreto, Guimarães, Portugal), `P-0065` (Perpétua da Silva, São
  Paulo), `P-0066` (João Rodrigues de Mello, Viana, Portugal), `P-0067` (Maria
  Francisca Cordeira, Villa de Ouro), `F-0031` (Amaro Barreto × Perpétua), `F-0032`
  (João Rodrigues × Maria Francisca). DOC-0061 added.
- Catalogue **PAR-0026** (2019 ecclesiastical certidão of 1838 São José del-Rei
  baptism of Carolina, daughter of Cezário José da Silva Lima): corroborates Amaro ×
  Ignez parentage; adds Cezário as documented_child on F-0029. DOC-0062 added.

- Catalogue **CIV-0024** (certified death extract of António Ladislão de Toledo, died
  11 February 1909 at Fazenda da Concórdia, Thebes district, Leopoldina MG; Termo Nº 6,
  folhas 144–145). Death date **11 February 1909** (not 12th — declarant said "hontem").
  Names father Ladislao Igidio Ferreira de Toledo (`P-0056`) and mother "Mathilde Luiza
  de Toledo" (new name variant for `P-0027`; non-family informant's simplification of
  "Mathilde Maria de Jesus"). New entities: `P-0063` (António Ladislão de Toledo,
  Ladisláo × Mathilde child #7, "surdo e mudo"), `E-0058` (death event). DOC-0060
  added; `F-0027` updated (P-0063 moved from documented_children to structured children).
- **Confirm four Lemos siblings** from Itaborahy baptism images (7 August 2026 reads):
  Maria (b.1832), Anna (b.1834), Thomaz de Lemos Pereira (b.1836), Polidoro (b.1838),
  all with parents Manoel de Lemos Pereira × Maria Thereza de Jesus (`F-0025`). Added
  as documented_children on `F-0025`; individual source cataloguing pending.
- **Toledo direct ancestors** added to `data/record-coverage.yaml`: `P-0054` (José
  Cesário de Toledo Lima), `P-0055` (Claudina Brandina de Jesus), `P-0027` (Mathilde
  Maria de Jesus), `P-0056` (Ladisláo Egídio Ferreira de Toledo), `P-0057` (Capitão
  João José Ferreira de Toledo), `P-0058` (Ritta Angélica Rodrigues), `P-0059`
  (Alferes Amaro da Silva Xavier), `P-0060` (Ignez Francisca de Lima).

### Changed

- **PRB-0006 corrected:** Title, abstract, reliability and notes updated to remove the
  misread that Eliza Balbina de Toledo (P-0017) is a daughter of JC × Claudina. The
  transcription correctly reads item 5 as "Simplicio José Ferreira Armond, cazado com
  D. Eliza Balbina de Tolledo" — naming Eliza as Simplício's wife, not as a listed
  representante. Two independent 1867 inventários (PRB-0008, PRB-0009) list JC's
  children without Eliza, rejecting the daughter hypothesis.
- **PRB-0008 corrected:** Page count corrected from "nine" to "eight" (cover gen1,
  p2–p5, p8, p9). Page p6 was NOT catalogued — the previous `catalogue_reference`
  incorrectly included it. P6 is critical: it holds the year of JC's death (p5 breaks
  off after "dois de Setembro"). Limitations expanded to note pp 2–4 as catalogued
  but untranscribed. Simplício's middle name discrepancy (Jaci in PRB-0009 vs. José
  in PRB-0008) flagged in both records' limitations.
- **`P-0059` and `P-0060` updated:** F-0031 and F-0032 added to family_ids; notes
  updated with confirmed parents and Meia Ponte / Barbacena birthplace conflict.
- **`F-0029` updated:** PAR-0025 and PAR-0026 added to partner_relationship source_ids;
  "Maria" (PAR-0025) and "Cezário José da Silva Lima" (PAR-0026) added as
  documented_children.
- **PAR-0026 limitations expanded:** Added that the certidão issuance date and
  certifying archivist's name are not legible in the delivered image.

- **`E-0054` (JC death date):** Updated from `kind: before, text: 1867-03-04` to
  `kind: exact, value: 1866-09-02`. PRB-0008 p5 (Claudina's inventariante oath,
  7 March 1867) records her sworn declaration: "seu marido fallecera no dia dois de
  Setembro." Year 1866 contextually inferred (p6 not catalogued). PRB-0008
  transcription updated with p5 content.
- **P-0055 note corrected:** Claudina Brandina de Jesus was alive on 7 March 1867
  (physically present and taking the oath in PRB-0008 p5). Prior note stated she
  "died before 4 March 1867" — wrong. Death bounded to after 7 March 1867 and before
  1879 (PRB-0006).
- **PRB-0009 corrected:** The p2 text "é viúva, cuja [morte] falleceu depois do
  Inventariado" was misread as Claudina being deceased. Correct reading: JC (Claudina's
  husband) died after Ladisláo. PRB-0009 abstract, notes and limitations updated with
  pp 3–5 findings.
- **P-0027 (Mathilde) name variant added:** "Mathilde Luiza de Toledo" from CIV-0024
  (non-family informant's simplification). Signed the March 1867 proceedings in person
  noted in P-0027.
- **F-0027 (Ladisláo × Mathilde) children restructured:** Francisco Leocádio (P-0061)
  and António Ladislão (P-0063) both moved from documented_children to the structured
  children list, correcting a consistency gap where modelled entities remained as
  documented entries.
- **E-0055, E-0056, E-0057 retired** in `id-ledger.yaml`: pre-allocated IDs that were
  never used (JC's 1813 baptism illegible at delivered resolution; Barbacena 1812/1816
  marriage images were byte-identical duplicates of PAR-0020/PAR-0021).
- **PAR-0005 date corrected** (second re-read, 7 August 2026): Suzana Rita Brandão born
  20 August 1875, baptized 22 March 1876. Previous session had "11 August 1865, 22 March
  1866" — misread of "vinte" as "onze" and "setenta" as "sessenta." PAR-0005, E-0035,
  P-0020 corrected.
- **PRB-0009 (Ladisláo inventário) new entity added to children:** `P-0061` (Francisco
  Leocádio de Toledo) added to structured children list of `F-0027`; removed from
  documented_children.

- Catalogue **PRB-0008** (José Cesário de Toledo Lima × Claudina Brandina de Jesus
  inventário, 1867, Concórdia/Rio Pardo, MG; 8 pages; archive [38403 268]). **PRIMARY
  source confirming Simplício (P-0016) as son of JC × Claudina** — from p8, item 6:
  "Simplicio José Ferrara [Ferreira] de Tolledo, Solteiro de quatorze annos." Cover
  PRIMARY-CONFIRMS Claudina's full name "Claudina Brandina de Jesus". Event E-0054
  (JC death, before 4 March 1867) created.

- Catalogue **PRB-0009** (Ladisláo Egídio Ferreira de Toledo inventário, 1867,
  Concórdia/Rio Pardo, MG; 5 pages). Lists Ladisláo's 8 children; p2 independently
  confirms Simplício as JC's representante #6 (second primary source). New entities:
  P-0061 (Francisco Leocádio de Toledo — Ladisláo's child #4, predeceased), P-0062
  (Maria Joaquina de Jesus — uncertain name, Francisco's wife), F-0030 (couple family).
  Confirms JC (P-0054) as Ladisláo's child — upgrades F-0027 relationship to confirmed.

### Changed

- **Data correction (F-0026, P-0016, P-0017):** Eliza Balbina de Toledo (P-0017) was
  incorrectly placed as a daughter of José Cezário de Toledo Lima in F-0026, based on a
  misread of PRB-0006. PRB-0008 and PRB-0009 confirm Simplício (P-0016) is JC's son;
  Eliza is his wife. F-0026 corrected: Simplício added as child, Eliza removed.
  P-0017 family_ids updated; parentage now unresolved. New material conflict #14 added
  to STATUS.md. P-0054, P-0055, P-0056 notes updated.

- **PAR-0005 re-read confirmed** (no data change): the retrieval agent's re-download
  was byte-identical to existing evidence. Re-reading confirms the existing transcription
  (Suzana born 11 Aug 1865, baptized 22 March 1866, transcript presented 24 Nov 1882).

- Catalogue **PAR-0023** (Ladisláo Egídio Ferreira de Toledo × Mathilde Maria de
  Jesus marriage, 8 May 1810, São João del Rei; ARK 3:1:939N-GW99-VX). **PRIMARY
  source confirming Matilde's parents: Alferes Amaro da Silva Xavier (P-0059) ×
  Ignez Francisca de Lima (P-0060)** — the last open item on the Toledo apical
  couple. New entities: P-0059, P-0060, F-0029 (Amaro × Ignez family), E-0052
  (marriage event). Explains prior bounded-negative Barbacena sweep: couple married
  at SJdRei, not Barbacena.
- Catalogue **PAR-0024** (Manoel Muniz Byttancourt × Francisca Roza do Espírito
  Santo marriage, 1 Feb 1845, N.S. Mãe de Deus, Povoação, São Miguel;
  SMG-PV-MAEDEDEUS-C-1841-1854, folio 73r). Marriage confirmed; event **E-0053**
  created. Parents present but illegible at scan resolution. F-0020 updated.
- Catalogue **PRB-0007** (1862 traslado of Fazenda da Concórdia purchase deed, ARK
  3:1:3QHJ-RQWY-RZLV). Tightens Ladisláo's (P-0056) death bound from before 1877
  → **before 2 August 1862**.
- Catalogue **PAR-0022** (João Muniz Bittencourt's own 1845 baptism, N.S. Mãe de
  Deus, Povoação, São Miguel; DGS 5228858 img 63) and event **E-0051**. Birth year
  confirmed as 1845 (corrects c.1847 estimate). **Francisca Roza do Espirito Santo
  (P-0047) upgraded to confirmed mother** of João (P-0019) — first direct
  attestation; previously strong-evidence only. F-0020 parent relationships updated.

- Add a **dedicated mobile layout** to the family-tree viewer. Below 700px the
  horizontal pedigree is replaced by a phone-native **focus view**: one person
  centred at a time with tappable rows for parents, partners, children and siblings,
  a back stack and a jump-to-subject control, the nationality flag and
  relationship-to-subject inline, and a "Full details" button. Tapping a name
  re-centres the view, so the whole tree is walkable one screen at a time. Same data
  and i18n as the desktop tree (chosen at runtime by viewport, desktop pedigree
  untouched); the detail panel becomes a bottom sheet, inputs are 16px to stop iOS
  focus-zoom, and touch targets are enlarged. New keys `mobile.*` (en + pt-BR).
- Extend the **Muniz Bittencourt line two generations into the Açores** from Manoel
  Muniz Bytancourt's own 1866 Povoação (São Miguel) death (`PAR-0015`): it corrects
  João's father's name (Manoel **Muniz** Bytancourt `P-0042`, not the 1915 óbito's
  "Luiz"), names João's mother **Francisca Roza do Espirito Santo** (`P-0047`) and
  primary-confirms the Azorean grandparents **João Muniz Bytancourt** (`P-0048`) ⚭
  **Maria Jacintha de Medeiros** (`P-0049`, family `F-0023`) — **resolving material
  conflict 6**'s open mother. Adds Manoel's death and approximate-birth events
  (`E-0047`, `E-0048`) and reworks `F-0020` (Francisca added as spouse; João's
  maternal link strong-evidence).
- Name the **Bohrer immigrant boundary** from Francisco José Bohrer's own 1888 Nova
  Friburgo will (`PRB-0005`): parents **Jacob Bahrer** (`P-0050`) ⚭ **Catharina
  Mayer** (`P-0051`, family `F-0024`), and his declaration "natural deste termo" —
  so Francisco José (`P-0034`) is Brazilian-born and the immigrant generation is his
  parents (nationality set to Brazilian). The will confirms his four children
  (upgrading Joaquim `P-0030` to confirmed; Laura and Fernando added as documented
  children on `F-0016`) and names Rosa's brother Candido Pereira de Lemos (a Lemos
  lead). The primary "Bahrer/Mayer" spellings are kept; the secondary Swiss-Soleure
  "Borer/Moser" reading is recorded only as a variant/lead.
- Extend the **Bohrer maternal (Lemos) line one generation** from Rosa Eugenia de
  Lemos's own 1835 Itaboraí baptism (`PAR-0016`): parents **Manoel de Lemos Pereira**
  (`P-0052`) ⚭ **Maria Thereza de Jesus** (`P-0053`, family `F-0025`), both natural
  of Itaboraí (so Rosa is Brazilian-born). The register gives only the forename
  "Roza", so the identity is strong-evidence (unique couple/parish/date match,
  corroborated by the 1879 marriage venue and the will's Candido Pereira de Lemos,
  added as a documented sibling). Resolves the earlier "weakened" Lemos doubt — the
  apparent childbearing gap was an indexing artifact. Adds baptism event `E-0049`;
  Rosa (`P-0035`) updated with parents, event and the "Roza" variant.
- Extend the **maternal Toledo line three generations** and resolve `P-0027`
  (Mathilde)'s orphan status, from Mathilde Maria de Jesus's 1879 Leopoldina estate
  inventory (`PRB-0006`, folios 6/8/9). Eliza Balbina de Toledo (`P-0017`) is heir #4
  José Cezário de Toledo Lima's (`P-0054`) fifth representante, so her parents are
  **José Cezário de Toledo Lima × Claudina [Brandina de Jesus]** (`P-0055`, family
  `F-0026`) and her grandparents **Mathilde Maria de Jesus × Ladisláo Egydio Ferreira
  de Toledo** (`P-0056`, family `F-0027`). **Corrects** the `PRB-0004` hypothesis —
  Antonio Zeferino de Toledo × Maria Perpétua are heir #3 (Eliza's uncle/aunt), added
  as a documented sibling — and **resolves the two same-named Ladisláo** (elder =
  Mathilde's husband; the 23-year-old namesake = Eliza's brother). Eliza's seven
  siblings are recorded as documented children on `F-0026`; `P-0017`, `P-0027` and
  `PRB-0004` updated. Watch the near-identical inventariante Cezário José de Toledo
  (heir #7) vs heir #4 José Cezário de Toledo Lima — kept distinct.
- Extend the maternal Toledo line to **Barbacena** from a re-synced retrieval batch.
  The 1821 baptism of Carolina (`PAR-0017`) places **Ladisláo Egídio Ferreira de
  Toledo** (`P-0056`) × **Matilde** (`P-0027`) at Barbacena and corroborates the
  `F-0027` union; his parents are modelled as **Joaquim José Ferreira de Toledo**
  (`P-0057`) × **Ritta Angélica Rodrigues** (`P-0058`, family `F-0028`) from their
  legible c.1786 marriage (`PAR-0018`). The Ladisláo→Joaquim José edge is
  **strong-evidence, not confirmed** — the connecting 9 Sep 1787 baptism is ink-bled
  and only partly legible (flagged for a clean re-scan; since confirmed and the father
  re-read as João José — see below). Joaquim José's and Ritta's
  own parents (Gaspar Ferreira × Gertrudes Maria de Toledo of Vila Rica; João
  Rodrigues do Valle × Izabel Ribeira) are named in `PAR-0018` but kept as leads, not
  modelled. The direct line now reaches generation 8.
- **Confirm** the Ladisláo → Joaquim José × Ritta parentage edge (previously
  strong-evidence) from Ladisláo's own 9 September 1787 Barbacena baptism (`PAR-0019`,
  event `E-0050`). The base scan was illegible from ink bleed-through; the retrieval
  agent recovered the filiation by image processing (the `-alt` derivative), and the
  parents ("[Joaquim] José Ferreira de Toledo e de Dona Ritta Angelica Rodriguez") and
  the date read clearly on the recovery. Both the original and recovered scans are held
  (DOC-0052); `F-0028` and `P-0056` upgraded to confirmed.
- Corroborate the Toledo apical couple with two of Ladisláo's sisters' marriages —
  Anna Belizaria de Toledo (1812, `PAR-0020`) and Carolina Francelina de Toledo (1816,
  `PAR-0021`, "Capitão João José Ferreira de Toledo") — added as documented children on
  `F-0028`. Both clearer records give the father as **João José**, so `P-0057` is
  renamed from the ink-bled "Joaquim José" to **João José Ferreira de Toledo** (Capitão),
  the old form preserved as a source variant. Record the **bounded negative** for the
  Ladisláo × Matilde marriage (absent from the Barbacena Piedade books 1793-1822, read
  cover-to-cover): Matilde Maria de Jesus's (`P-0027`) own parents are now the single
  open item on that couple — she married in her home parish, still to be pinned.
- Catalogue the Santa Luzia de Carangola parish (religious) marriage cluster from the
  retrieval sync (3 sources). Deocleciano's 1916 parish marriage (`PAR-0012`) is the
  religious counterpart of the civil record (sourcing the same event `E-0001`); it
  primary-confirms Luiza's parents and **resolves material conflict 12** — her father is
  Secundino (Maria) de Azevedo, so the `CIV-0006` "Sebastião" reading was a misread. Two
  more sisters of Deocleciano are added as documented children on `F-0007`: Joventina
  (`PAR-0013`, m.1916) and Mercedes (`PAR-0014`, m.1917), both born in Carangola —
  dating the family's Sapucaia→Carangola move. Evidence `DOC-0043`–`DOC-0045`; Isaltino
  (1918) recorded as a collateral lead.
- Adopt the principle that a pre-civil-registration **parish baptism is the birth
  record** (same evidentiary level as a civil birth certificate): it establishes the
  birth date and birthplace, so create a birth event from it where the birth is not
  otherwise recorded (`research/README.md`, "Baptism as a birth record"). Apply it:
  add Susanna Rita Brandão's birth (`E-0041`, 11 Aug 1865, Sapucaia, from her baptism
  PAR-0005), and upgrade Deocleciano's birth (`E-0032`) from an age-inferred estimate
  to confirmed (June 1892, Sapucaia) now that his own baptism (PAR-0004) is in hand.
  Also add the approximate birth events the completeness checklist requires for the
  five óbito-documented ancestors (inferred from age at death): João (`E-0042`, ~1847,
  **Ilha de São Miguel** — structurally surfacing his Azorean birthplace), José do
  Rego Brandão (`E-0043`, ~1833), Rita (`E-0044`, ~1847), Antonio Caetano Machado
  (`E-0045`, ~1798) and Ignacia Maria de Jesus (`E-0046`, ~1813).
- Catalogue the Sapucaia/Carangola death registers from the retrieval sync (5 óbito
  sources). João Muniz Bittencourt's 1915 death (`PAR-0007`) records him "natural da
  Ilha de São Miguel" (Açores) — **resolving material conflict 6**: he was the Azorean
  immigrant (nationality Portuguese) and it names his father Manoel Luiz Bittencourt
  (`P-0042`, family `F-0020`). The maternal Brandão/Machado deaths extend those lines
  two generations: José do Rego Brandão's 1912 death (`PAR-0008`) names his parents
  (`P-0043`/`P-0044`, `F-0021`); Rita's 1898 death (`PAR-0009`); Antonio Caetano
  Machado's 1868 death (`PAR-0010`, resolving the "Castro/Caetano" reading to Caetano)
  and Ignacia Maria de Jesus's 1878 death (`PAR-0011`, Rita's probable mother; couple
  `F-0022`). Adds 5 ancestors, 3 families, 5 death events (`E-0036`–`E-0040`) and
  evidence `DOC-0038`–`DOC-0042`. Damazio Muniz Bitencourt (a probable São-Miguel-born
  brother of João), a "José Armond" in Carangola, and an Azevedo-infant record are
  recorded as leads.
- Occupations completeness pass from evidence already in hand: add attested
  professions to the direct-line principals — Geraldo Paz Armond *padeiro*
  (CIV-0002, alongside the existing *aposentado*), Antonio Engracio Filho
  *negociante* (CIV-0017), and João Gonçalves Bohrer *lavrador* (CIV-0016, 1924) →
  *comerciante* (CIV-0014, 1970). Each is attributed to the record's own subject
  (the "industriário" in CIV-0014 is the declarant, deliberately excluded), and
  the 1831 Curral Novo census (GOV-0002, `context_only`) is deliberately NOT used
  for P-0016 — it names the elder Barbacena namesake, not this Simplício.
- Catalogue a new Santo Antônio de Sapucaia (RJ) parish cluster from the retrieval
  sync: Deocleciano Muniz Bittencourt's own 1892 baptism (`PAR-0004`), Susanna Rita
  Brandão's 1866 baptism (`PAR-0005`), and Anna Muniz Bittencourt's 1885 baptism
  (`PAR-0006`). Adds Susanna's parents José do Rego Brandão (`P-0040`) and Rita
  Ignacia de Jesus (`P-0041`) as new ancestors with family `F-0019`; baptism events
  `E-0034`/`E-0035`; Anna as a documented sibling of Deocleciano on `F-0007`; and
  upgrades Deocleciano's parentage to confirmed (settling the father's name as
  "João"). Evidence `DOC-0035`–`DOC-0037`. Collateral Muniz Bittencourt couples and
  a non-Muniz "Antônio Firmino Bittencourt" namesake family recorded as leads.
- Add a GEDCOM exporter (`scripts/export_gedcom.py`, `make export` /
  `make export-bundle` / `make export-legacy`) rendering the canonical YAML to a
  portable genealogy file in **GEDCOM 7.0 by default** (the current standard) or
  **5.5.1** (`--gedcom-version`, widest commercial-site import). It is a **full
  backup**, no redaction: people, families, events, citations, living people in
  full, transcriptions, `OBJE` records referencing the `evidence/` scans, and
  `rejected` edges flagged (`QUAY 0`, never as fact). Hypotheses are included and
  flagged (`QUAY 1`); attested `documented_children` become standard synthetic
  `INDI` + `CHIL` nodes (export-only `@DOC…@` xrefs, no person entity minted).
  `make export-bundle` writes a **GEDZIP** (`.gdz`) packaging the GEDCOM plus the
  scan files. The `.ged` is committed as an in-repo backup; `.gdz` bundles and the
  5.5.1 file are gitignored. Adds `tests/test_export_gedcom.py`.
- Add an optional `sex` field (`male` / `female` / `unknown`) to the person schema
  and template, populated on all 39 people, so the export can set `INDI.SEX` and
  assign a family's `HUSB` / `WIFE`. Derived from each person's cited vital records
  and documented spousal or parental role, never from a name.
- Catalogue two records from the retrieval sync: Cidália's own 1930 birth
  registration (`CIV-0022`, Alvorada) and a third Armond daughter — Aristides
  Ferreira Armand's 1894 marriage to João Rodrigues Braga (`CIV-0023`, Boa Família,
  Muriaé). Cidália's birth confirms her date, parents and all four grandparents;
  Aristides is added as a documented child of Simplício × Eliza (F-0006), a sister
  of Aristão and Marfiza, giving a fourth attestation of Simplício's signed name and
  Eliza's "Elisa Balbina de Jesus" variant. Adds DOC-0033/DOC-0034 and strong
  Simplício-line locality leads (Boa Família/Muriaé 1894; Rio Pardo/Argirita ~1875).
- Add the missing ancestor birth events from records already in hand, so the
  grandparents' and great-grandparents' viewer cards show their dates: Geraldo
  (E-0029, 30 Jan 1915, Rosário da Limeira MG) and Cidalia (E-0030, 15 Sep 1930,
  Alvorada MG) from their 1952 marriage (CIV-0002); and approximate births inferred
  from ages for Aristão (E-0031, c.1879), Deocleciano (E-0032, c.1892, Sapucaia RJ)
  and Luiza (E-0033, c.1898, Muriaé MG). Applies the person-completeness rule
  consistently (as already done for P-0010/P-0014/P-0015).
- Catalogue Liliosa Paz Armond's death (event `E-0028`, 16 April 1946, Eugenópolis)
  from a clearer view of the Geraldo × Cidalia 1952 marriage (CIV-0002), resolving
  the long-open Liliosa death-date gap (material conflict 2) and recording her
  Eugenópolis birthplace; her parents remain the next target (Eugenópolis óbito).
- Ingest Aristides Muniz Bittencourt's 1922 Carangola baptism (`PAR-0003`) from the
  retrieval drop: adds Aristides as a documented child (Antenor's brother) on
  F-0001, establishes Luiza's parents as new ancestors — José Secundino de Azevedo
  (P-0038) and Thereza Fernandes de Azevedo (P-0039), family F-0018 — corroborated
  by CIV-0001, adds Luiza's "Secundina" name variant, and fixes the family's
  Carangola (MG) origin. Plus DOC-0032.
- Record two owner-confirmed documented collaterals: Marfiza Ferreira Armond
  (1873–1962), Aristão's sister, on F-0006 from her 1962 civil death (CIV-0013);
  and Eunir Bohrer (b.1924), Iris's brother, on F-0005 from his 1924 birth
  (CIV-0016). Both now appear in the viewer's Siblings/Children.
- Record Maria Aurora Guimarães's five siblings — José (1901), Maria da Conceição
  (1906), Sebastião (1909), João José (1912) and Maria de Lourdes (1915) — as
  `documented_children` on F-0008 from the same 1915 collective registration
  (CIV-0007) that documents her. A completeness gap found while validating the
  Siblings/Children feature; they now populate her Siblings and her parents'
  Children. Also clarified the Francisco José × Rosa marriage event (E-0026):
  "1879" is only the justificação (upper bound) date — the wedding was decades
  earlier, since their son was already a father by 1890.
- Add a **Children** section to the viewer, mirroring Siblings: a person's
  children — modelled `P-` children plus the family's `documented_children`, with
  possibly-living ones omitted — computed from the families where the person is a
  partner, shown as bullets below Marriages & partners. Reuses the existing
  `documented_children` field (no new data or schema change). Covered by a
  data-loader unit test and en/pt-BR strings.
- Add a **Siblings** section to the family-tree viewer, shown below Parents in a
  person's detail. Siblings are drawn from a new optional `documented_children`
  list on the family schema — attested collateral children (each with
  `source_ids`) that are deliberately not modelled as their own person entities —
  together with any deceased modelled children of the same parents.
  Possibly-living siblings are omitted entirely. Populated for the Bohrer line:
  Celina's sibling Alberto (CIV-0019) and Joaquim José's brother Guilherme Samuel
  (CIV-0019). Covered by a new data-loader unit test and en/pt-BR strings.
- Extend the Bohrer maternal line to Celina's grandparents from three retrieval-drop
  records: Alberto Bohrer's 1890 birth (`CIV-0019`), an 1891 sibling birth
  (`CIV-0020`), and Francisco José Bohrer × Rosa Eugenia de Lemos's 1879 marriage
  (`PAR-0002`, a parish record). Adds four ancestors (P-0034–P-0037), families
  F-0016/F-0017, marriage event E-0026, and DOC-0029–DOC-0031. The grandparent
  links are strong-evidence; Celina's own parentage confidence is unchanged. See
  `logs/2026-07-30-bohrer-maternal-line-extension.md`.
- Catalogue two Engracio-line civil deaths from the retrieval drop: Antonio
  Engracio Filho's 1964 death (`CIV-0017`) and Maria Aurora Guimarães's 1991
  death (`CIV-0018`). Adds death/birth events for P-0010, a death event for
  P-0011, new ancestors P-0032/P-0033 (Cidalia's paternal grandparents) with
  family F-0015, a marriage attestation on F-0012, and DOC-0027/DOC-0028. See
  `logs/2026-07-30-engracio-deaths-ingest.md`.

### Changed

- Codify the "do your work" retrieval-drop cycle in AGENTS.md: orient from
  `FINDINGS.md` + the triage ledger + the CSV before opening images, diff the drop,
  value-gate each new image (leads-not-evidence, privacy, parish-vs-civil, and the
  AI-generated FS-tree-portrait caution), ingest with reciprocal back-references,
  finish with the completion protocol, and end by reviewing the agent's plans and
  FINDINGS to give feedback.
- Resolve material conflict 1: Cidália's own birth registration (CIV-0022) fixes her
  birth at 15 September 1930, superseding the "15 November" variant. Upgraded her
  birth event (E-0030) and her parentage in F-0012 to **confirmed** (direct primary
  from her own birth record).
- Correct and complete CIV-0002 from a clearer alternate view: Cidalia's father is
  named "Antônio Engrácio de Souza" (correcting the earlier obscured "Antonio
  Engracio Filho" reading) with an exact birth 15 June 1894 — refining P-0010's
  birth event E-0024 — and Maria Aurora's birth is confirmed as 1 January 1904.
  P-0010 keeps both name forms ("Filho" distinguishes him from his father P-0032).
- Complete CIV-0006's transcription from the newly synced inteiro-teor images (the
  1916 marriage act was previously "pending, low contrast") and link CIV-0001 to
  Luiza's now-modelled parents (P-0038/P-0039, F-0018).
- Set P-0016's preferred name to "Simplício José Ferreira Armond" (owner-confirmed
  full name) — it matches his autograph signature (PRB-0002) and the two 1880s
  Leopoldina probate records; the shorter source forms "Simplicio Armand" (CIV-0005)
  and "Simplício Ferreira Armond" (CIV-0013) stay as variants. Coverage note and
  the inventory identity label updated to match.
- Transcription deep-dive: verified every source transcription against the images
  where available and confirmed each aligns with the structured entities. Fixed two
  alignment gaps it surfaced — recorded the probate name forms "Simplicio José
  Ferreira Armond" (P-0016, from PRB-0001/PRB-0002, one bearing his autograph
  signature) and "Eliza Balbina de Toledo" (P-0017, from PRB-0001), and added a
  birth event (E-0027) for P-0018 José Olavo Armond (25 Sep 1926, Eugenópolis; per
  GOV-0001 and NWS-0001). Confirmed João Gonçalves Bohrer's death date (CIV-0014,
  3 Aug 1970) and Celina's Nova Friburgo origin (CIV-0016) directly from the images.
- Remove the mistaken "Infant son (1891–1892)" documented child from F-0014: a
  re-read of CIV-0020 shows the child's given name is on an unretained next folio,
  so it was a placeholder, not a record fact (kept as a noted, pending record).
- Mark P-0018 (José Olavo Armond, a granduncle) deceased, per the owner's
  confirmation that everyone from his grandparents' generation back is deceased.
- Record the owner-confirmed fuller name variants "Simplício Ferreira Armond"
  (P-0016) and "Eliza Ferreira Toledo" (P-0017) from CIV-0013, resolving the
  earlier lead caveat; preferred names unchanged pending a decision on the fuller
  forms.
- Document the `documented_children` mechanism in the governance docs: a new bullet
  in AGENTS.md's "Entity connectivity and completeness" protocol and an extension
  to the `data/README.md` person-completeness checklist. Both state that an
  attested collateral child needing no research of its own is recorded as a family
  `documented_children` entry (name + required `source_ids`, deceased only) rather
  than a full person entity, and that the viewer's Siblings and Children sections
  are built from a family's modelled children plus these entries.
- Audit every person for the Selina/Celina class of error (a preferred name less
  supported by primary records than an available variant). Found and fixed one
  analog: P-0011's preferred name changes from "Maria Amora" to "Maria Aurora" —
  three sources including her own 1991 death (CIV-0018) use "Aurora" against a
  single retrospective, certified-copy birth registration (CIV-0007) with the
  unusual "Amora". Also backed P-0027's preferred spelling "Mathilde" with its own
  source variants (PRB-0004/PRB-0002) and documented P-0018's reconstructed
  spelling ("CLAVO" is a misprint for "OLAVO"). No other under-sourced preferred
  name remains.
- Change P-0015's preferred name from "Selina" to "Celina". Three primary civil
  records spell it "Celina" — her own 1977 death (CIV-0015), her husband's 1970
  death (CIV-0014) and Eunir's 1924 birth (CIV-0016) — versus "Selina" only in the
  1949 marriage certificate (CIV-0004) and the owner's family roster (REC-0001).
  "Selina" is preserved as a documented variant; the change is recorded in the
  person's notes.
- Resolve material conflict 10: Maria Amora Guimarães (1904 birth, CIV-0007) and
  Maria Aurora Guimarães (1991 death, CIV-0018) are the same woman — both records
  name identical parents. Both name forms preserved; preferred name kept as Maria
  Amora.

### Removed

- Remove superseded research working files — the old `research/resources/` and
  `research/sources/` caches and `research/PLAN-close-simplicio-gap.md` (replaced by
  the `research/from-retrieval/` workflow) — and a redundant alternate scan of
  CIV-0005 (`evidence/references/…-recapture-spread.pdf`). CIV-0005's note is
  updated: that two-page spread was reviewed and confirmed entry 9890 but is not
  retained (the evidence model keeps one authoritative image per record).

### Fixed

- Repair and de-drift the GitHub Pages deploy (`.github/workflows/static.yml`). The
  inline build had gone stale against the viewer and would deploy a site that fails
  to load: it did not copy `i18n.js` (an `app.js` import), did not build the `fan`
  dataset (the loader hard-errors on the missing index key), wrote sources flat while
  the loader fetches them by category subfolder, and dropped the person `nationality`
  / `sex` / `occupations` fields (breaking flags and biographies). Replaced it with a
  dynamic, testable `scripts/build_pages_site.py` that copies the whole viewer
  directory, publishes deceased people verbatim (living reduced to a private stub),
  builds every entity kind, and writes sources into their category subfolders — so it
  stays in step with the viewer automatically. Sources and FAN references remain
  privacy-reduced (no transcriptions, repositories or scans published). `_site` is
  gitignored.
- Publish **deceased people's evidence on the public site** (owner directive): a
  source or FAN record about only deceased people is now deployed verbatim with its
  scan, so its card links the document image and shows the transcription. Records
  involving any living person (the owner's own birth/marriage documents) stay
  reduced — no scan, transcription or link — and their scans are never copied into
  the site (verified: CIV-0008–0012 withheld). `evidenceHref` resolves against a new
  `EVIDENCE_ROOT` that the build rewrites to the site root.
- Restore the P-0021/P-0022 → E-0007 back-links: both parents (Francisco José de
  Carvalho Guimarães and Emmerenciana Maria de Jesus) participate in their child
  P-0011's 1904 birth (E-0007) but had omitted it from their `event_ids`. This
  was the only person↔event reciprocity gap; a full connectivity and completeness
  audit (person↔family, person↔event, person↔FAN, orphan, nationality and
  vital-event coverage) found no other structural defect. See
  `logs/2026-07-30-connectivity-completeness-audit.md`.
- Document that P-0019 (João Monis Bittencourt) carries no `nationality` by
  design — his origin (an unproved Azorean lead versus Brazilian jus soli) is
  unresolved — tying the omission to material conflict 6 rather than leaving the
  field silently blank.

### Changed

- Codify an "Entity connectivity and completeness" protocol in `AGENTS.md` (both
  ends of every family/event/FAN link kept in step; catalogued records reach the
  viewer via events, not prose; deliberate omissions noted) and add a completion
  step to verify reciprocity and completeness beyond `make check`, so the class
  of gap fixed in E-0007 is caught before completion.
- Reflow the viewer toolbar to a flex layout so it accommodates the language
  selector cleanly: all six controls bottom-align on one row, the search field
  absorbs the slack, and Reset stays content-sized (adding the selector had
  pushed Reset onto a full-width second row under the 5-column grid).
- Widen the viewer's header, toolbar and summary to the full width of the tree
  box: raise `--shell-max` to the tree's 150rem cap and align the header/main/
  footer side padding to the tree's 1.5rem margins, so the controls and
  repository tiles line up with the tree instead of sitting in a narrower centred
  column.
- Name FAN reference images by ID only (`FAN-NNNN.<ext>`), dropping the
  descriptive suffix; the date, place, record type and role stay in the FAN
  record. Applies to `evidence/references/` (the FAN folder); the source-folder
  naming convention is unchanged.
- Rename the external record-retrieval workflow throughout the repository to
  "retrieval agent" terminology: the drop folder is now `research/from-retrieval/`,
  alongside the value-gate resume ledger, the 30 July read-pass research log, and
  the prose in `AGENTS.md`, `STATUS.md`, `.gitignore`, `research/README.md` and
  the affected `data/` records. Terminology and paths only; no genealogical data,
  conclusion or evidence changed. The external agent's own config must point at
  the new folder for the rename to persist across syncs.
- Ignore the entire retrieval drop directory `research/from-retrieval/` in one
  rule (previously only `output/`, `README.md` and `resources/` were listed),
  now also covering the `correspondence/` and `plans/` folders, `people.txt` and
  `FINDINGS.md`. The whole area is regenerable working data, not history; valuable
  finds are promoted into `data/`, `evidence/` or `logs/` via the value gate.

### Removed

- Remove the unused `evidence/incoming/` staging folder and its README. Nothing
  was ever staged there: owner-supplied scans are reserved an ID and written
  directly into `evidence/<category>/`, and retrieval-agent images promote from
  `research/from-retrieval/` through the value gate. Residual references in
  `README.md` and the full-text-references README were updated.

### Added

- Create the missing birth and death events for the Bohrer couple so their
  lifespans and events display: E-0019 (João Gonçalves Bohrer death, Volta
  Redonda 1970) and E-0020 (birth c.1894, Rio de Janeiro), E-0021 (Celina Bohrer
  death, Volta Redonda 1977) and E-0022 (birth c.1900, Nova Friburgo) — dates
  taken from the death ages, places from the records. They had catalogued deaths
  but no event, so the viewer showed "Dates not established".
- Add a person-completeness checklist to `data/README.md` (populate name,
  privacy, nationality, name variants, birth+death events with places, family
  links, occupations and notes on every person create/update) so vital events
  and other fields are not missed again.
- Add a `nationality` field to the person schema and surface it in the viewer:
  each card now shows, below the name, the lifespan, the birthplace and the
  nationality, and the details overview gains a Nationality row. Nationality is
  populated evidence-based — Brazilian by Brazilian birth, Portuguese for Vicente
  José de Carvalho Guimarães (CIV-0007) — and left unset for João Muniz
  Bittencourt (P-0019), whose nationality is genuinely contested. Covered by
  `tests/js/data_loader.test.mjs`.
- Extend the maternal Bohrer line two generations from three primary Rio de
  Janeiro civil records (retrieval sync): catalogue João Gonçalves Bohrer's 1970
  Volta Redonda death (CIV-0014), Celina/Selina Bohrer's 1977 death (CIV-0015)
  and Eunir Bohrer's 1924 Nova Friburgo birth (CIV-0016); add Iris's grandparent
  generation — Valentim Martinho Bohrer + Carolina Bohrer (P-0028/P-0029, F-0013)
  and Joaquim José Bohrer + Lucinda Ferreira da Silva (P-0030/P-0031, F-0014) —
  and link P-0014/P-0015 as their children (strong-evidence). Fix Celina's origin
  to Nova Friburgo (resolving the São Leopoldo RS namesake) and record the
  civil-registered "Celina" variant. Inventory DOC-0024–0026. Two modern sibling
  death records were reviewed but withheld (collateral + living-person data).
- Add an English / Brazilian-Portuguese (pt-BR) dual-language UI to the
  family-tree viewer. A new dependency-free `family-tree-viewer/i18n.js`
  translates the chrome and controlled-vocabulary labels (event types, statuses,
  privacy); a language selector defaults to the browser language (falling back to
  English), persists the choice in `localStorage`, and encodes it in the URL hash.
  Record content (names, transcriptions, places, record types) is never
  translated. Covered by `tests/js/i18n.test.mjs`.
- Surface FAN references and source transcriptions in the family-tree viewer.
  `data-loader.js` now loads the `fan` entities and projects them per person via
  `participants`; the details panel lists each person's FAN / context references
  (role, record category, place, transcription and image link) and shows each
  source's transcription and abstract. Covered by new `tests/js/data_loader.test.mjs`
  assertions.
- Catalogue the Muriaé/Leopoldina Full-Text FAN set as FAN entities FAN-0002–
  FAN-0013 — third-party probate/notarial records where Simplício José Ferreira
  Armond (P-0016) or Aristão Ferreira Armond (P-0008) appear only in a functional
  role (creditor, witness, appraiser/louvado, attorney, party, co-owner) — each
  with a transcription and a person link. Flatten the images into
  `evidence/references/` under `FAN-NNNN-…` names, fix FAN-0001's path, remove the
  `armond-muriae-fulltext-probates/` subfolder, and preserve the Full-Text
  candidate list as `logs/2026-07-29-fulltext-muriae-leopoldina-candidates.csv`.
  Codify the references-folder rule (one catalogued FAN entity per flat,
  `FAN-NNNN`-named image) in `evidence/README.md` and `evidence/references/README.md`.
- Catalogue two Barbacena-context sources from the retrieval resources cache
  via the value gate: PUB-0002 (Antônio Henrique Duarte Lacerda's 2010 UFF
  doctoral thesis on the Ferreira Armonde family; published_genealogy,
  lead_only) and GOV-0002 (the 1831 Curral Novo population list; census,
  context_only — a Projeto Compartilhar transcription of the APM manuscript).
  Both linked to P-0016 with evidence PDFs and inventory entries DOC-0022 and
  DOC-0023. They put the anti-merge (the Barbacena Gen-2 Simplício died
  celibate) on catalogued sources without asserting the unproven bridge to this
  line.
- Complete a full per-image read pass of the `research/from-retrieval/`
  drop and catalogue PRB-0004 (a Toledo Concórdia / Ribeirão de São Bento deed
  naming Eliza's maternal grandparents Mathilde × Ladisláo Egydio Ferreira de
  Toledo and the parent couple Antonio Zeferino de Toledo × Maria Perpétua), with
  evidence image and document-inventory entry DOC-0021. Record the resulting
  hypothesis (Antonio Zeferino × Maria Perpétua as Eliza's parents) and the
  two-Ladisláo conflict without creating unverified edges; flag a Moura-family
  "Mathilde Maria de Jesus" namesake to avoid conflation.
- Gitignore the retrieval-agent working area (`research/from-retrieval/output/`,
  `research/from-retrieval/README.md`, `research/from-retrieval/resources/` and the
  local `from-retrieval-triage-ledger.md`) as regenerable, non-history working data.
- Define the initial YAML entity model and JSON Schemas for people, families,
  events, places and sources.
- Add entity and research templates, evidence-handling guidance and the initial
  document-cataloguing plan.
- Add an ID allocation ledger and automated validation for schemas, references,
  evidence quality, privacy, duplicate identities and parent-child chronology.
- Document the local workflow, implementation roadmap and policies for derived
  timelines and exports.
- Establish permanent research principles and a cumulative research log, and
  record that the source documents are absent from the worktree and Git history.
- Consolidate repository governance, remove obsolete foundation and placeholder
  documentation, and allow empty entity directories to remain untracked.
- Add a versioned document-inventory schema and validation for file integrity,
  privacy review, duplicate handling and source-allocation state.
- Version every structured entity and replace the overloaded evidence class
  with separate record category, source form, information quality and evidence
  type fields.
- Model each parent-child assertion as a separately typed and cited edge, and
  constrain event participant roles with explicit exceptional-role details.
- Split the validator into focused model, inventory, reference and genealogical
  rule modules while preserving its command-line and imported interfaces.
- Replace stored next-ID counters with derived allocation and add atomic,
  recoverable entity reservation and draft generation with dry-run support.
- Add staged validation and recoverable batch promotion for mutually dependent
  entity drafts, including rollback and interrupted-transaction recovery.
- Add a least-privilege, concurrency-cancelled GitHub Actions matrix that runs
  the frozen local repository check with pinned action and tool versions.
- Consolidate the older duplicate remote validation workflow into the canonical
  pinned, multi-version repository-health workflow.
- Consolidate project scope and operating principles into `README.md`, current
  state and planning into `STATUS.md`, and research policy and history under
  `research/`; add checks for root-document ownership and broken local Markdown
  links.
- Remove the duplicate document-cataloguing plan after retaining its unique
  source-processing order in `STATUS.md`; keep research policy, inventory and
  reproducible history as separate canonical artifacts.
- Audit the original ChatGPT genealogy conversation against the repository,
  preserve previously omitted leads and superseded interpretations without
  promoting them, and identify its 24 unavailable image attachments as the
  primary transfer gap; downgrade Aristão's proposed parentage to `hypothesis`
  because collaborative-tree support alone cannot establish `strong-evidence`.
- Recover and catalogue the first authorised record from FamilySearch
  Memories: the certified 1916 marriage of Deocleciano Muniz Bittencourt and
  Luiza Fernandes de Azevedo; add its private reconstructed image, inventory
  provenance, checksum and six directly required linked entities.
- Fix prospective entity promotion so the default command-line workflow uses
  the repository schemas, and cover the previously untested path.
- Recover and catalogue three alternate photographs of the damaged 1952
  marriage certificate of Geraldo Paz Armond and Cidalia Engracio Guimarães as
  one source; add its private evidence files, inventory provenance, retained
  birth-date conflict and six directly required linked entities.
- Consolidate `CIV-0002` to the clearest photograph under one canonical
  filename; keep the two omitted alternate views recoverable in Git history and
  preserve their FamilySearch provenance in the research record.
- Migrate the initial person block to Ahnentafel order, add privacy-minimised
  roster records for direct-ancestor positions 1–15, remap all existing
  references, and document that the identifiers remain immutable after this
  low-cost migration.
- Recover and catalogue Geraldo Paz Armond's original 1991 civil death
  registration; preserve the FamilySearch archival citation, private
  reconstructed register image, record-number conflict and source-qualified
  parentage of Aristão Ferreira Armond and Liliosa Paz Armond.
- Review the data model against three real records: distinguish reported
  co-parents from sourced partners, enforce inventory-to-source file checksum
  consistency, and add a validated missing-record coverage ledger for deceased
  direct ancestors.
- Recover and catalogue the 1949 marriage certificate of Antenor Muniz and
  Iris Bohrer; add its private reconstructed image, source-qualified marriage,
  married-name form and reported parent-child relationships.
- Audit Liliosa Paz Armond's FamilySearch Sources and Memories; document that
  the attached source is only her mention in Geraldo's 1991 death record, reject
  a 1975 newspaper PDF as her death evidence, and restore the conflicting 1946
  death dates to unresolved lead status.
- Recover and catalogue Aristão Ferreira Armond's original 1957 civil death
  registration; confirm his death, preserve the malformed FamilySearch index,
  and add source-qualified strong-evidence parentage for Simplicio Armand and
  Eliza Ferreira Armand without promoting unproved fuller name forms.
- Record the unsuccessful indexed and full-text search for Aristão's birth and
  marriage, identify São Sebastião de Leopoldina baptism image group
  `004640627` Item 3 as the bounded 1879 manual-review target, and exclude the
  marriage series ending in July 1897 as probably too early for the target
  marriage.
- Redesign `AGENTS.md` as a stable context-loading, decision and completion
  protocol that routes agents to canonical live state and task-specific
  contracts without duplicating volatile research context.
- Consolidate `STATUS.md` into a present-only operational snapshot, move
  historical ownership back to the existing canonical logs and structured
  records, clarify the policy boundary with `AGENTS.md`, and add a regression
  test against renewed status-file accumulation.
- Add a required, short and ordered `Next steps` section to `STATUS.md`,
  separating the visible tactical handoff from the detailed coverage ledger
  and longer-term strategic priorities.
- Add a concise root README entry point linking directly to the current
  objective, next-step queue, agent instructions and research-history index.
- Map Aristão Ferreira Armond's restricted baptism and marriage register
  targets, document the exhausted searchable layers, mark both coverage rows
  inaccessible, and advance the current objective to the direct-line
  FamilySearch Memories audit.
- Require highest-authorised-resolution evidence retention, record acquisition
  and resolution status with encoded pixel dimensions, and validate PNG/JPEG
  dimensions while rejecting catalogued lower-resolution working copies.
- Audit all known direct-line FamilySearch Memories in Ahnentafel order,
  identify shared and non-record artifacts, document a living-person visibility
  risk, and catalogue the three-page 2019 full-content Deocleciano–Luiza
  marriage certificate as `CIV-0006`.
- Replace five viewer-tile reconstructions with authorised original-file or
  original-image JPEG downloads, increasing retained resolution by up to
  sixteen times in pixel area while keeping superseded files recoverable in Git
  history.
- Record the unsuccessful exact, variant and bounded-register search for
  Liliosa Paz Armond's own 1946 death or burial, preserve both date leads, and
  document the January–October gap in the accessible Volta Redonda series.
- Catalogue the full-resolution March 1973 Guanabara driver-dossier index as
  `GOV-0001`, preserve its printed "Aristac" name variant, and add José Olavo
  Armond as a source-qualified strong-evidence child of Aristão and Liliosa.
- Recover and catalogue the original 1882 marriage provision for João Monis
  Bittencourt and Susanna Rita Brondão as `PAR-0001`; distinguish the issued
  authorisation from a completed ceremony, preserve the FamilySearch `1633`
  index defect, and identify the Espírito Santo parish as the next register
  target.
- Complete the corresponding ceremony-book access review: document the absence
  of a separately exposed Espírito Santo parish film series, verify from the
  Archdiocese's historical record that its chapel was the parish seat in 1882,
  and specify the exact Cúria Metropolitana request without treating the
  provision date as a completed marriage.
- Recover and catalogue the 1915 Carvalho Guimarães collective birth
  registration as `CIV-0007`; retain its authorised original-upload file,
  structure six direct ancestors, three parent groups and the reported events
  and places, preserve the Maria Amora/Aurora conflict, and keep Vicente's
  Portuguese origin at nationality level until a parish is documented.
- Preserve and catalogue six unique original PDFs from the living repository
  subject's private FamilySearch Memories as `CIV-0008` through `PUB-0001`;
  deduplicate two byte-identical birth uploads without losing provenance,
  separate four distinct manifestations of one marriage, and retain the
  Chagas dissertation as a secondary Armond research lead rather than proof of
  lineage or Azorean origin.
- Redesign the static family-tree viewer with a heritage-archival theme
  (parchment, forest green and gold, serif display, framed register cards and
  rounded-elbow lineage connectors), replace the placeholder monogram with a
  family-tree seal emblem and matching favicon, and vendor `js-yaml` locally so
  the viewer makes no external network requests and works fully offline.
- Extend the viewer to present couples with per-family marriage markers, link
  each non-private evidence file and external record from the detail panel
  while surfacing source form, quality and reliability limitations, add
  auto-fit zoom with manual controls and drag-to-pan, widen the tree canvas,
  and encode a bookmarkable view in the URL hash; keep living-person data
  minimised throughout.
- Cover the viewer's read-only data projection with Node unit tests run through
  `make check`, guard `entity-index.json` against drift from the canonical data
  directories, restore focus to the invoking card when the detail panel closes,
  and copy the vendored parser and favicon into the privacy-filtered GitHub
  Pages build.
- Audit the direct-line vital records against their document images and correct
  the source transcriptions: fix Geraldo Paz Armond's death entry number from a
  misread 39005 to 39006 (39005 is the unrelated infant on the facing page) and
  add its cause of death, registration date and son-declarant; add the cause of
  death, time and declarant to Aristão Ferreira Armond's death entry; and record
  the civil-register citation (livro A-350, folha 98) printed on Juan Carlos
  Muniz Armond's birth certificate.
- Recover Antenor Muniz's (2 November 1923, Alvorada) and Iris Bohrer's
  (27 February 1929, Presidente Soares) birth facts stated as secondary
  information in their 1949 marriage certificate, which the source had wrongly
  called illegible; structure them as events E-0017 and E-0018 with the new
  place PL-0009 and note them against both coverage rows.
- Record a resolvable FamilySearch profile URL for every collaborative-tree
  lead in the record-coverage ledger, extending the coverage schema with an
  optional lead-only `url` field.
- Allow a certified copy of an official record (derivative source form with
  direct primary information) to support a `confirmed` conclusion, alongside
  original records; family recollection and collaborative trees still cannot
  confirm. Update the confidence-status policy and validator accordingly, and
  promote Juan Carlos Muniz Armond's parentage to `confirmed` on his certified
  birth certificate corroborated by his Ontario marriage record.
- Correct the 1882 marriage provision (PAR-0001): re-reading the register shows
  the couple's provision was directed to the Santo Antônio de Sapucaia parish,
  not the Espírito Santo parish (that wording belongs to the adjacent José
  Pereira Mendes entry). Repoint place PL-0005, event E-0006 and the coverage
  search target to Sapucaia, preserving the superseded interpretation, and
  refresh the STATUS snapshot counts.
- Promote to `confirmed` the events directly attested by a certified or
  original official record now that certified copies may confirm: the 1916,
  1952 and 1949 marriages (E-0001, E-0002, E-0004), the 1882 provision issuance
  (E-0006) and Maria Amora Guimarães's 1904 birth (E-0007). Parentage reported
  in another record, and births reported in a marriage record, remain
  strong-evidence.
- Add `research/familysearch-image-targets.md`, an autonomous-agent task-spec
  for retrieving restricted record images, and an `evidence/incoming/` staging
  area for un-catalogued downloads. Record the online gap-and-resource research
  session, fold the discovered resources into the coverage ledger, and update
  place PL-0009's present-day equivalence to Alto Jequitibá, MG (from IBGE
  administrative history) without changing the source-recorded birthplace.
- Unify the agent-governance documentation on `AGENTS.md` as the single source
  of truth for both Claude Code and Codex, and document the assistant/Codex
  research split. Refresh `README.md` (family-tree viewer, `CLAUDE.md` loader
  and updated layout) and give `STATUS.md` a currency pass: reprioritise the
  current objective to the now-unblocked Aristão baptism and Aristão×Liliosa
  marriage retrieval, trim the per-source list in favour of the canonical
  `data/sources/`, and record the viewer and certified-copy confirmation rule
  in the engineering state.
- Run four parallel read-only research passes (Liliosa vital records, the
  Ferreira Armond bridge, Vicente's Portuguese origin and the Sapucaia marriage)
  and fold the leads into the coverage ledger, the Codex image-retrieval
  worksheet and a dated session log without changing any conclusion: reframe
  Liliosa's 1946 death to the Barra Mansa index, place the Aristão×Liliosa
  marriage in Piacatuba/Leopoldina, identify the Simplício×Elisa marriage as the
  decisive (still unproven) Ferreira Armond bridge with the b.1784 Simplício
  doubly documented as unmarried, fix Vicente's parish as Santa Luzia do
  Carangola (mother parish Tombos), and separate the Sapucaia provision from the
  completed ceremony assento by custody. Record the Portugal/Azores
  custody-and-access workflow (100-year rule, free DigitArq/GEA images) in
  `research/README.md`.
- Add an optional, source-qualified `occupations` field to the person schema
  (each occupation cites the source that records it), enabling profession and
  wealth analysis. The recursive reference and living-person privacy checks
  cover its `source_ids` automatically; no validator change was needed.
- Preserve key research-reference documents in `research/resources/` with a
  provenance manifest: the ASBRAP "Armond, Por Quê?" article, the 1831 Curral
  Novo census transcription, the Lacerda 2010 (UFF) thesis, the Chagas 2018
  (UFMG) dissertation and a snapshot of the Senra blog — all leads about the
  historical Barbacena Ferreira Armonde family, not this line's proven ancestry.
  Record the deep-dig session (five parallel agents plus the 1831 census).
- Preserve two further Projeto Compartilhar documents in `research/resources/`
  (the 1831 João Gomes census — a married Manoel Antonio de Armond household —
  and the 1751 will/inventory of the patriarch), and add
  `logs/correspondence-log.md` recording outreach to Mauro Senra, Nilza
  Cantoni and the Piacatuba parish about the Simplício × Elisa marriage.
- Survey the owner-supplied source sites (a full Projeto Compartilhar crawl, the
  My Portuguese Gen Azores directory, and the Scribd Forjaz & Mendes "Genealogias
  da Ilha Terceira") and consolidate the leads: record the survey session log;
  add a per-locality FamilySearch catalog-ID map and an Iris Bohrer 1929-birth
  target to the retrieval worksheet; note the married Manoel Antonio de Armond
  (João Gomes 1831) as a candidate later-namesake and reaffirm, from the 1831
  census (a primary source), that the documented Armonde tree does not reach
  Piacatuba. No conclusion changed.
- Populate the new `occupations` field from held-source transcriptions for six
  deceased direct-line people: Aristão Ferreira Armond (padeiro, CIV-0005),
  Antenor Muniz (da lavoura, CIV-0004), Cidalia Engracio Guimarães (doméstica,
  CIV-0002), Geraldo Paz Armond (aposentado, stated at death, CIV-0003), and
  Francisco José de Carvalho Guimarães and Emmerenciana Maria de Jesus
  (lavradores, CIV-0007). Each occupation cites the record that states it.
- Show each person's occupations in the family-tree viewer's detail panel (a new
  source-cited "Occupation" section, minimised for living people), aggregate an
  occupation's cited sources into the person's source list, and cover the
  projection with a data-loader unit test.
- Record the owner-supplied Armond documents (Aristão's 1957 death = CIV-0005;
  Marfiza Ferreira Armond's 1962 death; José Olavo's 1975 marriage bann in O
  Processo): Marfiza is confirmed as Aristão's sister by a second primary record
  of the parents Simplício Ferreira Armond + Elisa Toledo (giving Elisa's maiden
  surname Toledo), and José Olavo's "natural de Eugenópolis" fixes the family's
  locus as Eugenópolis, MG — redirecting the Aristão×Liliosa marriage and the
  children's-birth search there, not Leopoldina. No conclusion promoted; the
  Azorean bridge stays unproven; formal source cataloguing pending the files.
- Stage the owner-supplied source files in `evidence/incoming/` (the O Processo
  newspaper, the Aristão 1957 death re-capture, and the Marfiza 1962 death image)
  for cataloguing, and record Nilza Cantoni's email reply in the correspondence
  log: the Simplício × Elisa couple likely lived in Dores do Monte Alegre (now
  Taruaçu), served by the Argirita/Piacatuba parishes; Piacatuba marriage book 1
  (1851-55, 1862-65) is a documented negative; and Elisa's Toledo family is rooted
  in Argirita (father an eleitor 1863-64; land registry 1856) — redirecting the
  Simplício × Elisa marriage and Elisa-origin search to Argirita/Taruaçu.
- Record 16 FamilySearch Full-Text hits for Aristão and Simplício Ferreira
  Armond in the Muriaé/Leopoldina probate records (staged in
  `evidence/references/armond-muriae-fulltext-probates/` with a candidates CSV):
  an 1881 Leopoldina probate documents "Simplício José Ferreira Armond casado com
  D. Eliza Balbina de Toledo" and lists Elisa's Toledo siblings and parent's
  estate; Simplício ("Capitão") and Aristão recur across the comarca's probate/
  property records. Folded into P-0016, P-0017 and P-0008. No conclusion
  promoted; formal per-source cataloguing to follow; the Azorean bridge stays
  unproven.
- Catalogue the two subject probate records from the Full-Text batch as sources:
  `PRB-0001` (1881 Leopoldina heir list naming Eliza Balbina de Toledo as wife of
  Simplício José Ferreira Armond, with her Toledo siblings) and `PRB-0002` (1884
  Leopoldina petition of Simplício as heir of the late D. Mathilde Maria de
  Jezus). Both are court_or_probate originals, linked to P-0016 and P-0017, with
  their images moved to a new `evidence/probate/` category and inventoried as
  DOC-0016/DOC-0017. The 1881 estate opens Elisa's maternal ancestry (decedent
  Mathilde Maria de Jezus); the remaining 13 Full-Text hits stay staged as FAN
  references. Simplício's own parentage is still not found.
- Catalogue the 1975 marriage bann of José Olavo Armond in the newspaper
  *O Processo* (Conselheiro Lafaiete, MG; Ano II, n.º 42, 1–15 February 1975) as
  `NWS-0001` (record_category `newspaper`), inventoried as DOC-0018 with the
  issue PDF filed under a new `evidence/newspapers/` category. It independently
  confirms José Olavo's parents (Aristão Ferreira Armond and Liliosa Paz Armond)
  and records his birthplace as Eugenópolis; P-0018 gains a name variant and the
  occupation "representante comercial".
- Catalogue the 1962 civil death registration of Marfiza Ferreira Armond as
  `CIV-0013` (owner-supplied register image, entry n.º 18892, watermarked "SEM
  VALOR LEGAL"; DOC-0019). It names her parents as Simplício Ferreira Armond and
  Eliza Ferreira Toledo — a second primary record giving Eliza the Toledo
  surname and documenting Marfiza (b. ~1873, aged 89) as a sister of Aristão.
- Add a FAN (Friends / Associates / Neighbours) reference entity type
  (`data/fan/`, `FAN-NNNN`, `schemas/fan.schema.json`) for third-party records
  where a family member appears only in a functional role, plus the first entity
  `FAN-0001` (an 1875 Muriaé procuração signed by Simplício José Ferreira
  Armond). People gain an optional `fan_references` back-link list.
- Catalogue the 1877 Leopoldina Toledo deed of sale (`PRB-0003`, two pages,
  promoted from the `research/from-retrieval/` sync via the value gate) and add
  `P-0027` Mathilde Maria de Jesus. Its clause "sua finada avó Dona Mathildes
  Maria de Jesus" (Fazenda da Concórdia) fixes Mathilde as the *grandmother* of
  Eliza Balbina de Toledo's (P-0017) Toledo grandchild set, resolving the
  mother-vs-grandmother question flagged on PRB-0001; the intervening parent
  (Eliza's) remains undocumented.

### Changed

- Restructure sources into category-prefixed entity kinds. Sources move to
  `data/sources/<category>/` with immutable category-prefixed IDs (`CIV`, `GOV`,
  `PAR`, `PRB`, `NWS`, `PUB`, `REC`) replacing the flat `SRC-NNNN` space, and
  their evidence files carry the same prefix. The validator resolves `source_ids`
  against the union of the seven source kinds, the viewer maps each prefix back
  to its folder, and `common.schema.json`, the ID ledger, per-category templates
  and the AGENTS/data/schemas/evidence docs are updated to match. IDs are
  immutable once assigned; adding a category follows a documented pattern
  (`data/README.md`). This supersedes the former "never renumber" rule only for
  this one-time re-scheme.
- Standardise evidence filenames and folders: rename the two probate images to
  the `SRC-<id>-<record-type>-<subject>-<year>-original` convention; relocate the
  13 FAN probate images from `evidence/incoming/` (staging) to a permanent
  `evidence/references/armond-muriae-fulltext-probates/`; and document in
  `evidence/README.md` that evidence categories reflect the record's origin (not
  the event) and that `references/` holds retained FAN/context images.
- Clear `evidence/incoming/`: an owner-supplied alternate scan of Aristão's 1957
  death entry (watermarked "SEM VALOR LEGAL") is a redundant recapture of the
  already-catalogued CIV-0005, so it is kept as a working reference under
  `evidence/references/` (not re-inventoried, since one authoritative image is
  kept per record) and noted in CIV-0005.
- Tighten `AGENTS.md` so the source-record (`data/sources/`) versus binary-scan
  (`evidence/`) two-layer split, the category-prefix scheme, and the
  FAN-versus-source decision are stated explicitly as non-negotiable format
  rules (imported into Claude via `CLAUDE.md`).
- Move all research history to a top-level `logs/` directory (a sibling of
  `research/`): the dated session logs, the `LOG.md` index and the
  `correspondence-log.md` now live there together, and every reference and
  internal markdown link is repointed.
- Move the validated control ledgers `document-inventory.yaml` and
  `record-coverage.yaml` from `research/` to `data/` (joining `id-ledger.yaml`),
  since they are settled, schema-validated structured data rather than research
  notes. Repoint the validator paths, test fixtures and docs. `research/` now
  holds policy, worksheets, entity drafts and reference resources.

### Fixed

- Show a person's own life events only in the viewer. The timeline projection
  attached each event to every participant, so a death that merely named a
  person as a parent (e.g. Geraldo Paz Armond's 1991 death naming Aristão
  Ferreira Armond) surfaced as that person's own death. Events now land on a
  person's timeline only when their role is the subject — principal, or
  spouse/partner in a marriage; a referenced role (parent, witness) still
  contributes the event's sources but no longer a spurious event. Regression
  test added.
