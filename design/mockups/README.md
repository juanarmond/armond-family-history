# Viewer mockups

Design references for the family-tree viewer (`family-tree-viewer/`), on phone and desktop.
The rules they follow are in [`../UI-STANDARDS.md`](../UI-STANDARDS.md).

- [`mobile.html`](mobile.html) — every phone screen (390 × 844), with what each one is for.
- [`desktop.html`](desktop.html) — every desktop screen (1440 × 900).
- [`branch-picker.html`](branch-picker.html) — the interactive concept mockup used to design the
  family branches and the phone layout (2026-10-09), kept in step with what shipped.
- `screens/mobile/`, `screens/desktop/` — the screenshots the two galleries show.
- [`capture.mjs`](capture.mjs) — regenerates those screenshots from the real app.

The screens were last captured on 2026-10-09, after every phone screen moved into one frame (top bar
with logo and title or ‹ Back, and ?; bottom bar) and the families chip moved beside the search box.

## Regenerate after a viewer change

```sh
uv run --frozen python scripts/build_pages_site.py   # privacy-filtered build in _site/
node design/mockups/capture.mjs                       # rewrites screens/mobile + screens/desktop
```

Needs Node 22+ and Google Chrome (set `CHROME` to another binary if it is not in the macOS default
location). Update the captions in `mobile.html` / `desktop.html` when a screen's purpose changes,
and add a step to `capture.mjs` for any new screen.

## Privacy and side effects

The screenshots come from the privacy-filtered build in `_site/`, never the raw data, so living
people appear only as "Private living person" — the same as the public site. The capture blocks
the visitor counter, the analytics beacon, the AI assistant Worker and the flag CDN, so a run never
counts as a visit or spends an AI call. It reads the notification Worker's public `/health` only,
so the What's new screen shows its notification bar.
