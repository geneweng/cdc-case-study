# Global minimum failure with cyclic edge connectivity five

Research date: **6 October 2026**.

**Cyclic five-connectivity does not make a globally minimum color class suitable for fiber repair.** A simple 130-vertex cubic graph has minimum color multiplicity three and a minimizing flow whose seven incident fibers all fail. The graph has no cyclic edge cut of size below five and contains no Petersen four-pole.

A twelve-edge circuit switch makes its three-edge minimum class suitable while preserving the entire seven-entry color-size vector. A 101-edge circuit switch then constructs a five-layer cover. Both the circuit distance and the fiber distance to a successful flow are exactly two, and the minimum remains three throughout.

This closes the cyclically five-edge-connected possibility left open in the [preceding checkpoint](petersen-free-minimum-obstruction.md). It also makes the [two-edge repair guarantee](matching-terminal-flow.md) sharp even when the specified class is globally minimum and the graph has the stronger connectivity. The general five-cycle double cover conjecture remains unproved; the example has an explicit cover.

## 1. Statement and scope

For a nowhere-zero F₂³-flow f, let Mₐ=f⁻¹(a), m(f)=minₐ≠₀|Mₐ|, and μ(G)=min_f m(f). A matching is **suitable** when it is the intersection of two binary cycles, which may be disconnected even subgraphs.

**Certified theorem.** There exist G and f such that:

1. G is simple and cubic, with 130 vertices, 195 edges, girth five, and cyclic edge connectivity exactly five.
2. Every color of every nowhere-zero three-bit flow on G occurs at least three times, and f attains μ(G)=3.
3. Each of f's seven color matchings has an odd unmatched component and is therefore unsuitable.
4. All three plane-mark tests fail in each of its seven incident coordinate planes.
5. Two legal circuit switches produce a successful five-label lift while remaining at minimum three.

The [complete fiber criterion](matching-fiber-repair.md) combines items 3 and 4: no successful state exists anywhere in an initial incident fiber. Item 5 proves exact distance two.

Global minimality is essential to the question being tested. The earlier three-edge Petersen matching already shows that cyclic five-connectivity cannot guarantee suitability for an arbitrary specified three-edge class. That class was not globally minimum. The present example removes that distinction.

## 2. The local ingredient and its attribution

The construction uses the 41-vertex five-pole Y₁ from Section 3 of [Mattiolo, Negrini and Pagani, *Cyclically 5-edge-connected snarks with resistance 2 and flow resistance n*, v1](https://arxiv.org/html/2604.22501v1). Its smaller pieces M,N,Z and their port connections are recorded explicitly in our certificate. This local ingredient is credited to that paper; the outer assembly and the flow/repair certificates below were constructed for this checkpoint.

We independently check the needed local property rather than relying on the paper's global connectivity or flow-resistance theorem. Two different enumeration methods give:

| Local piece | Internal vertices | Internal edges | Binary flows, including ports | Nowhere-zero two-bit flows |
|---|---:|---:|---:|---:|
| M | 7 | 8 | 64 | 36 |
| N | 9 | 11 | 128 | 42 |
| Z | 17 | 23 | 2,048 | 72 |

Every piece has five ports. In the saved port order, the enumerations verify these boundary facts:

- M: its first pair or its second pair has equal values.
- N: its first two values differ.
- Z: its first pair agrees, and its final three values are all distinct.

Y₁ joins two Z pieces through M. The port identifications would force both of M's pairs to have different values. The resulting incompatibility can also be checked directly: all **11,664 triples of local boundary patterns** fail at least one joining equation. Thus Y₁ admits no zero-free two-bit flow. The constructor uses binary cycle spaces; the verifier uses proper-edge-coloring search and checks the joining edges separately.

For the rest of this report write Y=Y₁. Its internal vertices are numbered 0,…,40, and its five port vertices, named (α,β,γ,δ,ε), are

\[
(0,4,17,21,40).
\]

Y has 59 internal edges. All edge lists and port maps are in the [certificate](cyclic_five_minimum_obstruction.json).

## 3. An outer assembly with a forced matching obstruction

Take three disjoint copies Yᵢ, for i∈{0,1,2}, with vertex numbers shifted by 41i. Add seven vertices:

\[
v=123,\qquad x_0=124,\ x_1=125,\ x_2=126,
\qquad b=127,\ c=128,\ d=129.
\]

For each i, with indices modulo three, connect

\[
\epsilon_i x_i,\qquad \alpha_{i+1}x_i,\qquad x_i v,
\qquad \beta_i b,\qquad \gamma_i c,\qquad \delta_i d.
\tag{1}
\]

Each port is used once and every new vertex has degree three. The graph has 3·41+7=130 vertices and 3·59+18=195 edges.

The cross-region connection αᵢ₊₁xᵢ is deliberate. Attaching αᵢ and εᵢ to the same xᵢ would enclose Yᵢ∪{xᵢ} behind a four-edge cut. The actual assembly passes the complete small-cut audit below.

### A general zero-counting observation

Suppose a cubic graph contains q uncolorable multipoles whose charged edge sets—internal edges plus their boundary edges—are pairwise disjoint. Restrict any two-bit flow to each multipole. Every restriction must contain a zero; otherwise it would give a proper three-edge-coloring there. The full flow therefore has at least q zero edges.

For a nowhere-zero three-bit flow and a nonzero color a, project to F₂³/⟨a⟩. The zero set of this two-bit flow is precisely Mₐ. Consequently every color has at least q edges.

Here each Yᵢ has a charged set of 59+5=64 edges. The three sets are disjoint: every boundary edge connects a region to an added vertex, and no edge directly joins two regions. They force **|Mₐ|≥3 for every color of every nowhere-zero flow**.

The supplied initial flow has color sizes

\[
(43,41,40,3,23,22,23),
\]

so μ(G)=3. This lower bound is proved by the local incompatibility and disjointness argument, independently of the SAT search used to discover the flow.

Its minimum class is exactly

\[
M_4=\{\epsilon_0x_0,\epsilon_1x_1,\epsilon_2x_2\}
=\{(40,124),(81,125),(122,126)\}.
\tag{2}
\]

All three neighbors of v=123 are endpoints of this matching, while v itself is unmatched. Thus {123} is an odd component of G−V(M₄), immediately excluding suitability of this globally minimum class.

## 4. The full graph really has cyclic edge connectivity five

A fundamental cycle basis has dimension 195−130+1=66. An edge set is a cut if and only if its incidence vector is orthogonal to every basis cycle.

The constructor groups pairs of edge columns by their XOR to find small cuts. The independent verifier builds a different fundamental basis and enumerates all three- and four-edge subsets directly.

| Check | Exhaustive result |
|---|---|
| One- and two-edge cuts | None: all 195 columns are nonzero and distinct |
| 1,216,865 triples | Exactly 130 cuts, all single-vertex boundaries |
| 58,409,520 quadruples | Exactly 195 cuts, all boundaries of adjacent vertex pairs |
| Five-edge witness | The boundary of the first 41-vertex region separates two connected subgraphs containing circuits |

Hence there is no cyclic cut of size at most four, and cyclic edge connectivity is exactly five. Separate shortest-cycle computations give girth five.

There is also **no Petersen four-pole**. Its eight internal vertices in a cubic graph would have a four-edge boundary. Every four-edge cut here isolates exactly two adjacent vertices, or their complement of size 128. In a connected graph, two vertex sets with the same boundary differ only by complementation. An eight-vertex side is therefore impossible.

## 5. All seven incident fibers fail

The minimum-class obstruction is part of a fully blocked state, not merely a bad choice of target color.

| Color | Matching size | Order of the certified odd component in G−V(Mₐ) |
|---|---:|---:|
| 1 | 43 | 5 |
| 2 | 41 | 11 |
| 3 | 40 | 17 |
| 4 | 3 | 1 |
| 5 | 23 | 1 |
| 6 | 22 | 1 |
| 7 | 23 | 1 |

The exact vertex sets are saved and independently checked to be connected components of the unmatched induced graph. Each odd component excludes the candidate even subgraph needed for an intersection pair. The singleton witnesses for colors 4,…,7 are vertices 123,78,40,81 respectively.

The certificate also supplies 21 paired cuts, covering all three possible first coordinates in each incident plane. With the notation of the [paired-cut theorem](fiber-cut-obstructions.md), each satisfies

\[
\delta(A)\subseteq F,\qquad
\delta(X)\setminus S=\delta(A)\cap y,\qquad
|\delta(X)\cap S|\equiv1\pmod2,
\qquad S=E(G)\setminus(F\cup y).
\]

These identities are checked directly; the verifier does not rerun the constructor's elimination method. They exclude every plane mark. Together with the seven odd-component certificates, they exclude success throughout every initial coordinate fiber.

## 6. An exact two-switch repair at the optimum

First add 6 on the twelve-edge circuit

\[
(82,84,87,90,95,92,116,118,122,126,123,125,82).
\]

In the saved edge order its indices are

```text
119, 123, 129, 133, 138, 165, 167, 173, 184, 185, 189, 191.
```

The color-4 matching replaces edge 189=(122,126) by edge 138=(87,90). Its new edge-index set is {138,177,183}. The unmatched obstruction at 123 disappears, and the new matching is suitable.

The supplied intersection pair, encoded as edge masks, is

```text
F = 9093334202154902477696747075051056032113828337972704771665
t = 12594718827481672415870838694324089607298511120473127911424.
```

Both sets are even and their intersection is the new matching. For the functional ℓ=4, F differs from the intermediate ℓ-coordinate on one 101-edge circuit. Adding 4 on that circuit reaches F, with the two coordinates annihilating 4 fixed. The fourth coordinate w=t+y+z and the established five-label decoding give a cover of every edge exactly twice.

| Stage | Sizes of colors 1,…,7 | Minimum |
|---|---|---:|
| Initial | 43, 41, 40, 3, 23, 22, 23 | 3 |
| After the twelve-edge switch | 43, 41, 40, 3, 23, 22, 23 | 3 |
| After the 101-edge switch | 47, 39, 39, 3, 19, 24, 24 | 3 |

No initial incident fiber has a successful state, so at least two fiber rounds, and hence at least two actual switches, are required. The displayed sequence attains both bounds.

The first step changes matching geometry without changing any color-class size. This shows that those two states cannot be distinguished by their size vector. It does **not** prove that the initial vector is optimal for some stronger lexicographic objective, or exclude a different repair route selected by such an objective.

## 7. What remains of the minimization approach

The progression of counterexamples is now:

| Graph | Global minimum | Girth | Cyclic edge connectivity | Initial incident fibers |
|---|---:|---:|---:|---|
| Previous Petersen-block example | 6 | 5 | 4 | All blocked |
| Previous flower-block example | 6 | 6 | 4 | All blocked |
| Present three-region example | 3 | 5 | 5 | All blocked |

Thus cardinality alone fails after excluding Petersen four-poles and cyclic four-edge cuts, already at the smallest class size beyond the two-edge theorem. Stronger connectivity did not turn the existing argument into an existence proof.

The viable question is now how to choose or reach a favorable minimizer. The example itself has one: its final flow is successful and still globally minimum. A secondary objective based on matching/cut structure, or a theorem guaranteeing a suitable neutral sequence, remains possible. None is proved here.

The construction still contains uncolorable five-poles behind cyclic five-edge cuts. It does not settle the cyclically six-edge-connected case or establish that every possible reduction has been exhausted. It also does not show that the general conjecture is close to resolution. The missing universal existence or escape argument remains the main gap.

## 8. Reproducibility

The [constructor](cyclic_five_minimum_obstruction.py) builds all four local pieces and the full graph, checks the fixed discovery witnesses, generates the cut certificates, and produces the cover. The [independent verifier](verify_cyclic_five_minimum_obstruction.py) imports no constructor. Both require only Python's standard library.

```bash
python3 -B research/five-cdc-attempt/cyclic_five_minimum_obstruction.py
python3 -B research/five-cdc-attempt/verify_cyclic_five_minimum_obstruction.py
```

The JSON certificate has 48,978 bytes and SHA-256 `e8ee46bb12c877499e3b631a3cac412f679b562cce48a9f4484a7e23197e2dd0`. Regeneration is byte-identical. Discovery used SAT and terminal-flow searches, but the saved proof and verification require neither solver. The work makes no smallest-order or literature-novelty claim.

Follow-up: [An odd-component secondary objective succeeds on the 130-vertex graph](minimum-matching-secondary.md). A complete local intersection relation classifies every one-edge-per-region matching: 261,356 are suitable and the other 26 have forced odd singleton components. Consequently every minimizer of class size followed by odd unmatched-component count is suitable on this graph. The local transfer lemma applies to other assemblies of the same five-pole; the general minimization and reachability questions remain open.
