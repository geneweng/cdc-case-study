# An exact quotient for neutral minimum-class exchanges

Research date: **6 October 2026**.

**Minimum-preserving changes inside a coordinate fiber can be classified by an exact parity quotient.** The reduction applies to any nowhere-zero three-bit flow on a cubic graph. At a global minimum of color-class size, every permitted replacement matching can be reached by at most as many neutral circuit switches as there are replaced matching edges.

For the [138-vertex counterexample](secondary-minimum-obstruction.md), the classification is complete: the six neighboring fibers permit exactly **29 distinct replacements** of the original three-edge minimum class, and **every replacement is suitable**. Each has a single legal neutral circuit witness. Thus every neutral circuit that changes this saved flow's minimum class repairs the matching.

There is also a much shorter escape than the previously saved forty-edge move. A **six-edge circuit**, shortest possible for a neutral change of this class, preserves the entire color-size vector and reaches a suitable matching. One further 55-edge switch constructs a five-layer cover. The general existence of neutral escape remains unproved.

**Follow-up:** [Neutral escape from an entire fixed-projection family](prepared-minimum-exchange.md) extends the classification to all 2⁶⁷ lifts of this projection. The same six-edge circuit works for every lift with an adaptive increment, and an exact prepared-exchange theorem describes all 37 potential replacement matchings.

## 1. Contract the edges with zero switching cost

Let f be a nowhere-zero F₂³-flow on a connected loopless cubic graph G. Fix distinct nonzero colors a,b and write

\[
M_x=f^{-1}(x),\qquad
E_b=M_a\cup M_{a+b},\qquad
Z_b=E(G)\setminus(M_a\cup M_b\cup M_{a+b}).
\]

We wish to change the class Mₐ using switches by b. The whole b-fiber consists of flows

\[
f_C(e)=f(e)+b\,1_C(e),
\qquad C\in Z(G-M_b),
\tag{1}
\]

where C is a binary cycle, possibly disconnected. Avoiding M_b ensures that no changed edge becomes zero.

Only the edges of E_b affect the size or identity of Mₐ. Edges in Z_b can participate in C without affecting that class. Form Q_b by contracting every component of the spanning subgraph (V(G),Z_b), including isolated vertices, retaining the edges of E_b, and discarding M_b. Parallel edges and loops are allowed in this quotient.

For an edge set J in Q_b, let ∂J be its set of odd-degree vertices. A loop contributes zero to this boundary. Put

\[
T_b=\partial M_a,
\]

using the images of the original matching edges in the quotient. A **T_b-join** is an edge subset K with ∂K=T_b.

## 2. The exact replacement theorem

**Quotient theorem.** An edge set K is the color-a class of some flow in the b-fiber of f if and only if

\[
K\subseteq E_b\qquad\text{and}\qquad\partial K=T_b\text{ in }Q_b.
\tag{2}
\]

In particular, the minimum possible size of color a in this fiber equals the minimum cardinality of a T_b-join in Q_b.

**Proof.** Under the update (1), the edges of Mₐ on C leave the class, and the edges of Mₐ₊ᵦ on C enter it. Thus

\[
K=M_a\mathbin\triangle(C\cap E_b),
\quad\text{or equivalently}\quad
C\cap E_b=M_a\mathbin\triangle K.
\tag{3}
\]

Once the right side is prescribed, the only free edges of C lie in Z_b. An even extension exists exactly when the prescribed incidence parity sums to zero on each component of (V,Z_b). This is the binary incidence-completion criterion. In the contracted graph it is precisely ∂(Mₐ△K)=0, giving (2).

Conversely, (2) supplies that even extension C. Equation (1) is then a nowhere-zero flow, with color-a class exactly K. This also proves that any K passing the quotient test is automatically a matching in the original cubic graph; no additional matching hypothesis is needed. ∎

### Exact multiplicities

For a fixed permitted K, the extensions differ by binary cycles supported on Z_b. Therefore exactly

\[
2^{r_b},\qquad r_b=|Z_b|-|V(G)|+c(V(G),Z_b),
\tag{4}
\]

flows in the b-fiber have color-a class K. Distinct extensions give distinct edge-labeled flows.

The entire b-fiber has 2ˢᵇ flows, where s_b is the cycle-space dimension of G−M_b. These counts concern flows with their actual three-bit labels, without identifying global color permutations.

## 3. At a global minimum, the circuits can all be neutral

Assume |Mₐ|=μ(G)=k, so no color class of any nowhere-zero three-bit flow on G has fewer than k edges. Let K be a k-edge T_b-join, and choose an extension C in the quotient theorem.

Since G is cubic, C is a disjoint union of vertex-disjoint circuits C₁,…,Cᵣ. Each individual b-switch is legal, and its change to the class size is

\[
\Delta_i=|C_i\cap M_{a+b}|-|C_i\cap M_a|.
\]

Global minimality implies Δᵢ≥0. Their sum is |K|−|Mₐ|=0. Hence every Δᵢ is zero.

Circuits meeting neither Mₐ nor Mₐ₊ᵦ may be omitted: they change other flow values but not the target matching. Each remaining circuit removes at least one edge of Mₐ, and their removed edges are disjoint. Consequently:

**Neutral realization corollary.** Every k-edge replacement allowed by (2) can be reached as a matching by at most

\[
|M_a\setminus K|\le k
\]

legal circuit switches by b, each preserving |Mₐ|=k.

The endpoint need not be a previously specified flow realizing K; it has the desired matching and the same fixed projection. The corollary controls cardinality. It does not generally guarantee that the number of odd unmatched components stays constant at intermediate steps. That stronger property is checked directly in the example below.

The theorem gives an exact test, rather than an existence theorem for a favorable replacement. The original Mₐ can be the only minimum T_b-join.

## 4. Complete neighboring fibers of the 138-vertex flow

Use the graph and initial flow in the [preceding certificate](secondary_minimum_obstruction.json). Their global minimum three, girth five, and cyclic edge connectivity five are already independently certified. Fix a=4 and

\[
M_4=\{(4,134),(45,130),(99,124)\},
\]

with edge indices {178,183,189}. Its secondary objective is (3,0), but it is unsuitable because of the forced hexagon with three matching endpoints.

For each b≠4, enumerate every edge subset of Q_b of size at most three. No smaller T_b-join exists. The three-edge joins give the following complete table:

| Increment b | Quotient vertices | Quotient edges | Full fiber dimension s_b | Free dimension r_b | Minimum matchings | Suitable replacements | Flows with a minimum class |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 6 | 12 | 12 | 5 | 4 | 3 | 128 |
| 2 | 8 | 14 | 13 | 5 | 2 | 1 | 64 |
| 3 | 9 | 15 | 14 | 7 | 2 | 1 | 256 |
| 5 | 6 | 61 | 61 | 5 | 24 | 23 | 768 |
| 6 | 8 | 61 | 59 | 5 | 2 | 1 | 64 |
| 7 | 9 | 59 | 58 | 7 | 1 | 0 | 128 |

Each row includes the original matching once. The 29 nontrivial replacements are distinct across the rows, giving **30 distinct minimum matchings** in total. For every replacement the certificate supplies:

- A single legal circuit switch from the original flow producing it.
- Two explicit even subgraphs F,t with F∩t equal to that replacement.

All 29 replacements therefore have no odd unmatched component. Their witnesses preserve the globally optimal secondary value (3,0).

The flow counts sum to 1,408 when tagged by increment. Of these, 1,024 have a suitable replacement matching. They are not asserted to be already completed five-label lifts; the intersection pairs guarantee that a subsequent fiber repair is available. The fixed-increment-4 fiber always preserves M₄ and is irrelevant to changing this matching.

### What the completeness proves

Any legal single b-circuit preserving |M₄| produces a three-edge class covered by the table. Therefore **every cardinality-neutral circuit that changes this initial M₄ makes it suitable**, including circuits never explicitly enumerated by the program.

Conversely, each listed replacement has a single-circuit witness. Thus the table is also the exact set of distinct minimum matchings reachable by one neutral circuit from this saved flow.

Increment 7 is a useful contrasting case. Its whole fiber contains 2⁵⁸ flows, but every flow in it with a three-edge color-4 class has the original matching. Even a sequence using only increment 7 cannot end at a different minimum matching. The other five increments all allow a suitable replacement. This is rigidity of one fiber, not a trap under all neutral switches.

## 5. A shortest six-edge matching escape

Add 1 on the circuit

\[
C'=(99,101,104,103,123,124,99),
\]

whose edge indices are

```text
142, 146, 148, 189, 190, 194.
```

Its values are the six nonzero colors other than 1, each appearing once. The switch is legal and exchanges each pair {x,x+1} equally. It therefore preserves the **entire** size vector

\[
(58,58,56,3,9,11,12).
\]

The color-4 matching replaces (99,124) by (103,104), becoming the suitable set with edge indices {148,178,183}. The original forced hexagon and C′ share the edge (123,124); the changed endpoint removes the old forced-circuit obstruction.

This is a shortest neutral circuit that changes the specified matching. Any such switch must remove an edge of M₄; otherwise preserving cardinality would leave M₄ unchanged. Independently computed shortest circuit lengths through its three edges are:

| Matching edge | Shortest circuit containing it |
|---|---:|
| 178=(4,134) | 13 |
| 183=(45,130) | 9 |
| 189=(99,124) | 6 |

Thus no matching-changing neutral circuit can have length below six, and C′ attains the bound.

The supplied intersection pair for the new matching differs from the current first coordinate on one 55-edge circuit. Adding 4 on that circuit gives a verified five-layer cover. The new repair has switch lengths **6 and 55**, replacing the earlier witness with lengths 40,30,25. Both stages retain the secondary optimum (3,0).

Only the shortest length of a neutral change of this matching is claimed. We do not claim that two is the minimum number of switches to any successful lift, or that this is a shortest total-length cover construction.

## 6. Scope and next gap

The quotient theorem and neutral realization corollary hold for general cubic flows under their stated hypotheses. They turn a search over potentially enormous fibers into a parity problem on retained edges, with an exact multiplicity formula. For a small minimum class, all candidate replacement matchings can be enumerated without enumerating the full fiber.

The stronger positive conclusion—every nontrivial neutral replacement is suitable—is specific to the saved 138-vertex flow. It explains why the forced-hexagon counterexample is easy to escape despite defeating the secondary minimization rule.

Nothing here proves that every obstructed optimum has a suitable join in one of these quotients. Nor does it classify the quotients arising after arbitrary preparations that preserve the matching, or exclude a closed collection of obstructed optima on another graph. Establishing an escape from such a collection remains the general gap. The five-cycle double cover conjecture remains unproved by this work.

## 7. Independent verification

The [constructor](neutral_minimum_quotient.py), [certificate](neutral_minimum_quotient.json), and [verifier](verify_neutral_minimum_quotient.py) use only Python's standard library and existing repository modules.

```bash
python3 -B research/five-cdc-attempt/neutral_minimum_quotient.py
python3 -B research/five-cdc-attempt/verify_neutral_minimum_quotient.py
```

The constructor tests parity on contracted components. The verifier independently builds a cycle-space basis of each G−M_b, projects it onto E_b, and uses binary elimination to decide every candidate replacement. It also checks all quotient data, fiber and kernel dimensions, 29 intersection pairs, 29 individual neutral switches, shortest-cycle lower bounds, and the new cover.

The previous graph and global-minimum proof are pinned by their certificate hash; the unchanged 74-million-subset connectivity audit is not repeated. The new certificate has **55,231 bytes** and SHA-256 `cd19d33ccb19649d6f39b5daf8d7b74d76317f9f2c328d9eb059c27e083ed754`. Regeneration is byte-identical. No literature-novelty claim is made.
