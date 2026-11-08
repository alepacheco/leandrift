/-
LeanDrift exporter: writes every declaration of the given module prefixes, as the project's own
Lean and Lake environment elaborated it, to a JSON Lines file.

Run it inside a built Lake project, so that its toolchain and its `.olean` files are the ones used:

    lake env lean --run /path/to/leandrift/leandrift/Export.lean --prefix MyProject -o export.jsonl

Each line is one JSON object with a `type`:
* `header`: the format version, the Lean version, the prefixes, the modules read, and whether
  statements were pretty-printed (`pp`) and axioms collected (`axioms`);
* `decl`: one declaration of those modules: `name`, `kind`, `module`, `levels` (its number of universe
  parameters), `tree` (its type as a structural tree, see below), `pp` (its type pretty-printed),
  `axioms` (the axioms it depends on, `sorryAx` included), for an inductive type its `ctors`, for a
  structure or class its `fields` (in order), and `deprecated` if it is deprecated;
* `alias`: a deprecation of the environment (`old` -> `new`), from the `deprecated` attribute,
  across every imported module, with `alias: true` when `old` is defined as `new` itself (so a
  statement may use either name and mean the same).

The tree keeps what Lean's kernel compares and drops what it ignores: binder names, metadata, and
proofs (any subterm whose type is a proposition becomes ["proof"]; `autoParam T tac` becomes `T`).
  ["c", name, [levels]]   constant              ["b", i]               bound variable (de Bruijn index)
  ["s", level]            sort                  ["a", fn, [args]]      application
  ["p", bi, dom, body]    pi (forall)           ["l", bi, dom, body]   lambda
  ["let", type, val, body]                      ["n", "123"] / ["str", s]  literals
  ["j", struct, idx, e]   projection            ["proof"]              a proof
`bi` is "d" (default), "i" (implicit), "s" (strict implicit) or "c" (instance). Levels are strings in
normal form, universe parameters by position ("u0", "u1"), so renaming a universe changes nothing.

It keeps to a small part of Lean's meta API so that it runs on toolchains a year apart.
-/
import Lean

open Lean Meta

namespace LeanDrift

def formatVersion : Nat := 1

def nameStr (n : Name) : String := n.toString (escape := false)

/-- The constant standing for an erased proof inside a statement. -/
def proofName : Name := `_leandrift_proof

/-! ### Statement trees -/

/-- The universe parameters `ps` renamed by position: `u0`, `u1`, ... -/
def positional (ps : List Name) : List Level :=
  (List.range ps.length).map fun i => Level.param (Name.mkSimple s!"u{i}")

partial def levelStr : Level → String
  | .zero => "0"
  | l@(.succ _) =>
    let (b, k) := peel l 0
    match b with
    | .zero => toString k
    | _ => s!"{levelStr b}+{k}"
  | .max a b => s!"max({levelStr a},{levelStr b})"
  | .imax a b => s!"imax({levelStr a},{levelStr b})"
  | .param n => nameStr n
  | .mvar _ => "?m"
where
  peel : Level → Nat → Level × Nat
    | .succ l, k => peel l (k + 1)
    | l, k => (l, k)

/-- A level, its parameters renamed by position before it is normalized. -/
def lvl (ps : List Name) (u : Level) : Json :=
  Json.str (levelStr (u.instantiateParams ps (positional ps)).normalize)

def biStr : BinderInfo → String
  | .default => "d"
  | .implicit => "i"
  | .strictImplicit => "s"
  | .instImplicit => "c"

def tag (t : String) (xs : Array Json) : Json := Json.arr (#[Json.str t] ++ xs)

partial def tree (ps : List Name) : Expr → Json
  | .bvar i => tag "b" #[toJson i]
  | .sort u => tag "s" #[lvl ps u]
  | .const n us =>
    if n == proofName then tag "proof" #[]
    else tag "c" #[Json.str (nameStr n), Json.arr (us.toArray.map (lvl ps))]
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

/-- The type with every proof replaced by `proofName` and `autoParam T tac` by `T`. -/
def eraseProofs (e : Expr) : MetaM Expr :=
  transform e (pre := fun e => do
    if e.isAppOfArity ``autoParam 2 then
      return .visit e.appFn!.appArg!
    match e with
    | .app .. | .const .. | .fvar .. | .lam .. | .proj .. | .letE .. =>
      if ← isProof e then return .done (mkConst proofName) else return .continue
    | _ => return .continue)

/-! ### Which declarations are exported -/

/-- Suffixes of what Lean generates for an inductive type, a constructor, or a definition. -/
def inductiveAux : List String :=
  ["below", "brecOn", "binductionOn", "ibelow", "casesOn", "recOn", "noConfusion",
   "noConfusionType", "ctorIdx", "toCtorIdx", "ctorElim", "ctorElimType"]
def ctorAux : List String := ["inj", "injEq", "sizeOf_spec", "elim", "noConfusion", "noConfusionType"]
def defAux : List String :=
  ["eq_def", "eq_unfold", "induct", "induct_unfolding", "mutual_induct", "fun_cases", "congr_simp",
   "splitter"]

def numbered (s pre : String) : Bool :=
  s.startsWith pre && s.length > pre.length && (s.drop pre.length).all Char.isDigit

/-- A name Lean generated for its parent declaration (judged by the parent's kind). -/
def isGenerated (env : Environment) : Name → Bool
  | .str p s =>
    match env.find? p with
    | some (.inductInfo _) => inductiveAux.contains s
    | some (.ctorInfo _) => ctorAux.contains s
    | some (.defnInfo _) | some (.thmInfo _) | some (.opaqueInfo _) =>
      defAux.contains s || numbered s "eq_" || numbered s "match_" || numbered s "proof_"
    | _ => false
  | _ => false

def skip (env : Environment) (n : Name) (ci : ConstantInfo) : Bool :=
  n.isInternal || ci.isUnsafe || isGenerated env n || isAuxRecursor env n || isNoConfusion env n ||
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

/-- The constant a declaration is defined as, if its value is just that constant (an alias). -/
def aliasTarget? (ci : ConstantInfo) : Option Name :=
  let v? : Option Expr := match ci with
    | .defnInfo d => some d.value
    | .thmInfo t => some t.value
    | .opaqueInfo o => some o.value
    | _ => none
  match v?.map Expr.eta with
  | some (.const n _) => some n
  | _ => none

/-! ### Axioms, memoized over the whole run

An inductive type, its constructors and its recursors form one node (they refer to each other);
every other constant is its own node. The dependency graph of safe constants is then acyclic.
Like `#print axioms`, an axiom counts itself and what its type uses. -/

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
  | some (.axiomInfo v) => (#[k], v.type.getUsedConstants)
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

/-! ### Running MetaM: pretty-printing and proof erasure -/

def ppOptions : Options :=
  ({} : Options) |>.setBool `pp.fullNames true |>.setBool `pp.universes false

def runMeta (env : Environment) (x : MetaM α) : IO α := do
  let ctx : Core.Context := { fileName := "<leandrift>", fileMap := default, options := ppOptions,
                              maxHeartbeats := 0 }
  let st : Core.State := { env }
  let (a, _) ← x.toIO ctx st
  return a

def pp (env : Environment) (e : Expr) : IO String := do
  try
    let fmt ← runMeta env (ppExpr e)
    return fmt.pretty 100
  catch ex =>
    return s!"<could not pretty-print: {ex}>"

/-- The statement's tree, its proofs erased (kept as they are if erasing fails). -/
def statementTree (env : Environment) (ps : List Name) (e : Expr) : IO Json := do
  let e' ← try runMeta env (eraseProofs e) catch _ => pure e
  return tree ps e'

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

def deprecation (env : Environment) (n : Name) (ci : ConstantInfo) (d : Linter.DeprecationEntry) :
    List (String × Json) := Id.run do
  let mut df : List (String × Json) := []
  if let some nn := d.newName? then
    df := df ++ [("new", Json.str (nameStr nn)), ("alias", Json.bool (aliasTarget? ci == some nn))]
  if let some s := d.since? then df := df ++ [("since", Json.str s)]
  let _ := env; let _ := n
  return df

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
    ("prefixes", jsonNames args.prefixes), ("modules", jsonNames mods),
    ("pp", Json.bool !args.noPP), ("axioms", Json.bool !args.noAxioms)]
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
         ("tree", ← statementTree env ps ci.type)]
      unless args.noPP do fields := fields ++ [("pp", Json.str (← pp env ci.type))]
      unless args.noAxioms do
        let ax ← axiomsOf env memo n
        fields := fields ++ [("axioms", jsonNames (ax.qsort (fun a b => a.toString < b.toString)))]
      if let .inductInfo ii := ci then
        let mut ctors : Array Json := #[]
        for c in ii.ctors do
          if let some cc := env.find? c then
            let mut cf : List (String × Json) :=
              [("name", Json.str (nameStr c)), ("tree", ← statementTree env ps cc.type)]
            unless args.noPP do cf := cf ++ [("pp", Json.str (← pp env cc.type))]
            ctors := ctors.push (Json.mkObj cf)
        fields := fields ++ [("ctors", Json.arr ctors)]
        if isStructure env n then
          fields := fields ++ [("fields", jsonNames (getStructureFields env n))]
      if let some d := Linter.deprecatedAttr.getParam? env n then
        fields := fields ++ [("deprecated", Json.mkObj (deprecation env n ci d))]
      h.putStrLn (Json.mkObj fields).compress
      count := count + 1
  -- the deprecations of the whole environment: the rename map for the comparison
  let mut aliases := 0
  for idx in [0:env.header.moduleNames.size] do
    for n in env.header.moduleData[idx]!.constNames do
      if let some d := Linter.deprecatedAttr.getParam? env n then
        if d.newName?.isSome then
          let some ci := env.find? n | continue
          let af : List (String × Json) :=
            [("type", Json.str "alias"), ("old", Json.str (nameStr n))] ++ deprecation env n ci d
          h.putStrLn (Json.mkObj af).compress
          aliases := aliases + 1
  h.flush
  IO.eprintln s!"leandrift: {count} declarations, {aliases} deprecations with a replacement"
  return 0
