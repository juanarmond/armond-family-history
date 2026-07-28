# Codex Starting Prompt

Copy the prompt below into Codex after opening this repository.

---

You are working in the private repository `juanarmond/armond-family-history`.

Act as the lead genealogy-research and repository-engineering agent. Read these files before making changes:

1. `AGENTS.md`
2. `PROJECT.md`
3. `CURRENT_STATE.md`
4. `TASKS.md`
5. `RESEARCH_RULES.md`

Your immediate objective is to establish a clean, evidence-led repository foundation without inventing facts.

Perform the following work:

1. Inspect the current repository and summarise its state.
2. Propose a minimal YAML schema for people, families, events, places and sources. Do not over-engineer it.
3. Create example schema documentation and validation rules, but do not convert uncertain genealogical statements into confirmed structured facts.
4. Create the initial research-log template, person-profile template and source-record template.
5. Create a first implementation plan for cataloguing the existing documents.
6. Add automated validation for identifier formats, required fields, source references and impossible parent-child chronology where the available precision permits.
7. Keep all content, filenames, code comments, commit messages and issue text in English.
8. Treat FamilySearch and other collaborative trees as leads only.
9. Preserve every uncertainty and conflict already documented in `CURRENT_STATE.md`.
10. Do not publish, expose or move private family records outside this private repository.

Before editing, state your plan. Work in small, reviewable commits. After each logical change, run relevant checks and update `CHANGELOG.md`.

The first milestone is complete when the repository has:

- stable templates;
- documented schemas;
- basic validation;
- a research-log structure;
- a clear ingestion plan for the existing certificates and screenshots;
- no unsupported relationship marked as confirmed.

Do not start broad internet genealogy searches until the repository can catalogue and cite the results consistently.

---
