# Terminal flows, cut obstructions, and two-edge color classes

Research date: **5 October 2026**.

**A color occurring on exactly two edges always permits coordinate-fiber repair on a simple cyclically four-edge-connected cubic graph.** The underlying graph statement is stronger: any two independent edges in such a graph are the exact intersection of two circuits. This extends the singleton repair result from the [matching criterion](matching-fiber-repair.md).

For larger matchings, there is now an exact test using ordinary integral max flow. A matching of size k requires at most ½ binom(2k,k) choices of terminal signs. A successful network supplies the two intersecting even subgraphs; an unsuccessful network supplies a deficient cut. Thus the expensive part can be parameterized by the size of the color class, independently of the graph's cycle-space dimension.

This does not prove that a suitable matching can always be reached. The new two-edge theorem identifies a sufficient target on irreducible cores; the switch calculations describe how that target can change.

## 1. Replacing an intersection by two terminal joins

Let G be a connected simple cubic graph, M a matching, D its endpoint set, and H=G−M. Write |M|=k, so |D|=2k. A binary cycle is an even subgraph and may be disconnected; a circuit is connected and 2-regular.

The previous result requires two binary cycles F,t with

\[
F\cap t=M.
\tag{1}
\]

Removing M from F and t gives two edge-disjoint **D-joins** in H: their odd-degree vertices are exactly D. Conversely, adjoining M to two disjoint D-joins gives (1). Thus the matching problem is a particular two-join packing problem.

This is established terminology, rather than a new general packing theorem. Cohen and Lucchesi discuss disjoint T-joins and examples where the minimum T-cut does not determine the packing number. Their additional hypotheses for packing theorems are not assumed here. The argument below uses the degree constraints of H directly. [Cohen–Lucchesi, *Minimax relations for T-join packing problems*, §1](https://deinfo.uepg.br/~jcohen/pdf/minimax.pdf)

Vertices in D have degree two in H; all other vertices have degree three. This is the feature that makes a terminal flow useful.

## 2. An exact balanced-terminal max-flow test

Choose S⊆D with |S|=k and put N=D∖S. Replace each edge of H by oppositely directed unit-capacity arcs. Add a source with an arc of capacity two to each vertex in S, and an arc of capacity two from each vertex in N to a sink.

**Terminal theorem.** Equation (1) holds if and only if some such network has an integral flow of value 2k.

**Proof, from a network to cycles.** Cancel opposing flow on each original edge. The resulting net values belong to {−1,0,1}. At a terminal in S, both H-edges point out; at a terminal in N, both point in. At every nonterminal, flow conservation and degree three imply that either zero or two edges carry net flow, with one entering and one leaving.

The support L is therefore an even subgraph of H covering D. On each circuit of L, the terminals alternate between S and N. In particular, their number is even. Color successive circuit segments alternately red and blue, changing color at terminals. Adjoining M to each color class gives F and t with intersection M. Circuit components without terminals may be discarded.

**Proof, from cycles to a network.** Given (1), the circuit criterion supplies L=F△t, whose circuits each meet D evenly. Assign alternate terminals on every circuit to S and N. Each circuit contributes equally to the two sets, so |S|=|N|=k. Orient the segments between consecutive terminals from S to N. These edge-disjoint segments carry two units out of every source terminal and into every sink terminal, giving value 2k. ∎

Reversing all terminal signs gives the same decision. For k≥1 it suffices to test the

\[
\binom{2k-1}{k-1}=\frac12\binom{2k}{k}
\tag{2}
\]

balanced sets containing one fixed terminal. For k=0, F=t=∅ suffices. The algorithm therefore uses at most 4ᵏ times a polynomial in the graph size. This is a parameterized algorithm, not a polynomial-time claim for unrestricted k.

### Exact cut certificates

For X⊆V(G), define

\[
\eta_S(X)=|X\cap S|-|X\cap N|.
\]

The source–sink cut with original vertex side X has capacity

\[
|\delta_H(X)|+2|S\setminus X|+2|N\cap X|
=2k+|\delta_H(X)|-2\eta_S(X).
\]

Consequently, a fixed terminal choice succeeds exactly when

\[
|\delta_H(X)|\ge 2|\eta_S(X)|
\qquad\text{for every }X\subseteq V(G).
\tag{3}
\]

The absolute value follows by also considering the complementary side. A failed network gives X with positive deficit

\[
2\eta_S(X)-|\delta_H(X)|>0.
\tag{4}
\]

The quantifiers matter: a matching succeeds when **some balanced terminal choice satisfies every cut inequality**. To certify failure, one deficient cut is needed for **each** terminal choice, up to simultaneous sign reversal. One cut need not block all choices.

For a color matching in a nowhere-zero three-bit flow, H already has a nowhere-zero two-bit projection and hence no bridges. That alone is insufficient: (3) also tests cuts around an excess of two or more source terminals.

## 3. Every two-edge matching on a cyclically four-edge-connected core works

**Two-circuit theorem.** Let G be a connected simple cubic graph with no cyclic edge cut of size at most three. For any independent edges e₁,e₂, there are circuits F,t with

\[
F\cap t=\{e_1,e_2\}.
\tag{5}
\]

Here cyclic means that both sides contain a circuit. No supplied flow or cover is required for this graph statement.

**Proof.** First, every nonempty cut of size at most three isolates one vertex and has size three. Indeed, one side must be a forest. If that forest has v vertices and c components, its boundary in a cubic graph has size v+2c. A nonempty forest with boundary at most three is a single vertex.

Put M={e₁,e₂}. Then H=G−M is connected: a disconnection would give a cut of G with at most two edges. It is also bridgeless. A bridge of H would give a cut of G contained in M together with that bridge, of size at most three. Such a cut must be the three edges at one vertex, which cannot contain both independent edges of M.

Choose **both endpoints of e₁ as S**, and both endpoints of e₂ as N. We verify (3).

- If ηₛ(X)=0, there is no demand across the cut.
- If |ηₛ(X)|=1, connectedness and bridgelessness give |δ_H(X)|≥2.
- If |ηₛ(X)|=2, X contains both ends of one matching edge and neither end of the other. No edge of M crosses the cut, so δ_H(X)=δ_G(X). Neither side is a singleton, and therefore this cut has size at least four.

Thus the network has value four. Discard support circuits without terminals. Every remaining segment between consecutive terminals joins an endpoint of e₁ to an endpoint of e₂. After the red/blue split, each color class consists of two such paths. Adding e₁ and e₂ makes each into one circuit, proving (5). ∎

**Flow corollary.** If a nowhere-zero F₂³-flow on such a core has a color a occurring exactly twice, its a-fiber contains a five-label lift. The original projection annihilating a remains fixed. The previous construction uses at most ⌊n/g⌋ actual circuit switches, where g is the girth.

The same conclusion holds for a singleton color by the earlier theorem, and an empty color already gives a suitable matching. Hence a flow on this core with **no suitable color matching must use every color at least three times**. This is a necessary condition on a blocked state, not a general way to escape one.

The size-two guarantee cannot be extended to every three-edge color class, even on the Petersen core. In its saved vertex labeling, take

\[
M=\{(1,2),(3,4),(0,5)\}.
\]

The certificate supplies a nowhere-zero flow having exactly these three edges of color 4. The unmatched induced graph is the path 8–6–9–7, so there is exactly one candidate circuit union. Its two pentagons are

\[
(0,1,6,9,4,0),\qquad (2,3,8,5,7,2).
\]

Each contains three of the matching endpoints {0,1,2,3,4,5}. Both fail the required parity, proving that M is unsuitable. Independently, all ten balanced terminal choices have deficient cuts. Other color matchings of this flow do permit repair; the example only limits the cardinality guarantee for a specified class.

**Later strengthening (6 October 2026):** The [cyclic-five minimum obstruction](cyclic-five-minimum-obstruction.md) has a globally minimum three-edge class that is unsuitable, with all seven incident fibers blocked. The graph has cyclic edge connectivity five and no Petersen four-pole. Thus even global minimality and that stronger connectivity cannot extend the two-edge guarantee to size three.

## 4. Why the connectivity hypothesis matters

Two explicit simple cubic examples have a nowhere-zero three-bit flow with a two-edge color class that fails (1). Both H graphs are connected and bridgeless. These are counterexamples to repairing that specified matching, not to the five-cycle double cover conjecture or to all possible fiber repairs.

### A 12-vertex obstruction before circuit parity is tested

Use the following edge order:

```text
[(0,5),(0,7),(0,9),(1,6),(1,7),(1,8),(2,6),(2,7),(2,8),
 (3,9),(3,10),(3,11),(4,9),(4,10),(4,11),(5,8),(5,11),(6,10)]
```

The flow is

```text
[4,6,2,4,1,5,5,7,2,1,3,2,3,2,1,7,3,1].
```

Its color-4 matching is M={(0,5),(1,6)}. Deleting its endpoints leaves components {2,7,8} and {3,4,9,10,11}, of orders three and five. The candidate lemma already excludes a circuit union covering the matching endpoints.

The max-flow obstruction independently blocks all three terminal partitions:

| Source terminals S | Deficient side X | Boundary edges in H, by index |
|---|---|---|
| {0,1} | {0,1,7} | {2,5,7} |
| {0,5} | {0,3,4,5,9,10,11} | {1,15,17} |
| {0,6} | {0,3,4,6,9,10,11} | {1,6,16} |

Each side contains both source terminals and no sink terminal: η=2 but the boundary has only three edges. Each network has maximum value three instead of four. The middle row is also a nontrivial three-edge cut of G separating the two matching edges.

### A 14-vertex obstruction after the candidate test passes

The [certificate](matching_terminal_flow.json) also gives a 14-vertex graph with color matching {(1,7),(3,11)}. Its unmatched induced graph is connected and has cycle-space dimension two. All four candidate circuit unions exist, but every one splits the four terminals between two circuits in counts **one and three**. Thus the additional circuit-parity condition can fail even for a two-edge matching when small cyclic cuts are allowed.

Its three terminal networks again have value three. All source choices, deficient cuts, candidate circuits, graph edges, and flow values are saved and independently checked. No assertion of minimal order is needed for either example.

## 5. Exact matching transport under a switch

Return to a nowhere-zero three-bit flow f and write M_b=f⁻¹(b). Switch by a on a legal circuit C. Its own matching remains fixed:

\[
M'_a=M_a.
\]

For b≠a, put Q_b=C∩(M_b∪M_{a+b}). Then

\[
\begin{aligned}
M'_b&=(M_b\setminus C)\cup(M_{a+b}\cap C)=M_b\mathbin\triangle Q_b,\\
|M'_b|-|M_b|&=|C\cap M_{a+b}|-|C\cap M_b|,\\
D'_b&=D_b\mathbin\triangle\partial Q_b.
\end{aligned}
\tag{6}
\]

Here ∂Q_b is the set of odd-degree vertices of Q_b. The first two identities follow from exchanging the paired values b and a+b on C. Taking incidence boundaries over F₂ gives the third. Since each M is a matching, its incidence boundary is exactly its endpoint set.

The last equation tracks the terminals of the new max-flow problem. A switch can change both the deleted edges and the source/sink candidates. There is no proved monotonicity of the matching sizes, the number of feasible partitions, or the number of suitable matchings along a general repair sequence.

### All first switches of the saved hard flower flow

The initial J₅ flow has no suitable matching and no marked incident plane. Exhausting its 610 legal circuit switches gives:

| Smallest color-class size after switching | Switches | Switches producing at least one suitable matching |
|---|---:|---:|
| 2 | 77 | 77 |
| 3 | 435 | 435 |
| 4 | 98 | 64 |
| **Total** | **610** | **576** |

All 512 switches that lower the smallest class from its initial size four create a suitable matching. Another 64 create one without lowering that size. The guarantee for size two now has a general proof on these cores; the size-three statement in this table is specific to the audited starting flow.

None of these first switches is itself a successful lift, as checked in the preceding flow-component work. A suitable matching provides the next fiber repair. The other 34 first switches are not declared trapped: this table neither tests all later sequences nor equates absence of suitable matchings with absence of marked planes.

### A new two-switch construction from the two-edge theorem

Using the saved native J₅ edge order, first add 2 on the seven-circuit

\[
\{0,2,4,5,15,17,24\}.
\]

The color-5 matching becomes {6,12}, whose graph edges are (2,10) and (4,11). Use source terminals {2,10} and sink terminals {4,11}. The network supplies intersection circuits with cycle codes **1220 and 524**.

Applying the earlier repair construction to this pair adds 5 on one eighteen-circuit, of cycle code 1362. The final first functional is 1. The formula w=t+y+z then produces a fourth cycle and a verified five-layer cover. This is a second explicit two-switch route, obtained through a two-edge matching; it does not improve the already known optimal distance of two.

## 6. Independent verification and scope

The [constructor](matching_terminal_flow.py) uses augmenting paths in a capacitated network. The [independent verifier](verify_matching_terminal_flow.py) imports no constructor and runs no max-flow algorithm. It enumerates binary cycles, traverses their circuits, and builds exactly the terminal partitions that alternate on every circuit. Both methods agree on every partition tested.

| Scope | Distinct matchings | Balanced terminal partitions | Feasible partitions | Suitable matchings |
|---|---:|---:|---:|---:|
| All feasible Petersen planes | 295 | 3,790 | 170 | 110 |
| Previously specified J₅ neighborhood | 937 | 108,243 | 799 | 374 |
| **Total** | **1,232** | **112,033** | **969** | **484** |

This retains the prior 1,076-plane J₅ scope, rather than claiming a full census of J₅ matchings. In addition:

- Every one of **2,940 two-edge matchings** on the nine saved snark cores and the K₄/K₃,₃ controls passes the source choice consisting of one whole matching edge. Both output even subgraphs are circuits.
- **34,501 edge-deletion checks** independently verify that these graphs have no cut of size at most three except a single-vertex cut.
- All **4,270 matching updates** from the 610 flower switches satisfy (6).
- Detailed network certificates cover the seven matchings at each of the three saved path states. Each failed network has both a feasible partial flow and a cut of the same capacity, proving its stated optimum. Successful networks give the intersection pair directly.
- Both small-cut counterexamples and every actual switch, flow value, intersection circuit, and cover layer in the new two-switch construction pass independent checks.
- A three-edge Petersen color class fails all ten terminal choices and has a unique candidate consisting of two pentagons with three terminals each, checking the limit of the size guarantee on a core.

The [saved JSON](matching_terminal_flow.json) includes source hashes, deterministic audit hashes, terminal signings, primal flows, deficient cuts, intersection witnesses, and the new graph and cover certificates. Reproduce with Python 3 and the standard library:

```bash
python3 -B research/five-cdc-attempt/matching_terminal_flow.py
python3 -B research/five-cdc-attempt/verify_matching_terminal_flow.py
```

## 7. What this changes in the attack

The matching branch of repair now has a concrete optimization interface: **choose terminal signs, then test cuts or construct a flow**. A failed matching has an explicit family of deficient cuts, including failures that survive the earlier candidate test. Actual circuit switches transport the matching and its terminal set by (6).

On cyclically four-edge-connected cores, a color class of size at most two is a proved sufficient endpoint for this search. The missing existence argument must still produce a suitable matching, a feasible terminal partition, or a marked plane from an arbitrary relevant exchange component. Counting many escapes from one J₅ state does not establish that argument. The general five-cycle double cover conjecture remains unproved by this work; no literature-novelty claim is made for these deductions.

Follow-up: [A globally minimum color class can still block every incident fiber](minimum-color-obstruction.md) rules out cardinality optimality as a sufficient condition, using a cyclically four-edge-connected 114-vertex graph with an elementary optimum of six and an exact two-switch repair that stays at that optimum.
