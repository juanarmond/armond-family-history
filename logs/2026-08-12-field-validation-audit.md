# 2026-08-12 — Field-validation audit (4 parallel agents) + remediation

## Question

After fixing the "Local de nascimento: Não estabelecido" birthplace bug (the
person panel read only `birth`-type events, ignoring baptism), validate **all
viewer-derived fields and all structured data** for other issues of the same
class (data present but not reaching the viewer, or wrong derivation) and any
new integrity issues.

## Method

Four **read-only** parallel audit agents over disjoint scopes, each told the
non-negotiable rules (no fabrication, mark uncertainty, privacy, anti-merge,
verify against the record image/data, do not edit or commit):

1. **Viewer field derivation** — `family-tree-viewer/*.js` vs the data it projects.
2. **`data/people/*.yaml`** — profiles, notes, bilingual parity, citations, links, dates.
3. **`data/families/*.yaml` + `data/events/*.yaml`** — reciprocity, chronology, orphans/dupes.
4. **`data/sources/**` + `data/fan/*` + `data/document-inventory.yaml`** — named-but-not-linked, categories, FAN hygiene.

Every finding was then **re-verified against the code/data by hand** before any
change (audit agents produce false positives): lineages traced through the
family graph, the data-loader role-filter confirmed, the FAN projection path
read.

## Confirmed and fixed

**Viewer (`app.js`, `data-loader.js`, one data-loader test):**
- `lifespan()` (panel-header "YYYY–YYYY") read only `birth`/`death` — the exact
  analogue of the birthplace bug. Added **baptism (start) / burial (end)
  fallback**, matching the biography prose and the fact rows. Restores headers
  for P-0056 (1787–), P-0035 (1835–), P-0078 (1728–), P-0072 (1751–1827),
  P-0073 (1760–1832). Verified with the real role-filtered event logic (the
  data-loader keeps only `principal`/`spouse`/`partner` roles, so P-0078's
  parent-role birth of Rita is correctly excluded → header 1728, not 1764).
- Mobile spouse row passed the marriage **object** to `bioWhen()` (expects a
  date) → marriage year never showed on mobile; now `spouse.marriage.date`.
- **Redact a living person's own events** (birth/death PII) at the data layer,
  closing a latent leak if an event were attached (the 3 living people have
  none today). Locked with a test. **Nationality is deliberately kept for the
  living** (low-sensitivity, already asserted by an existing test) — the audit's
  "gate nationality" suggestion was a false positive against explicit design and
  was reverted after the test caught it.

**Data — relationship labels (prose only, lineages re-verified):**
- **P-0004:** Simplício (P-0016) is Geraldo's **grandfather/avô**, not
  great-grandfather/*bisavô* (Geraldo ← Aristão ← Simplício).
- **P-0059 (Amaro)** & **P-0060 (Ignez):** on **Eliza's father's maternal
  line** (Eliza ← father José Cezário ← his mother Mathilde ← Amaro/Ignez), not
  "maternal."
- **P-0040 (José do Rego Brandão):** Antenor's **paternal** great-grandfather
  (via Antenor's father Deocleciano → his mother Susanna), not "maternal"; the
  "maternal grandfather of Deocleciano" half was correct and left.
- **P-0032:** prose "P-0010 b. c.1895" → **1894** (proven, E-0024/CIV-0002).

**Data — F-0016 double-count:** "Joaquim José Bohrer" was both the modelled
child **P-0030** and a `documented_children` entry, so the viewer rendered him
**twice** in both parents' Children and made **P-0030 his own sibling** (the
roster builder appends documented_children with no de-dup). Removed the
redundant entry (evidence already on P-0030's parent-relationship + family
notes). The 3 never-modelled documented children remain.

**Data — 8 source→person link gaps** (record names a modelled person but
`linked_people` omitted them, so the source did not surface on that person's
page — `data-loader.js:145-146` feeds per-person sources from `linked_people`):
PRB-0009+P-0063, PRB-0002+P-0027, PRB-0004+P-0056, CIV-0014+P-0015,
PAR-0005+P-0045, PAR-0018+P-0078/P-0079 (bride's parents now modelled — stale
"not yet modelled" note corrected), CIV-0006+P-0019/P-0020/P-0039,
NWS-0001+P-0009, PAR-0045+P-0048/P-0049/P-0086/P-0087, PAR-0044+P-0086/P-0087.

**Data — CIV-0006 name conflict preserved:** its 2019 full-content reproduction
reads Luiza's father "Sebastião [uncertain: Manoel] de Azevedo" vs "José
Secundino de Azevedo" (P-0038) in CIV-0001 — same 1916 record. P-0038 left
**unlinked** to this derivative with an explaining note (conflict preserved, not
erased).

## Confirmed clean (verified, not merely unreported)

Full family↔person and event↔participant reciprocity both ways; all relationship
`source_ids` resolve; chronology sane (three auto-flags were prose-year-regex
false positives — no "mother aged 9" class bug); no orphans or duplicate events;
all places resolve; all 84 deceased have matching bilingual `profile`/
`profile_pt`; every note has a real `text_pt`; all name-variant/occupation
citations present; category prefix/folder/`record_category` consistent across 93
sources; all 13 FANs `usage: context`, never cited as evidence. **S12
(FAN back-links) is a non-issue** — the viewer projects FAN associations from
`FAN.participants` (data-loader 334-341), not from `person.fan_references`, so
the 12 FANs without a person back-link still reach their participants' pages.

## Deferred item — subsequently actioned (2026-08-12)

- **Redundant `transcription_pt`** — actioned via 4 parallel agents (each
  verifying byte-identity before deleting). **Removed from 33 records** (20
  sources CIV-0005/0008/0013/0017/0018/0020/0022/0024, GOV-0001,
  PAR-0001/0005/0006/0010/0017/0018/0019/0023/0025/0026, PRB-0006; and FAN-0001…
  FAN-0013) where the only difference was translated editorial framing. **Kept**
  the Italian (CIV-0010/11/12) and Latin (PAR-0027/28/29) originals, and **5
  records whose `transcription_pt` translates substantive editorial/summary prose,
  not just brackets** (PRB-0008, PRB-0009, PUB-0001, PUB-0002, PUB-0003) — removing
  those would strip real bilingual content. Pure deletion (410 lines); every
  `transcription` intact; `make check` green; index and GEDCOM unchanged.

## Result

317 entities; `make check` green (69 Python + JS tests); reciprocity verified;
viewer index unchanged; GEDCOM regenerated (7.0, 4053 lines). No entities
created or removed.
