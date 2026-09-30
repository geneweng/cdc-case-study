# Coordinate completion reduces exactly through Petersen pieces

**30 September 2026. The general 5-cycle double cover conjecture remains unproved here.** Completing a selected flow coordinate after repairs inside Petersen pieces is equivalent to completing its projection on the contracted graph. If q pieces are contracted and a suitable five-layer cover of the quotient is supplied, it can be lifted after at most **2q internal pentagon switches**, preserving every exterior flow value and every exterior cover-label pair.

The key is a joint extension property: a three-bit flow boundary and a five-layer cover boundary can always be realized together when they agree on the membership of one distinguished layer. This is stronger than separately extending the flow and the cover. It does not require the cover to induce the entire three-bit flow; they share the one specified binary coordinate.

The local two-switch bound is sharp for a specified cover boundary. An exhaustive independent computation checks 21,640 compatible boundary pairs and 2,455,920 starting-flow/cover-boundary cases. As an application, each of the seven coordinates in the earlier 72m-vertex obstructed family can be repaired separately in **exactly m internal pentagon switches**, with all exterior flow values fixed.

**Continuation:** [A four-flow criterion](fourflow-quotient-repair.md) supplies the quotient cover explicitly whenever contracting the selected cycles of the original blowup or semiblowup graph leaves a four-flow. It handles every starting flow and every chosen normal on all prism constructions, using at most two pentagons per piece, and identifies cases where this sufficient condition fails.

## 1. Joint boundary data

Let B be the Petersen graph with adjacent vertices 0,1 deleted, using the internal edge and port order

```text
(2,3), (3,4), (2,7), (3,8), (4,9),
(5,7), (6,8), (7,9), (8,5), (9,6),
a1 at 4, a2 at 5, b1 at 2, b2 at 6.
```

A local nowhere-zero flow assigns values in F₂³∖{0} to these fourteen edges, with XOR zero at every internal vertex. Its boundary p=(p₁,p₂,p₃,p₄) must have XOR zero. There are 301 possible ordered boundaries and 34,230 local flows.

For covers use

\[
Q=\{x\in\mathbb F_2^5:|x|=2\}.
\]

A Q-valued edge assignment with XOR zero at each internal cubic vertex specifies five even layers, covering every edge exactly twice. Let q=(q₁,q₂,q₃,q₄) be its boundary, also with XOR zero. The [earlier boundary theorem](petersen-boundary.md#the-petersen-four-pole-accepts-every-parity-state) shows that all 640 possible ordered Q-boundaries extend.

Fix a nonzero linear functional ℓ:F₂³→F₂ and distinguish cover label 0. Call the two boundaries compatible when

\[
\ell(p_i)=(q_i)_0\qquad(i=1,2,3,4).
\]

We seek extensions f and c with these exact boundaries and with

\[
\ell(f(e))=(c(e))_0
\]

on all fourteen edges. Other flow coordinates and other cover labels are not identified with one another.

## 2. The exact local extension theorem

**Joint extension and repair theorem.** Every compatible pair (p,q) has simultaneous extensions. Starting from any local nowhere-zero flow with boundary p, at most two internal pentagon switches produce a flow whose ℓ-support is label 0 of a cover with boundary q. Throughout the repair, all four flow boundary values stay fixed.

For the exhaustive proof normalize ℓ to the least significant bit by a linear change of basis. Such changes preserve nowhere-zero flows and valid circuit switches. Define

\[
\mathcal S(p)=\{\operatorname{supp}(f_1):f\text{ has boundary }p\},
\qquad
\mathcal T(q)=\{\operatorname{supp}(c_0):c\text{ has boundary }q\}.
\]

The prescribed port bits admit exactly eight binary even extensions inside B: its connected internal graph has cycle-space dimension 10−8+1=3. The flow relation has a particularly simple form:

> Every one of those eight supports is realizable, except that the empty support is excluded when all pᵢ lie in ker ℓ and p₁≠p₂.

For normalized ℓ, precisely twelve boundaries have that exception:

\[
(x,y,x,y)\quad\text{or}\quad(x,y,y,x),
\qquad x,y\in\{2,4,6\},\ x\ne y.
\]

They realize seven supports each; the other 289 boundaries realize eight. Thus there are 2,396 realized flow-boundary/support pairs. The exceptional empty support would confine all values to a two-dimensional subspace, giving a three-edge coloring of the four-pole with unequal a-port colors, which is impossible. Sufficiency in every remaining case is established by the complete local enumeration described below.

For cover boundaries the support counts are:

| Number of possible label-0 supports | Cover boundaries |
|---:|---:|
| 2 | 48 |
| 3 | 12 |
| 4 | 78 |
| 7 | 240 |
| 8 | 262 |

Every cover boundary therefore offers at least two choices. Since a compatible flow boundary excludes at most one of the eight common binary candidates, the two relations always intersect. Direct enumeration gives the sharper intersection counts:

| Size of S(p)∩T(q) | Compatible boundary pairs |
|---:|---:|
| 2 | 1,872 |
| 3 | 180 |
| 4 | 2,598 |
| 7 | 8,568 |
| 8 | 8,422 |
| **Total** | **21,640** |

To prove the quantitative repair statement, form the fixed-boundary reconfiguration graph for each p. Its vertices are local flows, and a pentagon edge is a valid addition of one nonzero vector on an internal five-cycle. Run breadth-first search from all states whose support belongs to T(q). Every starting state has distance at most two. For comparison, allowing all seven internal circuits gives:

| Distance to compatibility with q | All internal circuits | Internal pentagons only |
|---:|---:|---:|
| 0 | 1,899,648 | 1,899,648 |
| 1 | 516,528 | 486,576 |
| 2 | 39,744 | 69,696 |
| **Total** | **2,455,920** | **2,455,920** |

These cases count a named starting local flow and a named compatible **cover boundary**, not a choice of an entire cover. They fix one normalized nonzero functional and one distinguished cover label; changes of basis and label permutations give the general statement.

This is an exhaustive finite computational proof. The independent verifier reconstructs the state spaces and their adjacency rather than accepting solver infeasibility results. The count does not establish a conjecture by extrapolation.

## 3. Two switches really can be needed

Use normal 1, flow boundary (4,4,4,4), and initial local flow

```text
35761136574444
```

Its coordinate support has mask 887. Prescribe cover boundary digits `4949`, meaning the pairs (12,34,12,34) under the dictionary

```text
0=01, 1=02, 2=03, 3=04, 4=12,
5=13, 6=14, 7=23, 8=24, 9=34.
```

The possible label-0 support masks for this cover boundary are **exactly {0,151,992}**. The initial flow has nineteen valid one-switch neighbors over all seven internal circuits. Their support masks are **only {442,717,887}**. Neither zero nor one switch can meet the prescribed cover boundary.

Two pentagons suffice:

| Step | Circuit edge mask | Added vector | Resulting flow word | Coordinate mask |
|---:|---:|---:|---|---:|
| 0 | — | — | `35761136574444` | 887 |
| 1 | 301 | 2 | `15541336774444` | 887 |
| 2 | 992 | 1 | `15541227664444` | 151 |

The final cover word is `01140762854949`. The first move preserves the selected support while preparing the second move.

There is a graph-level sharpness example for any q≥3. Form a closed necklace of q copies of B by joining a₁ⁱ to b₁ⁱ⁺¹ and a₂ⁱ to b₂ⁱ⁺¹. Repeat the initial local flow above; all joining-edge flow values are 4. Prescribe pair 12 on every first-rail joining edge and pair 34 on every second-rail joining edge. This is a valid quotient cover whose label 0 is empty.

Every piece has the same local two-switch lower bound. When switches are confined to piece interiors and the specified exterior cover pairs must be retained, the exact distance is therefore **2q**. Repeating the two displayed switches supplies the upper bound. Certificates are included for q=3,6,12.

This sharpness concerns extending the **specified quotient cover**. The starting coordinate already has a five-layer completion if the exterior cover pairs may change: the local word `01140004114444` extends it with pair 12 on both rails. The verifier checks that alternative cover as well. Thus this example does not give a 2q lower bound for ordinary coordinate completion with unrestricted choice of quotient cover.

## 4. An exact graph reduction

Let G be a loopless cubic graph containing q vertex-disjoint induced Petersen four-pole interiors, each with exactly four port edges leaving it. Edges between different pieces are allowed. Let H be obtained by contracting each piece to one vertex and deleting its ten internal edges. Write E₀ for the retained edges.

The graph H has degree-three vertices outside the pieces and degree-four vertices representing them. A cover layer on H is an **even subgraph**: it may have degree four at a contracted vertex. Requiring degree at most two there would incorrectly reject valid quotient covers. Parallel edges are allowed.

Fix a nowhere-zero three-bit flow f on G and a nonzero functional ℓ. Its restriction f̄ to H is a nowhere-zero flow. Let

\[
\bar F=\{e\in E_0:\ell(f(e))=1\}.
\]

**Coordinate-completion reduction.** The following statements are equivalent:

1. H has a five-layer cover containing F̄ as one whole layer.
2. Starting from f, switches confined to the piece interiors can reach a flow g whose ℓ-support is a whole layer of a five-layer cover of G.

Moreover, given **any particular cover** in (1), at most 2q pentagon switches suffice in (2). They preserve f on E₀, and the resulting cover preserves all pairs of the given quotient cover on E₀.

**Proof.** For sufficiency, name the quotient layer 0. At each contracted vertex, the four flow values XOR to zero and the four cover pairs XOR to zero. Their distinguished bits agree because the quotient layer is F̄. Apply the joint local theorem, independently in each piece. Internal switches leave port values fixed, so choices remain compatible even when an edge joins two pieces. Keep the quotient cover pairs on E₀ and insert the local cover assignments. Every original vertex has even layer degrees and every edge has exactly two labels. The bound is the sum of at most two pentagons per piece.

For necessity, every allowed switch leaves E₀ unchanged. Restrict a final cover to E₀. Summing each label's parity over a contracted piece proves even degree at its quotient vertex; multiplicity two is retained. Its label-0 support is precisely F̄. □

There is also an unconditional cover equivalence:

\[
G\text{ has a five-layer CDC}
\quad\Longleftrightarrow\quad
H\text{ has a five-layer CDC}.
\]

Restriction proves necessity. For sufficiency, use the earlier complete Q-boundary extension relation in each piece; no flow need be prescribed. This quotient has degree-four vertices and does not assert equivalence with an arbitrary cubic two-vertex cap.

The reduction identifies exactly what remains after allowing internal flow repair. It does not supply a cover of H. It also does not preserve the original coordinate support *inside* the pieces; that support can be impossible before repair, as the previous examples show. No monotonicity of the original palette-dependent defect potential is asserted.

## 5. Each of the seven obstructed coordinates can be repaired separately

Apply the reduction to the six Petersen pieces of G₁, the 72-vertex example. Its quotient H₁ has **30 vertices and 48 edges**: 24 degree-three vertices and six degree-four vertices. The certificate gives a five-layer cover for each of the seven supports of its restricted flow.

The constructor takes those seven quotient cover words as input and finds compatible local extensions using the joint relation. Only one piece needs one pentagon switch in each case:

| Selected normal ℓ | Piece | Internal circuit mask | Added vector |
|---:|---:|---:|---:|
| 1 | 5 | 992 | 3 |
| 2 | 1 | 992 | 3 |
| 3 | 1 | 151 | 1 |
| 4 | 0 | 992 | 6 |
| 5 | 4 | 992 | 1 |
| 6 | 5 | 992 | 3 |
| 7 | 3 | 602 | 7 |

Piece indices are zero-based. The circuit masks use the fourteen-edge convention above and only select internal edges. These repairs are alternatives: the target flow can depend on the chosen normal. The table does not claim a single resulting flow completes all seven coordinates.

For Gₘ, repeat the chosen local switch once per period and pull back the associated cover. All retained flow values remain unchanged, and every quotient cover pair is preserved. For each specified normal, the previous m disjoint Z–W witnesses require at least m pieces to be touched by internal repair. Hence **the exact internal repair distance is m for each of the seven prescribed normals separately**.

The earlier one-global-switch repair remains valid and addresses a different move class. Here every move is a pentagon inside one piece, and the selected normal can be chosen in advance. Explicit certificates are checked for m=1,2,10, through 720 vertices. The periodic covering argument and disjoint-witness lower bound prove the statement for all m≥1.

## 6. Verification, context, and the remaining problem

```bash
python3 research/five-cdc-attempt/joint_boundary_completion.py
python3 research/five-cdc-attempt/verify_joint_boundary_completion.py
```

The [constructor](joint_boundary_completion.py) writes the [certificate](joint_boundary_completion.json). Its flow enumeration uses triples of binary even masks, and its cover relation uses the previously certified boundary table. The [independent verifier](verify_joint_boundary_completion.py) imports neither constructor nor any earlier verifier. It independently enumerates both relations by assigning three chords of a spanning tree and solving the remaining internal edges from the four prescribed port values.

That reconstruction yields all 34,230 local flows and all 14,700 local covers. The verifier recognizes switches from differences of flow pairs, recomputes the complete distance histograms, checks the sharp local and necklace examples, validates quotient cover parity including degree-four vertices, and checks all twenty-one periodic graph repairs and their complete cover assignments. The family distance lower bound uses the proved Z–W charge obstruction from the earlier report; its disjoint witness premises are checked again here.

Five-cover methods involving superpositions, nowhere-zero 4-flows, and graph reduction already occur in the literature. The result recorded here is the explicit joint boundary classification, its sharp local repair bound, and the resulting prescribed-coordinate reduction; no claim of priority is made. [Liu–Hao–Luo–Zhang, *5-Cycle Double Covers, 4-Flows, and Catlin Reduction*, 2023](https://epubs.siam.org/doi/10.1137/22M1472425)

The general problem has not disappeared: the contracted graph still needs a suitable prescribed-layer cover. The new result proves that these Petersen interiors create no further joint flow/cover obstruction once that quotient cover exists. A continuing proof strategy must handle the contracted graph or establish another existence step, rather than infer global completion from local boundary flexibility alone.
