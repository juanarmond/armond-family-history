# Next task

## Objective

Run the complete repository health check automatically on GitHub pushes and
pull requests.

## Why this is next

Local validation is comprehensive but voluntary. The repository has a GitHub
remote and no workflow, so invalid schemas, references, privacy state or
allocator regressions could merge without running the test suite.

## Completion criteria

- Add one minimal workflow using the pinned dependency lock.
- Run `make check` on supported Python versions for pushes and pull requests.
- Use least-privilege read-only repository permissions.
- Add concurrency cancellation for superseded runs.
- Document the local/CI parity without duplicating validation policy.
- Validate the workflow syntax and run the complete local check before commit.
- Run the complete repository check before committing.

## External blocker

Actual document cataloguing still requires authorised, privacy-reviewed copies
of the certificates and screenshots described in `CURRENT_STATE.md`.
