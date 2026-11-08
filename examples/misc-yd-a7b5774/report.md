# LeanDrift report: misc-yd a7b5774^ -> a7b5774

| | old | new |
|---|---|---|
| Lean | 4.35.0 | 4.36.0-rc1 |
| modules read | 17 | 17 |
| declarations | 260 | 261 |
| declarations depending on `sorryAx` | 28 | 28 |

| statement | declarations |
|---|---|
| same | 259 |
| same after renames | 0 |
| changed | 1 |
| removed | 0 |
| added | 1 |
| newly depending on `sorryAx` | 0 |
| newly depending on another non-standard axiom | 0 |

## Changed statements (1)

### `GenerateLine` (inductive -> def, `MiscYD.Book.SylvesterChvatal`)

was an inductive with 3 constructors, now a def

Old:

```lean
{V : Type u_1} → [MetricSpace V] → Set V → Set V
| basic : ∀ {V : Type u_1} [inst : MetricSpace V] {s : Set V} {x : V}, x ∈ s → GenerateLine s x
| extend_out : ∀ {V : Type u_1} [inst : MetricSpace V] {s : Set V} (u v w : V),
  GenerateLine s u → GenerateLine s v → SBtw.sbtw u v w → GenerateLine s w
| extend_in : ∀ {V : Type u_1} [inst : MetricSpace V] {s : Set V} (u v w : V),
  GenerateLine s u → GenerateLine s v → SBtw.sbtw u w v → GenerateLine s w
```

New:

```lean
{V : Type u_1} → [MetricSpace V] → Set V → Set V
```

## New `sorry` (0)

None.

## New axioms other than Classical.choice, Quot.sound, propext and `sorryAx` (0)

None.

## Same after renames (0)

None.

## Removed (0)

None.

## Added (1)

- `IsGenerated` (inductive, `MiscYD.Book.SylvesterChvatal`)

Statements are compared as Lean elaborated them (binder names and proofs ignored, binder kinds kept), after mapping names through both versions' deprecation aliases, the renames above and the members of renamed types. Definitional equality is not checked yet: a statement reported as changed may still be equivalent.
