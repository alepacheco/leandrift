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

1. **Export** (`exporter/Export.lean`): a Lean 4 program run inside the project's own Lake
   environment (`lake env lean --run`), with the project's toolchain and its built `.olean` files.
   For every declaration of the given module prefixes it writes, as JSON Lines:
   its name, kind (theorem, def, abbrev, instance, axiom, opaque, inductive, structure, class) and
   module; its type as a structural tree (constants with universe levels, bound variables by
   de Bruijn index, binder names dropped, binder kinds kept, universe parameters by position);
   its type pretty-printed; the axioms it depends on (as `#print axioms` lists them, `sorryAx`
   included); for an inductive type, its constructors. It also writes the environment's
   deprecation aliases (old name -> new name, from the `deprecated` attribute) for the rename map.
   It keeps to a small part of Lean's meta API and runs unchanged on toolchains a year apart
   (tested on v4.24.0, v4.25.0, v4.31.0, v4.32.0, v4.35.0, v4.36.0-rc1 and v4.36.0-rc2).
2. **Diff** (`leandrift diff`, Python 3.9+, standard library only): matches each old declaration
   to a new one by name, through the new version's deprecation aliases, or, failing both, by an
   identical statement (one to one; for declarations that are not theorems, only between similar
   names). Each is then:
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
export PATH="$PWD/leandrift/bin:$PATH"     # or: pip install ./leandrift
leandrift --help
```

Or use the container image, which has all of them:

```sh
docker build -t leandrift -f leandrift/docker/Dockerfile leandrift
docker run --rm -it -v leandrift-elan:/opt/elan -v leandrift-cache:/root/.cache -v "$PWD/out:/out" \
  leandrift leandrift --help
```

(The two volumes keep Lean toolchains and Mathlib's cache between runs.)

## Use

Compare a project before and after an upgrade commit:

```sh
leandrift compare https://github.com/YaelDillies/cam-combi 34a573b79a^ 34a573b79a \
  --prefix LeanCamCombi --out out/cam-combi
```

This writes `out/cam-combi/report.md` and `report.json`, the two exports (`old.jsonl`,
`new.jsonl`) and each side's build log. `--prefix` names the module prefix whose declarations are
compared (repeatable); `--fail-on-change` makes it exit with status 1 when a statement changed or a
declaration newly depends on `sorry`.

Or run the two steps yourself, in projects you have built:

```sh
cd my-project-before && lake build && leandrift export . --prefix MyProject -o ../old.jsonl
cd my-project-after  && lake build && leandrift export . --prefix MyProject -o ../new.jsonl
leandrift diff old.jsonl new.jsonl --md report.md --json report.json
```

`leandrift export` runs `lake env lean --run exporter/Export.lean --prefix MyProject -o ...` in the
project; you can run that command directly too. By default it imports every built module under
the prefixes; `--module M` imports only `M` and what it imports.

## Examples

`examples/` holds real upgrade commits of projects in Mathlib's
[downstream-reports](https://github.com/leanprover-community/downstream-reports) inventory, each
with its report and one command that reproduces it in a container. See
[examples/README.md](examples/README.md).

## Tests

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
docker run --rm -v leandrift-elan:/opt/elan leandrift \
  sh -c 'cd /opt/leandrift && python3 -m unittest discover -s tests -v'
```

## Limits

- A statement reported as changed may still be definitionally equal to the old one in the new
  environment, or equivalent to it; release 0.0 does not check either.
- Definitions are compared by their type, not their body: a definition whose body changed (in
  the project or in Mathlib) changes the meaning of statements that use it without showing here.
- Renames without a deprecation alias are inferred only from identical statements, one to one.
- Declarations Lean generates (recursors, equation lemmas, structure projections, auxiliary
  definitions) and private declarations are not exported.
- Every module under a prefix is imported together; a project whose modules cannot all be
  imported at once needs `--module`.

## License

Apache-2.0. See [LICENSE](LICENSE).
