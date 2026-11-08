# LeanDrift report: cam-combi 34a573b^ -> 34a573b

| | old | new |
|---|---|---|
| Lean | 4.24.0 | 4.25.0 |
| modules read | 25 | 25 |
| declarations | 169 | 169 |
| declarations depending on `sorryAx` | 41 | 41 |

| statement | declarations |
|---|---|
| same | 141 |
| same after renames | 0 |
| changed | 28 |
| removed | 0 |
| added | 0 |
| newly depending on `sorryAx` | 0 |
| newly depending on another non-standard axiom | 0 |

## Changed statements (28)

Where several changed statements first differ in the same way (often one change upstream, such as a definition or instance that statements elaborate to):

| old | new | statements |
|---|---|---|
| `Finset.toSet.{u0}` | `SetLike.coe.{u0,u0}` | 23 |
| `Finset.toSet.{0}` | `SetLike.coe.{0,0}` | 3 |
| `Finset.instMembership.{u0}` | `SetLike.instMembership.{u0,u0}` | 2 |

### `ProbabilityTheory.IsBernoulliSeq.meas` (theorem, `LeanCamCombi.ExtrProbCombi.BernoulliSeq`)

first difference at body/body/body/body/body/body/body/body/body/body/arg1/arg5/arg1/body/arg2/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {α : Type u_1} {Ω : Type u_2} [inst : MeasurableSpace Ω] {X : Ω → Set α}
  {μ : MeasureTheory.Measure Ω} {p : NNReal},
  ProbabilityTheory.IsBernoulliSeq X p μ →
    ∀ [MeasureTheory.IsProbabilityMeasure μ] [inst_2 : Fintype α] (s : Finset α),
      μ {ω | {a | a ∈ X ω} = ↑s} = ↑p ^ s.card * (1 - ↑p) ^ (Fintype.card α - s.card)
```

New:

```lean
∀ {α : Type u_1} {Ω : Type u_2} [inst : MeasurableSpace Ω] {X : Ω → Set α}
  {μ : MeasureTheory.Measure Ω} {p : NNReal},
  ProbabilityTheory.IsBernoulliSeq X p μ →
    ∀ [MeasureTheory.IsProbabilityMeasure μ] [inst_2 : Fintype α] (s : Finset α),
      μ {ω | {a | a ∈ X ω} = ↑s} = ↑p ^ s.card * (1 - ↑p) ^ (Fintype.card α - s.card)
```

### `GraphTheory.ES1.q12` (theorem, `LeanCamCombi.GraphTheory.ExampleSheet1`)

first difference at body/body/body/body/body/arg1/body/arg1/body/arg1/arg1/arg0/body/body/arg2/arg0/arg1/body/arg2/fn: Finset.instMembership.{u0}  ->  SetLike.instMembership.{u0,u0}

Old:

```lean
∀ {α : Type u_2} [inst : DecidableEq α] (G : SimpleGraph α) [inst_1 : DecidableRel G.Adj]
  (s : Finset α),
  ∃ u v,
    Disjoint u v ∧
      u ∪ v = s ∧
        (∀ a ∈ u, Even (Cardinal.mk { x // x ∈ {b ∈ u | G.Adj a b} })) ∧
          ∀ a ∈ v, Even (Cardinal.mk { x // x ∈ {b ∈ v | G.Adj a b} })
```

New:

```lean
∀ {α : Type u_2} [inst : DecidableEq α] (G : SimpleGraph α) [inst_1 : DecidableRel G.Adj]
  (s : Finset α),
  ∃ u v,
    Disjoint u v ∧
      u ∪ v = s ∧
        (∀ a ∈ u, Even (Cardinal.mk ↥({b ∈ u | G.Adj a b}))) ∧
          ∀ a ∈ v, Even (Cardinal.mk ↥({b ∈ v | G.Adj a b}))
```

### `GraphTheory.ES1.q14_part1` (theorem, `LeanCamCombi.GraphTheory.ExampleSheet1`)

first difference at arg1/body/arg0/body/arg3/arg0/arg1/arg3/fn: Finset.toSet.{0}  ->  SetLike.coe.{0,0}

Old:

```lean
∃ r,
  (∀ (A : Finset ℕ), ↑A.card ≤ Cardinal.mk ↑(r.image ↑A)) ∧
    ∀ (f : ℕ → ℕ), Function.Injective f → ∃ n, (n, f n) ∉ r
```

New:

```lean
∃ r,
  (∀ (A : Finset ℕ), ↑A.card ≤ Cardinal.mk ↑(r.image ↑A)) ∧
    ∀ (f : ℕ → ℕ), Function.Injective f → ∃ n, (n, f n) ∉ r
```

### `GraphTheory.ES1.q14_part2` (theorem, `LeanCamCombi.GraphTheory.ExampleSheet1`)

first difference at body/body/body/body/body/body/body/binder/body/arg3/arg0/arg1/arg3/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {α : Type u_2} {β : Type u_3} [inst : DecidableEq β] [Countable α] [Countable β] (r : SetRel α β)
  [inst_3 : (a : α) → Fintype ↑(r.image {a})],
  (∀ (A : Finset α), A.card ≤ Fintype.card ↑(r.image ↑A)) →
    ∃ f, Function.Injective f ∧ ∀ (a : α), (a, f a) ∈ r
```

New:

```lean
∀ {α : Type u_2} {β : Type u_3} [inst : DecidableEq β] [Countable α] [Countable β] (r : SetRel α β)
  [inst_3 : (a : α) → Fintype ↑(r.image {a})],
  (∀ (A : Finset α), A.card ≤ Fintype.card ↑(r.image ↑A)) →
    ∃ f, Function.Injective f ∧ ∀ (a : α), (a, f a) ∈ r
```

### `GraphTheory.ES1.q14_part3` (theorem, `LeanCamCombi.GraphTheory.ExampleSheet1`)

first difference at body/body/body/body/body/binder/body/arg3/arg0/arg1/arg3/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {α : Type u_2} {β : Type u_3} [inst : DecidableEq β] (r : SetRel α β)
  [inst_1 : (a : α) → Fintype ↑(r.image {a})],
  (∀ (A : Finset α), A.card ≤ Fintype.card ↑(r.image ↑A)) →
    ∃ f, Function.Injective f ∧ ∀ (a : α), (a, f a) ∈ r
```

New:

```lean
∀ {α : Type u_2} {β : Type u_3} [inst : DecidableEq β] (r : SetRel α β)
  [inst_1 : (a : α) → Fintype ↑(r.image {a})],
  (∀ (A : Finset α), A.card ≤ Fintype.card ↑(r.image ↑A)) →
    ∃ f, Function.Injective f ∧ ∀ (a : α), (a, f a) ∈ r
```

### `GrowthInGroups.Lecture1.conjecture_1_4` (theorem, `LeanCamCombi.GrowthInGroups.Lecture1`)

first difference at arg1/body/arg1/arg1/body/arg1/body/body/body/body/body/body/body/body/binder/arg1/arg2/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∃ Cᵤ ≥ 0,
  ∃ dᵤ ≥ 0,
    ∀ {G : Type u_2} [inst : Group G] [IsSimpleGroup G] [inst_2 : Fintype G]
      [inst_3 : DecidableEq G] (X : Finset G),
      1 ∈ X →
        X⁻¹ = X →
          Subgroup.closure ↑X = ⊤ →
            ∃ m, ↑m ≤ Cᵤ * Real.log ↑(Fintype.card G) ^ dᵤ ∧ X ^ m = Finset.univ
```

New:

```lean
∃ Cᵤ ≥ 0,
  ∃ dᵤ ≥ 0,
    ∀ {G : Type u_2} [inst : Group G] [IsSimpleGroup G] [inst_2 : Fintype G]
      [inst_3 : DecidableEq G] (X : Finset G),
      1 ∈ X →
        X⁻¹ = X →
          Subgroup.closure ↑X = ⊤ →
            ∃ m, ↑m ≤ Cᵤ * Real.log ↑(Fintype.card G) ^ dᵤ ∧ X ^ m = Finset.univ
```

### `GrowthInGroups.Lecture1.fact_1_10` (theorem, `LeanCamCombi.GrowthInGroups.Lecture1`)

first difference at body/body/body/body/body/arg1/body/body/body/arg0/arg2/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {G : Type u_1} [inst : Group G] [inst_1 : DecidableEq G] {A : Finset G},
  (A * A).card ≤ A.card → ∃ H, ∀ a ∈ A, a • ↑H = ↑A ∧ MulOpposite.op a • ↑H = ↑A
```

New:

```lean
∀ {G : Type u_1} [inst : Group G] [inst_1 : DecidableEq G] {A : Finset G},
  (A * A).card ≤ A.card → ∃ H, ∀ a ∈ A, a • ↑H = ↑A ∧ MulOpposite.op a • ↑H = ↑A
```

### `GrowthInGroups.Lecture1.fact_1_1_1` (theorem, `LeanCamCombi.GrowthInGroups.Lecture1`)

first difference at body/body/body/body/body/body/binder/arg1/arg2/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {G : Type u_1} [inst : Group G] [inst_1 : DecidableEq G] {X : Finset G} [Infinite G],
  1 ∈ X → Subgroup.closure ↑X = ⊤ → ∀ (n : ℕ), n + 1 ≤ (X ^ n).card
```

New:

```lean
∀ {G : Type u_1} [inst : Group G] [inst_1 : DecidableEq G] {X : Finset G} [Infinite G],
  1 ∈ X → Subgroup.closure ↑X = ⊤ → ∀ (n : ℕ), n + 1 ≤ (X ^ n).card
```

### `GrowthInGroups.Lecture1.lemma_1_11` (theorem, `LeanCamCombi.GrowthInGroups.Lecture1`)

first difference at body/body/body/body/body/arg1/body/arg1/body/arg1/body/body/arg0/arg2/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {G : Type u_1} [inst : Group G] [inst_1 : DecidableEq G] {A : Finset G},
  ↑(A * A).card < 3 / 2 * ↑A.card →
    ∃ H x,
      ↑(Fintype.card ↥H) < 3 / 2 * ↑A.card ∧ ∀ a ∈ A, ↑A ⊆ a • ↑H ∧ a • ↑H = MulOpposite.op a • ↑H
```

New:

```lean
∀ {G : Type u_1} [inst : Group G] [inst_1 : DecidableEq G] {A : Finset G},
  ↑(A * A).card < 3 / 2 * ↑A.card →
    ∃ H x,
      ↑(Fintype.card ↥H) < 3 / 2 * ↑A.card ∧ ∀ a ∈ A, ↑A ⊆ a • ↑H ∧ a • ↑H = MulOpposite.op a • ↑H
```

### `GrowthInGroups.Lecture1.proposition_1_7` (theorem, `LeanCamCombi.GrowthInGroups.Lecture1`)

first difference at arg1/body/arg1/body/body/body/arg1/body/arg1/arg1/body/arg2/fn: Finset.toSet.{0}  ->  SetLike.coe.{0,0}

Old:

```lean
∃ ε > 0,
  ∀ (X : Finset (Matrix.SpecialLinearGroup (Fin 2) ℝ)),
    (X ^ 2).card ≤ 1000 * X.card →
      (∀ M ∈ X, ∀ (i j : Fin 2), |↑M i j| ≤ ε) → ∃ A, IsMulCommutative ↥A ∧ ∃ a, ↑X ⊆ ⋃ i, a i • ↑A
```

New:

```lean
∃ ε > 0,
  ∀ (X : Finset (Matrix.SpecialLinearGroup (Fin 2) ℝ)),
    (X ^ 2).card ≤ 1000 * X.card →
      (∀ M ∈ X, ∀ (i j : Fin 2), |↑M i j| ≤ ε) → ∃ A, IsMulCommutative ↥A ∧ ∃ a, ↑X ⊆ ⋃ i, a i • ↑A
```

### `GrowthInGroups.Lecture1.theorem_1_8` (theorem, `LeanCamCombi.GrowthInGroups.Lecture1`)

first difference at body/body/arg1/body/arg1/body/body/body/body/body/arg1/body/arg1/body/arg1/body/arg1/arg0/arg3/arg4/arg4/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {K : ℝ},
  0 ≤ K →
    ∃ C > 0,
      ∀ {G : Type u_2} [inst : Group G] [inst_1 : DecidableEq G] (A : Finset G),
        ↑(A.mulConst A) ≤ K →
          ∃ N D,
            ∃ (_hD : D.Normal),
              upperCentralSeries (↥N ⧸ D) C = ⊤ ∧
                Subtype.val '' ↑D ⊆ (↑A / ↑A) ^ 4 ∧ ∃ a, ↑A ⊆ ⋃ i, a i • ↑N
```

New:

```lean
∀ {K : ℝ},
  0 ≤ K →
    ∃ C > 0,
      ∀ {G : Type u_2} [inst : Group G] [inst_1 : DecidableEq G] (A : Finset G),
        ↑(A.mulConst A) ≤ K →
          ∃ N D,
            ∃ (_hD : D.Normal),
              upperCentralSeries (↥N ⧸ D) C = ⊤ ∧
                Subtype.val '' ↑D ⊆ (↑A / ↑A) ^ 4 ∧ ∃ a, ↑A ⊆ ⋃ i, a i • ↑N
```

### `GrowthInGroups.Lecture1.theorem_1_9` (theorem, `LeanCamCombi.GrowthInGroups.Lecture1`)

first difference at body/arg1/body/arg1/arg1/body/arg1/body/body/body/body/body/binder/arg1/arg2/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {n : ℕ},
  ∃ δ > 0,
    ∃ ε > 0,
      ∀ (k : Type u_2) [inst : Field k] [inst_1 : Fintype k] [inst_2 : DecidableEq k]
        (A : Finset (Matrix.SpecialLinearGroup (Fin n) k)),
        Subgroup.closure ↑A = ⊤ →
          A.card ^ (1 + δ) ≤ (A ^ 3).card ∨
            Fintype.card (Matrix.SpecialLinearGroup (Fin n) k) ^ (1 - ε) ≤ A.card
```

New:

```lean
∀ {n : ℕ},
  ∃ δ > 0,
    ∃ ε > 0,
      ∀ (k : Type u_2) [inst : Field k] [inst_1 : Fintype k] [inst_2 : DecidableEq k]
        (A : Finset (Matrix.SpecialLinearGroup (Fin n) k)),
        Subgroup.closure ↑A = ⊤ →
          A.card ^ (1 + δ) ≤ (A ^ 3).card ∨
            Fintype.card (Matrix.SpecialLinearGroup (Fin n) k) ^ (1 - ε) ≤ A.card
```

### `exists_isApproximateAddSubgroup_of_small_doubling` (theorem, `LeanCamCombi.Mathlib.Combinatorics.Additive.ApproximateSubgroup`)

first difference at body/body/body/body/body/body/body/arg1/body/arg1/arg0/arg3/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {G : Type u_1} [inst : AddGroup G] {K : ℝ} [inst_1 : DecidableEq G] {A : Finset G},
  A.Nonempty →
    ↑(2 • A).card ≤ K * ↑A.card →
      ∃ S ⊆ 2 • (-A + A),
        IsApproximateAddSubgroup (2 ^ 12 * K ^ 36) ↑S ∧
          ↑S.card ≤ 16 * K ^ 12 * ↑A.card ∧
            ∃ a ∈ A, ↑A.card / (2 * K) ≤ ↑(A ∩ (AddOpposite.op a +ᵥ S)).card
```

New:

```lean
∀ {G : Type u_1} [inst : AddGroup G] {K : ℝ} [inst_1 : DecidableEq G] {A : Finset G},
  A.Nonempty →
    ↑(2 • A).card ≤ K * ↑A.card →
      ∃ S ⊆ 2 • (-A + A),
        IsApproximateAddSubgroup (2 ^ 12 * K ^ 36) ↑S ∧
          ↑S.card ≤ 16 * K ^ 12 * ↑A.card ∧
            ∃ a ∈ A, ↑A.card / (2 * K) ≤ ↑(A ∩ (AddOpposite.op a +ᵥ S)).card
```

### `exists_isApproximateSubgroup_of_small_doubling` (theorem, `LeanCamCombi.Mathlib.Combinatorics.Additive.ApproximateSubgroup`)

first difference at body/body/body/body/body/body/body/arg1/body/arg1/arg0/arg3/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {G : Type u_1} [inst : Group G] {K : ℝ} [inst_1 : DecidableEq G] {A : Finset G},
  A.Nonempty →
    ↑(A ^ 2).card ≤ K * ↑A.card →
      ∃ S ⊆ (A⁻¹ * A) ^ 2,
        IsApproximateSubgroup (2 ^ 12 * K ^ 36) ↑S ∧
          ↑S.card ≤ 16 * K ^ 12 * ↑A.card ∧
            ∃ a ∈ A, ↑A.card / (2 * K) ≤ ↑(A ∩ MulOpposite.op a • S).card
```

New:

```lean
∀ {G : Type u_1} [inst : Group G] {K : ℝ} [inst_1 : DecidableEq G] {A : Finset G},
  A.Nonempty →
    ↑(A ^ 2).card ≤ K * ↑A.card →
      ∃ S ⊆ (A⁻¹ * A) ^ 2,
        IsApproximateSubgroup (2 ^ 12 * K ^ 36) ↑S ∧
          ↑S.card ≤ 16 * K ^ 12 * ↑A.card ∧
            ∃ a ∈ A, ↑A.card / (2 * K) ≤ ↑(A ∩ MulOpposite.op a • S).card
```

### `GrowthInGroups.Lecture2.lemma_2_7` (theorem, `LeanCamCombi.GrowthInGroups.Lecture2`)

first difference at body/body/body/body/body/body/body/body/arg3/arg4/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {G : Type u_1} [inst : DecidableEq G] [inst_1 : Group G] {K : ℝ} {A : Finset G},
  1 ∈ A → A⁻¹ = A → ↑(A ^ 3).card ≤ K * ↑A.card → IsApproximateSubgroup (K ^ 3) (↑A ^ 2)
```

New:

```lean
∀ {G : Type u_1} [inst : DecidableEq G] [inst_1 : Group G] {K : ℝ} {A : Finset G},
  1 ∈ A → A⁻¹ = A → ↑(A ^ 3).card ≤ K * ↑A.card → IsApproximateSubgroup (K ^ 3) (↑A ^ 2)
```

### `GrowthInGroups.Lecture3.lemma_3_1` (theorem, `LeanCamCombi.GrowthInGroups.Lecture3`)

first difference at body/body/body/body/body/body/body/body/arg3/arg4/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {G : Type u_1} [inst : Group G] {K : ℝ} [inst_1 : DecidableEq G] {A : Finset G},
  1 ∈ A → A⁻¹ = A → ↑(A ^ 3).card ≤ K * ↑A.card → IsApproximateSubgroup (K ^ 3) (↑A ^ 2)
```

New:

```lean
∀ {G : Type u_1} [inst : Group G] {K : ℝ} [inst_1 : DecidableEq G] {A : Finset G},
  1 ∈ A → A⁻¹ = A → ↑(A ^ 3).card ≤ K * ↑A.card → IsApproximateSubgroup (K ^ 3) (↑A ^ 2)
```

### `GrowthInGroups.Lecture3.proposition_3_3` (theorem, `LeanCamCombi.GrowthInGroups.Lecture3`)

first difference at body/body/body/body/body/body/body/arg1/body/arg1/arg0/arg3/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {G : Type u_1} [inst : Group G] {K : ℝ} [inst_1 : DecidableEq G] {A : Finset G},
  A.Nonempty →
    ↑(A ^ 2).card ≤ K * ↑A.card →
      ∃ S ⊆ (A⁻¹ * A) ^ 2,
        IsApproximateSubgroup (2 ^ 12 * K ^ 36) ↑S ∧
          ↑S.card ≤ 16 * K ^ 12 * ↑A.card ∧
            ∃ a ∈ A, ↑A.card / (2 * K) ≤ ↑(A ∩ MulOpposite.op a • S).card
```

New:

```lean
∀ {G : Type u_1} [inst : Group G] {K : ℝ} [inst_1 : DecidableEq G] {A : Finset G},
  A.Nonempty →
    ↑(A ^ 2).card ≤ K * ↑A.card →
      ∃ S ⊆ (A⁻¹ * A) ^ 2,
        IsApproximateSubgroup (2 ^ 12 * K ^ 36) ↑S ∧
          ↑S.card ≤ 16 * K ^ 12 * ↑A.card ∧
            ∃ a ∈ A, ↑A.card / (2 * K) ≤ ↑(A ∩ MulOpposite.op a • S).card
```

### `GrowthInGroups.Lecture3.proposition_3_6_1` (theorem, `LeanCamCombi.GrowthInGroups.Lecture3`)

first difference at body/body/body/body/body/body/body/body/body/body/body/body/arg1/body/arg1/arg3/arg4/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {G : Type u_1} [inst : Group G] {A B : Set G} {K L : ℝ} {m n : ℕ},
  IsApproximateSubgroup K A →
    IsApproximateSubgroup L B →
      2 ≤ m →
        2 ≤ n → ∃ F, ↑F.card ≤ K ^ (m - 1) * L ^ (n - 1) ∧ A ^ m ∩ B ^ n ⊆ ↑F * (A ^ 2 ∩ B ^ 2)
```

New:

```lean
∀ {G : Type u_1} [inst : Group G] {A B : Set G} {K L : ℝ} {m n : ℕ},
  IsApproximateSubgroup K A →
    IsApproximateSubgroup L B →
      2 ≤ m →
        2 ≤ n → ∃ F, ↑F.card ≤ K ^ (m - 1) * L ^ (n - 1) ∧ A ^ m ∩ B ^ n ⊆ ↑F * (A ^ 2 ∩ B ^ 2)
```

### `GrowthInGroups.Lecture3.corollary_4_3` (theorem, `LeanCamCombi.GrowthInGroups.Lecture4`)

first difference at body/body/arg1/body/arg1/body/body/arg1/body/arg1/body/arg1/body/arg1/arg3/arg4/fn: Finset.toSet.{0}  ->  SetLike.coe.{0,0}

Old:

```lean
∀ (K C₀ : ℝ),
  ∃ C > 0,
    ∀ (A : Set (Matrix.SpecialLinearGroup (Fin 2) ℂ)),
      IsApproximateSubgroup K A →
        ∃ Z, ∃ (_ : ∀ x ∈ Z, ∀ y ∈ Z, Commute x y), ∃ F, F.card ≤ C ∧ A ⊆ ↑F * ↑Z
```

New:

```lean
∀ (K C₀ : ℝ),
  ∃ C > 0,
    ∀ (A : Set (Matrix.SpecialLinearGroup (Fin 2) ℂ)),
      IsApproximateSubgroup K A →
        ∃ Z, ∃ (_ : ∀ x ∈ Z, ∀ y ∈ Z, Commute x y), ∃ F, F.card ≤ C ∧ A ⊆ ↑F * ↑Z
```

### `GrowthInGroups.Lecture3.lemma_4_2` (theorem, `LeanCamCombi.GrowthInGroups.Lecture4`)

first difference at body/body/body/body/body/body/arg1/body/body/binder/arg3/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {C₀ : ℝ},
  ↑(Fintype.card n) < C₀ →
    ∀ (K : ℝ),
      ∃ δ,
        ∀ (A : Finset (GL n ℂ)),
          IsApproximateSubgroup K ↑A →
            (∀ a ∈ A, ‖↑a‖ ≤ C₀) → ∃ γ ∈ A ^ 2, δ * ↑A.card ≤ ↑{x ∈ A ^ 4 | Commute γ x}.card
```

New:

```lean
∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {C₀ : ℝ},
  ↑(Fintype.card n) < C₀ →
    ∀ (K : ℝ),
      ∃ δ,
        ∀ (A : Finset (GL n ℂ)),
          IsApproximateSubgroup K ↑A →
            (∀ a ∈ A, ‖↑a‖ ≤ C₀) → ∃ γ ∈ A ^ 2, δ * ↑A.card ≤ ↑{x ∈ A ^ 4 | Commute γ x}.card
```

### `GrowthInGroups.Lecture3.theorem_4_4` (theorem, `LeanCamCombi.GrowthInGroups.Lecture4`)

first difference at body/body/arg1/body/arg1/body/body/body/body/body/arg1/body/arg1/body/arg1/body/arg1/body/arg1/arg1/arg3/arg4/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {K : ℝ},
  0 ≤ K →
    ∃ C > 0,
      ∀ {G : Type u_2} [inst : Group G] [DecidableEq G] (A : Set G),
        IsApproximateSubgroup K A →
          ∃ H N,
            ∃ (_hD : N.Normal),
              ∃ F, upperCentralSeries (↥H ⧸ N) C = ⊤ ∧ Subtype.val '' ↑N ⊆ (A / A) ^ 4 ∧ A ⊆ ↑F * ↑H
```

New:

```lean
∀ {K : ℝ},
  0 ≤ K →
    ∃ C > 0,
      ∀ {G : Type u_2} [inst : Group G] [DecidableEq G] (A : Set G),
        IsApproximateSubgroup K A →
          ∃ H N,
            ∃ (_hD : N.Normal),
              ∃ F, upperCentralSeries (↥H ⧸ N) C = ⊤ ∧ Subtype.val '' ↑N ⊆ (A / A) ^ 4 ∧ A ⊆ ↑F * ↑H
```

### `GrowthInGroups.Lecture3.theorem_4_5` (theorem, `LeanCamCombi.GrowthInGroups.Lecture4`)

first difference at body/body/body/body/body/body/binder/arg1/arg3/arg2/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {C : ℝ} {G : Type u_2} [inst : Group G] [inst_1 : DecidableEq G] {S : Finset G},
  S⁻¹ = S →
    ↑(Subgroup.closure ↑S) = Set.univ →
      ∀ {d : ℕ}, (∀ (n : ℕ), ↑(S ^ n).card ≤ C * ↑n ^ d) → Group.IsVirtuallyNilpotent G
```

New:

```lean
∀ {C : ℝ} {G : Type u_2} [inst : Group G] [inst_1 : DecidableEq G] {S : Finset G},
  S⁻¹ = S →
    ↑(Subgroup.closure ↑S) = Set.univ →
      ∀ {d : ℕ}, (∀ (n : ℕ), ↑(S ^ n).card ≤ C * ↑n ^ d) → Group.IsVirtuallyNilpotent G
```

### `Numbering.prefixedEquiv` (def, `LeanCamCombi.PlainCombi.KatonaCircle`)

first difference at body/body/body/body/arg0/arg1/body/arg2/fn: Finset.instMembership.{u0}  ->  SetLike.instMembership.{u0,u0}

Old:

```lean
{α : Type u_1} →
  [inst : Fintype α] →
    [inst_1 : DecidableEq α] →
      (s : Finset α) →
        { x // x ∈ Numbering.prefixed s } ≃ Numbering { x // x ∈ s } × Numbering { x // x ∈ sᶜ }
```

New:

```lean
{α : Type u_1} →
  [inst : Fintype α] →
    [inst_1 : DecidableEq α] →
      (s : Finset α) → ↥(Numbering.prefixed s) ≃ Numbering ↥s × Numbering ↥sᶜ
```

### `Finset.exists_littlewood_offord_partition` (theorem, `LeanCamCombi.PlainCombi.LittlewoodOfford`)

first difference at body/body/body/body/body/body/body/body/body/body/arg1/body/arg1/arg1/body/body/arg1/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {ι : Type u_1} {E : Type u_2} [inst : NormedAddCommGroup E] [NormedSpace ℝ E] {s : Finset ι}
  {f : ι → E} {r : ℝ} [inst_2 : DecidableEq ι],
  0 < r →
    (∀ i ∈ s, r ≤ ‖f i‖) →
      ∃ P,
        P.parts.card = s.card.choose (s.card / 2) ∧
          (∀ 𝒜 ∈ P.parts, ∀ t ∈ 𝒜, t ⊆ s) ∧
            ∀ 𝒜 ∈ P.parts, (↑𝒜).Pairwise fun u v => r ≤ Dist.dist (∑ i ∈ u, f i) (∑ i ∈ v, f i)
```

New:

```lean
∀ {ι : Type u_1} {E : Type u_2} [inst : NormedAddCommGroup E] [NormedSpace ℝ E] {s : Finset ι}
  {f : ι → E} {r : ℝ} [inst_2 : DecidableEq ι],
  0 < r →
    (∀ i ∈ s, r ≤ ‖f i‖) →
      ∃ P,
        P.parts.card = s.card.choose (s.card / 2) ∧
          (∀ 𝒜 ∈ P.parts, ∀ t ∈ 𝒜, t ⊆ s) ∧
            ∀ 𝒜 ∈ P.parts, (↑𝒜).Pairwise fun u v => r ≤ Dist.dist (∑ i ∈ u, f i) (∑ i ∈ v, f i)
```

### `LYM_inequality` (theorem, `LeanCamCombi.PlainCombi.ProbLYM`)

first difference at body/body/body/binder/arg2/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {α : Type u_1} [inst : Fintype α] {𝒜 : Finset (Finset α)},
  IsAntichain (fun x1 x2 => x1 ⊆ x2) ↑𝒜 → ∑ s ∈ 𝒜, (↑((Fintype.card α).choose s.card))⁻¹ ≤ 1
```

New:

```lean
∀ {α : Type u_1} [inst : Fintype α] {𝒜 : Finset (Finset α)},
  IsAntichain (fun x1 x2 => x1 ⊆ x2) ↑𝒜 → ∑ s ∈ 𝒜, (↑((Fintype.card α).choose s.card))⁻¹ ≤ 1
```

### `Finset.IsLowerSet.certificator_eq_inter` (theorem, `LeanCamCombi.PlainCombi.VanDenBergKesten`)

first difference at body/body/body/body/binder/arg2/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {α : Type u_1} [inst : BooleanAlgebra α] (s t : Finset α),
  IsLowerSet ↑s → IsUpperSet ↑t → s.certificator t = s ∩ t
```

New:

```lean
∀ {α : Type u_1} [inst : BooleanAlgebra α] (s t : Finset α),
  IsLowerSet ↑s → IsUpperSet ↑t → s.certificator t = s ∩ t
```

### `Finset.IsUpperSet.certificator_eq_disjSups` (theorem, `LeanCamCombi.PlainCombi.VanDenBergKesten`)

first difference at body/body/body/body/binder/arg2/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {α : Type u_1} [inst : BooleanAlgebra α] (s t : Finset α),
  IsUpperSet ↑s → IsUpperSet ↑t → s.certificator t = s.disjSups t
```

New:

```lean
∀ {α : Type u_1} [inst : BooleanAlgebra α] (s t : Finset α),
  IsUpperSet ↑s → IsUpperSet ↑t → s.certificator t = s.disjSups t
```

### `Finset.IsUpperSet.certificator_eq_inter` (theorem, `LeanCamCombi.PlainCombi.VanDenBergKesten`)

first difference at body/body/body/body/binder/arg2/fn: Finset.toSet.{u0}  ->  SetLike.coe.{u0,u0}

Old:

```lean
∀ {α : Type u_1} [inst : BooleanAlgebra α] (s t : Finset α),
  IsUpperSet ↑s → IsLowerSet ↑t → s.certificator t = s ∩ t
```

New:

```lean
∀ {α : Type u_1} [inst : BooleanAlgebra α] (s t : Finset α),
  IsUpperSet ↑s → IsLowerSet ↑t → s.certificator t = s ∩ t
```

## New `sorry` (0)

None.

## New axioms other than Classical.choice, Quot.sound, propext and `sorryAx` (0)

None.

## Same after renames (0)

None.

## Removed (0)

None.

## Added (0)

None.

Statements are compared as Lean elaborated them (binder names ignored, binder kinds kept), after mapping names through the new version's deprecation aliases and the renames above. Definitional equality is not checked yet: a statement reported as changed may still be equivalent.
