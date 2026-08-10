# Session log — 2026-08-10: Maternal Toledo/Valle line extended to 1700s Portugal

**Objective:** Value-gate the Toledo deep-ancestry images in the retrieval drop and, where
evidence supports it, extend the maternal Toledo line above Ritta Angélica Rodrigues (P-0058).

---

## Research question

Ritta Angélica Rodrigues (P-0058), wife of Joaquim José Ferreira de Toledo (P-0057), is named
in her own c.1786 marriage (PAR-0018) as "filha legitima de João Rodrigues [do Valle] e de
Izabel Ribeira, natural da Freguesia da Borda do Campo" — with those parents flagged as an
unmodelled lead. Can that couple, and their ancestry, be documented from the drop?

---

## Images read (direct reads; agent-2 classification was a lead only)

Agent 2 (parallel classification pass) flagged many Toledo images "PROMOTE" but with a high
false-positive rate (see triage ledger). Each was verified against the catalogue and image.

### rec-toledo-isabel-ribeiro-doc-02-gen4.jpg → PAR-0034 (promoted)

Modern certidão from the **Arquivo Eclesiástico da Arquidiocese de Mariana** transcribing the
**22 February 1751** marriage at the **Matriz de N.S. da Piedade da Borda do Campo (Barbacena)**
of **João Rodrigues Valle × Isabel Ribeiro** (Livro de Casamentos de Barbacena 1737-1751, Livro
D 10, pp. 234/234v). Names groom's parents João Rodrigues × Joanna Gonçalves and bride's parents
Manoel Nado Pestana × Anna Francisca. Marginal correction: the groom was **not** native to Borda
do Campo but **"de Ruvans [Ruivais] do Arcebispado de Braga"** (Portugal). Fully legible (typed
certidão).

### rec-toledo-joaorodrigues-valle-baptism-fstree.jpg → PAR-0035 (promoted)

Genuine archival scan (fólio 93) of the **São Martinho de Ruivais (Braga, Portugal)** baptism
register: **João, legitimate son of João Rodrigues [Valle] × Joana Gonçalves, born 15 April 1728,
baptized 16 April 1728** by Padre Domingos [Pereira] de Valle. This is João Rodrigues Valle
himself; corroborates the 1751 certidão's Portuguese-origin correction.

### rec-toledo-joaorodrigues-marriage-barbacena-fstree.jpg → PAR-0036 (promoted)

Genuine archival scan of the **Ruivais** marriage register: **13 May 1716 marriage of João
Rodrigues** (son of Gonçalo Rodrigues †, Elebia Francisca) **× Joanna Gonçalves** (daughter of
Domingos Gonçalves †, Maria Fernandes), all of Ruivais. The parents of João Rodrigues Valle.
(The "barbacena" token in the filename is a retrieval-agent mislabel; the register is Ruivais,
Portugal.)

---

## Evidence assessment and identification

Three mutually corroborating records — the existing PAR-0018 (Ritta's marriage naming her
parents), the 1751 Mariana certidão (PAR-0034), and the 1728 Ruivais baptism (PAR-0035) —
converge on the same couple in the same Borda do Campo parish with a consistent timeline. The
child links (P-0058 ← F-0038; P-0078 ← F-0039) are recorded as **strong-evidence**, not
confirmed, because the identifications rest on name/parish/timeline agreement (common names),
not an explicit cross-reference within a single record. The marriages themselves (E-0070,
E-0072) and João's baptism (E-0071) are **confirmed** from their own primary records.

---

## Entities created / updated

**New sources:** PAR-0034 (1751 marriage certidão, derivative/primary/direct), PAR-0035 (1728
Ruivais baptism, original/primary/direct), PAR-0036 (1716 Ruivais marriage, original/primary/direct).
**New scans:** evidence/parish/PAR-0034…PAR-0036 (all `private: false`, matching the Swiss
deep-ancestry precedent PAR-0027–0029).
**New people:** P-0078 João Rodrigues Valle (b.15 Apr 1728 Ruivais, Portuguese), P-0079 Isabel
Ribeiro (Borda do Campo, Brazilian), P-0080 João Rodrigues (Ruivais, Portuguese), P-0081 Joanna
Gonçalves (Ruivais, Portuguese).
**New families:** F-0038 (P-0078 × P-0079, child P-0058), F-0039 (P-0080 × P-0081, child P-0078).
**New events:** E-0070 (1751 marriage), E-0071 (1728 baptism), E-0072 (1716 marriage).
**Updated:** P-0058 (added F-0038 as parent family; lead resolved). P-0080/P-0081 event_ids
include E-0071 (parents named in the baptism). Reciprocity verified by hand.
**Inventory:** DOC-0070–0072.
**Not modelled (leads):** the 1716-named grandparents (Gonçalo Rodrigues × Elebia Francisca;
Domingos Gonçalves × Maria Fernandes) and Isabel Ribeiro's parents (Manoel Nado Pestana × Anna
Francisca) — named in the marriage records but with no records of their own; recorded as notes.

Repository now 286 entities. All 69 tests pass; viewer index rebuilt; GEDCOM regenerated (3381 lines).

---

## Deferred / not promoted from the Toledo cluster (agent-2 flags, verified against catalogue)

- **José Cesário 1813 baptism** (rec-toledo-jose-cesario-baptism-1813-sjdrei): agent flagged
  PROMOTE, but record-coverage already records this image as **too illegible to transcribe**
  (assessed 7 Aug 2026). Not promoted. Needs a higher-resolution scan.
- Already catalogued (agent false positives): Ladisláo × Matilde 1810 = PAR-0023; Ladisláo
  baptism 1787 = PAR-0019; Carolina 1821 = PAR-0017; Joaquim José × Ritta marriage ≈ PAR-0018.
- **Still to process (verified new, next sessions):** 1856 Lei de Terras land register (José
  Cesário); 1885 Rio Pardo tutela; 1881 Ladisláo estate citation; several new PRB-0006 inventário
  folios (título de herdeiros pp.0-2, p.5b, folios 7/10/20); the 1751 Barbacena original-folio
  scan backing PAR-0034.
