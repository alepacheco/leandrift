"""Comparing two exports of the same project: which statements stayed, moved, changed, went or came."""

import difflib
from dataclasses import dataclass, field

from . import trees

SAME = "same"
RENAMED = "same after renames"
CHANGED = "changed"
REMOVED = "removed"
ADDED = "added"
STATUSES = [SAME, RENAMED, CHANGED, REMOVED, ADDED]

STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
SORRY = "sorryAx"

# Kinds whose statement is a proposition: two of them with the same statement are the same fact.
PROP_KINDS = {"theorem"}


@dataclass
class Entry:
    status: str
    old: str = None  # name in the old export
    new: str = None  # name in the new export
    kind: str = ""
    old_kind: str = ""
    module: str = ""
    via: str = ""  # how a renamed declaration was matched: "deprecation alias" or "identical statement"
    renames: list = field(default_factory=list)  # [(old constant, new constant)] used to match
    detail: str = ""  # for a changed statement: where it first differs
    old_pp: str = ""
    new_pp: str = ""
    new_axioms: list = field(default_factory=list)  # axioms the new version depends on, the old not
    sorry: bool = False  # depends on sorryAx in the new version but not in the old

    def to_json(self):
        d = {"status": self.status, "old": self.old, "new": self.new, "kind": self.kind,
             "module": self.module}
        if self.old_kind and self.old_kind != self.kind:
            d["old_kind"] = self.old_kind
        for k in ("via", "detail"):
            if getattr(self, k):
                d[k] = getattr(self, k)
        if self.renames:
            d["renames"] = [list(r) for r in self.renames]
        if self.status == CHANGED:
            d["old_pp"], d["new_pp"] = self.old_pp, self.new_pp
        if self.new_axioms:
            d["new_axioms"] = self.new_axioms
        if self.sorry:
            d["new_sorry"] = True
        return d


@dataclass
class Result:
    old: object
    new: object
    entries: list
    inferred_renames: dict  # renames found by identical statements (no deprecation alias)

    def by_status(self, status):
        return [e for e in self.entries if e.status == status]

    def counts(self):
        return {s: len(self.by_status(s)) for s in STATUSES}

    def new_sorries(self):
        return [e for e in self.entries if e.sorry]

    def new_nonstandard_axioms(self):
        return [e for e in self.entries
                if any(a not in STANDARD_AXIOMS and a != SORRY for a in e.new_axioms)]

    def sorry_counts(self):
        def n(exp):
            return sum(1 for d in exp.decls.values() if SORRY in d.axioms and not d.alias_of)
        return n(self.old), n(self.new)

    def to_json(self):
        old_sorry, new_sorry = self.sorry_counts()
        return {
            "leandrift": 1,
            "old": _side(self.old), "new": _side(self.new),
            "summary": dict(self.counts(), new_sorry=len(self.new_sorries()),
                            new_nonstandard_axioms=len(self.new_nonstandard_axioms()),
                            sorry_old=old_sorry, sorry_new=new_sorry),
            "inferred_renames": self.inferred_renames,
            "declarations": [e.to_json() for e in self.entries],
        }


def _side(exp):
    h = exp.header
    return {"file": exp.path, "lean": h.get("lean"), "prefixes": h.get("prefixes"),
            "modules": len(h.get("modules", [])), "declarations": len(exp.decls),
            "deprecation_aliases": len(exp.aliases)}


class Resolver:
    """Maps an old constant name to its name in the new version: deprecation aliases of the new
    environment, then renames inferred from identical statements; chains are followed."""

    def __init__(self, aliases, new_names):
        self.aliases = aliases
        self.new_names = new_names
        self.inferred = {}

    def __call__(self, name):
        seen = set()
        cur = name
        while cur not in seen:
            seen.add(cur)
            if cur in self.inferred:
                cur = self.inferred[cur]
            elif cur in self.aliases and (cur not in self.new_names or self.aliases[cur] in self.new_names):
                cur = self.aliases[cur]
            else:
                break
        return cur


def _statement(decl, resolve=None):
    """The comparable statement of a declaration: its type, and for an inductive type its
    constructors (last name component and type), with names resolved if asked."""
    def r(t):
        return trees.rename(t, resolve) if resolve else t
    ctors = [[c["name"].rsplit(".", 1)[-1], r(c["tree"])] for c in decl.ctors]
    return trees.key([r(decl.tree), ctors])


def _similar(a, b):
    a, b = a.rsplit(".", 1)[-1].lower(), b.rsplit(".", 1)[-1].lower()
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.6


def _renames_used(decl, resolve):
    names = trees.constants(decl.tree)
    for c in decl.ctors:
        trees.constants(c["tree"], names)
    return sorted((n, resolve(n)) for n in names if resolve(n) != n)


def compare(old, new):
    """Compare two exports (exports.Export) and return a Result."""
    new_real = {n for n, d in new.decls.items() if not d.alias_of}
    resolve = Resolver(new.aliases, set(new.decls))

    def counterpart(name):
        """The new declaration an old one corresponds to, by name or deprecation alias."""
        d = new.decls.get(name)
        if d is not None and not d.alias_of:
            return name, ""
        target = resolve(name)
        if target != name and target in new_real:
            return target, ("identical statement" if name in resolve.inferred else "deprecation alias")
        if d is not None:
            return name, ""
        return None, ""

    # Old declarations with no counterpart by name or alias may have been renamed without an alias.
    # Match them to unclaimed new declarations by identical statement (after the renames known so
    # far), one to one; repeat, since each rename can make more statements match.
    while True:
        claimed = set()
        unmatched = []
        for name in old.decls:
            c, _ = counterpart(name)
            if c is None:
                unmatched.append(name)
            else:
                claimed.add(c)
        free = [n for n in new_real if n not in claimed and n not in old.decls]
        new_by_key = {}
        for n in free:
            new_by_key.setdefault(_statement(new.decls[n], resolve), []).append(n)
        old_by_key = {}
        for o in unmatched:
            old_by_key.setdefault(_statement(old.decls[o], resolve), []).append(o)
        found = {}
        for k, olds in old_by_key.items():
            news = new_by_key.get(k, [])
            if len(olds) != 1 or len(news) != 1:
                continue
            o, n = olds[0], news[0]
            od, nd = old.decls[o], new.decls[n]
            if (od.kind in PROP_KINDS and nd.kind in PROP_KINDS) or _similar(o, n):
                found[o] = n
        if not found:
            break
        resolve.inferred.update(found)
        # an inferred rename of an inductive type renames its constructors with it
        for o, n in found.items():
            oc, nc = old.decls[o].ctors, new.decls[n].ctors
            if len(oc) == len(nc):
                for a, b in zip(oc, nc):
                    if a["name"] != b["name"]:
                        resolve.inferred.setdefault(a["name"], b["name"])

    entries = []
    claimed = set()
    for name, od in old.decls.items():
        if od.alias_of:
            # a deprecated alias in the old version: compared through what it points to
            continue
        target, via = counterpart(name)
        if target is None:
            entries.append(Entry(REMOVED, old=name, kind=od.kind, module=od.module, old_pp=od.full_pp))
            continue
        claimed.add(target)
        nd = new.decls[target]
        e = Entry(SAME, old=name, new=target, kind=nd.kind, old_kind=od.kind, module=nd.module,
                  via=via, old_pp=od.full_pp, new_pp=nd.full_pp)
        if _statement(od) == _statement(nd) and target == name:
            e.status = SAME
        elif _statement(od, resolve) == _statement(nd, resolve):
            e.status = RENAMED
            e.renames = _renames_used(od, resolve)
            if target != name:
                e.renames = [(name, target)] + [r for r in e.renames if r != (name, target)]
        else:
            e.status = CHANGED
            e.detail = _describe(od, nd, resolve)
            e.renames = _renames_used(od, resolve)
        gained = sorted(set(nd.axioms) - set(od.axioms))
        e.new_axioms = gained
        e.sorry = SORRY in gained
        entries.append(e)
    for name, nd in new.decls.items():
        if name in claimed or nd.alias_of:
            continue
        if name in old.decls and not old.decls[name].alias_of:
            continue
        extra = sorted(a for a in nd.axioms if a not in STANDARD_AXIOMS)
        entries.append(Entry(ADDED, new=name, kind=nd.kind, module=nd.module, new_pp=nd.full_pp,
                             new_axioms=extra, sorry=SORRY in extra))
    return Result(old=old, new=new, entries=entries,
                  inferred_renames=dict(sorted(resolve.inferred.items())))


def _describe(od, nd, resolve):
    if od.kind != nd.kind and (od.ctors or nd.ctors) and len(od.ctors) != len(nd.ctors):
        return (f"was {_article(od.kind)} with {len(od.ctors)} constructors, "
                f"now {_article(nd.kind)} with {len(nd.ctors)}")
    a, b = trees.rename(od.tree, resolve), trees.rename(nd.tree, resolve)
    if a == b:
        # the type is the same: a constructor differs
        oc = {c["name"].rsplit(".", 1)[-1]: c for c in od.ctors}
        nc = {c["name"].rsplit(".", 1)[-1]: c for c in nd.ctors}
        if set(oc) != set(nc):
            gone, came = sorted(set(oc) - set(nc)), sorted(set(nc) - set(oc))
            parts = []
            if gone:
                parts.append("constructors removed: " + ", ".join(gone))
            if came:
                parts.append("constructors added: " + ", ".join(came))
            return "; ".join(parts)
        for k in oc:
            ta, tb = trees.rename(oc[k]["tree"], resolve), trees.rename(nc[k]["tree"], resolve)
            if ta != tb:
                return f"constructor {k} changed: " + _where(ta, tb)
        return "constructors reordered"
    if trees.erase_binder_info(a) == trees.erase_binder_info(b):
        return "only binder info changed (explicit, implicit or instance arguments)"
    return _where(a, b)


def _where(a, b):
    d = trees.first_difference(a, b)
    if d is None:
        return ""
    path, x, y = d
    place = "/".join(path) or "top"
    return f"first difference at {place}: {trees.show(x, 120)}  ->  {trees.show(y, 120)}"


def _article(kind):
    return ("an " if kind[:1] in "aeiou" else "a ") + kind
