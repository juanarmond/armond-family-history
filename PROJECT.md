# Project Overview

## Objective

Reconstruct and preserve the documented ancestry and family history of **Juan Carlos Muniz Armond**, born 22 June 1982 in Rio de Janeiro, Brazil.

The project is intended to become a durable private archive containing:

- a source-based family tree;
- person and family profiles;
- civil and parish records;
- document transcriptions and translations;
- research logs and rejected hypotheses;
- migration and residence histories;
- structured data suitable for GEDCOM, timelines, maps and future publication.

## Geographic scope

The present evidence is concentrated in:

- Rio de Janeiro and Minas Gerais, Brazil;
- Portugal, including possible island research that remains unproved;
- possible German-speaking origins for one or more Bohrer lines, subject to evidence.

## Time scope

The immediate objective is to document every direct ancestral line through the nineteenth century. Earlier research will proceed only after each generation is linked by reliable evidence.

## Repository architecture

```text
.
├── AGENTS.md
├── README.md
├── PROJECT.md
├── CURRENT_STATE.md
├── TASKS.md
├── RESEARCH_RULES.md
├── ROADMAP.md
├── CHANGELOG.md
├── data/
│   ├── people/
│   ├── families/
│   ├── events/
│   ├── places/
│   └── sources/
├── people/
├── families/
├── evidence/
│   ├── civil/
│   ├── parish/
│   ├── immigration/
│   ├── naturalisation/
│   ├── newspapers/
│   └── probate/
├── research/
│   ├── logs/
│   ├── brazil/
│   ├── portugal/
│   └── unresolved/
├── timelines/
├── exports/
└── scripts/
```

Git does not preserve empty directories, so folders should be created when their first substantive file is added.

## Data strategy

The repository will initially use curated Markdown for analysis and YAML for stable structured entities. Markdown remains the human-readable research layer; YAML becomes the machine-readable source of truth after the schema has been validated against several real people and sources.

## Naming conventions

- Markdown filenames: lowercase kebab-case, for example `aristao-ferreira-armond.md`.
- Person IDs: `P-0001`.
- Source IDs: `SRC-0001`.
- Family IDs: `F-0001`.
- Event IDs: `E-0001`.
- Place IDs: `PL-0001`.
- Dates: ISO 8601 only when exact; otherwise use explicit text such as `about 1879` or `between 1885 and 1887`.

## Research standard

The project follows the genealogical proof principle: reasonably exhaustive research, complete source citation, analysis of evidence quality, resolution of conflicts and a written conclusion.

## Privacy standard

Information about living people is minimised and remains private. Government identifiers, addresses, signatures and other sensitive details must not be transcribed unless essential to the research purpose.
