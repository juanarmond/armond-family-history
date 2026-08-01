# 2026-08-01 — Muniz Azorean parents (Povoação) and Francisco José Bohrer's 1888 will

## Scope

Value-gated the newest `research/from-retrieval/` drop (FINDINGS re-synced
2026-08-01) and promoted the two genuinely-new **primary** findings it flagged,
each confirmed against the record image before promotion (FINDINGS, the CSVs and
the FS-tree data are leads, never evidence):

1. **Muniz Bittencourt line → two generations into the Açores.** João Muniz
   Bittencourt's (P-0019) father's own **1866 death** at Nossa Senhora Mãe de
   Deus, Povoação, Ilha de São Miguel.
2. **Bohrer line → the immigrant boundary named.** Francisco José Bohrer's
   (P-0034) own **1888 registered will**, Provedoria de Nova Friburgo.

## 1. Manoel Muniz Bytancourt's 1866 Povoação death (PAR-0015)

Read `rec-muniz-manoel-obito-1866-povoacao-saomiguel.jpg`, act **N.º 70** (right
column; adjacent N.º 67/69/71 "Manoel"/"Elizeu" entries are unrelated
namesakes). The act states: *"…falleceu… um individuo do sexo Masculino, de nome
**Manoel Muniz Bytancourt**, de idade de quarenta e seis annos, proprietario,
cazado com **Francisca Roza do Espirito Santo**, natural desta freguesia, e
morador na Lomba do Botão da mesma; filho legitimo de **João Muniz Bytancourt**,
proprietario, e de **Maria Jacintha de Medeiros**, d'occupação domestica,
naturaes desta freguesia; não fez testamento, e deixou **oito filhos**."*
He drowned at sea off the Garajau on 24 July 1866, without the sacraments.

This single primary record carries the whole two-generation extension:

- **Corrects the father's name.** João's 1915 Carangola óbito (PAR-0007) recorded
  "Manoel **Luiz** Bittencourt"; the true name is **Manoel MUNIZ Bytancourt**
  (P-0042). The erroneous form is preserved as a source variant.
- **Names João's mother** (previously the one open name in his parentage):
  **Francisca Roza do Espirito Santo** (P-0047), natural of the parish. Her link
  to João specifically is strong-evidence (indirect): João, b. c.1847, is taken
  to be one of the couple's "oito filhos".
- **Promotes the grandparents to primary:** **João Muniz Bytancourt** (P-0048) ⚭
  **Maria Jacintha de Medeiros** (P-0049), both *naturaes* of Povoação (family
  F-0023) — the line's furthest documented Açorean generation.

Non-catalogued corroboration held as a lead only (transcription, no image): the
two brothers' 1880 Ponta Delgada emigration passports (BPAR/Archeevo, GCPDL/P),
each "filho de João Moniz Bettencourt e Maria Jacinta".

**Filename/content mismatch flagged (not promoted).** The image slugged
`rec-muniz-jose-baptism-1847-povoacao-saomiguel.jpg` does **not** show José
Muniz's baptism — its two entries are a foundling "Ignez" and "Maria" (dau. of
Antonio d'Amaral e Maria Flora, b. 19 Mar 1847). Only the testemunha signature
(João Jacintho Botelho de Bulhões) is in frame. The José baptism must be re-pulled;
Manoel's death alone carries the parentage, so nothing is lost for the direct line.

## 2. Francisco José Bohrer's 1888 will (PRB-0005)

Read `rec-bohrer-francisco-jose-testamento-1888-RJ-p1/-p2.jpg` — a certified copy
by the escrivão João José Kramith from the Livro de Registro de Testamentos nº 9,
fl. 8v, Provedoria de Nova Friburgo (FamilySearch DGS 105875530; FS mis-attaches
it to Rosa as a "1888 inventário"). The testator declares: *"…sou natural deste
termo, **filho legitimo de Jacob Bahrer e de Catharina Mayer**, já fallecidos…
casado… com **Roza Eugenia de Lemos Bohrer**, de cujo matrimonio tenho
actualmente quatro filhos que são **Joaquim, Laura, Guilherme e Fernando**…"* P2
names his executors — his wife, his cunhado **Candido Pereira de Lemos** (Rosa's
brother) and his friend Samuel Antonio dos Santos.

- **Parents named** (Bohrer immigrant boundary): **Jacob Bahrer** (P-0050) ⚭
  **Catharina Mayer** (P-0051), family F-0024, both deceased by 1888.
- **Resolves "immigrant vs Brazilian-born":** Francisco José was **"natural deste
  termo"** — Brazilian-born at Nova Friburgo. His nationality is now Brazilian and
  the immigrant generation is his parents. The secondary Swiss-Soleure reading
  (Jacob Borer of Erschwil ⚭ Catharina Moser of Hägendorf) and the mother's
  "Moser" surname are recorded only as variants/leads; the primary "Bahrer/Mayer"
  spellings are not overwritten.
- **Corroborates the children of F-0016:** Joaquim (P-0030) is now confirmed by
  his father's own will (was strong-evidence via a grandchild's 1890 birth);
  Laura and Fernando added as documented_children; the existing Guilherme Samuel
  Bohrer entry now also cites the will.

## Entities

- **Sources:** PAR-0015 (parish, Manoel 1866 Povoação death); PRB-0005 (probate,
  Francisco José's 1888 will, 2 page images).
- **People:** P-0047 Francisca Roza do Espirito Santo; P-0048 João Muniz
  Bytancourt; P-0049 Maria Jacintha de Medeiros; P-0050 Jacob Bahrer; P-0051
  Catharina Mayer.
- **Families:** F-0023 (Muniz grandparents ⚭, child P-0042); F-0024 (Bohrer
  parents ⚭, child P-0034).
- **Events:** E-0047 (Manoel death, 24 Jul 1866); E-0048 (Manoel approx. birth,
  ~1820).
- **Updated:** P-0042 (name corrected to Manoel Muniz Bytancourt, nationality
  Portuguese, death/birth events, spouse + parents); F-0020 (Francisca added as
  spouse, João's maternal link); P-0019 (parents note); P-0034 (parents,
  nationality Brazilian, Nova Friburgo birth); F-0016 (will corroboration,
  documented_children Laura/Fernando/Guilherme, Candido lead); coverage P-0019;
  STATUS conflict 6 + the Muniz/Bohrer research-snapshot rows.

## Verification

`uv run --frozen make check` green (69 tests). Viewer index rebuilt (193
entities). Reciprocity audit: 0 errors. Viewer projection confirms both couples
now trace as degree-6 direct ancestors of P-0001 (Azorean grandparents via João;
Bohrer immigrant couple via Francisco José). GEDCOM full backup regenerated.

## Remaining in the drop (not this pass)

The drop holds 165 images; the bulk of the 121 semantically-named `rec-*` files
are re-syncs of already-catalogued Sapucaia/Carangola records, the collateral
Muniz Bittencourt clan (FAN/context), or privacy-excluded 20th-century
living-adjacent records (RGs, recent deaths, portraits). The Lemos Itaboraí
baptisms belong to the *weakened/negative* Manoel-de-Lemos-Pereira strand (Rosa's
parentage is now to be pursued via her brother Candido Pereira de Lemos, named in
the will). These await a separate FAN/collateral triage pass.

## 3. Rosa Eugenia de Lemos's Lemos parents (PAR-0016) — addendum, same drop

A second read of FINDINGS surfaced a third direct-line primary record I had
under-weighted. Read `rec-lemos-rosa-baptism-1835-itaborai.jpg` (Matriz de São
João Batista de Itaboraí, img 197, a torn "volume em mau estado"): *"...baptizou...
a innocente **Roza**, nascida a dez mezes, filha legitima de **Manoel de Lemos** e
**Maria Thereza de Jesus**, naturaes desta freguezia; Padrinho Manoel José da Silva
e Flor de Maria da Conceição."*

Promoted as PAR-0016, establishing Rosa Eugenia de Lemos's (P-0035) parents
**Manoel de Lemos Pereira** (P-0052) ⚭ **Maria Thereza de Jesus** (P-0053), family
F-0025, with baptism event E-0049. Both parents are *naturaes* of Itaboraí, so
Rosa's nationality is now Brazilian (Itaboraí-born).

- **Identity = strong-evidence, not direct.** The register gives only the forename
  "Roza"; a *second, unrelated* "Roza" (dau. of José Nunes × Luiza Maria da
  Conceição) sits on the same page. The tie to our Rosa rests on: she is the
  couple's only Roza across the browsed 1832-1838 Itaboraí baptisms; the parish
  matches her 1879 marriage venue (PAR-0002, "em casa do pai de José Antunes de
  Lemos"); and her brother **Candido Pereira de Lemos** is named in her husband's
  1888 will (PRB-0005) — added as a documented sibling on F-0025.
- **Resolves the earlier "weakened" doubt.** The apparent 1831→1841 childbearing
  gap was an indexing artifact; the 1832-1838 baptisms are unindexed (browse-only).
  Rosa's siblings (Manoel 1831, Maria 1832, Anna 1834, Thomaz 1836, Polidoro 1838,
  João/Maria 1841) were located in the same register (images held, not individually
  catalogued) — noted as a lead on F-0025.
- PAR-0002 checked: it does **not** name Rosa's parents, so the baptism is genuinely
  the establishing record (not a duplicate). The `rec-lemos-rosa-marriage-1879-RJ`
  image is the same record already catalogued as PAR-0002.

New entities: PAR-0016, P-0052, P-0053, F-0025, E-0049 (inventory DOC-0048).
make check green (69 tests, 198 entities); reciprocity clean; both parents trace
as degree-6 direct ancestors via Iris → Celina → Joaquim → Rosa.
