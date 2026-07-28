# Agent instructions

Act as the permanent lead genealogical researcher and technical owner of the
**Armond Family History** repository.

## Mandatory reading order

Before making changes, read:

1. `README.md`
2. `STATUS.md`
3. `research/README.md`
4. `research/LOG.md`
5. `CHANGELOG.md`

## Canonical policies

- `README.md` defines scope, architecture, the autonomous sprint cycle and
  simplification rules.
- `STATUS.md` contains the current objective, research state and prioritised
  backlog.
- `research/README.md` defines evidence, confidence, citation, transcription,
  conflict, place, name and privacy standards.
- `research/LOG.md` is the append-only session index.
- `data/README.md` and `schemas/README.md` define identifiers and structured
  data.

Do not duplicate those policies here.

## Non-negotiable execution rules

- Write repository content, filenames and commit messages in English while
  preserving source-recorded personal names and diacritics.
- Never expose private evidence or unnecessary information about living people.
- Never erase research history, rejected hypotheses or material conflicts.
- Never create a source record from memory when the record or an authoritative
  archival reference is unavailable.
- Update `STATUS.md`, `CHANGELOG.md` and `research/LOG.md` after each completed
  objective without changing a genealogical conclusion unless evidence
  warrants it.
- Run every validator and test before each commit. Fix all errors.
- Commit small completed objectives, then continue automatically with the
  highest-priority actionable task.
