# 2026-07-30 — Repository connectivity and completeness audit

## Question

Are all YAML entities connected correctly, and is any required link or field
missing? This is a data-integrity review, not a record search.

## Method

`uv run --frozen make check` is green (58 tests; 116 entities; 0 errors/0
warnings). The schema validator (`scripts/validation/`) already resolves every
reference and enforces chronology, evidence gates, privacy and place-hierarchy
rules. It does **not** enforce two things, which this audit covered with a
throwaway cross-reference script:

1. **Reciprocity** — a link declared on one side must appear on the other:
   person.`family_ids` ↔ family `partners`/`children`; person.`event_ids` ↔
   event `participants`; person.`fan_references` ↔ FAN `participants`.
2. **Completeness / orphans** — nationality present on deceased people; a
   person who is the *subject* of an own birth/death record having the matching
   event; and dangling people/events/places/sources.

The audit iterated every (entity, reference) pair; the reciprocity checks are
exhaustive, so a single reported failure means the convention holds everywhere
else.

## Findings

### Fixed — 1 structural defect

- **P-0021 and P-0022 omitted E-0007.** Both are `parent`-role participants in
  their child **P-0011**'s 1904 birth (E-0007, CIV-0007) but did not list E-0007
  in `event_ids`. Every other participant↔event pair in the repository
  reciprocates (e.g. the parents in the marriage E-0004 all list it), so this
  was the lone anomaly. Added E-0007 to both people's `event_ids` (ascending
  order, before their own births E-0008/E-0009).

### Verified deliberate — not defects

- **13 "vital-event" flags.** The heuristic flags anyone *linked* to a civil or
  parish source without a birth/death event. Classified against each source's
  subject:
  - *Marriage-only subjects* (already have a marriage/"other" event, no
    birth/death record exists): P-0004/P-0005 (E-0002), P-0012/P-0013 (E-0001),
    P-0019/P-0020 (E-0006).
  - *Named relatives, not the record's subject* — appear only as a parent or
    widow(er) in someone else's birth/death record: P-0009 (Geraldo's death
    CIV-0003), P-0010 (CIV-0002), P-0016/P-0017 (Aristão's death CIV-0005 and
    Marfiza's death CIV-0013), P-0028–P-0031 (the Bohrer deaths CIV-0014/0015
    and Eunir's birth CIV-0016).
  Cross-check: every person who *is* the subject of an own birth/death record
  does have the matching event (P-0004, P-0008, P-0011, P-0014, P-0015, P-0021,
  P-0022, P-0023–P-0026, P-0006, P-0007). The P-0014/P-0015 gap that motivated
  the person-completeness checklist is the only prior instance, already fixed.

- **7 sources cited in no structured `source_ids`.** All deliberate:
  - **CIV-0013, GOV-0002** name Simplício/Eliza with fuller/variant forms their
    person notes explicitly treat as uncatalogued leads — so they are correctly
    not wired into the accepted `Simplicio Armand`/`Eliza Ferreira Armand`
    variants.
  - **PUB-0001, PUB-0002** are published genealogies (weak standalone); correctly
    not backing any conclusion.
  - **PRB-0001, PRB-0002, PRB-0004** support P-0027's account in prose because
    STATUS withholds the Toledo edges until the intervening generation is named.

- **P-0027 (Mathilde) has no `family_ids`.** Deliberate and documented in its
  notes: the intervening Toledo generation is unnamed, so the link to P-0017 is
  prose-only with no Ahnentafel position, "before creating any edges."

- **P-0019 (João Monis Bittencourt) has no `nationality`.** Intentional — origin
  unresolved. Added a note tying the omission to material conflict 6 (was
  previously silent about the field).

- **FAN back-links absent** for P-0016 (FAN-0002–0009) and P-0008
  (FAN-0010–0013). `fan_references` is optional per `data/README.md`; the FAN→
  person direction (`participants`) is present. No change.

- **Reciprocity elsewhere:** person↔family (both directions), all other
  person↔event pairs, all 9 places referenced, every source's `digital_file`
  present with matching checksum — all clean.

## Result

`make check` green after the fix (58 tests, 116 entities, 0/0). Viewer index
unchanged (it does not key on `event_ids`). One data edit (E-0007 back-links),
one documentation note (P-0019), no genealogical conclusions changed.

## Recommended follow-up (not done)

A `validate_event_reciprocity` rule (and its person↔family analogue) would catch
this class mechanically. It is low-risk because it is purely structural, unlike
the completeness checklist, which cannot be automated cleanly (a source's
`linked_people` does not distinguish the record's subject from named parents).
Deferred pending owner decision.
