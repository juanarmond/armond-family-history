# FamilySearch image-retrieval — agent task spec

AGENT ROLE: You are an autonomous research agent operating the repository owner's
already-signed-in FamilySearch browser session. Work the TASKS below top to
bottom (by `priority`). For each: open the URL, browse the given image range,
find the target record, DOWNLOAD the full-resolution image with FamilySearch's
authorised Download button, save it, and append a RESULTS entry. Then stop and
let a human catalogue it.

## Execution contract (read once)

- SAVE downloads to `evidence/incoming/` (create the folder if missing).
  Filename: `<task_id>__img<NNNN>.jpg` (e.g. `aristao-baptism__img0071.jpg`).
  If FamilySearch supplies a PDF, keep `.pdf`.
- REPORT: after each task, append one block to `## RESULTS` (append-only; never
  edit earlier entries) using the RESULT TEMPLATE at the bottom. Include the exact
  `ark:` URL of the page, the saved filename, and a short transcription of the key
  fields you can read (names, dates, parents, places). Mark uncertain readings
  with `[?]`.
- STATUS values: `found` (downloaded) / `restricted` (page blocked even while
  logged in — a FamilySearch affiliate library is required; note the image number
  and move on) / `not_found` (searched the whole range, absent) / `partial`.
- DO NOT edit any other repository file. DO NOT invent `SRC-xxxx` IDs — a human
  reserves those during cataloguing.
- TRANSCRIBE what is visible; do not infer. Preserve Portuguese spelling and
  diacritics exactly. These records are handwritten Portuguese, mostly Latin
  church-Latin headers.
- ACCESS pattern: leading pages of a film are usually blocked and the body is
  open; individual interior pages can still be restricted. Owner-confirmed
  viewable ranges are in each task.

## Machine-readable task list

```yaml
collections:
  catholic_mg: "2177275"   # Brazil, Minas Gerais, Catholic Church Records
  civil_mg: "3479702"      # Brazil, Minas Gerais, Civil Registration 1879-1949
catalog_place_search: "https://www.familysearch.org/search/catalog"
affiliate_locator: "https://locations.familysearch.org/en/search"
save_dir: "evidence/incoming/"

tasks:
  - id: aristao-baptism
    priority: 1
    film: "004640627"
    url: "https://www.familysearch.org/en/search/film/004640627"
    image_range: "54-497"          # 1-53 restricted (owner-confirmed)
    sample_viewable: "https://www.familysearch.org/ark:/61903/3:1:939J-TWD5-6?i=50&lang=en&cc=2177275&groupId=2177275"
    looking_for: "Baptism of Aristão Ferreira Armond, ~1879 (window 1878-1888)."
    match:
      person: "Aristão Ferreira Armond"
      surname_variants: ["Ferreira Armond", "Armond", "Amaral", "Armande"]
      event: baptism
      date_approx: "1879 (accept 1878-1881)"
      father: "Simplício Ferreira Armond"
      mother: "Elisa Balbina Toledo (also Elizia/Eliza; Tolledo)"
      parish: "Nossa Senhora da Piedade, Piacatuba / Leopoldina, MG"

  - id: armond-siblings
    priority: 3
    film: "004640627 and 004640632"
    url: "https://www.familysearch.org/en/search/film/004640632?i=0"
    image_range: "004640632 from image 6 (1-5 restricted); 004640627 from 54"
    looking_for: "Any baptism whose parents are Simplício Ferreira Armond + Elisa Balbina Toledo, ~1868-1888."
    calibration_record:
      person: "Marfisa Ferreira Armond"
      event: baptism
      date: "15 Feb 1873"
      parish: "Nossa Senhora da Piedade, Piacatuba"
      note: "Known to exist; use to confirm the parish/handwriting, then collect the full sibling set."

  - id: aristao-liliosa-marriage
    priority: 2
    film: "004640632 (item 2, marriages 1898-1920)"
    url: "https://www.familysearch.org/en/search/film/004640632?i=0"
    image_range: "from image 6; marriages section (item 2)"
    looking_for: "Marriage of Aristão Ferreira Armond to Liliosa Paz. HIGHEST VALUE: the act should name Liliosa's parents and birthplace."
    match:
      groom: "Aristão Ferreira Armond"
      bride: "Liliosa Paz (maiden surname unknown - capture it)"
      capture: "bride's parents, bride's naturalidade/birthplace, marriage date and parish"
    fallback: "If not in 1898-1920, they may have married earlier; report not_found and request earlier Leopoldina/Piacatuba marriage films."

  - id: aristao-father-bridge
    priority: 5
    film: null
    action: "Build the link between Aristão's father and the Barbacena Armonde family from primary records (do not assume it). Catalog place-search 'Brazil, Minas Gerais, Leopoldina', 'Além Paraíba' and 'Barbacena' (Catholic collection 2177275); also try projetocompartilhar.org."
    looking_for: "(a) DECISIVE: marriage of Simplício José Ferreira Armond x Elisa Balbina (Toledo/Tolledo), ~1855-1872 — names BOTH spouses' parents. (b) The FULL baptismal act of Marfiza (Piacatuba, 15 Feb 1873), which may name grandparents. (c) Baptism of that Simplício, only after his parents surface."
    named_targets:
      - "Piacatuba/Leopoldina marriage books ~1855-1872; then the Além Paraíba matriz (strongest untested — absent from the cantoni.pro.br transcriptions)"
      - "Livro de Batismos, Freguesia de N. Sra. da Piedade de Barbacena, 1828-1872 (only if a Barbacena origin surfaces)"
    anti_merge: "Do NOT identify Aristão's father with the 1st-generation Simplício José Ferreira Armonde, b.1784, who died UNMARRIED (doubly documented: Lacerda 1845 inventory/1831 census, and the Mauro Senra blog). Simplício José is a recurring family name; the Piacatuba Simplício is a later namesake."

  - id: sapucaia-marriage
    priority: 4
    film: null
    action: "Catalog place-search 'Brazil, Rio de Janeiro, Sapucaia' -> Santo Antônio parish -> casamentos 1882-1883. Confirm or reject candidate catalog 145484 ('Registros paroquiais 1880-1971'). Also browse DGS 004626365 a few images around p.191 — the habilitação/banhos may name filiation/naturalidade even if the assento is elsewhere."
    looking_for: "Marriage of João Monis (Muniz) Bittencourt x Susanna Rita Brandão, after the 23 Dec 1882 provision."
    match:
      groom: "João Monis Bittencourt (also Muniz; given name may read José)"
      bride: "Susanna Rita Brandão (also Susana; Brondão)"
      date_approx: "late 1882 to 1883"
    if_no_film: "FamilySearch may not hold Sapucaia's own casamentos (the provision was filmed from the Sé volume). The completed assento is most likely at the Paróquia Santo Antônio de Sapucaia, then the Cúria de Valença (NOT the Cúria do Rio, NOT Niterói); the fuller habilitação is at the Cúria do Rio (catedral.com.br/arquivo, paid form). Authorised human task."

  - id: vicente-carangola-marriage
    priority: 5
    film: null
    action: "Catalog place-search 'Brazil, Minas Gerais, Carangola' in collections 2177275 (Catholic) and 3479702 (Civil). Carangola's parish is Santa Luzia do Carangola (curato subsidiary of Tombos)."
    looking_for: "TWO origin records for Vicente José de Carvalho Guimarães (Portuguese): (a) his Santa Luzia marriage/habilitação (marriages filmed 1898-1924; if earlier, the mother parish TOMBOS); (b) his civil ÓBITO before 12 Oct 1915 (collection 3479702) — a Minas death states naturalidade, parents and widow."
    match:
      groom: "Vicente José de Carvalho Guimarães"
      bride: "Maria Tertuliana da Conceição"
      capture: "groom's Portuguese naturalidade (district/municipality/parish) and parents"
      place: "Santa Luzia do Carangola / Tombos, MG; before Oct 1915"

  - id: liliosa-1946-death
    priority: 6
    film: null
    action: "Civil death ~1946. PRIMARY = Barra Mansa (Volta Redonda was its district until 1954 and its own óbito registry likely opened only ~Nov 1946, so an April 1946 death sits in Barra Mansa). FamilySearch catalog 516378 — Barra Mansa death index 1889-1982 and books 1889-2005; also check a pre-Nov-1946 Volta Redonda death group."
    looking_for: "Death registration of Liliosa Paz Armond, ~1946 (leads: 16 April and 15 November 1946). Search the index under Armond and Paz and the given name Liliosa."
    match:
      person: "Liliosa Paz Armond"
      capture: "exact death date, age, stated parents, spouse (Aristão)"
    if_no_film: "Request an inteiro-teor óbito by name+year from Cartório Souza Reis, 1º distrito de Barra Mansa (registrocivil.org.br's free locator excludes RJ)."

  - id: iris-1929-birth
    priority: 7
    film: null
    action: "Iris Bohrer's 1929 civil birth. FamilySearch MG Civil Registration 1879-1949 (collection 3479702); catalog place-search under BOTH 'Alto Jequitibá' and 'Manhuaçu' - in 1929 'Presidente Soares' was only a district."
    looking_for: "Birth of Iris Bohrer, 27 Feb 1929, district of Presidente Soares (now Alto Jequitibá), MG."
    match:
      person: "Iris Bohrer"
      capture: "parents (João Gonçalves Bohrer, Selina/Celina Bohrer), exact place and date"
    disambiguate: "Use CIV-0004 (the 1949 marriage), which names her parents."
```

## Catalog references (FamilySearch Research Wiki, 2026-07-29)

Public catalog IDs + date ranges (film/DGS numbers are login-gated; open the
catalog to read them). Statewide browse: MG Civil `3479702`, MG Catholic
`2177275`, RJ Civil `1582573`, RJ Catholic `1719212`.

- Leopoldina parish (São Sebastião), covers Piacatuba district: catalog `345430`,
  1852-1924 — Aristão baptism (from ~1879), Aristão×Liliosa marriage, and the
  decisive Simplício×Elisa marriage.
- Barra Mansa civil: `516378`, 1889-2005 — Liliosa death (VR pre-1954 events too).
- Sapucaia civil: `385592` / `4135303` — João×Susanna civil marriage; no Sapucaia
  parish film on the wiki, so the church record falls back to RJ Catholic `1719212`.
- Barbacena parish (N. Sra. da Piedade): `21641`, 1730-1915 — bridge, only if a
  Barbacena origin surfaces.
- Carangola / Tombos: NO local catalog on the wiki — use MG full-text + statewide
  `3479702` / `2177275` and a bounded manual review (Vicente).

## Why each target matters (for the human cataloguer)

| task_id | Closes |
| --- | --- |
| aristao-baptism | Fuller names of Simplício & Elisa Balbina Toledo; Aristão's birth/origin |
| aristao-liliosa-marriage | Liliosa's parents, maiden surname and origin (open conflict) |
| sapucaia-marriage | Whether the João–Susanna ceremony followed the 1882 provision |
| vicente-carangola-marriage | Vicente's Portuguese district/parish (Portuguese-origin gap) |
| liliosa-1946-death | Liliosa's exact death date and parents |

## RESULT TEMPLATE (append one per task under RESULTS)

```
### <task_id> — <YYYY-MM-DD>
- status: found | restricted | not_found | partial
- ark_url: <exact page ark: URL>
- image_number: <NNNN>
- saved_file: evidence/incoming/<filename>
- transcription: <key fields read: names, dates, parents, place; use [?] for uncertain>
- notes: <anything the cataloguer needs>
```

## RESULTS

- 2026-07-29 (owner, manual): film 004640627 restricted images 1–53, viewable
  from ~54; film 004640632 restricted images 1–5, viewable from 6. Interior pages
  intermittently restricted in both. No records downloaded yet.
