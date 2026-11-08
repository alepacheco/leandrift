import Tiny.Basic

namespace Tiny

structure Point where
  x : Nat
  y : Nat
  z : Nat

inductive Color
  | red
  | green

instance : Inhabited Point := ⟨⟨0, 0, 0⟩⟩

abbrev Pair := Nat × Nat

def origin : Point := default

theorem origin_x : origin.x = 0 := rfl

end Tiny
