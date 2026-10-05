# Fixed-layer completion through length nine

**5 October 2026.** For both Blowup and SemiBlowup, prescribed-layer completion reduces exactly to the core for **any number of selected cycles of lengths three through nine**. The new length-nine cases include regions whose boundary meets the distinguished layer. Protected port pairings still allow a bad boundary to be repaired without spoiling any good boundary.

The finite proof treats all three possible length-nine obstruction types. Independent checks verify **43,632 rejected cases** and **223,840 good cases needing protection**, together with ten full cubic completions through **780 vertices**. Counts are for boundary words together with their normalized marked-position pattern; the same word can occur in different patterns.

The result requires a compatible core cover. It does not establish the general 5-cycle double cover conjecture or completion for longer regions with at least eight marked cuts. No literature novelty is claimed.

## 1. Statement and retained repair bound

Use the conventions of the [simultaneous eight-cycle theorem](simultaneous-eight-completion.md). Form X by either blowup construction on disjoint selected cycles D of a simple cubic base S. Contract the inserted Petersen four-poles B to obtain H, and contract the full selected cycle regions to obtain K=S/D. Let E₀ be the full-graph edges retained in H. Core loops and parallel edges are allowed, with loops counted twice in incidence.

A five-layer CDC means at most five even subgraphs, possibly disconnected or empty, covering every edge exactly twice. Label sets on edges are two-element subsets of {0,1,2,3,4}. Let an even subgraph F of H be the prescribed whole layer 0.

**Nine-cycle completion theorem.** If every selected cycle has length between three and nine, then

\[
\boxed{\quad
F\text{ extends to a five-layer CDC of }H
\iff
F\cap E(K)\text{ extends to a five-layer CDC of }K.
\quad}
\tag{1}
\]

Given a core cover witnessing the right side, at most **b auxiliary-label exchanges on closed trails** make all regional boundaries extend, where b is the initial number of rejected regions. Every exchange fixes a selected bad region and preserves every good one. Label 0 stays fixed on all core edges.

As before, a cover exchange is not a switch of the given flow. For any nowhere-zero three-bit flow f on X and any nonzero coordinate ℓ, core completion of ℓ(f)|E(K) is therefore equivalent to completion after switches confined to the B pieces. At most **2q internal pentagon switches** suffice once the core cover is supplied, where q is the number of pieces. Every E₀ flow value remains fixed. This last step uses [joint Petersen completion](joint-boundary-completion.md).

The theorem also allows additional selected regions of arbitrary length if each has at most seven marked cuts for F. Finding a compatible core cover remains a separate requirement.

## 2. Exactly three new boundary types

Recall the [marked-cut criterion](eight-cycle-completion.md#3-marked-cuts-and-a-shorter-proof-of-the-length-threshold). A cut at a contracted B vertex is marked if at least one of its two port pairs consists entirely of F-edges. For boundary pairs r₀,…,rₖ₋₁, set

\[
R_0=0,\qquad R_i=\bigoplus_{j<i}r_j,\qquad R_k=0.
\]

With U={1,2,3,4}, mask 30, the forbidden initial cover charges are exactly U⊕Rᵢ at the marked positions. All lie in the same eight-element parity class. Consequently a boundary is bad precisely when the marked prefixes occupy all eight states in that class. At most seven marked positions always suffice for extension.

Let xᵢ be the F-parity of the port pair at cut i. Conservation at the contracted B vertex makes this parity the same on its two sides. A marked cut has xᵢ=0, and the distinguished-layer membership of core port i is

\[
1_{0\in r_i}=x_i\oplus x_{i+1}.
\tag{2}
\]

At length nine, a possible obstruction has either nine marked cuts or exactly eight. In the latter case rotate the region so that its sole unmarked cut is cut 0. This gives the complete list:

| Type | Marked cuts | Parity at the unmarked cut | Core ports belonging to F | Prefix condition for rejection |
|---|---|---|---|---|
| A | All nine | — | None | The nine prefixes cover all eight even subsets of U |
| B | 1,…,8 | 0 | None | R₁,…,R₈ are the eight even subsets of U, once each |
| C | 1,…,8 | 1 | Exactly ports 0 and 8 | R₁,…,R₈ are the eight even five-label sets containing 0, once each |

This classification follows directly from (2): all marked parities vanish, so only the unmarked parity can be nonzero. The verifier additionally checks all **19** possible marked-set/parity patterns before rotation: one of type A, nine of type B, and nine of type C. These are the only possibilities satisfying “marked implies parity zero.” Any further restrictions imposed by a particular construction only reduce this set.

For A, exactly one of the nine prefix values is repeated. For B, the unmarked prefix R₀=0 repeats one of the eight marked values. For C, R₀ is in the other parity class and the marked values are all distinct. Thus neither ignoring the unmarked position nor treating every boundary pair as auxiliary would correctly describe all length-nine cases.

The six auxiliary pairs form the alphabet Q* of two-element subsets of U. Types A and B use Q* at all nine ports. Type C uses {01,02,03,04} at ports 0 and 8, and Q* at the seven remaining ports. The XOR of all nine pairs is zero in every case.

### Type C and the previous Hamiltonian words

For a bad type-C word, r₀ and r₈ are distinct pairs containing 0. Their XOR is an auxiliary pair. Replacing these two pairs by their XOR gives the closed eight-letter auxiliary word

\[
r_1,r_2,\ldots,r_7,r_8\oplus r_0,
\]

whose prefixes visit all eight auxiliary states, after translation by r₀. Conversely each of the 1,488 previous Hamiltonian words gives two type-C words by splitting its closing pair αβ into 0α and 0β in the two possible orders. Hence there are exactly **2,976** bad type-C words. The independent verifier obtains the same count by permuting the eight marked prefix states directly.

## 3. The finite escape and protection lemmas

Fix an auxiliary pair t={α,β}. A port is affected when its edge pair contains exactly one of α,β. Exchanging the two labels there replaces rᵢ by rᵢ⊕t. This remains valid when rᵢ contains label 0: the distinguished label itself is unchanged. The number of affected ports is even, so at length nine there are at most eight of them.

**Escape lemma.** For every bad boundary in A, B, or C, some auxiliary t has the following property: every perfect matching of the affected ports contains a pair whose simultaneous exchange makes the boundary good.

To check this exactly, form the graph on affected ports whose edges are the pairs that keep the boundary bad when toggled. The required property is equivalent to this graph having no perfect matching. We check that condition, rather than assuming that the small non-escaping-pair bound used at length eight persists.

**Protection lemma.** For every good boundary in A, B, or C, and every auxiliary t, there is a perfect matching of the affected ports such that toggling any subset of its matched pairs leaves the boundary good.

Here “bad” and “good” always use the specified marked positions. In particular, a type-B word may be good even when the prefixes at all nine positions cover eight states.

### Exhaustive counts

The complete normalized boundary spaces and rejected subsets are:

| Type | Closed boundary cases | Rejected cases | Classes containing a bad case for t=12 | Good cases needing a protection check |
|---|---:|---:|---:|---:|
| A | 1,259,520 | 33,264 | 5,976 | 151,920 |
| B | 1,259,520 | 7,392 | 1,760 | 51,328 |
| C | 559,872 | 2,976 | 852 | 20,592 |
| Total | 3,078,912 | 43,632 | 8,588 | 223,840 |

For fixed t, the classes are defined by the unchanged port pairs and the two-element orbit {rᵢ,rᵢ⊕t} at each affected position, exactly as in the previous protection proof. A class with no bad word needs no search: every matching is protected. The additional automatically safe good-case counts are 1,074,336, 1,200,800, and 536,304 for A, B, and C respectively.

Every one of the 223,840 threatened good cases has at least one protected matching. The certificate records the complete histograms and witness digests. Auxiliary-label symmetry reduces this universal protection check to t=12; it fixes label 0, the marked positions, and the boundary type.

For rejected cases, the number of auxiliary pairs t that force an escape is:

| Forcing choices among the six auxiliary pairs | Type A cases | Type B cases | Type C cases |
|---:|---:|---:|---:|
| 3 | 12,960 | 768 | 384 |
| 4 | 15,120 | 2,304 | 864 |
| 5 | 4,320 | 3,264 | 1,344 |
| 6 | 864 | 1,056 | 384 |

Thus every rejected case has at least three choices. To obtain these counts the constructor uses dynamic programming for perfect matchings. The independent verifier enumerates the outside matchings directly and checks the label symmetries separately.

For completeness, the two implementations enumerate the underlying cases differently. The constructor scans closed auxiliary words for A and B, and constructs C by splitting a Hamiltonian closing pair. The verifier enumerates the repeated prefix state and its positions for A, and permutations of the eight marked states for B and C. It counts all closed words by combining XOR counts of four-position and five-position partial words, independently of the constructor's walk-count recurrence.

Protection is also checked differently. The constructor tests unions of matched pairs against the bad assignments in a class. The verifier requires the matching to cross every dangerous difference cut, then directly rebuilds the marked prefixes for every subset of the chosen matching. No SAT solver or external graph library is used.

These exhaustive checks prove the two finite lemmas for every listed case. The classification in Section 2 proves that no length-nine obstruction type is omitted.

## 4. Simultaneous completion with mixed cycle lengths

The [transition-pairing argument](simultaneous-eight-completion.md#4-a-global-exchange-that-preserves-all-good-regions) now applies to mixtures of lengths eight and nine.

Choose a bad region and a forcing auxiliary pair t. The symmetric difference of the two corresponding core layers is an even subgraph T. At every good region with at least eight marked cuts, pair the T-incidences using its protected matching. Use arbitrary pairings at other core vertices except the target.

Split the target into terminals and follow these pairings. They give a perfect matching of its affected ports by edge-disjoint terminal trails. The escape lemma guarantees an escaping terminal pair. Exchange the auxiliary labels along its trail, after restoring the target vertex.

The resulting closed trail uses each edge at most once. At every visited vertex it changes an even number of incidences, so all cover layers remain even. At a protected region its changed incidences are a union of matched pairs, so that region stays good. Label 0 is preserved on every edge, including type-C distinguished-layer ports.

The target becomes good and no good region becomes bad. The bad-region set therefore strictly decreases. After at most b exchanges, all boundaries extend with the original F by the marked-cut criterion. Gluing the regional covers proves the reverse direction of (1). Restriction to the core proves the forward direction. □

As before, a chosen trail may revisit vertices other than its target. Its length is not bounded independently of the core. With constant finite tables, each cover exchange takes O(|V(K)|+|E(K)|), followed by O(q) work to extend the final boundaries. The actual full-graph flow repairs remain B-internal pentagons.

## 5. Full graph certificates, including a protected type-C region

For each type A, B, and C, the basic core has two vertices joined by nine parallel edges, expanded to two selected nine-cycles in the cubic base. The initial cyclic boundary pair words are:

```text
A and B: 12,12,13,12,14,12,13,12,24
C:       01,12,13,12,14,12,13,12,04.
```

The junction membership words z are respectively all 15; 0 followed by seven 15s and 0; and 14 followed by seven 15s and 11. They realize all nine marks for A and marks 1,…,8 for B and C, in both constructions.

A further type-C example swaps positions 6 and 7 at the second core vertex, making that boundary initially good. Exchanging labels 2 and 3 on the edges at positions 6 and 7 of the first vertex merely moves the obstruction from region 0 to region 1. The protected construction instead exchanges the edges at positions 1 and 2. Both regions then become good. The saved matching at the initially good region is {(1,2),(3,6),(5,7)}, and the chosen exchange uses its first pair. This verifies protection at a nine-cycle whose boundary meets F, not only at a purely auxiliary boundary.

The largest examples connect four two-region cells: one eight-cycle cell and one of each nine-cycle type. They have eight initially bad regions and 70 inserted B pieces. A Petersen two-edge sum makes the core fail the earlier four-flow criterion. Any core four-flow would restore one on Petersen across the two-edge cut; the verifier independently excludes this by checking all 4,096 pairs of Petersen's 64 even supports.

| Example | Initial bad regions | Cover exchanges | Blowup vertices / B pentagons | SemiBlowup vertices / B pentagons |
|---|---:|---:|---:|---:|
| Type A pair | 2 | 1 | 198 / 14 | 162 / 10 |
| Type B pair | 2 | 1 | 198 / 12 | 162 / 12 |
| Type C pair | 2 | 1 | 198 / 14 | 162 / 12 |
| Protected good type-C region | 1 | 1 | 198 / 15 | 162 / 9 |
| Mixed eight/nine regions, no core four-flow | 8 | 4 | 780 / 58 | 640 / 32 |

The last row has bad-region counts 8→6→4→2→0. Every listed flow switch is an internal pentagon, and every quotient edge keeps its original flow value. The final label-0 support on H equals the prescribed F exactly. Counts are constructed bounds, not minimum distances.

## 6. Reproduction and remaining boundary

From this directory:

```bash
python3 -B nine_cycle_completion.py
python3 -B verify_nine_cycle_completion.py
python3 -B verify_simultaneous_eight_completion.py
python3 -B verify_joint_boundary_completion.py
```

* [Constructor](nine_cycle_completion.py) and [certificate](nine_cycle_completion.json): all three finite classifications, protection and escape counts, ten full graph completions, and the unsuccessful unprotected exchange.
* [Independent verifier](verify_nine_cycle_completion.py): imports no constructor or earlier verifier. It rebuilds the length-nine cases and both finite lemmas, reconstructs the full graphs and quotients, and checks every cover exchange, intermediate flow, unchanged quotient value, and final cover.

The earlier eight-cycle and joint-completion theorems supply the unchanged prerequisites for mixed lengths and the two-pentagon repair bound. The new result moves the unresolved threshold to **length ten with at least eight marked cuts**. At that length a rejected boundary can have two unmarked positions or more repeated prefix states; the three cases above do not exhaust those possibilities.
