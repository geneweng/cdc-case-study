# Full component permutations and changing the prescribed layer

**29 September 2026. The general 5-cycle double cover conjecture remains unproved here. The result below is a computer-assisted characterization of a fixed-coloring repair family, followed by a finite layer-selection experiment. No claim of novelty over the complete literature is made.**

**Subsequent result:** [All seven coordinates can be impossible prescribed layers](layer-selection-obstruction.md) gives a 30-vertex counterexample to universal coordinate selection from an arbitrary flow. The finite successes below remain valid. The new example has a verified five-layer cover after one circuit switch changes the flow's coordinate space.

The remaining rank-one interaction problem can now be classified under **all six color permutations on every complement component**, together with arbitrary circuit constants. A second matrix records the reflections omitted by cyclic recoloring. After normalization, exactly two choices of this second matrix remain obstructed for each of the two previously identified obstruction types.

For the 215 saved failed prescribed-layer cases, representing 35 distinct graphs, every selected starting coloring has one of these persistent forms. Nevertheless, choosing another coordinate of the same three-bit flow and then completing that new layer produces a verified five-layer cover in every case. This is finite evidence for changing the layer; it is not a proof that such a choice always works.

## Scope and the remaining boundary form

Use the notation of [Rank one obstructions and component reflections](rank-one-obstruction.md). The prescribed even subgraph F has circuits C₁,…,Cₜ, and H=G−E(F) has five components. A witnessing nowhere-zero flow f=(F,q) gives a boundary matrix A. Earlier results handle all but the following possible failures:

\[
A=cw^{\mathsf T},\qquad
w\in\mathbb F_2^t\setminus\{0\},\qquad
|\operatorname{supp}w|\text{ even},\qquad
|\operatorname{supp}c|\in\{4,5\}.
\tag{1}
\]

Write εₖ=1 if cₖ≠0 and zero otherwise. Divide demands on each active component by cₖ, leaving inactive components unchanged. Each normalized boundary row is εₖw. The field is F₄={0,1,α,α²}, with α²=α+1 and conjugation \(\bar x=x^2\).

We keep the internal coloring of each H-component fixed up to a global permutation of its three nonzero colors. Changing a coloring by internal circuit switches is outside this repair family. F also stays fixed throughout the matrix classification.

## The second matrix records reflections

For positions r<i on one ordered F-circuit, let dᵢ,dᵣ be normalized nonzero demands and k(i),k(r) their H-component indices. Define, for k≠l,

\[
D_{kl}=\sum_j\sum_{\substack{r<i\text{ on }C_j\\k(i)=k,\ k(r)=l}}
d_i\overline{d_r},\qquad
E_{kl}=\sum_j\sum_{\substack{r<i\text{ on }C_j\\k(i)=k,\ k(r)=l}}
d_i d_r.
\tag{2}
\]

Set their diagonals to zero. The first matrix is Hermitian, Dₖₗ=\(\overline{D_{lk}}\); the second is symmetric, Eₖₗ=Eₗₖ. In each case the difference between the two position orders is the product of their component boundary sums, summed over circuits, which vanishes because w has even weight.

Every permutation of the three nonzero colors has the form

\[
d\longmapsto\lambda_k\sigma_{r_k}(d),
\qquad \sigma_0(d)=d,\quad \sigma_1(d)=\bar d,
\quad \lambda_k\in\mathbb F_4^*,\quad r_k\in\{0,1\}.
\]

Since conjugation fixes the binary vector w, closure is independent of the reflection choices:

\[
\sum_k\varepsilon_k\lambda_k=0.
\tag{3}
\]

The Hermitian matrix after choosing reflections is

\[
D^{(r)}_{kl}=\begin{cases}
D_{kl},&r_k=r_l=0,\\
\overline{D_{kl}},&r_k=r_l=1,\\
E_{kl},&r_k=0,\ r_l=1,\\
\overline{E_{kl}},&r_k=1,\ r_l=0.
\end{cases}
\tag{4}
\]

This follows by substituting d or \(\bar d\) in (2). The previous cyclic-recoloring criterion now applies to D⁽ʳ⁾. With Tr(x)=x+\(\bar x\), full completion is equivalent to

\[
\exists r,\lambda,z:\quad
\sum_k\varepsilon_k\lambda_k=0,\qquad
\sum_{l\ne k}\operatorname{Tr}(\lambda_k\overline{\lambda_l}D^{(r)}_{kl})
=\varepsilon_k\operatorname{Tr}(\lambda_kz)
\quad\text{for all }k.
\tag{5}
\]

The aggregate z accounts for all circuit constants, as proved in the preceding report. Thus (D,E) retains exactly the information needed for this entire component-permutation family.

## Normalization preserves every reflection choice

For arbitrary uₖ∈F₄, apply the following changes to off-diagonal entries:

\[
\begin{aligned}
D'_{kl}&=D_{kl}+\varepsilon_k\overline{u_l}+u_k\varepsilon_l,\\
E'_{kl}&=E_{kl}+\varepsilon_ku_l+u_k\varepsilon_l.
\end{aligned}
\tag{6}
\]

For each reflection vector r, equation (4) turns (6) into the previous Hermitian gauge change, with uₖ replaced by uₖ or \(\bar u_k\) according to rₖ. That change lies in the circuit-offset image for every closed λ. Consequently (5)'s feasibility is unchanged for **every** reflection vector, not only for r=0.

Choose an active reference component p and put uₚ=0, uₖ=Dₖₚ. All reference interactions in D′ disappear. E′ is updated simultaneously and need not have zero reference interactions. This distinction is essential: discarding them would lose information about reflections.

A simultaneous conjugation of every component preserves feasibility. With five components, every subset or its complement has size at most two. It therefore suffices to test the 16 subsets of size zero, one, or two. Equivalently one may fix the reference reflection to zero and test the other four binary choices.

## Computer-assisted classification of the persistent forms

If the reduced D already permits cyclic completion, no reflection is needed. Otherwise, the earlier complete matrix classification leaves either a binary path on four nonreference components, or a three-color star with a uniform active triangle.

These have one canonical representative each. Label the reference component 4. For five active components, relabel the other four to make D the path 0—1—2—3, with component 4 isolated. For four active components, use active indices {0,1,2,4}, inactive index 3, and

\[
D_{03}=1,\quad D_{13}=\alpha,\quad D_{23}=\alpha^2,
\]

with all other upper-triangular entries zero. The reverse entries are their conjugates.

The uniform active triangle may initially have ones instead of zeros. To toggle it while keeping the reference row zero, use (6) with u₄=α and uᵢ=εᵢα² for i≠4. Relabel the other three active indices to order the star colors. These changes are bijections on the possible E matrices and preserve full feasibility.

**Finite classification theorem.** For either canonical D, the pair resists all component-color permutations and circuit offsets exactly when, on its ten upper-triangular entries,

\[
E_{ij}=\overline{D_{ij}}+\eta\varepsilon_i\varepsilon_j
\quad(i<j),\qquad \eta\in\{0,1\}.
\tag{7}
\]

E is then completed symmetrically, rather than by Hermitian symmetry. The same upper-triangular description holds for any of the reduced path or star representatives in the stated active/inactive ordering. Permuting the nonreference active indices preserves it; the triangle-toggle normalization exchanges the two η values.

More explicitly:

- In the five-active path case, E is either the same binary path matrix as D or its off-diagonal complement on all five components, including the reference component.
- In the four-active star case, E's three star entries are 1,α²,α. Every pair of active components, including pairs involving the reference, receives the same entry η. The reference-to-inactive entry is zero.

### Exhaustive verification of the finite theorem

For each canonical D, all 4¹⁰=1,048,576 symmetric zero-diagonal E matrices are considered. A complete filter first asks whether each of the five single-component reflections is still obstructed. Any excluded matrix already has a completion. All 16 reflection classes are then checked for every survivor.

| Canonical D | E matrices enumerated | Survive all single reflections | Survive every reflection class |
|---|---:|---:|---:|
| Four-active star | 1,048,576 | 4 | 2 |
| Five-active path | 1,048,576 | 8 | 2 |

The final two matrices in each row are precisely (7). In the star case, the other two single-reflection survivors remain obstructed in 10 of the 16 reflection classes. In the path case, the other six survive in only six classes. Thus testing single reflections alone can miss a repair by two reflections.

Two implementations verify this classification. The first uses the previously verified obstruction signatures. The independent verifier does not use those signatures or the gauge reduction: it tests the scalar and offset equations directly, using polynomial-bit field arithmetic and binary elimination. Both enumerate all 2,097,152 E matrices and agree on all surviving lists. The general characterization combines the mathematical reductions (2)–(6) with this finite exhaustive lemma. No proof-assistant verification is claimed.

## The exceptional algebraic cases have word realizations

The finite matrices are not merely unchecked algebraic possibilities. Any pair of the required Hermitian/symmetric matrices can be realized by circuit words with binary generator w=(1,1).

Start with two identical words containing the active component symbols, with zero-sum coefficients: (1,1,1,2,3) in the five-active case, or (1,1,1,0,1) in the four-active ordering. Their normalized interaction matrices cancel. If needed, add a consecutive equal-colored pair for the inactive component.

Appending a four-position block

\[
(i,a),\ (j,b),\ (i,a),\ (j,b)
\tag{8}
\]

changes only the interaction on {i,j}, adding

\[
(\Delta D_{ij},\Delta E_{ij})=(a\bar b,ab).
\]

The block has zero total demand on each component, so it preserves boundary sums, closure, and interactions with positions outside the block. The four choices a,b∈{1,α} give a binary basis of F₄×F₄: their resulting pairs are (1,1), (α²,α), (α,α), and (1,α²). Thus blocks independently realize every desired matrix entry. Multiply normalized demands back by the original component coefficients to obtain closed words.

The script constructs all four persistent canonical pairs and one case of each type that requires two reflections. It recomputes their matrices from the words and verifies all reflection choices. These are algebraic word realizations; their realization as cubic graphs is not asserted. The previously certified 26-vertex graph is also checked and still requires one reflection before cyclic completion succeeds.

## Changing the layer repairs the saved graph cases

The input here is the same set of 215 failed prescribed supports used in the preceding report, on 35 distinct graphs. There is one selected witnessing flow for each support. All 215 have η=0 in (7), and all 16 reflection classes remain obstructed. This confirms, within the exact permutation model, that these starting colorings cannot be repaired while keeping their prescribed layer.

For each input flow f, examine the six other nonzero linear functionals on F₂³. Each supplies a different coordinate representation of the same nowhere-zero flow and a candidate support F′. Test the existing completion criteria, then construct and independently verify the resulting cover. Every one of the 215 inputs succeeds:

| First successful route in the script's normal order | Cases |
|---|---:|
| At most four complement components | 102 |
| Balanced boundary, any number of complement components | 92 |
| Five components and field rank at least two | 5 |
| Five components with successful cyclic recoloring and offsets | 16 |
| Total | 215 |

The counts depend on checking normals in numerical order and stopping at the first success; they do not measure how many routes are available. Covers are checked by direct flow conservation, component-cut obstructions, even degrees, exact edge multiplicities, and equality of their fifth layer with the newly selected F′.

This is **one starting flow per saved failed support**, not every flow on those graphs and not a universal layer-selection theorem. In particular, failure of the fixed-coloring permutation family does not characterize all possible internal colorings of H.

### A 20 vertex example needs the earlier balanced theorem

One saved input has complement-component counts, in normal order 1 through 7,

\[
(6,6,9,5,10,9,9),
\]

and lift-defect counts

\[
(2,2,2,2,4,2,2).
\]

Its only coordinate support with at most five complement components is the original failed support, at normal 4. No coordinate relabeling alone gives a successful lift, since every displayed defect is positive.

At normal 1, however, the coordinate support is a single circuit of length 16, and its complement has six components. The boundary is automatically balanced. Component rotations and circuit constants give a verified five-layer cover. This example shows why a selector restricted to the newest five-component theorem would miss a repair available from the earlier single-circuit theorem.

The saved certificate includes the graph, original flow, all displayed counts, coordinate change, recoloring, and decoded cover. It does not show that every starting flow on this graph needs six components, or that the graph lacks some other successful support with fewer components.

## Reproduction and remaining gap

```bash
python3 research/five-cdc-attempt/component_permutations.py
python3 research/five-cdc-attempt/verify_component_permutations.py
```

Files: [construction and classification](component_permutations.py), [independent finite verifier](verify_component_permutations.py), and [saved results and cover certificates](component_permutation_results.json).

Beyond the complete matrix enumeration, checks compare 8,000 reflected matrices against direct word recomputation on 500 seeded systems, test the six constructed exceptional word systems and the 26-vertex graph, and check all 215 changed-layer covers. The saved graph checks also recompute all reflected matrices directly from their circuit words.

The matrix classification completely describes the full component-permutation family for the remaining five-component binary-generator form. The successful coordinate-selection experiment suggested a broader mechanism, but the [subsequent counterexample](layer-selection-obstruction.md) rules out selecting from the seven coordinates of an arbitrary fixed flow, even with unrestricted changes to the remaining coordinates. A general proof must allow changes beyond that starting coordinate space, or use decomposition and independent cover choices on the pieces. The existence step remains unresolved here.
