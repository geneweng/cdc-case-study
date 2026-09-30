# Rank one obstructions and component reflections

**29 September 2026. The general 5-cycle double cover conjecture remains unproved here. This report gives a conditional theorem, a proved algebraic reduction with a finite computer-assisted classification, and an explicit graph demonstrating a new repair step. No claim of novelty over the complete literature is made.**

**Further result:** [Full component permutations](component-permutations.md) adds a second interaction matrix, classifies the obstructions surviving every component-color permutation, and constructs covers after changing the prescribed layer in all 215 saved test cases.

With five complement components, the preceding report confined a failed prescribed layer to boundary rank one over F₄. Allowing all six permutations of the nonzero component colors sharpens this condition: **two distinct nonzero boundary columns guarantee completion**. Any genuine failure must have all its nonzero columns equal, and exactly four or five nonzero rows.

For that remaining form, cyclic component recoloring and circuit offsets reduce to a Hermitian matrix on the complement components. At five components, an exhaustive finite classification leaves two explicit obstruction patterns. This is an exact test for the restricted recoloring family, not for the existence of a cover with the prescribed layer.

The distinction matters. A simple bridgeless cubic graph on 26 vertices has a starting coloring for which all 960 closed cyclic-recoloring-and-offset choices fail. Reflecting the colors in one component produces 48 successful choices, with the same prescribed layer. The verified cover is saved with the results.

## Setting and notation

Use the setting of [Five component completion](five-component-completion.md). The prescribed even subgraph F has circuits C₁,…,Cₜ. Its complement H has components K₁,…,K₅. A witnessing nowhere-zero flow f=(F,q) has nonzero two-bit colors on H. At v on F, write dᵥ for the color of its incident H-edge. The boundary matrix is

\[
A_{kj}=\sum_{v\in K_k\cap C_j}d_v\in\mathbb F_4.
\tag{1}
\]

Its rows and columns sum to zero. A column describes the boundary of one F-circuit across the five H-components. A row describes one H-component across all F-circuits. A cover layer may contain several circuits.

Write F₄={0,1,α,α²}, with α²=α+1, and let \(\bar x=x^2\) and Tr(x)=x+\(\bar x\). The code uses 0,1,2,3 for 0,1,α,α². The alternating binary pairing is

\[
\omega(x,y)=\operatorname{Tr}(x\bar y).
\]

The three cyclic color permutations are x↦ax for a≠0. The other three are x↦a\(\bar x\). All six are invertible binary linear maps, so applying any of them to an entire H-component preserves its internal flow conservation.

## A conditional theorem using reflections

**Theorem.** Suppose H has five components. If A is zero, has at most three nonzero rows, or has two distinct nonzero columns, then F is one whole layer of a five-cycle double cover.

**Proof.** Rank zero is the earlier balanced theorem, and F₄-rank at least two is the preceding five-component theorem. It remains to consider rank one. Write

\[
a_k=c_kv,\qquad v\ne0,\qquad \sum_k c_k=0.
\tag{2}
\]

Normalize v so its first nonzero coordinate is 1. The nonzero coefficient count m is between two and five.

If m=2, the two nonzero rows are equal and form one minimal zero-sum group. If m=3, the nonzero coefficients are the three distinct nonzero field elements, and the three rows form one minimal zero-sum group. Together with the zero singleton rows, these satisfy the stable grouped construction in the [four-component report](four-component-completion.md#recoloring-groups-of-components). This construction is not limited to four groups. It completes both cases.

Now suppose m is four or five and the nonzero columns are not all equal. Then v has a coordinate outside F₂, and v and \(\bar v\) are independent over F₄. Indeed, if \(\bar v=bv\), their first nonzero coordinates force b=1, making every coordinate of v fixed by conjugation and therefore binary.

Two nonzero coefficients cᵢ,cⱼ must be equal. Conjugate the colors on Kᵢ and Kⱼ. Their two boundary rows remain equal and still sum to zero, so closure on every F-circuit is preserved. They now lie on the line of \(\bar v\), while the remaining nonzero rows lie on the independent line of v. The new boundary matrix has F₄-rank two. Reintegrate the F-edge colors and apply the preceding five-component theorem. This completes the proof. □

Consequently, if an admissible F with five complement components cannot be a whole cover layer, **every** witnessing coloring has the form

\[
A=cw^{\mathsf T},\qquad
w\in\mathbb F_2^t\setminus\{0\},\qquad
|\operatorname{supp}w|\text{ even},\qquad
|\operatorname{supp}c|\in\{4,5\}.
\tag{3}
\]

The even weight follows from the zero row sums. Equivalently, every column is either zero or the same nonzero column c, repeated an even number of times. This is necessary for failure, not sufficient.

A useful special case is a prescribed layer with three circuits: if all three boundary columns are nonzero, completion follows. The six three-circuit failures checked in the preceding report instead have one zero column and two equal nonzero columns.

## A Hermitian model independent of the number of circuits

The following reduction works for any number h of complement components, provided (3)'s binary-generator form holds; the finite classification below specializes to h=5.

Put εₖ=1 when cₖ≠0 and εₖ=0 otherwise. On an active component, divide all its boundary demands by cₖ. Leave the other components unchanged. These normalized demands have boundary row εₖw. They need not close around the F-circuits until scalars are chosen.

Choose λₖ∈F₄* for every component, including those with zero boundary row. Circuit closure is exactly the single field equation

\[
\sum_k\varepsilon_k\lambda_k=0.
\tag{4}
\]

Fix an ordering around each F-circuit. For distinct k,l, sum over all pairs of positions on the same circuit, with the position from component k later in that order than the position from l:

\[
D_{kl}=\sum_j\ \sum_{\substack{r<i\text{ on }C_j\\k(i)=k,\ k(r)=l}}
d_i\overline{d_r}.
\tag{5}
\]

Here d denotes the normalized demand. Set Dₖₖ=0. Adding the two possible orders of a pair gives

\[
D_{kl}+\overline{D_{lk}}
=\sum_j(\varepsilon_kw_j)\overline{(\varepsilon_lw_j)}=0,
\tag{6}
\]

because w has even weight. Thus D is Hermitian.

For scalars satisfying (4), integrate the demands around the circuits starting from zero. The lift obstruction bit on component k is

\[
b_k(\lambda)=\sum_{l\ne k}
\operatorname{Tr}(\lambda_k\overline{\lambda_l}D_{kl}).
\tag{7}
\]

To justify the missing constant and same-component terms, use the norm N(x)=x\(\bar x\), which is one for nonzero x and zero for x=0. Its polarization is ω. On each circuit, the constant terms from the nonzero demands and the same-component pair terms sum to the norm of that component's boundary sum. Summing over circuits gives εₖ|supp w|=0. The remaining terms are exactly (7). This is the zero-indicator calculation from the earlier offset proof, with all interactions collected into D.

The arbitrary circuit constants affect b only through one aggregate z∈F₄. All four z values are possible because w is nonzero. Completion is therefore equivalent to

\[
\exists\lambda\in(\mathbb F_4^*)^h,\ z\in\mathbb F_4:
\quad \sum_k\varepsilon_k\lambda_k=0,
\quad b_k(\lambda)=\varepsilon_k\operatorname{Tr}(\lambda_kz)
\ \text{for every }k.
\tag{8}
\]

For circuit constants sⱼ, one may take \(z=\sum_jw_j\overline{s_j}\). Equation (8) is an exact criterion for the cyclic recolorings of the chosen component coloring and all circuit offsets. Other internal H-colorings and component reflections are additional freedoms.

This reduction compresses all circuit lengths and orders into a finite interaction matrix. The remaining choice of nonzero scalars is nonlinear; compressing it does not prove a solution always exists.

## Removing interactions with one reference component

For arbitrary u₁,…,uₕ∈F₄, replace each off-diagonal entry by

\[
D'_{kl}=D_{kl}+\varepsilon_k\overline{u_l}+u_k\varepsilon_l.
\tag{9}
\]

For a closed scalar assignment, substitution in (7) changes the obstruction vector by

\[
b'_k+b_k=\varepsilon_k\operatorname{Tr}(\lambda_k Z),
\qquad Z=\sum_l\overline{\lambda_l}\,\overline{u_l}.
\tag{10}
\]

This lies in the offset image, so (8)'s solvability is unchanged. Diagonal entries can continue to be set to zero; a Hermitian diagonal entry is binary and contributes zero trace.

Choose an active reference component p, put uₚ=0, and set uₖ=Dₖₚ for k≠p. Then all interactions with p vanish. The reduced matrix has only \(\binom{h-1}{2}\) independent field entries. A simultaneous rotation of all λ values leaves (7) unchanged, so λₚ may be fixed to 1.

For h=5, there are exactly 4⁶=4,096 reduced matrices for each active-component count. This bounded classification is independent of the size of the original graph or the number of F-circuits.

## The finite classification

Order the active reference component last, the other active components first, and the inactive components between them. The following finite lemma was checked exhaustively by **two implementations**, one using field tables and explicit offset values, the other using polynomial-bit multiplication and binary elimination. The computer-assisted part of the result is this finite lemma; equations (4)–(10) give the mathematical reduction to it.

| Nonzero boundary rows m | Closed states with λₚ=1 | Reduced matrices checked | Failing matrices |
|---|---:|---:|---:|
| 2 | 27 | 4,096 | 0 |
| 3 | 18 | 4,096 | 0 |
| 4 | 21 | 4,096 | 12 |
| 5 | 20 | 4,096 | 12 |

The failures have explicit descriptions:

1. **Five active components.** Every reduced entry is binary, and the entries equal to one form a path on the four nonreference components. There are 12 labeled paths.
2. **Four active components.** Among the four nonreference components, three are active and one is inactive. The three active-to-active entries are either all zero or all one. The three entries directed from the active components to the inactive component are 1,α,α² in some order. There are 2·6=12 such matrices.

All other matrices satisfy (8). A reduced matrix is an algebraic interaction object; its path or star does **not** assert that the original graph contains that configuration as a subgraph or has a Petersen minor.

The two programs check all 16,384 matrices and all 352,256 closed scalar assignments. The saved output includes every failing matrix and the entire histogram of successful state counts. This is a complete finite check of the stated matrix lemma, rather than a sample of graph instances. No formal proof-assistant verification is claimed.

## A reflection repairs an actual 26 vertex graph

The saved example has F equal to the two nine-circuits on vertex lists

```text
0 1 2 3 4 5 6 7 8 0
9 10 11 12 13 14 15 16 17 9
```

H has five components: the edges {0,9}, {2,13}, {4,12}, and two properly colored trees with six leaves each. Their vertex sets are

```text
{1,5,6,11,15,17,22,23,24,25}
{3,7,8,10,14,16,18,19,20,21}
```

The full edge list, initial flow, and decoded cover are in the saved certificate. Independent checks verify that G is simple, connected, bridgeless, and cubic. Its boundary columns are equal; the generator is w=(1,1), so the stronger column theorem does not apply directly.

For the initial coloring, the reduced interaction graph is the path 0—2—1—3, with the reference component isolated. All 60 closed rotation assignments fail for every one of the 16 circuit-offset pairs: 960 failures in total.

Reflect the colors in the tree containing vertex 3. Its boundary coefficient is 1, so this simply swaps colors 2 and 3 while fixing color 1. The boundary matrix stays unchanged, but the reduced interaction edge {1,3} disappears. The matrix is no longer an obstruction.

| Choice family | Closed rotation and offset pairs | Successful pairs |
|---|---:|---:|
| Original coloring, cyclic rotations and offsets | 960 | 0 |
| One component reflection, then cyclic rotations and offsets | 960 | 48 |

For one explicit solution, the subsequent component rotation states are (1,1,0,2,1), with state s meaning multiplication by αˢ. The circuit constants are (2,0). Component indices follow the sorted component order in the certificate. Direct flow conservation, the lift obstruction, even degrees in each layer, exact double coverage, and equality of the fifth layer with F are all checked.

Thus failure of the cyclic-recoloring search does not even exclude success under another permutation of the same component colors. The path signature is exact for the stated restricted family and must be used with that scope.

## Checks against the earlier data

For each of the 215 saved failed prescribed supports with five complement components, the script constructs one admissible flow independently and computes its reduced interaction matrix. Every one has the five-active path signature. This is a check of one witnessing coloring per support; it does not enumerate all colorings of those supports anew.

Additional seeded checks cover 1,600 binary-generator word systems, with 34,400 direct scalar-state comparisons. For each state, the Hermitian formula, the change under (9), and the offset solvability agree with direct circuit integration. The test finds both exceptional patterns. A further 800 nonbinary-generator rank-one systems are completed by conjugating a pair of components and applying the preceding theorem. Artificial word systems test the algebra; graph realization is claimed only for the explicit graph certificate.

The graph example has a separate enumeration of all 960 closed rotation-and-offset pairs before and after reflection. The two finite-matrix implementations use different arithmetic and different offset solvers.

```bash
python3 research/five-cdc-attempt/rank_one_obstruction.py
python3 research/five-cdc-attempt/verify_rank_one_obstruction.py
```

Files: [construction and classification](rank_one_obstruction.py), [independent finite verifier](verify_rank_one_obstruction.py), and [results and certificates](rank_one_obstruction_results.json).

## The remaining existence problem

There are now additional sufficient ways to finish a selected layer, and a small exact obstruction signature for one restricted family. What is still missing is a theorem that every bridgeless cubic graph admits a suitable layer, or that changes of layer, internal component colorings, or reflections always escape the relevant obstructions. Petersen's prescribed two-factor still prevents such a universal statement with F held fixed.

The next question is whether these interaction signatures can be connected to a graph operation that changes F while preserving enough flow structure to apply one of the proved completion criteria. The results here do not establish that operation or settle the general conjecture.
