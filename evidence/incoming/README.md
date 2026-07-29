# evidence/incoming — staging area

Un-catalogued record images land here (e.g. downloads driven by
`research/familysearch-image-targets.md`). Files here are NOT yet evidence:
they have no reserved `SRC-xxxx` ID, no inventory entry and no checksum.

Cataloguing step (human/assistant): privacy-review the file, reserve a source ID
with `scripts/new_entity.py`, move it to the correct `evidence/<category>/`
folder under its `SRC-xxxx-...` name, add its `document-inventory.yaml` entry with
checksum, and create/point the `data/sources/SRC-xxxx.yaml` record. Then remove
the staged copy.
