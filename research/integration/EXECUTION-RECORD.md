# Retrieval integration refactor — execution record

Restart-safe state for the retrieval-integration and AI-architecture refactor (plan §14.3). A fresh agent resumes
from this file plus repository state. It never holds private data: no names or details of living people, no
record content, no secrets.

- **Plan:** `_local/PLAN-RETRIEVAL-INTEGRATION-REFACTOR.md`. It lives on the owner's machine (untracked), and
  this record names it by its role; the plan's own revision log (§25) tracks its changes.
- **Owner decisions (final, 2026-10-11):**
  - O1 public repository: decided.
  - O2 GEDCOM never tracked: decided.
  - O3 six restricted sources withheld: decided.
  - O4 pointer + accepted SHA-256: approved.
  - O5 Git/GitHub backup only: decided.
  - O6 real evidence promotion is per-task: standing rule.
  - O7 Batch P release: approved after O9.
  - O8 no history rewrite: closed; residual historical exposure accepted.
  - O9 private repository: approved.
- **Living-person classification:** exactly P-0001, P-0002 and P-0003; everyone else in the tree is deceased.
  Canonical rules: `research/README.md`, "Living people and private material".

## Ending state (2026-10-11)

| Repository | Ending HEAD | Visibility | Notes |
| --- | --- | --- | --- |
| `armond-family-history` | `b8be0a5` (`main`) | public | commits `5272303`, `6b0e505`, `95ebcae`, `b8be0a5`; deployed; no notification sent |
| `armond-family-history-private` | `2b40417` (`main`) | private | `afb30e4`, `2b40417`; a fresh clone matched the manifest and the local store |
| `armond-genealogy-retrieval` | `2f4d6db` (`main`) | private | unchanged (O10) |

`make check` passed: 559 entities, 0 errors, 0 warnings, 177 tests. `make privacy-audit` was clean.

## Starting checkpoints (2026-10-11)

| Repository | Role | Start HEAD | Visibility |
| --- | --- | --- | --- |
| `juanarmond/armond-family-history` | consumer, canonical genealogy | `ce2bfca` (`main`) | public |
| `juanarmond/armond-genealogy-retrieval` | producer, research | `2f4d6db` (`main`) | private |
| `juanarmond/armond-family-history-private` | private originals (O9) | created `afb30e4` | private |

Cross-repository rule (plan §14.12): each repository is changed only by a session working in it. This consumer
session reads the producer's files by path and never runs Git there. Producer changes are requested from the
producer's own session.

## Batches

| Batch | State | Notes |
| --- | --- | --- |
| P — forward privacy containment | **done** | O9 verified, O7 released (`main` `95ebcae`), site verified externally |
| 0 — current-state refresh | **done** | 2026-10-11: all three repositories re-verified (HEADs, visibility, drop, tests) |
| 1 — contract alignment and instruction authority (O4) | **done (consumer)** | pointer plus accepted SHA-256; v1 schemas vendored in `research/integration/schemas/` |
| 2 — producer hardening | **not implemented — owner decision O10** | the owner told the producer's session to do nothing in that repository (2026-10-11) |
| 3 — consumer intake validation | **done** | `make intake` (snapshot, verify, pin, log); legacy and v1 accepted |
| 4 — triage, promotion, Channel B | **done (consumer)** | `data/triage-index.yaml` (857 entries); `new_entity.py apply` |
| 5 — AI architecture and resilience | **done** | authority bound, drift tests, this record |
| 6 — engineering cleanup | **done (consumer)** | stale paths, false all-clear audits, Pages source |
| 7 — end-to-end audit | **done (legacy contract)** | intake verified and pinned the live handoff; audits ran by content |

### Batch P — forward privacy containment (done)

- **Working-tree containment:** commits `5272303`, `6b0e505` and `95ebcae`.
- **O9 private repository:** `juanarmond/armond-family-history-private`.
  - It is private, confirmed with `gh api`.
  - Commits `afb30e4` (originals) and `2b40417` (triage migration report).
  - A fresh clone matched the manifest and the local store byte for byte.
  - All 22 public references into `private/` resolve with their SHA-256.
- **O7 release:**
  - checks passed: `make check`, the privacy audit and a notifier dry-run ("no notification");
  - `main` was fast-forwarded and pushed, and the deploy succeeded;
  - the live site was checked from outside: 564 data files with no private strings and no living names;
    restricted scans return 404.
- **Residual historical exposure (O8, accepted):** copies committed before 2026-10-11 remain in public history and
  in Git LFS. The owner's five PDFs were still downloadable from LFS on 2026-10-11. This refactor does not and will
  not erase them.

### Consumer implementation (Batches 1, 3–6)

| Area | Implementation | Tests |
| --- | --- | --- |
| Instruction authority | AGENTS.md pointer; `research/integration/accepted-intake.json`; drift in `make intake` | `tests/test_instruction_authority.py` |
| Intake | `scripts/intake.py`; `research/integration/intake-log.yaml`; state in gitignored `research/.intake/` | `tests/test_intake.py` (C1–C7, O4, Channel A text-only) |
| Triage | `data/triage-index.yaml` and schema; `scripts/validation/triage.py`; migration `scripts/migrate_triage_ledger.py` | `tests/test_triage_index.py` (T1, T2, strict audits) |
| Promotion and Channel B | `scripts/new_entity.py apply`; inventory `transfer` block | `tests/test_promotion_transaction.py`, `tests/test_new_entity.py` (T3–T5) |
| Privacy | `held_privately`; validator rules; site and assistant scrubbing; `make privacy-audit` | `tests/test_public_surface.py`, `tests/test_pages_site.py`, `tests/test_validate_data.py` |

- **Ledger migration:**
  - 453 rows; 402 map to files, giving 840 entries; 17 more come from holdings, for 857.
  - 51 rows are unmapped; they are reported privately in `private/triage/migration-report-2026-10-11.md`, and
    none was discarded.
- **Intake:** pinned `828414254673…` (legacy, 341 files).

### Producer side (Batch 2) — not implemented (O10)

- **What happened:** the producer work package was sent to the retrieval repository's own session on 2026-10-11.
  The owner told that session to do nothing in `armond-genealogy-retrieval`.
- **Rules for this repository:**
  - do not write, run Git or run scripts in the producer repository;
  - do not ask its session to act;
  - keep legacy-manifest support (do **not** retire it);
  - reading the producer's files by path, read-only, is the only contact, as authorised.
- **Current state:** the consumer verifies the legacy contract itself:
  - it computes SHA-256 for every file;
  - it detects torn snapshots from the manifest bytes and the size and mtime of every live file;
  - it accepts Markdown/UTF-8 only;
  - it reads the producer's records manifest by path for page grouping and aliases.
- **Readiness:** contract v1 support and its schemas are ready if the owner reopens O10.

## Next safe action

The refactor's consumer side is complete. Resume only for:

1. a new handoff — run `make intake`, then work from the pinned snapshot;
2. owner-authorised evidence promotion — write a change set and run `scripts/new_entity.py apply`;
3. the owner reopening O10 in the producer's session — then verify the first v1 handoff end to end and, only
   after that, retire legacy support.

## Rollback

- Batch P can be rolled back with `git revert` of its commits on `main`; the private originals stay in the
  private repository.
- The private repository can be re-verified at any time: `shasum -a 256 -c MANIFEST.sha256` inside `private/`.
