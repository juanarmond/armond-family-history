# Project Status

> This file is the present operational snapshot. It contains the current
> objective, blockers, material conflicts and strategic priorities only.
> Research history belongs in `logs/LOG.md` and its detailed logs;
> engineering history belongs in `CHANGELOG.md`; genealogical conclusions
> belong in structured YAML and source records.

## Current objective

Obtain and catalogue Aristão Ferreira Armond's baptism and his marriage to
Liliosa Paz Armond from the FamilySearch image ranges now confirmed viewable
(baptism film `004640627` from image 54; marriage film `004640632` from image
6), and locate Liliosa's own vital records. FamilySearch retrieval now runs through the external
retrieval agent, which syncs its finds into `research/from-retrieval/`; this
assistant runs the value gate (`research/from-retrieval-triage-ledger.md`) and
catalogues each valuable image as evidence.

### Objective completion signal

- Aristão's baptism entry is retrieved, transcribed and catalogued as a source,
  or the target image range is exhausted with a documented negative result.
- The Aristão×Liliosa marriage entry is retrieved and catalogued, recording both
  parties' reported parents where present.
- Liliosa's own death, birth or marriage record is located, or the searched
  series and their bounds are recorded as negative results.
- Any retained image uses the highest resolution authorised by the provider.

## Next steps

This is the immediate execution queue, in order:

1. **Direct-line follow-up (30 July value-gate pass complete):** every image in
   the `research/from-retrieval/` drop has now been read per-image. PRB-0004
   catalogued Eliza's maternal Toledo ancestry deed (grandparents Mathilde ×
   Ladisláo; parents Antonio Zeferino de Toledo × Maria Perpétua). NEXT: confirm
   Eliza's parents — retrieve PRB-0004's adjacent folios (the grantor names) and
   the 1881 partilha's opening to test the hypothesis that Antonio Zeferino de
   Toledo × Maria Perpétua are P-0017's parents, and resolve the two same-named
   "Ladisláo Egydio Ferreira de Toledo" (elder grandfather vs grantor) before
   creating any Toledo ancestor edges. **Owner decision pending:** whether to
   ingest the titled Ferreira Armond branch (Barão de Pitangui / Amaro), which is
   collateral with no established link to the owner's own line.
2. Catalogue each retrieved image: privacy-review, reserve a source, transcribe,
   and promote the directly-attested events.
3. Locate Liliosa's own death, birth or marriage record; retest the Volta
   Redonda / Barra Mansa civil death series once it reaches April 1946.
4. Continue the 1866 Vicente identity lead and his Portuguese-locality search as
   the next line once the Aristão and Liliosa retrieval is queued.
5. **Human-access tasks:** request the João–Susanna ceremony entry from the
   Cúria and review any still-restricted Aristão parish images when authorised.

Keep this queue short and actionable. Detailed person-by-record actions remain
canonical in `data/record-coverage.yaml`; retrieval finds arrive via the
`research/from-retrieval/` sync and are tracked in
`research/from-retrieval-triage-ledger.md`; strategic branch order remains under
**Strategic research priorities** below.

## Current blockers and dependencies

- The imported ChatGPT conversation refers to 24 image attachments whose
  binaries and metadata were not transferred. Their descriptions remain
  preserved in the conversation-transfer audit, but exact document matching
  requires the original attachments.
- FamilySearch image groups `004640627` (Aristão's baptism, from image 54) and
  `004640632` (the Aristão×Liliosa marriage, from image 6) are viewable in the
  identified ranges and are queued for the external retrieval agent (its finds
  arrive via `research/from-retrieval/`); only the earlier images in each group
  still display `Image Restricted` and would need authorised FamilySearch Center
  or Library access.
- Archive enquiries, paid certificates and conservatory or parish requests
  require explicit user authorisation before submission.
- Liliosa's 1946 death now points primarily to the Barra Mansa civil death
  index (Volta Redonda was its district until 1954 and its own óbito registry
  opened only ~November 1946); this is a Codex retrieval target, not a hard
  blocker.
- FamilySearch exposes João and Susanna's 1882 marriage provision but no
  separate ceremony entry. The provision was re-read as directed to the Santo
  Antônio de Sapucaia parish (not Espírito Santo); the surviving Sapucaia
  marriage-book series and the exact archival request require identification
  and explicit authorisation before submission.
- Requiring the repository-health workflow in GitHub branch rules requires
  repository-administrator access.

None of these dependencies prevents the current Aristão and Liliosa retrieval
and cataloguing work.

## Repository snapshot

| Item | Current state |
| --- | --- |
| Structured people | 39 |
| Structured families | 18 |
| Structured events | 33 |
| Structured places | 9 |
| Structured sources | 35 |
| Structured FAN references | 13 |
| Inventoried retained documents | 34 |
| Validation | 147 entities; zero errors or warnings at the last check |
| Automated tests | 58 passing at the last check |

The 35 catalogued sources (across the `CIV`, `GOV`, `PAR`, `PRB` and `PUB`
categories) span the Armond/Paz, Muniz Bittencourt/Azevedo,
Engracio/Souza/Guimarães, Bohrer and Portuguese-origin lines, include the
maternal Toledo probate cluster and the Barbacena context sources, and include
the living subject's private records. Source
details, archival references, transcriptions, limitations and conclusion links
are canonical in `data/sources/`; record-by-record gaps are canonical in
`data/record-coverage.yaml`.

## Research snapshot

| Area | Strongest current position | Strategic gap |
| --- | --- | --- |
| Armond and Paz | Aristão's death is confirmed; a second original government record independently names Liliosa Paz Armond and reports the couple as José Olavo's parents. Leads (not evidence): a sibling Marfisa (bapt. 1873, N. Sra. da Piedade, Piacatuba) fixes the likely baptism parish; the documented Azorean Ferreira Armonde tree does NOT reach Piacatuba (bridge unsupported), and the 1831 census confirms the anti-merge on a primary document; a third daughter, Aristides Ferreira Armand (m.1894, CIV-0023), adds a fourth attestation/signature of Simplício José Ferreira Armand and places the family at Boa Família/Muriaé in 1894, with Aristides born ~1875 at Rio Pardo da Leopoldina (the Argirita area) | Retrieve Aristão's baptism (from ~1879) and the Aristão×Liliosa marriage; find the Simplício×Elisa marriage (the decisive bridge test, likely Rio Pardo/Argirita ~1870s); locate Liliosa's parents (her death date is now fixed) |
| Muniz Bittencourt and Azevedo | The 1916 marriage (CIV-0001) reports Deocleciano's parents; the 1882 provision (PAR-0001) names João and Susanna; Antenor's brother Aristides's 1922 Carangola baptism (PAR-0003) confirms Deocleciano × Luiza, establishes Luiza's parents (José Secundino de Azevedo × Thereza Fernandes de Azevedo, F-0018) and fixes the family's Carangola (MG) origin | Completed João × Susanna ceremony entry in the Sapucaia registers; João/Susanna's and the Azevedo grandparents' own vital records; test rather than assume island origin |
| Engracio, Souza and Guimarães | The 1915 collective registration documents Maria Amora/Aurora, her parents and all four grandparents; her 1991 death (CIV-0018) confirms the same parents, and Antonio Engracio Filho's 1964 death (CIV-0017) names his parents — Antonio Engracio de Souza × Luzia Pinheiro da Conceição — and attests the couple's marriage; Cidalia's own 1930 birth (CIV-0022) confirms her parents and all four grandparents and fixes her birth date at 15 September 1930 | Locate Vicente's Portuguese origin; find the Antonio × Maria Aurora marriage act and the P-0032/P-0033 own vital records (both off-index) |
| Bohrer | João Gonçalves Bohrer (d.1970) and Celina/Selina Bohrer (d.1977) catalogued from RJ civil deaths (CIV-0014/0015). Celina's maternal line now reaches her grandparents: Joaquim José Bohrer's parents Francisco José Bohrer × Rosa Eugenia de Lemos (their 1879 Nova Friburgo marriage, PAR-0002) and Lucinda's parents Antonio da Silva Ferreira × Maria Joanna da Silva Ferreira, both named in Alberto Bohrer's 1890 birth (CIV-0019) | Valentim Martinho Bohrer × Carolina's own records; Francisco José Bohrer's parents (the Nova Friburgo German-Swiss colony immigrant boundary, ~1820s, off-index); the Rosa Eugenia de Lemos / Itaboraí Lemos family; and the João Gonçalves × Celina civil marriage |
| Portuguese origins | `CIV-0007` directly reports Vicente as Portuguese; an 1866 Rio Claro record is an unlinked identity lead | Identify a district, municipality and parish before searching Portugal |

The direct-line working roster follows Ahnentafel order from `P-0001` through
`P-0017`. These are immutable repository identifiers, not proof of
relationships. Collaborative profiles remain navigation leads only.

## Material unresolved conflicts

1. Cidalia's birth date: RESOLVED (2026-07-31) as 15 September 1930 by her own
   civil birth registration (CIV-0022, Alvorada) — the "15 November" family variant
   is superseded. The recorded `Engracio`, `Igracio` and married-name forms still
   require source-by-source preservation rather than silent normalisation.
2. Liliosa's death date is now RESOLVED (16 April 1946, per Geraldo's 1952
   marriage CIV-0002 → event E-0028) and her birthplace is Eugenópolis, MG; her
   original surname and parents remain unresolved (next: the Eugenópolis 1946 óbito
   inteiro teor, which would name her parents).
3. The fuller names and identities of Aristão's reported parents.
4. The exact transcription of João Gonçalves Bohrer's parents.
5. Vicente José de Carvalho Guimarães's Portuguese parish.
6. Whether João Muniz Bittencourt had an Azorean, Madeiran or other Portuguese
   island origin.
7. Whether several nineteenth-century collaborative profiles refer to the same
   people documented in the family records.
8. Whether the 1871 naturalisation link attached to João's profile concerns the
   same person; the unproved 1864 birth would make the chronology unusually
   early and requires the original record.
9. FamilySearch's index table displays `1633` for the provision catalogued as
   `PAR-0001`; the original image and citation state 23 December 1882.
10. RESOLVED (2026-07-30): "Maria Amora Guimarães" (1915 birth registration,
    CIV-0007) versus "Maria Aurora Guimarães" (her own 1991 death CIV-0018, her
    marriage CIV-0002 and family information). Both name the identical parents,
    proving the two forms are one woman (P-0011). Both are preserved as variants;
    the preferred name is "Maria Aurora" — three sources including her own death
    outweigh the single retrospective, certified-copy birth registration (same
    reasoning as P-0015 Celina/Selina).
11. Whether the 1866 Vila do Rio Claro power of attorney names the same
    Vicente José de Carvalho Guimarães documented as Francisco's father.
12. José Secundino de Azevedo's given name (P-0038): "José Secundino"/"Secundino
    Maria" in the 1922 baptism (PAR-0003) and 1916 marriage register (CIV-0001),
    but the 2019 certidão of the same act (CIV-0006, handwritten) is read
    "Sebastião [uncertain] de Azevedo" — probable misread; verify the original
    before altering P-0038.
13. João Gonçalves Bohrer × Celina marriage place: "neste Município" (Nova
    Friburgo, RJ) in CIV-0016 (1924) vs "em Carangola, MG" [uncertain] in CIV-0014
    (1970); confirm the CIV-0014 reading before use.

Do not resolve a conflict by deleting the weaker version. Preserve every
material interpretation with its source and confidence.

## Strategic research priorities

1. Retrieve and catalogue Aristão's baptism and the Aristão×Liliosa marriage
   from the FamilySearch image ranges now confirmed viewable.
2. Locate Liliosa's own death, burial, birth or marriage record.
3. Obtain the João–Susanna ceremony entry from the Santo Antônio de Sapucaia
   parish registers and their earlier records.
4. Test the 1866 Vicente identity and locate a family-linked record that gives
   his Portuguese locality.
5. Catalogue João Gonçalves Bohrer and Celina Bohrer's own vital records.
6. Extend the Engracio/Souza, Guimarães and Azevedo lines one documented
   generation at a time.

The canonical person-by-record actions and last-reviewed dates are maintained
only in `data/record-coverage.yaml`.

## Engineering state

- **Active:** catalogue the Aristão and Liliosa retrievals into structured
  evidence once Codex delivers; reassess assertion-level citation quality after
  5–10 varied records.
- **External:** require the frozen repository-health check in GitHub branch
  rules; the external retrieval agent syncs authorised FamilySearch finds into
  `research/from-retrieval/` for the value gate.
- **Deferred until schema stability:** generated person pages.
- **Complete:** versioned schemas, evidence inventory, stable ID allocation,
  recoverable batch promotion, validation, tests, GitHub Actions, the static
  read-only family-tree viewer, the certified-copy (derivative) confirmation
  rule, and the GEDCOM full-backup exporter (7.0/5.5.1 + GEDZIP; `make export`).

Completed engineering work is recorded only in `CHANGELOG.md`.
