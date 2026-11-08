"""Unit tests of the comparison, on small exports written here."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from leandrift import exports, trees  # noqa: E402
from leandrift.cli import main  # noqa: E402
from leandrift.diff import ADDED, CHANGED, REMOVED, RENAMED, SAME, compare  # noqa: E402
from leandrift.report import markdown  # noqa: E402

NAT = ["c", "Nat", []]


def const(n):
    return ["c", n, []]


def app(f, *args):
    return ["a", f, list(args)]


def pi(dom, body, bi="d"):
    return ["p", bi, dom, body]


def eq(a, b):
    return app(["c", "Eq", ["1"]], NAT, a, b)


def b(i):
    return ["b", i]


def decl(name, tree, kind="theorem", axioms=(), ctors=(), deprecated=None, module="P.Basic", pp=None):
    d = {"type": "decl", "name": name, "kind": kind, "module": module, "levels": 0, "tree": tree,
         "pp": pp if pp is not None else trees.show(tree), "axioms": list(axioms)}
    if ctors:
        d["ctors"] = [{"name": n, "tree": t, "pp": trees.show(t)} for n, t in ctors]
    if deprecated:
        d["deprecated"] = deprecated
    return d


def alias(old, new):
    return {"type": "alias", "old": old, "new": new}


class Exports:
    """Writes two exports to a temporary directory."""

    def __init__(self, old, new):
        self.dir = tempfile.TemporaryDirectory()
        self.old = self._write("old.jsonl", "4.25.0", old)
        self.new = self._write("new.jsonl", "4.36.0", new)

    def _write(self, name, lean, records):
        path = os.path.join(self.dir.name, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "header", "format": 1, "lean": lean, "prefixes": ["P"],
                                "modules": ["P", "P.Basic"]}) + "\n")
            for r in records:
                f.write(json.dumps(r) + "\n")
        return path

    def result(self):
        return compare(exports.load(self.old), exports.load(self.new))

    def close(self):
        self.dir.cleanup()


def run(old, new):
    ex = Exports(old, new)
    try:
        r = ex.result()
    finally:
        ex.close()
    return r, {(e.old or e.new): e for e in r.entries}


# n + 0 = n, n ≤ n + 1 and n < n + 1, as trees over one bound Nat
ADD_ZERO = pi(NAT, eq(app(const("HAdd.hAdd"), b(0), const("zero")), b(0)))
LE_SUCC = pi(NAT, app(const("LE.le"), b(0), app(const("Nat.succ"), b(0))))
LT_SUCC = pi(NAT, app(const("LT.lt"), b(0), app(const("Nat.succ"), b(0))))


class TestCompare(unittest.TestCase):
    def test_same(self):
        r, e = run([decl("P.a", ADD_ZERO)], [decl("P.a", ADD_ZERO)])
        self.assertEqual(e["P.a"].status, SAME)
        self.assertEqual(r.counts()[SAME], 1)

    def test_changed_shows_first_difference(self):
        _, e = run([decl("P.a", LE_SUCC)], [decl("P.a", LT_SUCC)])
        self.assertEqual(e["P.a"].status, CHANGED)
        self.assertIn("LE.le", e["P.a"].detail)
        self.assertIn("LT.lt", e["P.a"].detail)

    def test_binder_info_only(self):
        _, e = run([decl("P.a", pi(NAT, eq(b(0), b(0)), bi="i"))], [decl("P.a", pi(NAT, eq(b(0), b(0))))])
        self.assertEqual(e["P.a"].status, CHANGED)
        self.assertIn("binder info", e["P.a"].detail)

    def test_removed_and_added(self):
        _, e = run([decl("P.a", ADD_ZERO)], [decl("P.b", LT_SUCC)])
        self.assertEqual(e["P.a"].status, REMOVED)
        self.assertEqual(e["P.b"].status, ADDED)

    def test_rename_through_deprecation_alias(self):
        # P.old became P.new; the new version keeps P.old as a deprecated alias
        _, e = run([decl("P.old", ADD_ZERO)],
                   [decl("P.new", ADD_ZERO), decl("P.old", ADD_ZERO, deprecated={"new": "P.new"}),
                    alias("P.old", "P.new")])
        self.assertEqual(e["P.old"].status, RENAMED)
        self.assertEqual(e["P.old"].new, "P.new")
        self.assertEqual(e["P.old"].via, "deprecation alias")
        self.assertNotIn("P.new", {x.new for x in e.values() if x.status == ADDED})

    def test_statement_using_a_renamed_constant(self):
        # Mathlib renamed Foo.bar to Foo.baz (alias in the new environment, outside the project)
        old_t = pi(NAT, app(const("Foo.bar"), b(0)))
        new_t = pi(NAT, app(const("Foo.baz"), b(0)))
        _, e = run([decl("P.a", old_t)], [decl("P.a", new_t), alias("Foo.bar", "Foo.baz")])
        self.assertEqual(e["P.a"].status, RENAMED)
        self.assertEqual(e["P.a"].renames, [("Foo.bar", "Foo.baz")])

    def test_deprecated_name_still_used_on_both_sides(self):
        # the new statement still uses the deprecated name: same after renames, not changed
        t = pi(NAT, app(const("Foo.bar"), b(0)))
        _, e = run([decl("P.a", t)], [decl("P.a", t), alias("Foo.bar", "Foo.baz")])
        self.assertIn(e["P.a"].status, (SAME, RENAMED))

    def test_alias_chain(self):
        old_t = pi(NAT, app(const("A"), b(0)))
        new_t = pi(NAT, app(const("C"), b(0)))
        _, e = run([decl("P.a", old_t)], [decl("P.a", new_t), alias("A", "B"), alias("B", "C")])
        self.assertEqual(e["P.a"].status, RENAMED)

    def test_alias_cycle_terminates(self):
        t = pi(NAT, app(const("A"), b(0)))
        _, e = run([decl("P.a", t)], [decl("P.a", t), alias("A", "B"), alias("B", "A")])
        self.assertIn(e["P.a"].status, (SAME, RENAMED, CHANGED))

    def test_theorem_renamed_without_alias(self):
        _, e = run([decl("P.mul_one_old", ADD_ZERO)], [decl("P.mul_one_new", ADD_ZERO)])
        self.assertEqual(e["P.mul_one_old"].status, RENAMED)
        self.assertEqual(e["P.mul_one_old"].via, "identical statement")

    def test_ambiguous_statement_match_is_not_a_rename(self):
        _, e = run([decl("P.x", ADD_ZERO)], [decl("P.y", ADD_ZERO), decl("P.z", ADD_ZERO)])
        self.assertEqual(e["P.x"].status, REMOVED)
        self.assertEqual(e["P.y"].status, ADDED)

    def test_defs_need_similar_names_to_match(self):
        fn = pi(NAT, NAT)
        _, e = run([decl("P.double", fn, kind="def")], [decl("P.square", fn, kind="def")])
        self.assertEqual(e["P.double"].status, REMOVED)
        _, e = run([decl("P.IntervalMorphism", fn, kind="def")],
                   [decl("P.intervalMorphism", fn, kind="def")])
        self.assertEqual(e["P.IntervalMorphism"].status, RENAMED)

    def test_renames_found_one_after_another(self):
        # a def renamed without alias, and a lemma about it renamed too: the lemma only matches
        # once the def's rename is known
        fn = pi(NAT, NAT)
        old_l = pi(NAT, eq(app(const("P.Morph"), b(0)), b(0)))
        new_l = pi(NAT, eq(app(const("P.morph"), b(0)), b(0)))
        r, e = run([decl("P.Morph", fn, kind="def"), decl("P.Morph_id", old_l, kind="def")],
                   [decl("P.morph", fn, kind="def"), decl("P.morph_id", new_l, kind="theorem")])
        self.assertEqual(e["P.Morph"].status, RENAMED)
        self.assertEqual(e["P.Morph_id"].status, RENAMED)
        self.assertEqual(e["P.Morph_id"].old_kind, "def")
        self.assertEqual(e["P.Morph_id"].kind, "theorem")
        self.assertEqual(r.inferred_renames, {"P.Morph": "P.morph", "P.Morph_id": "P.morph_id"})

    def test_constructor_change(self):
        ty = ["s", "1"]
        old = decl("P.Point", ty, kind="structure", ctors=[("P.Point.mk", pi(NAT, const("P.Point")))])
        new = decl("P.Point", ty, kind="structure",
                   ctors=[("P.Point.mk", pi(NAT, pi(NAT, const("P.Point"))))])
        _, e = run([old], [new])
        self.assertEqual(e["P.Point"].status, CHANGED)
        self.assertIn("constructor mk", e["P.Point"].detail)

    def test_inductive_became_def(self):
        ty = pi(NAT, ["s", "1"])
        old = decl("P.Gen", ty, kind="inductive", ctors=[("P.Gen.basic", pi(NAT, app(const("P.Gen"), b(0))))])
        new = decl("P.Gen", ty, kind="def")
        _, e = run([old], [new])
        self.assertEqual(e["P.Gen"].status, CHANGED)
        self.assertIn("inductive", e["P.Gen"].detail)

    def test_new_sorry_and_axioms(self):
        r, e = run([decl("P.a", ADD_ZERO, axioms=["propext"]), decl("P.b", LE_SUCC)],
                   [decl("P.a", ADD_ZERO, axioms=["propext", "sorryAx"]),
                    decl("P.b", LE_SUCC, axioms=["P.my_axiom", "Classical.choice"]),
                    decl("P.c", LT_SUCC, axioms=["sorryAx"])])
        self.assertTrue(e["P.a"].sorry)
        self.assertEqual(e["P.a"].status, SAME)
        self.assertEqual([x.new for x in r.new_sorries()], ["P.a", "P.c"])
        self.assertEqual([x.new for x in r.new_nonstandard_axioms()], ["P.b"])
        self.assertFalse(e["P.b"].sorry)
        self.assertEqual(r.sorry_counts(), (0, 2))

    def test_reports(self):
        r, _ = run([decl("P.a", LE_SUCC, pp="∀ n, n ≤ n + 1"), decl("P.gone", ADD_ZERO)],
                   [decl("P.a", LT_SUCC, pp="∀ n, n < n + 1")])
        md = markdown(r)
        self.assertIn("## Changed statements (1)", md)
        self.assertIn("∀ n, n < n + 1", md)
        self.assertIn("## Removed (1)", md)
        j = json.loads(json.dumps(r.to_json()))
        self.assertEqual(j["summary"][CHANGED], 1)
        self.assertEqual(j["summary"][REMOVED], 1)


class TestLoad(unittest.TestCase):
    def test_header_required(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.jsonl")
            with open(p, "w") as f:
                f.write(json.dumps(decl("P.a", ADD_ZERO)) + "\n")
            with self.assertRaises(ValueError):
                exports.load(p)

    def test_unknown_format(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.jsonl")
            with open(p, "w") as f:
                f.write(json.dumps({"type": "header", "format": 99}) + "\n")
            with self.assertRaises(ValueError):
                exports.load(p)


class TestTrees(unittest.TestCase):
    def test_rename_and_constants(self):
        t = pi(NAT, app(const("A"), b(0), ["j", "S", 0, const("B")]))
        self.assertEqual(trees.constants(t), {"Nat", "A", "S", "B"})
        r = trees.rename(t, lambda n: {"A": "X"}.get(n, n))
        self.assertEqual(trees.constants(r), {"Nat", "X", "S", "B"})

    def test_show_is_bounded(self):
        t = NAT
        for _ in range(200):
            t = pi(NAT, t)
        self.assertLessEqual(len(trees.show(t, 50)), 50)

    def test_first_difference(self):
        self.assertIsNone(trees.first_difference(LE_SUCC, LE_SUCC))
        path, x, y = trees.first_difference(LE_SUCC, LT_SUCC)
        self.assertEqual(path, ("body", "fn"))


class TestCli(unittest.TestCase):
    def test_diff_writes_reports(self):
        ex = Exports([decl("P.a", LE_SUCC)], [decl("P.a", LT_SUCC)])
        try:
            md = os.path.join(ex.dir.name, "r.md")
            js = os.path.join(ex.dir.name, "r.json")
            self.assertEqual(main(["diff", ex.old, ex.new, "--md", md, "--json", js]), 0)
            self.assertEqual(main(["diff", ex.old, ex.new, "--md", md, "--fail-on-change"]), 1)
            with open(js) as f:
                self.assertEqual(json.load(f)["summary"]["changed"], 1)
        finally:
            ex.close()


if __name__ == "__main__":
    unittest.main()
