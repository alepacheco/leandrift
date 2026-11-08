/-
LeanDrift exporter: writes every declaration of the given module prefixes, as the project's own
Lean and Lake environment elaborated it, to a JSON Lines file.

Run it inside a built Lake project, so that its toolchain and its `.olean` files are the ones used:

    lake env lean --run /path/to/leandrift/exporter/Export.lean --prefix MyProject -o export.jsonl

Each line is one JSON object with a `type`:
* `header`: the format version, the Lean version, the prefixes and the modules read;
* `decl`: one declaration of those modules: `name`, `kind`, `module`, `levels` (its number of universe
  parameters), `tree` (its type as a structural tree, see below), `pp` (its type pretty-printed),
  `axioms` (the axioms it depends on, `sorryAx` included), and for an inductive type its `ctors`;
* `alias`: a deprecation alias of the environment (`old` -> `new`), from the `deprecated` attribute,
  across every imported module, for the rename map.

The tree keeps what Lean's kernel compares and drops what it ignores: binder names and metadata.
  ["c", name, [levels]]   constant              ["b", i]               bound variable (de Bruijn index)
  ["s", level]            sort                  ["a", fn, [args]]      application
  ["p", bi, dom, body]    pi (forall)           ["l", bi, dom, body]   lambda
  ["let", type, val, body]                      ["n", "123"] / ["str", s]  literals
  ["j", struct, idx, e]   projection
`bi` is "d" (default), "i" (implicit), "s" (strict implicit) or "c" (instance). Levels are strings in
normal form, universe parameters by position ("u0", "u1"), so renaming a universe changes nothing.

It keeps to a small part of Lean's meta API so that it runs on toolchains a year apart.
-/
import Lean

open Lean Meta

namespace LeanDrift

def formatVersion : Nat := 1

def nameStr (n : Name) : String := n.toString (escape := false)

def indexOf (ps : List Name) (n : Name) : Option Nat :=
  go ps 0
where
  go : List Name → Nat → Option Nat
    | [], _ => none
    | p :: ps, i => if p == n then some i else go ps (i + 1)

partial def levelStr (ps : List Name) : Level → String
  | .zero => "0"
  | l@(.succ _) =>
    let (b, k) := peel l 0
    match b with
    | .zero => toString k
    | _ => s!"{levelStr ps b}+{k}"
  | .max a b => s!"max({levelStr ps a},{levelStr ps b})"
  | .imax a b => s!"imax({levelStr ps a},{levelStr ps b})"
  | .param n =>
    match indexOf ps n with
    | some i => s!"u{i}"
    | none => s!"?{nameStr n}"
  | .mvar _ => "?m"
where
  peel : Level → Nat → Level × Nat
    | .succ l, k => peel l (k + 1)
    | l, k => (l, k)

def lvl (ps : List Name) (u : Level) : Json := Json.str (levelStr ps u.normalize)

def biStr : BinderInfo → String
  | .default => "d"
  | .implicit => "i"
  | .strictImplicit => "s"
  | .instImplicit => "c"

def tag (t : String) (xs : Array Json) : Json := Json.arr (#[Json.str t] ++ xs)

partial def tree (ps : List Name) : Expr → Json
  | .bvar i => tag "b" #[toJson i]
  | .sort u => tag "s" #[lvl ps u]
  | .const n us => tag "c" #[Json.str (nameStr n), Json.arr (us.toArray.map (lvl ps))]
  | e@(.app ..) =>
    let args := e.getAppArgs
    tag "a" #[tree ps e.getAppFn, Json.arr (args.map (tree ps))]
  | .lam _ t b bi => tag "l" #[Json.str (biStr bi), tree ps t, tree ps b]
  | .forallE _ t b bi => tag "p" #[Json.str (biStr bi), tree ps t, tree ps b]
  | .letE _ t v b _ => tag "let" #[tree ps t, tree ps v, tree ps b]
  | .lit (.natVal n) => tag "n" #[Json.str (toString n)]
  | .lit (.strVal s) => tag "str" #[Json.str s]
  | .mdata _ e => tree ps e
  | .proj s i e => tag "j" #[Json.str (nameStr s), toJson i, tree ps e]
  | .fvar id => tag "f" #[Json.str (nameStr id.name)]
  | .mvar _ => tag "m" #[]

/-! ### Which declarations are exported -/

/-- Names Lean generates for its own use, which carry no statement of their own. -/
def generatedSuffixes : List String :=
  ["below", "brecOn", "binductionOn", "ibelow", "casesOn", "recOn", "rec", "noConfusion",
   "noConfusionType", "sizeOf_spec", "inj", "injEq", "ctorIdx", "toCtorIdx", "ctorElim",
   "ctorElimType", "eq_def", "eq_unfold", "induct", "induct_unfolding", "mutual_induct",
   "fun_cases", "match_1", "proof_1"]

def isGeneratedName (n : Name) : Bool :=
  match n with
  | .str _ s =>
    generatedSuffixes.contains s || (s.startsWith "eq_" && (s.drop 3).all Char.isDigit) ||
      (s.startsWith "match_" && (s.drop 6).all Char.isDigit) ||
      (s.startsWith "proof_" && (s.drop 6).all Char.isDigit)
  | _ => false

def skip (env : Environment) (n : Name) (ci : ConstantInfo) : Bool :=
  n.isInternal || ci.isUnsafe || isGeneratedName n || isAuxRecursor env n || isNoConfusion env n ||
    isMatcherCore env n || env.isProjectionFn n ||
    (match ci with
     | .ctorInfo _ | .recInfo _ | .quotInfo _ => true
     | _ => false)

def kindOf (env : Environment) (n : Name) : ConstantInfo → String
  | .thmInfo _ => if isInstanceCore env n then "instance" else "theorem"
  | .axiomInfo _ => "axiom"
  | .opaqueInfo _ => if isInstanceCore env n then "instance" else "opaque"
  | .quotInfo _ => "quot"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"
  | .inductInfo _ =>
    if isClass env n then "class" else if isStructure env n then "structure" else "inductive"
  | .defnInfo d =>
    if isInstanceCore env n then "instance" else if d.hints.isAbbrev then "abbrev" else "def"

/-! ### Axioms, memoized over the whole run

An inductive type, its constructors and its recursors form one node (they refer to each other);
every other constant is its own node. The dependency graph of safe constants is then acyclic. -/

def groupKey (env : Environment) (n : Name) : Name :=
  match env.find? n with
  | some (.ctorInfo c) =>
    match env.find? c.induct with
    | some (.inductInfo i) => i.all.headD c.induct
    | _ => c.induct
  | some (.recInfo r) => r.all.headD n
  | some (.inductInfo i) => i.all.headD n
  | _ => n

def usedIn (env : Environment) (k : Name) : Array Name × Array Name := Id.run do
  -- (the axioms the node itself is, the constants it uses)
  match env.find? k with
  | some (.axiomInfo _) => (#[k], #[])
  | some (.defnInfo v) => (#[], v.type.getUsedConstants ++ v.value.getUsedConstants)
  | some (.thmInfo v) => (#[], v.type.getUsedConstants ++ v.value.getUsedConstants)
  | some (.opaqueInfo v) => (#[], v.type.getUsedConstants ++ v.value.getUsedConstants)
  | some (.inductInfo i) =>
    let mut cs : Array Name := #[]
    for t in i.all do
      if let some (.inductInfo ti) := env.find? t then
        cs := cs ++ ti.type.getUsedConstants
        for c in ti.ctors do
          if let some ci := env.find? c then cs := cs ++ ci.type.getUsedConstants
    return (#[], cs)
  | some (.recInfo r) => (#[], r.type.getUsedConstants)
  | some (.ctorInfo c) => (#[], c.type.getUsedConstants)
  | _ => (#[], #[])

def union (a b : Array Name) : Array Name :=
  b.foldl (fun acc x => if acc.contains x then acc else acc.push x) a

/-- The axioms `root` depends on, as `#print axioms` lists them; `memo` is shared across calls. -/
def axiomsOf (env : Environment) (memo : IO.Ref (Std.HashMap Name (Array Name))) (root : Name) :
    IO (Array Name) := do
  let r := groupKey env root
  if let some a := (← memo.get)[r]? then return a
  -- iterative post-order walk: (node, its dependencies once expanded)
  let mut stack : Array (Name × Option (Array Name × Array Name)) := #[(r, none)]
  let mut active : NameSet := {}
  let mut cycle := false
  while !stack.isEmpty do
    let (k, info) := stack.back!
    stack := stack.pop
    match info with
    | some (own, deps) =>
      let m ← memo.get
      let mut acc := own
      for d in deps do
        match m[d]? with
        | some ax => acc := union acc ax
        | none => cycle := true
      memo.modify (·.insert k acc)
      active := active.erase k
    | none =>
      if (← memo.get).contains k then continue
      if active.contains k then
        cycle := true
        continue
      let (own, used) := usedIn env k
      let deps := (used.map (groupKey env)).foldl
        (fun acc d => if d == k || acc.contains d then acc else acc.push d) #[]
      active := active.insert k
      stack := stack.push (k, some (own, deps))
      let m ← memo.get
      for d in deps do
        unless m.contains d do stack := stack.push (d, none)
  if cycle then
    throw <| IO.userError s!"dependency cycle while collecting the axioms of {root}"
  return (← memo.get)[r]?.getD #[]

/-! ### Pretty-printing -/

def ppOptions : Options :=
  ({} : Options) |>.setBool `pp.fullNames true |>.setBool `pp.universes false

def pp (env : Environment) (e : Expr) : IO String := do
  let ctx : Core.Context := { fileName := "<leandrift>", fileMap := default, options := ppOptions,
                              maxHeartbeats := 0 }
  let st : Core.State := { env }
  try
    let (fmt, _) ← (ppExpr e).toIO ctx st
    return fmt.pretty 100
  catch ex =>
    return s!"<could not pretty-print: {ex}>"

/-! ### Module discovery -/

/-- The modules under `dir` named by `pre` (the module itself and everything below it). -/
partial def modulesUnder (dir : System.FilePath) (pre : Name) : IO (Array Name) := do
  let rel := pre.components.foldl (fun p c => p / nameStr c) dir
  let mut out := #[]
  if ← (rel.addExtension "olean").pathExists then out := out.push pre
  if ← rel.isDir then
    for entry in ← rel.readDir do
      let p := entry.path
      if ← p.isDir then
        out := out ++ (← modulesUnder dir (pre.str entry.fileName))
      else if p.extension == some "olean" then
        let stem := p.fileStem.getD ""
        if !(← (rel / stem).isDir) then out := out.push (pre.str stem)
  return out

def discover (prefixes : Array Name) : IO (Array Name) := do
  let sp ← searchPathRef.get
  let mut mods : Array Name := #[]
  for dir in sp do
    for pre in prefixes do
      for m in ← modulesUnder dir pre do
        unless mods.contains m do mods := mods.push m
  return mods.qsort (fun a b => a.toString < b.toString)

/-! ### Main -/

structure Args where
  prefixes : Array Name := #[]
  modules : Array Name := #[]
  out : Option System.FilePath := none
  noPP : Bool := false
  noAxioms : Bool := false

def usage : String :=
  "usage: lake env lean --run Export.lean --prefix <Module> [--prefix ...] [--module <Module> ...] " ++
  "[-o out.jsonl] [--no-pp] [--no-axioms]\n" ++
  "  --prefix P   export the declarations of the modules P and P.* (imports them all, unless --module)\n" ++
  "  --module M   import M (and what it imports) instead of every module under the prefixes"

partial def parseArgs : List String → Args → Except String Args
  | [], a => .ok a
  | "--prefix" :: p :: rest, a => parseArgs rest { a with prefixes := a.prefixes.push p.toName }
  | "--module" :: m :: rest, a => parseArgs rest { a with modules := a.modules.push m.toName }
  | "-o" :: f :: rest, a => parseArgs rest { a with out := some f }
  | "--no-pp" :: rest, a => parseArgs rest { a with noPP := true }
  | "--no-axioms" :: rest, a => parseArgs rest { a with noAxioms := true }
  | x :: _, _ => .error s!"unknown argument: {x}\n{usage}"

def jsonNames (ns : Array Name) : Json := Json.arr (ns.map (Json.str ∘ nameStr))

end LeanDrift

open LeanDrift in
unsafe def main (argv : List String) : IO UInt32 := do
  let args ← match parseArgs argv {} with
    | .ok a => pure a
    | .error e => IO.eprintln e; return 2
  if args.prefixes.isEmpty then
    IO.eprintln usage
    return 2
  initSearchPath (← findSysroot)
  enableInitializersExecution
  let mods ← if args.modules.isEmpty then discover args.prefixes else pure args.modules
  if mods.isEmpty then
    IO.eprintln s!"no built module under {args.prefixes.toList} on the search path: run `lake build` first"
    return 1
  IO.eprintln s!"leandrift: importing {mods.size} modules"
  let env ← importModules (mods.map fun m => { module := m }) {} (trustLevel := 1024) (loadExts := true)
  let h ← match args.out with
    | some f => pure (IO.FS.Stream.ofHandle (← IO.FS.Handle.mk f .write))
    | none => IO.getStdout
  let header := Json.mkObj [("type", "header"), ("format", toJson formatVersion),
    ("lean", Json.str Lean.versionString), ("githash", Json.str Lean.githash),
    ("prefixes", jsonNames args.prefixes), ("modules", jsonNames mods)]
  h.putStrLn header.compress
  let memo ← IO.mkRef ({} : Std.HashMap Name (Array Name))
  let mut count := 0
  for idx in [0:env.header.moduleNames.size] do
    let modName := env.header.moduleNames[idx]!
    unless args.prefixes.any (·.isPrefixOf modName) do continue
    let names := env.header.moduleData[idx]!.constNames.qsort (fun a b => a.toString < b.toString)
    for n in names do
      let some ci := env.find? n | continue
      if skip env n ci then continue
      let ps := ci.levelParams
      let mut fields : List (String × Json) :=
        [("type", "decl"), ("name", Json.str (nameStr n)), ("kind", Json.str (kindOf env n ci)),
         ("module", Json.str (nameStr modName)), ("levels", toJson ps.length),
         ("tree", tree ps ci.type)]
      unless args.noPP do fields := fields ++ [("pp", Json.str (← pp env ci.type))]
      unless args.noAxioms do
        let ax ← axiomsOf env memo n
        fields := fields ++ [("axioms", jsonNames (ax.qsort (fun a b => a.toString < b.toString)))]
      if let .inductInfo ii := ci then
        let mut ctors : Array Json := #[]
        for c in ii.ctors do
          if let some cc := env.find? c then
            let mut cf : List (String × Json) := [("name", Json.str (nameStr c)), ("tree", tree ps cc.type)]
            unless args.noPP do cf := cf ++ [("pp", Json.str (← pp env cc.type))]
            ctors := ctors.push (Json.mkObj cf)
        fields := fields ++ [("ctors", Json.arr ctors)]
      if let some d := Linter.deprecatedAttr.getParam? env n then
        let mut df : List (String × Json) := []
        if let some nn := d.newName? then df := df ++ [("new", Json.str (nameStr nn))]
        if let some s := d.since? then df := df ++ [("since", Json.str s)]
        fields := fields ++ [("deprecated", Json.mkObj df)]
      h.putStrLn (Json.mkObj fields).compress
      count := count + 1
  -- the deprecation aliases of the whole environment: the rename map for the comparison
  let mut aliases := 0
  for idx in [0:env.header.moduleNames.size] do
    for n in env.header.moduleData[idx]!.constNames do
      if let some d := Linter.deprecatedAttr.getParam? env n then
        if let some nn := d.newName? then
          let mut af : List (String × Json) := [("type", "alias"), ("old", Json.str (nameStr n)),
            ("new", Json.str (nameStr nn))]
          if let some s := d.since? then af := af ++ [("since", Json.str s)]
          h.putStrLn (Json.mkObj af).compress
          aliases := aliases + 1
  h.flush
  IO.eprintln s!"leandrift: {count} declarations, {aliases} deprecation aliases"
  return 0
