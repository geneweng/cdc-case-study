# Neutral escape from an entire fixed-projection family

Research date: **6 October 2026**.

**Every one of the 2⁶⁷ flows sharing the saved projection on the 138-vertex graph admits a six-edge neutral escape to the same suitable minimum matching.** The circuit is fixed; its legal increment is either 1 or 5, determined by one edge value. It is a shortest possible circuit changing this minimum matching throughout the family.

The complete classification is stronger than this one escape: each flow has exactly **21, 25, or 29 distinct suitable minimum-matching replacements**, each reachable by one circuit. There are **37 potential replacements** across the family, eight more than for the original saved flow. All nontrivial minimum replacements are suitable.

Two general deductions support the calculation: an exact test for exchanges after preparation within a coordinate fiber, and a bijection between whole fibers supplied by a particular kind of single-edge exchange. Neither proves that an arbitrary obstructed minimum admits an escape. The five-cycle double cover conjecture remains unproved by this work.

**Follow-up:** [Every globally minimizing flow escapes on the 138-vertex graph](short-circuit-minimum-escape.md) removes the fixed-projection restriction. A complete matching census finds only one unsuitable candidate, and a general short-circuit lemma forces a neutral replacement of it in every projection.

## 1. What preparation preserves

Let f be a nowhere-zero F₂³-flow on a connected loopless cubic graph. Fix distinct nonzero values a,b, and write c=a+b. Set

\[
M=f^{-1}(a),\quad
P=f^{-1}(\{a,b,c\}),\quad
R=P\setminus M,\quad Z=E(G)\setminus P.
\]

The **a-fiber** consists of all nowhere-zero flows with the same projection modulo the line ⟨a⟩:

\[
\mathcal A(f)=\{f+a1_X:X\in\mathcal Z(G-M)\},
\tag{1}
\]

where \(\mathcal Z(H)\) denotes the binary cycle space of H. The zero edges of the projection must still have value a in any nowhere-zero lift, so every flow in (1) has exactly the same matching M. In particular, preparation within this fiber preserves every structural property of M, including its suitability and its unmatched-component counts.

The partition M,R,Z is fixed throughout the fiber. Preparation swaps b and c on selected R edges and changes values within their a-cosets on Z.

Form a multigraph Q by contracting **every** component of the spanning subgraph (V,Z), including isolated vertices, and retaining **all** P edges. Loops and parallel edges are retained. This differs from the [previous fixed-increment quotient](neutral-minimum-quotient.md), which discards the edges currently colored b.

Let ∂ be binary incidence in Q, and put T=∂M. Conservation of the original flow, summed over each contracted component, gives

\[
\partial f^{-1}(a)=\partial f^{-1}(b)
=\partial f^{-1}(c)=T,\qquad \partial R=0.
\tag{2}
\]

Indeed, the three boundary parities satisfy \(n_a a+n_b b+n_c(a+b)=0\), so they are equal. The projection onto F₂³/⟨a,b⟩ also shows that Z is even; its nontrivial components are circuits.

## 2. An exact prepared-exchange theorem

**Preparation lemma.** As the flow varies over \(\mathcal A(f)\), its b-colored edges can be exactly the sets

\[
J\subseteq R,\qquad \partial J=T.
\tag{3}
\]

Each such J occurs in exactly \(2^{r_Z}\) flows, where

\[
r_Z=|Z|-|V(G)|+c(V(G),Z).
\tag{4}
\]

**Proof.** Necessity follows from (2), which holds for every lift. For sufficiency, prescribe the a-switching set on R to be \(f^{-1}(b)\triangle J\), and prescribe it to be empty on M. Its quotient boundary is zero by (2) and (3), so it extends through Z to a binary cycle. The extension produces a nowhere-zero flow with b-class J. All extensions differ by a binary cycle supported on Z, giving (4). ∎

**Prepared replacement theorem.** An edge set K can occur as the a-class after an a-fiber preparation followed by a b-fiber update if and only if

\[
K\subseteq P,\qquad \partial K=T,
\qquad R\setminus K\text{ contains a }T\text{-join}.
\tag{5}
\]

The last condition has a component test: **every component of the spanning multigraph (V(Q),R∖K) contains an even number of vertices of T**. Isolated vertices count as components.

**Proof.** In a prepared flow with b-class J, the edges that can enter or leave the a-class under b-switching are exactly P∖J. The fixed-increment quotient theorem therefore permits K precisely when K avoids J and ∂K=T. The preparation lemma says that the available J are exactly the T-joins in R. Existence of such a J disjoint from K is the final condition in (5). The component test is the ordinary binary incidence criterion for existence of a T-join. ∎

There is no extra assumption that K is a matching: a set satisfying (5) is realized as a nonzero color class of a cubic flow, so it is automatically a matching.

### Exact source multiplicity

For an admissible K, let

\[
r_{R-K}=|R\setminus K|-|V(Q)|+c(V(Q),R\setminus K).
\]

The number of source flows in \(\mathcal A(f)\) from which a b-fiber update can reach K is exactly

\[
2^{r_Z+r_{R-K}}.
\tag{6}
\]

There are \(2^{r_{R-K}}\) T-joins J in R∖K, and the preparation lemma supplies \(2^{r_Z}\) flows for each. From each such source flow, exactly \(2^{r_Z}\) flows in its b-fiber have a-class K. These are counts of edge-labeled flows, with no identification by color permutations.

If |M| is the global minimum color multiplicity k and |K|=k, preparation can be performed by a-circuits preserving M. The subsequent matching exchange needs at most |M∖K| cardinality-neutral b-circuits, by the previous neutral realization corollary. This does not in general control the secondary odd-component objective during the exchange.

### Availability from a specified lift

Suppose K satisfies (5). In a particular lift f′∈\(\mathcal A(f)\), it is available through the b-fiber exactly when

\[
f'(e)=a+b\quad\text{for every }e\in K\setminus M.
\tag{7}
\]

The quotient parity condition is already fixed; (7) says that no new matching edge is forbidden by having color b. Allowing either increment b or c, K is available exactly when all edges of K∖M have the same full flow value. These conditions involve only the restriction of the source cycle space to the potential new matching edges.

## 3. A single-edge exchange transports whole fibers

**Fiber transport lemma.** Suppose a circuit C meets M in exactly one edge e and meets R in exactly one edge e′. Its other edges lie in Z. Then every f′∈\(\mathcal A(f)\) has a legal switch on this same C with increment

\[
d(f')=a+f'(e')\in\{b,c\}.
\tag{8}
\]

The new a-class is always

\[
K=M-e+e'.
\]

Moreover, this adaptive switch is a bijection from the entire source a-fiber to the entire a-fiber containing its output on f.

**Proof.** The edge e has value a, e′ has value a+d, and every other edge of C has value outside ⟨a,b⟩. None has value d, so the switch is legal and makes exactly the stated replacement. Modulo a, both possible increments have the same image, so every output has the same projection.

For the bijection, put d₀=a+f(e′), g=f+d₀1_C, and write f′=f+a1_X. Then the output is

\[
g+a1_{L(X)},\qquad
L(X)=X\triangle\bigl(X(e')C\bigr).
\tag{9}
\]

Here X(e′) is 0 or 1, and multiplying C by 0 means the empty set. The map L sends \(\mathcal Z(G-M)\) into \(\mathcal Z(G-K)\): it preserves evenness and cancels the coordinate on e′, while remaining zero on M∩K. Its inverse is

\[
Y\longmapsto Y\triangle\bigl(Y(e)C\bigr).
\tag{10}
\]

Since X(e)=0 and Y(e′)=0, the two formulas are mutual inverses. ∎

Thus a suitable K of this form supplies a uniform neutral matching escape for a whole fixed-projection family. Suitability then permits repair within the target a-fiber. The lemma gives a sufficient structural condition; it does not assert that such a circuit or suitable K always exists.

## 4. Complete classification on the 138-vertex graph

Use the [saved graph and flow](secondary_minimum_obstruction.json), with

\[
a=4,\qquad M=\{178,183,189\}.
\]

The graph's global minimum color multiplicity is three. This M is unsuitable despite attaining the secondary optimum (3,0). The cycle space of G−M has dimension **67**, so the source a-fiber has exactly **2⁶⁷** flows, all with this same unsuitable optimum.

The three planes containing a give the following complete prepared classification. Counts include the unchanged M unless specified otherwise.

| Interchangeable increments | Quotient vertices | Retained P edges | r_Z | Minimum matchings | Suitable replacements |
|---|---:|---:|---:|---:|---:|
| 1 / 5 | 6 | 70 | 5 | 35 | 34 |
| 2 / 6 | 8 | 72 | 5 | 3 | 2 |
| 3 / 7 | 9 | 71 | 7 | 2 | 1 |

No smaller matching passes the test. Every three-edge set passing quotient parity also passes the remaining T-join test in this example. Apart from M, the three sets of replacements are disjoint, giving **37 distinct suitable matchings**. Every one has a directly checked intersection pair of binary cycles F,t with F∩t=K.

For each replacement the certificate supplies a fixed circuit whose P-intersection is exactly M△K. Whenever (7) holds in a lift, that same circuit is a legal neutral switch to K. Consequently the classification describes **single-circuit replacements**, as well as minimum endpoints of whole neighboring fibers. Any cardinality-neutral circuit changing M, from any of the 2⁶⁷ source lifts, reaches one of these suitable matchings.

For a specified increment, the source multiplicities are:

| Plane | Replacement type | Number of matchings | Source flows per matching |
|---|---|---:|---:|
| 1 / 5 | Replace one edge | 10 | 2⁶⁶ |
| 1 / 5 | Replace two edges | 24 | 2⁶⁵ |
| 2 / 6 | Replace one edge | 2 | 2⁶⁶ |
| 3 / 7 | Replace one edge | 1 | 2⁶⁶ |

The unchanged M is available from all 2⁶⁷ sources for each increment.

### Only thirteen edge values determine availability

All potential new matching edges lie in

```text
6, 7, 143, 144, 148, 163, 174, 175, 177, 179, 180, 181, 190.
```

Restriction of \(\mathcal Z(G-M)\) to these thirteen coordinates has rank **10**. There are therefore exactly **1,024** possible bit patterns, each representing **2⁵⁷** source flows. Exhausting these patterns gives:

| Replacements in planes (1/5, 2/6, 3/7) | Total distinct replacements | Patterns | Fraction of all lifts |
|---|---:|---:|---:|
| (18, 2, 1) | 21 | 192 | 3/16 |
| (22, 2, 1) | 25 | 640 | 5/8 |
| (26, 2, 1) | 29 | 192 | 3/16 |

Each of increments **1, 2, 5, and 6** permits at least one suitable replacement from every source lift. Increment 3 permits a replacement from exactly half the lifts; increment 7 does so from the complementary half. Thus the previously rigid increment 7 reflects the choice of lift, not rigidity of the whole projection family.

## 5. The same six-edge escape works everywhere

The circuit from the previous checkpoint has edge indices

```text
142, 146, 148, 189, 190, 194.
```

In the plane ⟨4,1⟩, it meets M only at 189 and R only at 148. The fiber transport lemma therefore applies. For **every** source lift f′, add

\[
4+f'(148)\in\{1,5\}
\]

on this fixed circuit. The output matching is always

\[
K=\{148,178,183\},
\]

which is suitable. The explicit map \(X\mapsto X+X(148)C\) has rank 67 and the inverse in (10), so the switch bijects the full source and target families.

The earlier shortest-cycle lower bound through an edge of M is six. Every cardinality-neutral change of M must remove an edge of M, so this is a shortest matching-changing circuit for every source lift. The entire color-size vector is preserved for the originally saved lift; that stronger property is not asserted for every lift. The minimum-class size and secondary objective (3,0) are preserved throughout the family.

Every output has the same projection modulo 4 as the previously saved successful flow. Its difference from that successful flow is 4 times a binary cycle avoiding K. Switching the circuit components of this difference reaches that exact flow and hence its verified five-layer cover. Since the graph has 138 vertices and girth five, there are at most 27 such vertex-disjoint circuits. Thus **every source lift reaches a verified cover within two fiber rounds and at most 28 actual circuit switches**.

This is a coarse uniform bound. The original lift still needs only the saved six-edge and 55-edge switches in this construction; the same second circuit is not claimed to work for all lifts.

## 6. A shortest preparation that unlocks increment 7

The plane ⟨4,3⟩ has exactly one alternative minimum matching:

\[
K_7=\{178,183,190\}.
\]

It is reachable by increment 7 precisely when edge 190 has value 3. The initial value is 7, explaining the previous rigidity. A shortest circuit through edge 190 in G−M has length fourteen:

```text
119, 121, 139, 145, 147, 162, 176,
187, 190, 193, 194, 196, 205, 206.
```

Adding 4 on it preserves M and changes the value on 190 from 7 to 3. Adding 7 on the six-edge circuit

```text
141, 143, 147, 189, 190, 194
```

then reaches K₇. Both switches retain the secondary optimum (3,0).

Fourteen is the **minimum length of a single color-4 preparation enabling a minimum-matching change by increment 7 from the saved lift**. The complete plane classification forces any such preparation to flip edge 190, and an independent breadth-first computation gives fourteen as its shortest circuit length in G−M. This restricted optimality claim does not concern shortest arbitrary repair sequences or total repair length.

## 7. What this advances, and what remains

The positive result now covers every lift of one fixed projection, rather than one selected flow. The prepared quotient identifies exactly how much freedom preparation provides, while the fiber transport lemma lets one local circuit certify escape for exponentially many flows at once. These provide tools for studying collections of obstructed optima without enumerating their lifts individually.

The missing step is still an existence theorem: an arbitrary obstructed minimum might have no suitable prepared replacement, and the transport lemma needs a specific circuit with a suitable exchanged matching. This checkpoint does not classify all projections even on the 138-vertex graph, much less rule out a closed collection of unsuitable optima on an arbitrary cubic graph. A useful next test is whether the prepared quotient can certify an optimum for which **all three planes lack suitable replacements**, and, if so, what further neutral changes escape that obstruction.

## 8. Independent verification

The [constructor](prepared_minimum_exchange.py), [certificate](prepared_minimum_exchange.json), and [independent verifier](verify_prepared_minimum_exchange.py) use Python's standard library and existing repository modules.

```bash
python3 -B research/five-cdc-attempt/prepared_minimum_exchange.py
python3 -B research/five-cdc-attempt/verify_prepared_minimum_exchange.py
```

The constructor uses quotient incidence and the T-even-component criterion. The verifier independently projects the cycle spaces of G and G−M: one projection tests exchange parity, and the other tests consistency of the preparation values on the new matching edges. It recovers all three candidate sets and every source multiplicity without calling the constructor or its component test.

The verifier also checks all 37 intersection pairs and circuit witnesses, all 1,024 availability patterns using full-flow representatives, the rank-67 transport map and inverse, the successful target flow and all five cover layers, and the fourteen-edge preparation lower bound. The algebraic dependence on only thirteen coordinates makes the representative check exhaustive for the family.

The previous graph, global-minimum proof, girth, and connectivity are pinned by certificate hashes; the unchanged 74-million-subset connectivity audit is not repeated. The new certificate has **70,351 bytes** and SHA-256 `f8d8035634c86344c0e3669041b69f79a1642a8a3c092cda50832bd00bf10150`. Regeneration is byte-identical. No literature-novelty claim is made.
