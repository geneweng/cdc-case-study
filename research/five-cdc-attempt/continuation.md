# Continuing the 5-CDC proof attempt

**29 September 2026. The general conjecture is still not proved by this work.**

**Subsequent correction to the proof strategy:** the proposed strict lexicographic repair lemma tested here is **false on a 16-vertex graph**. See [the explicit counterexample and triangle reduction](repair-obstruction.md). The finite checks and algebraic reformulations below remain valid; the proposed universal inference does not.

This continues [the first attempt](attempt.md). The new mathematical result is an exact formulation using alternating bilinear forms, followed by a linear completion problem. The new computational result is exhaustive verification of the proposed lexicographic repair lemma on every connected bridgeless simple cubic graph with at most 14 vertices. These are finite checks of a proposed lemma, not a proof of that lemma for arbitrary graphs. No novelty over the complete literature is claimed for the algebraic deductions.

## 1. Exhaustive verification of the candidate repair lemma

For a nowhere-zero binary 3-flow f, let D_ℓ(f) count the obstructed components of the complement of the binary cycle ℓ∘f. As before, use

\[
\Psi(f)=\left(\min_{\ell\ne0}D_\ell(f),\ \sum_{\ell\ne0}D_\ell(f)\right)
\]

in lexicographic order. The proposed lemma says: if its first entry is positive, some circuit Q and nonzero vector a absent from f(Q) give a flow f+aχ_Q with strictly smaller Ψ.

The complete small-graph check found no counterexample:

| Vertices | Connected simple cubic graphs generated | Bridgeless graphs checked | Nowhere-zero flow classes | Classes requiring repair |
|---:|---:|---:|---:|---:|
| 4 | 1 | 1 | 2 | 0 |
| 6 | 2 | 2 | 15 | 0 |
| 8 | 5 | 5 | 178 | 15 |
| 10 | 19 | 18 | 3,164 | 641 |
| 12 | 85 | 81 | 73,459 | 26,693 |
| 14 | 509 | 480 | 2,218,848 | 1,144,965 |
| **Total** | **621** | **587** | **2,295,666** | **1,172,314** |

“Class” here identifies flows under the 168 invertible linear changes of coordinates in F₂³; it does not additionally identify graph automorphisms. An improving move was found in every class requiring repair. Classes already admitting a five-label lift need no move.

### Why this covers every flow, rather than a sample

Let Z=ker B be the binary cycle space, with dimension r=|E|−|V|+1 for a connected graph. A binary 3-flow is a triple of vectors in Z. Its coordinate span W is unchanged by an invertible change of coordinates. Conversely, any two spanning triples of the same W are related by such a change. Thus the flow classes correspond precisely to subspaces W⊆Z of dimension at most three. Nowhere-zero means that the union of their supports is E.

Rank one is impossible in a nonempty cubic graph: three identical nonzero values cannot sum to zero. A full-support rank-two flow already has a successful normal annihilating its image. The program enumerates every rank-two and rank-three subspace in unique reduced row echelon form. For each rank k it checks its enumeration count against the Gaussian binomial coefficient

\[
{r\brack k}_2=\prod_{i=0}^{k-1}\frac{2^r-2^i}{2^k-2^i}.
\]

A coordinate change permutes the seven normals, so it preserves Ψ. It also sends an allowed move (Q,a) to an allowed move (Q,Ta). Checking one representative is therefore sufficient. A full-support rank-two subspace represents 7×6=42 labeled flows; a rank-three subspace represents 7×6×4=168.

The graph census uses `geng -c -d3 -D3 n`, followed by an explicit bridge test. Circuit enumeration exhausts the binary cycle space and retains connected nonempty supports; in a cubic graph these are exactly the circuits. The implementation stops inspecting a flow's neighbors as soon as it finds a strictly improving move. It exhausts the neighborhood only if no such move is found. See [nauty's documentation](https://users.cecs.anu.edu.au/~bdm/nauty/nug28.pdf) for the graph generator.

The optimized implementation represents cycles and cuts by bitmasks and caches component cuts. It cross-checks regularly against the earlier edge-list implementation. All graph encodings, per-graph counts, potential histograms, and verification counts are saved in [exhaustive_repair_results.json](exhaustive_repair_results.json).

**Limits.** This census concerns simple graphs, not cubic multigraphs, and stops at 14 vertices. These size bounds do not apply to a possible counterexample to the original 5-CDC conjecture: the program is testing the stronger flow-repair statement. The check also does not establish any connectivity theorem for the full graph of flow reconfigurations.

### Additional exhaustive test on the two 18-vertex snarks

I also tested the two 18-vertex snarks of girth at least five and cyclic edge-connectivity at least four. This is a standard, independently catalogued pair in the [House of Graphs snark census](https://houseofgraphs.org/meta-directory/snarks). Here the graphs were generated locally: `geng -c -d3 -D3 -t -f 18` produces 455 connected cubic graphs of girth at least five. Exact three-edge-coloring backtracking and a check of every two- and three-edge cut retain precisely two graphs. Thus these inputs were regenerated, rather than relying on copied edge lists.

| 18-vertex graph, identified by saved order | Nowhere-zero flow classes | Classes requiring repair | Counterexamples |
|---|---:|---:|---:|
| First | 118,960 | 88,372 | 0 |
| Second | 119,260 | 89,182 | 0 |

Both flow enumerations were exhaustive; their rank-two full-support counts are zero, as expected from failure of three-edge-colorability. The graph6 encodings, complete edge lists, and per-graph results are in [snark_repair_results.json](snark_repair_results.json).

**Combined scope:** 589 graphs, 2,533,886 flow classes, and 1,349,868 classes requiring repair. These classes represent 425,361,594 labeled nowhere-zero flows. The larger labeled total follows from the proved coordinate-change symmetry, not from individually traversing that many flows. This does not constitute a census of all 16- or 18-vertex cubic graphs.

## 2. The obstruction is an alternating bilinear form

Write a binary cycle as its edge-indicator vector. Fix F∈Z and let K range over the connected components of H=(V,E∖supp F). Define

\[
\beta_K(y,z)=\sum_{e\in\delta(K)}y_ez_e\quad\text{in }\mathbb F_2,
\qquad y,z\in Z.
\tag{1}
\]

These forms have three useful properties.

1. **They are alternating.** For y∈Z, β_K(y,y)=∑_{δ(K)}y_e=0, because every binary cycle meets every cut evenly.
2. **F lies in every radical.** All edges of δ(K) lie in supp F, so β_K(F,z)=∑_{δ(K)}z_e=0 for every z∈Z. Consequently the forms descend to Z/⟨F⟩. If F=0, interpret this quotient as Z.
3. **Their sum is zero.** Each edge between components of H occurs in two component cuts. Therefore ∑_K β_K=0 as a bilinear form.

The common vanishing condition has a direct cover interpretation.

**Proposition.** Suppose F,y,z∈Z and their supports together cover E. Form the nowhere-zero flow

\[
f_e=4F_e+2y_e+z_e.
\]

The canonical extra-coordinate lift from the first attempt exists if and only if β_K(y,z)=0 for every component K of H.

**Proof.** On the edges of F, the required fourth bit is 1+y_ez_e: it is one on flow values 4,5,6 and zero on value 7. Binary incidence completion is possible exactly when its prescribed sum on each component cut is zero. The cardinality of δ(K) is even, because δ(K)⊆supp F and F is a binary cycle. Thus the prescribed sum is

\[
\sum_{e\in\delta(K)}(1+y_ez_e)
=\beta_K(y,z).
\]

The extra-coordinate lift then decodes to five even layers as proved in [the first attempt, Section 1](attempt.md#1-an-exact-reformulation-one-extra-binary-flow-coordinate). □

Equivalently, the search is for F and a subspace U of Z/⟨F⟩ of dimension at most two such that every β_K vanishes on U×U, and U covers every edge outside F. Here “covers” means that for each such edge, some vector in U has coordinate one. This is well-defined in the quotient because adding F does not change coordinates outside F.

The equivalence is exact in both directions. A successful pair of generators y,z gives a five-layer cover by the proposition. Conversely, any five-layer cover has a nowhere-zero projected three-bit flow under the five-vector encoding in the first attempt, so its coordinates supply F,y,z with these properties.

This explains what changes from the ordinary CDC argument. In that argument, a local identity annihilates the linear dual obstructions for every starting flow. Here the cut obstructions become bilinear conditions on the choice of two cycle vectors. They do not automatically vanish; the cube and Petersen failures from the first attempt remain valid.

## 3. Fixing two coordinates makes the last choice linear

For fixed binary cycles F and y, the entire search for the third coordinate z is the following linear system:

\[
\begin{aligned}
Bz&=0,\\
z_e&=1 &&\text{if }F_e=y_e=0,\\
\sum_{e\in\delta(K)}y_ez_e&=0 &&\text{for each component }K\text{ of }G\setminus F.
\end{aligned}
\tag{2}
\]

The first line makes z a binary cycle, the second makes f nowhere-zero, and the third is precisely the proposition's lift criterion. Thus consistency is sufficient, and every canonical successful flow occurs in one such system.

This gives an exact search over 2^(2r) pairs (F,y), each followed by a linear solve, instead of enumerating all 2^(3r) labeled three-coordinate flows individually. This is an exponential decision procedure, not a proof of universal consistency and not a claim of the best known algorithm. A consistent pair with solution-space dimension d represents exactly 2^d distinct successful labeled flows. These are flow counts, not counts of distinct cycle double covers.

The implementation exhausts the pairs on two test graphs:

| Graph | All pairs (F,y) | Consistent pairs | Successful flows, summed by affine dimension |
|---|---:|---:|---:|
| Petersen | 4,096 | 750 | 4,560 |
| Cube | 1,024 | 507 | 2,784 |

The Petersen total agrees with the earlier independent enumeration of all 262,144 three-coordinate flows. A separate enumeration of all 32,768 three-coordinate cube flows finds 5,712 nowhere-zero flows and exactly 2,784 canonical lifts, also agreeing. For every consistent pair on both graphs, the script constructs one solution, runs the separate fourth-coordinate solver, and checks the resulting cover by actual edge multiplicities and even vertex degrees. For every inconsistent pair, it checks a row-combination certificate of 0=1. It also verifies the form identities on a basis. Results, example covers, and example inconsistency certificates are in [isotropic_completion_results.json](isotropic_completion_results.json).

On Petersen, the first coordinates admitting no completion are precisely F=0 and the six spanning 2-factors. The F=0 failure is its lack of a nowhere-zero binary 2-flow; the other six failures have the structural explanation already given in the first attempt.

## 4. What remains unproved

The two concrete mathematical questions from this stage now have different statuses:

- Does every unsuccessful three-bit flow have a circuit move decreasing Ψ? **No.** The later [16-vertex counterexample](repair-obstruction.md) answers this negatively, despite every finite check recorded above passing.
- Can one always choose F,y so that (2) is consistent? This is exactly the missing existence step in the new formulation, and is equivalent to the original five-layer problem via the encoding.

The latter question has two coupled requirements: common isotropy for the cut forms and full support outside F. A generic dimension argument for isotropic subspaces does not ensure that all those edge coordinates are covered. Holding F fixed is already known to fail. These are substantive obstacles, not omitted routine steps.

## Reproduction

Use Python 3.10+, NetworkX 3.6.1, and nauty's `geng` (or `nauty-geng`) on PATH.

The recorded run used Python 3.13.7 and Nauty&Traces 2.9301 (32 bits), alongside NetworkX 3.6.1. The census JSON files record the runtime versions.

```bash
python3 research/five-cdc-attempt/exhaustive_repair.py --max-order 14
python3 research/five-cdc-attempt/snark_repair.py
python3 research/five-cdc-attempt/isotropic_completion.py
```

The first command took about seven minutes on the current machine, the snark check about two minutes, and the completion check about a second; timing depends on the environment. The previous experiments remain reproducible with `run_experiments.py`.
