# Armond Family History

Private genealogy research repository for the Armond, Muniz, Bohrer, Guimarães, Engracio and related family branches.

## Purpose

This repository preserves a documented and reproducible family history. It separates confirmed facts from research leads and hypotheses, records conflicting evidence, and maintains a clear audit trail for every conclusion.

## Working language

All repository content is written in English. Original records remain in their original language, with English summaries or transcriptions added separately.

## Evidence model

The canonical evidence hierarchy, confidence statuses and citation standard are
defined in [`RESEARCH_RULES.md`](RESEARCH_RULES.md).

## Start here

1. [`PROJECT.md`](PROJECT.md) — scope and architecture.
2. [`PROJECT_PRINCIPLES.md`](PROJECT_PRINCIPLES.md) — permanent operating
   principles and autonomous research cycle.
3. [`CURRENT_STATE.md`](CURRENT_STATE.md) — present family-tree state.
4. [`TASKS.md`](TASKS.md) — prioritised research backlog.
5. [`NEXT_TASK.md`](NEXT_TASK.md) — one current actionable objective.
6. [`RESEARCH_RULES.md`](RESEARCH_RULES.md) — research and citation standards.
7. [`RESEARCH_LOG.md`](RESEARCH_LOG.md) — cumulative append-only research index.
8. [`AGENTS.md`](AGENTS.md) — concise execution instructions.
9. [`schemas/README.md`](schemas/README.md) — YAML entity model and validation.
10. [`research/DOCUMENT_CATALOGUING_PLAN.md`](research/DOCUMENT_CATALOGUING_PLAN.md)
   — staged ingestion of the documents already supplied.

## Repository workflow

Install the pinned local dependencies and run the repository checks:

```console
uv sync
uv run make check
```

Before adding structured data:

1. Inventory and privacy-review the document.
2. Preview an ID reservation with
   `python3 scripts/new_entity.py reserve source --dry-run`, then rerun without
   `--dry-run` to create a reserved draft.
3. Complete the draft under `research/entity-drafts/` and retain the search
   path in a research log.
4. Preview mutually dependent completed drafts together with
   `python3 scripts/new_entity.py promote ID... --dry-run`, then promote the
   valid batch without `--dry-run`.
5. Run `uv run make check` before committing.

Reservation and promotion rules are defined in [`data/README.md`](data/README.md).
Validation scope is documented once in
[`schemas/README.md`](schemas/README.md).

## Current status

Active research. The current tree is well established through the grandparents and mostly established through the great-grandparents. Several earlier generations remain provisional pending civil, parish, immigration, naturalisation or probate records.

The structured entity directories are intentionally empty. Existing narrative
claims have not been bulk-converted: the first source records must be created
from the clearest original certificates, then the model must be reviewed after
three records before wider ingestion or generated person pages.

## Privacy

This is a private repository. Documents concerning living people must not be published or copied outside the repository without explicit permission.
