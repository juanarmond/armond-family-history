# UI & Layout Standards (enforce strictly)

These rules govern every change to the viewer (`family-tree-viewer/`) and its references
(`design/mockups/`). If a change would break one, stop and ask the owner first.

## Stack

- Plain HTML, CSS and JavaScript ES modules — no framework, no build step. A static PWA on GitHub
  Pages: `index.html`, `app.js`, `branches.js`, `data-loader.js`, `i18n.js`, `styles.css`, `sw.js`.
- Logic with no screen of its own goes in a pure module with a Node test (`branches.js`,
  `data-loader.js` → `tests/js/`); `app.js` only draws.
- No external fonts, CDNs or trackers. Network calls go only to the project's own Workers
  (assistant, notify, visitor counter) and Cloudflare Analytics.

## Phone layout (≤ 700px) — one frame everywhere

- Every screen sits between two fixed bars:
  - **Top bar** (`.site-header`, `--header-h`): left — the logo and "Quatro Rios" on a main screen,
    or **‹ Back** once deeper; right — **?**, which opens help for the screen on top
    (`currentHelpTopic()`). The family question adds **EN | PT**.
  - **Bottom bar** (`#tabbar`, `--tabbar-h`): Family · What's new · Story · Ask AI.
- Main screens: Home, What's new, Story, Ask AI. Deeper screens: person view, person page, More
  details, a record, help, surname lists — **‹ Back** (`goBack()`) closes the top one, one level at
  a time.
- Pages open *between* the bars (`top: var(--header-h)`; `bottom: var(--tabbar-h)`). Only the
  family question (the start page) and the families sheet (which has its own Done) may cover the
  bottom bar.
- Phone pages carry no close (×), help or Ask AI buttons of their own — the bars provide them. Mark
  such desktop controls `desktop-only` and the bars' controls `phone-only`; never hide them one by one.
- The families chip sits beside the search box, never in the top bar; the title must always fit in
  full.
- A new screen needs an entry in `LAYERS` (`app.js`): how to tell it is open, how ‹ Back closes it,
  and its help topic. Pages share one rule in the phone section of `styles.css` — add the new panel
  to it rather than giving it its own geometry; stacking uses the `--z-*` scale.

## Desktop layout (> 700px)

- Masthead → toolbar (Families · Start person · Generations · Find a person · Language · Reset view ·
  What's new · Family Story) → tree.
- Panels keep their desktop controls (×, ?, robot): the person page and What's new are side drawers;
  the Story is a centred card; ? and the Ask AI pill float at the bottom.
- The phone frame must not leak into desktop: phone rules live inside `@media (max-width: 700px)`.

## Theme — only the `:root` variables in `styles.css`

- Parchment `--paper` / `--paper-2`; cards `--card` / `--card-2`; text `--ink` / `--ink-2` /
  `--muted` / `--faint`; lines `--rule` / `--rule-strong`.
- Brand `--green` / `--green-deep` and `--gold` / `--gold-soft`.
- Evidence colours — **only** for how well something is proven: `--confirmed`, `--strong`,
  `--hypothesis`, `--conflict`.
- Family colours live only in `BRANCHES` (`branches.js`), applied as `--b`, and must never resemble
  an evidence colour.
- Fonts: `--serif` for names, headings and reading text; `--sans` for labels, buttons, tags and
  small print.
- Shape: `--radius-sm` (rows, inputs), `--radius` (blocks), `--radius-lg` (cards, sheets), `999px`
  (chips, pills, tags); shadows `--shadow-xs` / `--shadow-sm` / `--shadow-md` / `--shadow-lg`.
- Fields and chips use `--field`; the unread count uses `--badge`. No raw colour values in new CSS.

## Components

- **Container card:** `background: var(--card); border: 1px solid var(--rule); border-radius:
  var(--radius-lg); box-shadow: var(--shadow-sm)`.
- **Person row** (`mobileRelationRow`, search results — built by `fillPersonRow`): two lines — the
  name across the full width with the **flag aligned right** on its line; beneath, the years (small,
  muted) with the **family tag aligned right**; a chevron when tappable. Flags and tags so form two
  tidy columns down a list. Never "…" on a name. Headers (the person page title, the person-view
  card) keep the tag beside the dates, and What's new keeps its tags in the entry's meta line.
- **Family tag** `branchTagsFor()`; **evidence badge** `createBadge()` — never mix them.
- **"These families · N / Everything · M"** — `scopeSwitch()`, for any list that can be scoped.
- **Buttons:** primary green full-width pill (`.branch-cta`); secondary outlined pill
  (`.update-chip`, `.home-browse`); round **?** in the bars.
- Touch targets at least `2.75rem`; phone inputs at 16px so iOS does not zoom.

## Text and language

- Every visible word is an `i18n.js` key, added in English **and** pt-BR together. Record content
  (names, transcriptions, places, record types) is never translated.
- Living people appear only as "Private living person"; relationship headings say "the archive's
  owner", never his name.
- Help must match the screen exactly: when a control moves, is renamed or is removed, update its
  help text in the same commit. Claim only what the app does (flags show recorded nationality, not
  birthplace).
- Numbers and years shown or shared publicly come from tested functions (`branches.js`) and claim no
  more than the evidence: a "since" or "back to" year counts only confirmed or strong-evidence events
  resting on an original record (never a published genealogy or a recollection alone), and people
  counts never include the living.

## Forbidden without the owner's explicit approval

- Changing the navigation pattern: the two bars, the four tabs, how ‹ Back works, the logo returning
  to the family question, Everything first and pre-selected.
- Moving the families chip, bringing × or robot buttons back on phone pages, or adding a third kind
  of top bar.
- Colours, fonts or shadows outside the variables; new external services.
- Removing a screen's ? help, or shipping English text without its Portuguese.

## Verification before any UI commit

1. `uv run --frozen make check` and `node --test tests/js/*.test.mjs` are green (they include
   EN/PT key parity).
2. Build the privacy-filtered site (`uv run --frozen python scripts/build_pages_site.py`) and check
   **390×844** and **360×760** (phone: both bars, no sideways scroll, full title, no "…" on names)
   and **1440×900** (desktop: no phone frame).
3. Check both languages — Portuguese is often 20–30% longer.
4. Re-run `node design/mockups/capture.mjs`; update the captions in `mobile.html` / `desktop.html`,
   the concept mockup (`branch-picker.html`) and the "last captured" line in
   [`mockups/README.md`](mockups/README.md) to match what shipped.
5. Describe the change in `family-tree-viewer/README.md` and `CHANGELOG.md`.
