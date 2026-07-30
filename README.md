# Armond Family History

Private, evidence-led genealogy for Juan Carlos Muniz Armond and the related
Armond, Paz, Muniz, Bittencourt, Bohrer, Guimarães, Engracio, Souza, Azevedo,
Brandão and Toledo branches.

## Purpose and scope

This repository preserves a documented and reproducible family history. It
separates confirmed facts from strong evidence, hypotheses and rejected
claims; retains conflicts; and keeps an audit trail for every conclusion.

The immediate objective is to document each direct ancestral line through the
nineteenth century, generation by generation. Current evidence is concentrated
in Rio de Janeiro and Minas Gerais, Brazil. Portuguese origins, including
possible island origins, and possible German-speaking origins in a Bohrer line
remain research questions rather than assumptions.

The repository is intended to support:

- a source-based family tree and family profiles;
- civil, parish, probate, immigration and other original records;
- transcriptions, translations, research logs and rejected hypotheses;
- migration and residence histories; and
- structured data for future profiles, timelines, maps and private exports.

All repository content, filenames and commit messages are in English. Personal
names remain exactly as recorded by the best available source, including
diacritics. Original records remain in their original language, with separate
English abstracts or translations.

## Start here

- See [`STATUS.md` — Current objective](STATUS.md#current-objective) for the
  work in progress.
- See [`STATUS.md` — Next steps](STATUS.md#next-steps) for the immediate
  ordered execution queue.
- See [`data/record-coverage.yaml`](data/record-coverage.yaml) for the
  canonical research plan: the per-ancestor record gaps and their next actions.
- Claude Code and Codex both read [`AGENTS.md`](AGENTS.md) for permanent
  instructions and context routing (`CLAUDE.md` simply imports it).
- Research history is indexed in [`logs/LOG.md`](logs/LOG.md); do not
  look for historical session detail in `STATUS.md`.

## Canonical documents

Each concern has one owner:

- [`STATUS.md`](STATUS.md) — present objective, immediate next steps, blockers,
  research snapshot, unresolved conflicts and strategic priorities.
- [`data/record-coverage.yaml`](data/record-coverage.yaml) — the
  canonical research plan: per-ancestor record gaps, search status and next
  actions. Priority ordering lives in `STATUS.md`.
- [`research/README.md`](research/README.md) — evidence, citation,
  transcription, conflict and privacy rules.
- [`logs/LOG.md`](logs/LOG.md) — append-only index of completed
  research and repository-audit sessions.
- [`CHANGELOG.md`](CHANGELOG.md) — notable repository engineering changes.
- [`data/README.md`](data/README.md) — identifiers, reservations, drafts and
  promotion.
- [`schemas/README.md`](schemas/README.md) — structured-data contracts and
  validation.
- [`AGENTS.md`](AGENTS.md) — stable execution and context-loading protocol,
  shared by Claude Code and Codex (`CLAUDE.md` imports it).
- [`family-tree-viewer/README.md`](family-tree-viewer/README.md) — the static,
  read-only family-tree viewer generated from the validated YAML.

## Repository layout

```text
.
├── AGENTS.md
├── CLAUDE.md           # Claude Code loader; imports AGENTS.md
├── README.md
├── STATUS.md
├── CHANGELOG.md
├── data/               # structured YAML: entities + control ledgers (id, inventory, coverage)
├── evidence/           # authorised source files, organised by record category
├── family-tree-viewer/ # static, read-only viewer generated from the YAML
├── logs/               # research history: LOG.md index, correspondence log, dated sessions
├── research/           # policy, worksheets, entity drafts and reference resources
├── schemas/            # JSON Schemas
├── scripts/            # validation and entity lifecycle commands
├── templates/          # canonical entity and research templates
└── tests/              # repository contract tests
```

Directories are created only with their first substantive artifact.

## Operating model

Build the smallest maintainable repository that preserves rigorous,
reproducible and private research. Accuracy and history take priority over tree
size or publication speed.

At the start of each sprint:

1. review the repository and Git state;
2. identify duplicated or obsolete files, dead code, stale TODOs and technical
   debt;
3. identify useful architecture, validation and automation improvements;
4. consolidate each concept into its canonical location; and
5. remove obsolete non-evidence files when Git provides sufficient recovery.

Then repeat: research, analyse, validate, document, commit and select the next
highest-priority actionable task. Never delete evidence, historical
conclusions, rejected hypotheses or material conflicts. Correct or supersede
them explicitly.

Challenge the architecture continuously, but prefer simple, readable designs.
Implement low-risk improvements immediately. Record higher-risk proposals,
migration effort and maintenance impact in `STATUS.md`. Defer generated person
pages and exports until real source records demonstrate schema stability.

If the highest-priority task is blocked, record the negative result and exact
intervention required. Continue to a lower task only when that does not bypass
an evidence gate; otherwise improve intake, validation or reproducibility
without inventing evidence.

## Repository workflow

Install the pinned dependencies and run the complete check:

```console
uv sync
uv run --frozen make check
```

Before adding structured data:

1. Inventory and privacy-review the document.
2. Preview an ID reservation with
   `python3 scripts/new_entity.py reserve source --dry-run`, then reserve it
   without `--dry-run`.
3. Complete the draft under `research/entity-drafts/` and record the search
   path.
4. Preview mutually dependent drafts together with
   `python3 scripts/new_entity.py promote ID... --dry-run`, then promote the
   valid batch.
5. Run `uv run --frozen make check` before committing.

The same frozen check runs on GitHub pushes and pull requests.

## Privacy

This is a private repository. Minimise information about living people and do
not publish or copy their documents outside the repository without explicit
permission. Government identifiers, full addresses, signatures and other
sensitive details must not be transcribed unless essential to the research.
