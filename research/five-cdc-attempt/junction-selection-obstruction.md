# All seven coordinates can fail at cyclic edge connectivity four

**30 September 2026. The general 5-cycle double cover conjecture remains unproved here. This report disproves the proposed universal seven-coordinate selection rule even on cyclically four-edge-connected cubic graphs. The graphs constructed below have explicit five-layer covers. No claim of novelty over the complete literature is made.**

There is a simple **72-vertex cubic graph of girth five and cyclic edge connectivity four** with a nowhere-zero F₂³-flow f for which every nonzero coordinate support

\[
F_\ell=\{e:\ell\cdot f(e)=1\},\qquad 0\ne\ell\in\mathbb F_2^3,
\tag{1}
\]

is impossible as one whole layer of a cycle double cover, **regardless of the number of layers**. All seven supports are nonspanning and disconnected. Selecting a different coordinate, or making arbitrary changes to the other coordinates while preserving one of these supports, cannot complete that support to a cover.

The construction repeats to an infinite family on 72m vertices, m≥1, with the same obstruction and with five-layer covers. On the 72-vertex example, one valid switch along a five-edge circuit produces a new flow with a completable coordinate.

This settles negatively the selection question left open by the [34-vertex experiment](cyclic-core-completion.md). It does not conflict with that experiment's positive theorem about every flow on its particular graph. The [30-vertex](layer-selection-obstruction.md) and [26-vertex](three-cut-completion.md) counterexamples depended on small cyclic cuts; those mechanisms are absent here.

## 1. Branching junctions change the charge

For a cover with L named layers, let

\[
Q_L=\{x\in\mathbb F_2^L:|x|=2\}.
\]

An edge carries the pair of layers containing it. At each cubic vertex the three pairs XOR to zero, and each named layer has degree zero or two. This description enforces exact edge multiplicity two, for any finite L.

The [chain algebra](petersen-chain-algebra.md) composed four-poles by matching two ports directly. Hägglund's Blowup construction inserts a three-vertex junction. Let (A₁,A₂) be the a-port pairs of the preceding Petersen piece and (B₁,B₂) the b-port pairs of the next piece. The junction has vertices u,w,v and pairs X on uv, Y on wv, and R on the third edge at v. The vertex equations are exactly

\[
X=A_1\oplus B_1,\qquad Y=A_2\oplus B_2,\qquad
R=X\oplus Y.
\tag{2}
\]

Define the two adjacent piece charges by α=A₁⊕A₂ and β=B₁⊕B₂. Equation (2) gives the decisive condition

\[
\boxed{R=\alpha\oplus\beta\in Q_L.}
\tag{3}
\]

For a fixed R, the exact junction relation additionally requires X,Y∈Q_L. In SemiBlowup the second rail goes straight through: the exact relation instead requires A₂=B₂ and A₁⊕B₁=R. Equation (3) holds there as well. These formulas follow directly from the definitions of [Hägglund's Constructions 1–2](https://arxiv.org/html/1203.2015v1#S2).

With five labels, direct enumeration gives 2,160 assignments for the Blowup junction and 600 for the SemiBlowup junction. They realize respectively all 16 and all eight binary even membership patterns on the junction variables. The verifier rebuilds these assignments by choosing label triangles at the internal vertices, independently of the constructor's boundary-first enumeration. Fixing a layer merely restricts each variable to pairs with its specified membership in label 0.

For five layers, these junctions also give an exact transfer formulation. Retain the earlier matrix Tᵢ mapping the a-port state of piece i to its b-port state, with its local layer fixed. Let Jᵢ map the preceding a-port state to the current b-port state through the junction, fixing its layer memberships and the retained edge pair Rᵢ. Completion around an expanded circuit is equivalent to a nonzero Boolean trace of

\[
J_0T_0^{\mathsf T}J_1T_1^{\mathsf T}\cdots J_{k-1}T_{k-1}^{\mathsf T}.
\tag{4}
\]

The transpose traverses each piece from b to a. This criterion is exact once the retained edge pairs are specified consistently, including the vertex conditions outside the expanded circuits. Shared retained edges still couple different circuits. Charge equation (3) is a necessary projection of these full relations; it alone need not be sufficient for completion.

## 2. Two local prescribed-layer types cannot meet

Use the Petersen graph with outer edges (i,i+1 mod 5), spokes (i,i+5), and inner edges (i+5,i+2 mod 5+5). Delete adjacent vertices 0 and 1 to obtain B. The internal edge order and four ports are

```text
(2,3), (3,4), (2,7), (3,8), (4,9),
(5,7), (6,8), (7,9), (8,5), (9,6),
a1 at 4, a2 at 5, b1 at 2, b2 at 6.
```

The 14-bit mask of a local subgraph includes its port memberships. Restrict each of the Petersen graph's six spanning 2-factors to B. Two types result:

| Type | Local masks | Removed edge 01 in the factor? | Port membership | Necessary cover charge |
|---|---|---|---|---|
| Z | 15609, 16270 | No | All four ports | 0 |
| W | 6115, 6782, 10045, 10711 | Yes | One port in each pair | Weight four, including label 0 |

Here the distinguished prescribed layer is named 0. These charge restrictions hold for **any number of cover labels**, not just five.

**Proof.** Recall why a spanning 2-factor of the Petersen graph cannot be a whole CDC layer. It consists of two pentagons, with the complementary perfect matching joining them. After using that layer, every circuit in every remaining layer must alternate between factor edges and matching edges. Each such circuit crosses between the pentagons an even number of times, so its length is divisible by four. Girth five and the ten-vertex bound force length eight. The remaining 20 edge occurrences cannot be a sum of eights. This is the [earlier Petersen obstruction](layer-selection-obstruction.md#a-local-obstruction-in-petersen), with the argument recalled here to make the present deduction explicit.

Now suppose a cover of B has one of the six restricted factors as layer 0. If its charge α were in Q_L, restore vertices 0,1 and put pair α on edge 01. The two new vertex equations hold. Label-0 membership on edge 01 is the XOR of the memberships of its two neighboring ports, exactly restoring the original spanning factor. This would give the forbidden Petersen cover. Thus α∉Q_L.

For type Z, both a-port pairs contain label 0, so their XOR has weight zero or two. Excluding Q_L leaves only zero. For type W, precisely one a-port pair contains label 0, so their XOR contains label 0 and has weight two or four. Excluding Q_L forces weight four. Boundary parity makes the b-port charge identical. □

**Junction obstruction.** A type-Z piece cannot meet another type-Z piece or a type-W piece across either junction described above, in a cover containing the prescribed layer. In the Z–Z case equation (3) would give R=0. In the Z–W case it would give |R|=4. Each contradicts |R|=2. The contradiction depends only on the two local restrictions; changing the cover anywhere else cannot remove it.

## 3. A flow that blocks all seven coordinates

Let k=6m, and start from the prism Cₖ□K₂. Write vᵢ for the top ring and tᵢ for the bottom ring, with matching edges vᵢtᵢ. Apply Blowup along the top ring. Piece Bᵢ has its b ports attached to uᵢ,wᵢ, and its a ports attached to uᵢ₊₁,wᵢ₊₁. The remaining edges are vᵢuᵢ, vᵢwᵢ, vᵢtᵢ, and the bottom-ring edges. Indices are cyclic.

For m=1 there are 12 original vertices, 48 vertices in the six Petersen pieces, and 12 auxiliary vertices, giving 72 vertices and 108 edges. More generally there are 72m vertices and 108m edges.

Assign the following nowhere-zero three-bit flow values inside successive pieces, repeating the six-row pattern. A word's 14 digits use the displayed local edge order. The digits 1,…,7 now denote vectors in F₂³, not cover-pair indices.

| i mod 6 | Local flow word | Flow charge hᵢ=a₁ⁱ⊕a₂ⁱ | vᵢuᵢ | vᵢwᵢ | vᵢtᵢ |
|---:|---|---:|---:|---:|---:|
| 0 | `15543237746547` | 3 | 7 | 2 | 5 |
| 1 | `56734156622727` | 5 | 4 | 2 | 6 |
| 2 | `63752166341212` | 3 | 3 | 5 | 6 |
| 3 | `46724166422534` | 7 | 2 | 6 | 4 |
| 4 | `23312724361414` | 5 | 3 | 1 | 2 |
| 5 | `12431175443553` | 6 | 4 | 7 | 3 |

Every local vertex has XOR zero, and each piece's two flow charges agree. The two auxiliary spoke values are forced by

\[
f(v_i u_i)=a_1^{i-1}\oplus b_1^i,\qquad
f(v_i w_i)=a_2^{i-1}\oplus b_2^i.
\]

Assign f(vᵢtᵢ)=hᵢ₋₁⊕hᵢ and f(tᵢtᵢ₊₁)=hᵢ. All displayed values and all hᵢ are nonzero. These equations verify conservation at uᵢ,wᵢ,vᵢ,tᵢ, including the seam between repetitions. Thus this is a nowhere-zero F₂³-flow for every m≥1. Its values include a basis of F₂³, so the seven supports in (1) are distinct.

The following table identifies one obstructing junction for each normal on the 72-vertex graph. Block numbers are modulo six. The bits of a normal are interpreted in the same least-significant-bit-first convention as the flow values.

| Normal ℓ | Edges in Fℓ | Circuit components | Adjacent blocks | Local masks | Types |
|---:|---:|---:|---|---|---|
| 1 | 57 | 2 | 5, 0 | 15609, 10711 | Z, W |
| 2 | 63 | 4 | 1, 2 | 16270, 10711 | Z, W |
| 3 | 60 | 4 | 1, 2 | 6115, 15609 | W, Z |
| 4 | 60 | 5 | 0, 1 | 16270, 10711 | Z, W |
| 5 | 63 | 6 | 4, 5 | 16270, 10045 | Z, W |
| 6 | 67 | 3 | 5, 0 | 16270, 6782 | Z, W |
| 7 | 62 | 5 | 3, 4 | 10045, 15609 | W, Z |

Each row contradicts equation (3) if Fℓ is assumed to be a whole CDC layer. No search over global covers is needed for this conclusion. In longer graphs the same local pattern repeats, so the same seven contradictions remain. The support sizes scale by m and remain smaller than 72m.

These are obstructions to including an entire disconnected even subgraph as one layer. They do not disprove the strong CDC conjecture about a single prescribed circuit.

## 4. There are no small cyclic cuts

The independent verifier checks all

\[
\binom{108}{1}+\binom{108}{2}+\binom{108}{3}=210{,}042
\]

edge-deletion sets on the 72-vertex graph. None of sizes one or two disconnects it. Exactly 72 sets of size three disconnect it, and each is the star of a single vertex. The four edges leaving any displayed Bᵢ separate an eight-vertex side from a 64-vertex side, both containing circuits. Hence cyclic edge connectivity is exactly four. A separate breadth-first check gives girth five.

For the infinite family, the prism Cₖ□K₂ is cyclically four-edge-connected when k≥4. Indeed, describe a vertex subset by its top and bottom index sets A,B. Its cut has size

\[
|\delta_{C_k}(A)|+|\delta_{C_k}(B)|+|A\mathbin\triangle B|.
\]

If both A and B are nonempty proper subsets, the first two terms already sum to at least four. If just one is proper, a nonempty cut of size at most three can only isolate a single vertex on one side. If neither is proper, a nontrivial cut separates the rings and has size k≥4.

Hägglund states that the blowup constructions applied to a cubic base with no cyclic edge cut of size at most three produce cyclically four-edge-connected snarks. Applying this preservation property proves the assertion for all k=6m. The four-edge boundary of an inserted piece gives equality rather than just a lower bound. The finite verifier establishes the primary 72-vertex case directly, independently of this cited preservation property. [Hägglund, Section 2, following Theorem 2.5](https://arxiv.org/html/1203.2015v1#S2)

## 5. The graphs have covers, and the starting flow can be repaired

Every prism has a proper three-edge coloring: its even Hamilton circuit can be colored alternately with two colors, and its remaining matching with a third. Pairing the three colors gives a three-layer cover. The [proved blowup inheritance theorem](petersen-boundary.md#proof-of-cover-inheritance-for-both-blowup-constructions) therefore supplies a five-layer cover for every graph in this family. The saved certificates include actual covers on 72, 144, and 216 vertices.

There is also a small explicit escape from the 72-vertex example's bad flow. Inside B₀, switch on the five-cycle

\[
2,3,4,9,7,2
\]

by adding vector 4 to its five flow values. Its local edge indices are 0,1,2,4,7, and none originally has value 4, so no zero is introduced. Each circuit vertex receives the same addition twice, preserving conservation. With the certificate's global numbering, these are edges 12,13,14,16,19.

The new normal-4 support has 59 edges. An explicit five-layer cover in the certificate has precisely that support as layer 0. This positive witness was found with a cover solver during exploration; both saved scripts reproduce or verify it without that solver. The switch is an escape for this example, not a general repair theorem.

## 6. A stronger explanation of the earlier 34-vertex failures

The same argument explains the three negative supports in [Blowup(K₄,C₃)](cyclic-core-completion.md):

| Normal | Local masks on B₀,B₁,B₂ | Obstructing adjacent blocks |
|---:|---|---|
| 1 | 15609, 6115, 887 | B₀(Z), B₁(W) |
| 2 | 16270, 3485, 15609 | B₂(Z), B₀(Z) |
| 3 | 887, 6782, 16270 | B₁(W), B₂(Z) |

The earlier DRUP certificates excluded five-layer covers. The charge argument now excludes **any number of layers** containing these supports, with a short structural proof. The independent verifier checks the old graph topology, flow, projections, and the three local contradictions against the saved certificate. Its theorem that some other coordinate works for every flow on that 34-vertex graph remains valid.

## 7. Reproduction and what remains

```bash
python3 research/five-cdc-attempt/junction_selection_obstruction.py
python3 research/five-cdc-attempt/verify_junction_selection_obstruction.py
```

The [constructor](junction_selection_obstruction.py) saves the [graph, flow, cover, and local certificates](junction_selection_obstruction.json). The [independent verifier](verify_junction_selection_obstruction.py) uses only the standard library and imports no constructor or earlier verifier. It checks all six Petersen factor restrictions and the premises of their counting obstruction; both junction relations; all graph topologies, flows, and positive covers; seven negative witnesses in each of three family examples; every edge-deletion set of size at most three for the primary graph; the five-edge switch; and the three strengthened older obstructions.

The negative proof does not rely on a solver's nonexistence verdict, on sampling, or on assuming that all allowed charges can be independently realized. Necessary charge restrictions alone give the contradictions. The infinite-family assertions follow from the repeated flow formulas, the local obstruction, cover inheritance, and the cited connectivity preservation, rather than from finite testing. No minimum-order claim or proof-assistant verification is made.

The universal rule “select a completable coordinate from every nowhere-zero three-bit flow after eliminating small cyclic cuts” is now ruled out by this work. The general 5-CDC existence problem still asks for **some suitable flow or cover**. A continuing flow-based approach must allow changes to the flow itself; the explicit circuit switch illustrates that distinction, while the earlier [repair obstructions](repair-obstruction.md) prevent assuming that a simple monotone repair rule always succeeds.
