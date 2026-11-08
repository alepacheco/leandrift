namespace Tiny

theorem add_zero' (n : Nat) : n + 0 = n := rfl

theorem zero_add_new (n : Nat) : 0 + n = n := Nat.zero_add n

@[deprecated zero_add_new (since := "2026-11-01")]
theorem zero_add_old (n : Nat) : 0 + n = n := zero_add_new n

theorem mul_one_new (n : Nat) : n * 1 = n := Nat.mul_one n

theorem le_succ' (n : Nat) : n < n + 1 := Nat.lt_succ_self n

theorem two_mul' (n : Nat) : 2 * n = n + n := by sorry

theorem comm (x y : Nat) : x + y = y + x := Nat.add_comm x y

theorem binfo (n : Nat) : n + 0 = n := rfl

universe v in
theorem refl' {β : Sort v} (b : β) : b = b := rfl

def twice (n : Nat) : Nat := 2 * n

@[deprecated twice (since := "2026-11-01")]
def double (n : Nat) : Nat := twice n

theorem double_eq (n : Nat) : twice n = 2 * n := rfl

axiom tiny_ax : 0 = 0

theorem uses_choice : ∃ n : Nat, n = n := ⟨0, tiny_ax ▸ rfl⟩

theorem fresh (n : Nat) : n * 0 = 0 := Nat.mul_zero n

end Tiny
