namespace Tiny

theorem add_zero' (n : Nat) : n + 0 = n := rfl

theorem zero_add_old (n : Nat) : 0 + n = n := Nat.zero_add n

theorem mul_one_old (n : Nat) : n * 1 = n := Nat.mul_one n

theorem le_succ' (n : Nat) : n ≤ n + 1 := Nat.le_succ n

theorem gone (n : Nat) : n = n := rfl

theorem two_mul' (n : Nat) : 2 * n = n + n := by omega

theorem comm (a b : Nat) : a + b = b + a := Nat.add_comm a b

theorem binfo {n : Nat} : n + 0 = n := rfl

universe u in
theorem refl' {α : Sort u} (a : α) : a = a := rfl

def double (n : Nat) : Nat := 2 * n

theorem double_eq (n : Nat) : double n = 2 * n := rfl

theorem uses_choice : ∃ n : Nat, n = n := ⟨0, rfl⟩

end Tiny
