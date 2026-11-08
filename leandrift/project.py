"""Running a Lean project's own toolchain: building it, exporting it, and comparing two revisions."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

EXPORTER = Path(__file__).resolve().parent.parent / "exporter" / "Export.lean"


class StepFailed(RuntimeError):
    pass


def log(msg):
    print(f"leandrift: {msg}", file=sys.stderr, flush=True)


def run(cmd, cwd, logfile=None):
    """Run a command in `cwd`, its output appended to `logfile` (or shown), failing loudly."""
    log(f"$ {' '.join(cmd)}   (in {cwd})")
    if logfile is None:
        r = subprocess.run(cmd, cwd=cwd)
    else:
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(f"\n$ {' '.join(cmd)}\n")
            f.flush()
            r = subprocess.run(cmd, cwd=cwd, stdout=f, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        where = f"; its output is in {logfile}" if logfile else ""
        raise StepFailed(f"`{' '.join(cmd)}` failed with exit code {r.returncode}{where}")


def uses_mathlib(project):
    manifest = Path(project) / "lake-manifest.json"
    if not manifest.exists():
        return False
    try:
        packages = json.loads(manifest.read_text(encoding="utf-8")).get("packages", [])
    except json.JSONDecodeError:
        return False
    return any(p.get("name") == "mathlib" for p in packages)


def export(project, prefixes, out, modules=(), logfile=None, pp=True, axioms=True):
    """Export a built project's declarations under `prefixes` with its own toolchain."""
    cmd = ["lake", "env", "lean", "--run", str(EXPORTER)]
    for p in prefixes:
        cmd += ["--prefix", p]
    for m in modules:
        cmd += ["--module", m]
    cmd += ["-o", str(Path(out).resolve())]
    if not pp:
        cmd.append("--no-pp")
    if not axioms:
        cmd.append("--no-axioms")
    run(cmd, cwd=project, logfile=logfile)


def build(project, logfile=None, cache=True, targets=()):
    """`lake exe cache get` (for a project on Mathlib) and `lake build`, with the project's toolchain."""
    if cache and uses_mathlib(project):
        run(["lake", "exe", "cache", "get"], cwd=project, logfile=logfile)
    run(["lake", "build", *targets], cwd=project, logfile=logfile)


def checkout(src, rev, logfile=None):
    run(["git", "checkout", "--quiet", "--force", "--detach", rev], cwd=src, logfile=logfile)
    # untracked files of the other revision go, the dependencies Lake fetched stay
    run(["git", "clean", "-ffdq", "-e", ".lake"], cwd=src, logfile=logfile)
    # the project's own build outputs go: a module the other revision had must not be read
    build_dir = Path(src) / ".lake" / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)


def compare_revisions(repo, old_rev, new_rev, prefixes, workdir, outdir, modules=(), cache=True,
                      targets=()):
    """Clone `repo` (a URL or a path), build and export it at two revisions, and return the two
    export paths. Each side's commands and output are logged to <outdir>/<side>.log."""
    workdir, outdir = Path(workdir).resolve(), Path(outdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    outdir.mkdir(parents=True, exist_ok=True)
    src = workdir / "src"
    if not (src / ".git").exists():
        run(["git", "clone", "--quiet", "--filter=blob:none", str(repo), str(src)], cwd=workdir)
    else:
        run(["git", "fetch", "--quiet", "origin"], cwd=src)
    paths = []
    for side, rev in (("old", old_rev), ("new", new_rev)):
        logfile = outdir / f"{side}.log"
        logfile.write_text("", encoding="utf-8")
        sha = subprocess.run(["git", "rev-parse", "--verify", f"{rev}^{{commit}}"], cwd=src,
                             capture_output=True, text=True)
        if sha.returncode != 0:
            raise StepFailed(f"no commit {rev} in {repo}")
        log(f"{side}: {rev} = {sha.stdout.strip()}")
        checkout(src, sha.stdout.strip(), logfile)
        toolchain = (src / "lean-toolchain").read_text(encoding="utf-8").strip() \
            if (src / "lean-toolchain").exists() else "(none)"
        log(f"{side}: toolchain {toolchain}; building (log: {logfile})")
        build(src, logfile=logfile, cache=cache, targets=targets)
        out = outdir / f"{side}.jsonl"
        log(f"{side}: exporting {', '.join(prefixes)}")
        export(src, prefixes, out, modules=modules, logfile=logfile)
        paths.append(out)
    return paths
