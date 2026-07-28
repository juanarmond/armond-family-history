# Armond Family History

Private genealogy research repository for the Armond, Muniz, Bohrer, Guimarães, Engracio and related family branches.

## Purpose

This repository preserves a documented and reproducible family history. It separates confirmed facts from research leads and hypotheses, records conflicting evidence, and maintains a clear audit trail for every conclusion.

## Working language

All repository content is written in English. Original records remain in their original language, with English summaries or transcriptions added separately.

## Evidence model

- **Confirmed** — supported by a primary source or a reliable contemporary record.
- **Strong evidence** — supported by multiple consistent sources, but the decisive primary record has not yet been examined.
- **Hypothesis** — plausible, but not sufficiently supported.
- **Rejected** — investigated and found inconsistent or unsupported.

## Start here

1. [`PROJECT.md`](PROJECT.md) — scope and architecture.
2. [`CURRENT_STATE.md`](CURRENT_STATE.md) — present family-tree state.
3. [`TASKS.md`](TASKS.md) — prioritised research backlog.
4. [`RESEARCH_RULES.md`](RESEARCH_RULES.md) — research and citation standards.
5. [`AGENTS.md`](AGENTS.md) — instructions for Codex and other agents.
6. [`schemas/README.md`](schemas/README.md) — YAML entity model and validation.
7. [`research/DOCUMENT_CATALOGUING_PLAN.md`](research/DOCUMENT_CATALOGUING_PLAN.md)
   — staged ingestion of the documents already supplied.

## Repository workflow

Install the pinned local dependencies and run the repository checks:

```console
uv sync
uv run make check
```

Before adding structured data:

1. Inventory and privacy-review the document.
2. Allocate its source ID through `data/id-ledger.yaml`.
3. Create the source record and retain the search path in a research log.
4. Add or update linked people, families, events and places without resolving
   uncertainty silently.
5. Run `uv run make check` before committing.

The validator checks schemas, identifier allocation, references, evidence
quality behind confirmed conclusions, FamilySearch and other collaborative-tree
usage, evidence-file checksums, living-person privacy, possible duplicate
identities and parent-child chronology.

## Current status

Active research. The current tree is well established through the grandparents and mostly established through the great-grandparents. Several earlier generations remain provisional pending civil, parish, immigration, naturalisation or probate records.

The structured entity directories are intentionally empty. Existing narrative
claims have not been bulk-converted: the first source records must be created
from the clearest original certificates, then the model must be reviewed after
three records before wider ingestion or generated person pages.

## Privacy

This is a private repository. Documents concerning living people must not be published or copied outside the repository without explicit permission.
