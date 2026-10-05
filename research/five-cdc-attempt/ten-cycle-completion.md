# Fixed-layer completion through length ten

**5 October 2026.** For both Blowup and SemiBlowup, prescribed-layer completion reduces exactly to the core for **any number of selected cycles of lengths three through ten**. Length ten has eighteen marked/parity patterns up to rotation and reflection. The escape and protection lemmas hold for all of them, including boundaries with four distinguished-layer ports.

Two independent exhaustive implementations agree on **82,397,184 normalized closed boundary cases**, including **1,020,960 rejected cases** and **5,173,584 good cases needing protection**. Eight full cubic certificates reach **824 vertices**. These are counts of words together with a normalized pattern; they are not counts of graphs or distinct words across patterns.

This remains conditional on a compatible core cover. It does not prove the general 5-cycle double cover conjecture. No literature novelty is claimed.

## 1. The theorem and flow repair bound

Use the conventions of the [length-nine theorem](nine-cycle-completion.md). Let X be either Blowup(S,D) or SemiBlowup(S,D), for a simple cubic base S and vertex-disjoint selected cycles D. Contract each inserted Petersen four-pole B to obtain H, then contract each whole selected region to obtain K=S/D. Let E₀ be the edges of X retained in H. Core loops and parallel edges are allowed; a loop contributes two incidences.

A five-layer CDC consists of at most five even subgraphs, possibly disconnected or empty, covering every edge exactly twice. Its edge labels are two-element subsets of {0,1,2,3,4}. Let F be an even subgraph of H prescribed as the whole layer labelled 0.

**Ten-cycle completion theorem.** If all selected cycle lengths lie between three and ten, then

\[
\boxed{
F\text{ extends to a five-layer CDC of }H
\iff
F\cap E(K)\text{ extends to a five-layer CDC of }K.
}
\tag{1}
\]

Given a core cover on the right, at most b auxiliary-label exchanges on closed trails suffice to make all regional boundaries extend, where b is the initial number of rejected regions. Each exchange fixes a bad region, keeps every good region good, and preserves label 0 on every core edge. Additional selected regions of arbitrary length are allowed if each has at most seven marked cuts.

For a supplied nowhere-zero three-bit flow f on X and a nonzero coordinate ℓ, a compatible cover of ℓ(f)|E(K) therefore gives completion after at most **2q B-internal pentagon switches**, where q is the number of inserted B pieces. Every flow value on E₀ stays fixed. This follows from the unchanged [joint Petersen completion theorem](joint-boundary-completion.md). The preceding exchanges choose a compatible cover; they do not switch f.

## 2. All length-ten marked/parity patterns

At cut i, let xᵢ be the F-parity of either port pair of the contracted B vertex. A cut is marked when one of its port pairs consists entirely of F-edges, so marked implies xᵢ=0. Write M for the marked positions. If rᵢ is the core edge pair at port i, then

\[
1_{0\in r_i}=x_i\oplus x_{i+1},\qquad
R_0=0,\qquad R_i=\bigoplus_{j<i}r_j,\qquad R_{10}=0.
\tag{2}
\]

The [marked-cut criterion](eight-cycle-completion.md#3-marked-cuts-and-a-shorter-proof-of-the-length-threshold) forbids precisely the initial charges U⊕Rᵢ for i∈M, where U={1,2,3,4}. They lie in the same eight-element parity class. A boundary fails to extend exactly when the marked prefixes occupy all eight states. At most seven marked cuts always allow extension.

A possible obstruction at length ten therefore has zero, one, or two unmarked positions. Up to rotation and reflection, the complete list is:

* No unmarked cut: all xᵢ=0, one pattern.
* One unmarked cut: put it at 0, and choose x₀=0 or 1, two patterns.
* Two unmarked cuts: put them at 0 and d, where 1≤d≤5. Their parities are 00, 10, or 11. Reflection exchanges the two cuts, so 01 is equivalent to 10. This gives fifteen patterns.

There are **18 patterns** in total. Before symmetry reduction there are 1+10·2+45·4=**201** labelled patterns. The verifier independently enumerates all 201 and checks their eighteen dihedral classes. Some patterns may have additional realizability restrictions in an individual construction; proving the lemmas for this larger list covers every realizable boundary.

For each pattern, (2) fixes whether a port uses an auxiliary pair from Q*={{1,2},{1,3},{1,4},{2,3},{2,4},{3,4}} or a pair containing 0. We exhaust every such word whose XOR is zero. There can be zero, two, or four distinguished-layer ports. In the adjacent two-unmarked case with parity 11, there are only two, because the edge joining those cuts has parity zero.

## 3. Finite escape and protection proofs

For an auxiliary pair t={α,β}, a port is affected when its pair contains exactly one of α,β. Swapping these labels replaces rᵢ by rᵢ⊕t. It preserves label 0 and the boundary pattern. There are an even number of affected ports, now possibly **ten**. All 945 perfect matchings are included when all ten are affected.

**Escape lemma.** Every rejected boundary has an auxiliary pair t such that every perfect matching of the affected ports includes a pair whose simultaneous exchange makes the boundary extend.

Equivalently, the graph of port pairs whose exchanges leave the boundary rejected has no perfect matching, for at least one t. Both implementations check all six t. Unlike length nine, a boundary can now have only **one** such choice.

**Protection lemma.** For every extending boundary and every auxiliary t, some perfect matching of the affected ports has the property that exchanging any subset of its matched pairs keeps the boundary extending.

The protection check fixes t={1,2}. Permutations of the four auxiliary labels reduce every other t to this case while fixing label 0, the marked positions, and the cut parities.

Partition words into orbits obtained by independently exchanging t at affected positions, retaining only closed assignments. An orbit containing no rejected assignment is automatically safe. In a threatened orbit, a matching is protected at assignment s precisely when its toggle subspace translated by s contains no rejected assignment. This includes every union of matched pairs, not just single-pair exchanges.

### Exhaustive counts

In the table, Uₘ denotes the **unmarked positions**, and O denotes those positions with xᵢ=1. This Uₘ is distinct from the auxiliary label set U above.

| Uₘ | O | Rejected cases | Good cases needing protection |
|---|---|---:|---:|
| ∅ | ∅ | 452,160 | 1,547,520 |
| {0} | ∅ | 176,256 | 874,656 |
| {0} | {0} | 72,480 | 360,272 |
| {0,1} | ∅ | 47,424 | 328,896 |
| {0,1} | {0} | 20,736 | 142,912 |
| {0,1} | {0,1} | 20,736 | 142,912 |
| {0,2} | ∅ | 35,328 | 269,312 |
| {0,2} | {0} | 14,784 | 111,648 |
| {0,2} | {0,2} | 5,952 | 44,928 |
| {0,3} | ∅ | 37,056 | 293,504 |
| {0,3} | {0} | 14,784 | 114,368 |
| {0,3} | {0,3} | 5,952 | 45,488 |
| {0,4} | ∅ | 37,056 | 284,736 |
| {0,4} | {0} | 14,784 | 112,928 |
| {0,4} | {0,4} | 5,952 | 45,344 |
| {0,5} | ∅ | 38,784 | 294,464 |
| {0,5} | {0} | 14,784 | 114,144 |
| {0,5} | {0,5} | 5,952 | 45,552 |
| **Total** | | **1,020,960** | **5,173,584** |

A pattern with zero, two, or four distinguished-layer ports has respectively 7,558,656, 3,359,232, or 1,492,992 closed words. Across the eighteen patterns there are 82,397,184 closed cases and 145,296 threatened swap orbits. Every rejected case satisfies escape, and every threatened good case satisfies protection. The remaining good cases belong to automatically safe orbits.

For the all-marked pattern, the numbers of rejected words having respectively one through six forcing choices are

```text
8,160; 111,600; 233,760; 86,160; 11,040; 1,440.
```

The certificate contains the complete forcing histograms for every pattern. Thus the stronger lower bound of three choices at length nine does not extend to length ten, although existence of a choice does.

### Independence of the computations

The constructor enumerates canonical fixed-t swap orbits. It checks protection by covering all good assignments with bad-free matching cosets, and checks escape with recursive perfect-matching search.

The independent verifier enumerates actual pair words, forces the closing letter by XOR, and tests rejection by deleting forbidden charges from the eight candidates. It groups the rejected words afterwards. For a good assignment s, each rejected assignment b defines a dangerous cut s⊕b in the affected ports. A matching avoids that rejection exactly when some matched pair crosses this cut. The verifier independently searches for a matching crossing every dangerous cut. For escape it builds all matchable vertex subsets by adding allowed pairs, rather than using the constructor's recursion.

The Python verifier additionally checks all 201 marked/parity patterns and independently counts swap orbits and their closed assignments by an XOR recurrence. Both C++ programs use integer arithmetic and the standard library; no SAT solver or external graph library is involved. Their complete counts and forcing histograms agree. This proves the two finite lemmas for the exhaustive list in Section 2.

## 4. Applying the lemmas simultaneously

The [protected-trail argument](simultaneous-eight-completion.md#4-a-global-exchange-that-preserves-all-good-regions) works unchanged with the new finite lemmas.

Select a bad target and a forcing pair t. The symmetric difference T of the two auxiliary cover layers is an even subgraph of K. At every currently good region with at least eight marked cuts, pair its T-incidences using a protected matching. Use arbitrary pairings at other vertices, except that the target's incidences remain terminals.

Following the paired incidences matches the target terminals by edge-disjoint trails. The escape lemma supplies a terminal pair whose trail fixes the target. After restoring the target vertex, swap the two auxiliary labels along this closed trail. The trail uses each edge once at most. Every vertex sees an even number of changed incidences, so every layer remains even. At a protected region the changed incidences form a union of matched pairs, so its boundary remains good.

The target becomes good and no good region becomes bad. Repeat at most b times, then extend every region using its surviving charge. The earlier lemmas cover lengths eight and nine; at most seven marked cuts require no protection. This proves the reverse implication in (1). Restriction to the core proves the forward implication. □

As before, a trail may revisit vertices other than the target. Its length can depend on the core size. With finite lookup tables, each exchange takes O(|V(K)|+|E(K)|); extending the final regional boundaries and repairing the B pieces takes O(q). The actual flow switches remain internal pentagons.

## 5. Full graph certificates

The first example uses two ten-cycle regions with all cuts marked and boundary word

```text
12,12,13,12,14,12,12,13,12,14.
```

Its only forcing auxiliary pair is **34**, independently checked against all outside port matchings. Exchanging it at ports 2 and 4 repairs both regions in the displayed two-vertex core.

The second example has unmarked cuts 0 and 5, both with odd F-parity, and word

```text
01,12,13,12,01,04,12,13,12,04.
```

Its four distinguished-layer ports are 0, 4, 5, and 9. The junction membership word is (14,15,15,15,11) repeated twice, realizing the pattern in both constructions.

For the protection example, swap ports 0 and 5 at the second core vertex. Its boundary becomes initially good. An unprotected exchange of labels 1 and 4 at the first vertex's ports 0 and 5 merely moves the obstruction from region 0 to region 1. The protected exchange instead swaps labels 2 and 3 at ports 1 and 2. The saved matching at the good region is {(1,2),(3,6),(7,8)}. Both regions then extend.

The largest examples join four two-region cells: length eight, the odd-unmarked length-nine pattern, and the two length-ten examples above. A Petersen two-edge sum gives a core with no four-flow. All eight regions are initially bad; four exchanges reduce the bad-region counts 8→6→4→2→0. There are 74 inserted B pieces and 18 core vertices.

| Example | Initial bad regions | Cover exchanges | Blowup vertices / B pentagons | SemiBlowup vertices / B pentagons |
|---|---:|---:|---:|---:|
| Only one forcing auxiliary pair | 2 | 1 | 220 / 16 | 180 / 8 |
| Four distinguished-layer ports | 2 | 1 | 220 / 16 | 180 / 12 |
| Protected good four-port region | 1 | 1 | 220 / 16 | 180 / 11 |
| Mixed eight/nine/ten, no core four-flow | 8 | 4 | 824 / 60 | 676 / 32 |

The independent verifier reconstructs each graph, H and K; checks every cover exchange and protected matching; and verifies every intermediate nowhere-zero flow, final cover, and unchanged E₀ value. It also restores Petersen across the two-edge cut and excludes a four-flow by enumerating pairs of its even supports. Counts of switches are constructed bounds, not minimum distances.

## 6. Reproduction and the next boundary

From this directory, with Python 3 and a C++17 compiler available:

```bash
python3 -B ten_cycle_completion.py
python3 -B verify_ten_cycle_completion.py
```

Each command compiles its own boundary program in a temporary directory. Set CXX to an alternate compiler executable if needed. The constructor writes [ten_cycle_completion.json](ten_cycle_completion.json). Its [Python source](ten_cycle_completion.py) uses the [orbit enumeration](ten_cycle_boundary.cpp); the [independent Python verifier](verify_ten_cycle_completion.py) uses a [separate closed-word enumeration](verify_ten_cycle_boundary.cpp). The certificate records hashes of its unchanged earlier certificate dependencies.

The earlier length-nine and joint-completion proofs remain prerequisites. They can be rerun with `verify_nine_cycle_completion.py` and `verify_joint_boundary_completion.py` respectively.

The next unresolved threshold is **length eleven with at least eight marked cuts**. Such a region may have three unmarked positions; the eighteen patterns above do not exhaust its possible boundaries. The compatible core-cover requirement also remains unresolved in general.
