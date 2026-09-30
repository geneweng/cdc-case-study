# Three-edge cuts: exact composition and a stronger selection obstruction

**29 September 2026. The general 5-cycle double cover conjecture remains unproved here. The results below concern decomposition and the limits of selecting a layer from an arbitrary fixed flow. No claim of novelty over the complete literature is made.**

The [previous 30-vertex obstruction](layer-selection-obstruction.md) used two-edge cuts. Removing that weakness does not restore the proposed selection rule: an explicit **26-vertex, 3-edge-connected cubic graph** has a nowhere-zero F₂³-flow whose seven coordinate supports are all impossible as whole CDC layers, even with arbitrarily many cover layers. The graph nevertheless has an explicitly verified five-layer cover.

The construction uses three-edge cuts. Prescribed-layer completion composes exactly across these cuts, extending the previous two-edge-cut theorem. At four-edge cuts, parity allows additional boundary patterns, and the same automatic capping argument fails. Two actual covers of the cube demonstrate that limitation.

## Exact composition across three-edge cuts

Let a three-edge cut have edges e₁,e₂,e₃. Each even layer uses zero or two of them. If xᵢⱼ counts the layers using exactly eᵢ and eⱼ, exact double coverage gives

\[
x_{12}+x_{13}=x_{12}+x_{23}=x_{13}+x_{23}=2,
\]

so

\[
x_{12}=x_{13}=x_{23}=1.
\tag{1}
\]

Thus exactly three distinct layers cross the cut, one through each pair of edges. All other layers miss it. In terms of the two layer labels on each edge, the boundary pairs are {a,b},{a,c},{b,c} for three distinct labels a,b,c.

**Capping a side** replaces the other side by one vertex incident with the three cut edges. By (1), the restriction of every layer is still even at the new vertex. Every edge is still covered twice. This works for a CDC with any number of layers.

Conversely, form a three-edge sum by deleting a cubic vertex from each of two cubic graphs and pairing their three incident half-edges. Suppose the factors have five-layer completions of prescribed layers F₁,F₂, whose membership agrees at corresponding ports. Distinguish Fᵢ as label 0. The three boundary pairs in each cover form a triangle of layer labels. Align these triangles by a permutation of the layer names in one factor:

- If Fᵢ misses the ports, label 0 is absent from both triangles. The other four labels can align the three crossing layers while fixing 0.
- If Fᵢ uses two ports, label 0 is the unique layer using that port pair on each side. Match these labels, then align the other two crossing layers.

After alignment, corresponding ports have identical pairs of labels, and gluing them produces a five-layer cover with the prescribed combined layer. Empty layers may be used to obtain a list (F,C₁,C₂,C₃,C₄).

**Three-cut composition theorem.** A prescribed even subgraph of a three-edge sum has a five-layer completion if and only if its capped restrictions have five-layer completions on both factors. The equivalence iterates along a tree of such sums. Together with the earlier result, it applies to successive two- and three-edge sums. □

The corresponding binary-flow statement also holds. The three nonzero cut values have XOR zero and hence are pairwise distinct. Capping creates a valid cubic flow vertex; compatible factor flows glue when their corresponding port values agree.

Consequently, for a compatible family of factor flows, the set of completable coordinate normals is the intersection of the sets for the factors. This explains how locally available choices can disappear on composition. The general importance of eliminating small cyclic cuts is established in the literature; for example, [Hägglund's introduction](https://arxiv.org/html/1203.2015v1#S1) discusses minimal counterexamples among cyclically 4-edge-connected snarks. The prescribed-layer argument above is given in full rather than assumed from that reduction.

## A 26 vertex obstruction with no smaller edge cut

Use the Petersen edge order from the [preceding construction](layer-selection-obstruction.md#an-explicit-30-vertex-construction): outer edges e₀,…,e₄, spokes e₅,…,e₉, and inner edges e₁₀,…,e₁₄. Start from

\[
p=(2,7,2,7,1,3,5,5,5,6,2,4,7,1,1).
\]

The three copies P₀,P₁,P₂ carry flows Tᵢp. Binary vectors are encoded by integers, and the maps are specified on the basis (1,2,4):

| Block | Tᵢ(1), Tᵢ(2), Tᵢ(4) | Normals giving Petersen 2-factors |
|---|---|---|
| P₀ | 1, 2, 4 | 1, 3, 7 |
| P₁ | 3, 1, 4 | 1, 2, 5 |
| P₂ | 5, 2, 1 | 3, 4, 6 |

Delete vertices 0 and 2 from P₀, and vertex 0 from each leaf P₁,P₂. The two removed vertices in P₀ are nonadjacent. Pair the half-edges as follows, using their original Petersen edge indices:

| Join | Central half-edge ↔ leaf half-edge | Common flow value |
|---|---|---:|
| P₀ vertex 0 ↔ P₁ vertex 0 | e₀ ↔ e₅ | 2 |
| | e₄ ↔ e₀ | 1 |
| | e₅ ↔ e₄ | 3 |
| P₀ vertex 2 ↔ P₂ vertex 0 | e₁ ↔ e₅ | 7 |
| | e₂ ↔ e₀ | 2 |
| | e₇ ↔ e₄ | 5 |

There are 8+9+9=26 remaining vertices and 39 edges. Conservation is preserved because each replacement port has the original value. All maps are invertible and all flow values are nonzero.

The verifier examines **all 9,919 sets of one, two, or three edges**. None of size one or two disconnects the graph. Exactly 28 sets of size three do: 26 isolate a vertex, and two separate a nine-vertex leaf from the other 17 vertices. Both of the latter cuts have circuits on each side. Thus the graph is 3-edge-connected and has exactly the two displayed cyclic three-edge cuts. It is not cyclically 4-edge-connected.

For every nonzero normal ℓ, at least one block in the first table has a Petersen 2-factor as its capped coordinate support. A CDC containing the global Fℓ as a whole layer would cap to a CDC containing that 2-factor. The previous elementary obstruction excludes this: every remaining circuit would have length eight, while the remaining required total is 20 edge occurrences.

Hence all seven coordinate supports are impossible, with no restriction on how the other flow coordinates might be changed while preserving the chosen support. Their sizes and complement counts are:

| ℓ | Edges in Fℓ | Circuits in Fℓ | Components of G−E(Fℓ) |
|---|---:|---:|---:|
| 1 | 22 | 3 | 9 |
| 2 | 22 | 2 | 9 |
| 3 | 24 | 3 | 11 |
| 4 | 24 | 3 | 11 |
| 5 | 22 | 3 | 9 |
| 6 | 20 | 2 | 7 |
| 7 | 22 | 2 | 9 |

This is an explicit example, not a claim of minimum order.

### The graph still has a five-layer cover

Take the explicit Petersen cover saved in the preceding report. At each join, permute the leaf's layer names to align its three boundary pairs with the central cover. The composition theorem supplies a cover of the combined graph. Its five layers have respectively **15, 17, 17, 18, and 11 edges**, summing to 78=2×39. Direct verification checks even degrees and exact multiplicity two on every edge.

Assign binary labels (4,5,6,7,0) to these five layers and put the XOR of the two incident layer labels on each edge. This gives another nowhere-zero F₂³-flow. Its normal-4 support is the fifth cover layer, and its seven fixed-flow lift-defect counts are

\[
(6,6,4,0,2,2,4),
\]

compared with (4,4,6,6,4,4,6) for the original flow. None of the five constructed layers belongs to the original three-dimensional coordinate subspace. This certifies existence on the example without asserting a general repair rule or a particular circuit-switch path between the two flows.

## Why the same cap is not automatic at four-edge cuts

With five named layers, each boundary edge has one of ten two-element label sets. An admissible boundary assignment must use each layer an even number of times across the cut. Enumerating these assignments gives:

| Cut size | Assignments examined | Satisfy boundary parity |
|---|---:|---:|
| 2 | 100 | 10 |
| 3 | 1,000 | 60 |
| 4 | 10,000 | 640 |

The two- and three-edge cases have the unique respective structures used in the composition proofs, up to relabeling. Four ports allow four types.

To cap four ports using two adjacent cubic vertices, partition the ports into two pairs. If the first pair has label sets A,B, evenness forces the new internal edge to have label set A△B. Boundary parity gives the same set at the other vertex. The cap is a double cover precisely when **|A△B|=2**; it otherwise gives the internal edge multiplicity zero or four.

There are three pair partitions. For each of the 640 parity-valid assignments, the sorted triple of resulting internal-edge multiplicities is one of the following:

| Boundary pattern | Multiplicities over the three caps | Assignments |
|---|---|---:|
| All four ports have the same label pair | 0, 0, 0 | 10 |
| Two distinct, repeated label pairs share a label | 0, 2, 2 | 180 |
| Two distinct, repeated label pairs are disjoint | 0, 4, 4 | 90 |
| Four distinct pairs form a cycle on four layer labels | 2, 2, 4 | 360 |

These types can also be read off from the multigraph whose vertices are layer labels and whose four edges are the port pairs: every label has even degree. Thus the classification follows by enumerating the possible even multigraphs with four loopless edges; the scripts check every labeled assignment separately.

The two types with no valid cap occur in actual covers. Take a cube as two squares joined by four matching edges. The saved certificates give one cover with pair {0,1} on all four matching edges, and another with pairs {0,1},{0,1},{2,3},{2,3}. In each case the square-edge pairs make every layer even and every edge doubly covered. Both boundary states resist all three two-vertex caps.

This establishes a limitation of capping a **given boundary labeling**. It does not exclude a different cover, a larger cap, or a more elaborate method across four-edge cuts. A general decomposition algorithm there must retain more boundary information than simple feasibility of a prescribed layer.

## The saved census implies much stronger finite success

The earlier coordinate-selection experiment tested 215 chosen flows. We can now make a stronger finite deduction from the already completed [first-coordinate census](first_coordinate_census.json), without re-enumerating its flows.

For each graph, let B be its set of **admissible** supports that have no five-layer completion. Across the 4,469 saved graphs there are 1,449 such supports, occurring on 40 graphs. For all **31,068 unordered pairs of distinct members** a,b of the same B, the symmetric difference a△b is absent from B. Every saved failure set is therefore sum-free in the binary cycle space.

In a rank-three nowhere-zero flow, any two distinct nonzero coordinate supports and their symmetric difference are all admissible. If the first two fail, the sum-free property forces the third to succeed. A rank-two nowhere-zero flow gives a three-edge-coloring and already has the empty support as a completable coordinate. Hence **every one of the 97,572,378 saved flow classes has a completable coordinate**.

The scope is all 4,461 connected bridgeless simple cubic graphs through 16 vertices, plus the specified two 18-vertex and six 20-vertex snarks. It is not all graphs through 20 vertices. The audit uses the saved census's established completeness and support classification; it does not recompute 97 million flows. The source file's SHA-256 is recorded in the new certificate.

The 26-vertex example shows that this finite pattern does not generalize even to all 3-edge-connected graphs: its seven coordinate supports contain an entire nonzero three-dimensional binary subspace of failed supports.

## Reproduction and the remaining direction

```bash
python3 research/five-cdc-attempt/three_cut_obstruction.py
python3 research/five-cdc-attempt/verify_three_cut_obstruction.py
```

Files: [constructor and census audit](three_cut_obstruction.py), [complete certificates](three_cut_obstruction.json), and [independent verifier](verify_three_cut_obstruction.py). The verifier uses only the standard library and previously saved independent helpers. It checks the cuts, capped Petersen obstructions, flows, cover, all boundary assignments, both cube examples, and the saved failure sets. It does not import the constructor or a completion solver. No proof-assistant verification is claimed.

The current conclusion is precise: two- and three-edge-cut decomposition permits independent choices of covers on the pieces, but a single global starting flow can encode incompatible choices. Requiring the graph merely to have no two-edge cut does not cure that problem.

The corresponding selection question on **cyclically 4-edge-connected cubic graphs** remains unresolved by this work. More broadly, the 5-CDC existence problem on those remaining pieces is still open here. The four-port analysis identifies boundary data that any further reduction would need to preserve or change deliberately.
