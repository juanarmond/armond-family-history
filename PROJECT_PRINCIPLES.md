# Project principles

These are the canonical operating and architecture principles. Evidence and
citation rules live only in `RESEARCH_RULES.md`; structured-data rules live only
in `schemas/README.md` and `data/README.md`.

## Objective

Build the smallest maintainable repository that can preserve a rigorous,
reproducible and private family history. Accuracy and research history take
priority over tree size or publication speed.

## Sprint opening review

At the start of each sprint:

1. review the complete repository and current Git state;
2. identify technical debt, duplicated or obsolete documentation and scripts,
   unused schemas or examples, stale TODOs and temporary files;
3. identify architecture, validation, automation and developer-experience
   improvements;
4. consolidate duplicated concepts into one canonical location;
5. remove obsolete non-evidence files when Git history is sufficient recovery.

Never delete evidence, historical conclusions, rejected hypotheses or research
history. Correct or supersede them explicitly.

## Sprint cycle

1. **Repository review** — simplify, validate and commit.
2. **Repository improvement** — improve architecture, documentation,
   validation, automation, templates and developer experience; commit.
3. **Genealogical research** — pursue the highest-priority unblocked direct
   ancestor or missing-parent question; commit reproducible positive or
   negative results.
4. **Data ingestion** — convert only verified evidence into YAML and update
   every state and history file; commit.
5. **Repository health** — run all checks, fix every error and commit any
   resulting repair.

Within each objective use: research, analyse, validate, document, commit, select
the next task, repeat.

## Architecture posture

- Continuously challenge the current design.
- Optimise for maintainability, scalability, data integrity, reproducibility,
  simplicity and historical accuracy.
- Prefer one canonical document per concept.
- Prefer fewer substantial files over placeholder files.
- Create directories only with their first substantive artifact.
- Implement a better design immediately when migration risk is low; otherwise
  record the rationale, effort and long-term impact in `ROADMAP.md`.
- Defer generated person pages and exports until real records demonstrate
  schema stability.

## Priority and blocking

Work in `TASKS.md` priority order. `NEXT_TASK.md` must contain one exact
actionable objective, not a second backlog.

If the highest-priority task is blocked:

1. record the negative result and exact intervention required;
2. continue to a lower task only when no explicit research gate is violated;
3. otherwise improve intake, validation, architecture or search planning
   without inventing evidence.

Ask for user intervention only for credentials, payment, physical retrieval,
rights clearance or access to a private record absent from the repository.

## Completion and reporting

After each completed objective:

- update `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, `CHANGELOG.md` and
  `RESEARCH_LOG.md`;
- add or update a detailed dated session log for research activity;
- run every validator and test;
- commit a small coherent change;
- continue automatically.

At the natural end of a sprint, report completed work, repository improvements,
research discoveries, files removed/merged/created, remaining technical debt,
blockers and the next objective.
