# An odd-component secondary objective succeeds on the 130-vertex graph

Research date: **6 October 2026**.

**The latest minimum-color counterexample admits a complete structural repair rule.** On the [130-vertex graph](cyclic-five-minimum-obstruction.md), every globally minimum color class is suitable exactly when deleting its endpoints leaves no odd component. Thus minimizing the class size and then the number of odd unmatched components always selects a class that permits fiber repair on this graph.

The proof classifies a larger family: every matching containing exactly one charged edge from each of the three 41-vertex regions. There are **261,382** such matchings. Exactly **261,356** are intersections of two binary cycles; the other **26** each have an unmatched singleton and a component of order 123. There is no additional circuit-parity obstruction anywhere in this family.

A complete local boundary table reduces the proof to a ten-vertex graph. This reduction applies to other assemblies of the same five-pole; the positive secondary-objective theorem and the five exceptional patterns below concern the particular 130-vertex assembly. The general conjecture remains unproved by this work.

## 1. The selection problem

For a nowhere-zero F₂³-flow f and a nonzero color a, write

\[
M_a=f^{-1}(a),\qquad
o(M_a)=\#\{\text{odd components of }G-V(M_a)\}.
\]

A matching M is **suitable** if M=F∩t for two binary cycles, meaning even subgraphs that may be disconnected. The [matching theorem](matching-fiber-repair.md) then constructs a successful flow in the fiber fixing the projection that annihilates a, followed by a five-layer cover.

The preceding checkpoint proves that this graph has global minimum color multiplicity μ(G)=3. Its three uncolorable regions have disjoint charged edge sets, each consisting of 59 internal edges and five boundary edges. Every color class meets each charged set. Consequently a three-edge color class contains **exactly one edge per region and no other edge**.

Cardinality alone was insufficient: the saved minimizing flow has seven unsuitable classes and all its incident fibers fail. We now study the lexicographic objective, over pairs (f,a),

\[
\Psi(f,a)=\bigl(|M_a|,o(M_a)\bigr).
\tag{1}
\]

**Theorem for ThreeY1Star130.** The minimum of (1) is (3,0), and every pair attaining it has a suitable color matching.

The theorem does not assert that every starting flow can reach that optimum by neutral switches. The supplied twelve-edge switch establishes such an escape for the saved initial flow; the full classification proves suitability for every secondary minimizer, independently of its flow values.

## 2. A complete local intersection relation

Use the five-pole Y from the preceding certificate, with internal vertices 0,…,40 and ports

\[
(\alpha,\beta,\gamma,\delta,\epsilon)=(0,4,17,21,40).
\]

The local graph is the Y₁ construction of Mattiolo–Negrini–Pagani, credited and specified in the [preceding report](cyclic-five-minimum-obstruction.md#2-the-local-ingredient-and-its-attribution). The new computation here concerns its full single-intersection boundary relation.

Number the 59 internal edges first, then the five dangling boundary edges. Fix one of these 64 edges e. Encode an ordered pair (F,t) by two-bit labels

\[
\lambda(h)=1_F(h)+2\,1_t(h)\in\{0,1,2,3\}.
\]

Local evenness means that the incident labels XOR to zero at every internal vertex. The intersection is exactly {e} when e has label 3 and every other edge has label 0, 1, or 2.

**Local table theorem.** A five-tuple of boundary labels extends to such a pair if and only if:

1. Its five labels XOR to zero.
2. Its label at port q equals 3 exactly when e is that boundary edge.
3. If e is internal and incident to a port vertex q, the boundary label at q belongs to {1,2}.

Necessity follows by summing the internal equations and examining an endpoint of e: the other two labels there must be 1 and 2. Sufficiency is certified by an explicit pair for **every** allowed case. The independent verifier checks all witnesses directly and compares their boundary words with all 4⁵ possible words for each target edge.

| Position of e | Number of edges | Allowed boundary words per edge | Witnesses |
|---|---:|---:|---:|
| Internal, incident to no port | 49 | 61 | 2,989 |
| Internal, incident to one port | 10 | 40 | 400 |
| Boundary edge | 5 | 20 | 100 |
| Total | 64 | — | **3,489** |

No internal edge joins two port vertices. Thus the table has only eleven edge types:

- U: any of the 49 internal edges away from the ports.
- Iq: either of the two internal edges incident to port q, for each of the five ports.
- Bq: the boundary edge at port q, for each of the five ports.

Edges of the same type have identical boundary relations, despite their different locations inside Y.

## 3. A gluing lemma for assemblies of Y

Consider any graph assembled from disjoint copies of Y and an outside graph, with each port joined to the outside and with no edge directly joining two copies. Suppose a matching M chooses one charged edge in each copy and no edge elsewhere. Contract each copy to a vertex, retaining every boundary and outside edge; call the resulting graph Q.

**Transfer lemma.** M is suitable in the original graph if and only if Q admits labels in {0,1,2,3} satisfying:

- The XOR at every vertex of Q is zero, including each degree-five region vertex.
- The edges with label 3 are exactly the selected boundary edges of M.
- A region of type Iq has label 1 or 2 at port q.

**Proof.** Restrict a full intersection pair to the retained edges. Evenness gives the equations at outside vertices; summing the equations inside a region gives its degree-five equation. The remaining constraints are necessary by the local table.

Conversely, every region's boundary word obeys the complete local relation for its selected edge. Choose the saved local pair for that edge and word, and glue along the common boundary labels. This gives even subgraphs F and t throughout the original graph, with intersection precisely M. ∎

The lemma removes the internal search from future assemblies of this same piece. It preserves the choice of the actual internal matching edge, not just its type: the local catalog contains a witness for every edge in that type.

## 4. The complete classification on this assembly

For ThreeY1Star130 the reduced graph Q has ten vertices and eighteen edges. Its three region vertices have degree five; its seven outside vertices have degree three. The binary cycle space has dimension 18−10+1=9.

There are 11³=1,331 type triples and 64³=262,144 raw edge selections. Weight each triple by the product of its type sizes, which are 49 for U, 2 for Iq, and 1 for Bq. A selection can fail to be a matching only when selected boundary edges meet at an outside vertex; this depends solely on the type triple.

The constructor finds reduced witnesses by finite-domain XOR propagation. The independent verifier enumerates **all 512²=262,144 ordered pairs of binary cycles on Q**, applies the transfer constraints and the matching condition, and recovers exactly the same positive type set.

| Classification | Type triples | Actual edge selections |
|---|---:|---:|
| Suitable matchings | 1,200 | 261,356 |
| Unsuitable matchings | 5 | 26 |
| Selections sharing an endpoint | 126 | 762 |
| Total | **1,331** | **262,144** |

For each positive type the certificate supplies a reduced pair. The verifier glues a full witness for one representative of each of the 1,200 types. The complete local relation then proves the same result for every actual edge choice in that type. The 261,356 total is this weighted, proved classification; it is not a claim that that many full flow states were enumerated.

### All five exceptional patterns

The outside vertices are v=123, xᵢ=124+i, b=127, c=128, and d=129. In each row below, all three regions choose the displayed type.

| Three region types | Actual matchings | Unmatched singleton |
|---|---:|---:|
| (Iβ,Iβ,Iβ) | 8 | b=127 |
| (Iγ,Iγ,Iγ) | 8 | c=128 |
| (Iδ,Iδ,Iδ) | 8 | d=129 |
| (Bα,Bα,Bα) | 1 | v=123 |
| (Bε,Bε,Bε) | 1 | v=123 |

For the first three rows, all three port neighbors of b, c, or d are matched internally. For the last two rows, the three neighbors x₀,x₁,x₂ of v are matched by boundary edges. The indicated outside vertex itself remains unmatched.

In every case all its incident edges would be forced into the even subgraph F△t, giving degree three. This directly proves unsuitability without trusting a failed search. The verifier checks every one of the 26 actual matchings, including that its unmatched components have orders **1 and 123**.

We do not assert that every one of the 261,382 valid matchings occurs as a color class of a nowhere-zero three-bit flow. That realization problem is unnecessary here: every minimum color class belongs to this larger classified family.

## 5. Why the secondary objective now works

For any matching in a cubic graph, suitability implies that every component of G−V(M) has even order. Indeed, F△t must include both nonmatching edges at every matched vertex. On an unmatched component K, the parity equation is therefore |δ(K)|≡0; cubicity gives |δ(K)|≡|K| modulo two. This is the necessary half of the [candidate lemma](matching-fiber-repair.md#the-existence-of-a-candidate-l-is-already-a-linear-question).

Conversely, in the present one-edge-per-region family, every unsuitable case appears in the table above and has odd components. Therefore the classification proves

\[
M\text{ suitable}\quad\Longleftrightarrow\quad o(M)=0.
\tag{2}
\]

The preceding certificate already contains an attained minimum with o=0. The independent verifier rechecks its first circuit switch, both nowhere-zero flows, the unchanged color-size vector, and the actual component counts:

| Stage | Region types of the color-4 matching | Objective (1) |
|---|---|---|
| Saved initial flow | (Bε,Bε,Bε) | (3,2) |
| After the twelve-edge switch adding 6 | (Bε,Bε,U) | (3,0) |

The switch replaces edge 189=(122,126) by edge 138=(87,90). The full color-size vector remains (43,41,40,3,23,22,23). The new local table also constructs an intersection pair for this actual repaired class.

Since μ(G)=3 and o is nonnegative, this realizes the global secondary minimum (3,0). Every pair attaining that minimum belongs to the classified family and passes (2), proving the theorem. The previously saved 101-edge second switch and five-layer cover remain available in the preceding certificate.

## 6. What this changes in the approach

The cardinality counterexample now has a complete explanation. Its minimum classes do not conceal a second, circuit-parity failure after the odd components are removed. The obstruction is exactly one of five visible placements around the outside junctions, and the known neutral switch leaves those placements while retaining all color sizes.

The complete local relation and transfer lemma are reusable beyond this graph. They allow a search for favorable minimum classes, or counterexamples to the secondary objective, to take place on a much smaller outside graph while retaining every internal matching choice.

Two general gaps remain. We have not proved that an arbitrary graph has a minimum color class with no odd unmatched component, nor that every such minimum class is suitable. The circuit-parity condition can fail for arbitrary matchings even when all unmatched components are even, as the [three-edge Petersen example](matching-terminal-flow.md) shows. The present classification eliminates that failure only for the stated family. It also gives no neutral reachability theorem for all starting flows.

This is a positive result for selecting a favorable minimizer in the latest example, together with a general transfer rule for its local piece. It does not establish a universal minimization principle or solve the five-cycle double cover conjecture.

## 7. Reproduction and certificate scope

The [constructor](minimum_matching_secondary.py), [certificate](minimum_matching_secondary.json), and [independent verifier](verify_minimum_matching_secondary.py) use only Python's standard library. Neither saved program needs SAT or a graph library.

```bash
python3 -B research/five-cdc-attempt/minimum_matching_secondary.py
python3 -B research/five-cdc-attempt/verify_minimum_matching_secondary.py
```

The new verifier imports no constructor. It directly verifies 3,489 local pairs, exhausts the reduced graph's 262,144 cycle pairs, checks all 1,331 type cases and their weights, glues 1,200 representative pairs plus the actual repaired class, and checks all 26 negative matchings. The graph's previously established cyclic connectivity and minimum multiplicity are reused from the preceding proof, whose JSON is pinned by SHA-256; the expensive small-cut audit is not repeated here.

The new JSON has **371,175 bytes** and SHA-256 `32082a951b4c3012b9f8a312e46b5b117490a899e3a3299a35b6f5dc344975ec`. Regeneration is byte-identical. No smallest-order or literature-novelty claim is made.
