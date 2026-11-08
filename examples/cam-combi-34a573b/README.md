# cam-combi: Mathlib bump to Lean v4.25.0

- Project: [YaelDillies/cam-combi](https://github.com/YaelDillies/cam-combi) (library
  `LeanCamCombi`, renamed `CamCombi` since), one of the projects Mathlib's downstream-reports
  service builds against new Mathlib.
- Commit: [34a573b](https://github.com/YaelDillies/cam-combi/commit/34a573b79a64c9521e9e85e5ea1e58e276e7cebc)
  "Bump mathlib" (16 November 2025), against its parent
  [da021ed](https://github.com/YaelDillies/cam-combi/commit/da021ed2e4ea40f691191260e1673f832ec0b6f2).
- What it upgraded: Lean v4.24.0 -> v4.25.0, and Mathlib with it.
- What it edited by hand, in four Lean files: two imports moved to Mathlib's new file names; in
  `lemma_4_2` (Lecture 4) the named hypotheses `(hA : IsApproximateSubgroup K A.toSet)` and
  `(hC₀ : ...)` became plain implications with `(A : Set (GL n ℂ))`; in `LYM_inequality`,
  `𝒜.toSet` became `(𝒜 : Set (Finset α))`; one step of a proof that still ends in `sorry`.

Reproduce (from the repository's root; needs Docker):

```sh
sh examples/cam-combi-34a573b/run.sh
```

or compare the exports kept here, without Lean:

```sh
bin/leandrift diff examples/cam-combi-34a573b/old.jsonl.gz examples/cam-combi-34a573b/new.jsonl.gz
```

## What the report found

[report.md](report.md) (and [report.json](report.json)): of 169 declarations (122 theorems,
39 definitions, 3 axioms, 2 abbreviations, 2 instances, 1 structure), 141 have the same statement
and 28 changed; none was removed, added, or newly depends on `sorry` or another axiom.

All 28 changed statements first differ in the same place: the coercion from `Finset` to `Set`.
Under the old Mathlib a statement about `(s : Set α)` for a finset `s` elaborated to
`Finset.toSet s`; under the new one, where finsets are a `SetLike` type and `Finset.toSet` is
deprecated (since 2025-10-22, in favour of `SetLike.coe`), it elaborates to `SetLike.coe s`
(26 statements), and membership `x ∈ s` inside a set-builder goes through
`SetLike.instMembership` instead of `Finset.instMembership` (2). The report groups them so:

| old | new | statements |
|---|---|---|
| `Finset.toSet.{u0}` | `SetLike.coe.{u0,u0}` | 23 |
| `Finset.toSet.{0}` | `SetLike.coe.{0,0}` | 3 |
| `Finset.instMembership.{u0}` | `SetLike.instMembership.{u0,u0}` | 2 |

Walking the 28 pairs of trees further shows no other kind of difference (two of them also use a
`Fintype` instance whose generated name changed with the coercion,
`instFintypeElemImageToSetOf...` to `instFintypeElemImageCoeFinsetOf...`). The two statements the
commit rewrote by hand, `lemma_4_2` and `LYM_inequality`, are among the 28 and differ only there:
naming the hypotheses or writing the coercion another way did not change them, and the upgrade
changed how all 28 elaborate. These are statements whose terms changed while their meaning most
likely did not; telling the two apart needs the definitional-equality check in the new
environment, which is not part of release 0.0.
