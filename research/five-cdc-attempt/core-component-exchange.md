# Exact auxiliary exchanges from core connected components

Research date: **5 October 2026**.

An auxiliary-label exchange can be tested using the actual core, without choosing arbitrary transitions at every outside vertex. After splitting the target and the protected good regions, **a set of target ports is reachable exactly when it meets each connected component in an even number of ports**. A spanning forest constructs the exchange. This applies the standard parity condition for a graph T-join to the prescribed-layer boundary and protection constraints.

For the two eleven-port witnesses in the [preceding report](eleven-cycle-obstruction.md), independent enumeration checks all **3,156 even component partitions and 102,048 admissible port subsets** against both Blowup and SemiBlowup. A further census checks **10,812 simple colored rim realizations** of the harder witness: every realization admits a single-circuit repair using at least two auxiliary-label choices. Twelve full graph certificates, through **890 vertices**, exercise protected neighbors, core loops, and cores with no four-flow.

The criterion is exact for a fixed auxiliary pair and specified protecting transitions. It does **not** establish that suitable transitions and an escaping auxiliary pair always exist. The general length-eleven core reduction and the general 5-CDC conjecture remain unresolved here.

## 1. The exchange problem on the actual core

Use the notation of the [length-ten reduction](ten-cycle-completion.md). The graph X is a Blowup or SemiBlowup of a simple cubic base along disjoint selected cycles. Contract its q Petersen four-poles to obtain H, then contract the selected cycle regions to obtain K. The core K may have loops or parallel edges. A supplied five-layer cover assigns a two-element label set Q(e) to each core edge, with each label having even degree at every vertex. Label 0 is the prescribed layer.

Fix two auxiliary labels t={α,β} contained in {1,2,3,4}. Let T consist of edges carrying exactly one label of t. It is the symmetric difference of two even layers, so every core vertex has even T-degree, counting each loop twice. Swapping α and β on an even edge subgraph of T gives another valid core cover and fixes label 0.

A selected region is **good** when its boundary extends over H with the prescribed whole layer, and **bad** otherwise. The marked-cut test decides this. At each good region requiring protection, supply a perfect matching of its affected port incidences such that exchanging any union of the matched pairs leaves that region good. These matchings are hypotheses of the criterion, or individually verified witnesses. Their universal existence at length eleven is not assumed. Regions with at most seven marked cuts need no protection because every compatible boundary extends there.

For a bad target vertex v, form a split graph L:

1. Keep only T-edges, retaining their individual incidences.
2. At each protected vertex, replace the vertex by one degree-two vertex per matched pair of incidences.
3. Leave every other vertex except v unsplit.
4. Split v into a separate degree-one terminal for each affected port incidence.

A target loop becomes an edge between two distinct terminals. Other loops retain their two incidences and follow the same rules. Ignore components without a target terminal when recording the boundary partition. Write this partition as

\[
\mathcal P=\{B_1,\ldots,B_c\},\qquad a=\sum_j|B_j|.
\]

Every B_j has even size: all nonterminal degrees in L are even, so each component has an even number of degree-one terminals.

## 2. Exact reachability and construction

**Proposition.** A set S of affected target ports is induced by an auxiliary exchange respecting the supplied protecting matchings if and only if

\[
|S\cap B_j|\equiv0\pmod2\quad\text{for every }j. \tag{1}
\]

There are exactly 2^(a−c) reachable target-port sets, including one when a=0.

**Proof.** An allowed exchange has even degree at every unsplit nontarget vertex. At a protected degree-two vertex it uses both edges or neither. Thus in L its odd-degree vertices are precisely the selected target terminals. The handshaking lemma in each component proves necessity.

Conversely, choose a spanning tree in each component and mark the terminals in S. Process each tree from leaves toward its root, selecting a vertex's parent edge exactly when its subtree contains an odd number of marks. The root has even parity by (1). The selected forest edges have odd degree exactly at the marked terminals. Merging the split vertices back into K gives an even edge subgraph: every protected pair is selected together, and the target has even degree. Swapping t on these edges realizes S. A block of size b has 2^(b−1) even subsets, independently of the other blocks, proving the count. ∎

Components without terminals need contribute no edges. Adding an internal cycle changes a realizing exchange but cannot change its target-port set. For a two-port S, the forest construction selects one path in L; after merging, it is a closed trail in K, potentially visiting an original core vertex more than once. In the cubic rim examples below it is a circuit.

Enumerate the reachable S and apply the regional extension test to the changed boundary. If none escapes, **no even-subgraph exchange with this t and these protecting matchings repairs the target**, including unions of arbitrarily many trails. If one escapes, the constructed exchange fixes the target while preserving every currently good region. Successful rounds strictly decrease the bad-region set; at most its initial size rounds suffice, conditional on finding an escape at every round.

For a target of degree at most eleven, a is even and at most ten, giving at most 512 reachable sets. Given valid protecting matchings, a linear-time construction of the split graph and its spanning forest reduces the problem to these small boundary tests and one realizing forest calculation. This bound excludes the search for protecting matchings. The certificate generator saves a realization of **every** reachable set for verification.

Coarsening a component partition enlarges the reachable family. In particular, leaving an unprotected high-degree vertex unsplit retains more possible exchanges than fixing one arbitrary perfect matching there. The failed universal outside-pairing lemma does not exploit this freedom.

## 3. Complete component partitions of the two witnesses

Represent label i by bit 2^i. The preceding report's two words are

\[
\begin{aligned}
A&=(6,10,6,12,20,6,10,20,18,12,20),\\
B&=(6,6,10,6,24,6,12,18,20,10,18).
\end{aligned}
\]

Here B is a boundary word, distinct from the Petersen four-pole also called B. Both words have eleven marked cuts and junction pattern z=15 everywhere. Neither has label 0 on a target port. For each word, four auxiliary choices affect eight ports and two affect six. There are 379 even partitions of eight labelled ports and 31 of six: 1,578 partitions per word.

The table gives the full result for B. “One pair” means an escaping set of two ports; “two pairs” means the smallest escaping set has four. “Blocked” excludes every admissible subset.

| Auxiliary labels | Partitions | Blocked | Minimum one pair | Minimum two pairs |
|---|---:|---:|---:|---:|
| 12 | 31 | 4 | 27 | 0 |
| 13 | 379 | 7 | 372 | 0 |
| 14 | 379 | 1 | 378 | 0 |
| 23 | 379 | 1 | 377 | 1 |
| 24 | 379 | 1 | 378 | 0 |
| 34 | 31 | 1 | 30 | 0 |

All counts and blocked partitions for both words are saved in the [certificate](core_component_exchange.json). The verifier checks 102,048 admissible subsets across 3,156 partitions, comparing the marked-prefix test with independently reconstructed local junction relations for both constructions.

For B and swap 14, the sole blocked partition is

\[
\{\{0,9\},\{1,2\},\{3,4\},\{5,8\}\}. \tag{2}
\]

Every other even partition admits a two-port escape. Thus if an actual target-bearing component contains at least four ports, a single terminal trail repairs B with swap 14, provided the protecting matchings are valid.

For B and swap 23, the sole fully blocked partition is instead

\[
\{\{0,3\},\{1,2\},\{4,9\},\{5,8\}\}. \tag{3}
\]

For **both A and B**, if the actual partitions for swaps 14 and 23 coincide, at least one swap repairs the boundary. Of the 379 shared partitions, 378 admit a two-port escape; the remaining one needs four ports. This extends the preceding matching observation to arbitrary even component blocks. The hypothesis is equality of the actual partitions, with valid protection for each swap. Equality is not automatic when label-0 edges occur elsewhere in K, or when different protecting matchings split the affected graphs differently.

## 4. A complete family of actual core realizations

Partitions for different swaps cannot necessarily be chosen independently in one core. To test this constraint, take a degree-eleven target and eleven cubic outside vertices indexed 0 through 10. Give stem i the pair r_i from B. If r_i={a,b}, give the two remaining incident edges the pairs {0,a} and {0,b}. Pair outside vertices independently at each auxiliary color. Their four incidence counts are 8, 6, 4, and 4, giving

\[
7!!\,5!!\,3!!\,3!!=105\cdot15\cdot3\cdot3=14\,175
\]

colored pairing choices. Discard choices with parallel rim edges. The remaining **10,812** rims are simple disjoint unions of cycles. These are labelled colored realizations of the fixed boundary, **not** graph isomorphism classes; the rim need not be connected.

**Finite result.** Every realization admits a single-circuit exchange repairing B, using at least two auxiliary-label choices.

| Auxiliary choices admitting a single-circuit repair | Realizations |
|---|---:|
| 2 | 1 |
| 3 | 34 |
| 4 | 427 |
| 5 | 2,874 |
| 6 | 7,476 |
| **Total** | **10,812** |

The constructor follows paths in selected rim colors. The independent verifier constructs each 12-vertex core and projects the binary kernel of its exchange equations onto the target ports: **64,872 kernel projections**. Outside vertices have T-degree zero or two, so each target-bearing component is a path, and a two-port escape gives a core circuit.

The unique realization with only two successful auxiliary choices has rim cycles

\[
(0,9,4,10,3),\qquad(1,2,6),\qquad(5,7,8).
\]

Its colored edges are saved explicitly. Its six terminal partitions are:

| Swap | Terminal pairs | Minimum escaping pairs |
|---|---|---:|
| 12 | (2,6), (7,8), (9,10) | None |
| 13 | (0,4), (1,6), (3,10), (5,7) | 1 |
| 14 | (0,9), (1,2), (3,4), (5,8) | None |
| 23 | (0,3), (1,2), (4,9), (5,8) | None |
| 24 | (0,3), (1,6), (4,10), (5,7) | 1 |
| 34 | (2,6), (7,8), (9,10) | None |

For each “None” row, no union of the available terminal trails repairs the target, as checked against the component-partition audit. Actual cores can therefore force the obstruction for several swaps simultaneously. The census proves they cannot force it for every swap within this specified family.

These rim cores have four-flows: properly color each rim cycle's edges with the three nonzero two-bit values and put the XOR of the two incident values on each stem. Target conservation holds because every rim edge contributes twice. Their cover existence was consequently already covered by the [four-flow criterion](fourflow-quotient-repair.md). The new finite conclusion concerns repair of this supplied rejected boundary by a single auxiliary circuit.

Attach Petersen by a compatible two-edge sum on a stem to obtain examples outside that criterion. For any auxiliary swap, the two cut edges are either both outside T or both in T. In the latter case they are joined inside the attachment: all internal degrees are even and there are only two odd terminals after cutting. Thus the attachment preserves the original target-port partition. Its cubic vertices also preserve path structure. The saved full examples use this attachment on the hardest rim and independently certify that the resulting core has no four-flow.

## 5. Twelve full graph completions

Each row is constructed in both forms. Construction columns give vertices / B-internal pentagon switches.

| Core configuration | Pieces q | Core exchanges | Blowup | SemiBlowup |
|---|---:|---:|---:|---:|
| Two bad eleven-regions, free neighbor | 22 | 1 | 242 / 18 | 198 / 8 |
| Bad eleven-region, protected good neighbor | 22 | 1 | 242 / 20 | 198 / 10 |
| Eleven-region, four core loops | 11 | 1 | 122 / 9 | 100 / 8 |
| Hardest colored rim | 11 | 1 | 132 / 9 | 110 / 9 |
| Hardest rim, no core four-flow | 11 | 1 | 142 / 9 | 120 / 9 |
| Mixed eight/ten/eleven regions, no core four-flow | 80 | 4 | 890 / 68 | 730 / 32 |

**Free neighbor.** Both eleven-regions start bad. For swap 12, the unsplit neighbor puts all six affected target ports in one component: 32 reachable sets, sixteen escaping. Selecting target ports 2 and 7 fixes both regions.

**Protected neighbor.** The second region starts good. A naive swap 13 at target ports 0 and 1 fixes the target but spoils its neighbor. The saved protecting matching at the neighbor is {(1,5),(2,3),(4,7),(6,10)}, inducing target components {(0,3),(1,5),(4,7),(6,10)}. Twelve of their sixteen reachable sets escape. Selecting ports 0 and 3 repairs the target and preserves the neighbor. Every union of protecting pairs is verified.

**Core loops.** Four chords of the selected cycle become loops at its core target. Across the two graphs, twelve saved realizations use at least one target loop. The incidence-based construction and independent equations handle both ends correctly.

**Hardest rim.** Swap 14 first fails on all sixteen reachable masks. Swap 12 then fails on all eight. Swap 13 succeeds at target ports 1 and 6; ten of its sixteen reachable masks escape. The same target partitions and repair survive the Petersen attachment.

**Mixed core.** Four eleven-regions, two eight-regions, and two ten-regions are joined with a Petersen attachment making the core non-four-flow. Four exchanges reduce the number of bad regions as 8 → 6 → 4 → 2 → 0. Later exchanges visit already good eleven-regions, exercising their protection during a sequence of repairs.

The exchanges change cover labels, not flows. Regional extensions retain the whole prescribed layer on H. The [joint Petersen lemma](joint-boundary-completion.md) supplies the displayed internal pentagon switches, at most 2q, without changing any original E₀ flow value. The verifier reconstructs every graph, both contractions, every intermediate flow, and each final five-layer cover. Switch counts are constructive bounds, not minimum distances.

## 6. Verification and the remaining step

The [constructor](core_component_exchange.py) writes the [certificate](core_component_exchange.json). The [independent verifier](verify_core_component_exchange.py) imports neither the constructor nor an earlier verifier. Besides a different partition enumeration, it uses binary edge variables with even-degree equations at core vertices and equality equations for protected port pairs. It computes the kernel and its target-port image independently of the component and spanning-forest construction.

For the twelve graphs it checks **752 explicit reachable-set realizations** across **30 auxiliary attempts**, including **12 attempts with no possible escape** and **14 visits to protected good regions by selected exchanges**. The component audit and 64,872 rim kernel projections are additional checks. Dependency hashes bind the certificate to earlier local data.

Reproduce from the repository root with Python 3 and its standard library:

```bash
python3 -B research/five-cdc-attempt/core_component_exchange.py
python3 -B research/five-cdc-attempt/verify_core_component_exchange.py
```

Two existence questions remain: whether suitable protecting matchings always exist for good eleven-regions, and whether some auxiliary swap with suitable protection always has an escaping reachable set at a bad target. The rim census settles the second for one boundary word and one specified family of outside cubic graphs. It does not cover every rejected eleven-port word or every outside core. The next step is to test or constrain **jointly realizable component partitions across different swaps**, using this oracle instead of a universal statement about arbitrary outside pairings. The general escape/protection reduction established in this work still stops at length ten.

Follow-up: [An actual core can require a neutral auxiliary exchange](actual-core-exchange-obstruction.md) realizes all six blocking partitions simultaneously in a core with no protected neighbors. Every one-step auxiliary exchange fails, but a neutral move followed by a repair succeeds. The exact distance is two and is preserved by compatible covered two-edge insertions; four full graph completions are independently verified.
