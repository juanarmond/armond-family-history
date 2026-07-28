# Evidence files

This directory holds private document images and legally permitted derivatives.
Do not publish, upload or move these files outside the private repository.

Create a category directory only when its first document is added:

- `civil/`
- `parish/`
- `immigration/`
- `naturalisation/`
- `newspapers/`
- `probate/`

## File handling

1. Review the image for living-person data before adding it.
2. Remove unnecessary identity numbers, addresses, signatures and financial
   information; retain an unredacted copy only when essential to the private
   research purpose.
3. Allocate the source ID before naming the file.
4. Use
   `SRC-NNNN-record-type-primary-person-event-year.ext`, using lowercase
   ASCII for the descriptive portion while preserving the person's recorded
   name inside the source record.
5. Calculate a SHA-256 checksum and record it in the source YAML.
6. Keep derivatives explicit, for example `-redacted` or `-detail-01`.

Screenshots are working copies, not proof of the assertions they display.
Catalogue their origin and pursue the underlying record image.
