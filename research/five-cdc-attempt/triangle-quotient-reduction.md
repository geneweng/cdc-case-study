# Triangle quotients preserve the core completion problem

**30 September 2026. The general 5-cycle double cover conjecture remains unproved here.** The quotient case without a four-flow has an exact solution when the selected cycles are triangles: completing a prescribed layer on the quotient is equivalent to completing its restriction on the smaller cubic core. The large triangle regions introduce no additional prescribed-layer obstruction, but they also cannot remove an obstruction on the core.

This gives both a positive result and a limitation of internal repair:

- On the Petersen-core constructions, every starting three-bit flow has at least **four** coordinates repairable using only the Petersen interiors. Any specified remaining coordinate becomes repairable after **one lifted core pentagon switch**. At most 60 further internal pentagons suffice.
- There are explicit 2,376- and 1,944-vertex graphs with five-layer covers and flows whose **seven coordinates all remain impossible under every repair that preserves the original core-edge values**. One switch meeting those edges, followed by internal repairs, escapes. The minimum number of switches meeting core edges is exactly one; this is not a claim that one switch suffices in total.

The finite classification exhausts all 28,560 three-bit flows on Petersen, and separately verifies all 5,760 bad cases for one normalized coordinate have a one-pentagon escape. A general three-terminal lifting lemma proves an exact equality of repair distances when only moves touching core edges are counted.

Follow-up: [Cycle regions through length seven preserve prescribed cover boundaries](short-cycle-boundary.md) extends the completion and internal-repair reduction to selected cycles of lengths three through seven. A specified boundary can first fail at length eight. The circuit-distance theorem is not extended: a square region already supplies a counterexample to preparation-free lifting.

## 1. The construction and the two levels of contraction

Let K be a connected loopless cubic graph. Replace each of its N vertices by a triangle, attaching its three incident edges at distinct triangle vertices. Call the resulting graph S, and let D consist of the N inserted triangles. Apply either Blowup(S,D) or SemiBlowup(S,D) to form X. There are q=3N Petersen four-poles in X.

Contract only those four-poles to obtain H. Then contract each entire triangle region of H to recover K. Edges of K are retained throughout; call them **core edges**. Write E₀ for all edges retained in the first contraction X→H, so E(K)⊂E₀.

| Construction | Vertices of X | Vertices of H | Vertices in one full region of X |
|---|---:|---:|---:|
| Blowup | 33N | 12N | 33 |
| Semiblowup | 27N | 6N | 27 |

Each full region has exactly three edges to the rest of the graph, corresponding to the three edges at one vertex of K. Each region contains three Petersen pieces. The original blowup definitions and port conventions are Hägglund's. [Hägglund, Constructions 1–2](https://arxiv.org/html/1203.2015v1#S2)

The [preceding four-flow theorem](fourflow-quotient-repair.md) says H has a four-flow exactly when K does. The results below also handle K with no four-flow, including Petersen and the earlier 72-vertex core.

## 2. Three-terminal regions with a four-flow cap

**Three-terminal extension lemma.** Let P be a connected region with three ports. Suppose adjoining one new vertex to the three ports gives a graph with a nowhere-zero F₂²-flow. Let F be any local even subgraph of P, including its port memberships. Every five-label cover boundary compatible with those memberships extends through P with layer 0 **exactly F**.

Compatibility means that the three prescribed edge pairs are members of Q={two-element subsets of {0,1,2,3,4}}, XOR to zero, and contain label 0 precisely on the F-ports.

**Proof.** The number of ports in F is even by summed vertex parity, so F extends over the new cap vertex. A four-flow on the capped graph gives three even layers C₁,C₂,C₃ covering every edge twice. As proved in the preceding report,

\[
F,\ C_1\triangle F,\ C_2\triangle F,\ C_3\triangle F
\tag{1}
\]

is a four-layer cover with F distinguished. Add an empty fifth layer.

At a cubic cap vertex the three edge pairs must be the three sides of a triangle on three layer names. If F uses no port, this triangle excludes label 0. If F uses two ports, the triangle includes 0, and those two ports are exactly the pairs incident to 0. In each case permutations of the other four names act transitively on the ordered boundary triangles with those memberships. Relabel the cover while fixing 0 to match the supplied boundary. Removing the cap vertex gives the desired extension without changing F. □

For a triangle region of H, the cap is exactly the quotient obtained from Blowup(K₄,triangle) or SemiBlowup(K₄,triangle). Contracting the selected triangle in K₄ gives two vertices joined by three parallel edges, which have a four-flow with values 1,2,3. Thus the preceding quotient theorem supplies the required capped four-flow.

The certificates make these two small regions explicit:

| Cap type | Vertices | Edges including three cap edges | Local even supports | Supports for each even port pattern | Compatible (support,boundary) states |
|---|---:|---:|---:|---:|---:|
| Blowup | 13 | 21 | 512 | 128 | 7,680 |
| Semiblowup | 7 | 12 | 64 | 16 | 960 |

There are 60 ordered five-label boundary triangles in total: 24 exclude label 0, while each of the three two-port membership patterns has 12. All **8,640 compatible local states** are checked independently. The general lemma rests on the symmetry and four-flow argument, not extrapolation from that check.

## 3. Exact prescribed-layer reduction to the cubic core

Let F be any even subgraph of H and let F_K=F∩E(K). Summing parity in each three-terminal region shows that F_K is even on K.

**Completion theorem.** H has a five-layer CDC containing F as a whole layer if and only if K has a five-layer CDC containing F_K as a whole layer.

**Proof.** A cover on H restricts to a cover on K: summing each label's parity within a region proves evenness at its contracted vertex, and each retained edge keeps exactly two labels. The distinguished layer restricts to F_K.

Conversely, take a cover on K with F_K named label 0. At each vertex its three edge pairs provide a compatible boundary for the actual restriction of F to the corresponding region of H. Apply the three-terminal extension lemma independently in each region. Matching port pairs glue the local covers, preserving every edge pair of the core cover. □

Now start with any nowhere-zero three-bit flow f on X and fix a nonzero functional ℓ. Its restriction f_K to core edges is a nowhere-zero flow on K. Combining this theorem with [joint Petersen completion](joint-boundary-completion.md) gives the exact criterion

\[
\begin{split}
&\ell(f_K)\text{ is a whole layer of a five-layer cover of }K\\
&\quad\Longleftrightarrow\quad
\text{the selected coordinate can be completed on }X
\text{ after switches inside the Petersen pieces.}
\end{split}
\tag{2}
\]

Whenever the left side holds, at most 2q=6N pentagon switches suffice. They preserve every flow value on E₀, not just on the core edges. A supplied core cover is preserved on its edges by the final cover.

If the left side fails, even arbitrary changes elsewhere that preserve all core-edge flow values cannot produce a five-layer cover containing the selected coordinate: restricting such a cover would contradict the failure on K. For obstructions that exclude any number of layers on K, the same stronger nonexistence statement holds on X.

## 4. Core circuit switches lift without preparation

The following flow fact applies to **any** expansion of a loopless cubic graph into disjoint connected three-terminal regions, not just the triangle construction.

**Circuit lifting lemma.** Every valid single circuit switch on the core lifts to a valid single circuit switch on the expanded graph, from any nowhere-zero F₂³-flow restricting to the given core flow. No preparation inside the regions is needed.

**Proof.** Let a≠0 be the increment. At a visited core vertex, the circuit selects two ports whose flow values differ from a. Reduce the flow modulo the one-dimensional subspace ⟨a⟩ and delete internal edges whose original value is a. Every remaining internal component has total boundary value zero in F₂³/⟨a⟩.

Both selected port images are nonzero. They must lie in the same internal component. Otherwise the component containing one selected port has either only that nonzero boundary value, or it also contains the third port. In the second case, their images would have to sum to zero, forcing the other selected port image to be zero by the total three-port equation. Both possibilities are contradictions.

Choose a simple path between the selected ports inside that component. Every edge of this path avoids a. Do this in each visited region and join the paths with the core circuit's edges. Regions are disjoint, so the result is a single circuit avoiding a. Switching it induces exactly the chosen core switch. □

There is a converse for projecting moves. A circuit crosses any three-edge region boundary zero or two times. If it uses core edges, its projection is connected and has degree two at every used core vertex, hence is a single core circuit. Its increment is absent on those core edges. A circuit using no core edge does not change the restricted flow.

Define d_K(f_K,ℓ) to be the minimum number of core circuit switches needed to reach a flow whose ℓ-support has a five-layer completion. Define d_X^core(f,ℓ) to count only switches using at least one core edge in a successful repair on X; other switches have zero cost. Then, for the present triangle constructions,

\[
\boxed{d_X^{\mathrm{core}}(f,\ell)=d_K(f_K,\ell).}
\tag{3}
\]

Projection gives the lower bound. For the upper bound lift an optimal core sequence one move at a time, then use (2) to finish with at most 6N internal pentagons. Equality also holds with value infinity, and when the endpoint is allowed to use any of the seven normals by minimizing both sides over ℓ. This does not assert that a finite core repair always exists.

If the core sequence has d moves, this construction uses at most d+6N moves in total. A core circuit of length r lifts to length at most 33r in the blowup or 27r in the semiblowup, since a simple internal path uses at most the region's vertex count minus one edges. These are upper bounds, not minimum-length claims.

## 5. Complete classification for a Petersen core

Use the standard 15-edge ordering: five outer pentagon edges, five spokes, then the inner star edges. Petersen has 64 binary even supports. The certificate supplies five-layer covers for exactly 57 of them:

| Support type | Count | Five-layer completion as a whole layer |
|---|---:|---|
| Empty | 1 | No |
| A five-cycle | 12 | Yes |
| A six-cycle | 10 | Yes |
| An eight-cycle | 15 | Yes |
| A nine-cycle | 20 | Yes |
| Two disjoint pentagons forming a spanning factor | 6 | No, for any number of layers |

The empty support would leave at most four nonempty layers and hence give a four-flow. The verifier independently exhausts all pairs of binary even supports and finds none whose union is all edges, excluding such a flow.

For a spanning factor, each remaining cover layer must alternate between factor edges and the complementary matching: using both factor edges at a vertex in another layer would leave no partner for either remaining occurrence of the matching edge. The only nonempty alternating layers on Petersen have eight edges. The remaining 20 edge occurrences cannot be a sum of eights. The verifier checks that alternating-layer premise for each of the six factors. This is the earlier structural Petersen obstruction, now combined with a complete set of positive witnesses for all other nonempty supports.

These six factor masks are

```text
8054, 15085, 20395, 26581, 29178, 31775.
```

Their only nonzero binary dependency is the sum of all six. In particular any four are independent. A nowhere-zero three-bit Petersen flow must have rank three, since rank at most two would give a four-flow. Its seven coordinate supports are therefore the seven nonzero vectors of a three-dimensional binary space. Such a space contains at most three factor masks. **At least four coordinates always have a five-layer completion.**

The exhaustive named-flow census is:

| Blocked coordinates | Completable coordinates | Three-bit flows |
|---:|---:|---:|
| 0 | 7 | 5,040 |
| 1 | 6 | 10,080 |
| 2 | 5 | 10,080 |
| 3 | 4 | 3,360 |
| **Total** | | **28,560** |

This counts flows with named values 1,…,7, without dividing by changes of basis. It concerns completing the coordinate after allowing the other flow coordinates to change; it is not the earlier fixed-flow palette-lift census.

For the normalized coordinate ℓ=1, all **5,760** bad flows admit a valid single **pentagon switch** whose new support is among the 57 positive ones. The verifier exhausts these flows, finds and applies the switch, and checks its target against the positive cover list. Changes of basis give the result for every nonzero ℓ. Hence d_K(f_K,ℓ) is exactly zero or one according as that coordinate is already completable or is a factor.

Consequently, on the **330-vertex blowup and 270-vertex semiblowup**, every initial flow has at least four coordinates repairable with at most 60 internal pentagons. Every chosen coordinate, including a blocked one, can be completed in at most **61 total moves**, with exactly one move meeting core edges when it was initially blocked. This theorem applies to every starting flow on either graph, not only the saved examples.

The completion theorem also classifies every even support on H without enumerating its enormous cycle space. The blowup quotient has 120 vertices, 195 edges, and cycle rank 76. Each of the 64 Petersen supports has 2⁷⁰ extensions, so exactly **57·2⁷⁰** quotient supports are completable and **7·2⁷⁰** are not. The semiblowup quotient has 60 vertices, 105 edges, and rank 46; the corresponding counts are **57·2⁴⁰** and **7·2⁴⁰**. Each region contributes respectively seven or four free internal binary coordinates for a fixed port pattern. The extensions whose core restriction is empty cannot be coordinates of a nowhere-zero three-bit flow on H, since that would give a four-flow on the Petersen core.

## 6. All seven coordinates can survive every internal repair

Take K to be the [earlier 72-vertex all-coordinate obstruction](junction-selection-obstruction.md), with its displayed flow f_K. Each of its seven supports violates a local Z–W charge condition and cannot be a whole layer of any CDC, regardless of the number of layers.

The constructor extends this core flow to X. At a core vertex its three flow values are the three nonzero values in a two-dimensional subspace. Map the capped four-flow into that subspace to extend over its triangle quotient region; matching core edges agree. Each Petersen boundary then has a local nowhere-zero three-bit extension, supplied by the previously enumerated complete flow relation.

Every resulting lift of f_K has seven blocked coordinates on X. Any purported completion, after any changes preserving the core-edge values, would restrict to a forbidden core cover. In particular **no finite sequence of internal Petersen switches can succeed, even if the successful normal may be chosen afterward**.

Both graphs nevertheless have explicit five-layer covers. Lift the known core cover through the three-terminal regions and then use the unconditional Petersen cover-boundary extension theorem. This cover need not contain any coordinate of the obstructed starting flow.

| Construction | Vertices | Edges | Verified global escape length | Subsequent internal pentagons |
|---|---:|---:|---:|---:|
| Blowup | 2,376 | 3,564 | 71 | 155 |
| Semiblowup | 1,944 | 2,916 | 41 | 152 |

For the displayed escapes, lift the earlier core's five-edge switch with increment 4. Its normal-4 support has a saved five-layer completion. The three-terminal path argument supplies the lifted circuit directly from the obstructed expanded flow. After that switch, the local extension algorithm completes normal 4 with the internal moves shown. The verifier checks every intermediate flow and the final complete cover. The listed lengths and move counts are constructive bounds, not asserted optima.

The minimum number of switches meeting core edges is **exactly one**: zero cannot remove any of the seven core obstructions, while the displayed sequence uses one such switch and only interior switches thereafter.

The same reasoning applies to every earlier core Gₘ, giving families on **2,376m and 1,944m vertices**. Their displayed core flows block all seven coordinates and have five-layer covers. The [one-global-circuit core repair](global-circuit-repair.md) completes normal 1 on the core. Together with (3), it proves that this normal needs exactly one core-edge-touching switch for all m≥1, with at most 432m additional internal pentagons. The minimum is also one when the successful normal may be chosen. Finite certificates here cover m=1; the infinite statement uses the previously proved core family and the general lifting/reduction arguments.

These expanded examples have **cyclic three-edge cuts** around the full regions; the verifier checks their three-edge boundaries and cycles on both sides. No cyclic-four-edge-connectivity claim is made for the expanded graphs.

## 7. Verification, interpretation, and the remaining problem

The [constructor](triangle_quotient_reduction.py) writes the [certificate](triangle_quotient_reduction.json). The [independent verifier](verify_triangle_quotient_reduction.py) imports neither constructors nor previous verifiers. It uses binary row elimination for local even spaces, reconstructs every compatible boundary orbit, checks Petersen's positive covers and structural obstruction premises, and exhausts all its nowhere-zero three-bit flows and normalized bad-coordinate escapes.

The saved graph cases contain ten initial flows on four graph topologies. All seven normals are classified for each: **44 internal repairs and 26 blocked-coordinate records**, plus the two global escape sequences. Direct checks include full graph topology and both contractions, flow conservation, valid circuit switches, every preserved exterior value, exact prescribed-layer membership, and all edge cover pairs. The 72-vertex core obstructions use the proved Z–W lemma; their premises are rechecked and the prior verifier can be rerun separately.

```bash
python3 research/five-cdc-attempt/triangle_quotient_reduction.py
python3 research/five-cdc-attempt/verify_triangle_quotient_reduction.py
python3 research/five-cdc-attempt/verify_joint_boundary_completion.py
python3 research/five-cdc-attempt/verify_junction_selection_obstruction.py
```

All commands use the standard library. The local two-pentagon theorem remains a finite exhaustive computational ingredient; the three-terminal extension lemma, circuit lifting lemma, exact reductions, and infinite-family deductions have the proofs above. No literature-wide novelty claim is made for these constructions or reduction ideas.

The obstruction is now located precisely: for triangle replacements, internal Petersen repair succeeds exactly when the selected coordinate on the cubic core is completable. Circuit repair at the core remains essential in general. The exact distance reduction transfers that remaining problem rather than solving it for every cubic core; the general 5-cycle double cover conjecture remains unproved here.
