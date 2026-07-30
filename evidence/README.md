# Evidence files

This directory holds private document images and legally permitted derivatives.
Do not publish, upload or move these files outside the private repository.

Categories reflect the **origin (repository) of the record** — where the
document was created — not the event it documents. A civil-registry marriage,
birth and death therefore all live in `civil/`; the specific record type is
carried by the filename and by the source's `record_category`, not by a separate
folder. Create a category directory only when its first document is added:

| Folder | Origin of the record | Typical `record_category` |
| --- | --- | --- |
| `civil/` | civil registry office (cartório de registro civil) | `civil_registration` |
| `parish/` | church / parish register | `parish_register` |
| `government/` | state agency (e.g. driver index) | `government_record`, `official_index` |
| `probate/` | probate / succession court — autos de inventário, juízo de órfãos | `court_or_probate` |
| `newspapers/` | newspaper / periodical | `newspaper` |
| `publications/` | published works | `published_genealogy` |
| `immigration/` | immigration / passenger records | `immigration` |
| `naturalisation/` | naturalisation records | `naturalisation` |

`references/` is **not** an origin category. It holds FAN/context images —
records where our people appear only in a functional role (witness, appraiser,
creditor, attorney, party, co-owner). Each image is catalogued as a FAN entity
(`data/fan/FAN-NNNN.yaml`, `usage: context`) with a transcription and a person
link, named `FAN-NNNN-…` and kept flat (no per-set subfolders). FAN references
are context, never sources. See `references/README.md`.

## File handling

1. Obtain the highest-resolution file that the owner is authorised to access.
   Prefer the service's original-file download. If that is unavailable, export
   the complete highest zoom level without upscaling, cropping or enhancement.
2. Never use a browser screenshot, preview, thumbnail or OCR rendering as the
   preservation file. If no qualifying image is accessible, record the item as
   inaccessible instead of saving a lower-resolution substitute.
3. Preserve downloaded bytes unchanged. Put redactions, rotations, details and
   other transformations in separately named derivative files.
4. Review the image for living-person data before adding it.
5. Remove unnecessary identity numbers, addresses, signatures and financial
   information from public derivatives; retain an unredacted copy only when
   essential to the private research purpose.
6. Allocate the source ID before naming the file. Its prefix is the source's
   category (`CIV`, `GOV`, `PAR`, `PRB`, `NWS`, `PUB`, `REC`), matching this
   folder and the `data/sources/<category>/` record.
7. Use
   `<PFX>-NNNN-record-type-primary-person-event-year.ext`, using lowercase
   ASCII for the descriptive portion while preserving the person's recorded
   name inside the source record.
8. Record the acquisition method, resolution status, pixel dimensions and
   SHA-256 checksum in `data/document-inventory.yaml`.
9. Keep derivatives explicit, for example `-redacted` or `-detail-01`.

Screenshots are working copies, not proof of the assertions they display.
Catalogue their origin and pursue the underlying record image.

`original-file` in preservation metadata means the exact file supplied by an
authorised download or contributor. It does not mean that the genealogical
record itself is original: a modern certificate can remain a derivative source
even when its uploaded JPEG is preserved byte-for-byte.
