# 2026-08-08 — Armond leads and Mathilde death date (2026-08-08 retrieval drop, fourth pass)

## Scope

Fourth value-gate pass on the retrieval agent drop, acting on new findings identified
from the 2026-08-08 OCR transcripts of the Ladisláo and Matilde inventário files:

- `research/from-retrieval/output/transcripts/ladislao-1867-part01-pp*.md`
- `research/from-retrieval/output/transcripts/ladislao-1867-part05-pp309-387.md`
- `research/from-retrieval/output/transcripts/matilde-1879-part01-pp001-092.md`

## New findings confirmed

### 1. Mathilde Maria de Jesus death date — CONFIRMED

Source: PRB-0006 (already catalogued), folio 6 (juramento ao inventariante).

Transcript text: the inventariante Cezário José de Toledo swore before the Juiz on
28 April 1879 that Mathilde "faleceu em o dia doze de Março proximo passado" and
"sem testamento." Death date: **12 March 1879**.

Actions taken:
- Created `data/events/E-0059.yaml` (death, 12 March 1879, confirmed, source PRB-0006).
- Added E-0059 to `data/people/P-0027.yaml` event_ids.
- Updated P-0027 notes with confirmed date and Capitão Manoel context.
- Updated `data/record-coverage.yaml` for P-0027 death:
  - status: `lead_only` → `catalogued`; source_ids: `[PRB-0006]`
  - next_action updated to reflect confirmed date
  - Coverage note fixed (removed outdated "Eliza's parent unresolved" language)
- Updated STATUS.md: structured events 55 → 56.

Prior estimate ("circa 1877 or after") was based on PRB-0003; now superseded by
the primary judicial record.

### 2. Capitão Manoel Rodrigues de Lima = Mathilde's uncle

Source: matilde-1879-part01-pp001-092.md, pp. 154–155 (certidão embedded in inventory).

A certidão at those pages records Capitão Manoel Rodrigues de Lima (São José d'El Rei)
donating the enslaved woman Martinha to "minha sobrinha Mathilde Maria de Jesus." This
makes Mathilde the Capitão's niece. He states he bought Martinha from "minha [irmã?]
Dona Francisca de Lima" — if "irmã" (sister) is the correct reading, Francisca de Lima
is the Capitão's sister and Mathilde's mother, corroborating Ignez Francisca de Lima
(P-0060) as Mathilde's mother (family F-0029). The "[maã?/irmã?]" word is uncertain in
the transcript; image verification required before using as evidence.

Actions taken:
- Added note to PRB-0006.yaml.
- Added note to P-0027.yaml (combined with death date note above).
- No structural data change pending image verification.

### 3. "Ladislao Egidio [?Ferre] [?Armonde]" signature, p.150 — CRITICAL LEAD

Source: ladislao-1867-part01 transcript, p. 150 (1873 partition notification).

At the notification of the partition of the Ladisláo estate (1873), the signatory list
includes "Ladislao Egidio [?Ferre] [?Armonde]" alongside Simplício and Eliza. If this
reading is correct, a person with the Armond surname (possibly Simplício's father) was
present alongside Simplício and Eliza at the same estate proceeding — suggesting two
Armond × Toledo generations in the same event. The reading is uncertain and requires
direct image verification. This is the highest-priority image to verify from this drop.

Actions taken:
- Added note to `data/record-coverage.yaml` P-0016 notes section.

### 4. "[Philos?] José Ferreira Armond" — second Armond × Toledo marriage, p.258

Source: ladislao-1867 transcript, p. 258 (1880 declaration by Francisco Leocádio de
Toledo).

Francisco Leocádio de Toledo (P-0061) names a daughter married to "[Philos?] José [?]
Ferreira Armond." If confirmed by image, this is a second Armond × Toledo marriage in
the same generation as Simplício × Eliza (P-0016 × P-0017). The "[Philos?] José Ferreira
Armond" may be a sibling or cousin of Simplício. Reading is uncertain; do not promote
until the p. 258 image is verified directly.

Actions taken:
- Added note to `data/record-coverage.yaml` P-0016 notes section.
- Added note to `data/sources/probate/PRB-0009.yaml` (as the document containing related
  context on FL's children).

### 5. Francisco Leocádio as son-in-law of Ladisláo — MATERIAL CONFLICT (conflict #15)

Source: ladislao-1867-part05-pp309-387.md, p. 383 (1882 embargos judgment).

The judgment reads: "D. Maria Joaquina de Jesus, mulher de Francisco Leocadio de
Toledo, sobreviveu ao seu pai Ladislão Eygidio Ferreira de Toledo." This places Maria
Joaquina de Jesus as Ladisláo's DAUGHTER and Francisco Leocádio as her husband (son-in-law
of Ladisláo), not his direct child. This directly contradicts PRB-0009-gen1, which lists
Francisco Leocádio as child #4 of Ladisláo × Mathilde.

Implications if confirmed:
- F-0027 would need restructuring (FL removed from children; MJ added as daughter).
- PRB-0009-gen1 item 4 reading would need re-examination.
- Alternatively, there could be a different Maria Joaquina, or the judgment prose uses
  "pai" loosely (father-in-law), though the plain reading is biological father.

Status: flagged. Do NOT restructure F-0027 or P-0061 until the p.383 image is verified.

Actions taken:
- Added material conflict #15 to STATUS.md.
- Added conflict note to `data/people/P-0061.yaml`.
- Added conflict note to `data/families/F-0027.yaml`.

## Test and export

- `make check`: 69/69 tests pass.
  - Also fixed `test_relative_markdown_links_resolve` to skip the gitignored
    `research/from-retrieval/` directory (transcript files contain OCR artifacts that
    look like broken markdown links but are not repository links).
- `make export`: GEDCOM regenerated (7.0, 2704 lines).

## Searches performed

No new searches. This pass acted on findings already extracted from the retrieval
agent's transcript files by the prior subagent analysis (session summary, 2026-08-08).

## Negative / bounded results

None this pass — all actions are from existing transcript findings.

## Next priorities

1. **Image verification (highest priority):** retrieve and read directly:
   - p. 150 image (1873 partition signatories — the "[?Armonde]" lead).
   - p. 258 image (FL's daughter's husband — the second Armond lead).
   - p. 383 image (1882 embargos judgment — FL son-in-law conflict).
2. Continue the current objective: Aristão baptism and Liliosa records retrieval.
