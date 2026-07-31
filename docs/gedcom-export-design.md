# GEDCOM export — design

Status: **implemented** — `scripts/export_gedcom.py`, `make export` /
`make export-public`. This document specifies how the canonical YAML data model
is exported to a portable, interoperable genealogy file, and — as importantly —
what is deliberately withheld to honour the repository's privacy contract ("the
record is exportable, the scan is never exported").

## 1. Target and shape

- **Format:** FamilySearch GEDCOM **5.5.1**, UTF-8, text-only. Maximum
  application compatibility (Gramps, Ancestry, MyHeritage, FamilySearch,
  RootsMagic all read it) and no media bundling — which is exactly what the
  privacy model wants. GEDCOM 7.0 deltas are noted in §7; GEDZIP (media bundle)
  is never used either way.
- **Entry point:** `scripts/export_gedcom.py`, reading the same YAML through the
  loader `scripts/validate_data.py` already uses, so the export can never drift
  from validated data.
- **Harness:** `make export` → `export/armond-family-history.ged`. The `export/`
  directory is **gitignored**: the YAML is the source of truth; the `.ged` is a
  regenerated derivative.
- **Guardrail:** a unit test in `make check` that scans the generated output for
  forbidden tokens (any `evidence/` path, any living person's birth/death date,
  RG/CPF digit patterns). The privacy rule becomes a test, not a promise.

## 2. Entity → record mapping

| YAML | GEDCOM | Notes |
|---|---|---|
| `P-0001` | `INDI @P0001@` | xref = ID minus the dash |
| `preferred_name` | `NAME Given /Surname/` | full name preserved verbatim; surname = best-effort last token (see §6) |
| `name_variants[]` | additional `NAME` with `TYPE aka` | each cited |
| `privacy` | `RESN privacy` when living | drives redaction (§4) |
| `occupations[]` | `OCCU` + `SOUR` | one per entry, cited |
| `event_ids[]` (as principal) | `BIRT` / `BAPM` / `DEAT` / `BURI` / `RESI` … | `DATE` + `PLAC` under the event |
| `family_ids[]` | `FAMC` (child) / `FAMS` (partner) | derived from the family's role for this person |
| `notes[]` | `NOTE` | author prose; `--no-notes` to suppress |
| `F-0011` | `FAM @F0011@` | |
| `partners[]` | `HUSB` / `WIFE` | **needs sex — §6** |
| `children[]` | `CHIL @Pxxxx@` | modelled children only |
| `documented_children[]` | `NOTE` on the FAM | no person ID exists → cannot be a `CHIL` link (§6) |
| family `event_ids` (marriage) | `MARR` `DATE` / `PLAC` | |
| `CIV-0001` etc. | `SOUR @CIV0001@` record | `TITL`←title, `TEXT`←abstract, `REPO`←repository.name, `CALN`←book/vol/page/record_number |
| event/relationship `source_ids` | `SOUR @…@` citation with `QUAY` | confidence → QUAY (§5) |
| `place_id` → place | inline `PLAC` string + `MAP`/`LATI`/`LONG` | 5.5.1 has no place records; places are inline text |

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
- **Default export = confirmed + strong-evidence only.** `hypothesis` edges are
  excluded unless `--include-hypotheses`, in which case they carry `QUAY 1` and a
  `NOTE: unproven hypothesis` so a downstream tree cannot silently harden a guess
  into fact.

## 6. Known structural gaps (decide before the first real export)

1. **No sex/gender field.** GEDCOM's `INDI.SEX` and, critically, `FAM.HUSB` /
   `WIFE` are gendered slots. `partners[].role` is `spouse` / `partner` /
   `parent`, not gendered, so HUSB vs WIFE cannot be assigned cleanly. Options:
   (a) add an optional, source-cited `sex` field to the person schema
   (recommended — sex is a documented vital fact, not a surname inference, and it
   fixes both `SEX` and `HUSB`/`WIFE`); (b) infer from given names (fragile in
   Portuguese); (c) arbitrary-but-stable assignment with a caveat note.
2. **`documented_children` have no IDs.** They are deliberately un-minted people,
   so they cannot be `CHIL @…@` links. They appear as a `NOTE` on the FAM
   ("Documented children not individually modelled: …") — lossless for humans but
   invisible to a consumer app's tree graph. This is the trade-off of the
   documented-child design.
3. **Portuguese compound surnames** make the `/Surname/` slash split a heuristic
   (last token by default). The full `preferred_name` is always preserved as the
   `NAME` value, so nothing is lost even when the split is imperfect.

## 7. If GEDCOM 7.0 is wanted later

Additive only: UTF-8 mandatory (already), richer `SNOTE` / citation structures,
standardized `MAP`. Still text-only for this repository — GEDZIP would **not** be
adopted, because bundling media is precisely what the privacy model forbids. Not
worth targeting first; 5.5.1 buys wider compatibility today.

## 8. Decisions (resolved)

1. **Version:** GEDCOM 5.5.1.
2. **Living people:** shown in **full** by default (`make export`, a private local
   backup); `make export-public` redacts them for sharing.
3. **Hypotheses:** included and flagged (`QUAY 1` + an "unproven hypothesis" note);
   `--exclude-hypotheses` drops them.
4. **Sex field:** added to the person schema (`male` / `female` / `unknown`) and
   populated on every person, fixing `INDI.SEX` and `HUSB` / `WIFE` cleanly.
