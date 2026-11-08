"""The comparison as Markdown, for people."""

from .diff import ADDED, CHANGED, REMOVED, RENAMED, SAME, STANDARD_AXIOMS


def _code(s):
    return "`" + s.replace("`", "'") + "`"


def _block(s):
    fence = "```"
    while fence in s:
        fence += "`"
    return f"{fence}lean\n{s}\n{fence}"


def markdown(result, title="LeanDrift report", max_items=200):
    old, new = result.old, result.new
    c = result.counts()
    old_sorry, new_sorry = result.sorry_counts()
    lines = [f"# {title}", ""]
    for w in result.warnings:
        lines += [f"**Warning:** {w}.", ""]
    lines += [
        "| | old | new |",
        "|---|---|---|",
        f"| Lean | {old.lean} | {new.lean} |",
        f"| modules read | {len(old.header.get('modules', []))} | {len(new.header.get('modules', []))} |",
        f"| declarations | {len(old.decls)} | {len(new.decls)} |",
        f"| declarations depending on `sorryAx` | {old_sorry} | {new_sorry} |",
        "",
        "| statement | declarations |",
        "|---|---|",
    ]
    for s in (SAME, RENAMED, CHANGED, REMOVED, ADDED):
        lines.append(f"| {s} | {c[s]} |")
    lines += [f"| newly depending on `sorryAx` | {len(result.new_sorries())} |",
              f"| newly depending on another non-standard axiom | {len(result.new_nonstandard_axioms())} |",
              ""]

    changed = result.by_status(CHANGED)
    lines += [f"## Changed statements ({len(changed)})", ""]
    if not changed:
        lines += ["None.", ""]
    common = result.common_changes()
    if common:
        lines += ["Where several changed statements first differ in the same way (often one change "
                  "upstream, such as a definition or instance that statements elaborate to):", "",
                  "| old | new | statements |", "|---|---|---|"]
        for (a, b), names in common[:10]:
            lines.append(f"| {_code(a)} | {_code(b)} | {len(names)} |")
        lines.append("")
    for e in changed[:max_items]:
        name = e.new if e.new == e.old else f"{e.old} -> {e.new}"
        kind = e.kind if e.old_kind in ("", e.kind) else f"{e.old_kind} -> {e.kind}"
        lines += [f"### {_code(name)} ({kind}, {_code(e.module)})", ""]
        if e.detail:
            lines += [e.detail, ""]
        lines += ["Old:", "", _block(e.old_pp or "(not printed)"), "", "New:", "",
                  _block(e.new_pp or "(not printed)"), ""]
        if e.renames:
            lines += ["Renames applied before comparing: " +
                      ", ".join(f"{_code(a)} -> {_code(b)}" for a, b in e.renames[:10]) +
                      (" ..." if len(e.renames) > 10 else ""), ""]
    if len(changed) > max_items:
        lines += [f"... and {len(changed) - max_items} more (see the JSON report).", ""]

    sor = result.new_sorries()
    lines += [f"## New `sorry` ({len(sor)})", ""]
    if not sor:
        lines += ["None.", ""]
    for e in sor[:max_items]:
        lines.append(f"- {_code(e.new)} ({e.kind}, {e.status})")
    if sor:
        lines.append("")

    ax = result.new_nonstandard_axioms()
    lines += [f"## New axioms other than {', '.join(sorted(STANDARD_AXIOMS))} and `sorryAx` ({len(ax)})", ""]
    if not ax:
        lines += ["None.", ""]
    for e in ax[:max_items]:
        extra = [a for a in e.new_axioms if a not in STANDARD_AXIOMS and a != "sorryAx"]
        lines.append(f"- {_code(e.new)} ({e.kind}, {e.status}): " + ", ".join(_code(a) for a in extra))
    if ax:
        lines.append("")

    renamed = result.by_status(RENAMED)
    lines += [f"## Same after renames ({len(renamed)})", ""]
    if renamed:
        lines += ["| old | new | matched by | renames in its statement |", "|---|---|---|---|"]
        for e in renamed[:max_items]:
            inner = [r for r in e.renames if r != (e.old, e.new)]
            shown = ", ".join(f"{_code(a)} -> {_code(b)}" for a, b in inner[:4])
            if len(inner) > 4:
                shown += f" (+{len(inner) - 4})"
            via = e.via or "name"
            if e.old_kind and e.old_kind != e.kind:
                via += f" ({e.old_kind} -> {e.kind})"
            lines.append(f"| {_code(e.old)} | {_code(e.new) if e.new != e.old else 'same name'} | "
                         f"{via} | {shown} |")
        lines.append("")
    else:
        lines += ["None.", ""]
    if result.inferred_renames:
        lines += ["Renames found by identical statement (no deprecation alias): " +
                  ", ".join(f"{_code(a)} -> {_code(b)}" for a, b in list(result.inferred_renames.items())[:20]) +
                  (" ..." if len(result.inferred_renames) > 20 else ""), ""]

    for status in (REMOVED, ADDED):
        items = result.by_status(status)
        lines += [f"## {status.capitalize()} ({len(items)})", ""]
        if not items:
            lines += ["None.", ""]
            continue
        for e in items[:max_items]:
            lines.append(f"- {_code(e.old or e.new)} ({e.kind}, {_code(e.module)})")
        if len(items) > max_items:
            lines.append(f"- ... and {len(items) - max_items} more")
        lines.append("")
    lines += ["Statements are compared as Lean elaborated them (binder names ignored, binder kinds "
              "kept), after mapping names through the new version's deprecation aliases and the "
              "renames above. Definitional equality is not checked yet: a statement reported as "
              "changed may still be equivalent.", ""]
    return "\n".join(lines)
