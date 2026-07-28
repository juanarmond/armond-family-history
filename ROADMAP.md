# Prioritised roadmap

`TASKS.md` is the detailed backlog. This file records sequencing, migration
cost and long-term architecture impact.

| Priority | Outcome | Migration effort | Maintenance impact | Status |
| --- | --- | --- | --- | --- |
| P0 | Consolidate governance and remove placeholder files | Low; no data migration | Fewer canonical documents and less drift | Complete |
| P0 | Version and validate the incoming-document inventory | Low; inventory is empty | Prevents ad hoc intake and privacy omissions | Complete |
| P0 | Add entity schema versions and correct the evidence taxonomy | Low now; high after ingestion | Enables controlled migrations and accurate source assessment | Complete |
| P0 | Add controlled parent relationship and participant roles | Low now; medium after ingestion | Prevents vocabulary drift across hundreds of people | Next |
| P1 | Catalogue and model the first three original records | Requires source-image access | Tests the model against reality before scale | Blocked by missing files |
| P1 | Review the model and migrate the remaining existing evidence | Depends on first-source findings | Establishes a stable machine-readable base | Pending |
| P2 | Refactor the monolithic validator into focused modules | Medium, approximately one engineering sprint | Easier testing and safer rule additions | Pending |
| P2 | Add safe ID allocation and entity-skeleton automation | Medium | Removes manual ledger and filename errors | Pending |
| P3 | Resume direct-ancestor research in `TASKS.md` order | Ongoing research | Advances genealogy without bypassing evidence gates | Blocked by existing-evidence gate |
| P4 | Generate profiles, timelines and privacy-filtered exports | Medium to high | Reproducible derived views after schema stability | Deferred |

## Architecture findings

The model is intentionally small. Findings 1, 2 and 5 were corrected before
live data ingestion:

1. Resolved: entity files now declare schema version 1.
2. Resolved: record category, source form, information quality and evidence
   type are separate fields. Evidence type remains a conservative source-level
   assessment until real records justify a citation-level model.
3. Parent-child relationships lack a relationship type, and event participant
   roles are uncontrolled strings.
4. The validator is a single file of more than one thousand lines. It works,
   but continued rule growth will make review and testing harder.
5. Resolved: the document inventory has a versioned schema and cross-file
   integrity checks.

Finding 3 has low migration risk because no live entities exist and must be
completed before the first source is ingested. Finding 4 is a medium-risk
internal refactor and can follow once the core contract is stable.
