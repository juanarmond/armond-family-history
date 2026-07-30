# evidence/references — FAN / context record images

`references/` holds record images where one of the family's people appears only
in a **functional or associative role** (witness, appraiser/*louvado*, creditor,
attorney/*procurador*, party, signatory, co-owner). These are **FAN references**
(Friends / Associates / Neighbours): timeline, place, standing and network
context — **never evidence** for a genealogical conclusion.

## Rules

- **One catalogued FAN entity per image.** Every file here is described by a
  `data/fan/FAN-NNNN.yaml` record (schema `schemas/fan.schema.json`,
  `usage: context`) with a transcription and at least one
  `participants[].person_id`.
- **Naming.** `FAN-NNNN.<ext>` — the record ID only, with **no descriptive
  suffix**. The date, place, record type and role live in the FAN record
  (`data/fan/FAN-NNNN.yaml`), not in the filename.
- **Flat.** No per-topic subfolders — one directory, one image per FAN entity.
- **Subject records do not belong here.** A record *about* the family (its own
  inventário, deed or vital record) is a subject **source** in the matching
  `evidence/<category>/` (e.g. `evidence/probate/`), catalogued under its own
  prefix. Worked example: a third party's inventário in which Simplício was
  summoned as *louvado* is FAN (his role, not the subject); his *own* inventário,
  if ever found, would be a PRB source in `evidence/probate/`.

## Current set — Muriaé/Leopoldina Full-Text (Simplício P-0016 / Aristão P-0008)

FamilySearch Full-Text hits in third-party probate/notarial records of the
Muriaé and Leopoldina comarcas (Zona da Mata, MG). The two **subject** records
from the same batch are catalogued elsewhere: **PRB-0001** (1881 Leopoldina
inventário heir list) and **PRB-0002** (1884 Leopoldina petition of Simplício).

| FAN | FamilySearch ARK | Record (date · place) | Our person's role |
| --- | --- | --- | --- |
| FAN-0001 | 3:1:3QHV-YQQY-PQGB | Procuração · 1875 · Muriaé | Simplício assina a rogo da outorgante |
| FAN-0002 | 3:1:3QHJ-HQ4H-CJQM | Conta de partilha (D. Rita Maria Ferreira) · c.1882-83 · Leopoldina | Simplício credor/pagável |
| FAN-0003 | 3:1:3QHJ-5QQH-275Y | Escritura/traslado · 1889 · Muriaé | Simplício parte |
| FAN-0004 | 3:1:3QHV-YQQ4-CS46 | Inventário · 1904 · Muriaé | Simplício louvado |
| FAN-0005 | 3:1:3QHJ-RQQH-2ZDL | Medição (Dores da Vitória) · 1906 · Muriaé | Simplício suplente de arbitrador |
| FAN-0006 | 3:1:3QHJ-5QQH-2H6M | Partilha · 1907 · Muriaé | Simplício procurador |
| FAN-0007 | 3:1:3QHK-HQQH-2CYY | Medição "Vae e Volta ou Dezengano" · 1910 · Muriaé | Simplício condômino |
| FAN-0008 | 3:1:3QHJ-RQQ4-B9Y7 | Inventário (encerramento) · 1913 · Muriaé | Simplício testemunha |
| FAN-0009 | 3:1:3QHK-YQ79-79HH-J | Partilha/testamento (s/d) · Muriaé | Simplício proposto louvado |
| FAN-0010 | 3:1:3QHK-HQQH-2RX | Escritura · 1903 · Laginha (Muriaé) | Aristão testemunha |
| FAN-0011 | 3:1:3QHV-4QQP-GPBY | Inventário de Antonio Marques da Silva · c.1917 · S. Paulo do Muriaé | Aristão credor |
| FAN-0012 | 3:1:3QHV-ZQQP-PFRL | Rateio entre credores · 1917 · Muriaé | Aristão credor |
| FAN-0013 | 3:1:3QHV-4QQP-L9HZ-R | Inventário de Joaquim dos Santos Garcia · c.1921-22 · Muriaé | Aristão requerente |

Full transcriptions and abstracts are in each `data/fan/FAN-NNNN.yaml`. The
original Full-Text candidate list (with negatives and false positives) is kept at
`logs/2026-07-29-fulltext-muriae-leopoldina-candidates.csv`; the search is
written up in `logs/2026-07-29-fulltext-muriae-leopoldina-probate-hits.md`.
