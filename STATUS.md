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
catalogues each valuable image as evidence. The deeper open problem — **Simplício José Ferreira Armond's (P-0016) unknown parentage** — is the family's central genealogical gap; its current state, candidate short-list and the three decisive records are consolidated in Next steps §1.

### Objective completion signal

- Aristão's baptism entry is retrieved, transcribed and catalogued as a source,
  or the target image range is exhausted with a documented negative result.
- The Aristão×Liliosa marriage entry is retrieved and catalogued, recording both
  parties' reported parents where present.
- Liliosa's own death, birth or marriage record is located, or the searched
  series and their bounds are recorded as negative results.
- Any retained image uses the highest resolution authorised by the provider.

## Next steps

_Resume checkpoint refreshed 2026-09-01._ Ordered queue; per-record detail lives in
`data/record-coverage.yaml`, archive replies in `logs/correspondence-log.md`.

1. **PRIMARY OPEN PROBLEM — Simplício José Ferreira Armond (P-0016): father unknown.**
   Modelled only as Eliza's husband (union F-0006), a child in no family, but the gap is
   well-bounded. _Ruled out (sourced):_ not the childless elder Simplício (b.~1785; PUB-0002
   + GOV-0002), and not a Toledo — the 2026-08-13/14 PRB-0006/PRB-0009 re-reads confirm his
   **Armond** surname separates him from all three Toledo "Simplícios". _Leading unproven
   hypothesis:_ descent from the Barbacena/Azorean Ferreira Armonde trunk — one of the six
   adult "Ferreira Armonde" heirs of Honório's 1845 inventário (Manoel Ignácio, Simão José,
   Pedro José Joaquim, Flávio José, Marcelino, Padre Francisco Antonio); circumstantial only,
   mint no trunk nodes. _Three decisive records, all needing physical/authorised retrieval:_
   (a) the Simplício × Eliza marriage (~1868–72, Argirita) — best test, blocked on the Arquivo
   Histórico Arquidiocesano de Juiz de Fora (C-004, awaiting); (b) his ~1853 baptism; (c) the
   Barbacena Ferreira Armonde _principal_ autos (off-tool, AHMPAJS) and the Pitanguy inventário
   (proc. 39803183/39803190, COARPE BH via the C-006 form).
2. **Aristão & Liliosa (external agent):** Aristão's baptism (film 004640627 img 54) and his
   marriage to Liliosa (film 004640632 img 6); Liliosa's own records (her 1946 Eugenópolis
   óbito naming her parents; Barra Mansa 1946 civil-death index). Value-gate and catalogue.
3. **Flagged drop targets (record-coverage P-0016):** culturacores C-1673-1766 `_0034`
   (+ sweep `_0030–_0044`) for the third Cardozo × Fagundes attestation; the Honório 1845
   principal autos; the Pitanguy inventário. Trunk material stays LEAD-level until a primary
   record bridges it.
4. **Other lines:** Vicente's Portuguese parish (CIV-0007); the João–Susanna Sapucaia ceremony
   entry (Cúria, needs authorisation); the Antonio Engracio × Maria Aurora marriage;
   Iris Bohrer's (P-0007) 1929 baptism — request from Paróquia Sant'Ana de Manhuaçu / Alto
   Jequitibá (C-007); conflict #15 (Francisco Leocádio son vs son-in-law).

## Current blockers and dependencies

- **Simplício (P-0016) parentage bridge:** the decisive Simplício × Eliza marriage is blocked
  on the Arquivo Histórico Arquidiocesano de Juiz de Fora (C-004, awaiting reply). The
  Barbacena/Pitanguy trunk probate is reachable via the COARPE form (C-006, BH central); the
  Honório 1845 _principal_ autos are off-tool (AHMPAJS Barbacena). BPAR Angra high-res declined
  — the held Terceira scans are legible and the free CDN offers nothing higher (C-005).
- **FamilySearch restricted images:** groups `004640627` (Aristão baptism, from img 54) and
  `004640632` (Aristão × Liliosa marriage, from img 6) are queued for the external retrieval
  agent; earlier images in each group need authorised FS Center/Library access.
- **Authorisation-gated:** archive enquiries, paid certificates and parish/conservatory requests
  need explicit owner authorisation; the João–Susanna Sapucaia ceremony entry and the
  repository-health branch rule are pending human access.

These dependencies gate only the archive-retrieval work; the Simplício-parentage records require
physical or authorised access, not read-only web.

## Repository snapshot

| Item | Current state |
| --- | --- |
| Structured people | 95 |
| Structured families | 46 |
| Structured events | 75 |
| Structured places | 9 |
| Structured sources | 101 |
| Structured FAN references | 13 |
| Inventoried retained documents | 99 |
| Validation | 339 entities; zero errors or warnings at the last check (2026-09-01) |
| Automated tests | 70 passing at the last check |

The catalogued sources span the Armond/Paz, Muniz Bittencourt/Azevedo,
Engracio/Souza/Guimarães, Bohrer and Portuguese-origin lines, include the maternal
Toledo probate cluster and the Barbacena context sources, and include the living
subject's private records. Details are canonical in `data/sources/`; gaps in
`data/record-coverage.yaml`.

## Research snapshot

| Area | Strongest current position | Strategic gap |
| --- | --- | --- |
| Armond and Paz | Aristão's 1957 death confirmed; Liliosa Paz Armond independently named (GOV-0001) as José Olavo's mother; Eliza Balbina de Toledo's (P-0017) parentage CONFIRMED = daughter of José Cezário de Toledo Lima × Claudina (F-0026, PRB-0006). Toledo line reaches Portugal (Ruivães 1716, PAR-0036) and the Vila Rica couple Gaspar Ferreira × Gertrudes Maria de Toledo (F-0045, PAR-0018). The 2026-08-13/14 PRB-0006 + PRB-0009 re-reads corrected several misreads and confirmed P-0016 (Armond) is distinct from all three Toledo "Simplícios". | **Simplício José Ferreira Armond's (P-0016) own parents remain UNKNOWN — well-bounded (see Next steps §1):** ruled out as the childless elder Simplício and as any Toledo; leading unproven hypothesis = the Barbacena/Azorean Ferreira Armonde trunk (Honório's 1845 six adult heirs). Three decisive records — the Simplício × Eliza marriage (C-004), his ~1853 baptism, and the Barbacena _principal_ autos / Pitanguy inventário (C-006) — all need physical/authorised retrieval. Aristão's baptism and his marriage to Liliosa, and Liliosa's own 1946 Eugenópolis óbito, still to retrieve. |
| Muniz Bittencourt and Azevedo | Deocleciano's own 1892 baptism (PAR-0004) and Susanna's 1866 baptism (PAR-0005) are catalogued; João's 1915 death (PAR-0007) confirms São Miguel origin; parents primary-confirmed by PAR-0015 (father Manoel Muniz Bytancourt P-0042, mother Francisca Roza P-0047) and grandparents (F-0023). João's own baptism found: PAR-0022, b. 24 Oct 1845. **Line extended +1 generation (2026-08-11, BPARPD reconcile + Culturacores images):** Manoel × Francisca's true marriage is PAR-0024 folio 32r, **17 Feb 1842** (the earlier "1 Feb 1845 folio 73r" was a namesake mis-ID, corrected); it names Francisca's parents Manoel de Motta × Anna de Souza (P-0086/P-0087, F-0042). The grandparents' 1819 marriage PAR-0037 (E-0074) names P-0048's parents Manoel Muniz Bitancourt elder × Tereza do Amaral (F-0040) and P-0049's parents João de Medeiros Brandão × Maria Eugenia (F-0041). Luiza's parents (F-0018) and Carangola origin fixed | The completed João × Susanna ceremony entry; the Azevedo grandparents' own vital records; the pre-1818 Mãe de Deus books (P-0082–P-0087 own records) are not digitised online |
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

1. Break Simplício (P-0016)'s parentage — the family's central gap (Next steps §1).
2. Retrieve Aristão's baptism, the Aristão × Liliosa marriage, and Liliosa's own records.
3. Locate Vicente's Portuguese locality; extend the Engracio/Souza, Guimarães and Azevedo lines
   one documented generation at a time; obtain the João–Susanna Sapucaia ceremony entry.

Canonical person-by-record actions and last-reviewed dates live in `data/record-coverage.yaml`.

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
  rule, and the GEDCOM full-backup exporter (7.0/5.5.1 + GEDZIP; `make export`), the multi-page evidence reader (all continuation pages ship to the deployed site — regression-tested via `tests/test_pages_site.py`), the symmetric ahnentafel pedigree with per-card expand/collapse and fit-floored zoom, and the advisory audits (`make drop-pages-audit`, `make ancestors-audit`, `make profiles-audit`).
Completed engineering work is recorded only in `CHANGELOG.md`.
