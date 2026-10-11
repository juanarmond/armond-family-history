# Retrieval integration refactor — consumer implementation

## Question

How does this repository consume the retrieval handoff safely? That means verifying it before reading,
identifying evidence by content, keeping triage durable, applying promotions atomically, and keeping the
producer's text subordinate to this repository's rules. All of it without promoting any real evidence.

## Owner decisions in force (2026-10-11)

- O1–O3 privacy containment and O5 Git/GitHub backup are decided.
- O4 pointer plus accepted SHA-256, O7 release and O9 private repository are approved.
- O8 is closed: no history rewrite; the residual historical exposure is accepted.
- Real evidence promotion stays per-task, owner-authorised.
- Only P-0001–P-0003 are living.

## Done (consumer side)

- **Batch P released.** The private repository was created, pushed and verified from a fresh clone (26 files plus
  manifest; 22 public references resolve by SHA-256). Then `main` was fast-forwarded to `95ebcae` and pushed. No
  family notification was sent: the deploy log reads "No new curated entries". The live site was checked from
  outside: 564 published data files, none containing a private string or a living person's name; restricted
  scans return 404.
- **Instruction authority (O4).** The pasted intake block is replaced by a pointer and
  `research/integration/accepted-intake.json` (pinned SHA-256 `6d8b49ea…`). The authority bound and producer
  vocabulary rule are stated in AGENTS.md and enforced by tests.
- **Intake.** `make intake` pinned the current handoff (legacy manifest, 341 files, digest `828414254673…`). A
  second run is a no-op. The tool accepts contract v1 as soon as the producer ships it.
- **Triage.**
  - 453 ledger rows: 402 map to producer files, giving 840 file entries. 17 more come from holdings, for 857 in
    `data/triage-index.yaml`.
  - 51 rows have no file identity (clusters, items, renamed files without aliases, two unknown ARKs). They stay
    authoritative in the private ledger and are listed in its private migration report; none was discarded.
  - Dispositions follow holdings: a held file is `promoted` or `fan` with its holder as target. A page counted
    inside a promoted set whose own bytes are not held is `reviewed`.
- **Promotion.** `new_entity.py apply` covers change sets, base-hash guards, staged validation with no new
  warnings, journalled exact rollback, `recover`, the lock, idempotence, and evidence copies requiring an owner
  authorisation reference. Synthetic tests only.
- **Tooling.** The audits are retargeted to the producer's scans by content, and fail strict on missing inputs.
  Stale paths are fixed. Pages now deploys through GitHub Actions only.

## Findings for the owner (no action taken)

- **Value-gate backlog.** 292 producer scans have no triage disposition yet (`make triage-audit`).
- **Partly catalogued records.** Three catalogued records hold fewer pages than the producer's record: FAN-0012
  (3 of 72), GOV-0008 (1 of 4), PRB-0009 (3 of 188). These may be deliberate selections from large inventories.
  Completing them would mean promoting real evidence, which is owner-gated.
- **Missing provenance.** Seven FAN scans (FAN-0003 to FAN-0009) have neither an inventory entry nor a producer
  copy, so their provenance row cannot be derived.

## Producer side

The producer's work (staged generation, manifest v1, evidence index, privacy lint, blocking tests, intake-text
fixes) was sent to the retrieval repository's own session, as §14.12 requires. This session neither writes nor
runs Git there. Status is tracked in `research/integration/EXECUTION-RECORD.md`.
