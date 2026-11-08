# PersistentDecomp: bump to Lean v4.32.0

- Project: [Paul-Lez/PersistentDecomp](https://github.com/Paul-Lez/PersistentDecomp) (library
  `PersistentDecomp`), one of the projects Mathlib's downstream-reports service builds against new
  Mathlib.
- Commit: [7cfd07c](https://github.com/Paul-Lez/PersistentDecomp/commit/7cfd07c5f5fdd9104af193fa7921335e2d02d3b6)
  "Bump to v4.32.0" (14 July 2026), against its parent
  [4e710a8](https://github.com/Paul-Lez/PersistentDecomp/commit/4e710a86969cef83b2735f36a66fa10a652c7acc).
- What it upgraded: Lean v4.31.0 -> v4.32.0, and Mathlib with it.
- What it edited by hand, in `PersistentDecomp/BumpFunctor.lean`: the definition
  `IntervalModuleMorphism` was renamed `intervalModuleMorphism`, and the two results about it
  renamed to match, `IntervalModuleMorphism_comp` (until then a `def`) becoming a `lemma`. No
  deprecation alias was left for the old names.

Reproduce (from the repository's root; needs Docker):

```sh
sh examples/persistentdecomp-7cfd07c/run.sh
```

or compare the exports kept here, without Lean:

```sh
bin/leandrift diff examples/persistentdecomp-7cfd07c/old.jsonl.gz examples/persistentdecomp-7cfd07c/new.jsonl.gz
```

## What the report found

[report.md](report.md) (and [report.json](report.json)): of 160 declarations (98 theorems,
31 definitions, 23 instances, 6 structures, 2 abbreviations), 151 have the same statement, 3 are
the same after renames, and 6 changed; none was removed, added, or newly depends on `sorry` or
another axiom.

The three renames had no deprecation alias. LeanDrift matched them by their statements:
`intervalModuleMorphism` has exactly the statement `IntervalModuleMorphism` had, and once that
rename is known, `intervalModuleMorphism_comp` and `intervalModuleMorphism_identity` match the old
results too. The report notes that `_comp` went from a definition to a theorem.

The 6 changed statements (`ExistsFittingn`, `PowEqCompLeft`, `PowEqCompRight`, `Step2_2`,
`Step3_1`, `Step3_2`, all in `EndoRingIsLocal.lean`) were not edited by the commit. Each states
something about a power `f ^ n` of a linear map, and every difference between their old and new
trees is the same one: the `^` they elaborate to now goes through `NPow.toPow` where it went
through `Monoid.toPow`. The upgrade changed the terms of these statements, most likely not their
meaning; confirming that needs the definitional-equality check in the new environment, which is
not part of release 0.0.
