# Family Tree Viewer

A private, read-only visualisation of the structured genealogy data in this repository.

The viewer reads the canonical YAML entities at request time. It does not create or maintain a second genealogy dataset, and it does not modify any source, person, family, event or place record.

## Run locally

From the repository root:

```console
uv run python family-tree-viewer/server.py
```

Then open:

```text
http://127.0.0.1:8765
```

The server binds to the local machine only. Stop it with `Ctrl+C`.

## Behaviour

- Starts with `P-0001` when that person exists.
- Allows any structured person to become the tree root.
- Renders ancestors recursively from the family relationship entities.
- Adds newly catalogued people and relationships automatically; no viewer code change is required.
- Prevents recursive loops and marks repeated ancestors as references.
- Distinguishes confirmed, strong-evidence, hypothesis and rejected relationships.
- Hides rejected relationships by default.
- Limits the displayed number of generations for usability.
- Minimises details shown for living people.

## Architecture

```text
data/**/*.yaml
      ↓
family-tree-viewer/server.py
      ↓
read-only /api/tree response
      ↓
index.html + app.js + styles.css
```

The API response is generated in memory on every request. It is a presentation projection, not an exported source of truth.

## Security

This viewer is intended for local use with the private repository. Do not expose the server to the public internet. The server deliberately binds to `127.0.0.1`, and living-person details are reduced before being sent to the browser.
