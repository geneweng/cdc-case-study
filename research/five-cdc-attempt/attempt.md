# Attempt to prove the 5-cycle double cover conjecture

**Date: 29 September 2026. Outcome: the general conjecture remains unproved in this attempt.**

I found no verified general resolution. A September 23 primary preprint explicitly still calls it open. Here, five means **five even subgraphs**, each possibly containing several circuit components. [Zerafa, arXiv:2609.28118](https://arxiv.org/abs/2609.28118)

This attempt produced an exact algebraic reformulation, three rejected proof shortcuts with certificates, and a more specific unproved repair lemma. The elementary derivations below are supplied here without a claim of research novelty. Finite computations are distinguished from statements proved for arbitrary graphs.

**Latest status:** the candidate repair lemma below is now **refuted** by an explicit 16-vertex graph. See [the counterexample and triangle reduction](repair-obstruction.md). The original 5-CDC conjecture remains unproved by this work. The [earlier continuation](continuation.md) records exhaustive positive checks through 14 vertices and on two 18-vertex snarks, plus an exact alternating-form formulation and a linear third-coordinate completion criterion; those algebraic equivalences remain valid.

## 1. An exact reformulation: one extra binary flow coordinate

The five-label restriction in the earlier report can be expressed with an especially small linear system. Its component criterion agrees with Hušek–Šámal's fixed-flow criterion; the derivation below uses a different set of coordinates and proves the cover correspondence directly. [Hušek–Šámal, §3.4](https://arxiv.org/html/2607.24724v1)

### Proposition 1: five even layers are equivalent to a flow avoiding five vectors

Represent vectors of F₂⁴ by integers 0–15, with addition given by XOR. Put

\[
C=\{c_0,c_1,c_2,c_3,c_4\}=\{4,5,6,15,8\}.
\]

These five vectors span F₂⁴ and their only nonzero linear dependency is

\[
c_0+c_1+c_2+c_3+c_4=0.
\]

Their ten pairwise sums are distinct and are exactly

\[
A=\mathbb F_2^4\setminus(\{0\}\cup C)
=\{1,2,3,7,9,10,11,12,13,14\}.
\]

**Claim.** A finite loopless graph has a five-layer CDC if and only if it has an F₂⁴-flow whose edge values all belong to A.

**Proof, cover to flow.** Give the layers indices 0,…,4. If e is in layers i and j, assign it c_i+c_j. Each layer has even degree at every vertex, so the assigned vectors sum to zero there. They are all in A.

**Proof, flow to cover.** Each edge value uniquely determines a pair {i,j}. Include the edge in those two layers. At a vertex, let d_i be the parity of the number of incident edges assigned to layer i. Conservation says ∑d_i c_i=0. Hence either every d_i=0 or every d_i=1. But every incident edge contributes two layer incidences, so ∑d_i=0; five ones would instead sum to one. Thus every layer is even. Each edge is in exactly two layers by construction. □

This is an exact encoding. It does not prove that an A-valued flow always exists.

### Proposition 2: for a fixed binary 3-flow, lifting is linear

Start with a nowhere-zero f:E→F₂³. Write the desired four-bit flow as

\[
h_e=f_e+8z_e,\qquad z_e\in\mathbb F_2,
\]

where the notation means appending a new binary coordinate. The lift avoids C exactly under these restrictions:

| Three-bit value f_e | Required z_e |
|---|---|
| 1, 2, 3 | Free |
| 4, 5, 6 | 1 |
| 7 | 0 |

The lower three coordinates already satisfy conservation. The remaining requirement is simply

\[
Bz=0\quad\text{over }\mathbb F_2,
\tag{1}
\]

with the table's prescribed coordinates, where B is the binary vertex-edge incidence matrix. Any solution decodes to a five-layer CDC by Proposition 1.

Conversely, the construction in Proposition 1 projects to a nowhere-zero three-bit flow: the projections of the five c_i are the distinct vectors 4,5,6,7,0. Thus **some starting flow admits this lift if and only if the graph has a five-layer CDC**.

The missing step is now explicit: choose f so that (1), with its prescribed coordinates, is consistent.

A tempting choice, making z a linear combination of the three existing coordinates, cannot work whenever f uses all seven nonzero values. On {4,5,6,7}, a linear functional has an even number of ones, while the required values (1,1,1,0) have odd parity. An additional cycle-space direction is needed in that situation.

## 2. The obstruction can be read on cuts

Put F={e:f_e∈{4,5,6,7}} and H=(V,E∖F). Prescribe z on F using the table. The remaining incidence equations on H are solvable exactly when, for every component K of H, the sum of the prescribed bits across δ(K) is zero. This follows from the standard characterization of the image of a binary incidence matrix: even total demand in each connected component.

All edges of δ(K) have values in {4,5,6,7}. Let n_a be the parity of the number with value a. Flow conservation summed over K gives

\[
n_4=n_5=n_6=n_7.
\]

The prescribed boundary sum is n_4+n_5+n_6, so it is precisely that common parity.

**Therefore a component is an obstruction exactly when all four boundary color counts are odd.** This is a four-color cut obstruction, not merely an arbitrary failed matrix equation.

The same description works for any nonzero linear functional ℓ on F₂³: remove the edges with ℓ(f_e)=1, and inspect the four values in the affine plane ℓ=1. There are seven choices of ℓ.

### Why seven tests cover all five-element label palettes

Every five-element subset S of F₂³ contains a unique four-element affine plane. To see this, its three-element complement {a,b,c} extends to the plane {a,b,c,a+b+c}; the complementary plane lies in S. Uniqueness follows because an affine plane's four vectors sum to zero, so its omitted point in S must be the sum of all five vectors of S.

Translating all cover labels leaves the edge flow unchanged. Translation makes that four-element plane linear, and translations within it move the fifth label anywhere in the other coset. Thus the 56 five-element palettes fall into seven translation classes, one for each ℓ.

For a cubic graph, the symmetric pair-label lift also recovers every labeled cover inducing f: the three layer labels at a vertex are distinct; their sum determines t_v, and their pairwise sums are the three incident flow values. Hence the seven tests examine every possible five-label lift of that fixed flow.

## 3. First attempted proof: relabel every input flow

**Proposed shortcut:** every nowhere-zero F₂³-flow has a compatible lift using some five labels.

**Result: false, already on the cube.**

Here is an explicit cube and flow, using integer-encoded binary vectors:

| Edge | f_e | Edge | f_e |
|---|---:|---|---:|
| 0–1 | 2 | 2–6 | 4 |
| 0–3 | 7 | 3–5 | 6 |
| 0–4 | 5 | 4–5 | 1 |
| 1–2 | 5 | 4–7 | 4 |
| 1–7 | 7 | 5–6 | 7 |
| 2–3 | 1 | 6–7 | 3 |

Every vertex has three nonzero incident values with XOR zero. The ordinary alignment system has 36 variables, 36 scalar equations, rank 33, and eight solutions. One solution uses the six labels {0,1,3,4,6,7}. All eight solutions are its global translations, so all use six labels. Independently, the seven extra-coordinate systems in Section 1 are all inconsistent.

The matrix and parity checks are reproducible from [cube_certificate.json](cube_certificate.json). The ordinary cube is 3-edge-colorable and therefore has a three-layer CDC. The failure concerns this particular flow, and proves that changing only the palette or the compatible translations is insufficient.

## 4. Second attempted proof: repair the flow while keeping F fixed

**Proposed shortcut:** for any first-coordinate support F that occurs in a nowhere-zero three-bit flow, adjust the other two coordinates until the obstructions disappear.

**Result: false on the Petersen graph.** There is also a short structural proof of the failure.

The first-coordinate support F becomes the fifth layer in Proposition 1: exactly the pairs involving c_4 project to values 4,5,6,7. Thus preserving F asks for a five-layer CDC containing that particular even subgraph as an entire layer.

Take F to be any spanning 2-factor of the Petersen graph; it consists of two pentagons, and its complement M is a perfect matching. Suppose a five-layer cover contains F.

At a vertex, any other active layer must use one edge of F and the matching edge. It cannot use both F-edges: they would then have reached their required multiplicity, leaving no second incident edge to accompany either remaining occurrence of the matching edge. Consequently every circuit in each other layer alternates between F and M and has even length.

The Petersen graph has girth five, so each nonempty other layer has at least six edges. All four other layers must be nonempty: otherwise this would be a four-layer CDC, which on a cubic graph implies 3-edge-colorability, impossible for Petersen. Yet their total number of edge occurrences is

\[
2|E|-|F|=30-10=20,
\]

whereas four nonempty layers would require at least 4×6=24. Contradiction. □

The four-layer/3-edge-coloring equivalence is recorded in [Oum, Theorem 19](https://arxiv.org/abs/2607.16356v3). The argument above explains this particular obstruction without relying on a search.

As a separate check, I enumerated all 8⁶=262,144 binary 3-flows on the Petersen graph, including those with zero edges. Exactly 28,560 are nowhere-zero. Among the 63 occurring first-coordinate supports, exactly six admit no successful lift for any choice of the remaining coordinates; they are the six spanning 2-factors. All 28,560 flows were also checked against the independent extra-coordinate formulation, which succeeded for the canonical coordinate on 4,560 flows. [Full results](petersen_exhaustive.json)

This failure does not refute the prescribed-single-circuit strong CDC conjecture: two disjoint pentagons required as one entire layer impose a different requirement.

## 5. Third attempted proof: strictly reduce the obstruction count

For a flow f and nonzero ℓ, let D_ℓ(f) be the number of obstructed components from Section 2, and put

\[
D(f)=\min_{\ell\ne0}D_\ell(f).
\]

Each D_ℓ is even, because summing its component parities counts the relevant marked edge endpoints twice. A five-label lift exists for f exactly when D(f)=0.

An allowed move chooses a circuit Q and a nonzero a absent from its edge values, then replaces f_e by f_e+a on Q. Conservation and nowhere-zero values are preserved.

**Proposed shortcut:** whenever D(f)>0, some allowed move strictly reduces D.

**Result: false.** On a 14-vertex cubic graph, I found

\[
(D_1,\ldots,D_7)=(4,4,4,2,4,4,2).
\]

The graph has 116 circuits. Exhausting every allowed circuit/value pair gives 123 distinct neighboring flows. Every neighbor still has minimum defect at least two. Thus a proof based on strict descent of D alone fails.

A neutral first move does escape: the saved two-move path reaches D=0, and the extra-coordinate solver then constructs and verifies five even layers covering every edge exactly twice. The complete graph, initial flow, neighborhood summary, moves, and final cover are in [descent_trap_certificate.json](descent_trap_certificate.json).

## 6. A more precise repair target, subsequently refuted

A stronger potential handles that particular plateau:

\[
\Psi(f)=\left(\min_\ell D_\ell(f),\ \sum_\ell D_\ell(f)\right),
\]

ordered lexicographically. A move can preserve the minimum while decreasing the second entry.

**Candidate repair lemma (now refuted).** For every connected bridgeless cubic graph and every nowhere-zero F₂³-flow f with D(f)>0, there is an allowed circuit move that strictly decreases Ψ(f).

If this lemma were true, the existing nowhere-zero 8-flow theorem would supply a starting flow. Repeated improvement must terminate because Ψ takes finitely many nonnegative integer values. The terminal flow would have D=0, and Sections 1–2 would construct a five-layer cover. Combined with the standard cubic reduction for five-layer CDC, this would prove the conjecture.

**What I established:** in 4,800 sampled flow instances with D>0 across 24 graph instances, including two flower-family graphs and a two-edge sum of Petersen graphs, an improving move was found every time. These include repeated samples, not necessarily 4,800 distinct flows. The sample is not an exhaustive graph census or a statistical estimate. [Main tests](lex_descent_search.json); [additional tests](further_lex_search.json)

**Subsequent stronger check:** the [continuation](continuation.md) exhausts all flow classes on 589 specified graphs, including 1,349,868 classes requiring repair; every such class has an improving move. Its exact finite scope and symmetry reduction are explained there.

**Later outcome:** [a 16-vertex counterexample](repair-obstruction.md) has Ψ=(2,18), and all 175 neighboring flows have at least this potential. A neutral move followed by an improvement reaches a verified five-layer cover. Thus the strict-descent lemma is false even though the graph itself has the desired cover. The positive finite checks did not supply a universal guarantee.

### A tractable subproblem, with a proved linear formulation

Fix ℓ and choose a nonzero a with ℓ(a)=0. For a binary cycle x, the modification f'_e=f_e+a x_e preserves F and is nowhere-zero if x_e=0 whenever f_e=a.

Choose r with ℓ(r)=1. For each component K of G∖F, its obstruction bit changes by

\[
\sum_{\substack{e\in\delta(K)\\f_e\in\{r,r+a\}}}x_e.
\]

Thus choosing such a modification to repair specified component parities is a linear system: Bx=0, the forced zeros, and one equation per component. This follows because precisely the edges of colors r and r+a toggle membership in color r. It is useful for exact local repair searches, but Section 4 proves that preserving F cannot be sufficient in general.

## 7. What is proved, what is experimental, and what remains open

| Result | Evidence | Scope |
|---|---|---|
| Five-layer CDC ↔ an F₂⁴-flow avoiding C | Proof in Section 1 | Arbitrary finite loopless graphs |
| Fixed-flow lift ↔ binary coordinate completion ↔ cut parity | Proof in Sections 1–2 | Arbitrary starting flows; cubic setting used for the palette classification of pair-label lifts |
| Relabeling an arbitrary input flow does not always suffice | Explicit cube, rank certificate, seven independent systems | Counterexample to the proposed shortcut |
| Holding F fixed does not always suffice | Petersen structural argument and full flow enumeration | Counterexample to the proposed shortcut |
| Strict descent of D does not always work | Exhaustive neighborhood of one 14-vertex graph | Counterexample to the proposed shortcut |
| A neutral move can be useful | Explicit two-step path and verified cover | One constructive example |
| Strict lexicographic repair always works | **False**; a 16-vertex counterexample exhausts all 175 allowed neighbors | See the latest [counterexample report](repair-obstruction.md) |
| Every bridgeless graph has a five-layer CDC | **Not proved in this attempt** | Original open conjecture |

Reproduce the saved experiments with Python 3.10+ and NetworkX 3.6.1 (pinned in [requirements.txt](requirements.txt)):

```bash
python3 research/five-cdc-attempt/run_experiments.py
```

The scripts validate decoded covers by actual integer edge counts and even vertex degrees. Inconsistency witnesses are verified by XORing the indicated equations to obtain 0=1. The strict-descent counterexample uses every circuit, obtained by enumerating the binary cycle space and retaining connected supports. The runtime versions are recorded in [environment.json](environment.json).

The strict repair lemma is now disproved. The next mathematical issue is whether suitable sequences allowing neutral moves, or an appropriate reduction to a smaller graph class, always reach a successful flow. The [triangle reduction](repair-obstruction.md#3-a-proved-triangle-flattening-lemma) supplies one proved step; no general reachability result is established.
