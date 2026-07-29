# Changelog

All notable repository changes are recorded here. Genealogical conclusions must
also remain traceable through source records and research logs.

## Unreleased

### Added

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
  `research/correspondence-log.md` recording outreach to Mauro Senra, Nilza
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

### Fixed

- Show a person's own life events only in the viewer. The timeline projection
  attached each event to every participant, so a death that merely named a
  person as a parent (e.g. Geraldo Paz Armond's 1991 death naming Aristão
  Ferreira Armond) surfaced as that person's own death. Events now land on a
  person's timeline only when their role is the subject — principal, or
  spouse/partner in a marriage; a referenced role (parent, witness) still
  contributes the event's sources but no longer a spurious event. Regression
  test added.
