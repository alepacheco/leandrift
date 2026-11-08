"""End-to-end: the tiny project of tests/e2e, built and exported with Lean v4.25.0 (old) and
v4.36.0-rc2 (new), then compared. Needs elan (it installs both toolchains on first use); skipped
when `lake` is not on the PATH or LEANDRIFT_E2E=0."""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from leandrift import exports, project  # noqa: E402
from leandrift.diff import ADDED, CHANGED, REMOVED, RENAMED, SAME, compare  # noqa: E402

EXPECTED = {
    # old name: (status, new name)
    "Tiny.add_zero'": (SAME, "Tiny.add_zero'"),
    "Tiny.comm": (SAME, "Tiny.comm"),  # binder names changed only
    "Tiny.refl'": (SAME, "Tiny.refl'"),  # universe parameter renamed only
    "Tiny.two_mul'": (SAME, "Tiny.two_mul'"),  # same statement, proof now sorry
    "Tiny.uses_choice": (SAME, "Tiny.uses_choice"),  # same statement, now uses an axiom
    "Tiny.Color": (SAME, "Tiny.Color"),
    "Tiny.Pair": (SAME, "Tiny.Pair"),
    "Tiny.origin": (SAME, "Tiny.origin"),
    "Tiny.origin_x": (SAME, "Tiny.origin_x"),
    "Tiny.instInhabitedPoint": (SAME, "Tiny.instInhabitedPoint"),
    "Tiny.zero_add_old": (RENAMED, "Tiny.zero_add_new"),  # deprecation alias
    "Tiny.double": (RENAMED, "Tiny.twice"),  # deprecation alias
    "Tiny.double_eq": (RENAMED, "Tiny.double_eq"),  # its statement uses double, now twice
    "Tiny.mul_one_old": (RENAMED, "Tiny.mul_one_new"),  # no alias: matched by statement
    "Tiny.le_succ'": (CHANGED, "Tiny.le_succ'"),  # ≤ became <
    "Tiny.binfo": (CHANGED, "Tiny.binfo"),  # implicit argument became explicit
    "Tiny.Point": (CHANGED, "Tiny.Point"),  # a field was added
    "Tiny.gone": (REMOVED, None),
    "Tiny.fresh": (ADDED, "Tiny.fresh"),
    "Tiny.tiny_ax": (ADDED, "Tiny.tiny_ax"),
}


@unittest.skipUnless(shutil.which("lake") and os.environ.get("LEANDRIFT_E2E", "1") != "0",
                     "needs elan's lake on the PATH (set LEANDRIFT_E2E=0 to skip)")
class TestTinyProject(unittest.TestCase):
    def test_two_toolchains(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            paths = {}
            for side in ("old", "new"):
                src = d / side
                shutil.copytree(ROOT / "tests" / "e2e" / f"tiny-{side}", src)
                project.build(src)
                paths[side] = d / f"{side}.jsonl"
                project.export(src, ["Tiny"], paths[side])
            old, new = exports.load(paths["old"]), exports.load(paths["new"])
            self.assertEqual(old.lean, "4.25.0")
            self.assertEqual(new.lean, "4.36.0-rc2")
            r = compare(old, new)
            got = {(e.old or e.new): (e.status, e.new) for e in r.entries}
            self.assertEqual(got, EXPECTED)
            by_name = {(e.old or e.new): e for e in r.entries}
            self.assertIn("binder info", by_name["Tiny.binfo"].detail)
            self.assertIn("fields changed: x, y -> x, y, z", by_name["Tiny.Point"].detail)
            self.assertEqual([e.new for e in r.new_sorries()], ["Tiny.two_mul'"])
            self.assertEqual(sorted(e.new for e in r.new_nonstandard_axioms()),
                             ["Tiny.tiny_ax", "Tiny.uses_choice"])
            self.assertEqual(r.inferred_renames, {"Tiny.mul_one_old": "Tiny.mul_one_new"})


if __name__ == "__main__":
    unittest.main()
