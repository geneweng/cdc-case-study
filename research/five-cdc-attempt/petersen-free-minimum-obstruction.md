# Global minimum failure without Petersen four-poles

Research date: **6 October 2026**.

**Excluding Petersen four-poles does not make an arbitrary globally minimizing flow repairable in one coordinate fiber.** An explicit simple cubic graph on 214 vertices has girth six, cyclic edge connectivity four, and minimum possible color multiplicity six. A flow attaining that minimum has seven unsuitable color matchings and 21 failed plane flags. None of its seven incident fibers contains a successful flow.

The graph has no Petersen four-pole: every such four-pole contains a pentagon, whereas this graph has no circuit shorter than six. Nevertheless, an eight-edge circuit switch followed by a 155-edge circuit switch constructs a five-layer cover. The minimum remains six throughout, and both the actual circuit distance and the fiber distance are exactly two.

This removes the Petersen-piece qualification from the [previous minimum-color obstruction](minimum-color-obstruction.md). It does not establish a failure on cyclically five-edge-connected graphs: the new graph still contains ten larger four-poles behind cyclic four-edge cuts. Favorable minimizers, secondary optimization, and a general neutral-repair theorem remain possible. The five-cycle double cover conjecture remains unproved by this work.

## 1. The precise statement

For a nowhere-zero three-bit flow f, put

\[
M_a=f^{-1}(a),\qquad m(f)=\min_{a\ne0}|M_a|,
\qquad \mu(G)=\min_f m(f).
\]

Call a matching **suitable** if it is the intersection of two binary cycles, which here means two even edge subgraphs. The [complete fiber criterion](matching-fiber-repair.md) says that the fiber with fixed color matching Mₐ contains a successful five-label lift precisely when Mₐ is suitable or its fixed coordinate plane is marked by one of the three linear completion tests.

**Certified theorem.** There are a simple cubic graph G and a nowhere-zero flow f such that:

1. G has 214 vertices, 321 edges, girth six, and cyclic edge connectivity four.
2. G contains no Petersen four-pole, even as a noninduced subgraph.
3. Every color in every nowhere-zero three-bit flow on G occurs at least six times, and m(f)=μ(G)=6.
4. All seven matchings Mₐ of f are unsuitable, and all seven incident planes are unmarked.
5. Two legal circuit switches reach a successful flow, with m=6 after each switch.

Items 3–4 refute cardinality optimality as a sufficient condition on graphs without Petersen four-poles. Items 4–5 give exact repair distance two. These statements concern an arbitrary minimizing flow; they do not refute the existence of a favorable minimizing flow on every graph.

## 2. Why the lower-bound mechanism extends beyond Petersen blocks

Let H be a cubic graph with no proper three-edge-coloring, and delete adjacent vertices u,v to make a four-pole B. Pair its four dangling edges according to whether their missing endpoint was u or v.

**Pair-equality lemma.** In every nowhere-zero two-bit flow on B, the two values in each port pair agree.

**Proof.** Write the boundary values as p,q at the former u and r,s at the former v. Summing the internal flow equations gives p+q=r+s. If p≠q, their common sum is nonzero. Restoring u,v and giving uv that sum extends the flow to a nowhere-zero two-bit flow on H, hence a proper three-edge-coloring. This is impossible. Therefore p=q and r=s. ∎

The argument needs no Petersen-specific property. Here we call a four-pole with this equality **isochromatic**; only the stated equality is used.

Arrange k such blocks around a replaced base cycle, using the junction construction in Section 3. Let Pⱼ comprise the internal edges and all four port edges of block j, and let sⱼ be the retained base spoke at position j. Every two-bit flow, allowing zeros, must have a zero in

\[
Y_j=P_{j-1}\cup P_j\cup\{s_j\}.
\]

Indeed, if both blocks are zero-free, their paired ports have values α,α and β,β. The two junction equations then give the same value α+β to both edges leading to the base vertex, forcing its spoke to zero.

Each block edge belongs to two of these k obligations; each spoke belongs to one. Thus every two-bit flow has at least ⌈k/2⌉ zero edges in the charged set of the region. Lower bounds from regions add whenever their charged edge sets are disjoint. This is the same counting argument as before, now for any block with the pair-equality property.

## 3. The flower block and the full graph

Use the flower graph J₅ with vertices aᵢ,bᵢ,cᵢ,dᵢ, for 0≤i<5. Join aᵢ to bᵢ,cᵢ,dᵢ; join the bᵢ in a pentagon; join cᵢ to cᵢ₊₁ and dᵢ to dᵢ₊₁ for 0≤i<4; and close the remaining ring with c₄d₀ and d₄c₀.

Number aᵢ,bᵢ,cᵢ,dᵢ as 4i,4i+1,4i+2,4i+3. Delete a₀=0 and b₀=1. The resulting block B has 18 internal vertices and 25 internal edges, with port pairs

\[
a=(2,3),\qquad b=(5,17).
\]

The local property is verified without assuming a literature result about J₅. A binary-flow enumeration and an independent proper-edge-coloring search both find exactly **108 nowhere-zero two-bit assignments** on the 25 internal and four port edges. Every assignment has boundary (α,α,β,β). Each of the nine choices of α,β∈{1,2,3} occurs twelve times. The binary local flow space has 2¹¹=2,048 elements. In particular, these paired boundaries also certify that no three-edge-coloring of J₅ can extend across the deleted adjacent vertices.

Use the same fourteen-vertex cubic base as in the preceding example: pentagons on vertices 0,…,4 and 5,…,9, the edge (12,13), and spokes

```text
(0,10), (5,10), (2,10), (1,11), (6,11),
(8,11), (3,12), (7,12), (4,13), (9,13).
```

Replace each pentagon using five copies Bⱼ and junctions uⱼ,wⱼ. Keep the original spoke at vⱼ, delete the pentagon edges, and add

\[
v_j u_j,\ v_j w_j,\ u_j b^0_j,\ w_j b^1_j,
\ a^0_j u_{j+1},\ a^1_j w_{j+1},
\]

with indices modulo five. Each region adds 5·18+10=100 vertices, giving 214 in total. The [certificate](petersen_free_minimum_obstruction.json) includes every edge, vertex map, port, and charged set.

The first region's blocks use vertices 14,…,103 and its junctions 104,…,113. The second uses blocks 114,…,203 and junctions 204,…,213. A block has 29 charged edges including ports; a region has 5·29+5=150 charged edges. The two charged sets are disjoint.

### Global minimum six

Each five-block region forces at least three zeros in every two-bit flow. The disjoint regions therefore force at least six zeros in total. For any nonzero three-bit color a, quotienting by ⟨a⟩ turns a nowhere-zero three-bit flow into a two-bit flow whose zero edges are exactly Mₐ. Consequently |Mₐ|≥6 for every a and every nowhere-zero flow.

The supplied initial flow has color sizes

\[
(54,47,53,6,51,58,52).
\]

It attains the lower bound, so μ(G)=6. No global SAT unsatisfiability assertion is needed to establish this minimum.

### Connectivity and absence of Petersen pieces

The independent verifier constructs a 108-dimensional fundamental cycle basis. Its 321 edge columns are distinct and nonzero, excluding one- and two-edge cuts. Checking all **5,461,280 edge triples** finds exactly 214 cuts, each a vertex star. The four ports of the first flower block give a cyclic four-edge cut, establishing cyclic edge connectivity exactly four.

Two shortest-cycle computations use different methods: one deletes each edge and searches between its endpoints; the other searches from every vertex and checks nontree edges. Both give girth six. The standard Petersen four-pole contains the pentagon (2,3,8,5,7,2), so it cannot occur in G.

## 4. Why all seven incident fibers fail

For each color, the initial matching has an unmatched vertex whose three neighbors are all matched:

| Color | Matching size | Unmatched obstruction vertex |
|---|---:|---:|
| 1 | 54 | 17 |
| 2 | 47 | 10 |
| 3 | 53 | 2 |
| 4 | 6 | 0 |
| 5 | 51 | 56 |
| 6 | 58 | 57 |
| 7 | 52 | 136 |

Each displayed vertex is an odd singleton component of G−V(Mₐ), excluding even the candidate subgraph required by the matching criterion. In particular, every color matching is unsuitable.

There are also 21 explicit paired-cut certificates, one for each choice of first coordinate in each of the seven incident planes. For each record, the verifier directly checks

\[
\delta(A)\subseteq F,\qquad
\delta(X)\setminus S=\delta(A)\cap y,\qquad
|\delta(X)\cap S|\equiv1\pmod2,
\]

where S=E(G)\(F∪y). The [paired-cut theorem](fiber-cut-obstructions.md) therefore excludes all three plane marks in every incident plane. Combining these certificates with the seven unsuitable matchings excludes successful states throughout all seven fibers, even after arbitrarily many switches with one fixed increment.

## 5. Two switches repair the minimizing flow

The initial color-4 matching, in the certificate's edge order, is

\[
\{1,65,139,164,215,241\}.
\]

First add 3 along the eight-edge circuit

\[
(0,104,86,90,88,91,87,105,0).
\]

Its edge indices are {112,113,126,127,136,137,164,165}. The matching replaces edge 164=(86,104) by edge 112=(88,90). Its size remains six, but the obstruction at vertex 0 disappears and the new matching is suitable.

The certificate supplies even edge sets F,t with F∩t equal to that new matching. For the first functional ℓ=4, the difference F△supp(ℓ∘f) is one 155-edge circuit. Adding 4 along it reaches the desired first coordinate while preserving the two coordinates y,z that annihilate color 4. Set w=t+y+z and use the established five-label decoding. Every edge receives exactly two labels and each label has even degree at every vertex.

| Stage | Sizes of colors 1,…,7 | Minimum |
|---|---|---:|
| Initial | 54, 47, 53, 6, 51, 58, 52 | 6 |
| After the eight-edge switch | 53, 48, 53, 6, 52, 57, 52 | 6 |
| After the 155-edge switch | 69, 69, 75, 6, 36, 36, 30 | 6 |

The initial fiber obstructions exclude any one-switch or one-fiber repair. The supplied two-switch repair proves that both distances are exactly two.

## 6. Consequence for the current approach

The failure of cardinality minimization is caused by a more general paired-port mechanism than the Petersen block alone. Raising girth to six and removing every Petersen four-pole leaves the same obstruction intact.

| Proposed sufficient hypothesis | Status after this checkpoint |
|---|---|
| An arbitrary globally minimum color class on a cyclically four-edge-connected graph is suitable | False |
| The same claim after excluding Petersen four-poles | False |
| An arbitrary globally minimizing flow has a successful incident fiber under those restrictions | False |
| Some globally minimizing flow always has a suitable color class | Unresolved |
| Neutral moves among minimizing flows always permit repair | Unresolved |
| Cardinality minimization suffices on cyclically five-edge-connected graphs | Unresolved |

The new example still has flower four-poles separated by cyclic four-edge cuts. It is not a certificate that all useful reductions have been exhausted, nor a counterexample to an existence theorem on fully reduced cores. A further optimization argument must use additional structure: a secondary choice among minimizers, control of neutral moves, or a stronger connectivity/reduction hypothesis. Another counterexample built by the same four-pole ring mechanism would not by itself address the cyclically five-edge-connected case.

## 7. Reproduction and verification

The [constructor](petersen_free_minimum_obstruction.py) builds the graph, generates the local and cut certificates, and checks fixed discovery witnesses. The [independent verifier](verify_petersen_free_minimum_obstruction.py) imports no constructor and checks the graph, local proper colorings, the global counting argument, all edge triples, girth, all obstructions, both actual switches, and the final cover.

```bash
python3 -B research/five-cdc-attempt/petersen_free_minimum_obstruction.py
python3 -B research/five-cdc-attempt/verify_petersen_free_minimum_obstruction.py
```

Both use only Python's standard library. SAT and a terminal-flow search were used to discover the fixed witnesses; neither is needed to reproduce or verify the result. The JSON certificate has 70,874 bytes and SHA-256 `855a7ac6b8b7fc60d782db7082e464b43c9e5e638a5e804242fe56a48a560ba8`. No smallest-order or literature-novelty claim is made.
