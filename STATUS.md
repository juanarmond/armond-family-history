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

1. **Direct-line follow-up:** Eliza’s parentage CONFIRMED (7 Aug 2026 Film 2
   triage, PRB-0006): Eliza Balbina de Toledo (P-0017) is a daughter of José Cezário
   de Toledo Lima (P-0054) × Claudina Brandina de Jesus (P-0055), family F-0026.
   Conflict #14 RESOLVED. Note: JC had a son also named "Simplício Ferreira de
   Toledo" (item 6, both 1867 inventários, b.~1853, died before 1879) — a DIFFERENT
   person from Simplício José Ferreira Armond (P-0016, Eliza’s husband). P-0016’s
   parentage is UNKNOWN. The Toledo line
   now reaches **Portugal**: PAR-0025 (1777 Piracatu baptism, primary) confirms
   Amaro da Silva Xavier’s parents as Amaro da Silva Barreto (Guimarães, Braga) ×
   Perpétua da Silva (São Paulo) — F-0031; and Ignez’s parents as João Rodrigues de
   Mello (Viana, Braga) × Maria Francisca Cordeira (Villa de Ouro) — F-0032.
   Material conflict: PAR-0025 places Amaro’s birthplace at Meia Ponte (Goiás);
   PAR-0023 (1810) says "naturais e batizados da Freguesia de Barbacena" — both
   preserved. **Owner decision pending:** whether to ingest the titled Ferreira Armond
   branch (collateral).
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
| Structured people | 81 |
| Structured families | 39 |
| Structured events | 70 |
| Structured places | 9 |
| Structured sources | 76 |
| Structured FAN references | 13 |
| Inventoried retained documents | 73 |
| Validation | 288 entities; zero errors or warnings at the last check (2026-08-10) |
| Automated tests | 69 passing at the last check |

The catalogued sources span the Armond/Paz, Muniz Bittencourt/Azevedo,
Engracio/Souza/Guimarães, Bohrer and Portuguese-origin lines, include the maternal
Toledo probate cluster and the Barbacena context sources, and include the living
subject's private records. Details are canonical in `data/sources/`; gaps in
`data/record-coverage.yaml`.

## Research snapshot

| Area | Strongest current position | Strategic gap |
| --- | --- | --- |
| Armond and Paz | Aristão's death is confirmed; a second original government record independently names Liliosa Paz Armond and reports the couple as José Olavo's parents. Eliza's parentage CONFIRMED (7 Aug 2026, PRB-0006 Film 2 triage): Eliza Balbina de Toledo (P-0017) is daughter of JC × Claudina (P-0054/P-0055, F-0026). Simplício Armond's (P-0016) own parentage remains UNKNOWN — he is Eliza's husband, not JC's son; JC had a distinct son "Simplício de Toledo" (b.~1853, died before 1879). Leads (not evidence): a sibling Marfiza (bapt. 1873, N. Sra. da Piedade, Piacatuba) fixes the likely baptism parish | Retrieve Aristão's baptism and marriage; find the Simplício×Eliza marriage; locate Simplício Armond's own parents; locate Liliosa's parents |
| Muniz Bittencourt and Azevedo | Deocleciano's own 1892 baptism (PAR-0004) and Susanna's 1866 baptism (PAR-0005) are catalogued; João's 1915 death (PAR-0007) confirms São Miguel origin; parents primary-confirmed by PAR-0015 (father Manoel Muniz Bytancourt P-0042, mother Francisca Roza P-0047) and grandparents (F-0023). João's own baptism found: PAR-0022, b. 24 Oct 1845. Marriage PAR-0024 found: 1 Feb 1845. Luiza's parents (F-0018) and Carangola origin fixed | The completed João × Susanna ceremony entry; the Azevedo grandparents' own vital records |
| Engracio, Souza and Guimarães | The 1915 collective registration documents Maria Amora/Aurora, her parents and all four grandparents; her 1991 death (CIV-0018) confirms the same parents, and Antonio Engracio Filho's 1964 death (CIV-0017) names his parents — Antonio Engracio de Souza × Luzia Pinheiro da Conceição — and attests the couple's marriage; Cidalia's own 1930 birth (CIV-0022) confirms her parents and all four grandparents and fixes her birth date at 15 September 1930 | Locate Vicente's Portuguese origin; find the Antonio × Maria Aurora marriage act and the P-0032/P-0033 own vital records (both off-index) |
| Bohrer | João Gonçalves Bohrer (d.1970) and Celina/Selina Bohrer (d.1977) catalogued from RJ civil deaths (CIV-0014/0015). Celina's maternal line reaches grandparents: Joaquim José Bohrer's parents Francisco José Bohrer × Rosa Eugenia de Lemos (PAR-0002) and Lucinda's parents Antonio da Silva Ferreira × Maria Joanna da Silva Ferreira (CIV-0019). Francisco José's parents Jacob Bahrer × Catharina Mayer (F-0024) primary-confirmed by PRB-0005; Rosa Eugenia's parents Manoel de Lemos Pereira × Maria Thereza de Jesus (F-0025) confirmed by PAR-0016. **Valentim's paternal line extended (2026-08-08/09, PUB-0003 + primary Swiss parish registers):** Valentim Martinho Bohrer b. 14/11/1868 (strong-evidence); parents Vicente Borer (P-0070, b.06/09/1828) × Maria Heggendorn (P-0071) — F-0034; grandparents Laurent Borer (P-0068, b.27/02/1797, Grindel, Soleure, CH, Heureux Voyage 1819) × Anna Maria Werhly (P-0069) — F-0033; great-grandparents Johann Jacob Wehrli (P-0072, b.17/01/1751, d.NF 28/05/1827) × Elisabetha Borer (P-0073, d.NF 10/10/1832) — F-0035, marriage PRIMARY confirmed by PAR-0029 (Grindel 27/01/1782); **2026-08-09 NEW (PRIMARY):** JJ Wehrli's parents confirmed by PAR-0027 (Grindel 1751 baptism): Johannes Wehrli (P-0074) × Barbara Alleman (P-0075), F-0036; Elisabetha Borer's parents confirmed by PAR-0028 (Erschwil 1760 baptism, church book #68): Joseph Borer (P-0076) × Anna Maria Borer (P-0077), F-0037. Line now reaches **1719 (est. birth of Johannes Wehrli × Barbara Alleman)** in Grindel/Solothurn. | Valentim's NF baptism (pre-1874, Fundação D. João VI); Carolina Bohrer's maiden name and birth record; Joaquim José's baptism (absent from Imigrantes compilation); Laurent Borer's parents (best lead: Jacob Borer × Catharina Heggendorn, Grindel 1782); Johannes Wehrli × Barbara Alleman marriage record not found |
| Portuguese origins | `CIV-0007` directly reports Vicente as Portuguese; an 1866 Rio Claro record is an unlinked identity lead | Identify a district, municipality and parish before searching Portugal |

The direct-line working roster follows Ahnentafel order from `P-0001` through
`P-0017`. These are immutable repository identifiers, not proof of
relationships. Collaborative profiles remain navigation leads only.

## Material unresolved conflicts

1. Cidalia's birth date: RESOLVED (2026-07-31) as 15 Sep 1930 (CIV-0022); "15 Nov" variant superseded; `Engracio`/`Igracio` forms require source-by-source preservation.
2. Liliosa's death date is now RESOLVED (16 April 1946, per Geraldo's 1952
   marriage CIV-0002 → event E-0028) and her birthplace is Eugenópolis, MG; her
   original surname and parents remain unresolved (next: the Eugenópolis 1946 óbito
   inteiro teor, which would name her parents).
3. The fuller names and identities of Aristão's reported parents.
4. The exact transcription of João Gonçalves Bohrer's parents.
5. Vicente José de Carvalho Guimarães's Portuguese parish.
6. RESOLVED (1 Aug 2026): João Muniz Bittencourt, São Miguel immigrant, b.~1847; father Manoel MUNIZ Bytancourt (P-0042), mother Francisca Roza (P-0047), grandparents F-0023 (PAR-0015).
7. Whether several nineteenth-century collaborative profiles refer to the same
   people documented in the family records.
8. Whether the 1871 naturalisation link attached to João's profile concerns the
   same person; the unproved 1864 birth would make the chronology unusually
   early and requires the original record.
9. FamilySearch's index table displays `1633` for the provision catalogued as
   `PAR-0001`; the original image and citation state 23 December 1882.
10. RESOLVED (2026-07-30): "Maria Amora/Aurora Guimarães" — same woman (P-0011);
    identical parents on CIV-0007 and CIV-0018; preferred name "Maria Aurora."
11. Whether the 1866 Vila do Rio Claro power of attorney names the same
    Vicente José de Carvalho Guimarães documented as Francisco's father.
12. RESOLVED (31 July 2026): José Secundino de Azevedo's given name (P-0038). The
    parish register of the 1916 marriage (PAR-0012) reads "Secundino Maria de Azevedo",
    matching CIV-0001 and the "José Secundino" of the 1922 baptism (PAR-0003) — the
    2019 civil inteiro-teor's "Sebastião" (CIV-0006) was a misread.
13. João Gonçalves Bohrer × Celina marriage place: "neste Município" (Nova
    Friburgo, RJ) in CIV-0016 (1924) vs "em Carangola, MG" [uncertain] in CIV-0014
    (1970); confirm the CIV-0014 reading before use.
14. Eliza Balbina de Toledo's parentage: RESOLVED (7 August 2026). PRB-0006 (1879
    Matilde inventário, Film 2 triage) confirms Eliza as a daughter of José Cezário de
    Toledo Lima × Claudina Brandina de Jesus (F-0026), appearing as representante #5
    under heir #4. Earlier in the same session a misread introduced the opposite claim;
    corrected same day. See PRB-0006 abstract and P-0017 notes for full evidence chain.
15. Francisco Leocádio de Toledo (P-0061) as Ladisláo's son vs. son-in-law:
    PRB-0009-gen1 lists FL as child #4 of Ladisláo × Mathilde (F-0027). The 1882
    embargos judgment transcript (ladislao-1867-part05-pp309-387.md, p.383, 2026-08-08)
    reads "mulher de Francisco Leocadio de Toledo, sobreviveu ao seu pai Ladislão" —
    placing Maria Joaquina de Jesus as Ladisláo's daughter and FL as son-in-law.
    Image verification required before any restructuring of F-0027 or P-0061.

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
