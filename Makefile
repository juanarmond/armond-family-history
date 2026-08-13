.PHONY: check test validate profiles-audit ancestors-audit drop-pages-audit export export-bundle export-legacy

PYTHON ?= python3

check: validate test

validate:
	$(PYTHON) scripts/validate_data.py

# Advisory (local-only): flag modelled-person profiles that lag the retrieval
# drop's FINDINGS/profiles. The drop is gitignored, so this is not part of
# `make check`; run it when processing a drop. Exits 0 unless --strict.
profiles-audit:
	$(PYTHON) scripts/profile_sync_audit.py

# Advisory: flag people who are the subject of their own vital record but have no
# parentage family — candidates whose record may name parents/grandparents still to
# be modelled (AGENTS.md, Entity connectivity). Heuristic; exits 0 unless --strict.
ancestors-audit:
	$(PYTHON) scripts/ancestor_gap_audit.py

# Advisory (local-only): by sha256, catch a catalogued source/FAN that is missing pages
# still sitting in the retrieval drop — the "the deed has 3 pages but only 1 shows" gap
# the validator cannot see. Run after every drop. Exits 0 unless --strict.
drop-pages-audit:
	$(PYTHON) scripts/drop_page_audit.py

test:
	$(PYTHON) -m unittest discover -s tests -v

# Full-backup GEDCOM 7.0 export (everything, no redaction). The .ged references
# the scans in evidence/ and is committed to the repo as a backup.
export:
	$(PYTHON) scripts/export_gedcom.py

# GEDZIP (.gdz): one portable ZIP packaging the GEDCOM plus the actual scan
# files, for an off-repo backup. Not committed (it duplicates evidence/ bytes).
export-bundle:
	$(PYTHON) scripts/export_gedcom.py --bundle \
		--output export/armond-family-history.gdz

# Legacy GEDCOM 5.5.1 export for the widest commercial-site import support.
export-legacy:
	$(PYTHON) scripts/export_gedcom.py --gedcom-version 5.5.1 \
		--output export/armond-family-history-5.5.1.ged
