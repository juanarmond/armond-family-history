# GEDCOM export — design

Status: **implemented** — `scripts/export_gedcom.py`, `make export` /
`make export-bundle` / `make export-legacy`. This document specifies how the
canonical YAML data model is exported to a portable genealogy file. The export is
a **full backup**: everything, no redaction. The repository is private and already
holds the scans, so the `.ged` is committed as an in-repo backup rather than
treated as a shareable artifact.

## 1. Target and shape

- **Format:** FamilySearch GEDCOM, UTF-8. Default **7.0** (the current standard,
  read by Gramps and FamilySearch), with **5.5.1** via `--gedcom-version 5.5.1` /
  `make export-legacy` for the widest commercial-site import. The `.ged` is text
  that *references* scans; `make export-bundle` additionally packages the scan
  files into a GEDZIP (§4). Version differences are handled in code (§7).
- **Entry point:** `scripts/export_gedcom.py`, reading the same YAML through the
  loader `scripts/validate_data.py` already uses, so the export can never drift
  from validated data.
- **Harness:** `make export` → `export/armond-family-history.ged`, **committed** as
  an in-repo backup (it references the `evidence/` scans already in the repo).
  GEDZIP bundles (`.gdz`) and the 5.5.1 file stay gitignored — generate on demand.
  The YAML is the source of truth; regenerate the `.ged` to refresh the backup.
- **Guardrail:** a unit test in `make check` asserting the full export carries the
  private detail (transcriptions, `OBJE` scan references, hashes), that rejected
  edges are flagged not asserted, that every output (7.0 and 5.5.1) is well-formed
  (level continuity, no dangling pointers), and that a GEDZIP round-trips (holds
  `gedcom.ged` plus the packed scans).

## 2. Entity → record mapping

| YAML | GEDCOM | Notes |
|---|---|---|
| `P-0001` | `INDI @P0001@` | xref = ID minus the dash |
| `preferred_name` | `NAME Given /Surname/` | full name preserved verbatim; surname = best-effort last token (see §6) |
| `name_variants[]` | additional `NAME` with `TYPE aka`/`AKA` | each cited; `AKA` in 7.0 |
| `sex` | `INDI.SEX` `M`/`F`/`U` | also assigns the family's `HUSB`/`WIFE` |
| `privacy` | `RESN privacy`/`PRIVACY` when living | truthful marker, not redaction; `PRIVACY` in 7.0 |
| `occupations[]` | `OCCU` + `SOUR` | one per entry, cited |
| `event_ids[]` (as principal) | `BIRT` / `BAPM` / `DEAT` / `BURI` / `RESI` … | `DATE` + `PLAC` under the event |
| `family_ids[]` | `FAMC` (child) / `FAMS` (partner) | derived from the family's role for this person |
| `notes[]` | `NOTE` | author prose; `--no-notes` to suppress |
| `F-0011` | `FAM @F0011@` | |
| `partners[]` | `HUSB` / `WIFE` | **needs sex — §6** |
| `children[]` | `CHIL @Pxxxx@` | modelled children |
| `documented_children[]` | synthetic minimal `INDI` + `CHIL`/`FAMC` | export-only node, xref `@DOC…@` (§6) |
| family `event_ids` (marriage) | `MARR` `DATE` / `PLAC` | |
| `CIV-0001` etc. | `SOUR @CIV0001@` record | `TITL`←title, `TEXT`←abstract, `REPO`←repository.name, `CALN`←book/vol/page/record_number |
| event/relationship `source_ids` | `SOUR @…@` citation with `QUAY` | confidence → QUAY (§5) |
| `place_id` → place | inline `PLAC` string + `MAP`/`LATI`/`LONG` | places are inline text (no place records in either version) |

**Date mapping** (`common.date` kinds → GEDCOM `DATE`):

| kind | GEDCOM |
|---|---|
| `exact` | `15 SEP 1930` |
| `month` | `SEP 1930` |
| `year` | `1930` |
| `approximate` | `ABT …` |
| `before` | `BEF …` |
| `after` | `AFT …` |
| `range` | `BET … AND …` |
| `inferred` | `EST …` |
| `conflicting` / `unknown` | omit `DATE`; keep an explanatory phrase `(…)` |

## 3. What the full backup contains

There is no redaction: `make export` emits everything, including material GEDCOM
treats as optional.

- **Living people in full.** Their vitals, names and links are exported as-is; a
  `RESN PRIVACY` marker is still emitted (truthful metadata, hiding nothing).
- **Scans as `OBJE`.** Each source with a `digital_file` becomes an `OBJE`
  referencing its `evidence/…` path — a 7.0 `OBJE` record plus a `1 OBJE` pointer,
  or a 5.5.1 inline `OBJE`/`FILE`/`FORM` — with media type, title and sha256. The
  `.ged` *references* the scans; `make export-bundle` packages the bytes (§4).
- **Transcriptions and private references** — the source `transcription`,
  `catalogue_reference` and `repository_path`, as `NOTE`s.
- **`rejected` edges, flagged.** A disproven event/relationship is emitted with
  `QUAY 0` and a `REJECTED` note, never as a plain fact (a reader treats unflagged
  lines as true).

Because the repository is private and already holds the scans and identifiers,
this file is an in-repo backup, not a shareable artifact. Referencing (not
embedding) media is standards-compliant; the GEDZIP bundle (§4) is the portable,
self-contained form.

## 4. GEDZIP bundle (`make export-bundle`)

`make export-bundle` writes a **GEDZIP** (`.gdz`): one ZIP holding the GEDCOM as
`gedcom.ged` plus every referenced scan at its `evidence/…` path, so the tree and
its images travel as a single portable file. GEDZIP is a 7.0 facility. The bundle
is not committed (it would duplicate the scan bytes already under `evidence/`);
generate it on demand for an off-repo backup. A referenced scan missing from disk
is reported, not fatal.

## 5. Confidence handling (Genealogical Proof Standard honesty)

GEDCOM has no first-class confidence model beyond the citation `QUAY` (0–3):

- `confirmed` → `QUAY 3`; `strong-evidence` → `QUAY 2`; `hypothesis` → `QUAY 1`.
- **Caveat:** `QUAY`'s standard meaning is *evidence quality* (3 = primary/direct,
  2 = secondary, 1 = questionable, 0 = unreliable), not *conclusion confidence*.
  Mapping our confidence status onto it is a pragmatic interpretation —
  syntactically standard, semantically approximate.
- **Hypotheses and rejected edges are included but flagged.** `hypothesis` edges
  carry `QUAY 1` and an "unproven hypothesis" note (`--exclude-hypotheses` drops
  them); `rejected` edges carry `QUAY 0` and a `REJECTED` note. Neither is emitted
  as a plain fact, so a downstream tree cannot silently harden a guess or a
  disproven claim into truth.

## 6. Structural gaps — resolved

1. **Sex/gender — closed.** An optional `sex` field (`male` / `female` /
   `unknown`) was added to the person schema and populated on every person,
   fixing both `INDI.SEX` and the family's `HUSB` / `WIFE` assignment. It is
   derived from each person's cited vital records and documented spousal/parental
   role, never from a surname.
2. **`documented_children` — closed the standard way.** Each attested collateral
   child (which has no repository person ID) is exported as a **synthetic minimal
   `INDI`** (`NAME`, `SEX U`, `FAMC`, a documented-child `NOTE` with its
   `source_ids`) and linked as a real `CHIL` on the family. The xref is
   export-only (`@DOC<family>_<n>@`); no person entity is minted, so the data
   model stays clean while the tree graph is complete in consumer apps.
3. **Portuguese compound surnames — not a standards gap.** The `/Surname/` split
   is a last-token heuristic, but the full `preferred_name` is always the `NAME`
   value, which is valid GEDCOM. Precise `SURN` on compound names would need an
   explicit surname field; deferred until it matters.

## 7. Version handling (7.0 default, 5.5.1 available)

The exporter emits either version from the same data. Differences handled in
code: **7.0** uses `GEDC.VERS 7.0`, no `CHAR`, BCP-47 `LANG pt-BR`, uppercase
`RESN PRIVACY`, `NAME.TYPE AKA`, no `CONC` (long lines are unwrapped), and date
`PHRASE` substructures for fuzzy dates. **5.5.1** uses `GEDC.VERS 5.5.1` +
`FORM LINEAGE-LINKED`, `CHAR UTF-8`, `LANG Portuguese`, lowercase `RESN privacy`,
`TYPE aka`, and `CONC`-wrapped long lines with parenthetical date phrases. Scan
media is inline `OBJE` in 5.5.1 and `OBJE` records in 7.0; the GEDZIP bundle (§4)
is 7.0-only.

## 8. Decisions (resolved)

1. **Version:** GEDCOM **7.0** by default (`make export`); **5.5.1** via
   `make export-legacy` / `--gedcom-version 5.5.1` for commercial-site upload.
2. **No redaction — full backup.** `make export` emits everything (living people
   in full, scans as `OBJE`, transcriptions, `rejected` edges flagged). The `.ged`
   is committed as an in-repo backup; `make export-bundle` gives a portable GEDZIP.
3. **Hypotheses:** included and flagged (`QUAY 1` + an "unproven hypothesis" note);
   `--exclude-hypotheses` drops them.
4. **Sex field:** added to the person schema (`male` / `female` / `unknown`) and
   populated on every person, fixing `INDI.SEX` and `HUSB` / `WIFE` cleanly.
