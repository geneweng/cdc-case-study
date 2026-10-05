# Flow components through affine coordinate fibers

Research date: **5 October 2026**.

This checkpoint returns to flows on the underlying cores. It assumes no supplied five-layer cover. The main structural result is an **exact description of flow-exchange components by intersections of full-support subspaces of the binary cycle space**. Fixing two coordinates makes the remaining feasible flows an affine space connected by circuit switches. This replaces exhaustive circuit-neighborhood construction with incidence calculations and linear solves.

As a principal test, all **103,602,240 labeled nowhere-zero three-bit flows on the 20-vertex flower graph J₅ lie in one exchange component**. Every one reaches a five-label lift within two coordinate-fiber rounds, hence within **eight circuit switches**. The graph is cyclically 5-edge-connected and contains no induced Petersen four-pole. Exactly 140 classes under linear relabeling require two fiber rounds; a concrete member has actual circuit distance exactly two.

These are a general component characterization and finite core results. Universal connectivity of three-bit flow spaces and the existence of a successful space on arbitrary cores are not proved.

## 1. The state space and the relevant endpoint

Let G be a connected bridgeless cubic graph and let Z be its binary cycle space. A nowhere-zero three-bit flow is a triple of binary cycles (x,y,z) whose supports together cover every edge. A circuit move adds a nonzero vector a to the values on a single connected circuit C, provided a is absent from C. Every intermediate flow remains nowhere-zero.

Call a flow **successful** if it admits one of the five-label lifts in the [original extra-coordinate formulation](attempt.md). Such a lift constructs five even layers covering every edge exactly twice. This endpoint is more specific than merely having a coordinate support that belongs to some independently chosen cover.

For graphs without a three-edge-coloring, every nowhere-zero three-bit flow has coordinate rank three: a rank-two flow would use the three nonzero elements of a two-dimensional binary space and give a proper three-edge-coloring. Thus its coordinate span W is a three-dimensional subspace of Z with full edge support. Its ordered bases give precisely one orbit of 168 flows under GL(3,2).

The label symmetry alone would not justify identifying connected components: a symmetry of a graph can exchange different components. The next lemma supplies the missing reachability statement.

## 2. Linear relabeling stays inside a flow component

**Lemma.** For nowhere-zero binary flows of any dimension, f and Tf lie in the same circuit-exchange component for every invertible linear map T.

**Proof.** It suffices to implement an elementary coordinate addition fⱼ ← fⱼ+fᵢ, with i≠j. The support of fᵢ is an even edge subgraph. Decompose it into edge-disjoint circuits and add the unit vector eⱼ on each circuit. On every affected edge the i-th bit is one, whereas eⱼ has i-th bit zero. Hence no edge currently has value eⱼ, and every switch is legal. These moves perform the coordinate addition. Elementary coordinate additions generate GL over the binary field. ∎

This lemma also applies to rank-deficient flows. It does not imply that all flows on a graph are connected: changing the coordinate span is a separate issue.

## 3. A fixed projection has a connected affine fiber

Fix binary cycles x,y and write T=supp(x)∪supp(y) and S=E(G)\T. A third coordinate z makes (x,y,z) nowhere-zero exactly when

\[
z\in Z,\qquad z_e=1\quad(e\in S).
\]

This is a binary linear system. If z₀ is one solution, its complete solution set is

\[
z_0+Z(T),
\]

where Z(T) consists of cycles supported entirely on T.

**Fiber lemma.** Any two feasible third coordinates are connected while x,y stay fixed, using circuit switches supported on T.

**Proof.** Their difference h is a binary cycle supported on T. Decompose h into circuits and add the third-coordinate unit vector on each. At every changed edge, at least one of x,y is nonzero, so neither intermediate value can be zero. ∎

For cubic G the circuits of h are vertex-disjoint. If G has n vertices and girth g, the update uses at most ⌊n/g⌋ circuits. This is a bound for a whole fiber update, not a claim that such an update is always one circuit.

The same proof works for any number of fixed coordinates and one free binary coordinate. It is related to the cycle-decomposition argument in Observation 6.11 of [Esperet et al., *Nowhere-zero flow reconfiguration*, v4](https://arxiv.org/html/2512.17342v4#S6.SS3). Here the fixed projection may vanish; feasibility forces the two endpoints to agree on its zero set. Their paper proves general connectivity for eight binary coordinates, which does not supply the three-coordinate result needed here.

## 4. Exact component reduction to subspace incidence

Suppose G has no nowhere-zero flow with fewer than d binary coordinates. For the main application d=3; the negative control below uses d=2. Form an incidence graph with:

- One state vertex for each d-dimensional full-support subspace W of Z.
- One fiber vertex for each (d−1)-dimensional subspace U contained in at least one such W.
- An incidence whenever U⊂W.

Equivalently, put an edge between distinct state spaces sharing a (d−1)-dimensional subspace. We call that adjacency one **fiber round**.

**Component theorem.** The connected components of this incidence graph are in bijection with the circuit-exchange components of nowhere-zero d-bit flows on G.

**Proof.** Flows with the same coordinate span are connected by the relabeling lemma. Suppose W and W′ contain a common U. Choose the same basis for U and extend it by z and z′ to bases of W and W′. Both ordered tuples are nowhere-zero. On every edge outside supp(U), both final coordinates equal one. Their difference is therefore supported on supp(U), and the fiber lemma connects them.

Conversely, a circuit move adds a vector a times a binary circuit indicator. Choose d−1 independent linear functionals annihilating a. Their coordinate cycles stay fixed throughout the move. They span a common (d−1)-dimensional subspace of the initial and final coordinate spans; the minimum-rank hypothesis ensures both spans still have dimension d. Thus a move either stays within a state vertex or crosses one fiber. ∎

**Constructive lifting of a fiber round does not require preliminary relabeling moves.** Given the current labeled flow and a basis of U, express those cycles as linear functionals of the current coordinates. Let a span their common annihilator. Choose a remaining coordinate functional evaluating to one on a. Its desired change h is supported on supp(U). Adding a on the circuit components of h implements the round in the original labeling.

Consequently, for a cubic graph of girth g,

\[
\text{fiber distance to success}\ \le\ \text{circuit distance to success}
\ \le\ \lfloor n/g\rfloor\,\text{fiber distance to success}.
\]

These distances permit temporary increases in any previously studied defect potential.

### Linear marks for detecting successful components

For an ordered basis (F,y) of a plane U, the [earlier alternating-form criterion](continuation.md#3-fixing-two-coordinates-makes-the-last-choice-linear) seeks a binary cycle z satisfying

\[
 z_e=1\quad\text{where }F_e=y_e=0,
 \qquad
 \sum_{e\in\delta(K)}y_ez_e=0
 \quad\text{for every component }K\text{ of }G-F.
\]

Together with the cycle equations, this is linear in z. Mark U if one of these systems is consistent. It is enough to test the three choices of nonzero F in U: the two remaining choices of y differ by F, whose contribution vanishes on every cycle cut.

**A component contains a successful flow if and only if it contains a marked plane.** A consistent system supplies a successful full-support span containing U. Conversely, any successful flow has coordinates (F,y,z) giving such a mark.

These marks provide an exact existence test within components. They need not mark every fiber incident to a successful space, because that space's successful first coordinate may lie outside the fiber. The distance census below instead marks successful state spaces directly and tests all seven coordinate choices.

This formulation identifies a global target without a prescribed-layer assumption. It does not prove that every incidence component has a marked plane. Even proving universal connectivity would still leave the nonemptiness of the successful set to establish.

## 5. Complete component checks on the saved snark cores

The inputs are Petersen, the two saved 18-vertex snarks, and the six saved 20-vertex snarks. Their edge lists are recorded explicitly. All are independently checked to be simple cubic graphs, to have girth at least five, to have no cyclic cut of size at most three, and to have no rank-two full-support flow space.

Every one of these nine three-bit flow graphs is connected. The table counts coordinate-span classes, without identifying graph automorphisms:

| Core | Flow classes | Already successful | Fiber distance 1 | Fiber distance 2 | Induced Petersen four-poles |
|---|---:|---:|---:|---:|---:|
| Petersen | 170 | 170 | 0 | 0 | 15 |
| Snark18_0 | 118,960 | 30,588 | 88,348 | 24 | 1 |
| Snark18_1 | 119,260 | 30,078 | 89,170 | 12 | 2 |
| Snark20_0 = J₅ | 616,680 | 137,320 | 479,220 | 140 | 0 |
| Snark20_1 | 613,740 | 114,856 | 498,508 | 376 | 1 |
| Snark20_2 | 612,630 | 112,779 | 499,520 | 331 | 1 |
| Snark20_3 | 616,840 | 115,925 | 500,336 | 579 | 2 |
| Snark20_4 | 612,330 | 112,726 | 499,244 | 360 | 1 |
| Snark20_5 | 614,880 | 107,606 | 506,970 | 304 | 2 |

The total is **3,925,490 classes**, representing **659,482,320 labeled flows**. The earlier records checked descent behavior; these new calculations determine entire components and exact fiber distances. The retained graph catalog does not assert anything about larger orders.

As controls, the two-bit flow graph on K₄ has one component with six labeled flows. On K₃,₃ it has **two components**, each with six labeled flows. Both components already have covers. The independent verifier recovers these components by explicit circuit moves, as it also does for the three-bit Petersen quotient. The K₃,₃ result concerns two-bit flows and is not a counterexample to three-bit connectivity.

## 6. The principal core has no small cyclic cut or Petersen piece

Define J₅ using vertices aᵢ,bᵢ,cᵢ,dᵢ for i=0,…,4. Join each aᵢ to bᵢ,cᵢ,dᵢ; join the bᵢ in a five-cycle; join cᵢcᵢ₊₁ and dᵢdᵢ₊₁ for i=0,…,3; and close with c₄d₀ and d₄c₀. The certificate supplies an explicit isomorphism from this description to the saved Snark20_0 edge order.

All cuts of size at most four are checked: none separates cycles on both sides. The b-ring supplies a cyclic five-edge cut, so cyclic edge-connectivity is exactly five. An independent induced-subgraph search finds no Petersen four-pole.

The J₅ incidence graph has **616,680 state vertices and 252,490 fiber vertices**, all in one component. Each fiber has 1,2,4,8,16,32,64,128, or 256 state members. These powers of two also follow from the affine formula: for a feasible plane U with T=supp(U), its distinct extensions number 2^(dim Z(T)−2), since adding either basis vector of U does not change the resulting three-space.

Every state is within two fiber rounds of success. Since n=20 and girth is five, the constructive bound is **eight actual circuit switches from every starting flow**. This bound need not be optimal. The 140 distance-two classes represent 23,520 labeled flows; none can be repaired by one circuit, or even by one same-increment update on an arbitrary even subgraph.

### A verified two-circuit repair on J₅

In the certificate's edge order, one of those 140 classes has initial flow

```
4,2,6,4,1,5,5,7,2,7,4,3,5,6,3,1,4,5,1,2,3,6,1,7,3,7,2,6,1,4
```

The independent verifier enumerates **all 610 legal circuit/increment choices** from this flow and confirms that every endpoint fails all seven five-label lift tests. A saved escape is:

1. Add 4 on edges `{1,2,7,8,9,11}`, a circuit of length six.
2. Add 2 on edges `{3,4,7,8,18,20,21,23,24,25,27}`, a circuit of length eleven.

The intermediate flow remains unsuccessful. The final flow has a decoded five-layer cover, verified edge by edge and vertex by vertex. Its actual circuit distance is therefore **exactly two**. This does not assert that the first move preserves the older lexicographic defect potential; fiber distance and potential descent are different measurements.

The example is an obstruction to direct one-step success on a core where the recent Petersen-piece and star-extension methods do not apply. It is not a counterexample to cover existence.

## 7. Independent computations and saved evidence

The [Python constructor](flow_space_components.py) invokes a [C++ enumerator](flow_space_components.cpp) that enumerates every full-support rank-three subspace by reduced row echelon form, and every rank-two subspace for the controls. It joins states sharing a hyperplane, uses the cut-parity lift test, and computes distances by traversing fibers.

The [independent verifier](verify_flow_space_components.py) invokes a separate [C++ affine enumerator](verify_flow_space_components.cpp). It imports no constructor code. It enumerates lower-dimensional spaces instead, solves for their feasible final coordinates, and identifies repeated extensions by Gaussian elimination. Its success test builds consistency equations for restricting a fourth binary cycle; it does not use the constructor's component cuts. It obtains connected components by traversal rather than the constructor's disjoint-set unions.

For each graph both programs produce the same sorted binary records `(space key, least component key, fiber distance + 1)`. The [certificate](flow_space_components.json) retains their SHA-256 digests, exact counts, all distance-two keys, one explicit cover witness per component, and the J₅ repair. Large intermediate record files remain temporary and can be regenerated.

Additional Python checks validate every cycle basis, graph simplicity and cuts, all Petersen-piece searches, the J₅ isomorphism, the small explicit circuit graphs, the 610 rejected first moves, both successful repair steps, and every decoded five-layer cover. The finite component and distance claims are computer-assisted; the fiber and component theorems above have direct proofs. No literature-wide novelty claim is made.

Reproduce with Python 3 and a C++17 compiler, with assertions enabled:

```bash
python3 -B research/five-cdc-attempt/flow_space_components.py
python3 -B research/five-cdc-attempt/verify_flow_space_components.py
```

The next structural question is whether every incidence component on an arbitrary bridgeless cubic core meets a plane satisfying the linear completion test. A closed unmarked component would refute the all-starting-flow repair mechanism, while cover existence could still hold in another component. The weaker existence target requires only one marked plane per graph. Neither universal statement is established by this checkpoint.

Follow-up: [Cut certificates for failed coordinate completion](fiber-cut-obstructions.md) gives an exact paired-cut obstruction and completion-count formula. It also verifies that an unmarked plane can contain successful extensions, including nine among 64 extensions of the plane used by the second switch above.
