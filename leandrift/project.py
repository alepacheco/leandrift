"""Running a Lean project's own toolchain: building it, exporting it, and comparing two revisions."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

EXPORTER = Path(__file__).resolve().parent / "Export.lean"


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
    src = Path(src)
    run(["git", "checkout", "--quiet", "--force", "--detach", rev], cwd=src, logfile=logfile)
    # untracked files of the other revision go, the dependencies Lake fetched stay
    run(["git", "clean", "-ffdq", "-e", ".lake"], cwd=src, logfile=logfile)
    # the project's own build outputs go: a module the other revision had must not be read
    lake = src / ".lake"
    if lake.is_symlink() or (lake.exists() and not lake.is_dir()):
        raise StepFailed(f"{lake} is not a plain directory; refusing to clean it")
    build_dir = lake / "build"
    if build_dir.is_symlink():
        raise StepFailed(f"{build_dir} is a symbolic link; refusing to remove it")
    if build_dir.exists():
        shutil.rmtree(build_dir)


def git_out(args, cwd):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def resolve_rev(src, rev):
    """The commit a revision names: a branch of origin as fetched, else as given (a hash, a tag,
    `abc^`)."""
    for cand in (f"origin/{rev}", rev):
        sha = git_out(["rev-parse", "--verify", "--quiet", f"{cand}^{{commit}}"], src)
        if sha:
            return sha
    raise StepFailed(f"no commit {rev} in {src}")


def compare_revisions(repo, old_rev, new_rev, prefixes, workdir, outdir, modules=(), cache=True,
                      targets=()):
    """Clone `repo` (a URL or a path), build and export it at two revisions, and return the two
    export paths. Each side's commands and output are logged to <outdir>/<side>.log."""
    workdir, outdir = Path(workdir).resolve(), Path(outdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    outdir.mkdir(parents=True, exist_ok=True)
    src = workdir / "src"
    repo_str = str(repo) if "://" in str(repo) or str(repo).startswith("git@") \
        else str(Path(repo).resolve())
    if (src / ".git").exists() and git_out(["remote", "get-url", "origin"], src) != repo_str:
        raise StepFailed(f"{src} is a clone of another repository; give another --workdir")
    if not (src / ".git").exists():
        run(["git", "clone", "--quiet", "--filter=blob:none", "--", repo_str, str(src)], cwd=workdir)
    else:
        run(["git", "fetch", "--quiet", "--tags", "--force", "origin",
             "+refs/heads/*:refs/remotes/origin/*"], cwd=src)
    # both revisions are resolved before either is checked out (`HEAD~1` must not move)
    shas = {"old": resolve_rev(src, old_rev), "new": resolve_rev(src, new_rev)}
    paths = []
    for side, rev in (("old", old_rev), ("new", new_rev)):
        logfile = outdir / f"{side}.log"
        logfile.write_text("", encoding="utf-8")
        log(f"{side}: {rev} = {shas[side]}")
        checkout(src, shas[side], logfile)
        toolchain = (src / "lean-toolchain").read_text(encoding="utf-8").strip() \
            if (src / "lean-toolchain").exists() else "(none)"
        log(f"{side}: toolchain {toolchain}; building (log: {logfile})")
        build(src, logfile=logfile, cache=cache, targets=targets)
        out = outdir / f"{side}.jsonl"
        log(f"{side}: exporting {', '.join(prefixes)}")
        export(src, prefixes, out, modules=modules, logfile=logfile)
        paths.append(out)
    return paths
