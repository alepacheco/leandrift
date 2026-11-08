"""leandrift: check that a Lean project's statements survive an upgrade of Lean or its dependencies."""

import argparse
import json
import sys
from pathlib import Path

from . import __version__, exports, project
from .diff import compare
from .report import markdown


def write_reports(result, md_path=None, json_path=None, title="LeanDrift report"):
    if md_path:
        Path(md_path).write_text(markdown(result, title=title), encoding="utf-8")
    if json_path:
        Path(json_path).write_text(json.dumps(result.to_json(), indent=1, ensure_ascii=False) + "\n",
                                   encoding="utf-8")


def summary_line(result):
    for w in result.warnings:
        print(f"leandrift: warning: {w}", file=sys.stderr)
    c = result.counts()
    return (", ".join(f"{v} {k}" for k, v in c.items()) +
            f"; {len(result.new_sorries())} newly using sorry, "
            f"{len(result.new_nonstandard_axioms())} newly using another non-standard axiom")


def cmd_export(a):
    project.export(a.project, a.prefix, a.output, modules=a.module, pp=not a.no_pp,
                   axioms=not a.no_axioms)
    return 0


def cmd_diff(a):
    result = compare(exports.load(a.old), exports.load(a.new))
    if a.markdown or a.json:
        write_reports(result, a.markdown, a.json, title=a.title)
    else:
        sys.stdout.write(markdown(result, title=a.title))
    print(summary_line(result), file=sys.stderr)
    return 1 if a.fail_on_change and result.has_drift() else 0


def cmd_compare(a):
    out = Path(a.out)
    name = Path(str(a.repo).rstrip("/")).name.removesuffix(".git")
    workdir = Path(a.workdir) if a.workdir else Path("leandrift-work") / name
    old_path, new_path = project.compare_revisions(
        a.repo, a.old, a.new, a.prefix, workdir, out, modules=a.module, cache=not a.no_cache,
        targets=a.target)
    result = compare(exports.load(old_path), exports.load(new_path))
    title = a.title or f"LeanDrift report: {name} {a.old} -> {a.new}"
    write_reports(result, out / "report.md", out / "report.json", title=title)
    print(summary_line(result), file=sys.stderr)
    print(f"report: {out / 'report.md'}", file=sys.stderr)
    return 1 if a.fail_on_change and result.has_drift() else 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="leandrift", description=__doc__)
    p.add_argument("--version", action="version", version=f"leandrift {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    e = sub.add_parser("export", help="export a built Lean project's declarations (JSON Lines)")
    e.add_argument("project", help="the Lake project's directory (built with `lake build`)")
    e.add_argument("--prefix", action="append", required=True,
                   help="module prefix whose declarations are exported (repeatable)")
    e.add_argument("--module", action="append", default=[],
                   help="import only this module and its imports (repeatable)")
    e.add_argument("-o", "--output", required=True, help="the export file to write")
    e.add_argument("--no-pp", action="store_true", help="skip pretty-printing")
    e.add_argument("--no-axioms", action="store_true", help="skip collecting axioms")
    e.set_defaults(func=cmd_export)

    d = sub.add_parser("diff", help="compare two exports",
                       description="Compare two exports. Without --md or --json, the Markdown "
                                   "report goes to standard output; the summary always goes to "
                                   "standard error. Exit status: 0, 1 with --fail-on-change and "
                                   "drift, 2 on an error.")
    d.add_argument("old", help="the export before the upgrade (.jsonl or .jsonl.gz)")
    d.add_argument("new", help="the export after the upgrade (.jsonl or .jsonl.gz)")
    d.add_argument("--markdown", "--md", help="write the Markdown report here")
    d.add_argument("--json", help="write the JSON report here")
    d.add_argument("--title", default="LeanDrift report", help="the report's title")
    d.add_argument("--fail-on-change", action="store_true",
                   help="exit 1 if a statement changed or was removed, or a declaration newly "
                        "depends on sorry or another non-standard axiom")
    d.set_defaults(func=cmd_diff)

    c = sub.add_parser("compare", help="build, export and compare a project at two revisions")
    c.add_argument("repo", help="a git URL or path of the Lake project")
    c.add_argument("old", help="the revision before the upgrade (e.g. abc123^)")
    c.add_argument("new", help="the revision after the upgrade")
    c.add_argument("--prefix", action="append", required=True,
                   help="module prefix whose declarations are compared (repeatable)")
    c.add_argument("--module", action="append", default=[],
                   help="import only this module and its imports (repeatable)")
    c.add_argument("--target", action="append", default=[],
                   help="Lake target to build instead of the default ones (repeatable)")
    c.add_argument("--out", default="leandrift-out",
                   help="directory for exports, logs and reports (default leandrift-out)")
    c.add_argument("--workdir", help="where the clone lives (default leandrift-work/<name>)")
    c.add_argument("--no-cache", action="store_true",
                   help="do not run `lake exe cache get` (the dependencies, Mathlib included, are "
                        "then built from source, for each revision)")
    c.add_argument("--title", help="the report's title")
    c.add_argument("--fail-on-change", action="store_true", help="as for diff")
    c.set_defaults(func=cmd_compare)

    a = p.parse_args(argv)
    try:
        return a.func(a)
    except (project.StepFailed, ValueError, FileNotFoundError) as ex:
        print(f"leandrift: error: {ex}", file=sys.stderr)
        return 2
