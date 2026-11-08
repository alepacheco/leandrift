"""Reading the exporter's JSON Lines files."""

import gzip
import json
import sys
from dataclasses import dataclass, field

# Statement trees nest one level per binder and application; deep ones exceed Python's default limit.
sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))


@dataclass
class Decl:
    name: str
    kind: str
    module: str
    tree: list
    pp: str = ""
    axioms: list = field(default_factory=list)
    ctors: list = field(default_factory=list)  # [{"name", "tree", "pp"}] for inductive types
    deprecated: dict = None  # {"new": ..., "since": ...} when the declaration is itself deprecated

    @property
    def full_pp(self):
        """The pretty-printed type, followed for an inductive type by its constructors."""
        lines = [self.pp]
        for c in self.ctors:
            lines.append(f"| {c['name'].rsplit('.', 1)[-1]} : {c.get('pp', '')}")
        return "\n".join(lines)

    @property
    def alias_of(self):
        """The declaration this one is a deprecated alias of, if any."""
        return (self.deprecated or {}).get("new")


@dataclass
class Export:
    header: dict
    decls: dict  # name -> Decl, in the exporter's order
    aliases: dict  # old name -> new name (the environment's deprecation aliases)
    path: str = ""

    @property
    def lean(self):
        return self.header.get("lean", "?")


def _open(path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, encoding="utf-8")


def load(path):
    header, decls, aliases = None, {}, {}
    with _open(path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{lineno}: not JSON: {e}") from None
            t = rec.get("type")
            if t == "header":
                header = rec
            elif t == "decl":
                d = Decl(name=rec["name"], kind=rec["kind"], module=rec.get("module", ""),
                         tree=rec["tree"], pp=rec.get("pp", ""), axioms=rec.get("axioms", []),
                         ctors=rec.get("ctors", []), deprecated=rec.get("deprecated"))
                decls[d.name] = d
            elif t == "alias":
                aliases[rec["old"]] = rec["new"]
    if header is None:
        raise ValueError(f"{path}: no header line; is this a LeanDrift export?")
    if header.get("format") != 1:
        raise ValueError(f"{path}: export format {header.get('format')} is not supported (expected 1)")
    return Export(header=header, decls=decls, aliases=aliases, path=str(path))
