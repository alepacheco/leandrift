"""Comparing two exports of the same project: which statements stayed, moved, changed, went or came."""

import os
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
    first_change: tuple = None  # (old subterm, new subterm) where a changed statement first differs
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
    warnings: list = field(default_factory=list)

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

    def common_changes(self, least=2):
        """The first differences shared by several changed statements, most frequent first."""
        groups = {}
        for e in self.by_status(CHANGED):
            if e.first_change:
                groups.setdefault(e.first_change, []).append(e.new)
        return sorted(((k, v) for k, v in groups.items() if len(v) >= least),
                      key=lambda kv: (-len(kv[1]), kv[0]))

    def has_drift(self):
        """A statement changed or went, or a declaration newly depends on sorry or another axiom."""
        return bool(self.by_status(CHANGED) or self.by_status(REMOVED) or self.new_sorries()
                    or self.new_nonstandard_axioms())

    def to_json(self):
        old_sorry, new_sorry = self.sorry_counts()
        return {
            "leandrift": 1,
            "old": _side(self.old), "new": _side(self.new),
            "summary": dict(self.counts(), new_sorry=len(self.new_sorries()),
                            new_nonstandard_axioms=len(self.new_nonstandard_axioms()),
                            sorry_old=old_sorry, sorry_new=new_sorry),
            "warnings": self.warnings,
            "inferred_renames": self.inferred_renames,
            "common_changes": [{"old": k[0], "new": k[1], "declarations": v}
                               for k, v in self.common_changes()],
            "declarations": [e.to_json() for e in self.entries],
        }


def _side(exp):
    h = exp.header
    return {"file": os.path.basename(exp.path), "lean": h.get("lean"), "prefixes": h.get("prefixes"),
            "modules": len(h.get("modules", [])), "declarations": len(exp.decls),
            "deprecation_aliases": len(exp.aliases)}


def _follow(name, mapping):
    """`name` mapped through `mapping` until it maps no further (a cycle stops it)."""
    seen = {name}
    cur = name
    while cur in mapping:
        nxt = mapping[cur]
        if nxt in seen:
            break
        seen.add(nxt)
        cur = nxt
    return cur


class Resolver:
    """Names of both versions, in the new version's terms. A new statement's names go through the
    new version's deprecation aliases. An old statement's names go through the old version's
    aliases (to the names the old version itself used), then the renames found (inferred from
    identical statements, and members of a renamed type: `Old.mk`, `Old.field` -> `New.mk`,
    `New.field`), then the new version's aliases."""

    def __init__(self, old_aliases, new_aliases):
        self.old_aliases = old_aliases
        self.new_aliases = new_aliases
        self.inferred = {}
        self.types = {}  # old type name -> new type name

    def renamed(self, name):
        if name in self.inferred:
            return self.inferred[name]
        parent, dot, last = name.rpartition(".")
        if dot and parent in self.types:
            return self.types[parent] + "." + last
        return name

    def old(self, name):
        return _follow(self.renamed(_follow(name, self.old_aliases)), self.new_aliases)

    def new(self, name):
        return _follow(name, self.new_aliases)

    __call__ = old


def _statement(decl, resolve=None):
    """The comparable statement of a declaration: its type, and for an inductive type its
    constructors (last name component and type) and a structure's field names, with names resolved
    if asked. The type's own name and its constructors' become placeholders, so a renamed type can
    match its old self."""
    ty, rest = _parts(decl, resolve)
    return trees.key([ty, rest])


def _parts(decl, resolve=None):
    """(the type's tree, [the constructors, the fields]) with names resolved and placeholders."""
    own = {decl.name: "§self"}
    for i, c in enumerate(decl.ctors):
        own[c["name"]] = f"§ctor{i}"

    def r(n):
        if n in own:
            return own[n]
        return resolve(n) if resolve else n
    ctors = [[c["name"].rsplit(".", 1)[-1], trees.rename(c["tree"], r)] for c in decl.ctors]
    return trees.rename(decl.tree, r), [ctors, decl.fields]


def _norm(name):
    return name.rsplit(".", 1)[-1].lower().replace("_", "")


def _similar(a, b):
    """Names close enough that a non-theorem with an identical statement is taken as renamed: the
    same but for case and underscores (`fooBar`, `FooBar`, `foo_bar`; not `foo'`)."""
    return _norm(a) == _norm(b)


def _renames_used(decl, resolve):
    names = trees.constants(decl.tree)
    for c in decl.ctors:
        trees.constants(c["tree"], names)
    return sorted((n, resolve(n)) for n in names if resolve(n) != n)


def compare(old, new):
    """Compare two exports (exports.Export) and return a Result."""
    warnings = []
    for flag, what in (("axioms", "axioms"), ("pp", "pretty-printed statements")):
        if old.header.get(flag, True) is False or new.header.get(flag, True) is False:
            warnings.append(f"an export was made without {what}: "
                            + ("new sorry and axioms are not reported" if flag == "axioms"
                               else "statements are not shown"))
    unerased = sum(1 for exp in (old, new) for d in exp.decls.values() if not d.erased)
    if unerased:
        warnings.append(f"{unerased} statements kept their proofs (the exporter could not erase them): "
                        "a change inside a proof shows as a changed statement")
    new_real = {n for n, d in new.decls.items() if not d.alias_of}
    resolve = Resolver(old.aliases, new.aliases)

    def counterpart(name):
        """The new declaration an old one corresponds to, by name or by renames known so far."""
        if name in new_real:
            return name, ""
        target = resolve.old(name)
        if target != name and target in new_real:
            if name in resolve.inferred:
                return target, "identical statement"
            if name.rpartition(".")[0] in resolve.types:
                return target, "renamed type"
            return target, "deprecation alias"
        if name in new.decls:
            return name, ""
        return None, ""

    def note_type_renames():
        for name, od in old.decls.items():
            if od.ctors and not od.alias_of:
                target, _ = counterpart(name)
                if target is not None and target != name:
                    resolve.types[name] = target

    note_type_renames()
    # Old declarations with no counterpart by name or alias may have been renamed without an alias.
    # Match them to unclaimed new declarations by identical statement (after the renames known so
    # far), one to one; repeat, since each rename can make more statements match.
    while True:
        claimed = set()
        unmatched = []
        for name, od in old.decls.items():
            if od.alias_of:
                continue
            c, _ = counterpart(name)
            if c is None:
                unmatched.append(name)
            else:
                claimed.add(c)
        free = [n for n in new_real if n not in claimed and n not in old.decls]
        new_by_key = {}
        for n in free:
            new_by_key.setdefault(_statement(new.decls[n], resolve.new), []).append(n)
        old_by_key = {}
        for o in unmatched:
            old_by_key.setdefault(_statement(old.decls[o], resolve.old), []).append(o)
        found = {}
        for k, olds in old_by_key.items():
            news = new_by_key.get(k, [])
            if len(olds) != 1 or len(news) != 1:
                continue
            o, n = olds[0], news[0]
            od, nd = old.decls[o], new.decls[n]
            if (od.kind in PROP_KINDS and nd.kind in PROP_KINDS) or _similar(o, n):
                found[o] = n
        found = {o: n for o, n in found.items() if resolve.inferred.get(o) != n}
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
        note_type_renames()

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
        elif _statement(od, resolve.old) == _statement(nd, resolve.new):
            e.status = RENAMED
            e.renames = _renames_used(od, resolve)
            if target != name:
                e.renames = [(name, target)] + [r for r in e.renames if r != (name, target)]
        else:
            e.status = CHANGED
            e.detail = _describe(od, nd, resolve)
            e.renames = _renames_used(od, resolve)
            d = trees.first_difference(trees.rename(od.tree, resolve.old),
                                       trees.rename(nd.tree, resolve.new))
            if d is not None:
                e.first_change = (trees.show(d[1], 80), trees.show(d[2], 80))
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
                  inferred_renames=dict(sorted(resolve.inferred.items())), warnings=warnings)


def _describe(od, nd, resolve):
    if od.kind != nd.kind and (od.ctors or nd.ctors) and len(od.ctors) != len(nd.ctors):
        return (f"was {_article(od.kind)} with {len(od.ctors)} constructors, "
                f"now {_article(nd.kind)} with {len(nd.ctors)}")
    a, b = trees.rename(od.tree, resolve.old), trees.rename(nd.tree, resolve.new)
    if a != b:
        if trees.erase_binder_info(a) == trees.erase_binder_info(b) and \
                _parts(od, resolve.old)[1] == _parts(nd, resolve.new)[1]:
            return "only binder info changed (explicit, implicit or instance arguments)"
        return _where(a, b)
    if od.fields != nd.fields:
        return f"fields changed: {', '.join(od.fields)} -> {', '.join(nd.fields)}"
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
        ta, tb = trees.rename(oc[k]["tree"], resolve.old), trees.rename(nc[k]["tree"], resolve.new)
        if ta != tb:
            return f"constructor {k} changed: " + _where(ta, tb)
    return "constructors reordered"


def _where(a, b):
    d = trees.first_difference(a, b)
    if d is None:
        return ""
    path, x, y = d
    place = "/".join(path) or "top"
    return f"first difference at {place}: {trees.show(x, 120)}  ->  {trees.show(y, 120)}"


def _article(kind):
    return ("an " if kind[:1] in "aeiou" else "a ") + kind
