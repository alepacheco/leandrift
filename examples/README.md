# Examples: real upgrades

Three upgrade commits of projects that Mathlib's
[downstream-reports](https://github.com/leanprover-community/downstream-reports) service builds
against new Mathlib, a year apart in Lean versions. Each folder holds the commit's description,
the report LeanDrift made (`report.md`, `report.json`), the two exports it compared
(`old.jsonl.gz`, `new.jsonl.gz`), and `run.sh`, one command that reproduces it all in a container.

| example | upgrade | declarations | same | same after renames | changed | removed | added |
|---|---|---|---|---|---|---|---|
| [cam-combi-34a573b](cam-combi-34a573b/) | Lean v4.24.0 -> v4.25.0 (Nov 2025) | 169 | 141 | 0 | 28 | 0 | 0 |
| [persistentdecomp-7cfd07c](persistentdecomp-7cfd07c/) | Lean v4.31.0 -> v4.32.0 (Jul 2026) | 160 | 151 | 3 | 6 | 0 | 0 |
| [misc-yd-a7b5774](misc-yd-a7b5774/) | Lean v4.35.0 -> v4.36.0-rc1 (Oct 2026) | 260 | 259 | 0 | 1 | 0 | 1 |

What they show, in short (each folder's README has the details):

- **cam-combi** (November 2025): 28 of 169 statements changed in the upgrade although the commit
  rewrote only two of them by hand, and those two only in form. In all 28 the change is how Mathlib
  now elaborates the coercion from `Finset` to `Set` (through `SetLike`), which the report groups
  into three rows.
- **PersistentDecomp** (July 2026): three declarations renamed without deprecation aliases, one of
  them from a definition to a theorem, are matched by their statements; six statements that the
  commit did not touch changed in how `^` elaborates (`Monoid.toPow` became `NPow.toPow`).
- **misc-yd** (October 2026): a clean upgrade for 259 of 260 statements; the one change is a
  definition the commit replaced (an inductive type turned into a definition over a new one).

In both changes that come from Mathlib, the new statements are very likely definitionally equal to
the old ones; release 0.0 shows them, and a later release checks them.

To reproduce one (needs Docker; the first run downloads two Lean toolchains and two versions of
Mathlib's prebuilt cache, a few GB):

```sh
sh examples/cam-combi-34a573b/run.sh
```

The report lands in `examples/cam-combi-34a573b/out/`. To check only the comparison, without Lean:

```sh
bin/leandrift diff examples/cam-combi-34a573b/old.jsonl.gz examples/cam-combi-34a573b/new.jsonl.gz
```
