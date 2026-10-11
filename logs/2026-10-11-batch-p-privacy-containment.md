# Batch P — privacy containment of the public repository

## Question

The repository is public. Which tracked material concerns living people or
records the owner restricts to private storage, and how is it removed from the
public repository, its committed GEDCOM and the public site without deleting any
evidence?

## Owner decision (2026-10-11)

The 2026-09-25 decision to keep the repository public stands, but it did not mean
that the owner's birth or marriage certificates, his spouse's records, other
living-person civil records or private transcriptions should be public. Those are
private. The six sources whose records say "authorised for this private repository
only" are not published on the site and are preserved privately, not deleted. The
full-backup GEDCOM is no longer tracked; it remains a local, private backup.
Evidence promotion and the final merge/release still need the owner's explicit
authorisation. Any history rewrite or other irreversible Git operation needs his
approval after he has seen its exact scope.

## Scope (verified 2026-10-11)

- **Held privately — living people's records:** CIV-0008 (the owner's birth
  certificate), CIV-0009–CIV-0012 (four marriage documents naming his spouse) and
  REC-0001 (the ancestor roster he supplied). The 19 other sources that mention a
  living person's ID are deceased people's records; the mention is the 2026-10-08
  privacy note, and they stay public under the owner's "the dead may be shown"
  directive.
- **Scans restricted to private storage:** CIV-0001–CIV-0005 and CIV-0013, whose
  own notes say to retain the images only in a private repository (signatures,
  registrar contact details, unrelated third-party entries, medical data).
- **Committed GEDCOM:** `export/armond-family-history.ged`, 116 historical versions.
- **Site leaks found while auditing:** records naming a living person published
  their date; three family notes published a living person's full name.

## Method

1. Branch `batch-p-privacy-containment`; nothing merged or pushed.
2. A one-off migration moved the 11 scans into the gitignored private store,
   verifying each SHA-256 before and after (two runs stopped on their own safety
   assertions; each time the partial state was restored from Git, every restored
   file was hash-checked against its private copy, and the run was repeated).
3. For the living people's records, the full originals went to
   `private/data/sources/` and the tracked files became citation stubs: no
   transcription, dates or places; scan path under `private/evidence/`;
   `withhold_from_site: true`. Their five inventory entries (DOC-0010–DOC-0014) keep
   public-safe fields only; the originals are in
   `private/data/document-inventory-private.yaml`. The scans of CIV-0008–CIV-0012 were
   renamed to drop personal names; the bytes are unchanged.
4. The six restricted records keep their tracked records, gain
   `withhold_from_site: true` and a dated note, and cite their scans in the
   private store.
5. Three session logs and one changelog entry had living people's identifiers,
   dates or the spouse's name; they are redacted, and the originals are kept
   under `private/`.
6. The validator, schemas, site build, knowledge base, GEDCOM export, tests and
   documents were updated (see `CHANGELOG.md`).

## Scans moved to the private store (SHA-256 unchanged)

| Source | Private path | SHA-256 |
| --- | --- | --- |
| CIV-0008 | `private/evidence/civil/CIV-0008-birth-original.pdf` | `10ea2916d9b5bf9f551261dad3b7a4025d5e569a5422838b0c3d48764bb69fb2` |
| CIV-0009 | `private/evidence/civil/CIV-0009-marriage-photostatic-original.pdf` | `2d8d570c217c63f09532260d88d426a16de7ddfdd59c5628d5edfaba12e6397a` |
| CIV-0010 | `private/evidence/civil/CIV-0010-marriage-transcription-original.pdf` | `a7315fb7e6ddc22b47cdc42abeeaecbeb60b1285fa1eea4053a394d917dd5011` |
| CIV-0011 | `private/evidence/civil/CIV-0011-marriage-certificate-original.pdf` | `aecc0d23f9b9e2aa1b5c26aea2bd118d8e3d94aed0691b4eca24795f02207148` |
| CIV-0012 | `private/evidence/civil/CIV-0012-marriage-summary-extract-original.pdf` | `88bc4698ede0fa53e822361381d9837a04ee1852dd4bd960bddb5ef3f68371bd` |
| CIV-0001 | `private/evidence/civil/CIV-0001-…-1916-original.jpg` | `d52385720d3cb0024df19cf650cb5bb79a1bd8af02947fcf7eaa80cae52d6249` |
| CIV-0002 | `private/evidence/civil/CIV-0002-…-1952-original.jpg` | `0def5d0019ea5167146f2f6528714b1e952837b78af5f51536aaa47cbcd01edc` |
| CIV-0003 | `private/evidence/civil/CIV-0003-…-1991-original.jpg` | `c4188e3a81f1547a7db4b178246e4154505798188b6aef05300321d41acdee8d` |
| CIV-0004 | `private/evidence/civil/CIV-0004-…-1949-original.jpg` | `32719dcd87a06322013b0760a5a0745ad713f86876a6fd05d7dd8516420f631e` |
| CIV-0005 | `private/evidence/civil/CIV-0005-…-1957-original.jpg` | `1ab59e308d28c2a069918b17864542d615e491182fc50950453f137fd3746b8b` |
| CIV-0013 | `private/evidence/civil/CIV-0013-…-1962-original.jpg` | `eaf6f82ef061e6661fbb64825bbc1fd9617c78cfdc2db587812b423d2e2e05e4` |

## Verification

- `make check`: 559 entities, 0 errors, 0 warnings; all tests pass. With the
  private store absent, as in CI, validation is also clean, because absent
  private-store files are skipped.
- `make privacy-audit`: none of the private strings in any tracked file or in
  the built site.
- The built site holds no living person's name and no private-store path, and
  does not contain the private store.

## Not done — needs the owner

- Git history still holds the earlier copies: raw blobs of all 11 scans, the 116
  GEDCOM versions, and the earlier versions of the six living people's records
  and the inventory. The cleanup is prepared, not performed.
- The private store is now the only copy of these originals outside Git history,
  and it has no backup yet.

## Re-audit against the owner's authoritative classification (2026-10-11, later)

**Owner clarification.**

- Exactly three people in the tree are living: the owner (P-0001) and his parents (P-0002, P-0003). Everyone else in
  the tree is deceased.
- Never infer that someone is living from a missing death date, a recent record, a `private: true` field, an old
  privacy tag, or a record's past in a private-repository workflow.
- The spouse is outside the tree; incidental personal information about her in the owner's records is private.
- A source restriction is not a living-person classification.
- Deceased-person genealogy is public unless a specific source restriction applies.
- Existing `private` classifications are not removed mechanically.
- Git/GitHub is the backup mechanism; the public repository can never hold the private backup. A separate private
  repository is proposed and needs the owner's approval before it is created.
- History rewriting remains separately owner-gated.

**Findings.**

- Classification: 3 living, 135 deceased. No deceased person's name equals or contains a living person's name, so
  the site scrubber redacts no deceased person. Only F-0011 (the parents' family) loses its notes on the site.
- Batch P had applied "held privately" to every record linked to a living person, which also removed the
  **roster REC-0001**. Apart from the three, the roster is deceased-person genealogy. Its transcription is
  restored, with only the owner's own birthplace and year withheld.
- REC-0001's own bracket note withholds positions 6–7 and 12–15 as "living or near-living". This predates Batch
  P and rests on the superseded assumption. Those people are deceased, and their names are in their person
  entities. No original wording exists to restore, so a note records the correction.
- **CIV-0003** (a deceased grandparent's death record) names the owner's father as declarant. His ID number and
  street were already withheld, and his name stays. His nationality, age, profession and residence are now
  withheld too, and the original is kept privately.
- The **published family story** named the owner's parents by their given names. It now refers to them only by
  relationship.
- No deceased person's information was removed by the log redactions: they touched only identifiers of the
  owner's own documents.
- No `private` classification was changed. The flag does not gate publication; it is kept as found.
- Inventory tags `living-person-data` on three deceased people's records are stale. They must not be read as
  "living"; they are left unchanged.
- A test fixture used the owner's real name; it now uses a synthetic one.

**Mechanism change.** An explicit `held_privately: true` marker now drives the citation-stub rule; it is set on
CIV-0008–CIV-0012. A record that merely names a living person stays in the repository, with that person's sensitive
details withheld, and its scan stays in the private store. Where the private store is present, a missing
private-store file is now an error. The pre-commit hook runs the privacy audit on every commit.

**Verified (2026-10-11).** All five of the owner's PDFs (CIV-0008–CIV-0012) are still downloadable from the public
repository's Git LFS store without signing in. Merging Batch P does not change that; only an LFS purge does
(GitHub Support, or deleting the repository).
