# LeanDrift

LeanDrift checks that the statements of a Lean project's theorems and definitions survive an
upgrade of Lean or Mathlib. Given the project before and after an upgrade, it lists every
declaration whose statement changed, beyond renames, and every declaration that newly depends on
`sorry` or on a new axiom.

It is for people who keep Lean libraries building on the latest Mathlib, by hand or with automated
repair: a repair that compiles can still change what a theorem says (a hypothesis weakened, `≤`
turned into `<`, an argument made implicit, a definition replaced). LeanDrift shows those changes,
so they can be reviewed instead of slipping through.

This is release 0.0, a prototype. It compares statements as Lean elaborated them; it does not yet
check whether a changed statement is definitionally equal to the old one in the new environment,
nor flag statements that use a Mathlib definition whose body changed. See [Limits](#limits).

## How it works

1. **Export** (`leandrift/Export.lean`): a Lean 4 program run inside the project's own Lake
   environment (`lake env lean --run`), with the project's toolchain and its built `.olean` files.
   For every declaration of the given module prefixes it writes, as JSON Lines:
   its name, kind (theorem, def, abbrev, instance, axiom, opaque, inductive, structure, class) and
   module; its type as a structural tree (constants with universe levels, bound variables by
   de Bruijn index, binder names dropped, binder kinds kept, universe parameters by position,
   proofs inside the statement erased, as the kernel ignores them); its type pretty-printed; the
   axioms it depends on (as `#print axioms` lists them, `sorryAx` included); for an inductive type,
   its constructors, and for a structure its field names. It also writes the environment's
   deprecations (old name -> new name, from the `deprecated` attribute), marking those where the
   old name is defined as the new one: these aliases make the rename map.
   It keeps to a small part of Lean's meta API and runs unchanged on toolchains a year apart
   (tested on v4.24.0, v4.25.0, v4.31.0, v4.32.0, v4.35.0, v4.36.0-rc1 and v4.36.0-rc2).
2. **Diff** (`leandrift diff`, Python 3.9+, standard library only): matches each old declaration
   to a new one by name, through the deprecation aliases (of the new version, then the old), or,
   failing both, by an identical statement (one to one; for declarations that are not theorems,
   only between names equal but for case and underscores). Each is then:
   - **same**: the same name and statement;
   - **same after renames**: equal once the constants it mentions (and its own name) are mapped
     through the deprecation aliases and the renames found;
   - **changed**: the statement differs; both versions are shown, with where they first differ;
   - **removed** or **added**.

   Any declaration that newly depends on `sorryAx`, or on an axiom other than `propext`,
   `Classical.choice` and `Quot.sound`, is reported too. The output is Markdown and JSON.
3. **Compare** (`leandrift compare`): clones a project, and for each of two revisions checks it
   out, fetches Mathlib's prebuilt cache (`lake exe cache get`) when the project uses Mathlib,
   builds it (`lake build`), exports it, and diffs the two exports.

## Install

LeanDrift needs [elan](https://github.com/leanprover/elan) (which installs each project's Lean
toolchain), git, and Python 3.9 or newer. Nothing else: the Python part uses only the standard
library.

```sh
git clone https://github.com/alepacheco/leandrift
export PATH="$PWD/leandrift/bin:$PATH"
leandrift --help
```

(Or install it as a package, in a virtual environment or with pipx:
`python3 -m venv .venv && .venv/bin/pip install ./leandrift`.)

`leandrift compare` builds the projects it compares, which runs their code (their Lake
configuration, the toolchain their `lean-toolchain` names, and what their build elaborates), as
`lake build` always does. Compare only projects you would build yourself, or run it in the
container below.

Or use the container image, which has all of them:

```sh
docker build -t leandrift -f leandrift/docker/Dockerfile leandrift
mkdir -p out
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -v leandrift-elan:/opt/elan -v leandrift-cache:/cache -v leandrift-work:/work -v "$PWD/out:/out" \
  leandrift leandrift compare https://github.com/YaelDillies/cam-combi '34a573b79a^' 34a573b79a \
  --prefix LeanCamCombi --out /out/cam-combi
```

The volumes keep Lean toolchains (`/opt/elan`), Mathlib's prebuilt files (`/cache`, about 1 GB
per Mathlib version) and the clones `compare` builds in (`/work`) between runs; a toolchain a
compared project fetched stays in the first one, so give each project you do not trust volumes of
its own. `out/` receives the reports, owned by you. A project the size of the examples takes
about five minutes on three cores the first time.

## Use

Compare a project before and after an upgrade commit:

```sh
leandrift compare https://github.com/YaelDillies/cam-combi '34a573b79a^' 34a573b79a \
  --prefix LeanCamCombi --out out/cam-combi
```

This writes `out/cam-combi/report.md` and `report.json`, the two exports (`old.jsonl`,
`new.jsonl`) and each side's build log (`old.log`, `new.log`; without `--out`, all of it goes to
`leandrift-out/`). The clone it builds in, with the project's dependencies (Mathlib's included, a
few GB), stays in `leandrift-work/<name>/` (or `--workdir`), so a second comparison of the same
project reuses it.

- `--prefix` names the module prefix whose declarations are compared; `--module M` imports only
  `M` and what it imports instead of every module under the prefixes (both repeatable).
- A revision is a branch of the repository (as fetched), a tag, a commit, or an expression such
  as `abc123^`.
- `--target T` builds Lake target `T` instead of the default ones (repeatable); `--no-cache`
  skips `lake exe cache get` (Mathlib is then built from source); `--title` sets the report's
  title.
- `--fail-on-change` makes it exit with status 1 when a statement changed or was removed, or a
  declaration newly depends on `sorry` or another non-standard axiom. Errors exit with status 2.

Or run the two steps yourself, in projects you have built:

```sh
(cd my-project-before && lake exe cache get && lake build && leandrift export . --prefix MyProject -o ../old.jsonl)
(cd my-project-after  && lake exe cache get && lake build && leandrift export . --prefix MyProject -o ../new.jsonl)
leandrift diff old.jsonl new.jsonl --md report.md --json report.json
```

(`lake exe cache get` fetches Mathlib's prebuilt files; leave it out for a project without
Mathlib.) `leandrift diff` reads exports plain or gzipped (`.jsonl.gz`); `--md` (or `--markdown`)
and `--json` write the reports to files, and without either it prints the Markdown report on
standard output. Its summary line goes to standard
error.

`leandrift export` runs `lake env lean --run <LeanDrift's checkout>/leandrift/Export.lean --prefix
MyProject -o ...` in the project; you can run that command directly too, with the full path to
`Export.lean`. `--no-pp` and `--no-axioms` skip pretty-printing and collecting axioms (faster,
but the diff then shows no statements or no new axioms). By default it imports every built module
under the prefixes, so build each version in a clean checkout (or delete `.lake/build` first):
the `.olean` of a module that no longer exists would otherwise still be read. `--module M`
imports only `M` and what it imports.

## Examples

`examples/` holds real upgrade commits of projects in Mathlib's
[downstream-reports](https://github.com/leanprover-community/downstream-reports) inventory, each
with its report and one command that reproduces it in a container. See
[examples/README.md](examples/README.md).

## Tests

In the clone's top directory (after the install steps above, `cd leandrift`):

```sh
python3 -m unittest discover -s tests -v
```

The unit tests (`tests/test_diff.py`) check the comparison on small exports. The end-to-end test
(`tests/test_e2e.py`) builds the tiny project in `tests/e2e/` at two versions, one on Lean
v4.25.0 (November 2025) and one on v4.36.0-rc2 (October 2026), exports both and checks every
declaration's verdict, including renames with and without deprecation aliases, a changed
statement, an argument made explicit, a field added to a structure, a new `sorry` and a new
axiom. It runs when `lake` is on the PATH (elan downloads both toolchains on first use); set
`LEANDRIFT_E2E=0` to skip it. In the container:

```sh
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v leandrift-elan:/opt/elan leandrift \
  sh -c 'cd /opt/leandrift && python3 -m unittest discover -s tests -v'
```

## Limits

- A statement reported as changed may still be definitionally equal to the old one in the new
  environment, or equivalent to it; release 0.0 does not check either.
- Definitions are compared by their type, not their body: a definition whose body changed (in
  the project or in Mathlib) changes the meaning of statements that use it without showing here.
- Renames without a deprecation alias are inferred only from identical statements, one to one
  (for declarations that are not theorems, only between names equal but for case and
  underscores). A renamed type's members (constructors, fields) are followed only for types of
  the project.
- A declaration the upgrade moved out of the project (often a lemma now in Mathlib) is reported
  as removed; release 0.0 does not look for it in the new dependencies.
- `compare` takes both revisions from the one repository given (its branches and tags); for a
  pull request from a fork, give the fork's URL.
- Declarations Lean generates (recursors, equation lemmas, structure projections, `simp`'s
  congruence lemmas, auxiliary definitions) and private declarations are not exported.
- Every module under a prefix is imported together; a project whose modules cannot all be
  imported at once needs `--module`.

## License

Apache-2.0. See [LICENSE](LICENSE).
