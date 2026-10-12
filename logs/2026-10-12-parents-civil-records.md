# The owner's parents' birth and marriage certificates (owner-supplied)

## Question

What do the four civil documents the owner supplied on 2026-10-12 prove? Which people do they belong to, and
which conclusions change?

## Documents and handling

The owner supplied three scans and one phone photograph of family-held originals and authorised their
attachment. They are the living parents' own civil documents, so, under the owner's privacy decision, each is
**held privately**. The scan, full record and transcription are in the private repository
(`private/`, pushed and verified from a fresh clone). The public repository keeps a citation stub with
`held_privately: true`. No birth or marriage event is modelled, because the dates and places concern living
people.

| ID | Record | Concerns |
| --- | --- | --- |
| CIV-0052 | civil birth certificate (photograph; old tape hides the father's line) | P-0002, P-0004, P-0005, P-0008–P-0011 |
| CIV-0053 | civil birth certificate | P-0003, P-0006, P-0007, P-0012–P-0015 |
| CIV-0054 | civil marriage certificate, issued on the day | P-0002, P-0003, P-0004–P-0007 |
| CIV-0055 | later certified copy of the same marriage register entry | P-0002, P-0003, P-0004–P-0007 |

Each file was copied byte for byte, and its SHA-256 was verified before and after the copy. The inventory holds
public-safe entries DOC-0131–DOC-0134; the full detail is in the private inventory.

## Conclusions

- **Confirmed (were strong-evidence):**
  - P-0002's parents, P-0004 and P-0005 (F-0002);
  - P-0003's parents, P-0006 and P-0007 (F-0004).
  Both marriage certificates name all four parents in full. The children's own birth registrations, declared
  by the fathers, name both of P-0003's parents and P-0002's mother legibly. On P-0002's certificate the
  father's line lies partly under old tape; the owner, who holds the original, reads it as Geraldo. The father
  link is confirmed on that basis, by owner decision. The links rested before on the grandchild's
  certificate (CIV-0008).
- **Confirmed (new):** the partnership of P-0002 and P-0003 (F-0011, now spouses), from their own marriage
  certificates.
- **Corroborated, unchanged:** the grandparent generation, named on each birth registration by the declaring
  father:
  - Geraldo's parents (F-0003) remain strong evidence;
  - Cidalia's parents (F-0012) remain confirmed;
  - Antenor's parents (F-0001) remain strong evidence;
  - Iris's parents (F-0005) remain strong evidence.
  The policy does not let an informant-reported statement confirm a conclusion on its own, so these keep their
  status and gain a citation.
- **Name forms recorded:**
  - "Luís Carlos Igracio Armond", "Lucinéa Aparecida Muniz" and "Lucinéa Aparecida Muniz Armond";
  - "Antonio [I]gracio" and "Maria A[ur]ora Igracia" (recorded with their uncertain letters);
  - the existing "Deocleciano Muniz" and "Selina Bohrer";
  - "Liliosa Pa[es?] Armond" on CIV-0052 is too uncertain to record as a variant.
- **Profiles:** the twelve deceased relatives each gain one cited entry (English and Portuguese) that names the
  record type only. No date, place, witness or profession of a living person is published.

## Verification

- `make check` passes.
- `make privacy-audit` covers tracked files and the built site. It now has 64 private strings, including the
  witnesses, the officials, an identity number on a stamp, the registration numbers and the living people's
  dates.
- The site publishes the four records as metadata only.
