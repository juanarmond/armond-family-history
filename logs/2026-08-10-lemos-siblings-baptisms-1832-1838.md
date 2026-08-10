# Session log — 2026-08-10: Lemos siblings baptism promotions (PAR-0030–0033)

**Objective:** Value-gate the four rec-lemos-*-baptism-*-itaborai.jpg images from the retrieval
drop and promote confirmed sibling records for the Lemos family of Itaboraí (F-0025).

---

## Research question

Can the 1832–1838 Itaboraí baptism register entries for siblings of Rosa Eugenia de Lemos
(P-0035) be confirmed as direct primary evidence, and promoted as individual sources?

---

## Images read (direct primary reads)

All four images are from FamilySearch DGS film 004620557 (cc=1719212), Livro de batismos,
Itaboraí 1832–1838, signed by Vigário Francisco Ramos Pena. Volume noted as "em mau estado /
páginas rasgadas" (poor condition, torn pages).

### rec-lemos-maria-baptism-1832-itaborai.jpg → PAR-0030

**Record:** Baptism of "Maria", 14 July 1832, Matriz de São João Batista de Itaborahy.
**Parents:** Manoel de Lemos [Ferreira] × Maria Nunes [de Jesus].
**Godfather:** [Felício?] José Custódio Vieira.
**Assessment:** Direct primary evidence. Father's surname "de Lemos" confirmed; mother
recorded as "Maria Nunes de Jesus" (differs from "Maria Thereza de Jesus" in PAR-0016/0032
— scribal inconsistency, same person).

### rec-lemos-anna-baptism-1834-itaborai.jpg → PAR-0031

**Record:** Baptism of "Anna", 12 February 1834, Matriz de São João Batista de Itaborahy.
**Parents:** Manoel de Lemos Ferreira × Maria Nunes de Jesus.
**Godparents:** José Antonio + Anna Roza de Guimarães.
**Assessment:** Direct primary evidence. Both parent names clearly legible; exact date
"doze dias do mês de Fevereiro" confirmed (corrects retrieval-agent read of "11 February").

Also visible on this page: a baptism of "José", son of Castro Guimarães × Leonora Maria
Correa de Oliveira, whose paternal grandparents were from Vizela de Brito, Bispado de Braga,
Portugal — separate family, no action required.

### rec-lemos-thomaz-baptism-1836-itaborai.jpg → PAR-0032

**Record:** Baptism of "Thomas", c. June 1836, Matriz de São João Batista de Itaborahy.
**Parents:** Manoel de Lemos × Maria Thereza [de Jesus].
**Godparents:** illegible (page damaged).
**Assessment:** Direct primary evidence. Month "Junho" confirmed; exact day illegible.
Mother recorded as "Maria Thereza" here — matching PAR-0016 (1835) and contrasting with
the "Maria Nunes" of PAR-0030/0031.

### rec-lemos-polidoro-baptism-1838-itaborai.jpg → PAR-0033

**Record:** Baptism of "Polídoro", c. November 1838, Matriz de São João Batista de Itaborahy.
**Father:** Manoel de Lemos Ferreira (legible); **mother:** name damaged and illegible.
**Godparents:** illegible.
**Assessment:** Direct primary evidence for the father; mother not recoverable from this image.
Month November inferred from surrounding entries. Page severely damaged.

**Date correction:** Retrieval agent's initial read was "approximately 15 March 1838".
Direct image read confirms ~November 1838, not March. F-0025 and PAR-0033 corrected.

---

## Evidence classification

All four records:
- Classification: **source** (primary evidence directly about F-0025 family members)
- `source_form: original`
- `information_quality: primary`
- `evidence_type: direct`
- `usage: evidence`
- `private: true` (19th-century Brazilians; no living-person exposure)

---

## Files created / updated

**New sources:** PAR-0030, PAR-0031, PAR-0032, PAR-0033 (data/sources/parish/)
**New scans:** evidence/parish/PAR-0030 through PAR-0033 (copied from retrieval drop)
**F-0025:** documented_children updated — source IDs corrected from PAR-0016 placeholder to
individual records; dates, godparents, and child names corrected; mother-name discrepancy note added.
**P-0053:** name_variants updated — "Maria Nunes de Jesus" added as source variant (PAR-0030/0031);
"Maria Thereza de Jesus" variant updated to include PAR-0032.
**PAR-0030 schema fix:** event_date changed from year/month/day fields to `value: "1832-07-14"`
(same fix applied to PAR-0031).
**Document inventory:** DOC-0063 through DOC-0069 added (PAR-0027–0033; PAR-0027–0029 had been
promoted in commit b855373 without inventory entries).
**Viewer index:** regenerated (274 entities, includes new sources).
**GEDCOM:** regenerated (3249 lines).

---

## Mother-name discrepancy (P-0053)

Vigário Francisco Ramos Pena recorded the same woman inconsistently:
- "Maria Nunes de Jesus" — 1832 (Maria) and 1834 (Anna) baptisms
- "Maria Thereza de Jesus" — 1835 (Rosa/PAR-0016) and 1836 (Thomaz) baptisms

Preferred form: "Maria Thereza de Jesus" (from PAR-0016, the most genealogically central
record). "Maria Nunes de Jesus" preserved as a source variant on P-0053.

---

## Searches performed

No new searches: these images were already retrieved by the external FamilySearch agent.
This session constitutes value-gate reads only.

---

## Next steps

1. Complete value-gate triage of remaining ~210 images (parallel agents in progress).
2. Aristão Ferreira Armond baptism (priority objective in STATUS.md): not yet located.
3. Aristão × Liliosa marriage record: not yet located.
