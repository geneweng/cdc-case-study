# A matching criterion for complete coordinate-fiber repair

Research date: **5 October 2026**.

A fixed color matching now gives an exact description of the previously missing half of coordinate-fiber repair. **A fiber admits a successful first coordinate outside its fixed projection exactly when its zero-projection matching is the intersection of two binary cycles.** Here a binary cycle means an even subgraph, possibly disconnected. The criterion depends on the matching and the graph, not on the particular two-bit coloring of the fixed projection.

Together with the three existing linear tests for first coordinates inside the projection, this gives an **exact test for whether the entire fiber contains a successful flow**. It also constructs the required flow switches and a five-layer cover.

On the flower graph J₅, the criterion explains the saved two-step repair structurally. Initially all seven color matchings fail. Six fail because required circuit edges would give a vertex degree three. For the seventh, a unique candidate consists of two circuits containing respectively five and three matching endpoints, both odd. The first, neutral switch creates two usable matchings; one directly supplies the second switch and a cover.

The general conjecture is not proved. The remaining existence problem is to reach a flow with a suitable color matching, or a marked plane. The [previous charge-transport formulas](cut-certificate-transport.md) lead to the reduction below.

## 1. What stays fixed when the first coordinate changes

Let G be a connected loopless cubic graph with a nowhere-zero F₂³-flow f. Fix a nonzero increment a and let

\[
M=f^{-1}(a),\qquad D=V(M),\qquad B=V(G)\setminus D.
\]

The color class M is a matching. Every legal a-switch preserves M: it changes a value x≠a to x+a, which is still neither zero nor a.

Choose two independent coordinate functionals y,z annihilating a, and a first functional ℓ with ℓ(a)=1. After this linear choice of coordinates, write

\[
f=4F+2y+z,
\]

so a has coordinate value 4. The fixed projection (y,z) vanishes exactly on M. Every possible first coordinate in its fiber is a binary cycle F with M⊆F. Conversely, any such F gives a nowhere-zero flow with the same projection.

Changing from one feasible F to another changes a binary cycle supported on G−M. Switching by a on its circuit components realizes the change. In a cubic graph of order n and girth g, at most ⌊n/g⌋ circuits suffice for the whole fiber update.

The vertex-normal formula has a particularly simple consequence here. Its invariant scalar is

\[
\nu(v)\cdot a=
\begin{cases}
0,&v\in D,\\
1,&v\in B.
\end{cases}
\]

Indeed, a lies in the incident flow plane exactly when a is one of the three incident values. For a component K of G−F, the obstruction bit is therefore |K∩B| modulo two. Every component of G−F has even order, since all its vertex degrees are one or three. Consequently the obstruction bit is also

\[
|K\cap D|\pmod2.
\tag{1}
\]

Thus, although switches change the complement components, their charge can be tested using a **fixed set of marked vertices**, the endpoints of M.

## 2. Two intersecting even subgraphs give exactly the outside-coordinate repairs

**Matching theorem.** Fix the projection annihilating a. It admits a successful first coordinate with ℓ(a)=1 if and only if there exist binary cycles F,t such that

\[
\boxed{F\cap t=M.}
\tag{2}
\]

In particular, existence of such an outside-coordinate completion is independent of the fixed projection's nonzero colors, once M is specified.

**Proof by the fourth-coordinate formula.** In coordinates f=4F+2y+z, a canonical five-label lift is a binary cycle w whose restriction to F equals 1+yz. Put

\[
t=w+y+z.
\]

On F this gives

\[
t=1+yz+y+z=(1+y)(1+z).
\]

It equals one precisely where y=z=0, namely on M. Hence F∩t=M.

Conversely, given (2), use F as the free coordinate while keeping y,z fixed, and set w=t+y+z. The same identity shows that w has the required restriction on F. It is a binary cycle and supplies the canonical five-label lift. ∎

There is also a direct component interpretation. Once F⊇M is chosen, a binary cycle t with F∩t=M must equal one on M, zero on F∖M, and is free on G−F. Binary incidence completion is possible exactly when each component of G−F has an even number of M-endpoints. This is precisely (1).

The construction does not assume a supplied cover. Given F,t, change the current first coordinate to F by a-switches and use **w=t+y+z** as the fourth coordinate. The earlier five-vector palette then decodes the five even cover layers.

## 3. An equivalent circuit condition

The intersection condition has a graph description without flow labels.

**Circuit criterion.** A matching M is the intersection of two binary cycles if and only if there is an even subgraph L⊆G−M such that:

1. Every endpoint of M lies on L.
2. Every circuit component of L contains an even number of endpoints of M.

**Proof.** If M=F∩t, set L=F+t. At an M-endpoint, the two L-edges belong to different cycles F,t. At an unmatched vertex used by L, both L-edges belong to the same one: otherwise F and t would need four incident edges in a cubic graph. Thus the choice between F and t changes exactly at M-endpoints as one traverses a circuit. There must be an even number of changes.

Conversely, color the edges of each circuit of L with two colors, changing color at M-endpoints and retaining it at the other vertices. The evenness assumption makes the coloring close. Adjoin M to each color class to obtain binary cycles F and t intersecting exactly in M. ∎

A candidate L with c circuit components gives exactly 2ᶜ ordered pairs (F,t). This counts pairs, not distinct first coordinates; several partners t can work for one F.

### The existence of a candidate L is already a linear question

Because a vertex in D has degree two in G−M, every edge outside M incident to D is forced into L. Only edges of the induced graph G[B] remain free.

**Candidate lemma.** An even subgraph L⊆G−M covering D exists if and only if **every component of G[B] has even order**. If it exists, the candidates form an affine space with direction Z(G[B]), and their number is

\[
2^{\,|E(G[B])|-|B|+c(G[B])}.
\tag{3}
\]

For B empty, the exponent is zero.

**Proof.** The forced edges already give degree two at each vertex of D. At a vertex of B, the free edges must supply the parity of the forced edges incident to it. This incidence system is solvable exactly when each component K of G[B] has even total prescribed parity. That total is |δ_G(K)|, which has the same parity as |K| in a cubic graph. Differences between solutions are exactly binary cycles supported on G[B]. ∎

An unmatched vertex whose three neighbors are matched is an immediate obstruction: it is an odd singleton component of G[B], and all three of its incident edges would be forced into L.

Passing the candidate lemma is not enough. The additional parity requirement on each circuit of L can fail for every candidate. That is the remaining part of the matching test; no polynomial algorithm for choosing a suitable candidate is claimed here.

## 4. The complete fiber test

On a non-three-edge-colorable cubic core, let U be a feasible two-dimensional coordinate plane and let M be its zero set. As before, call U **marked** if one of its three nonzero first coordinates passes the linear completion test.

**Complete fiber theorem.** The fiber over U contains a successful flow space if and only if

\[
\boxed{\ U\text{ is marked}\quad\text{or}\quad
M\text{ is the intersection of two binary cycles}.\ }
\tag{4}
\]

**Proof.** A successful flow's first coordinate either belongs to U or lies outside it. The first case is exactly the definition of a mark. For the second case, its functional is nonzero on the increment a annihilated by U, and the matching theorem applies. Both conditions also construct a successful extension. ∎

Neither condition subsumes the other. Among the 400 feasible Petersen planes, 65 are unmarked but their matchings pass (2); 245 are marked while their matchings fail (2). Thus matching failure alone does not exclude a fiber, just as an unmarked plane alone did not exclude it.

For a starting rank-three flow, this gives an exact criterion for reaching success within one whole fiber round: at least one incident plane is marked, or at least one of its seven color matchings satisfies (2). A whole round can require several actual circuit switches.

There is a useful necessary condition on an already successful flow. If ℓ is its successful first functional, all four color matchings Mₐ with ℓ(a)=1 satisfy (2). Conversely, just **one** suitable color matching is enough to reach success within its fiber, even when the starting flow is unsuccessful.

## 5. A general positive case: a value occurring on one edge

**Singleton corollary.** If a nowhere-zero three-bit flow has a value a occurring on exactly one edge e=uv, then it can be repaired within the a-fiber to a five-label lift.

**Proof.** Delete e and project the flow to F₂³/⟨a⟩. Every remaining edge has nonzero projected value, so G−e has no bridge. It is connected, since a graph with a nowhere-zero flow has no bridge to begin with. A connected bridgeless subcubic graph has no cut vertex: two components attached at a cut vertex would each require at least two incident edges there, exceeding degree three.

Hence u and v lie on a common circuit L in G−e. It contains exactly two endpoints of M={e}, so the circuit criterion holds. Equivalently, the two u–v arcs of L, each adjoined to e, are circuits F,t whose intersection is {e}. Apply the matching theorem. ∎

The repair retains the original two-bit projection and uses at most ⌊n/g⌋ circuit switches. The missing general step is not this singleton case, but obtaining an appropriate color matching in an arbitrary starting component.

## 6. A structural explanation of the J₅ obstruction and escape

Use the saved native edge order and fundamental cycle basis in [flow_space_components.json](flow_space_components.json). Cycle codes below are coefficient masks in that basis, not edge masks.

### Why the initial flow cannot succeed in any single fiber

The initial flow has no marked incident plane, as certified by the 21 paired-cut failures in the [preceding cut report](fiber-cut-obstructions.md). Its seven matching tests fail as follows:

| Increment a | Color-matching edges | A vertex with all three remaining edges forced into L |
|---|---|---:|
| 1 | {4,15,18,22,28} | 2 |
| 2 | {1,8,19,26} | 4 |
| 3 | {11,14,20,24} | 7 |
| 4 | {0,3,10,16,29} | 18 |
| 6 | {2,13,21,27} | 8 |
| 7 | {7,9,23,25} | 0 |

For increment 5, the matching is {5,6,12,17}. Its unmatched induced graph is a **tree on 12 vertices**, so equation (3) gives exactly one candidate L. Its cycle code is 1465, and it consists of circuits of lengths 11 and 9. They contain respectively **five and three matching endpoints**, so neither closes the required two-color assignment.

These are structural certificates for every matching failure. Combined with the failed plane marks and (4), they show that the initial flow cannot reach success using any single increment, even with arbitrarily many switches by that increment. This is stronger than checking only its individual circuit neighbors, and consistent with the earlier exact fiber-distance calculation.

### What the first switch changes

The six-circuit switch adding 4 leaves its own color matching fixed. It changes the color-2 matching from {1,8,19,26} to **{2,19,26}**, and the color-7 matching from {7,9,23,25} to **{11,23,25}**. Both new matchings pass (2).

| Stage | Marked incident planes | Increments whose matchings pass (2) |
|---|---:|---|
| Initial | 0 | None |
| After the six-circuit switch | 0 | 2, 7 |
| After the eleven-circuit switch | 3 | 2, 3, 6, 7 |

The first switch was neutral for the older potential Ψ=(4,38), and it creates no marked plane. Its progress is now visible as the creation of suitable color matchings. This table is evidence for this path, not a proof that their number can always be increased.

### Constructing the second switch from an intersection pair

For M={2,19,26}, the unmatched induced graph is connected on 14 vertices with 15 edges. Its cycle-space dimension is two, so there are four candidate L's. Three pass the per-circuit parity test. They give ten ordered intersection pairs, using nine distinct first coordinates.

One pair has cycle codes

\[
F=577,\qquad t=996,\qquad F\cap t=M.
\]

The intermediate flow's first coordinate for ℓ=2 has code 712. Thus its required change has code 137, the XOR of 712 and 577. It is the eleven-circuit

\[
\{3,4,7,8,18,20,21,23,24,25,27\}.
\]

Adding 2 on this circuit is exactly the previously saved second switch. The fixed coordinate functionals are 1 and 4, with cycle codes 406 and 1071. The construction supplies the fourth binary cycle directly as

\[
w=t+y+z,
\]

and decodes a verified five-layer cover. No search over possible fourth coordinates is needed for this witness.

This also explains the earlier unmarked plane ⟨406,1071⟩ containing nine successful spaces among 64 extensions. Its matching permits outside-coordinate repairs despite all three inside-coordinate tests failing.

## 7. Independent checks

The [constructor](matching_fiber_repair.py) enumerates candidates L, splits their circuits into the two colors, and constructs every resulting pair F,t. The [independent verifier](verify_matching_fiber_repair.py) imports no constructor code. It finds the admissible F's from component parity in G−F, counts partners by independent incidence completion, and directly checks all saved intersections. It separately enumerates complete flow-space extensions and all restrictions of a fourth cycle.

| Scope | Feasible planes | Distinct color matchings | Matchings passing (2) | No candidate L | Candidates exist, but every one fails circuit parity |
|---|---:|---:|---:|---:|---:|
| All Petersen planes | 400 | 295 | 110 | 125 | 60 |
| Specified J₅ neighborhood | 1,076 | 937 | 374 | 503 | 60 |

For the J₅ planes, the two parts of the complete fiber criterion separate as follows:

| Plane marked? | Matching passes (2)? | Planes |
|---|---|---:|
| No | No | 352 |
| No | Yes | 192 |
| Yes | No | 302 |
| Yes | Yes | 230 |

The neighborhood consists of planes incident to the initial state, its 185 fiber neighbors, and the saved path. It is not a census of every J₅ plane.

Across both graphs, **140,456 outside-coordinate completion tests** and **19,832 distinct extension spaces** agree with the exact criterion. The candidate-count formula is checked on all 1,232 color matchings in the audit. Detailed certificates cover all 21 color matchings along the path, including repeated matchings, the tree obstruction, both cycles in the intersection pair, the actual eleven-circuit switch, and its decoded cover. All 45 singleton matchings of the two graphs also pass the criterion.

The [saved certificate](matching_fiber_repair.json) includes source hashes, exact audit totals and record hashes, all path matching data, every admissible intersection pair there, and the explicit flow/cover construction. Reproduce with Python 3 and the standard library:

```bash
python3 -B research/five-cdc-attempt/matching_fiber_repair.py
python3 -B research/five-cdc-attempt/verify_matching_fiber_repair.py
```

## 8. The remaining existence step

The five-layer existence problem can now be expressed as finding a nowhere-zero three-bit flow with **one color class that is the intersection of two binary cycles**. A successful flow supplies four such classes; one suitable class supplies a successful flow after a fiber update. This equivalence does not prove that a suitable class occurs on every graph or in every exchange component.

The new question is therefore concrete: can changes of increment always create such a matching, or otherwise reach a marked plane? The initial J₅ example shows why one increment can be permanently insufficient and how a neutral move changes the relevant matching geometry. A general argument must still guarantee that some sequence reaches the favorable case.

Follow-up: [Terminal flows and two-edge color classes](matching-terminal-flow.md) give an exact max-flow/cut test parameterized by matching size, prove repair for every two-edge color class on cyclically four-edge-connected cubic cores, and track matching endpoints under actual switches. The global existence step remains open.
