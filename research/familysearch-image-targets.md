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

  - id: sapucaia-marriage
    priority: 4
    film: null
    action: "Catalog place-search 'Brazil, Rio de Janeiro, Sapucaia' -> Santo Antônio parish -> casamentos 1882-1883."
    looking_for: "Marriage of João Monis (Muniz) Bittencourt x Susanna Rita Brandão, after the 23 Dec 1882 provision."
    match:
      groom: "João Monis Bittencourt (also Muniz; given name may read José)"
      bride: "Susanna Rita Brandão (also Susana; Brondão)"
      date_approx: "late 1882 to 1883"
    if_no_film: "Book likely at Cúria do Rio (https://catedral.com.br/arquivo/, paid by form) or the parish; also check freguesias de Aparecida and São José do Vale do Rio Preto."

  - id: vicente-carangola-marriage
    priority: 5
    film: null
    action: "Catalog place-search 'Brazil, Minas Gerais, Carangola' and 'São Francisco do Glória' in collections 2177275 (Catholic) and 3479702 (Civil)."
    looking_for: "Brazilian marriage/habilitação of Vicente José de Carvalho Guimarães (he was Portuguese - the record should state his naturalidade = Portuguese parish)."
    match:
      groom: "Vicente José de Carvalho Guimarães"
      bride: "Maria Tertuliana da Conceição"
      capture: "groom's Portuguese naturalidade (district/municipality/parish) and parents"
      place: "Carangola region / Vila do Rio Claro, MG; before 1915"

  - id: liliosa-1946-death
    priority: 6
    film: null
    action: "Civil death ~1946. Volta Redonda was a district of Barra Mansa in 1946. Try registrocivil.org.br locator, then FamilySearch 'Brazil, Rio de Janeiro, Civil Registration' catalog for Barra Mansa/Volta Redonda."
    looking_for: "Death registration of Liliosa Paz Armond, ~1946 (a lead points to 16 April 1946), Volta Redonda RJ."
    match:
      person: "Liliosa Paz Armond"
      capture: "exact death date, age, stated parents, spouse (Aristão)"
```

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
