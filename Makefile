.PHONY: check test validate export export-bundle export-legacy

PYTHON ?= python3

check: validate test

validate:
	$(PYTHON) scripts/validate_data.py

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
