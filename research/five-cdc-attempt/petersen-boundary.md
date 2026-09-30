# Petersen boundary relations and a cover inheritance theorem

**29 September 2026. The general 5-cycle double cover conjecture remains unproved here. This report proves a local extension lemma, a reduction, and a conditional theorem for entire graph families. No claim of novelty over the complete literature is made.**

**Subsequent result:** [A finite algebra for prescribed layers in Petersen chains](petersen-chain-algebra.md) classifies all conditional serial-chain relations into 36 nonzero types, each realized by at most three pieces. It proves both a persistent odd/even boundary obstruction and completion of every prescribed even subgraph on closed Petersen necklaces, with independent certificates. The attachment vertices in general blowups remain an additional constraint.

**Further reduction:** [Joint boundary completion](joint-boundary-completion.md) aligns a given three-bit flow with a compatible cover boundary after at most two internal pentagon switches. Contracting disjoint Petersen pieces preserves five-layer-cover existence exactly, and prescribed-coordinate completion after internal repair is equivalent to completion on that quotient, whose contracted vertices have degree four.

The Petersen four-pole used in the [34-vertex experiment](cyclic-core-completion.md) has a particularly useful property: **every parity-compatible assignment of five-layer cover labels to its four ports extends through the piece**. Ten explicit partial covers prove this, up to permutations of layer names.

This yields a structural result, independent of graph size:

> If a cubic graph G has a five-layer cycle double cover, then both Blowup(G,D) and SemiBlowup(G,D) have one, for every collection D of vertex-disjoint circuits of length at least three. The cover pairs on every retained edge of G can be preserved exactly.

These are Hägglund's two constructions. They are already studied graph families, and related five-cover results for superpositions appear in the literature. The contribution of this checkpoint is an explicit boundary proof, executable construction, and independent verification; it does not establish priority. [Hägglund, Constructions 1–2](https://arxiv.org/html/1203.2015v1#S2); [Liu–Hao–Luo–Zhang, 2023, abstract](https://doi.org/10.1137/22M1472425)

The theorem assumes a cover of the base graph. It does not prove that every bridgeless base graph has one, or extend the earlier statement about selecting a coordinate from **every starting flow** to all these families.

## A ten-state alphabet for five-layer covers

Write the two layer labels carried by an edge as a two-element subset of {0,1,2,3,4}. Encode it by a five-bit vector. The allowed alphabet is

\[
Q=\{x\in\mathbb F_2^5:|x|=2\}.
\]

At a cubic vertex the three edge values must XOR to zero. Three members of Q have this property exactly when they are {a,b}, {a,c}, {b,c} for distinct a,b,c. Consequently this local condition gives exact multiplicity two on every edge and even degree in every layer. Layers may be disconnected or empty.

For a graph piece H with t open ports, define its **boundary relation**

\[
R_H=\{(p_1,\ldots,p_t)\in Q^t:
\text{there is a Q-valued assignment on H with XOR zero at each vertex}\}.
\tag{1}
\]

Summing the vertex equations cancels each internal edge twice. Thus every member of R_H satisfies p₁⊕⋯⊕pₜ=0. Sufficiency is an additional property of a piece, not a consequence of this necessary condition.

## The Petersen four-pole accepts every parity state

Let B be the Petersen graph with adjacent vertices 0 and 1 deleted. Its remaining vertices are 2,…,9. Use the following ordered internal edges:

```text
(2,3), (3,4), (2,7), (3,8), (4,9),
(5,7), (6,8), (7,9), (8,5), (9,6).
```

Append the four semiedges at vertices 4,5,2,6, respectively named a₁,a₂,b₁,b₂. The a ports originally met vertex 0, and the b ports originally met vertex 1. This is the four-pole in Hägglund's construction, with the repository's Petersen labeling.

**Boundary extension lemma.**

\[
R_B=\{(p_1,p_2,p_3,p_4)\in Q^4:p_1\oplus p_2\oplus p_3\oplus p_4=0\}.
\tag{2}
\]

**Proof.** Necessity follows by summing vertex equations. For sufficiency, regard the four port pairs as four edges of a multigraph on the layer labels. Every label has even degree. Its possible forms are four identical edges; two repeated, distinct edges; or a four-cycle. The repeated edges can share a label or be disjoint. Keeping port positions fixed gives one orbit for identical edges, three for repeated edges sharing a label, three for repeated disjoint edges, and three for a four-cycle, under permutations of the five layer names.

The following table supplies an extension for every orbit. A digit indexes the pair in this dictionary:

```text
0=01, 1=02, 2=03, 3=04, 4=12,
5=13, 6=14, 7=23, 8=24, 9=34.
```

The cover word has 14 digits: ten internal edges in the displayed order, followed by a₁,a₂,b₁,b₂. It is a directly checkable certificate: each edge carries a pair and every internal vertex has XOR zero.

| Boundary digits | Full cover word |
|---|---|
| 0000 | 12475150420000 |
| 0011 | 02455170420011 |
| 0077 | 12275157440077 |
| 0101 | 23596280730101 |
| 0110 | 23796829350110 |
| 0157 | 03266085490157 |
| 0175 | 12275399860175 |
| 0707 | 12475110220707 |
| 0715 | 02455100220715 |
| 0770 | 12275117240770 |

Permuting the layer names in these ten words covers all 640 parity-compatible ordered boundaries. The table and the orbit classification prove (2). □

Five available labels matter. The boundary (01,02,01,02) cannot be extended using only labels 0,1,2,3. Quotienting the even-weight subspace of F₂⁴ by the all-ones vector maps each pair to a nonzero element of F₂² and turns such an extension into a proper three-edge coloring of B. The a₁,a₂ port colors would differ, contrary to the Petersen four-pole coloring property. [Hägglund, Lemma 2.2](https://arxiv.org/html/1203.2015v1#S2) The independent verifier also exhausts four-label partial covers and confirms this failure.

## A finite algebra that composes exactly

Index rows of a 100×100 Boolean matrix M_B by (a₁,a₂)∈Q² and columns by (b₁,b₂)∈Q². Equation (2) becomes

\[
M_B[(p,q),(r,s)]=[p\oplus q=r\oplus s].
\tag{3}
\]

The quantity p⊕q is the boundary pair's **charge**, an element of the four-dimensional even-weight subspace of F₂⁵. All 16 charges occur. Charge zero has ten ordered decompositions p=q. Each of the other fifteen charges has six ordered decompositions into members of Q. After grouping states by charge, M_B consists of one 10×10 all-ones block and fifteen 6×6 all-ones blocks. Its total number of ones is 10²+15·6²=640.

Gluing the b ports of one four-pole to the a ports of another is Boolean matrix multiplication: an entry is true when **some** matching intermediate boundary state exists. Therefore

\[
M_B\mathbin{\odot}M_B=M_B.
\tag{4}
\]

Any positive-length serial chain of these Petersen pieces has the same external feasibility relation as one piece. This is an exact statement for chains of arbitrary length, with no graph-size enumeration.

More generally, (1) maps a graph piece to a finite relation. Gluing identifies shared variables and existentially quantifies their common label values. A split into input and output ports turns this operation into Boolean matrix multiplication; larger interfaces give tensors with the same Boolean operations. Local admissibility rules for other finite-label graph problems can be composed in the same way. This supplies a reusable graph-to-algebra connection, while the size and structure of the relations control whether it is useful for a proof.

The choice of algebra is consequential: **M_B²=0 over F₂**, since both possible nonzero counts of intermediate states, six and ten, are even. Boolean multiplication records existence; F₂ multiplication records its parity. Ordinary linear elimination cannot substitute for the existential step. The verifier checks both identities directly. Fixed-boundary feasibility becomes simple here because this particular relation has the complete charge-block form (3).

## Replacing a four-port piece and reducing a counterexample

**Replacement rule.** Suppose a cubic graph already has a five-layer cover. Remove a vertex set with exactly four boundary edges and insert B, joining its ports to the four exposed outside ends in any specified order. The old cover on the outside extends to a five-layer cover of the new graph.

Indeed, the old boundary labels XOR to zero by summing parity over the removed vertices. Equation (2) supplies the extension, while every retained edge keeps its old pair.

There is also a useful reduction in the opposite direction of graph size. Suppose a bridgeless cubic graph G contains B as an induced four-port piece and the subgraph R outside B is connected. Replace B by two adjacent cubic vertices, attaching two ports to each new vertex in any partition. Call the smaller graph G′; it has six fewer vertices and may have parallel edges.

G′ is bridgeless. Every new edge lies on a circuit because R is connected. For an edge e of R, either R−e is connected or it has two components. In the latter case each component has a port: otherwise e would have been a bridge in G. The connected two-vertex cap joins the two sides again, so e is not a bridge in G′. These cases account for all edges.

Every five-layer cover of G′ extends through B by the replacement rule. Thus a smallest counterexample to the 5-CDC conjecture among loopless bridgeless cubic graphs cannot contain such a piece. In a 3-edge-connected graph the outside is automatically connected: two outside components would each require at least three boundary edges, but B has only four. In particular, a smallest counterexample that is 3-edge-connected contains no such copy of B.

The implication is one-way. A particular cover of G can have boundary pairs that do not fit the chosen two-vertex cap, as the [earlier four-cut examples](three-cut-completion.md#why-the-same-cap-is-not-automatic-at-four-edge-cuts) demonstrate.

## Proof of cover inheritance for both blowup constructions

Take a five-layer cover of G and a circuit C=(v₀,…,vₖ₋₁) in D. Write sᵢ∈Q for the pair on vᵢvᵢ₊₁ and rᵢ∈Q for the pair on the third edge at vᵢ. Subscripts are modulo k. The vertex condition gives rᵢ=sᵢ₋₁⊕sᵢ.

At each vᵢ, independently write

\[
s_{i-1}=\{a,b\},\qquad s_i=\{a,c\},\qquad r_i=\{b,c\},
\]

and choose a label d outside {a,b,c}. There are two choices. Write xy for {x,y}. The letters a,b,c,d in the following assignments are local to this vertex.

For **SemiBlowup**, attach the ports as in Construction 1: b₁ⁱ meets vᵢ, a₁ⁱ⁻¹ meets vᵢ, and a₂ⁱ⁻¹ is joined to b₂ⁱ. Assign

\[
(a_1^{i-1},a_2^{i-1})=(bd,ad),\qquad
(b_1^i,b_2^i)=(cd,ad).
\tag{5}
\]

The joined ports agree. The three pairs at vᵢ are bd,cd,bc, a label triangle. The a pair of Bᵢ₋₁ has XOR ab=sᵢ₋₁, and the b pair of Bᵢ has XOR ac=sᵢ.

For **Blowup**, let uᵢ meet a₁ⁱ⁻¹,b₁ⁱ,vᵢ and let wᵢ meet a₂ⁱ⁻¹,b₂ⁱ,vᵢ, as in Construction 2. Assign

\[
(a_1^{i-1},a_2^{i-1})=(ad,bd),\qquad
(b_1^i,b_2^i)=(ab,bc),
\]
\[
v_i u_i=bd,\qquad v_i w_i=cd.
\tag{6}
\]

The three pairs at uᵢ are ad,ab,bd; at wᵢ they are bd,bc,cd; and at vᵢ they are bd,cd,bc. Each is a label triangle. Again the a and b pair XORs are sᵢ₋₁ and sᵢ, respectively.

Consequently, in either construction **both port pairs of Bᵢ have XOR sᵢ**. Its full boundary satisfies (2), and the extension lemma fills all its internal edges. Repeat for every inserted piece and every circuit of D. All new vertices have even layer degrees; all edges carry exactly two labels; and every retained edge has its original pair. This proves the theorem. □

The local choices have no further global matching condition, because B accepts every boundary with the required charge. Once a base cover is given and the fixed table is prepared, the construction takes time linear in the output graph size. It can be iterated any number of times. For example, prisms Cₖ□K₂ have an even Hamilton circuit; alternating two edge colors on it and using a third on the remaining matching gives a three-layer cover. The theorem therefore supplies covers for both blowup families over these prisms for every k≥3.

## Why prescribing a layer retains an obstruction

Fix a particular binary even subgraph F inside B, including its semiedge memberships, and require it to be layer 0. There are 64 such binary subgraphs. The finer relation

\[
R_{B,F}=\{p\in R_B:\text{some extension has layer 0 exactly F}\}
\]

cannot be recovered from boundary parity alone. An exhaustive calculation gives:

| Number of ports in F | Pairs (F,boundary) compatible with parity and port membership | Have an extension with layer 0 exactly F |
|---|---:|---:|
| 0 | 1,344 | 1,020 |
| 2 | 3,456 | 2,976 |
| 4 | 320 | 224 |
| **Total** | **5,120** | **4,220** |

Thus 900 candidate states are impossible. Every individual F does have some extension on the isolated piece; the obstruction concerns matching it to an imposed boundary.

For a concrete case, in the 14-edge order above take F with mask 15609 or 16270. Each uses all four ports and has degree two at every internal vertex. Its allowed boundary assignments are exactly

\[
(0x,0x,0y,0y),\qquad x,y\in\{1,2,3,4\},
\tag{7}
\]

giving 16 states instead of all 40 parity-compatible states with all ports in layer 0. Necessity also has a short explanation: if the two a ports had different partner labels, their XOR would be a valid two-label value for a restored edge 01. Boundary parity would give the same value at the restored other vertex. Capping would then yield a Petersen cover containing a spanning 2-factor as a whole layer, excluded by the [earlier Petersen obstruction](layer-selection-obstruction.md). If the a port pairs agree, parity forces the b port pairs to agree. The saved witnesses verify sufficiency of all sixteen choices for each of the two masks.

The inheritance theorem is free to choose the internal layers of every piece. The seven-coordinate question fixes those internal memberships through the starting flow. Relation (7) shows exactly where that additional requirement can defeat unrestricted boundary extension. The theorem here therefore gives a family-level existence method while leaving the stronger selection question open.

## Reproduction and independent checks

```bash
python3 research/five-cdc-attempt/petersen_boundary.py
python3 research/five-cdc-attempt/verify_petersen_boundary.py
```

Both scripts use only Python's standard library. The [constructor](petersen_boundary.py) enumerates compatible label triangles at the eight vertices, finding **14,700 named partial covers**. It saves the ten representative words, one witness for each of the **4,220** prescribed-layer states, and sixteen lifted graph covers.

The [independent verifier](verify_petersen_boundary.py) does not import the constructor. It first checks the ten words and all their label permutations. It then independently enumerates the 64 binary even supports and selects five supports whose ordinary edge multiplicities are exactly two. This gives the same 14,700 covers and exactly the same 4,220 projected states, certifying both feasibility and the 900 omissions. It also checks the Boolean and F₂ matrix products, the four-label obstruction, all **240** choices in formulas (5)–(6), and the sixteen graph constructions.

The graph certificates include Blowup(K₄,C₃), both constructions on several prisms, multiple disjoint replacement circuits, the Petersen graph with its spanning two-factor, and a second iteration on a previously expanded graph. They range from 28 to 110 vertices. The checker verifies the graph topology against the construction, even layer degrees, exact edge coverage, and retention of the original pairs outside D. The infinite-family theorem follows from the displayed proof; these finite examples check its implementation.

Files: [metadata and graph covers](petersen_boundary.json), [compressed prescribed-layer witnesses](petersen_boundary_relation.txt.gz), [constructor](petersen_boundary.py), and [independent verifier](verify_petersen_boundary.py). No SAT solver or proof assistant is required or claimed. The constructor reuses the already verified Petersen seed cover from the preceding checkpoint.

The [next report](petersen-chain-algebra.md) controls conditional boundary relations such as R_{B,F} on arbitrary serial chains. Branching attachment vertices and useful reductions in graphs without this Petersen piece remain unresolved. Charge conservation supplies an exact composition law for unrestricted covers here; it does not yet supply a universal five-layer existence proof.
