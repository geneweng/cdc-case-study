# Petersen flow repair: local bounds and an infinite family

**30 September 2026. The general 5-cycle double cover conjecture remains unproved here.** This continuation establishes exact finite reconfiguration bounds inside a Petersen four-pole, and proves that every nowhere-zero three-bit flow on the preceding 72m-vertex family can reach a flow with a completable coordinate. The latter is a deduction from an existing short-cycle contraction theorem, applied to an explicit contraction sequence. No literature-wide novelty claim is made.

The [preceding obstruction](junction-selection-obstruction.md) concerns a *fixed* flow: none of its seven coordinate supports can be a whole layer of any CDC. Here the flow is allowed to change. For that particular starting flow on 72m vertices, the minimum number of switches confined to individual Petersen pieces is **exactly m**. The endpoint has an explicit five-layer cover containing its normal-4 support.

**Continuation:** [One global circuit repairs every repetition](global-circuit-repair.md) determines the unrestricted distance: it is exactly one, via a winding circuit of length 13m. The distance remains exactly m if every switch has length at most seven. The continuation also extends quantitative lifting to multiple disjoint pieces and exhibits the necessity of preparation in that lifting model.

Throughout, a switch adds one nonzero vector a∈F₂³ along one connected circuit, provided that a is absent from its edges. All intermediate flows must remain nowhere-zero. A k-layer CDC consists of at most k even subgraphs, each possibly disconnected. We distinguish a completable coordinate from the more restrictive palette-dependent defect criterion in the original attempt.

## 1. Every fixed-boundary Petersen flow can be changed locally

Use the four-pole B obtained by deleting adjacent vertices 0,1 from the Petersen graph. Its ten internal edges and four port edges, in order, are

```text
(2,3), (3,4), (2,7), (3,8), (4,9),
(5,7), (6,8), (7,9), (8,5), (9,6),
a1 at 4, a2 at 5, b1 at 2, b2 at 6.
```

A local flow assigns a nonzero vector to all fourteen edges, with XOR zero at each of the eight internal vertices. Its boundary is the ordered tuple p=(a₁,a₂,b₁,b₂). Necessarily p₁⊕p₂⊕p₃⊕p₄=0. There are 301 such nonzero boundary tuples, and **all 301 occur**.

**Finite local theorem.** For every boundary p:

1. Any two local flows with boundary p are joined by at most three internal circuit switches. The reconfiguration graph has diameter exactly three.
2. If only internal pentagons may be switched, the graph still remains connected and has diameter exactly four.
3. From any local flow, at most two pentagon switches reach a flow for which none of the seven coordinate supports has any of the six factor-restriction masks
   \[
   Z=\{15609,16270\},\qquad W=\{6115,6782,10045,10711\}.
   \]
   The boundary remains fixed throughout.

These are exhaustive finite statements, independently checked by two different enumerations. They are not extrapolations from sampled flows.

The internal graph has precisely seven circuits. Their edge masks are

| Length | Circuit masks |
|---|---|
| 5 | 151, 301, 602, 992 |
| 6 | 442, 717 |
| 8 | 887 |

GL(3,2) acts on flow values and boundary tuples. Its 168 invertible maps preserve allowable switches and permute the seven coordinate supports. The 301 boundaries split into the five orbits below. All flow words retain named vector values; internal graph automorphisms are not used in these counts.

| Boundary representative | Boundary orbit size | Flows in one fiber | Switch edges, all circuits | Switch edges, pentagons | States with no Z/W support | Pentagon distance to that set: 0 / 1 / 2 |
|---|---:|---:|---:|---:|---:|---|
| (1,1,1,1) | 7 | 102 | 927 | 528 | 24 | 24 / 72 / 6 |
| (1,1,2,2) | 42 | 118 | 1086 | 680 | 52 | 52 / 64 / 2 |
| (1,2,1,2) | 42 | 108 | 894 | 572 | 12 | 12 / 48 / 48 |
| (1,2,2,1) | 42 | 108 | 894 | 572 | 12 | 12 / 48 / 48 |
| (1,2,4,7) | 168 | 116 | 1030 | 664 | 24 | 24 / 88 / 4 |

The orbit-weighted total is 34,230 local flows. The certificate contains all 552 words in the five representative fibers, exact distance histograms, pairs attaining both diameters, and a sequence of at most two pentagon switches for each word.

For completeness of the orbit classification, a nonzero zero-sum tuple either has all entries equal, consists of two equal pairs in one of three positions, or has four distinct entries. In the last case any three form a basis: a dependence among them would force the fourth to be zero. These are exactly the five displayed types.

Removing these masks removes the specific adjacent Z–Z and Z–W charge contradictions. It does **not** establish that any coordinate is globally completable: other boundary compatibility conditions remain. In an ambient graph containing q vertex-disjoint copies of B, the clearing operations can be performed independently in at most 2q pentagon switches, with every edge outside their interiors fixed.

## 2. Switches through a contracted piece can be lifted

The following stronger finite check permits boundary changes.

**Preparation lemma.** Let f be any local flow, choose two distinct ports p,q, and choose nonzero a different from their two flow values. After at most one internal pentagon switch, there is a simple internal path of length at most three between the selected port vertices on which a is absent.

Adding a on this path and the two port edges changes exactly those two boundary values and preserves all internal vertex equations. Their new values remain nonzero by the hypothesis on a. The enumeration checks all **9,324** choices of boundary tuple, unordered port pair, and allowable increment, transporting the five representative computations by the explicit linear maps. For every local starting flow, readiness has distance zero or one in the pentagon reconfiguration graph.

This yields a useful reduction with precise hypotheses. Suppose a loopless graph G contains an **induced** copy of the internal graph B, with exactly its four port edges leaving it and no other incident edges. Let H=G/B, deleting the internal edges; parallel edges in H are allowed. Restriction gives a surjection from nowhere-zero F₂³-flows of G to those of H, because every nonzero zero-sum four-port tuple extends.

**Contraction deduction.** Restriction induces a bijection between the connected components of the two flow reconfiguration graphs. If the restrictions of flows f,g on G are at distance d in H, then

\[
\operatorname{dist}_{G}(f,g)\le 2d+3.
\]

**Proof.** A switch in H that avoids the contracted vertex lifts unchanged. A circuit using that vertex selects two port edges. Apply the preparation lemma to the current local flow, and replace the contracted vertex's passage by its internal path. The resulting circuit in G is simple, and its increment is absent from every edge. Thus each quotient move lifts in at most two switches. At the end, f and the desired target g agree outside B; at most three internal switches align them.

Conversely, a circuit switch in G restricts either to nothing or to an even edge set in H. Decompose that set into edge-disjoint circuits and apply the same increment separately. Every intermediate value is either its original or final nonzero value. Hence projection cannot join previously separate components. Together with surjectivity and connected fibers, this proves the component bijection. □

This is a reduction for **flow reachability**. It neither preserves a prescribed CDC layer during the intermediate moves nor proves that some layer on H can be lifted with an arbitrary prescribed restriction inside B.

## 3. All flows in the 72m-vertex family can be repaired

Write Gₘ for the preceding Blowup(C₆ₘ□K₂, top ring), with k=6m. Its pieces are Bᵢ; their ports attach to uᵢ,wᵢ and uᵢ₊₁,wᵢ₊₁. Each vᵢ is adjacent to uᵢ,wᵢ,tᵢ, and the tᵢ form the bottom ring. The graph has 12k=72m vertices.

We use the following existing result. Cranston, Li, Su, Wang, and Xu prove that contracting an A-flow-reconfiguration-contractible subgraph preserves flow connectedness in both directions. For A=F₂³, every circuit of length at most seven has that property. Parallel two-edge circuits are included. [Theorem 5.9 and Corollary 5.14, arXiv:2606.24685v1](https://arxiv.org/html/2606.24685v1#S5.SS2)

Here is an explicit sequence using only lengths two through five; loops created by contraction are discarded.

1. In each Bᵢ, contract its pentagon (2,3,4,9,7). The remaining internal graph is two triangles sharing an edge. Contract the triangle through the images of 2,5,8, then the resulting digon through the image of 6. Each Bᵢ becomes one vertex bᵢ.
2. For i=0,…,k−2, contract the four-cycle (bᵢ₋₁,uᵢ,bᵢ,wᵢ), with previously merged b vertices understood as their common image. Contract the resulting digon to vᵢ. At the last junction, contract the digons to uₖ₋₁, wₖ₋₁, and vₖ₋₁. All b,u,w,v vertices now form one hub.
3. The remainder is a wheel with rim t₀,…,tₖ₋₁. Contract the hub–t₀–t₁ triangle, then the successive digons to t₂,…,tₖ₋₁. One vertex remains.

There are 3k digon contractions, k+1 triangle contractions, k−1 four-cycle contractions, and k pentagon contractions: **6k=36m steps** in total. Every step is visibly available for k≥6. The supplied verifier additionally checks the actual surviving edge IDs throughout this process for m=1,2,3,10, including parallel-edge circuits and the final one-vertex quotient.

The terminal graph has a single empty flow, so repeated application of the cited theorem proves that **the entire nowhere-zero F₂³-flow reconfiguration graph of Gₘ is connected**, for every m≥1. Section 4 gives one flow gₘ with a coordinate that is an explicit five-layer-cover layer. Consequently every starting flow on Gₘ can reach such a flow.

The qualitative reduction through an individual Petersen piece also follows from its pentagon–triangle–digon contraction above. The independent finite checks in Sections 1–2 add exact diameters, a one-pentagon preparation bound with a three-edge path, and clearing certificates. We do not present qualitative short-cycle contraction as a new theorem.

This establishes unrestricted reachability for this family. It does not impose monotonicity on the original defect potential or bound the lengths of lifted circuits independently of m. The exact unrestricted repair distance of the specified starting flow is determined in the [continuation](global-circuit-repair.md).

## 4. Exact distance when switches stay inside pieces

Let fₘ be the periodically repeated bad flow from the preceding report. Define its repair distance using only switches whose circuit lies wholly in one Bᵢ. The target is **any flow with at least one coordinate support that can be a whole layer of a CDC**, with any number of layers permitted.

**Exact-distance theorem.** This distance is m. A shortest repair ends with a five-layer completion of normal 4.

**Lower bound.** For each normal ℓ, retain the following m obstructing pairs of pieces, indexed by r=0,…,m−1. Piece indices are modulo 6m.

| Normal ℓ | Pair for repetition r | Types |
|---:|---|---|
| 1 | (6r+5, 6r+6) | Z, W |
| 2 | (6r+1, 6r+2) | Z, W |
| 3 | (6r+1, 6r+2) | W, Z |
| 4 | (6r, 6r+1) | Z, W |
| 5 | (6r+4, 6r+5) | Z, W |
| 6 | (6r+5, 6r+6) | Z, W |
| 7 | (6r+3, 6r+4) | W, Z |

For a fixed normal these pairs are disjoint as sets of pieces. A switch inside one piece can touch at most one retained pair for that normal. After fewer than m switches, each normal still has at least one pair in which neither piece has changed. Its original local masks persist.

Recall the charge contradiction: a type-Z restriction forces cover charge zero, and a type-W restriction forces weight four, for any number of cover labels. The junction's third edge must carry their XOR, which must have weight two. A surviving Z–W pair makes that impossible. Thus all seven coordinates remain noncompletable after fewer than m allowed moves, regardless of how the normal is selected at the end. This proves the lower bound without counting the other, potentially changing obstructions.

**Upper bound.** In each B₆ᵣ, add vector 4 along the pentagon (2,3,4,9,7,2), whose local edge indices are 0,1,2,4,7. These m circuits are disjoint, and none has value 4 in fₘ. The moves commute and remain valid in any order.

The graph Gₘ has a natural m-sheeted covering projection onto G₁, reducing every piece and ring index modulo six. The resulting flow gₘ is exactly the lift of the previously certified one-switch flow g₁. Lift its explicit five-layer cover edge by edge. The graph projection maps every vertex star bijectively onto its image, so degree zero-or-two for each label and multiplicity two on each edge are preserved. Layer 0 is exactly the normal-4 support of gₘ, with **59m edges**.

The certificate repeats the four edge classes separately—bottom edges, stems, piece interiors, and junctions—so it preserves the original edge order and the cyclic seam. The independent checker validates the graph covering map, all intermediate flows, and every cover layer on 72, 144, 216, and 720 vertices. The graph-covering argument proves the statement for arbitrary m, beyond those finite checks. □

Thus the restricted repair distance grows linearly with graph order despite each local boundary fiber having bounded diameter. If switches are allowed to cross several pieces, this lower-bound argument no longer applies. Adding 4 to the disconnected union of all m pentagons would be one even-subgraph modification, but under our definition it comprises m circuit switches.

## 5. Literature context, verification, and remaining work

Flow reconfiguration is an existing research subject. The July 2026 version of Esperet–Hendrey–Lagoutte–Marseloo–Norin–Steiner disproves the group and integer 5-flow reconfiguration analogues, and proves universal connectedness for F₂⁸-flows. Those statements do not establish a universal F₂³ repair theorem toward a CDC-compatible coordinate. The group and target conditions must be kept distinct. [Nowhere-zero flow reconfiguration, arXiv:2512.17342v4](https://arxiv.org/html/2512.17342v4)

Reproduce from the repository root:

```bash
python3 research/five-cdc-attempt/petersen_flow_repair.py
python3 research/five-cdc-attempt/verify_petersen_flow_repair.py
```

The [constructor](petersen_flow_repair.py) saves the [certificate](petersen_flow_repair.json). The [independent verifier](verify_petersen_flow_repair.py) imports no constructor or earlier verifier and uses only the Python standard library.

The constructor enumerates triples of binary even masks. The verifier instead chooses a spanning tree, assigns the three chord values, and solves the remaining edge values by leaf elimination. It enumerates all 301 boundary fibers and verifies their explicit GL(3,2) identifications. Adjacency is then recognized independently from pairwise flow differences, requiring one constant nonzero increment on a connected circuit. It recomputes both exact diameter tables, all clearing paths, and every representative preparation case. It also rebuilds the six Petersen factor restrictions and checks the premises of their obstruction, the replicated disjoint witnesses, short-cycle contractions, graph covering maps, switches, and positive covers.

The exact-distance lower bound and the all-m contraction and covering deductions are mathematical arguments above; checking four values of m is an audit of their implementation, not the basis for an infinite extrapolation. No proof-assistant verification is claimed.

This family therefore cannot furnish a component of flows permanently separated from every completable coordinate: all its flows lie in one reconfiguration component containing an explicit successful flow. The remaining general problem is to show, for arbitrary bridgeless cubic graphs, that an appropriate component contains a successful flow—or to use another existence argument. Local clearing alone and unrestricted reconfiguration connectedness on this family do not close that gap. The earlier question of repair without increasing the proposed defect potential remains unresolved.
