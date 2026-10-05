# An actual core can require a neutral auxiliary exchange

Research date: **5 October 2026**.

There is a supplied core cover with one bad eleven-cycle region for which **every single auxiliary-label exchange fails**, even when the exchange may use an arbitrary even edge subgraph. Two circuit exchanges repair it: the first leaves the region bad, and the second makes it extend. Its auxiliary-exchange distance is therefore **exactly two**.

This strengthens the [local eleven-port obstruction](eleven-cycle-obstruction.md). The six obstructing terminal partitions now occur simultaneously in one actual core, with no artificial outside transitions or protected neighbors. Choosing transitions more carefully cannot produce a strictly improving first move. The example still has a successful completion; it does not disprove the length-eleven completion equivalence or the 5-CDC conjecture.

The native cubic base has 22 vertices. Four independently verified full certificates give Blowup and SemiBlowup completions on 132 and 110 vertices, and Petersen-attached variants on 142 and 120 vertices whose cores have no four-flow. A two-edge insertion lemma preserves the exchange distance and gives an infinite family of such core obstructions.

## 1. What one move means

Keep the notation X, H, K and distinguished cover label 0 from the [component criterion](core-component-exchange.md). A move chooses one auxiliary pair t={α,β} from {1,2,3,4} and swaps those labels on any even edge subgraph of

\[
T_t=\{e:|Q(e)\cap t|=1\}.
\]

This includes a circuit, several circuits, or any union of terminal trails that is even after the target is restored. A move uses one fixed pair of labels throughout. It preserves the validity of the five-layer core cover and its distinguished layer.

The distance is measured from the **supplied core cover** to any core cover whose target boundary extends with the prescribed whole layer on H. It is not a flow-switch distance or a minimum over all possible starting covers. Core cover exchanges do not change flow values.

There is only one selected cycle in the example, so no other region needs protection. An unsuccessful move leaves the bad-region count at one. Thus any successful sequence must begin with a neutral move, if it changes the cover at all.

## 2. The explicit cubic base and cover

The selected cycle is (0,1,…,10). The other vertices are 11,…,21. Add its eleven stems according to this table. A pair such as 12 denotes cover labels {1,2}, not a flow value.

| Port i | Outside endpoint | Cover pair |
|---|---:|---|
| 0 | 19 | 12 |
| 1 | 13 | 12 |
| 2 | 11 | 13 |
| 3 | 12 | 12 |
| 4 | 16 | 34 |
| 5 | 20 | 12 |
| 6 | 11 | 23 |
| 7 | 13 | 14 |
| 8 | 20 | 24 |
| 9 | 17 | 13 |
| 10 | 15 | 14 |

The eleven remaining outside edges are:

| Edge | Cover pair | Edge | Cover pair |
|---|---|---|---|
| 11–21 | 12 | 12–16 | 14 |
| 12–18 | 24 | 13–21 | 24 |
| 14–15 | 34 | 14–17 | 03 |
| 14–18 | 04 | 15–16 | 13 |
| 17–19 | 01 | 18–19 | 02 |
| 20–21 | 14 | | |

These edges and the selected cycle form a connected simple cubic graph. Contract the selected cycle to obtain K: one degree-eleven target and eleven cubic outside vertices. The stem and outside pairs define a valid five-layer cover of K. At every outside vertex the three pairs form a triangle on three labels; each label has even degree at the target as well.

The distinguished layer on K is the four-cycle (14,17,19,18). In H prescribe junction pattern z=15 around the selected region, so all eleven cuts are marked. Encoding label i by bit 2^i, the target word is the previous hard witness

\[
r=(6,6,10,6,24,6,12,18,20,10,18).
\]

Its prefix set is the full eight-element even auxiliary space

\[
E=\{0,6,10,12,18,20,24,30\},
\]

so the boundary is rejected in both constructions. The certificate also supplies a four-flow on this native core and an initial nowhere-zero three-bit flow on each full graph with the specified whole layer on H. Thus the obstruction belongs to realizable cover and flow data.

## 3. All six actual partitions block every union

For each auxiliary pair, split the target into degree-one terminals and retain all affected edges. Every outside vertex has affected degree zero or two. Each component meeting the target terminals is therefore a path and forces the following actual pairing:

| Swap | Terminal pairs | Reachable target-port sets | Escaping sets |
|---|---|---:|---:|
| 12 | (2,6), (7,8), (9,10) | 8 | 0 |
| 13 | (0,10), (1,7), (3,4), (5,6) | 16 | 0 |
| 14 | (0,9), (1,2), (3,4), (5,8) | 16 | 0 |
| 23 | (0,3), (1,2), (4,9), (5,8) | 16 | 0 |
| 24 | (0,10), (1,7), (3,4), (5,6) | 16 | 0 |
| 34 | (2,6), (7,8), (9,10) | 8 | 0 |

The [component criterion](core-component-exchange.md) says that a reachable set is exactly a union of these pairs. All **80 swap/subset cases**, including the empty set separately for each swap, leave the prefix set equal to E. Components with no target terminal cannot change the boundary, so their cycles cannot rescue a one-step exchange.

The independent verifier proves this directly from the binary exchange equations. It computes the kernel of the incidence parity matrix for each affected graph, projects the entire kernel onto target ports, and tests every element of the image against the regional junction relation. It does not assume the path pairings recorded by the constructor are complete.

The preceding positive census of 10,812 colored rims remains valid. That family required one stem at each outside vertex and label 0 on every rim edge. Here some outside vertices have two stems, others have none, and the distinguished layer visits only four outside vertices. Compatibility between different label swaps does not rule out all six obstructions in this larger class.

## 4. A neutral move followed by a repair

First swap labels 1 and 2 on the two core edges at target ports **2 and 6**. They meet the same outside vertex 11, so they form a two-edge circuit in K. The new target word is

\[
r'=(6,6,12,6,24,6,10,18,20,10,18).
\]

Its prefix set is still E. This move is neutral: the number of bad regions remains one.

Now swap labels 1 and 3 on the three-edge core circuit through target ports **3 and 4** and outside edge **12–16**. The resulting word is

\[
r''=(6,6,12,12,18,6,10,18,20,10,18).
\]

Its prefix set is E minus {10}. Since the excluded regional charges have the form 30 XOR prefix, the surviving charge is **20**. The boundary extends in both Blowup and SemiBlowup, with the prescribed whole layer fixed on H.

After the neutral move, the actual 13-partition is {(0,10),(1,7),(2,5),(3,4)}. Four of its sixteen reachable sets escape, including the selected pair (3,4). Notice that the first move is needed even though (3,4) was already paired for swap 13: the same second circuit did not repair the original boundary. The obstruction depends on the cover word as well as its paths.

The initial boundary is bad, and Section 3 excludes every one-move repair. The two displayed circuits provide the matching upper bound. Thus the minimum number of auxiliary exchanges is exactly two, even when a move may use an arbitrary even subgraph.

## 5. Covered two-edge insertions preserve this distance

**Lemma.** Replace an edge of a covered core by a covered two-terminal graph, attached by two cut edges carrying the old edge's label pair. Suppose the inserted graph contains no selected region whose extension is part of the goal. The minimum auxiliary-exchange distance to the specified outside boundary condition is unchanged.

**Proof.** In any even-subgraph exchange, the two cut edges are selected together or not at all, by summing incidence parity over the inserted vertices. Projecting them to the old edge therefore maps an exchange to an allowed exchange on the old core, possibly an empty one, and preserves the outside boundary change. Every exchange sequence projects, giving a lower bound on the expanded distance.

Conversely, suppose an exchange on the old core selects the replaced edge. Its pair is affected by the chosen auxiliary swap, so both cut edges are affected in the expanded core. Cut them at their outside ends. All internal affected degrees are even, and the two cut ends are the only odd terminals. They lie in one component, which supplies a joining path. Use that path in place of the old edge. If the old edge was not selected, use no edges inside the insertion. This lifts the exchange and preserves the outside boundary.

After any lifted move, the two cut pairs are still equal. More generally this equality follows from even parity of every cover label across a two-edge cut. The argument thus applies successively to every move, proving the reverse distance bound. ∎

Apply the lemma to a compatible Petersen two-edge sum on the stem at port 2. All six initial target partitions persist. The neutral circuit now has seven edges and passes through the Petersen insertion; the second circuit still has three. The new core has no four-flow: a four-flow would give equal nonzero values to the two cut edges, restoring a four-flow on Petersen. The verifier independently excludes the latter by enumerating Petersen's even supports.

Repeating compatible Petersen insertions on a non-distinguished edge gives **infinitely many covered cores with no four-flow and auxiliary-exchange distance two**. This is a structural consequence of the lemma; it is not an exhaustive graph census. There is no claim that the displayed 22-vertex base is smallest.

## 6. Full graph certificates and scope

| Construction and core | Vertices | Core circuit lengths | B-internal pentagons |
|---|---:|---|---:|
| Blowup, native core | 132 | 2 then 3 | 10 |
| Blowup, Petersen-attached core | 142 | 7 then 3 | 10 |
| SemiBlowup, native core | 110 | 2 then 3 | 9 |
| SemiBlowup, Petersen-attached core | 120 | 7 then 3 | 9 |

Every graph has q=11 inserted Petersen four-poles. After the two cover exchanges, the [joint boundary completion lemma](joint-boundary-completion.md) aligns their flows with the chosen regional cover. The displayed internal pentagon counts are below 2q=22. All original E₀ flow values remain fixed, and the final five-layer cover contains the final selected flow coordinate as a whole layer. The prescribed whole layer on H never changes.

The [constructor](actual_core_exchange_obstruction.py) writes the [certificate](actual_core_exchange_obstruction.json). The [independent verifier](verify_actual_core_exchange_obstruction.py) imports no constructor or earlier verifier. It reconstructs the simple cubic graphs and both contractions; checks every cover and flow conservation equation; verifies all six failures, both core circuits, every internal pentagon switch, and the completed covers. Across four graphs it checks **384 explicit reachable-set realizations**, **28 auxiliary attempts**, and **24 fully blocked attempts**. Hashes bind the certificate to earlier local data.

Reproduce from the repository root:

```bash
python3 -B research/five-cdc-attempt/actual_core_exchange_obstruction.py
python3 -B research/five-cdc-attempt/verify_actual_core_exchange_obstruction.py
```

The search for an actual obstruction used pair-compatible rewiring of cubic cover vertices, followed by reductions of the resulting witness. The saved construction is explicit and deterministic; its proof does not depend on search coverage or on a smallest-example claim.

The next existence question must allow neutral exchanges, broader cover changes, or a different potential function. The exact component criterion remains useful as a one-step oracle, but even without protected neighbors it cannot always supply a strict decrease in bad regions. Universal length-eleven protection, eventual escape under auxiliary exchanges, the general length-eleven core reduction, and the general 5-CDC conjecture all remain unresolved here.
