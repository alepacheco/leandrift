"""Operations on the exporter's statement trees (see leandrift/Export.lean for their shape)."""

import json

BINDERS = {"p", "l"}


def key(tree):
    """A canonical string for a tree: equal keys mean structurally equal statements."""
    return json.dumps(tree, separators=(",", ":"), ensure_ascii=False)


def rename(tree, resolve):
    """The tree with every constant name `n` replaced by `resolve(n)`."""
    if not isinstance(tree, list) or not tree:
        return tree
    tag = tree[0]
    if tag == "c":
        return ["c", resolve(tree[1]), tree[2]]
    if tag == "a":
        return ["a", rename(tree[1], resolve), [rename(x, resolve) for x in tree[2]]]
    if tag in BINDERS:
        return [tag, tree[1], rename(tree[2], resolve), rename(tree[3], resolve)]
    if tag == "let":
        return ["let"] + [rename(x, resolve) for x in tree[1:]]
    if tag == "j":
        return ["j", resolve(tree[1]), tree[2], rename(tree[3], resolve)]
    return tree


def constants(tree, out=None):
    """The set of constant names a tree mentions."""
    if out is None:
        out = set()
    if isinstance(tree, list) and tree:
        tag = tree[0]
        if tag == "c":
            out.add(tree[1])
        elif tag == "a":
            constants(tree[1], out)
            for x in tree[2]:
                constants(x, out)
        elif tag in BINDERS:
            constants(tree[2], out)
            constants(tree[3], out)
        elif tag == "let":
            for x in tree[1:]:
                constants(x, out)
        elif tag == "j":
            out.add(tree[1])
            constants(tree[3], out)
    return out


def erase_binder_info(tree):
    if not isinstance(tree, list) or not tree:
        return tree
    tag = tree[0]
    if tag in BINDERS:
        return [tag, "d", erase_binder_info(tree[2]), erase_binder_info(tree[3])]
    if tag == "a":
        return ["a", erase_binder_info(tree[1]), [erase_binder_info(x) for x in tree[2]]]
    if tag == "let":
        return ["let"] + [erase_binder_info(x) for x in tree[1:]]
    if tag == "j":
        return ["j", tree[1], tree[2], erase_binder_info(tree[3])]
    return tree


BRACKETS = {"d": "()", "i": "{}", "s": "⦃⦄", "c": "[]"}


def show(tree, limit=200):
    """A compact one-line rendering of a tree, for pointing at a difference (not Lean syntax)."""
    out = []
    budget = [limit]

    def emit(s):
        if budget[0] > 0:
            out.append(s)
            budget[0] -= len(s)

    def go(t):
        if budget[0] <= 0:
            return
        if not isinstance(t, list) or not t:
            emit(str(t))
            return
        tag = t[0]
        if tag == "c":
            emit(t[1] + (".{" + ",".join(t[2]) + "}" if t[2] else ""))
        elif tag == "b":
            emit(f"#{t[1]}")
        elif tag == "s":
            emit(f"Sort {t[1]}")
        elif tag == "n":
            emit(t[1])
        elif tag == "str":
            emit(json.dumps(t[1], ensure_ascii=False))
        elif tag == "a":
            emit("(")
            go(t[1])
            for x in t[2]:
                emit(" ")
                go(x)
            emit(")")
        elif tag in BINDERS:
            o, c = BRACKETS.get(t[1], "()")
            emit(("∀ " if tag == "p" else "λ ") + o)
            go(t[2])
            emit(c + ", ")
            go(t[3])
        elif tag == "let":
            emit("let ")
            go(t[2])
            emit("; ")
            go(t[3])
        elif tag == "j":
            go(t[3])
            emit(f".{t[2] + 1}")
        else:
            emit(key(t))

    go(tree)
    s = "".join(out)
    return s if len(s) <= limit else s[: limit - 1] + "…"


def first_difference(a, b, path=()):
    """The first place two trees differ: (path, subtree of a, subtree of b), or None if equal."""
    if a == b:
        return None
    if isinstance(a, list) and isinstance(b, list) and a and b and a[0] == b[0]:
        tag = a[0]
        if tag == "a":
            if a[1] != b[1]:
                return first_difference(a[1], b[1], path + ("fn",))
            if len(a[2]) == len(b[2]):
                for i, (x, y) in enumerate(zip(a[2], b[2])):
                    d = first_difference(x, y, path + (f"arg{i}",))
                    if d:
                        return d
        elif tag in BINDERS and a[1] == b[1]:
            d = first_difference(a[2], b[2], path + ("binder",))
            if d:
                return d
            return first_difference(a[3], b[3], path + ("body",))
    return (path, a, b)
