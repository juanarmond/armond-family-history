# GEDCOM export — design

Status: **implemented** — `scripts/export_gedcom.py`, `make export` /
`make export-public` / `make export-legacy`. This document specifies how the
canonical YAML data model is exported to a portable, interoperable genealogy
file, and — as importantly — what is deliberately withheld to honour the
repository's privacy contract ("the record is exportable, the scan is never
exported").

## 1. Target and shape

- **Format:** FamilySearch GEDCOM, UTF-8, text-only. Default **7.0** (the current
  standard, read by Gramps and FamilySearch), with **5.5.1** available via
  `--gedcom-version 5.5.1` / `make export-legacy` for the widest commercial-site
  import support. No media bundling (GEDZIP) in either — that is exactly what the
  privacy model wants. Version differences are handled in code (§7).
- **Entry point:** `scripts/export_gedcom.py`, reading the same YAML through the
  loader `scripts/validate_data.py` already uses, so the export can never drift
  from validated data.
- **Harness:** `make export` → `export/armond-family-history.ged`. The `export/`
  directory is **gitignored**: the YAML is the source of truth; the `.ged` is a
  regenerated derivative.
- **Guardrail:** a unit test in `make check` that scans the generated output, in
  every version and living mode, for forbidden tokens (any `evidence/` path,
  `repository_path`, `sha256`, transcription text, RG/CPF digit patterns) and for
  well-formedness (level continuity, no dangling pointers). The privacy rule is a
  test, not a promise.

## 2. Entity → record mapping

| YAML | GEDCOM | Notes |
|---|---|---|
| `P-0001` | `INDI @P0001@` | xref = ID minus the dash |
| `preferred_name` | `NAME Given /Surname/` | full name preserved verbatim; surname = best-effort last token (see §6) |
| `name_variants[]` | additional `NAME` with `TYPE aka`/`AKA` | each cited; `AKA` in 7.0 |
| `sex` | `INDI.SEX` `M`/`F`/`U` | also assigns the family's `HUSB`/`WIFE` |
| `privacy` | `RESN privacy`/`PRIVACY` when living | drives redaction (§4); `PRIVACY` in 7.0 |
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

## 3. What is deliberately NOT exported

GEDCOM makes multimedia (`OBJE`) and source transcription (`TEXT`) **optional**,
so omitting them is fully standards-compliant — this is a privacy *policy*, not a
deviation from the standard.

- **`digital_file` / `evidence/` paths → nothing.** No `OBJE` records are ever
  emitted. This is the code-level enforcement of "scans never leave", and the
  reason the export is text-only.
- **`transcription` → excluded by default.** Full transcriptions can carry RG
  numbers, addresses, and signatures. The citation carries `abstract` (curated)
  plus the archival reference, not the raw transcription.
- **`private: true` sources → citation shell only.** The assertion stays sourced
  (archive / book / folio), but transcription, `repository_path`, and
  `digital_file` are suppressed.
- **`rejected` events / relationships → omitted.** They are disproven; a GEDCOM
  consumer treats every line as asserted fact, so exporting them would
  misrepresent.

## 4. Redaction rules (living people)

The `--living` mode controls how living people (`privacy: living` or `unknown`,
treated conservatively as living) appear:

- **`full` (default, `make export`)** — everything, including living people's
  vitals. This is a **private local backup**; do not upload it to an online tree.
- **`redact` (`make export-public`)** — emit a minimal privatized `INDI`:
  `NAME Living /Surname/`, `RESN privacy`, and the `FAMC` / `FAMS` links **only**;
  no dates, places, occupations, citations, name variants, or notes. Keeps the
  tree connected without leaking the living person's own record.
- **`omit`** — drop the living person's node entirely (and any child/partner link
  to it), for a fully public tree.

**Caveat — redaction is not a name scrub.** `redact` / `omit` anonymise a living
person's *own* record; they do **not** rewrite researcher-authored free text
elsewhere (a deceased relative's note, or a source title such as "birth
certificate of <living person>"). A truly public file still needs a human review
pass. The tested, guaranteed properties are: no `evidence/` path, transcription,
`digital_file`, or `repository_path` in *any* mode, and the living person's own
`NAME`/vitals absent under `redact` / `omit`.

## 5. Confidence handling (Genealogical Proof Standard honesty)

GEDCOM has no first-class confidence model beyond the citation `QUAY` (0–3):

- `confirmed` → `QUAY 3`; `strong-evidence` → `QUAY 2`; `hypothesis` → `QUAY 1`.
- **Caveat:** `QUAY`'s standard meaning is *evidence quality* (3 = primary/direct,
  2 = secondary, 1 = questionable, 0 = unreliable), not *conclusion confidence*.
  Mapping our confidence status onto it is a pragmatic interpretation —
  syntactically standard, semantically approximate.
- **Default export includes hypotheses, flagged.** `hypothesis` edges carry
  `QUAY 1` and a `NOTE: unproven hypothesis` so a downstream tree cannot silently
  harden a guess into fact; `--exclude-hypotheses` drops them entirely.
  `rejected` edges are never exported.

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
`TYPE aka`, and `CONC`-wrapped long lines with parenthetical date phrases. Both
are text-only; GEDZIP is never used, because bundling media is precisely what the
privacy model forbids.

## 8. Decisions (resolved)

1. **Version:** GEDCOM **7.0** by default (`make export`); **5.5.1** via
   `make export-legacy` / `--gedcom-version 5.5.1` for commercial-site upload.
2. **Living people:** shown in **full** by default (`make export`, a private local
   backup); `make export-public` redacts them for sharing.
3. **Hypotheses:** included and flagged (`QUAY 1` + an "unproven hypothesis" note);
   `--exclude-hypotheses` drops them.
4. **Sex field:** added to the person schema (`male` / `female` / `unknown`) and
   populated on every person, fixing `INDI.SEX` and `HUSB` / `WIFE` cleanly.
