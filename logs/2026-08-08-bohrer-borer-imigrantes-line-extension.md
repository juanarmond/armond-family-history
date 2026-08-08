# Session log — Bohrer/Borer line extension via Imigrantes de Nova Friburgo (2026-08-08)

**Session type:** Retrieval drop processing — value gate on 2026-08-07 Bohrer image set  
**Date:** 2026-08-08  
**Images processed:** 17 images in `research/from-retrieval/output/images/rec-bohrer-*.jpg`  
**Receipt consulted:** `research/from-retrieval/output/receipts/bohrer-images-deep-read-2026-08-07.md`

---

## 1. Source created

**PUB-0003** — Imigrantes de Nova Friburgo (Henrique Bon, compiler), pp.300–303 and Casa Suíça DB entries.  
Category: `published_genealogy`; quality: secondary; usage: evidence.  
Images read: pages 300–303 (BORER I and BORER II trees), plus Casa Suíça DB screenshots for Laurent, Vicente, Anna Maria Wehrli, and Johann Jacob Wehrli.  
Also read: Swiss Catholic marriage register, Grindel parish, page 71 (entry 4 — Wehrli × Borer marriage, 27 January 1782). Image `rec-bohrer-werly-borer-marriages-grindel-1780.jpg` in retrieval area; needs to be archived as a PAR source.

---

## 2. People created

| ID | Name | Dates | Status |
|---|---|---|---|
| P-0068 | Laurent Borer | b. 27/02/1797 Grindel, Soleure, CH; d. unknown (NF area) | strong-evidence (PUB-0003) |
| P-0069 | Anna Maria Werhly | b. ~1793 Grindel; d. unknown | strong-evidence (PUB-0003) |
| P-0070 | Vicente Borer | b. 06/09/1828 NF, Brazil; d. unknown | strong-evidence (PUB-0003) |
| P-0071 | Maria Heggendorn | b. unknown; parents Joseph Heggendorn × Maria Freese | strong-evidence (PUB-0003) |
| P-0072 | Johann Jacob Wehrli | b. 17/01/1751 Grindel; d. NF 28/05/1827 | strong-evidence (PUB-0003) |
| P-0073 | Elisabetha Borer | b. unknown; d. NF 10/10/1832 | strong-evidence (PUB-0003) |

---

## 3. Families created

| ID | Partners | Notes |
|---|---|---|
| F-0033 | Laurent Borer (P-0068) × Anna Maria Werhly (P-0069) | 11–12 children documented; structured child: Vicente (P-0070) |
| F-0034 | Vicente Borer (P-0070) × Maria Heggendorn (P-0071) | Marriage 11/04/1864; structured child: Valentim (P-0028) |
| F-0035 | Johann Jacob Wehrli (P-0072) × Elisabetha Borer (P-0073) | Marriage 27/01/1782 Grindel (Swiss parish register, PRIMARY); structured child: Anna Maria (P-0069) |

---

## 4. Events created

| ID | Type | Date | Participants | Status |
|---|---|---|---|---|
| E-0060 | birth | 1797-02-27 | Laurent Borer (P-0068) | strong-evidence |
| E-0061 | marriage | 1820-07-03 | Laurent × Anna Maria | strong-evidence |
| E-0062 | birth | 1828-09-06 | Vicente Borer (P-0070) | strong-evidence |
| E-0063 | marriage | 1864-04-11 | Vicente × Maria Heggendorn | strong-evidence |
| E-0064 | birth | 1868-11-14 | Valentim Martinho Bohrer (P-0028) | strong-evidence |
| E-0065 | marriage | 1782-01-27 | Johann Jacob × Elisabetha (Grindel) | strong-evidence |
| E-0066 | death | 1827-05-28 | Johann Jacob Wehrli (P-0072) | strong-evidence |
| E-0067 | death | 1832-10-10 | Elisabetha Borer (P-0073) | strong-evidence |

---

## 5. Existing entities updated

- **P-0028 (Valentim):** added E-0064 to event_ids; added F-0034 to family_ids; added note on birth confirmation.
- **P-0034 (Francisco José Bohrer):** added exact death date (06/07/1888), causa mortis (insuficiência mitral e dilatação aórtica), and siblings from PUB-0003.
- **P-0050 (Jacob Bohrer):** updated notes to reflect PUB-0003 was directly read (not just a lead); confirmed Casa/Lote 70/56 (distinct from Laurent's 73/86).
- **record-coverage.yaml:** updated P-0014 (João Gonçalves) Bohrer-line note to reflect the line now reaches Laurent (1819 immigrant).
- **STATUS.md:** counts updated; Bohrer research snapshot updated.

---

## 6. Key findings and caveats

**BORER I vs BORER II distinction confirmed:** Jacob Borer (P-0050, BORER I, Erschwil, Casa/Lote 70/56) and Laurent Borer (P-0068, BORER II, Grindel, Casa/Lote 73/86) are distinct families sharing the Borer surname; both came on the Heureux Voyage 1819 but the compilation explicitly states no proven close kinship. Valentim (and thus João Gonçalves and Iris) descends from BORER II via Vicente.

**Vicente's middle name "Lourenço":** the compilation gives only "Vicente Borer" — no middle name. "Lourenço" appears only in blog/collaborative-tree sources and is NOT confirmed by PUB-0003. Recorded as unconfirmed in P-0070 notes.

**Maria Heggendorn's full name:** the compilation confirms only "Maria Heggendorn." The names "Thecla Regina" and birth date "23 Nov 1844" appear only in blog/collaborative-tree sources; NOT confirmed by PUB-0003. Recorded as unconfirmed in P-0071 notes.

**Swiss register primary image (E-0065):** the Grindel marriage register (27 Jan 1782) was read directly by the retrieval agent (image `rec-bohrer-werly-borer-marriages-grindel-1780.jpg`). The event status is `strong-evidence` rather than `confirmed` because the source_ids currently list only PUB-0003 (the compilation); the primary image is in the retrieval area and needs to be archived as a PAR source before the status can be upgraded to `confirmed`.

**Joaquim José Bohrer absent from Imigrantes compilation:** the compilation's BORER I list for Francisco José's children shows only Ludovina, Laura, Guilherme, Fernando. Joaquim José (P-0030), the firstborn per PRB-0005 will, is absent — the compiler likely missed his NF baptism. PRB-0005 remains authoritative.

**Antonio da Silva Ferreira's parents (Justino × Maria Angélica, Portugal):** blog-confirmed in the family-bohrer.md plan but NOT confirmed by any image read in this session. Recorded as a blog-level lead only; no entity created.

**Carolina Bohrer's maiden name (Klein):** blog-only lead. Not confirmed by any record. P-0029 still has no source-confirmed maiden name.

---

## 7. Pending actions

- Archive the Grindel marriage register image as a PAR source and upgrade E-0065 to `confirmed`.
- Locate Valentim's NF parish baptism at Fundação D. João VI (pre-1874 registers, NF).
- Locate Joaquim José Bohrer's NF baptism (absent from Imigrantes compilation).
- Catalogue Lemos sibling baptism images (Maria b.1832, Anna b.1834, Thomaz b.1836, Polidoro b.1838) — images held, sources not yet catalogued.
- Verify Antonio da Silva Ferreira's parents (Justino × Maria Angélica) from primary records.
