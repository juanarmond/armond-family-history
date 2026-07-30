# 2026-07-30 — Engracio line: two civil deaths ingested from the retrieval drop

## Question

The `research/from-retrieval/` drop (FINDINGS.md §6–7) reported new targeted
record images (`rec-*.jpg`, 30 July) beyond the earlier full-text sweep. Which
are genuinely new, valuable, direct-line records, and what do they establish?

## Method

Per-image value gate on the `rec-*.jpg` set. Cross-checked each against the
already-catalogued sources and the direct roster; read the two highest-value
direct-line images in full; classified the rest (duplicate / line-extension /
privacy-excluded). Promoted only the read-and-verified direct-line records.

## Read and promoted (2 sources, direct line)

- **CIV-0017 — Antonio Engracio Filho (P-0010), civil death, 21 June 1964**
  (óbito nº 37.787, fl. 122; Rio de Janeiro region, residence Pavuna, burial São
  João de Meriti). Aged 69 (born c.1895, Minas Gerais), *negociante*, married to
  Maria Aurora Guimarães. Names his parents **Antonio Engracio de Souza** and
  **Luzia Pinheiro da Conceição**, both deceased; six surviving adult children.
  - Created his death event (E-0023, confirmed) and an approximate birth event
    (E-0024, c.1895 MG, strong-evidence) — P-0010 previously had zero events.
  - Modelled his parents as new direct ancestors **P-0032** (Antonio Engracio de
    Souza) and **P-0033** (Luzia Pinheiro da Conceição), family **F-0015**
    (strong-evidence, informant-reported at death). Their own records are
    off-index.
- **CIV-0018 — Maria Aurora Guimarães (P-0011), civil death, 15 Sep 1991**
  (óbito nº 63.792, Livro 386-C, fl. 103, 5ª Circunscrição, Rio de Janeiro).
  Aged 87 (born c.1904, matching E-0007), widow of Antonio Engracio Filho. Names
  her parents **Francisco José de Carvalho Guimarães + Emerenciana Maria de
  Jesus** — identical to CIV-0007.
  - Created her death event (E-0025, confirmed); added CIV-0018 as a second
    source on F-0008's parent link (corroboration, still strong-evidence).

## Conclusions

- **Material conflict 10 RESOLVED:** the 1904 "Maria Amora" (CIV-0007) and the
  1991 "Maria Aurora" (CIV-0018) are provably the same woman — both records name
  the identical parents. Both forms preserved; preferred name kept as Maria
  Amora.
- **Marriage of P-0010 × P-0011 now attested** by two original civil deaths
  ("casado com" / "viúva de"); a partner_relationship was added to F-0012
  (strong-evidence). The marriage act itself (date/place) is still unlocated.
- Line extended one generation: Cidalia's paternal grandparents (P-0032, P-0033)
  are now modelled.

## Privacy

Both sources marked `private: true`; each names a possibly-living declarant
(withheld) and refers to surviving adult children (not named individually). No
living person is linked as an entity, so no living-person source-privacy rule is
engaged.

## Not promoted this pass (recorded in the triage ledger)

- **Duplicates of already-catalogued records:** `rec-armond-geraldo-paz-death-1991`
  (= CIV-0003), `rec-muniz-jose-susana-marriage-provision-1882` (= PAR-0001),
  and the three Bohrer records already catalogued (CIV-0014/0015/0016).
- **Bohrer maternal-line extension (pending, high value):** `rec-bohrer-alberto-birth`
  (1890), `rec-bohrer-francisco-jose-marriage-1879`, `rec-bohrer-joao-birth-1891`
  — sibling/parent records that would extend Celina's line up to her grandparents
  and great-grandparents. Not yet read per-image or promoted.
- **Privacy-excluded collaterals (recent deaths, likely-living relatives):**
  `rec-bohrer-joao-death-2001`, `rec-bohrer-maria-teixeira-death-2003`,
  `rec-bohrer-ercy-death`, `rec-muniz-rozalina-death-1983` — corroborate
  already-established couples; low marginal value, withheld.

## Result

`make check` green (58 tests; 124 entities; 0/0). Connectivity/completeness audit
clean (0 reciprocity problems). Viewer index rebuilt.
