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
| P — forward privacy containment | in progress | see below |
| 0 — current-state refresh | pending | |
| 1 — contract alignment and instruction authority (O4) | pending | |
| 2 — producer hardening | pending | producer session |
| 3 — consumer intake validation | pending | |
| 4 — triage, promotion, Channel B | pending | |
| 5 — AI architecture and resilience | pending | |
| 6 — engineering cleanup | pending | |
| 7 — end-to-end audit | pending | |

### Batch P — forward privacy containment

- **Working-tree containment:** commits `5272303` and `6b0e505` on branch `batch-p-privacy-containment`. Living
  people's own documents are held privately (`held_privately` stubs), the six restricted scans are in the
  private store, the GEDCOM is untracked, the site and assistant are scrubbed, and checks are blocking.
- **O9, done:**
  - Created `juanarmond/armond-family-history-private` (private; checked with `gh api`), cloned at `private/`.
  - 26 files plus `MANIFEST.sha256`.
  - A fresh clone matched the manifest and the local store byte for byte.
  - All 22 public references into `private/` resolve with their SHA-256.
- **O7:** release checks, merge, push and external site verification — pending.
- **Residual historical exposure (O8, accepted):** copies committed before 2026-10-11 remain in public history
  and Git LFS. This refactor does not and will not erase them.

## Next safe action

Run the O7 release checks on `batch-p-privacy-containment`:

1. `make check`;
2. `make privacy-audit`;
3. a site build;
4. a notifier dry-run against the live feed.

If they pass, fast-forward `main` and push, then verify the deployed site.

## Rollback

- Batch P can be rolled back with `git revert` of its commits on `main`; the private originals stay in the
  private repository.
- The private repository can be re-verified at any time: `shasum -a 256 -c MANIFEST.sha256` inside `private/`.
