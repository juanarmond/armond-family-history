.PHONY: check test validate

PYTHON ?= python3

check: validate test

validate:
	$(PYTHON) scripts/validate_data.py

test:
	$(PYTHON) -m unittest discover -s tests -v
