---
date: "2026-07-28"
researcher: Codex
research_question: Was material research context lost when the original ChatGPT conversation was transferred to this repository?
related_people: []
related_families: []
---

# Original ChatGPT conversation transfer audit

## Scope

This audit compares the current repository with the complete ChatGPT
conversation titled `Pesquisa genealógica profunda`, conversation ID
`6a67aee6-f6d0-83eb-b4b8-26e9b19abc72`.

The conversation is a lead and provenance record, not a genealogical source.
It contains family statements, assistant interpretations, web-search summaries,
opaque citation tokens and summaries of images that are not available in this
checkout.

The transcript refers to 24 attached images across ten messages. The imported
conversation does not expose the image contents, original filenames, checksums
or attachment metadata. No statement attributed to an image can become a
structured source record until the image is recovered and reviewed.

## Overall result

The current repository preserves the corrected direct-ancestor structure, the
main date and name conflicts and the highest-priority research questions. This
audit found and corrected one policy inconsistency: Aristão's proposed parents
had been labelled `strong-evidence` even though the stated support was limited
to collaborative trees and sibling groupings.

Material not previously preserved falls into three groups:

1. transcript-only collaborative-tree and web-search leads;
2. the sequence of incorrect or superseded interpretations; and
3. the missing attachment manifest and automation history.

Information about living descendants and collateral people of uncertain living
status was intentionally not copied. That is privacy minimisation, not research
loss.

No person or relationship is added or removed. The confidence assigned to
Aristão's proposed parents is downgraded from `strong-evidence` to `hypothesis`.

## Repository coverage

| Conversation area | Repository result | Assessment |
| --- | --- | --- |
| Subject, parents and four grandparents | Summarised in `STATUS.md` with source cataloguing pending | Preserved |
| Geraldo Paz Armond and Cidalia Engracio Guimarães | Corrected dates, places, marriage and unresolved birth-date conflict retained | Preserved |
| Aristão Ferreira Armond and Liliosa Paz Armond | Aristão's proposed parents are retained as a `hypothesis`; Liliosa's parents remain unknown | Corrected to match evidence policy |
| Engracio and Guimarães direct lines | Direct ancestors and the Portuguese-origin question are retained | Preserved |
| Muniz Bittencourt and Azevedo direct lines | The 1916 marriage, parents and unproved island-origin claim are retained | Preserved |
| Bohrer direct lines | Parent readings and the Francisco José Bohrer/Rosa Eugênia de Lemos hypothesis are retained with uncertainty | Preserved |
| Named collateral groups | Only a general warning is retained | Intentionally minimised pending evidence and privacy review |
| Source-level facts such as witnesses, addresses, causes of death and sibling lists | Not converted into tree facts | Correctly deferred until images are catalogued |
| Original documents and screenshots | Absent | Material provenance gap |
| Web-search paths and cited URLs | Opaque turn citations only; no reproducible URLs or profile identifiers | Material reproducibility gap |
| Daily research task | Narrative status only; no task identifier, prompt, schedule or reproducible run log | Operational history gap |

## Architecture and output proposals

The conversation proposed manual person and family pages, many empty topical
folders, a knowledge graph or Neo4j/RDF layer, GEDCOM, timelines, maps, a
website and an illustrated family-history book.

These ideas were not lost, but most were deliberately deferred:

- structured YAML is the canonical data layer because it is simpler to review,
  validate and migrate than a graph database at the present scale;
- person pages, family narratives and timelines should be generated from YAML
  after real records establish schema stability;
- GEDCOM and privacy-filtered exports remain in the engineering backlog;
- regional research folders should appear only with their first substantive
  reproducible search; and
- a website, maps and book are publication outputs, not evidence infrastructure,
  and should follow source ingestion rather than drive it.

The repository's current smaller architecture is therefore a considered
replacement for the early speculative folder trees, not an accidental omission.

## Correction ledger

The conversation repeatedly revised earlier readings. The latest answer is not
automatically more reliable; each item still requires its original record.

| Topic | Earlier conversation claim | Later position retained by the repository |
| --- | --- | --- |
| Geraldo's parents | Luiz do Carmo Armond and Petrosa Paz Armond | Aristão Ferreira Armond and Liliosa Paz Armond |
| Geraldo's death | 18 July 1991 | 18 February 1991; original record still uncatalogued |
| Cidalia's birth | 15 September 1930 and 15 November 1930 both appeared | Conflict remains unresolved |
| Maria Aurora's given name | `Marta Aurora` appeared in an early reading | `Maria Aurora Guimarães`; source review pending |
| Luiza's surname | `Luiza Fernandes de Aguiar` appeared early | `Luiza Fernandes de Azevedo` |
| Antonio Engracio identities | Father, son and collateral grandson were repeatedly conflated | Direct line distinguishes Antonio Engracio Filho from his parents; collateral assertions remain unstructured |
| Liliosa's parents | Simplício Ferreira Armond and Eliza/Elizia Toledo were temporarily assigned to Liliosa | Liliosa's parents remain unknown; the couple is only proposed for Aristão |
| Aristão's parents | At different points described as unknown, probable and corrected from Liliosa | `hypothesis`, pending independent record evidence |
| Antenor's name | `Antenor Muniz Bittencourt` was presented as his birth/family name | Official identity form `Antenor Muniz` is retained, with the fuller form as a lead |
| João Muniz Bittencourt's origin | São Miguel, Azores was presented as probable | Island origin remains an unproved hypothesis |
| João Gonçalves Bohrer's mother | `Carolina` and `Carolissa` both appeared | Parental transcription remains provisional |
| Historical Ferreira Armond connection | A path to the eighteenth-century Barbacena family was suggested | No connection is accepted without every intermediate generation |

## Transcript-only leads requiring recovery or a new search

These details are preserved here only so they are not forgotten. They are not
structured conclusions and must not be cited as evidence.

### Armond and Paz

- A proposed sibling cluster for Aristão includes Aristides, Marfizia Augusta,
  Julia, Aurora, Rosalina, Simplicio Ferreira Armond Filho and Tereza Ferreira
  Armond. Dates in the transcript came from collaborative profiles or a
  screenshot and require identity-by-identity verification.
- A possible baptism lead names Marfisa Ferreira Armond, dated 15 February
  1873 in Piacatuba, Leopoldina, with parents rendered as Simplicio Ferreira
  Armond and Elisa Balbina Tolledo. The Marfisa/Marfizia identity and citation
  were never resolved.
- The older Ferreira Armond family of Barbacena is a separate research lead.
  Homonymous people named Simplício must not be merged across generations.

### Muniz Bittencourt and Azevedo

- Collaborative profiles proposed a marriage of João Muniz Bittencourt and
  Suzana Ritta Brandão on 23 December 1882 at a truncated locality beginning
  `Centro...`.
- The same profiles proposed João's birth about 1864 on São Miguel and
  conflicting parents involving Manoel Muniz Bittencourt, Francisca Roza,
  Manoel Muniz Bittencourt Junior and Anna Maria Bittencourt. The chronology
  was internally inconsistent.
- A collaborative profile proposed Luiza's exact birth as 16 August 1898,
  a locality rendered as Alegre/Comercinho, and the variant `Luiza Secundina de
  Azevedo`. The 1916 marriage record summary supports only the more conservative
  facts retained in `STATUS.md`.

### Bohrer

- Collaborative profiles proposed Joaquim José Bohrer born about 1859,
  Lucinda Ferreira da Silva born about 1863 and died in 1921, and a possible
  child Francisco José Bohrer born in 1885.
- Francisco José Bohrer and Rosa Eugênia de Lemos were proposed as Joaquim's
  parents. This remains a tree-derived hypothesis.
- `Presidente Soares` appeared as a possible birthplace for Iris Bohrer, but
  the underlying image is unavailable.
- Claims that the Bohrer line passed through Portuguese islands or can be
  inferred as German from the surname are unsupported and are not active
  conclusions.

### Guimarães and Engracio

- A multi-person civil registration was described as listing children of
  Francisco José de Carvalho Guimarães and Emmerenciana Maria de Jesus,
  associating the family with Fazenda Barroso and São Francisco do Glória.
  Names, dates, naturalities and the exact registration must be retranscribed
  from the image.
- A 1871 naturalisation screenshot was mentioned without a visible subject or
  a demonstrable link to any ancestor. It remains unassigned.

### Collateral relatives

Several sibling and descendant groups were named in screenshots or public
trees. They are not reproduced here because some may be living and none has a
catalogued source. Recover the relevant images, perform privacy review and then
add only people required by verified evidence.

## Missing attachment candidates

The assistant summaries suggest that the unavailable attachments may include:

- family-tree application screenshots;
- a birth registration for Cidalia;
- a death registration and marriage material for Geraldo;
- marriage and identity records for Antenor and Iris;
- the 1916 marriage of Deocleciano and Luiza;
- a death registration for Liliosa;
- death registrations for João Gonçalves Bohrer and Selina Bohrer;
- a collective Guimarães civil registration;
- death registrations for Maria Aurora Guimarães and Antonio Engracio Filho;
  and
- an unidentified 1871 naturalisation screenshot.

This is not an inventory of documents. It is an inventory of descriptions in a
conversation. The number of descriptions does not necessarily equal the number
of distinct records or files.

## Attachment recovery procedure

1. Export or download the original attachments from the ChatGPT conversation.
2. Do not copy conversational text containing living-person details into
   evidence filenames or public metadata.
3. Retain original filenames and available creation/export metadata.
4. Add each file to `data/document-inventory.yaml` only after privacy
   review.
5. Calculate checksums and identify duplicate, cropped or derivative images.
6. Match each image to the candidate list above without assuming the
   assistant's transcription is correct.
7. Catalogue the first three clearest original records, review the model and
   then process the remainder.

## Automation history

The conversation states that a daily task called `Pesquisa genealógica
profunda` was created, ran once on 27 July 2026, produced no material confirmed
finding and had notifications disabled.

That statement is not a reproducible negative search:

- no task identifier or full prompt is present;
- no queries, repositories, collections, date ranges or URLs are recorded;
- no run output is preserved; and
- no matching Codex scheduled task exists in the local automation registry.

The legacy task may still exist separately in ChatGPT, but its current status
cannot be verified from this repository. It should be paused before any
replacement is activated to avoid duplicated research.

## Conclusion

The transfer retained the central family structure but not all research leads
or provenance. This audit preserves the missing leads at hypothesis level,
records the correction chain and aligns Aristão's proposed parentage with the
collaborative-tree evidence rule without creating source or person entities.

The highest-value next action is unchanged: recover the original attachments,
privacy-review them and catalogue the first three clearest records. Repeating
broad internet searches before recovering those records is lower value and
risks duplicating earlier, undocumented searches.
