# Cumulative research log

This is the append-only index of completed research and repository-audit
sessions. Detailed reproducible notes live under `research/logs/` using
`YYYY-MM-DD-short-question.md`. Later corrections must identify the earlier
entry they amend; they must not erase it.

## 2026-07-28 — Repository evidence availability audit

- Outcome: no source document, source entity or historical binary/LFS object was
  found; Priority 0 requires authorised copies before cataloguing can begin.
- Detailed log:
  [`logs/2026-07-28-repository-evidence-availability-audit.md`](logs/2026-07-28-repository-evidence-availability-audit.md).

## 2026-07-28 — Governance and architecture consolidation

- Outcome: established canonical sprint governance, removed obsolete foundation
  instructions and placeholder documentation, and changed validation so empty
  entity directories are created only with their first substantive record.
- Genealogical conclusions changed: none.
- Next action: validate the document inventory contract.

## 2026-07-28 — Document inventory contract

- Outcome: added a strict versioned contract and automated checks for inventory
  IDs, file paths and checksums, privacy review, duplicates and proposed source
  allocation.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: version every entity schema and correct the evidence taxonomy
  before the first source record is created.

## 2026-07-28 — Entity versioning and evidence taxonomy

- Outcome: required schema version 1 on every entity and separated record
  category, source form, information quality and evidence type in source
  records.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: add controlled parent-child relationship types and event
  participant roles before ingesting people.

## 2026-07-28 — Relationship and participant semantics

- Outcome: modelled each parent-child relationship as a separately typed,
  sourced and confidence-rated edge; added controlled participant roles with an
  explicit exceptional-role detail field.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: reduce validator maintenance risk by separating its loading,
  schema and cross-entity concerns without changing the public command.

## 2026-07-28 — Validator modularisation

- Outcome: reduced the stable validator façade from more than 1,100 lines to
  fewer than 500 and isolated inventory, reference, shared-model and
  genealogical policy concerns without duplicating functions.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: add an atomic ID allocation and entity-skeleton command so
  record creation cannot desynchronise filenames and the ledger.

## 2026-07-28 — Identifier reservation and draft automation

- Outcome: removed redundant next-ID counters, added explicit reservations and
  a dry-run-capable command that atomically reserves the next ID before
  creating a recoverable non-live draft.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: add validated batch promotion so mutually dependent completed
  drafts can enter the live data model without a transient invalid state.

## 2026-07-28 — Validated batch promotion

- Outcome: added prospective whole-repository validation, dry-run, rollback and
  interrupted-transaction recovery for promoting mutually dependent drafts.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: enforce the complete repository check on GitHub pushes and pull
  requests so invalid changes cannot silently bypass the local workflow.

## 2026-07-28 — Continuous repository health enforcement

- Outcome: added a read-only GitHub Actions workflow for Python 3.11 and 3.13,
  pinned all executable actions and uv, cancelled superseded runs, and tested
  the workflow contract locally. Merge blocking still requires an external
  GitHub branch-rule setting.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: obtain authorised, privacy-reviewed copies of the previously
  supplied documents and catalogue the first three original records.

## 2026-07-28 — Remote workflow reconciliation

- Outcome: rebased the sprint commits onto the independently added remote
  validation workflow, preserved that commit in history and removed the
  obsolete duplicate from the worktree in favour of the pinned canonical
  workflow.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: unchanged; obtain authorised, privacy-reviewed document copies
  for the first three source records.

## 2026-07-28 — Documentation ownership consolidation

- Outcome: reduced root Markdown to four canonical documents by merging stable
  project guidance into `README.md`, active state and priorities into
  `STATUS.md`, and research policy and cumulative history under `research/`.
  Added automated checks against broken local links and renewed root-document
  fragmentation.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: unchanged; obtain authorised, privacy-reviewed document copies
  for the first three source records.

## 2026-07-28 — Research workspace consolidation

- Outcome: reviewed every file under `research/`, retained the distinct policy,
  intake-inventory, cumulative-history and detailed-session responsibilities,
  and removed the task-specific cataloguing plan after moving its unique record
  order into `STATUS.md`.
- Research evidence added: none.
- Genealogical conclusions changed: none.
- Next action: unchanged; obtain authorised, privacy-reviewed document copies
  for the first three source records.

## 2026-07-28 — Original conversation transfer audit

- Outcome: compared the complete original ChatGPT research conversation with
  the repository, preserved transcript-only leads and the correction chain at
  hypothesis level, and identified 24 unavailable attachments as the principal
  provenance gap.
- Detailed log:
  [`logs/2026-07-28-chatgpt-conversation-transfer-audit.md`](logs/2026-07-28-chatgpt-conversation-transfer-audit.md).
- Research evidence added: none.
- Genealogical conclusions changed: Aristão's proposed parentage remains
  recorded but is downgraded from `strong-evidence` to `hypothesis` because the
  available support is limited to collaborative-tree and transcript leads.
- Next action: recover and privacy-review the original attachments before
  creating source or person entities.

## 2026-07-28 — First FamilySearch document ingestion

- Outcome: recovered the certified 21 October 1916 marriage record of
  Deocleciano Muniz Bittencourt and Luiza Fernandes de Azevedo from
  FamilySearch Memories, reconstructed the complete viewer image, completed
  privacy and provenance review, and promoted the first six linked entities.
- Detailed log:
  [`logs/2026-07-28-familysearch-marriage-record-ingestion.md`](logs/2026-07-28-familysearch-marriage-record-ingestion.md).
- Genealogical conclusions changed: the marriage, spouses' ages and
  birthplaces, and their four named parents now have catalogued direct evidence;
  the marriage remains `strong-evidence` because the retained image is a
  derivative.
- Negative result: neither spouse has the 1916 record attached as a formal
  FamilySearch source; each has only a 1983 record concerning a child.
- Next action: recover and catalogue two additional original records before
  reviewing the schema against the evidence sample.

## 2026-07-28 — Armond–Guimarães marriage-record ingestion

- Outcome: recovered and privacy-reviewed three alternate photographs of the
  damaged 31 May 1952 marriage certificate of Geraldo Paz Armond and Cidalia
  Engracio Guimarães, and treated them as one source rather than three pages.
- Detailed log:
  [`logs/2026-07-28-familysearch-armond-guimaraes-marriage-ingestion.md`](logs/2026-07-28-familysearch-armond-guimaraes-marriage-ingestion.md).
- Genealogical conclusions changed: the marriage and Cidalia's married-name
  form now have catalogued direct evidence. The certificate's report of 15
  September 1930 is retained as secondary birth information and does not
  resolve the existing date conflict.
- Preservation limitation: physical damage and opaque tape obscure material
  text; all uncertainty remains marked rather than supplied from the
  collaborative tree.
- Next action: inspect Geraldo's attached source and death-certificate Memory,
  then recover one distinct record to complete the three-record schema sample.

## 2026-07-28 — SRC-0002 evidence-file consolidation

- Outcome: retained the clearest of the three reviewed photographs of the
  Armond–Guimarães marriage certificate under one canonical filename and
  removed the two less-readable alternates from the current worktree.
- Preservation: the omitted files remain recoverable from Git commit
  `3dc9c5e`; source provenance still records all three FamilySearch Memories.
- Genealogical conclusions changed: none.

## 2026-07-28 — Ahnentafel person-ID migration

- Outcome: aligned the initial direct-ancestor person block with Ahnentafel
  order, created privacy-minimised roster entries for positions 1–15, and
  migrated every existing person cross-reference.
- Detailed log:
  [`logs/2026-07-28-ahnentafel-person-id-migration.md`](logs/2026-07-28-ahnentafel-person-id-migration.md).
- Evidence boundary: `SRC-0003` is owner-supplied family information and
  supports the working roster and spellings only; it does not replace vital or
  relationship records.
- Engineering decision: person IDs remain immutable after this one low-cost
  migration, even if later evidence changes a pedigree relationship.

## 2026-07-28 — Geraldo Paz Armond death-record ingestion

- Outcome: located the original 18 February 1991 Volta Redonda civil death
  entry through Geraldo's attached FamilySearch source, reconciled it with the
  identical Memory image, and preserved a privacy-reviewed reconstruction with
  archival citation and checksum.
- Detailed log:
  [`logs/2026-07-28-familysearch-geraldo-death-record-ingestion.md`](logs/2026-07-28-familysearch-geraldo-death-record-ingestion.md).
- Genealogical conclusions changed: Geraldo's death is now supported by
  catalogued direct evidence; the record supplies strong evidence that Aristão
  Ferreira Armond and Liliosa Paz Armond were his parents.
- Conflict retained: the handwritten entry number appears to be `39005`, while
  the FamilySearch index reports certificate `39006`.
- Negative result: the original-image viewer's controlled JPG download did not
  yield a file, so the identical Memory page was reconstructed from its full
  Deep Zoom tile set.
- Next action: review the model against the completed three-document sample
  before wider ingestion.

## 2026-07-28 — Three-record structured-model review

- Outcome: corrected the family model so reported co-parents do not imply an
  unsupported partnership; enforced inventory-to-source file integrity; and
  added a validated missing-record coverage ledger for all deceased direct
  ancestors currently numbered `P-0004` through `P-0015`.
- Detailed log:
  [`logs/2026-07-28-three-record-model-review.md`](logs/2026-07-28-three-record-model-review.md).
- Genealogical conclusions changed: the unsupported partner relationship
  between Aristão Ferreira Armond and Liliosa Paz Armond was removed. Their
  separately sourced parent-child relationships to Geraldo remain
  `strong-evidence`.
- Architecture decision: defer assertion-level citation objects until five to
  ten more varied records show whether the added complexity is justified.
- Next action: resume evidence ingestion with the 1949 Antenor–Iris marriage.

## 2026-07-28 — Antenor–Iris marriage-record ingestion

- Outcome: recovered and catalogued the damaged 7 December 1949 civil marriage
  certificate of Antenor Muniz and Iris Bohrer from Antenor's user-created
  FamilySearch source.
- Detailed log:
  [`logs/2026-07-28-familysearch-antenor-iris-marriage-ingestion.md`](logs/2026-07-28-familysearch-antenor-iris-marriage-ingestion.md).
- Genealogical conclusions changed: the marriage, Iris's married-name form and
  both spouses' reported parents now have catalogued direct evidence; each
  relationship is `strong-evidence` because the retained document is a
  derivative.
- Negative result: Iris's FamilySearch profile had no attached sources.
- Preservation limitation: folds, tape, stains and low contrast obscure
  register details and several vital fields, which remain untranscribed.
- Next action: inspect Liliosa Paz Armond's 1946 death evidence.

## 2026-07-28 — Liliosa Paz Armond evidence audit

- Outcome: exhausted Liliosa's currently attached FamilySearch Source and
  Memory without locating her own 1946 death registration.
- Detailed log:
  [`logs/2026-07-28-familysearch-liliosa-evidence-audit.md`](logs/2026-07-28-familysearch-liliosa-evidence-audit.md).
- Negative result: source `SJBH-LL3` resolves to Liliosa's person-level mention
  as Geraldo's mother in his 1991 death registration, already catalogued as
  `SRC-0004`; it is not evidence of Liliosa's death.
- Negative result: Memory `120876994` is a scanned eight-page 1975 issue of
  *O Processo*, not a civil or parish record. No identifiable Liliosa, Aristão
  or Armond reference was found in extracted text or rendered-page review.
- Conflict restored: 16 April 1946 on the collaborative FamilySearch profile
  and 15 November 1946 in the imported conversation remain unsourced leads.
- Genealogical conclusions changed: Liliosa's exact death date is no longer
  stated as established. Her parentage and original surname remain unresolved.
- Next action: inspect Aristão Ferreira Armond's Sources and Memories for his
  1957 death registration and direct evidence of parentage.

## 2026-07-28 — Aristão Ferreira Armond death-record ingestion

- Outcome: located, reconstructed, privacy-reviewed and catalogued Aristão
  Ferreira Armond's original 1 November 1957 Volta Redonda death registration
  as `SRC-0006`.
- Detailed log:
  [`logs/2026-07-28-familysearch-aristao-death-record-ingestion.md`](logs/2026-07-28-familysearch-aristao-death-record-ingestion.md).
- Genealogical conclusions changed: Aristão's death is confirmed; the record
  provides `strong-evidence` that Simplicio Armand and Eliza Ferreira Armand
  were his parents.
- Index defect retained: FamilySearch transcribes Aristão as `Axstai Ferreira
  Armand Armand` and duplicates part of his mother's surname.
- Negative result: one attached source only repeats Aristão's mention as
  Geraldo's father in `SRC-0004`, and his sole Memory is the same 1975
  newspaper issue already rejected as Liliosa's vital-record evidence.
- Next action: locate Aristão's birth or baptism record, or his marriage to
  Liliosa, to verify fuller parent names and identify Liliosa's original
  surname and parents.

## 2026-07-28 — Aristão Ferreira Armond birth and marriage search

- Outcome: indexed, spouse-linked, parent-linked and full-text searches did not
  locate Aristão's birth, baptism or marriage record.
- Detailed log:
  [`logs/2026-07-28-aristao-birth-marriage-search.md`](logs/2026-07-28-aristao-birth-marriage-search.md).
- Negative-result limitation: zero indexed or OCR results do not establish that
  an entry is absent from the original parish books.
- Register target: São Sebastião de Leopoldina image group `004640627`, Item 3,
  images 234–497, includes baptism coverage for 1878–1888 and should be
  reviewed manually for the reported 1879 birth.
- Marriage limitation: image group `004640631` ends its identified parish
  marriage coverage in July 1897, probably before the target marriage. A later
  volume should be located before manual marriage review.
- Genealogical conclusions changed: none.
- Next action: identify the internal indexes and 1879 sequence in baptism image
  group `004640627`, then inspect the original entries manually.

## 2026-07-28 — Agent context protocol review

- Outcome: clarified that `AGENTS.md` is the stable instruction and context
  router rather than a duplicate project-memory file.
- Repository improvement: added layered, task-specific context loading;
  explicit research, intake, data, engineering and review decision paths; safe
  browser boundaries; and a verifiable completion protocol.
- Genealogical conclusions changed: none.
- Next action: continue the current Aristão baptism-register objective using
  the context sources selected by the revised protocol.

## 2026-07-28 — Current-status consolidation

- Outcome: reduced `STATUS.md` from 496 lines to a present-only operational
  snapshot while preserving research and engineering history in their
  canonical logs, structured records and Git.
- Repository improvement: removed duplicated intake history, person
  narratives, record-level task lists and generic completion policy; retained
  the current objective, blockers, evidence summary, material conflicts,
  strategic priorities and active engineering state.
- Automation added: documentation tests now reject obsolete historical or
  person-database sections and cap `STATUS.md` at 200 lines.
- Genealogical conclusions changed: none.
- Next action: continue the current Aristão baptism-register review.

## 2026-07-28 — Immediate next-step queue

- Outcome: added a short ordered `Next steps` section near the top of
  `STATUS.md` so the operational handoff is visible without reading the
  record-coverage YAML.
- Repository improvement: separated the current objective, immediate tactical
  queue, detailed person-by-record ledger and strategic branch priorities.
- Automation updated: the documentation contract now requires the next-step
  section.
- Genealogical conclusions changed: none.
- Next action: inspect Item 3 of baptism image group `004640627`.

## 2026-07-28 — Root README navigation review

- Outcome: verified the root README against the consolidated documentation
  architecture and added direct entry links to the current objective and
  immediate next-step queue.
- Repository improvement: a human or new agent can now identify the live work
  without reading historical logs or opening the record-level YAML ledger.
- Genealogical conclusions changed: none.
- Next action: inspect Item 3 of baptism image group `004640627`.

## 2026-07-28 — Aristão parish-register access review

- Outcome: mapped the relevant baptism and later marriage volumes for Aristão
  Ferreira Armond, including a previously unidentified Piacatuba baptism
  target and the 1898–1920 Leopoldina marriage item.
- Detailed log:
  [`logs/2026-07-28-aristao-parish-register-access-review.md`](logs/2026-07-28-aristao-parish-register-access-review.md).
- Access restriction: the relevant original images in groups `004640627` and
  `004640632` display `Image Restricted` in the owner's authenticated session.
- Negative-result limitation: structured-index and full-text searches returned
  no qualifying target, but do not establish absence from the restricted
  registers.
- Genealogical conclusions changed: none.
- Next action: obtain authorised register access; meanwhile audit all
  direct-line FamilySearch Memories in Ahnentafel order.

## 2026-07-28 — Full-resolution evidence preservation contract

- Outcome: made highest-authorised-resolution retention an explicit evidence
  requirement and recorded the acquisition method, preservation status and
  encoded pixel dimensions for every retained image.
- Automation added: validation now compares inventory dimensions with the
  encoded PNG or JPEG and rejects lower-resolution working copies as reviewed
  or catalogued primary evidence.
- Existing evidence changed: none; the five current reconstructions were
  measured and recorded as complete highest-level viewer exports.
- Genealogical conclusions changed: none.
- Next action: replace technical reconstructions with authorised original-file
  downloads when FamilySearch supplies them, retaining provenance and Git
  recovery history.

## 2026-07-28 — Direct-line FamilySearch Memories audit

- Outcome: audited every known FamilySearch Memories page from `P-0001`
  through `P-0015`, deduplicated shared artifacts and distinguished records
  from photographs, newspapers, academic material and a genealogical display.
- Detailed log:
  [`logs/2026-07-28-familysearch-direct-line-memories-audit.md`](logs/2026-07-28-familysearch-direct-line-memories-audit.md).
- Source added: catalogued the three-page 2019 full-content certificate of the
  1916 Deocleciano–Luiza marriage as `SRC-0007`.
- Preservation improvement: replaced five technical reconstructions with
  authorised original-file or original-image JPEG downloads; the prior files
  remain recoverable from Git history.
- Privacy blocker: six civil PDFs concerning living people are attached to
  `P-0001` as Public Memories. They were not downloaded; changing visibility
  requires explicit owner authorisation.
- Genealogical conclusions changed: none; `SRC-0007` independently supports
  the already catalogued 1916 marriage at `strong-evidence`.
- Next action: locate Liliosa's own 1946 death or burial record.

## 2026-07-28 — Liliosa Paz Armond death-record search

- Outcome: exact, variant, fuzzy, spouse-linked and bounded place searches
  produced no qualifying civil death or parish burial record for Liliosa.
- Detailed log:
  [`logs/2026-07-28-liliosa-death-record-search.md`](logs/2026-07-28-liliosa-death-record-search.md).
- Bounded negative result: Volta Redonda death group `004366685` begins in
  November 1946. Original images 8–11 cover the immediate 15 November
  registration window and contain no Liliosa entry.
- Coverage gap: the identified Volta Redonda series cannot test the alternative
  16 April 1946 lead because it begins in November.
- Source added: catalogued a full-resolution March 1973 government
  driver-dossier index as `SRC-0008`. It names José Olavo Armond, prints his
  father as "Aristac Ferreira Armond", and names his mother exactly as Liliosa
  Paz Armond.
- Genealogical conclusion changed: José Olavo is added as a strong-evidence
  child of the couple. Liliosa's own death date remains unresolved; neither
  1946 variant was promoted.
- Next action: locate João Muniz Bittencourt and Suzana Ritta Brandão's
  marriage and test the 23 December 1882 collaborative-tree lead.

## 2026-07-28 — João–Susanna marriage-provision review

- Outcome: recovered the original record behind the 23 December 1882
  collaborative-tree lead and corrected its interpretation.
- Detailed log:
  [`logs/2026-07-28-joao-suzana-marriage-provision-review.md`](logs/2026-07-28-joao-suzana-marriage-provision-review.md).
- Source added: `SRC-0009`, an authorised 4749×3774 original download from DGS
  `004626365`, item 1, image 21, page 191.
- Interpretation: the entry issued provisions for João Monis Bittencourt and
  Susanna Rita Brondão to marry in the Espírito Santo parish. It does not
  certify that the ceremony occurred on 23 December 1882.
- Index conflict: FamilySearch's detail table displays `1633`, while the
  original image and citation state 23 December 1882.
- Profile audit: João's `GLMF-KCR` and Suzana's `LB1N-YC9` profiles contain no
  Memories. Their other attached sources remain unverified leads.
- Genealogical conclusion changed: the couple and intended parish are now
  strong evidence; no confirmed marriage event or island origin was added.
- Next action: locate the corresponding Espírito Santo parish ceremony entry
  after 23 December 1882 or document the exact archival access gap.

## 2026-07-28 — Espírito Santo marriage-book access review

- Outcome: exact and broader FamilySearch index searches exposed only the
  already catalogued 1882 provision and no separate ceremony entry.
- Detailed log:
  [`logs/2026-07-28-espirito-santo-marriage-book-access-review.md`](logs/2026-07-28-espirito-santo-marriage-book-access-review.md).
- Catalog finding: the reviewed Rio de Janeiro Catholic collection does not
  expose a separate Espírito Santo parish film series; this is an online-access
  gap, not proof that the book or ceremony does not exist.
- Historical finding: the Archdiocese's own heritage record confirms that the
  Espírito Santo chapel was the parish seat in 1882.
- Access requirement: the precise Cúria Metropolitana request, people, date
  window, spelling variants and supporting provision reference are documented.
  No external request was sent.
- Genealogical conclusions changed: none; 23 December 1882 remains the
  provision date rather than a confirmed ceremony date.
- Next action: while this request awaits explicit authorisation, recover the
  original record describing Vicente José de Carvalho Guimarães as Portuguese.

## 2026-07-28 — Carvalho Guimarães collective registration ingestion

- Outcome: recovered the certified record behind the transcript-only Vicente
  lead and retained FamilySearch's authorised original-upload file at
  768×1040.
- Detailed log:
  [`logs/2026-07-28-carvalho-guimaraes-registration-ingestion.md`](logs/2026-07-28-carvalho-guimaraes-registration-ingestion.md).
- Source added: `SRC-0010`, a 2025 full-content certificate transcribing the
  1915 collective registration of six Carvalho Guimarães siblings.
- Genealogical conclusions changed: added six direct ancestors and three
  source-qualified parent groups; structured the source-reported places and
  events at `strong-evidence`.
- Conflict added: the registration names the 1904 direct ancestor Maria Amora
  Guimarães, while later family information uses Maria Aurora Guimarães.
- Portuguese-origin limit: Vicente is described only as Portuguese; no
  district, municipality, island or parish is stated.
- Memories audit: the six newly identified direct-line profiles were checked.
  Francisco and Emmerenciana share the already catalogued artifact; the four
  grandparents have no Memories or attached sources.
- New lead: an 1866 Vila do Rio Claro power of attorney names a Vicente José de
  Carvalho Guimarães, but no relationship proves that he is `P-0023`.
- Next action: test the 1866 identity and search Vicente's marriage and death
  records for a Portuguese locality.

## 2026-07-28 — Living-profile files and academic-article review

- Outcome: downloaded all seven authorised original PDFs from the living
  repository subject's FamilySearch Memories after explicit owner approval.
- Detailed log:
  [`logs/2026-07-28-familysearch-living-profile-download-and-article-review.md`](logs/2026-07-28-familysearch-living-profile-download-and-article-review.md).
- Deduplication: two separate birth Memories yielded byte-identical PDFs; both
  Memory identifiers remain in provenance, while only one file is retained.
- Sources added: `SRC-0011` for the private birth certificate,
  `SRC-0012`-`SRC-0015` for four distinct civil manifestations of one marriage,
  and `SRC-0016` for the Chagas dissertation.
- Privacy result: all seven Memories displayed `Private` during this session.
  No FamilySearch visibility or profile setting was changed.
- Article result: the 2018 dissertation provides historical Ferreira Armond
  context and cites Lacerda's 2010 thesis, but it does not connect Aristão or
  his source-reported parents to that historical group. Its Azorean-origin
  statement remains a research lead only.
- Genealogical conclusions changed: no disputed deceased-ancestor conclusion
  changed; the private civil records corroborate the living direct line.
- Next action: resume the current Vicente identity and Portuguese-locality
  objective.

## 2026-07-28 — Direct-line document audit and online Ferreira Armond leads

- Outcome: reconciled every direct-line source transcription against its image;
  corrected Geraldo's death entry number (39006, not a misread 39005) and added
  missing causes of death, the son-declarant and register citations; recovered
  Antenor's (1923) and Iris's (1929) reported births from the 1949 marriage
  certificate as events E-0017/E-0018 with place PL-0009; and added resolvable
  FamilySearch URLs to every collaborative-tree lead in the coverage ledger.
- Detailed log:
  [`logs/2026-07-28-direct-line-document-audit-and-online-leads.md`](logs/2026-07-28-direct-line-document-audit-and-online-leads.md).
- Leads recorded (not promoted): Santo Antônio de Sapucaia (a freguesia from
  1871) strengthens the SRC-0009 parish re-reading over Espírito Santo; a
  published genealogy names Simplício Ferreira Armond and Elisa Balbina Tolledo
  in Piacatuba (Leopoldina), corroborating the fuller-name leads for P-0016 and
  P-0017.
- Genealogical conclusions changed: none; source transcriptions were corrected
  and two reported births were structured as strong-evidence events.
- Next action: with authorised FamilySearch access, retrieve the original 1982
  birth register so the subject's parentage can reach `confirmed`, inspect the
  Piacatuba baptism books for Aristão's family, and re-examine SRC-0009 at full
  resolution to settle the Sapucaia-versus-Espírito-Santo parish question.

## 2026-07-29 — Online gap-and-resource research

- Outcome: four parallel web-research passes mapped concrete resources to every
  open direct-line gap and blocker, all recorded as leads (no conclusion changed).
- Detailed log:
  [`logs/2026-07-29-online-gap-and-resource-research.md`](logs/2026-07-29-online-gap-and-resource-research.md).
- Key leads: FamilySearch "Image Restricted" scans are viewable free at an
  affiliate library; Aristão's family baptisms are in the Piacatuba/Leopoldina
  parish (catalog 345430, films 004640627/004640632), confirmed by sibling
  Marfisa (1873); the Azorean Ferreira Armonde origin is documented (Lacerda 2010;
  Chagas UFMG) but NOT yet linked to Aristão; Volta Redonda was a district of
  Barra Mansa in 1946; Sapucaia's pre-1925 books may be at the Cúria do Rio.
- Verified place equivalence: Iris Bohrer's "Presidente Soares" is present-day
  **Alto Jequitibá, MG** (IBGE), not Raul Soares; PL-0009 updated accordingly.
- Artifacts: added `research/familysearch-image-targets.md` (an autonomous-agent
  task-spec for image retrieval) and the `evidence/incoming/` staging area.
- Genealogical conclusions changed: none.
- Next action: retrieve the Aristão baptism and Aristão×Liliosa marriage images
  via an affiliate library; order Liliosa's 1946 death; chase Vicente's Carangola
  marriage/inventário for his Portuguese locality.

## 2026-07-29 — Parallel vital-records and origin research

- Question: advance, read-only and in parallel, the Liliosa vital-records,
  Ferreira Armond bridge, Vicente Portuguese-origin and Sapucaia-marriage gaps
  while authorised FamilySearch retrieval waits on Codex.
- Method: four parallel web agents, public sources only; no authenticated
  session. Everything recorded as leads; no conclusion changed.
- Detailed log:
  [`logs/2026-07-29-parallel-vital-records-and-origin-research.md`](logs/2026-07-29-parallel-vital-records-and-origin-research.md).
- Access test (empirical): DigitArq, the Azores archive, Arquivo Nacional-Rio
  (CAPTCHA), CEPESE/APM (POST) and FamilySearch (login) are unreadable by the
  assistant's fetch tool — retrieval belongs to the Codex browser agent or a
  person.
- Key leads: Liliosa's 1946 death most likely sits in the Barra Mansa death
  index (not Volta Redonda), and the Aristão×Liliosa marriage in
  Piacatuba/Leopoldina; the Simplício×Elisa marriage (~1855-1872) is the decisive
  Ferreira Armond bridge record, with the b.1784 Simplício doubly documented as
  unmarried (anti-merge holds) and the patriarch's own origin itself contested;
  Vicente's parish is Santa Luzia do Carangola (mother parish Tombos), and his
  Carangola civil óbito (<1915) should state his naturalidade; João's Sapucaia
  provision/habilitação (Cúria do Rio) and the completed assento (Paróquia de
  Sapucaia → Cúria de Valença) are in separate custodies, and his São Miguel
  origin lead is supported (not contradicted) by an 1871 naturalisation.
- Portugal/Azores workflow refined (100-year rule → free DigitArq images; GEA
  for Azores; Torre do Tombo = Lisbon district) and recorded in
  `research/README.md`.
- Genealogical conclusions changed: none.
- Next action: Codex to pull the FamilySearch targets (Barra Mansa 1946 death;
  Piacatuba/Leopoldina marriage; Santa Luzia/Tombos marriage and Carangola óbito;
  Simplício×Elisa marriage and Marfiza's full act; Sapucaia catalog) and run the
  name-searchable CEPESE and Arquivo Nacional-Rio databases.

## 2026-07-29 — Ferreira Armond deep dig, locality catalogue, 1831 census

- Question: extract the full Barbacena Armonde tree, exhaustively sweep the
  Leopoldina/Piacatuba transcriptions, harvest a per-locality FamilySearch
  catalogue, and read the 1831 Curral Novo census (a primary source).
- Method: five parallel read-only agents (curl / pdftotext / Wayback; headless
  Chrome for the public FS wiki) plus a direct read of the census. WebSearch was
  exhausted; everything is a lead.
- Detailed log:
  [`logs/2026-07-29-ferreira-armond-deep-dig-and-locality-catalogue.md`](logs/2026-07-29-ferreira-armond-deep-dig-and-locality-catalogue.md).
- Key results: the documented Armonde tree does **not** reach Piacatuba (the
  bridge is currently unsupported, not merely unproven); the 1831 census confirms
  the anti-merge on a primary document (Simplício b.~1785 was 46 and solteiro,
  and the district Juiz de Paz); the decisive test is the untranscribed Piacatuba
  marriage register; the patriarch's origin is documentarily Azorean
  (Terceira/São Sebastião), the French claim uncited. Built a per-locality
  catalog-ID map (345430 Leopoldina parish, 516378 Barra Mansa, 385592 Sapucaia,
  21641 Barbacena, ...); Carangola/Tombos have no local catalog (manual review).
- Genealogical conclusions changed: none.
- Preserved sources in `research/resources/`: the ASBRAP "Armond, Por Quê?"
  article, the 1831 census transcription, the Lacerda 2010 thesis, the Chagas
  2018 dissertation and a Senra-blog snapshot.
- Next action: batch the ledger/worksheet/coverage updates and the occupations
  population with the running projetocompartilhar crawl, then Codex retrieval.

## 2026-07-29 — Projeto Compartilhar crawl and Azores source survey

- Question: survey projetocompartilhar.org (full crawl), myportuguesegen (Azores
  resource directory) and the Scribd Forjaz & Mendes "Genealogias da Ilha
  Terceira" for our families and the Azorean Armonde leads.
- Method: three read-only agents + direct fetches; curl/pdftotext/Wayback only
  (WebSearch exhausted). All leads.
- Detailed log:
  [`logs/2026-07-29-projetocompartilhar-and-azores-source-survey.md`](logs/2026-07-29-projetocompartilhar-and-azores-source-survey.md).
- Key results: projetocompartilhar's scope (São Paulo + sul de Minas) excludes
  Piacatuba/RJ/ES; new lead of a MARRIED Manoel Antonio de Armond (João Gomes
  1831) as a candidate later-namesake; the 1751 will corroborates the Azorean
  origin. Scribd (Forjaz) is bot-walled → browser/human target; the evidence
  route is the GEA parish images. Built a per-locality FamilySearch catalog-ID map.
- Preserved in research/resources/: the João Gomes census and the 1751 inventory.
- Contacts sent (research/correspondence-log.md): Mauro Senra, Nilza Cantoni,
  Paróquia de Piacatuba.
- Genealogical conclusions changed: none.
- Next action: Codex FamilySearch pulls (345430 Piacatuba marriage + baptisms
  1879+; 516378 Barra Mansa; 385592 Sapucaia; 3479702 Iris 1929 birth); await the
  three replies; populate person occupations from held sources.

## 2026-07-29 — Owner-supplied Armond documents: siblings and the Eugenópolis locus

- Question: assess owner-located documents (FamilySearch + newspaper) on Aristão
  Ferreira Armond's family.
- Detailed log:
  [`logs/2026-07-29-owner-supplied-armond-family-documents.md`](logs/2026-07-29-owner-supplied-armond-family-documents.md).
- Key results: Marfiza Ferreira Armond's 1962 death (aged 89 → b.~1873, viúva)
  names the same parents as Aristão's death → she is his sister; a second primary
  record of Simplicio Ferreira Armond + Eliza/Elisa Toledo, giving Elisa's maiden
  surname Toledo; "filho/filha legítima" in both → Simplício & Elisa were married.
  José Olavo's 1975 marriage bann (O Processo) names him "natural de Eugenópolis",
  son of Aristão + Liliosa → the family's locus is EUGENÓPOLIS, MG.
- Redirect: search the Aristão×Liliosa marriage and the children's births in
  Eugenópolis (not Leopoldina). Does NOT prove the Barbacena/Azorean bridge.
- Conclusions changed: none promoted; formal source cataloguing pending saved files.
- Next action: catalogue Marfiza's death + the José Olavo bann once files are
  staged; redirect the marriage search to Eugenópolis.

## 2026-07-29 — Full-Text hits: Ferreira Armond in the Muriaé/Leopoldina probates

- Question: FamilySearch Full-Text (AI-OCR) search for Aristão and Simplicio
  Ferreira Armond in MG notarial/probate records.
- Detailed log:
  [`logs/2026-07-29-fulltext-muriae-leopoldina-probate-hits.md`](logs/2026-07-29-fulltext-muriae-leopoldina-probate-hits.md).
- Key result: an 1881 Leopoldina probate/partilha (ARK 3:1:3QHJ-YQWY-R9GH) lists
  the Toledo heirs — "Simplício José Ferreira Armond casado com D. Eliza Balbina
  de Toledo" and her siblings (Maria Bulandina de Toledo m. Manoel Marques Jorge;
  Ladisláo Egydio Ferreira de Toledo; Geraldo Augusto de Toledo Lima; Josepha
  Olympia) — documenting the marriage and opening Elisa's parentage. Simplício
  ("Capitão") and Aristão recur across Muriaé/Leopoldina probate/property records
  (Simplício 1875-1913; Aristão 1903-1921) — the family's inventário evidence.
- Provenance: 16 full-text page images + fulltext_candidates.csv staged in
  evidence/references/armond-muriae-fulltext-probates/. Formal cataloguing to follow.
- Conclusions changed: none promoted; Azorean bridge still unproven.
- Next action: read the 1881 inventário fully to name Elisa's parent; catalogue
  the key probate images; chase Elisa's father in Argirita.
