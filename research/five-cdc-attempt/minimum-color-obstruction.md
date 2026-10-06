# A globally minimum color class can still block every incident fiber

Research date: **6 October 2026**.

**Minimizing the smallest color class does not force repair, even on a simple cubic graph of girth five and cyclic edge connectivity four.** An explicit 114-vertex graph has minimum possible color multiplicity six. A flow attaining this global minimum has no suitable color matching and no marked coordinate plane: none of its seven incident fibers contains a successful flow.

Nevertheless, a seven-edge circuit switch followed by a 77-edge circuit switch gives a verified five-layer cover. The smallest class has size six throughout. Thus the actual repair distance and the fiber distance are both exactly two, while the proposed cardinality objective is already globally optimal at every stage.

This refutes the proposed sufficient condition that an arbitrary minimum-size color class must be the intersection of two binary cycles. It does not refute the five-cycle double cover conjecture, a suitable secondary choice among minimizers, or repair by neutral moves. The graph contains ten Petersen four-poles and belongs to a family already covered by the earlier conditional lifting results; it is not an example without those pieces.

**Follow-ups (6 October 2026):** [Global minimum failure without Petersen four-poles](petersen-free-minimum-obstruction.md) replaces the blocks with flower four-poles. The resulting 214-vertex graph has girth six and no Petersen four-pole, yet retains minimum six, seven blocked fibers, and exact two-switch repair. [Global minimum failure with cyclic edge connectivity five](cyclic-five-minimum-obstruction.md) then gives a 130-vertex example at minimum three, closing the stronger-connectivity possibility as well. Favorable minimizers and a general neutral-repair argument remain unresolved.

## 1. The optimization proposal

For a nowhere-zero F₂³-flow f, write Mₐ=f⁻¹(a), and define

\[
m(f)=\min_{a\ne0}|M_a|,
\qquad
\mu(G)=\min_f m(f).
\]

The proposed route was to choose a globally minimizing pair (f,a), then use its optimality to prove

\[
M_a=F\cap t
\tag{1}
\]

for two binary cycles F,t. The [matching theorem](matching-fiber-repair.md) would then construct a five-label lift inside the a-fiber. Here, as before, binary cycles are even subgraphs, possibly disconnected.

The [two-edge theorem](matching-terminal-flow.md) supports this idea when μ(G)≤2 on a cyclically four-edge-connected cubic core. But it does not imply that larger minimizing matchings satisfy (1).

The example below proves the stronger failure

\[
\mu(G)=m(f)=6,
\quad
\text{every }M_a\text{ fails (1), and every incident plane is unmarked}.
\tag{2}
\]

Global minimization alone therefore cannot select a successful state or even one whose incident fibers contain success.

## 2. The graph

Start with a cubic graph on vertices 0,…,13. It contains two pentagons

\[
(0,1,2,3,4,0),\qquad(5,6,7,8,9,5),
\]

the edge (12,13), and the ten spokes

```text
(0,10), (5,10), (2,10), (1,11), (6,11),
(8,11), (3,12), (7,12), (4,13), (9,13).
```

Blow up both pentagons using the established Petersen four-pole construction. For completeness, the four-pole B has internal vertices 2,…,9 and edges

```text
(2,3), (3,4), (2,7), (3,8), (4,9),
(5,7), (6,8), (7,9), (8,5), (9,6).
```

Its port pairs are a=(4,5) and b=(2,6). For each replaced pentagon v₀,…,v₄, use five copies Bⱼ and two new junction vertices uⱼ,wⱼ at each position. Retain each original spoke at vⱼ, delete the pentagon edges, and add

\[
v_j u_j,\ v_j w_j,\ u_j b^0_j,\ w_j b^1_j,
\ a^0_j u_{j+1},\ a^1_j w_{j+1},
\]

with indices modulo five. Each replaced pentagon adds 50 vertices, so the resulting graph has **114 vertices and 171 edges**.

The [certificate](minimum_color_obstruction.json) specifies the complete edge order and vertex maps. In that order, the first region's blocks use vertices 14,…,53 and its junctions 54,…,63; the second uses blocks 64,…,103 and junctions 104,…,113.

### Connectivity is checked independently

The verifier constructs a full fundamental cycle basis using a depth-first spanning tree. A set of edges is a cut precisely when its incidence vector is orthogonal to that cycle basis.

- Every edge column is nonzero, and all 171 columns are distinct. Thus there are no one- or two-edge cuts.
- Exhausting all **818,805 triples of edges** finds exactly 114 cuts, the three edges incident to each vertex.
- The four port edges around the first Petersen four-pole form a cut with a circuit on both sides.

Consequently the cyclic edge connectivity is exactly four. A separate shortest-cycle check gives girth five. The counterexample does not rely on a bridge, a two-edge cut, or a nontrivial three-edge cut.

## 3. An elementary global lower bound of six

The lower bound applies to **every two-bit flow on this graph**, allowing zeros. It therefore applies to every color of every nowhere-zero three-bit flow after quotienting by that color.

### The four-pole equality

Whenever all fourteen internal and port edges of B have nonzero two-bit values, the values at the two a-ports agree and the values at the two b-ports agree.

This is the standard equality property of this Petersen four-pole used in the [earlier boundary work](petersen-boundary.md). It can also be checked completely here: its binary local flow space has 64 elements. Pairing them gives exactly **18 zero-free two-bit flows**, all with paired port values. The independent verifier instead enumerates proper three-edge colorings and obtains the same eighteen assignments.

### Five obligations in each region

Let Pⱼ be the fourteen-edge set belonging to block Bⱼ, including its four port edges. Let sⱼ be the original spoke at vⱼ. Define

\[
Y_j=P_{j-1}\cup P_j\cup\{s_j\}.
\]

**Every Yⱼ contains a zero edge of any two-bit flow.** Otherwise both adjacent blocks are zero-free. Write their relevant paired port values as α,α and β,β. Kirchhoff's law at uⱼ and wⱼ gives the same value α+β on both edges to vⱼ. Kirchhoff's law at vⱼ then forces sⱼ to have value zero, contradicting the assumption.

There are five obligations Yⱼ in a region. A block edge belongs to exactly two of them; a spoke belongs to one. Every other edge belongs to none. Hence at least

\[
\left\lceil\frac52\right\rceil=3
\]

distinct zero edges are needed in the union of the region's blocks and spokes.

The two regions have disjoint charged edge sets: each has 70 block edges and five spokes. Their obligations therefore add, giving **at least six zero edges in every two-bit flow**.

For any nonzero a, choose a rank-two projection F₂³→F₂² with kernel {0,a}. Applied to a nowhere-zero flow f, its zero edges are exactly Mₐ. Thus

\[
|M_a|\ge6\quad\text{for every }f\text{ and every }a\ne0.
\tag{3}
\]

This is a global bound derived from the graph, not from a solver's optimality claim.

## 4. A flow attaining the bound and failing every fiber

The saved initial flow has color sizes

\[
(|M_1|,\ldots,|M_7|)=(27,21,21,6,28,33,35).
\]

Its color-4 matching consists of edge indices

\[
\{1,63,78,90,101,161\}.
\tag{4}
\]

There are three such edges in each charged region. Together with (3), this proves μ(G)=6. The projected two-bit flow also attains the minimum of six zeros even when the minimization allows arbitrary two-bit flows.

### Every color matching has an odd unmatched component

For a matching M, put D=V(M). The previous candidate lemma says that an even subgraph of G−M covering D can exist only if every component of G−D has even order. The following odd components independently certify failure for every color:

| Color | Class size | An odd component of G−V(Mₐ) |
|---|---:|---|
| 1 | 27 | {0,10,55} |
| 2 | 21 | {73} |
| 3 | 21 | {89} |
| 4 | 6 | {0} |
| 5 | 28 | {14} |
| 6 | 33 | {36} |
| 7 | 35 | {33} |

For the minimum matching M₄, vertex 0 is unmatched but all three neighbors—10,54,55—are matched. Their matching edges are respectively (5,10), (54,14), and (49,55). Any candidate even subgraph covering the matching endpoints would have to use all three edges at vertex 0, an immediate contradiction.

More generally, for any odd component K in the table, every edge of δ(K) would be forced into the candidate. Cubicity makes |δ(K)| odd, whereas an even subgraph crosses every cut evenly.

### The plane tests fail as well

Matching failure alone does not exclude a complete fiber: an internal first coordinate might still work. We therefore also certify all **21 flags** in the seven incident coordinate planes.

For each flag, let F and y be the two binary coordinate supports and S=E∖(F∪y). The saved vertex sets A,X satisfy

\[
\delta(A)\subseteq F,\qquad
\delta(X)\setminus S=\delta(A)\cap y,\qquad
|\delta(X)\cap S|\text{ odd}.
\]

These are the exact [paired-cut failure certificates](fiber-cut-obstructions.md). They rule out all three internal first coordinates in every plane. Together with the seven matching failures and the complete fiber theorem, they prove:

**No successful flow is reachable from this initial flow using only one increment, even with arbitrarily many switches by that increment.** In particular, neither the initial flow nor any one-circuit neighbor has a successful five-label lift.

## 5. A neutral two-switch repair at the global minimum

First add 6 on the seven-circuit with edge indices

\[
\{11,14,17,61,62,63,64\}.
\]

In vertex notation it is

\[
(0,54,14,15,20,18,55,0).
\]

The color-4 matching replaces edge 63=(54,14) by edge 17=(18,20). It still has six edges, but vertex 0 no longer supplies the forced-degree-three obstruction.

The new matching is suitable. The certificate gives two even edge sets F,t whose intersection is exactly this matching. In decimal edge-mask encoding they are

```text
F = 1149039833540733743438802862584251342053628920875206
t = 1698995659070370239468476443645301808823510261989419.
```

Use first functional ℓ=6, with ℓ(4)=1. The symmetric difference between the intermediate first coordinate and F is a **single 77-edge circuit**. Adding 4 on that circuit reaches F while retaining the two coordinates annihilating 4. The fourth-coordinate formula w=t+y+z then constructs a valid five-layer cover.

| Stage | Smallest color class | Size of color 4 | What has changed |
|---|---:|---:|---|
| Initial | 6 | 6 | All seven fibers are unsuccessful |
| After the seven-circuit switch | 6 | 6 | The color-4 matching becomes suitable |
| After the 77-circuit switch | 6 | 6 | The flow has an explicit five-label lift |

The first switch cannot already be successful, by the initial fiber obstruction. The second one is successful. Thus the **actual circuit distance is exactly two**, as is the fiber distance. No temporary increase of the smallest class is required in this example.

## 6. What this excludes from an optimization proof

For a fixed target color a and another increment b, give edges of G−M_b weights −1 on Mₐ, +1 on Mₐ₊ᵦ, and zero otherwise. The exact matching-update formula gives

\[
|M'_a|-|M_a|=\sum_{e\in C}w_b(e)
\]

for a legal b-switch on C. Consequently, absence of a decreasing single circuit is equivalent to absence of a decrease anywhere in that b-fiber: a difference even subgraph decomposes into edge-disjoint circuits, and the changes add.

The initial color-4 class satisfies every such nondecrease condition because it is globally minimum. It still fails the matching criterion, and every incident fiber fails the complete success test. Thus neither single-circuit optimality, full-fiber optimality, nor global cardinality optimality supplies the missing implication by itself.

The two final states demonstrate why a secondary choice matters: the same optimum value six occurs before any incident fiber can succeed, after a suitable matching appears, and after a cover has been constructed.

This leaves several distinct possibilities open. A favorable minimizer might always exist; a suitable secondary objective might select one; or a nonincreasing sequence allowing neutral steps might always reach success. This example proves none of those statements false. It also leaves open an optimization strategy restricted to graphs after all applicable Petersen-piece reductions.

## 7. Reproducibility and limitations

The [constructor](minimum_color_obstruction.py) builds the graph from the fourteen-vertex base, verifies the fixed discovery flow, generates the cut certificates, and constructs the cover. Discovery used SAT and max-flow searches, but **the global minimum is proved by the two-region counting argument**. Reproduction needs only Python's standard library.

The [independent verifier](verify_minimum_color_obstruction.py) imports no constructor. It rebuilds the graph structure, enumerates local proper edge colorings, checks a different fundamental cycle basis and every edge triple, verifies the region obligations and disjointness, checks all seven odd-component certificates and all 21 paired cuts, and directly verifies both switches and every cover edge and vertex.

```bash
python3 -B research/five-cdc-attempt/minimum_color_obstruction.py
python3 -B research/five-cdc-attempt/verify_minimum_color_obstruction.py
```

The result is an obstruction to a proposed proof strategy, accompanied by a complete repair certificate. It makes no claim of smallest order or literature novelty. The graph has a verified five-layer cover, and the general conjecture remains unproved by this work.
