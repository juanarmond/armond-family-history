# evidence/incoming — staging area

Un-catalogued record images land here before they become evidence (an
owner-supplied file, or a scan promoted from the `research/from-retrieval/`
drop). Files here are NOT yet evidence: they have no reserved ID, no inventory
entry and no checksum.

Cataloguing step (human/assistant): privacy-review the file, reserve a
category-prefixed source ID with `scripts/new_entity.py` (`CIV`, `GOV`, `PAR`,
`PRB`, `NWS`, `PUB`, `REC`), move the scan to `evidence/<category>/` under its
`<PFX>-NNNN-...` name, add its `data/document-inventory.yaml` entry with checksum,
and create the `data/sources/<category>/<PFX>-NNNN.yaml` record. Then remove the
staged copy.
