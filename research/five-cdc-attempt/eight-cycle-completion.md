# Fixed-layer completion with one eight-cycle region

**5 October 2026.** For both Blowup and SemiBlowup, prescribed-layer completion still reduces exactly to the core when **at most one selected cycle has length eight and all the others have lengths three through seven**. A supplied core cover may need to change, but the prescribed layer on the entire contracted-piece quotient stays fixed.

This answers the first length-eight case left open by the [boundary obstruction](short-cycle-boundary.md). That obstruction to preserving a particular core cover remains valid. The new result proves that a different compatible core cover always works under the stated restriction. Multiple eight-cycle regions, general longer regions, and the general 5-cycle double cover conjecture remain unresolved by this work. No literature novelty is claimed.

Follow-up: [Simultaneous eight-cycle completion](simultaneous-eight-completion.md) removes the restriction to one eight-cycle. Protected port pairings ensure that each chosen closed-trail cover exchange fixes a bad region while preserving all good regions. That later result covers any number of selected cycles of lengths three through eight.

The proof has two parts. An exact formula identifies the forbidden charges at marked positions around a region. If an eight-cycle boundary fails, its prefix values visit all eight auxiliary states. A finite lemma then guarantees that swapping two auxiliary labels along a core circuit makes a prefix repeat, allowing extension. An independent standard-library verifier checks all **1,488** possible failing boundary words, their **11** symmetry classes, and **52,848** outside pairings for the chosen label swaps.

## 1. Statement and the two kinds of change

Use the conventions of the [short-cycle report](short-cycle-boundary.md#1-two-contractions-and-the-extension-question). From a simple cubic graph S and vertex-disjoint selected cycles D, form X by inserting Petersen four-poles using either construction. Contract each inserted four-pole B to obtain H, then contract each selected cycle region to obtain K=S/D. Let E₀ be the full-graph edges retained in H. Core edges E(K) are retained too; loops in K count twice in vertex incidence.

A five-layer CDC means at most five even subgraphs, allowing disconnected or empty layers, with every edge in exactly two distinct layers. Represent the pair of labels on an edge by a five-bit mask from Q, the ten two-element subsets of {0,1,2,3,4}. XOR of incident masks must be zero. Name the prescribed even layer F by label 0.

**Single-eight-cycle theorem.** Suppose at most one selected cycle has length eight and every other selected cycle has length between three and seven. For every even F on H,

\[
\boxed{\quad
F\text{ is a whole layer of a five-layer CDC of }H
\iff
F\cap E(K)\text{ is a whole layer of one on }K.
\quad}
\tag{1}
\]

Starting with any cover witnessing the right side, either it already extends or **one exchange of two auxiliary labels along a circuit of K** produces a cover that does. The exchange preserves label 0 on every core edge.

This exchange chooses a new *cover*. It is not a switch of the given three-bit flow. In particular, if F is a coordinate of a flow on H, every edge value of that flow can stay fixed while the cover is chosen.

**Internal repair consequence.** Given any nowhere-zero three-bit flow f on X and any nonzero coordinate ℓ, core completion of ℓ(f)|E(K) is equivalent to completion after switches confined to the inserted B pieces. If a compatible core cover is supplied, at most **2q internal pentagon switches** suffice, where q is the number of inserted pieces. Every E₀ flow value stays fixed. The final core pairs may differ from the supplied cover's pairs.

This consequence follows by applying (1) to F=ℓ(f)|E₀ and then applying [joint Petersen completion](joint-boundary-completion.md). It restores the same B-only repair bound as for cycles through length seven. The [regional repair theorem](region-joint-repair.md) handles arbitrary lengths by also allowing junction values to change; the present theorem keeps the entire quotient layer and flow fixed.

## 2. An exact formula for the local exclusions

At junction i use the ordered port pairs a,b,c,d, with

\[
r_i=a\oplus b\oplus c\oplus d\in Q,
\qquad L_i=a\oplus b,
\qquad L_{i+1}=c\oplus d=L_i\oplus r_i.
\]

In Blowup, a⊕c and b⊕d must also belong to Q. In SemiBlowup, b=d denotes one shared edge. Encode membership in F by zᵢ=1₀∈a+2·1₀∈b+4·1₀∈c+8·1₀∈d. Let M(r,z) be the possible left charges for this local data.

Write U={1,2,3,4}, whose mask is 30, and let

\[
\mathcal A_p=\{h\subseteq\{0,1,2,3,4\}:|h|\text{ even},\ 1_{0\in h}=p\}.
\]

Each Aₚ has eight members. For every admissible local key, in **both** constructions,

\[
\boxed{\quad
M(r,z)=\mathcal A_{\,1_{0\in a}\oplus1_{0\in b}}
\setminus
\left(
\{U:a,b\in F\}\ \cup\ \{U\oplus r:c,d\in F\}
\right).
\quad}
\tag{2}
\]

Here a,b∈F means both represented edges belong to the prescribed layer; the set is empty if that condition fails. Each excluded value has the required parity when its condition holds.

The necessity is immediate: two pairs both containing 0 cannot XOR to all four auxiliary labels. Apply this on either side of the junction. Sufficiency is a finite local lemma: enumeration of the cubic-vertex label triangles gives exactly these exclusions, with a witness for every remaining charge. The independent verifier rebuilds all **2,160 Blowup** and **600 SemiBlowup** assignments, accounting for all **80** and **40** admissible keys respectively. It checks equality in (2), including completeness of the admissible keys. There are no other local exclusions.

## 3. Marked cuts and a shorter proof of the length threshold

For a compatible closed boundary r₀,…,rₖ₋₁, put

\[
R_0=0,\qquad R_i=\bigoplus_{j<i}r_j,\qquad R_k=0.
\]

The cut just before junction i represents the contracted B between junctions i−1 and i. **Mark this cut** if at least one of its two port pairs consists entirely of F-edges: either c,d at junction i−1 or a,b at junction i. This is determined by F, independently of the auxiliary labels in the core cover. Indices are cyclic.

At a marked cut, the F-parity of a port pair is zero. If p is the initial charge parity, compatibility therefore gives 1₀∈Rᵢ=p at every marked i. In particular U⊕Rᵢ belongs to Aₚ there.

**Marked-cut criterion.** A specified boundary extends with the prescribed F exactly when

\[
\boxed{\quad
\mathcal A_p\setminus
\{U\oplus R_i:i\text{ is marked}\}\ne\varnothing.
\quad}
\tag{3}
\]

Indeed, charge propagation gives Lᵢ=h⊕Rᵢ. The two exclusions in (2) forbid h=U⊕Rᵢ at a marked left side and h=U⊕Rᵢ₊₁ at a marked right side. Taking their union gives exactly (3). Conversely any surviving h gives compatible local witnesses at every junction, which glue at each contracted B vertex.

This yields two useful deductions without the earlier automaton search:

* If a region has **at most seven marked cuts**, every compatible boundary extends, regardless of the region's length.
* If a region of length eight fails, **all eight cuts are marked** and their prefix values are distinct. Every charge parity around the region is therefore zero, p=0, and none of its core ports belongs to F.

In the failing eight-cycle case the prefixes are exactly the eight even subsets of U. Consecutive prefixes differ by an auxiliary pair rᵢ, so the cyclic prefix walk is a Hamiltonian cycle in the graph on these eight states with adjacency x⊕y∈Q and 0∉x⊕y. This is K₈ with the four complementary-state edges removed.

Thus the obstruction at eight is very specific: a cover must give this Hamiltonian boundary walk, and F must mark every position. The old rejected word (12,13,12,14,12,13,12,14), written as pairs of auxiliary label names, is one such walk.

## 4. A boundary lemma for exchanging auxiliary labels

Fix such a Hamiltonian boundary word r and an auxiliary pair t={α,β}. Let Iₜ be the ports whose pair contains exactly one of α,β. Exchanging α and β on such an edge replaces rᵢ by rᵢ⊕t, another valid auxiliary pair.

If the exchange changes just boundary positions i<j, the prefixes Rᵢ₊₁,…,Rⱼ are translated by t; all other prefixes are unchanged. Since the original prefixes occupy all eight states, the new word remains Hamiltonian exactly when

\[
\{R_{i+1},\ldots,R_j\}\oplus t
=\{R_{i+1},\ldots,R_j\}.
\tag{4}
\]

Call such a pair (i,j) **non-escaping** for t.

**Eight-state pairing lemma.** For every Hamiltonian boundary word, there is a t such that |Iₜ|≥4 and there is at most one non-escaping pair in Iₜ. Consequently every perfect matching of Iₜ contains an escaping pair.

Here is the complete finite classification, up to permutation of the four auxiliary labels, cyclic rotation, and reversal. Port indices in the last column start at zero; a dash means no non-escaping pair.

| Boundary pairs in cyclic order | Orbit size | Exchange t | Affected ports | Non-escaping pair |
|---|---:|---|---:|---|
| 12,13,12,14,12,13,12,14 | 48 | 23 | 6 | — |
| 12,13,12,14,12,23,12,24 | 96 | 34 | 4 | — |
| 12,13,12,14,13,23,13,24 | 384 | 34 | 6 | — |
| 12,13,12,14,23,13,23,14 | 192 | 24 | 6 | — |
| 12,13,12,24,12,13,12,24 | 48 | 34 | 4 | — |
| 12,13,12,24,13,12,13,34 | 192 | 14 | 8 | — |
| 12,13,12,24,23,13,23,24 | 96 | 14 | 6 | — |
| 12,13,12,34,12,13,12,34 | 96 | 14 | 8 | — |
| 12,13,14,23,34,14,23,24 | 192 | 23 | 4 | — |
| 12,13,14,24,34,13,23,24 | 48 | 12 | 6 | (1,7) |
| 12,13,24,13,34,24,13,24 | 96 | 23 | 8 | — |

For completeness, fixing R₀=0 leaves only 7!=5,040 orders to examine. Exactly 1,488 have every successive difference, including the closing one, equal to an auxiliary pair. The table's disjoint symmetry orbits cover all 1,488. Each row satisfies the lemma by direct evaluation of (4). A perfect matching has at least two pairs, so it cannot consist solely of the at most one non-escaping pair. This proves the finite lemma.

The constructor enumerates walks by successive allowed steps. The independent verifier instead enumerates all permutations of the seven remaining states and computes the prefixes after each proposed swap directly. It also rebuilds every orbit and checks disjointness and completeness. Across the words it checks **52,848** perfect matchings for the deterministically chosen t. Checking all six choices of t gives respectively 3,4,5,6 forcing choices on 192,432,672,192 words.

## 5. From a boundary pairing to an actual core circuit

Take any core cover with distinguished layer F∩E(K). If it extends through the eight-cycle region, no change is needed. Otherwise choose t={α,β} using the pairing lemma and let v be the corresponding core vertex.

The edges belonging to exactly one of auxiliary layers α,β form an even subgraph T of K: it is their symmetric difference. Split v into one terminal per incident edge of T. The terminal incidences are exactly Iₜ. All other vertices have even degree, so the edges can be decomposed into terminal-to-terminal trails and closed trails. The terminal trails give a perfect matching of Iₜ. A loop at v becomes an edge joining its own two terminals and is included in this argument.

Some matched pair (i,j) escapes by the lemma. Delete closed subtrails from its terminal trail to obtain a simple path. On restoring v, this path becomes a circuit through v with exactly those two incidences. The loop case is a one-edge circuit. Exchange α and β on every edge of this circuit.

Every changed edge still has exactly two labels, and at each circuit vertex the parities of α and β each change twice. All five layers remain even. Label 0 is untouched. At v, precisely rᵢ and rⱼ change by t. The prefix walk now repeats a state, so at most seven states are forbidden in (3). The same fixed regional F therefore extends.

Every other selected region has length at most seven, so its new compatible boundary also extends. Gluing these extensions proves the reverse direction of (1); restriction and summing parity over a contracted region prove the forward direction. □

The proof gives a slightly broader version: the other regions may have **any lengths if each has at most seven marked cuts for the prescribed F**. The cover exchange leaves those marks unchanged, and (3) guarantees extension there. This does not cover two independently obstructed eight-cycle regions: fixing one boundary could change the other, so the argument does not justify iterative repair in that case.

## 6. Explicit completions, including cores without a four-flow

The certificate first revisits the two cubic examples from the short-cycle report. Their initially supplied core covers are rejected while F on H stays fixed. An auxiliary-label exchange along a three-edge core circuit makes them extend. Joint B repair then produces full covers while preserving every original quotient flow value.

Two further examples take a two-edge sum of the same base graph with Petersen, along a bottom rim edge and an edge outside the chosen Petersen pentagon layer. The selected eight-cycle is retained. The core now has no nowhere-zero four-flow: any such flow would have equal nonzero values on the two-edge cut, and restoring the removed Petersen edge would give Petersen a four-flow. The independent verifier restores that graph and exhausts its 64 binary even supports; none of the 4,096 ordered support pairs covers all 15 edges, certifying the impossibility.

These cases therefore fall outside the earlier [four-flow sufficient condition](fourflow-quotient-repair.md). Their compatible initial core covers, fixed quotient layers, initial full flows, changed core covers, B switches, and final full covers are explicit.

| Construction | Full X vertices | H vertices | K vertices | Core has four-flow? | Internal B switches |
|---|---:|---:|---:|---|---:|
| Blowup | 96 | 40 | 9 | Yes | 1 |
| Blowup with Petersen two-edge sum | 106 | 50 | 19 | No | 1 |
| Blowup of an eight-cycle with four opposite chords | 88 | 32 | 1 | Yes | 7 |
| SemiBlowup | 80 | 24 | 9 | Yes | 5 |
| SemiBlowup with Petersen two-edge sum | 90 | 34 | 19 | No | 5 |
| SemiBlowup of an eight-cycle with four opposite chords | 72 | 16 | 1 | Yes | 5 |

The two chorded-cycle examples explicitly check the loop case in the proof: their core is one vertex with four loops, and the cover exchange uses just one loop. Their base has cycle edges i(i+1) modulo eight and chords i(i+4) for i=0,1,2,3. Every regional cut is marked, and the initial chord-pair word is 12,13,12,14 repeated twice around the region.

All listed flow switches are internal pentagons. The auxiliary-label exchange is a change of cover only and is not counted as a flow switch. The counts are constructed bounds, not claims of minimum repair distance. In particular these counts have a different final-core-cover requirement from the four- and five-switch examples in the [linear regional report](linear-region-repair.md#6-revisiting-the-earlier-rejected-eight-cycle-covers).

## 7. Reproduction and remaining question

From this directory:

```bash
python3 -B eight_cycle_completion.py
python3 -B verify_eight_cycle_completion.py
python3 -B verify_joint_boundary_completion.py
```

* [Constructor](eight_cycle_completion.py) and [certificate](eight_cycle_completion.json): local relation digests, the complete eleven-orbit table, all boundary-pairing counts, and six full cubic completions.
* [Independent verifier](verify_eight_cycle_completion.py): imports no constructor or previous verifier. It rebuilds the local relations and boundary lemma, reconstructs every graph from its cubic base, checks the cover exchanges, and verifies every intermediate flow, fixed E₀ value, prescribed quotient layer, and final cover. It also verifies that the two enlarged cores have no four-flow.

The boundary search is a proof over a finite, explicitly exhaustive state space. The reduction from arbitrary core graphs to that finite lemma is the trail-pairing argument above. The general two-pentagon-per-piece bound uses the previously verified joint completion theorem.

The next unresolved step is simultaneous fixed-layer completion for multiple eight-cycle regions, followed by longer regions with at least eight marked cuts. The present result proves that a single eight-cycle region cannot supply the existential counterexample sought at the previous checkpoint.
