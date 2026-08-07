# 2026-08-07 — Retrieval drop value-gate, third pass

## Scope

Continued the value-gate cycle begun in the second pass of 2026-08-07. This
pass completed the triage of the remaining new images from the current
`research/from-retrieval/` drop and corrected several errors introduced in
earlier passes of this same drop.

## New images triaged

### rec-toledo-matilde-inventario-1879-titulo-herdeiros-p0.jpg
Blank or unreadable cover page of Matilde's 1879 inventário. No genealogical
facts visible. Not catalogued; recorded in triage ledger as `no data`.

### rec-toledo-matilde-inventario-1879-titulo-herdeiros-p5b.jpg
New folio image, not previously triaged. Read in full. Contains:

- Continuation of heir #5 block: Carolina Leopoldina Marques (⚭ Narciso
  Marques Braz), already deceased at this date (margin annotation "Palleceo").
  Six named representantes:
  1. Maria Marques ⚭ Antonio Marques Pereira
  2. Herculano Ernesto Marques, solteiro, 26 anos
  3. Octaviano Marques Braz ⚭ Amelia Baldoina de Tolledo
  4. Alda Clothilde Marques ⚭ Aurelio Ferreira Pinto
  5. Sophia Olympia Marques ⚭ Joaquim Dias de Medeiros
  6. Hortencia Cecilia Marques, solteira, 15 anos

- Heir #6 (new): Aureliano de Salles Tolledo, "cazado que foi com D. Marianna
  Euphragia de Tolledo, já fallecida"; resident S. Sebastião dos Aflitos, termo
  de Santa Rita do Turvo.

**Conflict flagged**: F-0027 documented_child for Aureliano previously read his
wife's name as "Marciana Espro[n?]de de Toledo" from PRB-0009. The p5b primary
source gives "Marianna Euphragia de Tolledo." The discrepancy is noted in
F-0027 and PRB-0006 notes; requires direct re-check of PRB-0009 to determine
whether this is a misread or indicates two marriages.

Data recorded in PRB-0006 notes and F-0027 documented_child entry.

### marfisa-death-1962-itaperuna-p1.jpg
Higher-quality re-scan of the Marfiza Ferreira Armond 1962 death register entry
(= CIV-0013). Read at full zoom. Multiple corrections to CIV-0013 applied:

| Field | Old reading | Corrected reading |
|---|---|---|
| Declarant | [Gustavo?] Barroso | Silvio/Goistos Barrozo |
| Death time | treze horas e trinta = 1:30 PM | três horas e trinta = 3:30 AM |
| Doctor | Dr. Carlos Antonio Deslandes | Dr. Carlos Antonio Rodrigues |
| Address | [rua Paes de Azevedo, 100?] | Rua Pres. de Azevedo 100 |
| City | uncertain (Itaperuna?) | CONFIRMED Itaperuna |

CIV-0013 transcription, abstract, informant, and limitations fields updated.
event_place_text and archive_or_registry corrected to "Itaperuna."

### PDF consolidations
The owner consolidated the individual JC inventário pages (→ PRB-0008), Ladisláo
inventário pages (→ PRB-0009), and Matilde inventário pages (→ PRB-0006) into
three PDF files for convenience. Contents are consolidations of already-triaged
individual images; not re-read. Recorded in triage ledger.

## Error corrections (continued from second pass)

### PRB-0009 — Simplício surname discrepancy flagged
The PRB-0009 p4 curator "Simplicio Jaci Ferrura [Ferreira] de Toledo" was
previously associated with P-0016 (Simplício José Ferreira ARMOND). This
association is suspect: the surname in the document is "de Toledo," while P-0016
has the "Armond" surname (confirmed in PRB-0006, 1879). The p4 curator may be
a different Toledo family member. Flagged in:
- PRB-0009 transcription (p4 note)
- PRB-0009 abstract
- PRB-0009 limitations
- PRB-0009 new note (TWO DISTINCT SIMPLÍCIOS clarification)

P-0016 remains in PRB-0009 linked_people pending image re-verification, as
the association was not definitively disproven — but the link is now explicitly
marked as uncertain.

### PRB-0009 — Two-Simplícios clarification added
Item 6 in JC's representante list (PRB-0009 p2) = "Simplicio José Perrura
[Ferreira] de Tolledo, Solteiro de quatorze annos" is JC's OWN SON with the
Toledo surname (b.~1853, dead before 1879). This is a DIFFERENT person from
P-0016 (Simplício José Ferreira Armond, Eliza's husband). Added to PRB-0009
title and abstract.

## Files modified

- `data/sources/civil/CIV-0013.yaml` — transcription corrections (6 fields)
- `data/sources/probate/PRB-0006.yaml` — new p5b data in notes
- `data/families/F-0027.yaml` — Aureliano wife-name conflict flagged
- `data/sources/probate/PRB-0009.yaml` — title, abstract, p4 note, limitations, new note
- `research/from-retrieval-triage-ledger.md` — new section for this pass
- `export/armond-family-history.ged` — regenerated

## Checks

`make check`: 0 errors, 0 warnings (69 tests passed).
`make export`: GEDCOM 7.0, 2697 lines.
