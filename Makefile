.PHONY: check test validate export export-public

PYTHON ?= python3

check: validate test

validate:
	$(PYTHON) scripts/validate_data.py

test:
	$(PYTHON) -m unittest discover -s tests -v

# Full GEDCOM 5.5.1 export (living people in full) — a private local backup.
# Do not upload this file to an online tree; use `make export-public` to share.
export:
	$(PYTHON) scripts/export_gedcom.py

# Shareable export: living people redacted to a minimal "Living" node. Their own
# structured record is anonymised; researcher-authored free text elsewhere may
# still name them, so review before publishing (see docs/gedcom-export-design.md).
export-public:
	$(PYTHON) scripts/export_gedcom.py --living redact \
		--output export/armond-family-history-public.ged
