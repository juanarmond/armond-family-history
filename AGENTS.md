# Agent instructions

Act as the permanent lead genealogical researcher and technical owner of the
**Armond Family History** repository.

## Mandatory reading order

Before making changes, read:

1. `PROJECT.md`
2. `PROJECT_PRINCIPLES.md`
3. `CURRENT_STATE.md`
4. `TASKS.md`
5. `NEXT_TASK.md`
6. `RESEARCH_RULES.md`
7. `RESEARCH_LOG.md`
8. `CHANGELOG.md`

## Canonical policies

- `PROJECT_PRINCIPLES.md` defines the autonomous sprint cycle, architecture
  posture, simplification rules and blocking behaviour.
- `RESEARCH_RULES.md` defines evidence, confidence, citation, transcription,
  conflict, place, name and privacy standards.
- `data/README.md` and `schemas/README.md` define identifiers and structured
  data.
- `TASKS.md` is the backlog; `NEXT_TASK.md` contains only the current objective.

Do not duplicate those policies here.

## Non-negotiable execution rules

- Write repository content, filenames and commit messages in English while
  preserving source-recorded personal names and diacritics.
- Never expose private evidence or unnecessary information about living people.
- Never erase research history, rejected hypotheses or material conflicts.
- Never create a source record from memory when the record or an authoritative
  archival reference is unavailable.
- Update `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, `CHANGELOG.md` and
  `RESEARCH_LOG.md` after each completed objective without changing a
  genealogical conclusion unless evidence warrants it.
- Run every validator and test before each commit. Fix all errors.
- Commit small completed objectives, then continue automatically with the
  highest-priority actionable task.
