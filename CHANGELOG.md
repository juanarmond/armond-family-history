# Changelog

All notable repository changes are recorded here. Genealogical conclusions must
also remain traceable through source records and research logs.

## Unreleased

### Added

- Add a GEDCOM 5.5.1 exporter (`scripts/export_gedcom.py`, `make export` /
  `make export-public`) that renders the canonical YAML to a portable, text-only
  genealogy file — people, families, events and source *citations*, never scans,
  transcriptions, checksums or `evidence/` paths. Living people are shown in full
  by default (a private local backup) or redacted with `make export-public`;
  hypotheses are included and flagged (`QUAY 1`). Adds
  `tests/test_export_gedcom.py` and `docs/gedcom-export-design.md`; `export/` is
  gitignored.
- Add an optional `sex` field (`male` / `female` / `unknown`) to the person schema
  and template, populated on all 39 people, so the export can set `INDI.SEX` and
  assign a family's `HUSB` / `WIFE`. Derived from each person's cited vital records
  and documented spousal or parental role, never from a name.
- Catalogue two records from the retrieval sync: Cidália's own 1930 birth
  registration (`CIV-0022`, Alvorada) and a third Armond daughter — Aristides
  Ferreira Armand's 1894 marriage to João Rodrigues Braga (`CIV-0023`, Boa Família,
  Muriaé). Cidália's birth confirms her date, parents and all four grandparents;
  Aristides is added as a documented child of Simplício × Eliza (F-0006), a sister
  of Aristão and Marfiza, giving a fourth attestation of Simplício's signed name and
  Eliza's "Elisa Balbina de Jesus" variant. Adds DOC-0033/DOC-0034 and strong
  Simplício-line locality leads (Boa Família/Muriaé 1894; Rio Pardo/Argirita ~1875).
- Add the missing ancestor birth events from records already in hand, so the
  grandparents' and great-grandparents' viewer cards show their dates: Geraldo
  (E-0029, 30 Jan 1915, Rosário da Limeira MG) and Cidalia (E-0030, 15 Sep 1930,
  Alvorada MG) from their 1952 marriage (CIV-0002); and approximate births inferred
  from ages for Aristão (E-0031, c.1879), Deocleciano (E-0032, c.1892, Sapucaia RJ)
  and Luiza (E-0033, c.1898, Muriaé MG). Applies the person-completeness rule
  consistently (as already done for P-0010/P-0014/P-0015).
- Catalogue Liliosa Paz Armond's death (event `E-0028`, 16 April 1946, Eugenópolis)
  from a clearer view of the Geraldo × Cidalia 1952 marriage (CIV-0002), resolving
  the long-open Liliosa death-date gap (material conflict 2) and recording her
  Eugenópolis birthplace; her parents remain the next target (Eugenópolis óbito).
- Ingest Aristides Muniz Bittencourt's 1922 Carangola baptism (`PAR-0003`) from the
  retrieval drop: adds Aristides as a documented child (Antenor's brother) on
  F-0001, establishes Luiza's parents as new ancestors — José Secundino de Azevedo
  (P-0038) and Thereza Fernandes de Azevedo (P-0039), family F-0018 — corroborated
  by CIV-0001, adds Luiza's "Secundina" name variant, and fixes the family's
  Carangola (MG) origin. Plus DOC-0032.
- Record two owner-confirmed documented collaterals: Marfiza Ferreira Armond
  (1873–1962), Aristão's sister, on F-0006 from her 1962 civil death (CIV-0013);
  and Eunir Bohrer (b.1924), Iris's brother, on F-0005 from his 1924 birth
  (CIV-0016). Both now appear in the viewer's Siblings/Children.
- Record Maria Aurora Guimarães's five siblings — José (1901), Maria da Conceição
  (1906), Sebastião (1909), João José (1912) and Maria de Lourdes (1915) — as
  `documented_children` on F-0008 from the same 1915 collective registration
  (CIV-0007) that documents her. A completeness gap found while validating the
  Siblings/Children feature; they now populate her Siblings and her parents'
  Children. Also clarified the Francisco José × Rosa marriage event (E-0026):
  "1879" is only the justificação (upper bound) date — the wedding was decades
  earlier, since their son was already a father by 1890.
- Add a **Children** section to the viewer, mirroring Siblings: a person's
  children — modelled `P-` children plus the family's `documented_children`, with
  possibly-living ones omitted — computed from the families where the person is a
  partner, shown as bullets below Marriages & partners. Reuses the existing
  `documented_children` field (no new data or schema change). Covered by a
  data-loader unit test and en/pt-BR strings.
- Add a **Siblings** section to the family-tree viewer, shown below Parents in a
  person's detail. Siblings are drawn from a new optional `documented_children`
  list on the family schema — attested collateral children (each with
  `source_ids`) that are deliberately not modelled as their own person entities —
  together with any deceased modelled children of the same parents.
  Possibly-living siblings are omitted entirely. Populated for the Bohrer line:
  Celina's sibling Alberto (CIV-0019) and Joaquim José's brother Guilherme Samuel
  (CIV-0019). Covered by a new data-loader unit test and en/pt-BR strings.
- Extend the Bohrer maternal line to Celina's grandparents from three retrieval-drop
  records: Alberto Bohrer's 1890 birth (`CIV-0019`), an 1891 sibling birth
  (`CIV-0020`), and Francisco José Bohrer × Rosa Eugenia de Lemos's 1879 marriage
  (`PAR-0002`, a parish record). Adds four ancestors (P-0034–P-0037), families
  F-0016/F-0017, marriage event E-0026, and DOC-0029–DOC-0031. The grandparent
  links are strong-evidence; Celina's own parentage confidence is unchanged. See
  `logs/2026-07-30-bohrer-maternal-line-extension.md`.
- Catalogue two Engracio-line civil deaths from the retrieval drop: Antonio
  Engracio Filho's 1964 death (`CIV-0017`) and Maria Aurora Guimarães's 1991
  death (`CIV-0018`). Adds death/birth events for P-0010, a death event for
  P-0011, new ancestors P-0032/P-0033 (Cidalia's paternal grandparents) with
  family F-0015, a marriage attestation on F-0012, and DOC-0027/DOC-0028. See
  `logs/2026-07-30-engracio-deaths-ingest.md`.

### Changed

- Codify the "do your work" retrieval-drop cycle in AGENTS.md: orient from
  `FINDINGS.md` + the triage ledger + the CSV before opening images, diff the drop,
  value-gate each new image (leads-not-evidence, privacy, parish-vs-civil, and the
  AI-generated FS-tree-portrait caution), ingest with reciprocal back-references,
  finish with the completion protocol, and end by reviewing the agent's plans and
  FINDINGS to give feedback.
- Resolve material conflict 1: Cidália's own birth registration (CIV-0022) fixes her
  birth at 15 September 1930, superseding the "15 November" variant. Upgraded her
  birth event (E-0030) and her parentage in F-0012 to **confirmed** (direct primary
  from her own birth record).
- Correct and complete CIV-0002 from a clearer alternate view: Cidalia's father is
  named "Antônio Engrácio de Souza" (correcting the earlier obscured "Antonio
  Engracio Filho" reading) with an exact birth 15 June 1894 — refining P-0010's
  birth event E-0024 — and Maria Aurora's birth is confirmed as 1 January 1904.
  P-0010 keeps both name forms ("Filho" distinguishes him from his father P-0032).
- Complete CIV-0006's transcription from the newly synced inteiro-teor images (the
  1916 marriage act was previously "pending, low contrast") and link CIV-0001 to
  Luiza's now-modelled parents (P-0038/P-0039, F-0018).
- Set P-0016's preferred name to "Simplício José Ferreira Armond" (owner-confirmed
  full name) — it matches his autograph signature (PRB-0002) and the two 1880s
  Leopoldina probate records; the shorter source forms "Simplicio Armand" (CIV-0005)
  and "Simplício Ferreira Armond" (CIV-0013) stay as variants. Coverage note and
  the inventory identity label updated to match.
- Transcription deep-dive: verified every source transcription against the images
  where available and confirmed each aligns with the structured entities. Fixed two
  alignment gaps it surfaced — recorded the probate name forms "Simplicio José
  Ferreira Armond" (P-0016, from PRB-0001/PRB-0002, one bearing his autograph
  signature) and "Eliza Balbina de Toledo" (P-0017, from PRB-0001), and added a
  birth event (E-0027) for P-0018 José Olavo Armond (25 Sep 1926, Eugenópolis; per
  GOV-0001 and NWS-0001). Confirmed João Gonçalves Bohrer's death date (CIV-0014,
  3 Aug 1970) and Celina's Nova Friburgo origin (CIV-0016) directly from the images.
- Remove the mistaken "Infant son (1891–1892)" documented child from F-0014: a
  re-read of CIV-0020 shows the child's given name is on an unretained next folio,
  so it was a placeholder, not a record fact (kept as a noted, pending record).
- Mark P-0018 (José Olavo Armond, a granduncle) deceased, per the owner's
  confirmation that everyone from his grandparents' generation back is deceased.
- Record the owner-confirmed fuller name variants "Simplício Ferreira Armond"
  (P-0016) and "Eliza Ferreira Toledo" (P-0017) from CIV-0013, resolving the
  earlier lead caveat; preferred names unchanged pending a decision on the fuller
  forms.
- Document the `documented_children` mechanism in the governance docs: a new bullet
  in AGENTS.md's "Entity connectivity and completeness" protocol and an extension
  to the `data/README.md` person-completeness checklist. Both state that an
  attested collateral child needing no research of its own is recorded as a family
  `documented_children` entry (name + required `source_ids`, deceased only) rather
  than a full person entity, and that the viewer's Siblings and Children sections
  are built from a family's modelled children plus these entries.
- Audit every person for the Selina/Celina class of error (a preferred name less
  supported by primary records than an available variant). Found and fixed one
  analog: P-0011's preferred name changes from "Maria Amora" to "Maria Aurora" —
  three sources including her own 1991 death (CIV-0018) use "Aurora" against a
  single retrospective, certified-copy birth registration (CIV-0007) with the
  unusual "Amora". Also backed P-0027's preferred spelling "Mathilde" with its own
  source variants (PRB-0004/PRB-0002) and documented P-0018's reconstructed
  spelling ("CLAVO" is a misprint for "OLAVO"). No other under-sourced preferred
  name remains.
- Change P-0015's preferred name from "Selina" to "Celina". Three primary civil
  records spell it "Celina" — her own 1977 death (CIV-0015), her husband's 1970
  death (CIV-0014) and Eunir's 1924 birth (CIV-0016) — versus "Selina" only in the
  1949 marriage certificate (CIV-0004) and the owner's family roster (REC-0001).
  "Selina" is preserved as a documented variant; the change is recorded in the
  person's notes.
- Resolve material conflict 10: Maria Amora Guimarães (1904 birth, CIV-0007) and
  Maria Aurora Guimarães (1991 death, CIV-0018) are the same woman — both records
  name identical parents. Both name forms preserved; preferred name kept as Maria
  Amora.

### Removed

- Remove superseded research working files — the old `research/resources/` and
  `research/sources/` caches and `research/PLAN-close-simplicio-gap.md` (replaced by
  the `research/from-retrieval/` workflow) — and a redundant alternate scan of
  CIV-0005 (`evidence/references/…-recapture-spread.pdf`). CIV-0005's note is
  updated: that two-page spread was reviewed and confirmed entry 9890 but is not
  retained (the evidence model keeps one authoritative image per record).

### Fixed

- Restore the P-0021/P-0022 → E-0007 back-links: both parents (Francisco José de
  Carvalho Guimarães and Emmerenciana Maria de Jesus) participate in their child
  P-0011's 1904 birth (E-0007) but had omitted it from their `event_ids`. This
  was the only person↔event reciprocity gap; a full connectivity and completeness
  audit (person↔family, person↔event, person↔FAN, orphan, nationality and
  vital-event coverage) found no other structural defect. See
  `logs/2026-07-30-connectivity-completeness-audit.md`.
- Document that P-0019 (João Monis Bittencourt) carries no `nationality` by
  design — his origin (an unproved Azorean lead versus Brazilian jus soli) is
  unresolved — tying the omission to material conflict 6 rather than leaving the
  field silently blank.

### Changed

- Codify an "Entity connectivity and completeness" protocol in `AGENTS.md` (both
  ends of every family/event/FAN link kept in step; catalogued records reach the
  viewer via events, not prose; deliberate omissions noted) and add a completion
  step to verify reciprocity and completeness beyond `make check`, so the class
  of gap fixed in E-0007 is caught before completion.
- Reflow the viewer toolbar to a flex layout so it accommodates the language
  selector cleanly: all six controls bottom-align on one row, the search field
  absorbs the slack, and Reset stays content-sized (adding the selector had
  pushed Reset onto a full-width second row under the 5-column grid).
- Widen the viewer's header, toolbar and summary to the full width of the tree
  box: raise `--shell-max` to the tree's 150rem cap and align the header/main/
  footer side padding to the tree's 1.5rem margins, so the controls and
  repository tiles line up with the tree instead of sitting in a narrower centred
  column.
- Name FAN reference images by ID only (`FAN-NNNN.<ext>`), dropping the
  descriptive suffix; the date, place, record type and role stay in the FAN
  record. Applies to `evidence/references/` (the FAN folder); the source-folder
  naming convention is unchanged.
- Rename the external record-retrieval workflow throughout the repository to
  "retrieval agent" terminology: the drop folder is now `research/from-retrieval/`,
  alongside the value-gate resume ledger, the 30 July read-pass research log, and
  the prose in `AGENTS.md`, `STATUS.md`, `.gitignore`, `research/README.md` and
  the affected `data/` records. Terminology and paths only; no genealogical data,
  conclusion or evidence changed. The external agent's own config must point at
  the new folder for the rename to persist across syncs.
- Ignore the entire retrieval drop directory `research/from-retrieval/` in one
  rule (previously only `output/`, `README.md` and `resources/` were listed),
  now also covering the `correspondence/` and `plans/` folders, `people.txt` and
  `FINDINGS.md`. The whole area is regenerable working data, not history; valuable
  finds are promoted into `data/`, `evidence/` or `logs/` via the value gate.

### Removed

- Remove the unused `evidence/incoming/` staging folder and its README. Nothing
  was ever staged there: owner-supplied scans are reserved an ID and written
  directly into `evidence/<category>/`, and retrieval-agent images promote from
  `research/from-retrieval/` through the value gate. Residual references in
  `README.md` and the full-text-references README were updated.

### Added

- Create the missing birth and death events for the Bohrer couple so their
  lifespans and events display: E-0019 (João Gonçalves Bohrer death, Volta
  Redonda 1970) and E-0020 (birth c.1894, Rio de Janeiro), E-0021 (Celina Bohrer
  death, Volta Redonda 1977) and E-0022 (birth c.1900, Nova Friburgo) — dates
  taken from the death ages, places from the records. They had catalogued deaths
  but no event, so the viewer showed "Dates not established".
- Add a person-completeness checklist to `data/README.md` (populate name,
  privacy, nationality, name variants, birth+death events with places, family
  links, occupations and notes on every person create/update) so vital events
  and other fields are not missed again.
- Add a `nationality` field to the person schema and surface it in the viewer:
  each card now shows, below the name, the lifespan, the birthplace and the
  nationality, and the details overview gains a Nationality row. Nationality is
  populated evidence-based — Brazilian by Brazilian birth, Portuguese for Vicente
  José de Carvalho Guimarães (CIV-0007) — and left unset for João Muniz
  Bittencourt (P-0019), whose nationality is genuinely contested. Covered by
  `tests/js/data_loader.test.mjs`.
- Extend the maternal Bohrer line two generations from three primary Rio de
  Janeiro civil records (retrieval sync): catalogue João Gonçalves Bohrer's 1970
  Volta Redonda death (CIV-0014), Celina/Selina Bohrer's 1977 death (CIV-0015)
  and Eunir Bohrer's 1924 Nova Friburgo birth (CIV-0016); add Iris's grandparent
  generation — Valentim Martinho Bohrer + Carolina Bohrer (P-0028/P-0029, F-0013)
  and Joaquim José Bohrer + Lucinda Ferreira da Silva (P-0030/P-0031, F-0014) —
  and link P-0014/P-0015 as their children (strong-evidence). Fix Celina's origin
  to Nova Friburgo (resolving the São Leopoldo RS namesake) and record the
  civil-registered "Celina" variant. Inventory DOC-0024–0026. Two modern sibling
  death records were reviewed but withheld (collateral + living-person data).
- Add an English / Brazilian-Portuguese (pt-BR) dual-language UI to the
  family-tree viewer. A new dependency-free `family-tree-viewer/i18n.js`
  translates the chrome and controlled-vocabulary labels (event types, statuses,
  privacy); a language selector defaults to the browser language (falling back to
  English), persists the choice in `localStorage`, and encodes it in the URL hash.
  Record content (names, transcriptions, places, record types) is never
  translated. Covered by `tests/js/i18n.test.mjs`.
- Surface FAN references and source transcriptions in the family-tree viewer.
  `data-loader.js` now loads the `fan` entities and projects them per person via
  `participants`; the details panel lists each person's FAN / context references
  (role, record category, place, transcription and image link) and shows each
  source's transcription and abstract. Covered by new `tests/js/data_loader.test.mjs`
  assertions.
- Catalogue the Muriaé/Leopoldina Full-Text FAN set as FAN entities FAN-0002–
  FAN-0013 — third-party probate/notarial records where Simplício José Ferreira
  Armond (P-0016) or Aristão Ferreira Armond (P-0008) appear only in a functional
  role (creditor, witness, appraiser/louvado, attorney, party, co-owner) — each
  with a transcription and a person link. Flatten the images into
  `evidence/references/` under `FAN-NNNN-…` names, fix FAN-0001's path, remove the
  `armond-muriae-fulltext-probates/` subfolder, and preserve the Full-Text
  candidate list as `logs/2026-07-29-fulltext-muriae-leopoldina-candidates.csv`.
  Codify the references-folder rule (one catalogued FAN entity per flat,
  `FAN-NNNN`-named image) in `evidence/README.md` and `evidence/references/README.md`.
- Catalogue two Barbacena-context sources from the retrieval resources cache
  via the value gate: PUB-0002 (Antônio Henrique Duarte Lacerda's 2010 UFF
  doctoral thesis on the Ferreira Armonde family; published_genealogy,
  lead_only) and GOV-0002 (the 1831 Curral Novo population list; census,
  context_only — a Projeto Compartilhar transcription of the APM manuscript).
  Both linked to P-0016 with evidence PDFs and inventory entries DOC-0022 and
  DOC-0023. They put the anti-merge (the Barbacena Gen-2 Simplício died
  celibate) on catalogued sources without asserting the unproven bridge to this
  line.
- Complete a full per-image read pass of the `research/from-retrieval/`
  drop and catalogue PRB-0004 (a Toledo Concórdia / Ribeirão de São Bento deed
  naming Eliza's maternal grandparents Mathilde × Ladisláo Egydio Ferreira de
  Toledo and the parent couple Antonio Zeferino de Toledo × Maria Perpétua), with
  evidence image and document-inventory entry DOC-0021. Record the resulting
  hypothesis (Antonio Zeferino × Maria Perpétua as Eliza's parents) and the
  two-Ladisláo conflict without creating unverified edges; flag a Moura-family
  "Mathilde Maria de Jesus" namesake to avoid conflation.
- Gitignore the retrieval-agent working area (`research/from-retrieval/output/`,
  `research/from-retrieval/README.md`, `research/from-retrieval/resources/` and the
  local `from-retrieval-triage-ledger.md`) as regenerable, non-history working data.
- Define the initial YAML entity model and JSON Schemas for people, families,
  events, places and sources.
- Add entity and research templates, evidence-handling guidance and the initial
  document-cataloguing plan.
- Add an ID allocation ledger and automated validation for schemas, references,
  evidence quality, privacy, duplicate identities and parent-child chronology.
- Document the local workflow, implementation roadmap and policies for derived
  timelines and exports.
- Establish permanent research principles and a cumulative research log, and
  record that the source documents are absent from the worktree and Git history.
- Consolidate repository governance, remove obsolete foundation and placeholder
  documentation, and allow empty entity directories to remain untracked.
- Add a versioned document-inventory schema and validation for file integrity,
  privacy review, duplicate handling and source-allocation state.
- Version every structured entity and replace the overloaded evidence class
  with separate record category, source form, information quality and evidence
  type fields.
- Model each parent-child assertion as a separately typed and cited edge, and
  constrain event participant roles with explicit exceptional-role details.
- Split the validator into focused model, inventory, reference and genealogical
  rule modules while preserving its command-line and imported interfaces.
- Replace stored next-ID counters with derived allocation and add atomic,
  recoverable entity reservation and draft generation with dry-run support.
- Add staged validation and recoverable batch promotion for mutually dependent
  entity drafts, including rollback and interrupted-transaction recovery.
- Add a least-privilege, concurrency-cancelled GitHub Actions matrix that runs
  the frozen local repository check with pinned action and tool versions.
- Consolidate the older duplicate remote validation workflow into the canonical
  pinned, multi-version repository-health workflow.
- Consolidate project scope and operating principles into `README.md`, current
  state and planning into `STATUS.md`, and research policy and history under
  `research/`; add checks for root-document ownership and broken local Markdown
  links.
- Remove the duplicate document-cataloguing plan after retaining its unique
  source-processing order in `STATUS.md`; keep research policy, inventory and
  reproducible history as separate canonical artifacts.
- Audit the original ChatGPT genealogy conversation against the repository,
  preserve previously omitted leads and superseded interpretations without
  promoting them, and identify its 24 unavailable image attachments as the
  primary transfer gap; downgrade Aristão's proposed parentage to `hypothesis`
  because collaborative-tree support alone cannot establish `strong-evidence`.
- Recover and catalogue the first authorised record from FamilySearch
  Memories: the certified 1916 marriage of Deocleciano Muniz Bittencourt and
  Luiza Fernandes de Azevedo; add its private reconstructed image, inventory
  provenance, checksum and six directly required linked entities.
- Fix prospective entity promotion so the default command-line workflow uses
  the repository schemas, and cover the previously untested path.
- Recover and catalogue three alternate photographs of the damaged 1952
  marriage certificate of Geraldo Paz Armond and Cidalia Engracio Guimarães as
  one source; add its private evidence files, inventory provenance, retained
  birth-date conflict and six directly required linked entities.
- Consolidate `CIV-0002` to the clearest photograph under one canonical
  filename; keep the two omitted alternate views recoverable in Git history and
  preserve their FamilySearch provenance in the research record.
- Migrate the initial person block to Ahnentafel order, add privacy-minimised
  roster records for direct-ancestor positions 1–15, remap all existing
  references, and document that the identifiers remain immutable after this
  low-cost migration.
- Recover and catalogue Geraldo Paz Armond's original 1991 civil death
  registration; preserve the FamilySearch archival citation, private
  reconstructed register image, record-number conflict and source-qualified
  parentage of Aristão Ferreira Armond and Liliosa Paz Armond.
- Review the data model against three real records: distinguish reported
  co-parents from sourced partners, enforce inventory-to-source file checksum
  consistency, and add a validated missing-record coverage ledger for deceased
  direct ancestors.
- Recover and catalogue the 1949 marriage certificate of Antenor Muniz and
  Iris Bohrer; add its private reconstructed image, source-qualified marriage,
  married-name form and reported parent-child relationships.
- Audit Liliosa Paz Armond's FamilySearch Sources and Memories; document that
  the attached source is only her mention in Geraldo's 1991 death record, reject
  a 1975 newspaper PDF as her death evidence, and restore the conflicting 1946
  death dates to unresolved lead status.
- Recover and catalogue Aristão Ferreira Armond's original 1957 civil death
  registration; confirm his death, preserve the malformed FamilySearch index,
  and add source-qualified strong-evidence parentage for Simplicio Armand and
  Eliza Ferreira Armand without promoting unproved fuller name forms.
- Record the unsuccessful indexed and full-text search for Aristão's birth and
  marriage, identify São Sebastião de Leopoldina baptism image group
  `004640627` Item 3 as the bounded 1879 manual-review target, and exclude the
  marriage series ending in July 1897 as probably too early for the target
  marriage.
- Redesign `AGENTS.md` as a stable context-loading, decision and completion
  protocol that routes agents to canonical live state and task-specific
  contracts without duplicating volatile research context.
- Consolidate `STATUS.md` into a present-only operational snapshot, move
  historical ownership back to the existing canonical logs and structured
  records, clarify the policy boundary with `AGENTS.md`, and add a regression
  test against renewed status-file accumulation.
- Add a required, short and ordered `Next steps` section to `STATUS.md`,
  separating the visible tactical handoff from the detailed coverage ledger
  and longer-term strategic priorities.
- Add a concise root README entry point linking directly to the current
  objective, next-step queue, agent instructions and research-history index.
- Map Aristão Ferreira Armond's restricted baptism and marriage register
  targets, document the exhausted searchable layers, mark both coverage rows
  inaccessible, and advance the current objective to the direct-line
  FamilySearch Memories audit.
- Require highest-authorised-resolution evidence retention, record acquisition
  and resolution status with encoded pixel dimensions, and validate PNG/JPEG
  dimensions while rejecting catalogued lower-resolution working copies.
- Audit all known direct-line FamilySearch Memories in Ahnentafel order,
  identify shared and non-record artifacts, document a living-person visibility
  risk, and catalogue the three-page 2019 full-content Deocleciano–Luiza
  marriage certificate as `CIV-0006`.
- Replace five viewer-tile reconstructions with authorised original-file or
  original-image JPEG downloads, increasing retained resolution by up to
  sixteen times in pixel area while keeping superseded files recoverable in Git
  history.
- Record the unsuccessful exact, variant and bounded-register search for
  Liliosa Paz Armond's own 1946 death or burial, preserve both date leads, and
  document the January–October gap in the accessible Volta Redonda series.
- Catalogue the full-resolution March 1973 Guanabara driver-dossier index as
  `GOV-0001`, preserve its printed "Aristac" name variant, and add José Olavo
  Armond as a source-qualified strong-evidence child of Aristão and Liliosa.
- Recover and catalogue the original 1882 marriage provision for João Monis
  Bittencourt and Susanna Rita Brondão as `PAR-0001`; distinguish the issued
  authorisation from a completed ceremony, preserve the FamilySearch `1633`
  index defect, and identify the Espírito Santo parish as the next register
  target.
- Complete the corresponding ceremony-book access review: document the absence
  of a separately exposed Espírito Santo parish film series, verify from the
  Archdiocese's historical record that its chapel was the parish seat in 1882,
  and specify the exact Cúria Metropolitana request without treating the
  provision date as a completed marriage.
- Recover and catalogue the 1915 Carvalho Guimarães collective birth
  registration as `CIV-0007`; retain its authorised original-upload file,
  structure six direct ancestors, three parent groups and the reported events
  and places, preserve the Maria Amora/Aurora conflict, and keep Vicente's
  Portuguese origin at nationality level until a parish is documented.
- Preserve and catalogue six unique original PDFs from the living repository
  subject's private FamilySearch Memories as `CIV-0008` through `PUB-0001`;
  deduplicate two byte-identical birth uploads without losing provenance,
  separate four distinct manifestations of one marriage, and retain the
  Chagas dissertation as a secondary Armond research lead rather than proof of
  lineage or Azorean origin.
- Redesign the static family-tree viewer with a heritage-archival theme
  (parchment, forest green and gold, serif display, framed register cards and
  rounded-elbow lineage connectors), replace the placeholder monogram with a
  family-tree seal emblem and matching favicon, and vendor `js-yaml` locally so
  the viewer makes no external network requests and works fully offline.
- Extend the viewer to present couples with per-family marriage markers, link
  each non-private evidence file and external record from the detail panel
  while surfacing source form, quality and reliability limitations, add
  auto-fit zoom with manual controls and drag-to-pan, widen the tree canvas,
  and encode a bookmarkable view in the URL hash; keep living-person data
  minimised throughout.
- Cover the viewer's read-only data projection with Node unit tests run through
  `make check`, guard `entity-index.json` against drift from the canonical data
  directories, restore focus to the invoking card when the detail panel closes,
  and copy the vendored parser and favicon into the privacy-filtered GitHub
  Pages build.
- Audit the direct-line vital records against their document images and correct
  the source transcriptions: fix Geraldo Paz Armond's death entry number from a
  misread 39005 to 39006 (39005 is the unrelated infant on the facing page) and
  add its cause of death, registration date and son-declarant; add the cause of
  death, time and declarant to Aristão Ferreira Armond's death entry; and record
  the civil-register citation (livro A-350, folha 98) printed on Juan Carlos
  Muniz Armond's birth certificate.
- Recover Antenor Muniz's (2 November 1923, Alvorada) and Iris Bohrer's
  (27 February 1929, Presidente Soares) birth facts stated as secondary
  information in their 1949 marriage certificate, which the source had wrongly
  called illegible; structure them as events E-0017 and E-0018 with the new
  place PL-0009 and note them against both coverage rows.
- Record a resolvable FamilySearch profile URL for every collaborative-tree
  lead in the record-coverage ledger, extending the coverage schema with an
  optional lead-only `url` field.
- Allow a certified copy of an official record (derivative source form with
  direct primary information) to support a `confirmed` conclusion, alongside
  original records; family recollection and collaborative trees still cannot
  confirm. Update the confidence-status policy and validator accordingly, and
  promote Juan Carlos Muniz Armond's parentage to `confirmed` on his certified
  birth certificate corroborated by his Ontario marriage record.
- Correct the 1882 marriage provision (PAR-0001): re-reading the register shows
  the couple's provision was directed to the Santo Antônio de Sapucaia parish,
  not the Espírito Santo parish (that wording belongs to the adjacent José
  Pereira Mendes entry). Repoint place PL-0005, event E-0006 and the coverage
  search target to Sapucaia, preserving the superseded interpretation, and
  refresh the STATUS snapshot counts.
- Promote to `confirmed` the events directly attested by a certified or
  original official record now that certified copies may confirm: the 1916,
  1952 and 1949 marriages (E-0001, E-0002, E-0004), the 1882 provision issuance
  (E-0006) and Maria Amora Guimarães's 1904 birth (E-0007). Parentage reported
  in another record, and births reported in a marriage record, remain
  strong-evidence.
- Add `research/familysearch-image-targets.md`, an autonomous-agent task-spec
  for retrieving restricted record images, and an `evidence/incoming/` staging
  area for un-catalogued downloads. Record the online gap-and-resource research
  session, fold the discovered resources into the coverage ledger, and update
  place PL-0009's present-day equivalence to Alto Jequitibá, MG (from IBGE
  administrative history) without changing the source-recorded birthplace.
- Unify the agent-governance documentation on `AGENTS.md` as the single source
  of truth for both Claude Code and Codex, and document the assistant/Codex
  research split. Refresh `README.md` (family-tree viewer, `CLAUDE.md` loader
  and updated layout) and give `STATUS.md` a currency pass: reprioritise the
  current objective to the now-unblocked Aristão baptism and Aristão×Liliosa
  marriage retrieval, trim the per-source list in favour of the canonical
  `data/sources/`, and record the viewer and certified-copy confirmation rule
  in the engineering state.
- Run four parallel read-only research passes (Liliosa vital records, the
  Ferreira Armond bridge, Vicente's Portuguese origin and the Sapucaia marriage)
  and fold the leads into the coverage ledger, the Codex image-retrieval
  worksheet and a dated session log without changing any conclusion: reframe
  Liliosa's 1946 death to the Barra Mansa index, place the Aristão×Liliosa
  marriage in Piacatuba/Leopoldina, identify the Simplício×Elisa marriage as the
  decisive (still unproven) Ferreira Armond bridge with the b.1784 Simplício
  doubly documented as unmarried, fix Vicente's parish as Santa Luzia do
  Carangola (mother parish Tombos), and separate the Sapucaia provision from the
  completed ceremony assento by custody. Record the Portugal/Azores
  custody-and-access workflow (100-year rule, free DigitArq/GEA images) in
  `research/README.md`.
- Add an optional, source-qualified `occupations` field to the person schema
  (each occupation cites the source that records it), enabling profession and
  wealth analysis. The recursive reference and living-person privacy checks
  cover its `source_ids` automatically; no validator change was needed.
- Preserve key research-reference documents in `research/resources/` with a
  provenance manifest: the ASBRAP "Armond, Por Quê?" article, the 1831 Curral
  Novo census transcription, the Lacerda 2010 (UFF) thesis, the Chagas 2018
  (UFMG) dissertation and a snapshot of the Senra blog — all leads about the
  historical Barbacena Ferreira Armonde family, not this line's proven ancestry.
  Record the deep-dig session (five parallel agents plus the 1831 census).
- Preserve two further Projeto Compartilhar documents in `research/resources/`
  (the 1831 João Gomes census — a married Manoel Antonio de Armond household —
  and the 1751 will/inventory of the patriarch), and add
  `logs/correspondence-log.md` recording outreach to Mauro Senra, Nilza
  Cantoni and the Piacatuba parish about the Simplício × Elisa marriage.
- Survey the owner-supplied source sites (a full Projeto Compartilhar crawl, the
  My Portuguese Gen Azores directory, and the Scribd Forjaz & Mendes "Genealogias
  da Ilha Terceira") and consolidate the leads: record the survey session log;
  add a per-locality FamilySearch catalog-ID map and an Iris Bohrer 1929-birth
  target to the retrieval worksheet; note the married Manoel Antonio de Armond
  (João Gomes 1831) as a candidate later-namesake and reaffirm, from the 1831
  census (a primary source), that the documented Armonde tree does not reach
  Piacatuba. No conclusion changed.
- Populate the new `occupations` field from held-source transcriptions for six
  deceased direct-line people: Aristão Ferreira Armond (padeiro, CIV-0005),
  Antenor Muniz (da lavoura, CIV-0004), Cidalia Engracio Guimarães (doméstica,
  CIV-0002), Geraldo Paz Armond (aposentado, stated at death, CIV-0003), and
  Francisco José de Carvalho Guimarães and Emmerenciana Maria de Jesus
  (lavradores, CIV-0007). Each occupation cites the record that states it.
- Show each person's occupations in the family-tree viewer's detail panel (a new
  source-cited "Occupation" section, minimised for living people), aggregate an
  occupation's cited sources into the person's source list, and cover the
  projection with a data-loader unit test.
- Record the owner-supplied Armond documents (Aristão's 1957 death = CIV-0005;
  Marfiza Ferreira Armond's 1962 death; José Olavo's 1975 marriage bann in O
  Processo): Marfiza is confirmed as Aristão's sister by a second primary record
  of the parents Simplício Ferreira Armond + Elisa Toledo (giving Elisa's maiden
  surname Toledo), and José Olavo's "natural de Eugenópolis" fixes the family's
  locus as Eugenópolis, MG — redirecting the Aristão×Liliosa marriage and the
  children's-birth search there, not Leopoldina. No conclusion promoted; the
  Azorean bridge stays unproven; formal source cataloguing pending the files.
- Stage the owner-supplied source files in `evidence/incoming/` (the O Processo
  newspaper, the Aristão 1957 death re-capture, and the Marfiza 1962 death image)
  for cataloguing, and record Nilza Cantoni's email reply in the correspondence
  log: the Simplício × Elisa couple likely lived in Dores do Monte Alegre (now
  Taruaçu), served by the Argirita/Piacatuba parishes; Piacatuba marriage book 1
  (1851-55, 1862-65) is a documented negative; and Elisa's Toledo family is rooted
  in Argirita (father an eleitor 1863-64; land registry 1856) — redirecting the
  Simplício × Elisa marriage and Elisa-origin search to Argirita/Taruaçu.
- Record 16 FamilySearch Full-Text hits for Aristão and Simplício Ferreira
  Armond in the Muriaé/Leopoldina probate records (staged in
  `evidence/references/armond-muriae-fulltext-probates/` with a candidates CSV):
  an 1881 Leopoldina probate documents "Simplício José Ferreira Armond casado com
  D. Eliza Balbina de Toledo" and lists Elisa's Toledo siblings and parent's
  estate; Simplício ("Capitão") and Aristão recur across the comarca's probate/
  property records. Folded into P-0016, P-0017 and P-0008. No conclusion
  promoted; formal per-source cataloguing to follow; the Azorean bridge stays
  unproven.
- Catalogue the two subject probate records from the Full-Text batch as sources:
  `PRB-0001` (1881 Leopoldina heir list naming Eliza Balbina de Toledo as wife of
  Simplício José Ferreira Armond, with her Toledo siblings) and `PRB-0002` (1884
  Leopoldina petition of Simplício as heir of the late D. Mathilde Maria de
  Jezus). Both are court_or_probate originals, linked to P-0016 and P-0017, with
  their images moved to a new `evidence/probate/` category and inventoried as
  DOC-0016/DOC-0017. The 1881 estate opens Elisa's maternal ancestry (decedent
  Mathilde Maria de Jezus); the remaining 13 Full-Text hits stay staged as FAN
  references. Simplício's own parentage is still not found.
- Catalogue the 1975 marriage bann of José Olavo Armond in the newspaper
  *O Processo* (Conselheiro Lafaiete, MG; Ano II, n.º 42, 1–15 February 1975) as
  `NWS-0001` (record_category `newspaper`), inventoried as DOC-0018 with the
  issue PDF filed under a new `evidence/newspapers/` category. It independently
  confirms José Olavo's parents (Aristão Ferreira Armond and Liliosa Paz Armond)
  and records his birthplace as Eugenópolis; P-0018 gains a name variant and the
  occupation "representante comercial".
- Catalogue the 1962 civil death registration of Marfiza Ferreira Armond as
  `CIV-0013` (owner-supplied register image, entry n.º 18892, watermarked "SEM
  VALOR LEGAL"; DOC-0019). It names her parents as Simplício Ferreira Armond and
  Eliza Ferreira Toledo — a second primary record giving Eliza the Toledo
  surname and documenting Marfiza (b. ~1873, aged 89) as a sister of Aristão.
- Add a FAN (Friends / Associates / Neighbours) reference entity type
  (`data/fan/`, `FAN-NNNN`, `schemas/fan.schema.json`) for third-party records
  where a family member appears only in a functional role, plus the first entity
  `FAN-0001` (an 1875 Muriaé procuração signed by Simplício José Ferreira
  Armond). People gain an optional `fan_references` back-link list.
- Catalogue the 1877 Leopoldina Toledo deed of sale (`PRB-0003`, two pages,
  promoted from the `research/from-retrieval/` sync via the value gate) and add
  `P-0027` Mathilde Maria de Jesus. Its clause "sua finada avó Dona Mathildes
  Maria de Jesus" (Fazenda da Concórdia) fixes Mathilde as the *grandmother* of
  Eliza Balbina de Toledo's (P-0017) Toledo grandchild set, resolving the
  mother-vs-grandmother question flagged on PRB-0001; the intervening parent
  (Eliza's) remains undocumented.

### Changed

- Restructure sources into category-prefixed entity kinds. Sources move to
  `data/sources/<category>/` with immutable category-prefixed IDs (`CIV`, `GOV`,
  `PAR`, `PRB`, `NWS`, `PUB`, `REC`) replacing the flat `SRC-NNNN` space, and
  their evidence files carry the same prefix. The validator resolves `source_ids`
  against the union of the seven source kinds, the viewer maps each prefix back
  to its folder, and `common.schema.json`, the ID ledger, per-category templates
  and the AGENTS/data/schemas/evidence docs are updated to match. IDs are
  immutable once assigned; adding a category follows a documented pattern
  (`data/README.md`). This supersedes the former "never renumber" rule only for
  this one-time re-scheme.
- Standardise evidence filenames and folders: rename the two probate images to
  the `SRC-<id>-<record-type>-<subject>-<year>-original` convention; relocate the
  13 FAN probate images from `evidence/incoming/` (staging) to a permanent
  `evidence/references/armond-muriae-fulltext-probates/`; and document in
  `evidence/README.md` that evidence categories reflect the record's origin (not
  the event) and that `references/` holds retained FAN/context images.
- Clear `evidence/incoming/`: an owner-supplied alternate scan of Aristão's 1957
  death entry (watermarked "SEM VALOR LEGAL") is a redundant recapture of the
  already-catalogued CIV-0005, so it is kept as a working reference under
  `evidence/references/` (not re-inventoried, since one authoritative image is
  kept per record) and noted in CIV-0005.
- Tighten `AGENTS.md` so the source-record (`data/sources/`) versus binary-scan
  (`evidence/`) two-layer split, the category-prefix scheme, and the
  FAN-versus-source decision are stated explicitly as non-negotiable format
  rules (imported into Claude via `CLAUDE.md`).
- Move all research history to a top-level `logs/` directory (a sibling of
  `research/`): the dated session logs, the `LOG.md` index and the
  `correspondence-log.md` now live there together, and every reference and
  internal markdown link is repointed.
- Move the validated control ledgers `document-inventory.yaml` and
  `record-coverage.yaml` from `research/` to `data/` (joining `id-ledger.yaml`),
  since they are settled, schema-validated structured data rather than research
  notes. Repoint the validator paths, test fixtures and docs. `research/` now
  holds policy, worksheets, entity drafts and reference resources.

### Fixed

- Show a person's own life events only in the viewer. The timeline projection
  attached each event to every participant, so a death that merely named a
  person as a parent (e.g. Geraldo Paz Armond's 1991 death naming Aristão
  Ferreira Armond) surfaced as that person's own death. Events now land on a
  person's timeline only when their role is the subject — principal, or
  spouse/partner in a marriage; a referenced role (parent, witness) still
  contributes the event's sources but no longer a spurious event. Regression
  test added.
