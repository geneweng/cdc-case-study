# The odd-component secondary minimum can still be unsuitable

Research date: **6 October 2026**.

**Minimizing color-class size and then odd unmatched-component count does not guarantee a suitable matching, even at cyclic edge connectivity five.** A simple 138-vertex cubic graph has global minimum color multiplicity three and a minimizing class M with G−V(M) connected on 132 vertices. Its objective is therefore the globally optimal pair **(3,0)**. Nevertheless M is not the intersection of two binary cycles.

The obstruction is elementary: three matching endpoints alternate around a six-cycle. Every candidate repair must contain that entire circuit, which has an odd number of matching endpoints. Three explicit terminal cuts give a second certificate of the same failure.

The [preceding positive theorem](minimum-matching-secondary.md) remains valid for its 130-vertex graph. This new outside assembly disproves its universal extension. A neutral switch repairs the present matching without changing the objective, and two further switches construct a five-layer cover. The original conjecture remains unproved by this work.

## 1. The precise counterexample

For a nowhere-zero F₂³-flow f and a nonzero color a, let

\[
M_a=f^{-1}(a),\qquad
\Psi(f,a)=\bigl(|M_a|,o(M_a)\bigr),
\]

where o(M) counts odd components of G−V(M). A matching is **suitable** when it is F∩t for two binary cycles, which may be disconnected even subgraphs.

**Certified theorem.** There exist a graph G and a nowhere-zero flow f such that:

1. G is simple and cubic, with 138 vertices, 207 edges, girth five, and cyclic edge connectivity exactly five.
2. Every color of every nowhere-zero three-bit flow on G occurs at least three times.
3. The color-4 class of f has three edges, and its unmatched induced graph is connected of order 132. Hence Ψ(f,4)=(3,0) is globally minimum.
4. That color-4 matching is unsuitable.
5. A legal circuit switch creates a suitable color-4 class while retaining Ψ=(3,0). Two further legal switches construct a five-layer cover, still retaining the objective.

This disproves the statement that **every** minimizer of Ψ is suitable. It does not disprove the possible existence of a favorable minimizer in every graph: this example has one. We also make no claim that all incident fibers of the supplied initial flow are blocked; only the specified minimum matching is proved unsuitable.

## 2. Assembly and the global lower bound

Use three copies Y₀,Y₁,Y₂ of the 41-vertex uncolorable five-pole from the preceding checkpoints. The local piece is credited to Mattiolo–Negrini–Pagani in the [original construction report](cyclic-five-minimum-obstruction.md#2-the-local-ingredient-and-its-attribution). Its internal vertices are shifted by 0,41,82, and its port order is

\[
(\alpha,\beta,\gamma,\delta,\epsilon)=(0,4,17,21,40).
\]

Add outside vertices 123,…,137. Attach the five ports of each region to the following outside vertices, in that port order:

| Region | α | β | γ | δ | ε |
|---|---:|---:|---:|---:|---:|
| Y₀ | 129 | 134 | 131 | 135 | 125 |
| Y₁ | 137 | 130 | 136 | 128 | 135 |
| Y₂ | 136 | 131 | 124 | 123 | 129 |

Add these fifteen outside edges:

```text
(133,128), (132,137), (124,123), (123,130), (124,126),
(131,129), (125,128), (127,134), (133,132), (127,130),
(134,126), (133,127), (135,125), (126,132), (137,136).
```

The graph has 3·41+15=138 vertices and 3·59+30=207 edges. The reduced graph obtained by contracting the regions has eighteen vertices and thirty edges. The [single-intersection transfer rule](minimum-matching-secondary.md#3-a-gluing-lemma-for-assemblies-of-y) was used to find this assembly; the final negative certificate below is directly about the full graph.

Each region has a charged set of 59 internal plus five boundary edges. These three sets are disjoint. The independent local-piece audit again proves that Y admits no zero-free two-bit flow: its smaller proper-coloring tables have 36,42,72 rows, and all 11,664 joining combinations fail.

For any nonzero color a, project a nowhere-zero three-bit flow to F₂³/⟨a⟩. The zero edges of this projection are precisely Mₐ. Each region forces at least one zero, so |Mₐ|≥3 for every color of every flow.

The supplied flow has color sizes

\[
(58,58,56,3,9,11,12).
\]

Its color-4 matching is

\[
M=\{(4,134),(45,130),(99,124)\},
\tag{1}
\]

with edge indices {178,183,189}. In the previous type notation it is (Bβ,Bβ,Bγ). The lower bound is attained, so μ(G)=3.

## 3. The odd-component test passes completely

The six matching endpoints are

\[
D=\{4,45,99,124,130,134\}.
\]

Deleting them leaves a **connected** induced graph on 132 vertices and 192 edges. Thus o(M)=0, not merely a smaller positive value than another choice.

The [candidate lemma](matching-fiber-repair.md#the-existence-of-a-candidate-l-is-already-a-linear-question) says that even subgraphs L⊆G−M covering D exist exactly when every unmatched component has even order. Their affine direction is the binary cycle space of G−D. Here its dimension is

\[
192-132+1=61.
\]

Consequently there are **2⁶¹ candidate even subgraphs** covering all six endpoints. The certificate supplies one explicitly. Its circuit lengths are 20,20,10,6, with matching-endpoint counts 1,1,1,3.

Existence of a candidate is therefore not the issue. Every one of the 2⁶¹ candidates fails the additional circuit-parity requirement for the following common reason.

## 4. A forced six-cycle defeats every candidate

The outside graph contains the circuit

\[
C=(124,123,130,127,134,126,124).
\tag{2}
\]

The alternating vertices 124,130,134 belong to D, and their matching edges all leave C. At each of these three vertices, the two nonmatching edges are therefore the two circuit edges. Every candidate L⊆G−M covering D must contain both.

Together these requirements force all six edges of C. Every vertex of C already has degree two in L. Since G is cubic and L is even, no extra edge at any circuit vertex can belong to L. Hence C is a whole circuit component of **every** candidate L.

But |V(C)∩D|=3 is odd. The [circuit criterion](matching-fiber-repair.md#3-an-equivalent-circuit-condition) requires every circuit component to contain an even number of matching endpoints. Thus no candidate gives an intersection pair, and M is unsuitable.

### A reusable obstruction

The argument proves a general lemma. Let M be a matching in a cubic graph, and suppose a circuit of length 2r has exactly its alternating r vertices in V(M), with their matching edges outside the circuit. Then every even subgraph of G−M covering V(M) contains this circuit as a component. If r is odd, M is unsuitable.

This lemma does not imply an odd component of G−V(M). The present graph demonstrates that distinction even for a globally minimum class and under cyclic five-connectivity.

## 5. Three small cuts independently certify failure

Put H=G−M. The [terminal-flow theorem](matching-terminal-flow.md) requires some balanced split D=S∪N, |S|=|N|=3, such that every vertex set X satisfies

\[
|\delta_H(X)|\ge 2\bigl||X\cap S|-|X\cap N|\bigr|.
\tag{3}
\]

Consider three vertex sets along the hexagon:

| X | X∩D | Boundary edges in H, by index |
|---|---|---|
| {123,124,130} | {124,130} | {190,196,201} |
| {124,126,134} | {124,134} | {194,199,205} |
| {127,130,134} | {130,134} | {195,202,203} |

Each set has three boundary edges in H and contains exactly the displayed two terminals. If those terminals have the same sign, the right side of (3) is four, exceeding the boundary size three. Therefore (3) would force each of the three pairs among 124,130,134 to have opposite signs. This is impossible.

The verifier checks these cut identities directly and verifies that they exclude all ten balanced terminal splits, up to reversing signs. No unsuccessful SAT result or max-flow computation is needed in the saved proof.

These are five-edge cuts in G: their other two boundary edges belong to M. They are fully compatible with cyclic edge connectivity five.

## 6. Connectivity and an explicit repair at the same optimum

The constructor uses a pair-column calculation to find the small cuts. The independent verifier builds a different fundamental cycle basis and checks every edge triple and quadruple.

| Check | Result |
|---|---|
| Cycle-space dimension | 70 |
| One- and two-edge cuts | None: all 207 edge columns are nonzero and distinct |
| 1,456,935 edge triples | Exactly 138 cuts, all vertex boundaries |
| 74,303,685 edge quadruples | Exactly 207 cuts, all adjacent-vertex-pair boundaries |
| Cyclic five-edge cut | Boundary of the first 41-vertex region |
| Girth | Five |

Thus the graph has cyclic edge connectivity exactly five. In particular, it contains no Petersen four-pole: that would supply an eight-vertex side of a four-edge cut, whereas every such cut here has sides of orders two and 136.

The obstruction can be escaped without improving Ψ. Add 1 on the saved forty-edge circuit. This replaces the matching edge (4,134) by (40,125), changing the region types to (Bε,Bβ,Bγ). The new matching is suitable, as witnessed by two explicit even subgraphs in the certificate.

With the projection annihilating 4 fixed, the required change of first coordinate splits into two circuits of lengths 30 and 25. Adding 4 on them and applying the existing five-label decoding produces a five-layer cover.

| Stage | Sizes of colors 1,…,7 | Ψ for color 4 |
|---|---|---|
| Initial, unsuitable class | 58,58,56,3,9,11,12 | (3,0) |
| After the forty-edge switch | 58,57,57,3,9,12,11 | (3,0) |
| After the thirty-edge switch | 59,57,56,3,8,12,12 | (3,0) |
| After the twenty-five-edge switch | 56,56,55,3,11,13,13 | (3,0) |

Every switch, intersection identity, and cover layer is independently verified. This is an explicit repair, with no claim that three switches are shortest. Unlike the earlier 130-vertex repair, the first switch changes the full color-size vector; it preserves the two-entry objective under examination.

## 7. Consequence for the approach

The previous complete boundary relation successfully exposed a limitation of its positive example. A different outside assembly has a minimum class that passes every unmatched-component parity test and still fails because of a forced circuit with odd endpoint count.

Neither global cardinality optimality, secondary odd-component optimality, nor cyclic five-connectivity removes this obstruction. An argument based on selecting an arbitrary minimizer of Ψ cannot prove the desired existence result.

Favorable ties and neutral escape remain possible: the displayed first switch demonstrates both. What is still missing is a general rule for reaching or selecting such a favorable tie, with control of circuit parity or the equivalent terminal-cut obstructions. This example does not refute every stronger objective, establish that all optimal flows are blocked, or settle the cyclically six-edge-connected case.

The original five-cycle double cover conjecture is not proved or disproved here. The graph itself has the explicit cover just described.

## 8. Reproducibility

The [constructor](secondary_minimum_obstruction.py), [certificate](secondary_minimum_obstruction.json), and [independent verifier](verify_secondary_minimum_obstruction.py) require only Python's standard library and the existing repository modules.

```bash
python3 -B research/five-cdc-attempt/secondary_minimum_obstruction.py
python3 -B research/five-cdc-attempt/verify_secondary_minimum_obstruction.py
```

The constructor stores fixed discovery witnesses and derives the graph, lower bound, obstruction, candidate, connectivity certificate, repair, and cover. The verifier imports no constructor; it reuses the preceding independent local-piece audit and directly checks all new claims. The negative proof consists of the forced hexagon and three explicit cuts. SAT was used only during discovery.

The certificate has **50,945 bytes** and SHA-256 `f722b31c3247ef29ad9a7214574a0283dfed1a877c4cc93ea07be75e2b1c87b5`. Regeneration is byte-identical. No smallest-order or literature-novelty claim is made.
