# Family Tree Viewer

A private, read-only visualisation of the structured genealogy data in this repository.

The viewer is fully static. It reads the canonical YAML entities directly in the browser and does not run an application server, maintain a second genealogy dataset or modify any source, person, family, event or place record.

## Run locally

Browsers block local `fetch()` calls from `file://`, so serve the repository with any static file server.

From the repository root:

```console
python3 -m http.server 8765
```

Then open:

```text
http://127.0.0.1:8765/family-tree-viewer/
```

Stop the static server with `Ctrl+C`.

No Python application or API is involved. The command above only serves repository files over HTTP.

## Static hosting

The directory can be hosted by GitHub Pages or another static host. The viewer loads:

```text
family-tree-viewer/index.html
family-tree-viewer/styles.css
family-tree-viewer/app.js
family-tree-viewer/static-api.js
family-tree-viewer/data-loader.js
data/**/*.yaml
```

Do not publish the site publicly while it contains private family data. GitHub Pages access control depends on the account and organisation plan.

## Behaviour

- Starts with `P-0001` when that person exists.
- Allows any structured person to become the tree root.
- Renders ancestors recursively from family relationship entities.
- Discovers newly catalogued sequential entity IDs automatically; no viewer-code change is required.
- Prevents recursive loops and marks repeated ancestors as references.
- Distinguishes confirmed, strong-evidence, hypothesis and rejected relationships.
- Hides rejected relationships by default.
- Limits the displayed number of generations for usability.
- Minimises details shown for living people.

## Architecture

```text
data/**/*.yaml
      ↓
data-loader.js (read-only browser projection)
      ↓
app.js + index.html + styles.css
```

The browser builds the presentation model in memory. YAML remains the sole persistent source of truth.

## Entity discovery

The loader follows the repository's stable sequential ID convention and stops after a bounded sequence of missing IDs. This avoids a duplicated manifest while supporting current and future entities. If the repository ever introduces very large intentional ID gaps, replace this strategy with a generated static manifest.

## Security

This viewer is intended for the private repository. It does not load evidence images or full source transcriptions, and living-person details are reduced before display. Do not expose the repository or viewer publicly without a separate privacy review.
