# Repository scripts

## Data validation

Run the full local check:

```console
uv run make check
```

Or run the live-data validator alone:

```console
uv run python scripts/validate_data.py
```

The command exits non-zero on errors. Possible duplicate identities are
warnings because automated merging would risk combining distinct people.

The validator reads repository content and evidence files only to validate
shape, references and checksums. It does not upload, rewrite or generate
genealogical data.
