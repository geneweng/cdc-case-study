# Where the universal escape lemma fails: length eleven

**5 October 2026.** The auxiliary-label escape lemma used for simultaneous fixed-layer completion is **sharp at length ten**. An explicit rejected eleven-port boundary has, for each of the six auxiliary-label pairs, an outside pairing for which **every union of paired trails remains rejected**. Allowing several trails at once therefore does not extend this universal local lemma to length eleven.

This is a limitation of the lemma, not a counterexample to completion. The [conditional core reduction remains proved through length ten](ten-cycle-completion.md). Eight full cubic examples realizing the local configurations all have positive completions, including four examples whose cores have no four-flow. The general length-eleven reduction and the general 5-CDC conjecture remain unresolved here. No literature novelty is claimed.

## 1. The quantifiers that fail

Retain the notation of the [length-ten report](ten-cycle-completion.md). Edge pairs use labels {0,1,2,3,4}; F is the prescribed whole layer labelled 0. The auxiliary pairs t use only {1,2,3,4}. Marked cuts specify the forbidden initial charges. A boundary is rejected precisely when its marked prefix states exhaust its eight candidate charges.

For an auxiliary pair t, an affected port contains exactly one label of t. An outside transition system pairs the affected ports by trails. Exchanging t along one trail toggles its two endpoint pairs by XOR with t. A union of trails toggles the union of their endpoint pairs.

The previous escape lemma asserts that, for every rejected boundary, there is a t such that **every** outside pairing has an escaping single trail. A proposed strengthening would replace “single trail” by “union of trails.” The witness below proves

\[
\forall t\quad \exists P_t\quad
\forall J\subseteq P_t:\quad
\text{exchanging }t\text{ at the endpoints of }J
\text{ leaves the boundary rejected}.
\tag{1}
\]

The outside pairing may depend on t. Statement (1) does **not** assert that a particular graph forces these six pairings, or that every possible outside pairing blocks repair. That distinction is essential.

The old lemma holds for all lengths at most ten, so this is also the first possible length at which its union-of-trails version can fail.

## 2. A witness blocking every union

Take eleven marked cuts, all with even F-parity, and the cyclic boundary word

```text
B = 12,12,13,12,34,12,23,14,24,13,14.
```

Here `12` means the label pair {1,2}; port indices run from 0 through 10. In bit masks the word is

```text
6,6,10,6,24,6,12,18,20,10,18.
```

Its XOR is zero. The prefixes before the eleven ports are

```text
0,6,0,10,12,20,18,30,12,24,18.
```

They contain all eight even subsets of the four auxiliary labels, so every candidate charge is forbidden. Setting every junction membership word z to 15 realizes these marked cuts in both Blowup and SemiBlowup.

The following are explicit blocking pairings. Each pair of integers denotes two **port indices**, not labels.

| Auxiliary labels exchanged | One fully blocking outside pairing | Blocking pairings / all pairings |
|---|---|---:|
| 12 | (2,6), (7,8), (9,10) | 3 / 15 |
| 13 | (0,4), (1,3), (5,6), (7,10) | 5 / 105 |
| 14 | (0,9), (1,2), (3,4), (5,8) | 1 / 105 |
| 23 | (0,3), (1,2), (4,9), (5,8) | 1 / 105 |
| 24 | (0,10), (1,7), (3,4), (5,6) | 1 / 105 |
| 34 | (2,6), (7,8), (9,10) | 1 / 15 |

For each displayed pairing, every subset of its three or four pairs remains rejected, including the empty and full subsets. These witnesses prove (1). The certificate also exhausts all other outside pairings and records the minimum number of trails that repairs the boundary, when such a union exists:

| Swap | No union repairs | Minimum one trail | Minimum two trails |
|---|---:|---:|---:|
| 12 | 3 | 12 | 0 |
| 13 | 5 | 100 | 0 |
| 14 | 1 | 104 | 0 |
| 23 | 1 | 103 | 1 |
| 24 | 1 | 104 | 0 |
| 34 | 1 | 14 | 0 |

There are 450 matching cases and 6,960 matching/subset cases for this word. The independent verifier rebuilds both junction tables from cubic vertex constraints, computes surviving charges directly, and checks every case against both tables.

## 3. A weaker failure that two trails do repair

A second rejected boundary illustrates why allowing unions initially appeared promising:

```text
A = 12,13,12,23,24,12,13,24,14,23,24.
```

No auxiliary pair guarantees a single-trail escape against every outside pairing. However, exchanging labels **1 and 4** guarantees escape by a union of at most two trails. Of its 105 outside pairings, 104 have an escaping single trail. The remaining pairing is

\[
P=\{(0,1),(2,4),(5,6),(7,10)\}.
\]

Every single pair in P leaves A rejected, while exchanging the pairs (0,1) and (2,4) together makes it extend. The certificate verifies this against all 105 matchings and every subset. It also checks all five other auxiliary swaps. Across A and B there are **13,920 matching/subset cases**, each checked in both constructions.

The global protection argument itself permits a union of edge-disjoint terminal trails: at every protected good region, the changed incidences still form a union of its matched pairs. The obstruction is the missing universal escape premise. Witness B shows that the premise cannot be recovered merely by increasing the permitted number of trails.

## 4. Legal pairings versus a forced global obstruction

The full examples start with two selected eleven-cycles joined by a matching in a simple cubic base. Their core consists of two vertices joined by eleven parallel edges. Put the same word A or B around both vertices and prescribe z=15 at every junction.

Every pairing in the table is a legal transition choice at the second core vertex. Following those transitions gives the corresponding target-terminal pairing. For B, all six blocking choices are saved on the same core, and every subset of their trails keeps both regions bad.

These transition choices are not forced. For B, exchanging labels 1 and 2 at ports **2 and 7** repairs both regions. The successful outside matching is {(2,7),(6,8),(9,10)}, which differs from the blocking row for that swap. For A, the saved transition system instead exercises the two-trail repair from Section 3.

A further compatibility check explains why the local witnesses alone do not produce a global impossibility. In a core using only auxiliary edge pairs, complementary swaps 14 and 23 have the same affected-edge subgraph. B's unique fully blocking pairings for those swaps are different. Thus for any **shared** terminal pairing in that subgraph, at least one of the two swaps admits an escaping union. This observation applies to the all-auxiliary core, not to arbitrary cores having label-0 edges elsewhere.

Four additional examples attach Petersen by a two-edge sum on a non-F core edge. Their cores have no four-flow, independently certified by restoring Petersen across the cut and excluding all pairs of its even supports. The same boundary pairings and repairs still work. One two-trail repair uses a trail passing through the Petersen attachment.

| Boundary and core | Selected trails | Blowup vertices / B pentagons | SemiBlowup vertices / B pentagons |
|---|---:|---:|---:|
| A, two-vertex core | 2 | 242 / 18 | 198 / 6 |
| A, no core four-flow | 2 | 252 / 18 | 208 / 6 |
| B, two-vertex core | 1 | 242 / 18 | 198 / 8 |
| B, no core four-flow | 1 | 252 / 18 | 208 / 8 |

All eight graphs have 22 inserted Petersen pieces. The final covers retain the prescribed whole layer on H. Every actual flow switch is a B-internal pentagon, and every original E₀ flow value stays fixed. The cover exchanges themselves change labels, not flow values. The displayed switch counts are constructive bounds, not minimum distances.

The independent verifier reconstructs every cubic graph, both contractions, and all saved terminal trails. It checks edge-disjointness, conservation, every blocked union, every successful repair, all intermediate flows, and the final five-layer covers. Thus these are positive completion examples demonstrating a limitation of the proof method.

## 5. Classification and what remains open

At length eleven, a possibly rejected boundary has at least eight marked cuts, so there are at most three unmarked positions. Each unmarked position can have F-parity 0 or 1. There are

\[
\sum_{j=0}^{3}\binom{11}{j}2^j
=1+22+220+1320
=1563
\]

labelled marked/parity patterns. Rotation and reflection reduce them to **88 classes**: 1, 2, 15, and 70 classes with respectively zero, one, two, and three unmarked cuts. The constructor records all classes and orbit sizes; the verifier independently partitions the labelled patterns. This is a classification of possible patterns, **not** an exhaustive verification of escape or protection for all length-eleven words. Both counterexamples already lie in the all-marked class.

The current proven completion range remains **three through ten**, with arbitrary longer regions allowed when they have at most seven marked cuts. Extending it through eleven needs an argument that uses more information than a bad region's boundary and an arbitrary outside pairing. Possible directions are choosing outside transitions using the actual core, coordinating different auxiliary swaps, or allowing intermediate covers that do not decrease the number of bad regions. Whether the protection lemma alone persists at length eleven is also unresolved here.

## 6. Reproduction

From this directory, using Python 3 and its standard library:

```bash
python3 -B eleven_cycle_obstruction.py
python3 -B verify_eleven_cycle_obstruction.py
```

The [constructor](eleven_cycle_obstruction.py) writes the [certificate](eleven_cycle_obstruction.json). The [independent verifier](verify_eleven_cycle_obstruction.py) imports no constructor or earlier verifier. It checks the finite negative result and all eight positive graph completions. Earlier [length-ten](ten-cycle-completion.md) and [joint Petersen](joint-boundary-completion.md) results supply the sharpness comparison and the unchanged local flow-repair step.

Follow-up: [Exact auxiliary exchanges from core connected components](core-component-exchange.md) replaces arbitrary outside pairings by an exact reachability test for the actual core and supplied protecting transitions. It classifies all even component partitions for A and B, proves a finite single-circuit repair result for all 10,812 simple colored rim realizations of B, and verifies twelve further full completions. The general length-eleven existence questions remain open.
