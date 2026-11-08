# misc-yd: bump to Lean v4.36.0-rc1

- Project: [YaelDillies/misc-yd](https://github.com/YaelDillies/misc-yd) (library `MiscYD`), one of
  the projects Mathlib's downstream-reports service builds against new Mathlib.
- Commit: [a7b5774](https://github.com/YaelDillies/misc-yd/commit/a7b57745ba06180ae7b1e6ef43489e035c21600d)
  "Bump to v4.36.0-rc1" (17 October 2026), against its parent
  [6d8c6cc](https://github.com/YaelDillies/misc-yd/commit/6d8c6ccea5a924d9b66fbd97e0fd83bba6b8f954).
- What it upgraded: Lean v4.35.0 -> v4.36.0-rc1, and Mathlib with it.
- What it edited by hand: `contrapose!` became `contrapose` in five places in the proofs of
  `MiscYD/AddCombi/Kneser/Kneser.lean`, and in `MiscYD/Book/SylvesterChvatal.lean` the inductive
  set `GenerateLine` was replaced by an inductive predicate `IsGenerated` and a definition
  `GenerateLine := Set.ofPred (IsGenerated s)`, with four lemmas about it restated.

Reproduce (from the repository's root; needs Docker):

```sh
sh examples/misc-yd-a7b5774/run.sh
```

or compare the exports kept here, without Lean:

```sh
leandrift diff examples/misc-yd-a7b5774/old.jsonl.gz examples/misc-yd-a7b5774/new.jsonl.gz
```

## What the report found

[report.md](report.md) (and [report.json](report.json)): of 260 declarations, 259 have the same
statement. The one that changed is `GenerateLine`, which went from an inductive type with three
constructors to a definition; `IsGenerated` is added. The five proof edits in `Kneser.lean` changed
no statement.

The six lemmas about `GenerateLine` (`subset_generateLine`, the three `generateLine_close_*`,
`generateLine_minimal`, `Set.IsLine.generateLine_subset`) are reported as the same, because their
statements still read `z ∈ GenerateLine s` and the like: what changed is the definition they use.
Release 0.0 compares statements, not the definitions inside them; the report shows that
`GenerateLine` itself changed, and following such a change to the statements that use it is
planned work.
