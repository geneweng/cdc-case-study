# All seven coordinates can be impossible prescribed layers

**29 September 2026. The general 5-cycle double cover conjecture remains unproved here. This report disproves a stronger proposed selection rule, gives a decomposition theorem, and supplies two verified five-layer covers of the example. No claim of novelty over the complete literature is made.**

The preceding [layer-selection experiment](component-permutations.md) succeeded on all 215 chosen input flows. That mechanism does **not** work for every starting flow: there is a simple connected bridgeless cubic graph on **30 vertices** with a nowhere-zero F₂³-flow f such that none of its seven coordinate supports

\[
F_\ell=\{e:\ell\cdot f(e)=1\},\qquad 0\ne\ell\in\mathbb F_2^3,
\]

can be a whole member of a cycle double cover. This holds even with arbitrarily many layers. In particular, allowing every possible change to the other two coordinates while preserving one of these seven supports cannot produce a five-layer cover.

The graph itself has a five-layer cover. One allowed circuit switch in f also produces a flow with a successful five-layer lift. The obstruction therefore concerns the choice of a layer from the original flow's three-dimensional cycle space.

Here a layer is an even subgraph and may consist of several circuits. Requiring F as one whole layer is stronger than requiring any one of its circuits separately.

## A local obstruction in Petersen

Let P be the Petersen graph and F one of its spanning 2-factors. It consists of two pentagons. Its complementary perfect matching M joins the two pentagons: a matching edge within one pentagon would be a chord, contradicting girth five.

Suppose a CDC contains F. At each vertex, F has already used both pentagon edges once. The remaining required incidences are one on each F-edge and two on the M-edge. Each other active layer must therefore use one F-edge and one M-edge. If it used both F-edges, their multiplicities would be exhausted, leaving the two remaining M-edge occurrences without an incident edge to accompany either one.

Consequently every circuit in every other layer alternates between F and M. Only M-edges cross the partition into the two pentagons, so each such circuit uses an even number of M-edges. Its length is divisible by four. A simple circuit in P has length at least five and at most ten, so every alternating circuit has length **eight**.

But the total number of edge occurrences still required is

\[
2|E(P)|-|F|=30-10=20,
\]

which is not divisible by eight. This contradiction excludes a CDC containing F, regardless of the number of layers. □

This underlying Petersen obstruction is known: Archdeacon's [1995 research note](https://www.sfu.ca/~mohar/Problems/CYCLECOV.HTM) describes the equivalent impossible weighted cover, with weight two on the matching and one on the pentagons. The proof above is supplied for completeness. Related obstructions to including 2-factors also appear in [Hägglund, 2012](https://arxiv.org/abs/1203.2015); the present construction is not a claim that the local phenomenon is new.

## Prescribed layers compose exactly across two-edge sums

Form a two-edge sum of graphs G₁,G₂ by deleting edges u₁v₁,u₂v₂ and inserting u₁u₂,v₁v₂. The two new edges form a cut. Any even subgraph uses both cut edges or neither, by parity of its total degree on either side.

**Capping** its restriction to Gᵢ means restoring uᵢvᵢ precisely when both cut edges were used. Capping preserves even degrees. If a collection double covers the sum, its capped layers double cover each factor: both cut edges have the same two layer labels, and the restored edge receives those labels.

Conversely, suppose the two factors each have a five-layer cover with a prescribed layer Fᵢ distinguished as label 0. Assume F₁,F₂ agree on whether their deleted edges belong to that layer. Permute the four other layer labels in one factor to align the two labels covering the deleted edges. This is always possible:

- If the deleted edges belong to Fᵢ, their pairs are {0,a} and {0,b}; send a to b.
- Otherwise both pairs are two-element subsets of the other four labels; map one pair to the other.

After this relabeling, replace the deleted edges by the connectors carrying their common label pair. This produces a five-layer cover with the prescribed combined layer. Empty layers are permitted; a completion here always means a list (F,C₁,C₂,C₃,C₄).

**Composition theorem.** For a graph assembled from a tree of two-edge sums, a prescribed even subgraph F has a five-layer completion if and only if every capped factor has a five-layer completion of its capped F. Necessity also holds for any number of cover layers. Sufficiency follows by the label alignment above, working along the tree. □

The corresponding flow statement is exact. The two connector values of a binary flow are equal, because their XOR over the cut is zero. Capping gives a nowhere-zero flow on each factor. Conversely, factor flows with matching deleted-edge values glue to a nowhere-zero flow.

For compatible flows fᵢ, define

\[
\mathcal A_i=\{\ell\ne0:F_\ell(f_i)\text{ has a five-layer completion on }G_i\}.
\]

Then the combined flow has precisely

\[
\mathcal A=\bigcap_i\mathcal A_i
\tag{1}
\]

as its successful coordinate choices. Thus each piece can have successful choices while the combined graph has none. Equation (1) is an exact finite compatibility rule, rather than a criterion tied to our component-recoloring algorithm.

## An explicit 30 vertex construction

Index Petersen's edges as follows, with subscripts modulo five:

\[
e_i=(i,i+1),\quad e_{5+i}=(i,i+5),\quad
e_{10+i}=(i+5,(i+2)\bmod5+5),\qquad 0\le i<5.
\]

In this edge order take the flow

\[
p=(2,7,2,7,1,3,5,5,5,6,2,4,7,1,1).
\tag{2}
\]

Integers encode binary vectors; addition is XOR. Directly, every entry is nonzero and the three incident values at every vertex have XOR zero. Use three copies P₀,P₁,P₂, with flows Tᵢp, where each linear map is specified by its images of the basis (1,2,4):

| Block | Tᵢ(1), Tᵢ(2), Tᵢ(4) | Normals whose supports are Petersen 2-factors |
|---|---|---|
| P₀ | 1, 2, 4 | 1, 3, 7 |
| P₁ | 3, 2, 4 | 1, 2, 6 |
| P₂ | 4, 7, 2 | 4, 5, 7 |

All three maps are invertible. Label Pₖ's vertices 10k through 10k+9.

Delete e₀,e₁ from P₀, and e₀ from each of P₁,P₂. Insert connectors

\[
(0,10),(1,11)\quad\text{with value }2,
\qquad
(1,20),(2,21)\quad\text{with value }7.
\tag{3}
\]

The removed values match: p(e₀)=T₁p(e₀)=2 and p(e₁)=T₂p(e₀)=7. Thus conservation survives at every endpoint. There are 30 vertices and 45 edges, and the result is simple, connected, cubic, and bridgeless.

Every nonzero normal occurs in at least one row of the table. If a CDC had Fℓ as a layer, cap it on such a block. The capped layer is that block's Petersen 2-factor, contradicted by the local proof. This establishes all seven failures without enumerating colorings of the 30-vertex graph.

For reference, the global supports have the following sizes. These counts are diagnostics, not the nonexistence proof.

| ℓ | Edges in Fℓ | Circuits in Fℓ | Components of G−E(Fℓ) | Obstruction blocks |
|---|---:|---:|---:|---|
| 1 | 28 | 4 | 13 | P₀, P₁ |
| 2 | 26 | 2 | 11 | P₁ |
| 3 | 26 | 3 | 11 | P₀ |
| 4 | 26 | 3 | 11 | P₂ |
| 5 | 22 | 4 | 7 | P₂ |
| 6 | 24 | 3 | 9 | P₁ |
| 7 | 28 | 3 | 13 | P₀, P₂ |

The seven supports are distinct and nonempty. Together with zero they form the three-dimensional binary cycle subspace W generated by f's coordinates. It has full edge support, yet **none of its seven nonzero elements can be a CDC layer**. No basis change within W can overcome this obstruction.

## One circuit switch leaves the obstruction behind

In P₂, choose the circuit with local Petersen edge indices

\[
Q=\{1,2,6,8,10,12,13,14\}.
\]

It avoids the deleted edge e₀, so it remains an eight-edge circuit in the combined graph. None of its flow values equals 3. Add 3 to each edge of Q. This preserves conservation and keeps every edge value nonzero.

The seven fixed-flow lift-defect counts change from

\[
(4,6,6,4,2,6,6)\quad\text{to}\quad(4,6,6,4,0,6,6).
\]

The normal-5 support now has 18 edges and has a verified five-layer completion. It is outside W. Thus the graph does admit the desired cover after changing the flow beyond its original coordinate space; the example does not refute the earlier nonincreasing circuit-repair proposal.

The certificate also supplies a second cover, obtained simply by gluing three explicit Petersen covers with aligned edge-label pairs. Both covers are checked directly for exact double coverage and even degrees.

## Verification and what remains open

```bash
python3 research/five-cdc-attempt/layer_selection_obstruction.py
python3 research/five-cdc-attempt/verify_layer_selection_obstruction.py
```

The [constructor](layer_selection_obstruction.py) saves the complete graph, flows, block maps, cuts, seven obstruction certificates, two covers, and circuit move in [layer_selection_obstruction.json](layer_selection_obstruction.json). The [independent verifier](verify_layer_selection_obstruction.py) uses only Python's standard library and an earlier independent DFS helper. It does not use the constructor, NetworkX, a completion solver, or the component-permutation classifier.

It independently enumerates all 64 binary even subgraphs and 57 circuits of Petersen. All six 2-factors have exactly five alternating circuits, each of length eight. It also checks all **28,560 labeled nowhere-zero three-bit flows**. The counts of flows with zero, one, two, or three 2-factor coordinate supports are respectively 5,040, 10,080, 10,080, and 3,360, agreeing with the constructor's 170 flow classes after multiplication by |GL(3,2)|=168. This census corroborates the local choices; the displayed construction and proof do not depend on the census's completeness.

For the larger graph, verification checks simplicity, connectivity, cubic degrees, absence of bridges, flow conservation, the actual two-edge cuts, every block projection, every obstructed normal, both covers, and the circuit switch. No proof-assistant verification or general graph-size census is claimed.

This closes the proposed universal shortcut from the previous report: **choosing a coordinate of an arbitrary starting flow, even followed by unrestricted repair of the remaining coordinates, is insufficient.** The conditional completion theorems remain valid. They must be combined with a way to change the coordinate space, or with independent choices on factors followed by cover gluing.

The example relies on two-edge cuts. It does not decide whether an analogous selection rule might hold after reducing to graphs without such cuts, and it does not prove the existence of a suitable flow on every remaining graph. The exact composition theorem identifies how a proof on those remaining pieces would transfer through two-edge sums.
