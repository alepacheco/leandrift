# LeanDrift report: PersistentDecomp 7cfd07c^ -> 7cfd07c

| | old | new |
|---|---|---|
| Lean | 4.31.0 | 4.32.0 |
| modules read | 14 | 14 |
| declarations | 160 | 160 |
| declarations depending on `sorryAx` | 75 | 75 |

| statement | declarations |
|---|---|
| same | 151 |
| same after renames | 3 |
| changed | 6 |
| removed | 0 |
| added | 0 |
| newly depending on `sorryAx` | 0 |
| newly depending on another non-standard axiom | 0 |

## Changed statements (6)

Where several changed statements first differ in the same way (often one change upstream, such as a definition or instance that statements elaborate to):

| old | new | statements |
|---|---|---|
| `Monoid.toPow.{0}` | `NPow.toPow.{0}` | 4 |
| `Monoid.toPow.{u1}` | `NPow.toPow.{u1}` | 2 |

### `ExistsFittingn` (theorem, `PersistentDecomp.EndoRingIsLocal`)

first difference at body/body/body/body/body/arg1/body/arg3/arg11/arg3/arg2/fn: Monoid.toPow.{0}  ->  NPow.toPow.{0}

Old:

```lean
∀ (R : Type) [inst : DivisionRing R] (M : ModuleCat R) [Module.Finite R ↑M] (f : ↑M →ₗ[R] ↑M),
  ∃ n, IsCompl (f ^ n).ker (f ^ n).range
```

New:

```lean
∀ (R : Type) [inst : DivisionRing R] (M : ModuleCat R) [Module.Finite R ↑M] (f : ↑M →ₗ[R] ↑M),
  ∃ n, IsCompl (f ^ n).ker (f ^ n).range
```

### `PowEqCompLeft` (theorem, `PersistentDecomp.EndoRingIsLocal`)

first difference at body/body/body/body/body/body/body/arg1/arg3/arg2/fn: Monoid.toPow.{u1}  ->  NPow.toPow.{u1}

Old:

```lean
∀ (C : Type) [inst : CategoryTheory.Category C] (R : Type) [inst_1 : DivisionRing R]
  (F : CategoryTheory.Functor C (ModuleCat R)) (θ : EndRing C R F) (n : ℕ),
  θ ^ (n + 1) = CategoryTheory.CategoryStruct.comp θ (θ ^ n)
```

New:

```lean
∀ (C : Type) [inst : CategoryTheory.Category C] (R : Type) [inst_1 : DivisionRing R]
  (F : CategoryTheory.Functor C (ModuleCat R)) (θ : EndRing C R F) (n : ℕ),
  θ ^ (n + 1) = CategoryTheory.CategoryStruct.comp θ (θ ^ n)
```

### `PowEqCompRight` (theorem, `PersistentDecomp.EndoRingIsLocal`)

first difference at body/body/body/body/body/body/body/arg1/arg6/arg3/arg2/fn: Monoid.toPow.{u1}  ->  NPow.toPow.{u1}

Old:

```lean
∀ (C : Type) [inst : CategoryTheory.Category C] (R : Type) [inst_1 : DivisionRing R]
  (F : CategoryTheory.Functor C (ModuleCat R)) (θ : EndRing C R F) (n : ℕ),
  CategoryTheory.CategoryStruct.comp θ (θ ^ n) = CategoryTheory.CategoryStruct.comp (θ ^ n) θ
```

New:

```lean
∀ (C : Type) [inst : CategoryTheory.Category C] (R : Type) [inst_1 : DivisionRing R]
  (F : CategoryTheory.Functor C (ModuleCat R)) (θ : EndRing C R F) (n : ℕ),
  CategoryTheory.CategoryStruct.comp θ (θ ^ n) = CategoryTheory.CategoryStruct.comp (θ ^ n) θ
```

### `Step2_2` (theorem, `PersistentDecomp.EndoRingIsLocal`)

first difference at body/body/body/body/body/body/body/body/body/body/arg1/arg6/arg6/arg3/arg2/fn: Monoid.toPow.{0}  ->  NPow.toPow.{0}

Old:

```lean
∀ (C : Type) [inst : CategoryTheory.Category C] (R : Type) [inst_1 : DivisionRing R] (X : C) (n : ℕ)
  (Y : C) (α : X ⟶ Y) (M : PtwiseFinitePersMod C R) (η : EndRing C R M.toFunctor),
  CategoryTheory.CategoryStruct.comp (M.map α) ((η ^ n).app Y) =
    CategoryTheory.CategoryStruct.comp ((η ^ n).app X) (M.map α)
```

New:

```lean
∀ (C : Type) [inst : CategoryTheory.Category C] (R : Type) [inst_1 : DivisionRing R] (X : C) (n : ℕ)
  (Y : C) (α : X ⟶ Y) (M : PtwiseFinitePersMod C R) (η : EndRing C R M.toFunctor),
  CategoryTheory.CategoryStruct.comp (M.map α) ((η ^ n).app Y) =
    CategoryTheory.CategoryStruct.comp ((η ^ n).app X) (M.map α)
```

### `Step3_1` (theorem, `PersistentDecomp.EndoRingIsLocal`)

first difference at body/body/body/body/body/body/body/body/body/body/body/binder/arg1/arg6/arg8/arg3/arg2/fn: Monoid.toPow.{0}  ->  NPow.toPow.{0}

Old:

```lean
∀ (C : Type) [inst : CategoryTheory.Category C] (R : Type) [inst_1 : DivisionRing R] (X Y : C)
  (M : PtwiseFinitePersMod C R) (α : X ⟶ Y) (n : ℕ) (ηx : ↑(M.obj X) →ₗ[R] ↑(M.obj X))
  (ηy : ↑(M.obj Y) →ₗ[R] ↑(M.obj Y)),
  CategoryTheory.CategoryStruct.comp (M.map α) (ModuleCat.ofHom (ηy ^ n)) =
      CategoryTheory.CategoryStruct.comp (ModuleCat.ofHom (ηx ^ n)) (M.map α) →
    ∀ (x : ↥(ηx ^ n).ker),
      (CategoryTheory.ConcreteCategory.hom
            (CategoryTheory.CategoryStruct.comp (M.map α) (ModuleCat.ofHom (ηy ^ n))))
          ↑x =
        0
```

New:

```lean
∀ (C : Type) [inst : CategoryTheory.Category C] (R : Type) [inst_1 : DivisionRing R] (X Y : C)
  (M : PtwiseFinitePersMod C R) (α : X ⟶ Y) (n : ℕ) (ηx : ↑(M.obj X) →ₗ[R] ↑(M.obj X))
  (ηy : ↑(M.obj Y) →ₗ[R] ↑(M.obj Y)),
  CategoryTheory.CategoryStruct.comp (M.map α) (ModuleCat.ofHom (ηy ^ n)) =
      CategoryTheory.CategoryStruct.comp (ModuleCat.ofHom (ηx ^ n)) (M.map α) →
    ∀ (x : ↥(ηx ^ n).ker),
      (CategoryTheory.ConcreteCategory.hom
            (CategoryTheory.CategoryStruct.comp (M.map α) (ModuleCat.ofHom (ηy ^ n))))
          ↑x =
        0
```

### `Step3_2` (theorem, `PersistentDecomp.EndoRingIsLocal`)

first difference at body/body/body/body/body/body/body/body/body/body/body/binder/arg1/arg6/arg8/arg3/arg2/fn: Monoid.toPow.{0}  ->  NPow.toPow.{0}

Old:

```lean
∀ (C : Type) [inst : CategoryTheory.Category C] (R : Type) [inst_1 : DivisionRing R] (X Y : C)
  (M : PtwiseFinitePersMod C R) (α : X ⟶ Y) (n : ℕ) (ηx : ↑(M.obj X) →ₗ[R] ↑(M.obj X))
  (ηy : ↑(M.obj Y) →ₗ[R] ↑(M.obj Y)),
  CategoryTheory.CategoryStruct.comp (M.map α) (ModuleCat.ofHom (ηy ^ n)) =
      CategoryTheory.CategoryStruct.comp (ModuleCat.ofHom (ηx ^ n)) (M.map α) →
    ∀ x ∈ (ηx ^ n).range,
      ∃ y, (CategoryTheory.ConcreteCategory.hom (M.map α)) x = y ∧ y ∈ (ηy ^ n).range
```

New:

```lean
∀ (C : Type) [inst : CategoryTheory.Category C] (R : Type) [inst_1 : DivisionRing R] (X Y : C)
  (M : PtwiseFinitePersMod C R) (α : X ⟶ Y) (n : ℕ) (ηx : ↑(M.obj X) →ₗ[R] ↑(M.obj X))
  (ηy : ↑(M.obj Y) →ₗ[R] ↑(M.obj Y)),
  CategoryTheory.CategoryStruct.comp (M.map α) (ModuleCat.ofHom (ηy ^ n)) =
      CategoryTheory.CategoryStruct.comp (ModuleCat.ofHom (ηx ^ n)) (M.map α) →
    ∀ x ∈ (ηx ^ n).range,
      ∃ y, (CategoryTheory.ConcreteCategory.hom (M.map α)) x = y ∧ y ∈ (ηy ^ n).range
```

## New `sorry` (0)

None.

## New axioms other than Classical.choice, Quot.sound, propext and `sorryAx` (0)

None.

## Same after renames (3)

| old | new | matched by | renames in its statement |
|---|---|---|---|
| `IntervalModuleMorphism` | `intervalModuleMorphism` | identical statement |  |
| `IntervalModuleMorphism_comp` | `intervalModuleMorphism_comp` | identical statement (def -> theorem) | `IntervalModuleMorphism` -> `intervalModuleMorphism` |
| `IntervalModuleMorphism_identity` | `intervalModuleMorphism_identity` | identical statement | `IntervalModuleMorphism` -> `intervalModuleMorphism` |

Renames found by identical statement (no deprecation alias): `IntervalModuleMorphism` -> `intervalModuleMorphism`, `IntervalModuleMorphism_comp` -> `intervalModuleMorphism_comp`, `IntervalModuleMorphism_identity` -> `intervalModuleMorphism_identity`

## Removed (0)

None.

## Added (0)

None.

Statements are compared as Lean elaborated them (binder names and proofs ignored, binder kinds kept), after mapping names through both versions' deprecation aliases, the renames above and the members of renamed types. Definitional equality is not checked yet: a statement reported as changed may still be equivalent.
