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
family-tree-viewer/i18n.js
family-tree-viewer/static-api.js
family-tree-viewer/data-loader.js
data/**/*.yaml
```

Do not publish the site publicly while it contains private family data. GitHub Pages access control depends on the account and organisation plan.

## Behaviour

- Starts with `P-0001` when that person exists.
- Allows any structured person to become the tree root; double-click a card to re-centre on that person.
- Renders ancestors recursively from family relationship entities.
- Marks co-parents who share a family with a marriage marker (`⚭` and year) on the lineage junction.
- Prevents recursive loops and marks repeated ancestors as references.
- Distinguishes confirmed, strong-evidence, hypothesis and rejected relationships, and matches the connector line style to the legend.
- Hides rejected relationships by default.
- Limits the displayed number of generations for usability.
- Auto-fits the tree to the viewport, with manual zoom (buttons, `Ctrl`/`⌘`+scroll) and drag-to-pan.
- Links each non-private evidence file and external record from the detail panel, and surfaces each source's form, quality, transcription, abstract and reliability limitations.
- Lists the FAN / context references a person appears in (witness, appraiser, creditor, attorney, party or co-owner), with the person's role, record category, place, image link and transcription.
- Shows each person's nationality on the card (below the name, lifespan and birthplace) and in the details overview, from the person record's `nationality` field.
- Encodes the current root, generation depth, hypothesis toggle and selected person in the URL hash, so a view is bookmarkable and shareable.
- Minimises details shown for living people, and never lists a living person's sources.
- Lets a viewer follow one family branch, several, or everything ("the four rivers": each of the subject's four grandparents heads a branch of their ancestors, plus the deceased children of every couple in it and those children's spouses). A first-visit question offers Everything first and pre-selected; afterwards a chip (header on a phone, toolbar on desktop) opens a sheet to switch branches and copy a share link (`#branch=muniz,bohrer`). The choice scopes search (with a count of matches elsewhere), the tree's starting person, the phone home screen and its surname index, What's new and the Family Story's chapter order. The branch roots, labels and colours live in `branches.js`; membership is derived from the tree.
- On a phone, every screen shares one frame: a top bar (the logo and title on a main screen — tapping them reopens the family question — or ‹ Back once you go deeper; ? explains the screen on top; the family question adds EN | PT) and a bottom tab bar (Family · What's new · Story · Ask AI) with an unread count on What's new for curated entries. Pages open between the two bars and have no × of their own; the families chip sits beside the search box. Person pages, the portrait, the story and the assistant keep their desktop design.
- Offers the interface in English and Brazilian Portuguese (pt-BR), defaulting to the browser language and falling back to English; the choice persists (localStorage) and is encoded in the URL hash. Only the UI chrome and controlled labels (event types, statuses, privacy) are translated — record content (names, transcriptions, places, record types) always displays exactly as recorded.

## Architecture

```text
data/**/*.yaml
      ↓
data-loader.js (read-only browser projection; parses YAML with the vendored js-yaml)
      ↓
branches.js (family branches, scopes, surname index — pure, tested under Node)
      ↓
app.js + index.html + styles.css
```

The browser builds the presentation model in memory. YAML remains the sole persistent source of truth. `js-yaml` is vendored locally in `vendor/js-yaml.mjs`, so the viewer makes no external network requests and works fully offline.

## Entity discovery

The loader reads `entity-index.json`, which enumerates every entity ID. Regenerate it from the canonical directories with `python3 scripts/build_viewer_index.py`. `tests/test_viewer_index.py` fails the build if the committed index drifts from the YAML files in `data/`.

## Security

This viewer is intended for the private repository. It links to the original evidence files and external record URLs recorded in each source, and it can display private, living-person-sensitive documents; every linked file carries a `Private` marker. Living-person details are reduced before display and their sources are never listed. Do not expose the repository or viewer publicly without a separate privacy review, and do not serve it on an untrusted host while it links to private evidence.
