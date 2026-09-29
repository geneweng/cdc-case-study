# Four component completion for a prescribed layer

**29 September 2026. This proves a conditional result, not the general 5-cycle double cover conjecture. No claim of novelty over the complete literature is made.**

The multiple-circuit completion problem can be solved when the complement has at most four connected components. This turns the corresponding observation in the preceding census into a theorem, with an explicit proof below. The bound is sharp for prescribed layers: a two-factor of Petersen has five complement components, is an admissible flow coordinate, and cannot be a whole layer of a five-layer cover.

The additional freedom is to add a constant two-bit color around each circuit. For fixed component recolorings, the constants solve a binary linear system. Combining this system with the earlier three-state parity argument handles every boundary configuration on at most four components, including configurations that are not entrywise balanced.

## Statement and scope

Let G be a connected loopless cubic graph. A binary even subgraph F is **admissible** if there is a nowhere-zero F₂³-flow f=(F,q), with q an F₂²-flow. Equivalently, G/E(F) has a nowhere-zero F₂²-flow: restrict q to the contracted graph, or extend such a flow across each contracted circuit. The lower two coordinates must be nonzero outside F but may be zero on F.

**Four component theorem.** Suppose F is admissible and H=G−E(F) has at most four connected components. Then G has a five-layer cycle double cover with F itself as one whole layer. Starting from any witnessing f, it is enough to cyclically permute the three nonzero q-colors independently on the H-components and change the colors on F.

F may contain arbitrarily many circuit components. Empty layers are permitted; if F is empty, admissibility already supplies a nowhere-zero 4-flow and the conclusion is immediate. The proof below treats nonempty F.

This does not show that every bridgeless cubic graph has an admissible F with at most four complement components. That selection step remains unproved here. It also does not give a sequence of moves with nonincreasing potential from the earlier repair experiments.

## Circuit constants give a linear completion problem

Write C₁,…,Cₜ for the circuits of F and K₁,…,Kₕ for the components of H. At each vertex v on F, let dᵥ≠0 be the q-color of its unique incident H-edge. As in the [preceding report](balanced-completion.md), define

\[
A_{kj}=\sum_{v\in K_k\cap C_j}d_v\in\mathbb F_2^2.
\tag{1}
\]

Every row sum and every column sum is zero. Regard each row aₖ=(Aₖ₁,…,Aₖₜ) as a vector in the binary space V=(F₂²)ᵗ. In particular, ∑ₖaₖ=0.

Let R(x₁,x₂)=(x₂,x₁+x₂). Choose Tₖ∈{I,R,R²} on each H-component. The transformed boundary rows a′ₖ=Tₖaₖ must satisfy the closure condition

\[
\sum_k a'_k=0.
\tag{2}
\]

This is necessary and sufficient to integrate the transformed leaf demands around every Cⱼ. Unlike the previous construction, allow an arbitrary starting constant sⱼ∈F₂² on each circuit. If its ordered vertices have transformed demands d′₀,…,d′ₘ₋₁, its outgoing edge colors are

\[
p_i=s_j+\sum_{r=0}^i d'_r.
\tag{3}
\]

Closure makes the last color equal the starting constant. Conservation holds, and f′=(F,q′) is nowhere-zero for every choice of the constants.

Let bₖ(s) be the parity of the zero-colored F-edges across δ(Kₖ). These are exactly the canonical lift obstruction bits. With ω(x,y)=x₁y₂+x₂y₁, the zero-indicator identity used previously gives

\[
b_k(s)=b_k(0)+\sum_j\omega(s_j,A'_{kj}).
\tag{4}
\]

Thus choosing the constants is a binary linear solve. Every component cut appears twice when summed, so ∑ₖbₖ(0)=0.

**Offset criterion.** Constants eliminating all obstructions exist if and only if

\[
\sum_k \lambda_k b_k(0)=0
\quad\text{whenever}\quad
\lambda\in\mathbb F_2^h,\quad\sum_k\lambda_k a'_k=0.
\tag{5}
\]

Indeed, the pairing ∑ⱼω(sⱼ,aⱼ) on V is nondegenerate. Therefore the left nullspace of the matrix in (4) consists precisely of the binary dependencies among its boundary rows. Standard binary linear duality gives (5).

An immediate consequence is useful: if the boundary rows have binary rank h−1, their only nonzero dependency is the sum of all rows, and the constants always solve the problem. At lower rank, the extra dependencies are the obstructions that recoloring must address.

## Recoloring groups of components

Partition {1,…,h} into groups P₁,…,Pᵣ such that

\[
\sum_{k\in P_a}a_k=0\quad\text{for each group }P_a.
\tag{6}
\]

Use one common transformation Tₐ on all components in Pₐ. Closure is then automatic for every independent choice of these group transformations.

The [balanced-boundary argument](balanced-completion.md#3-proof-of-balanced-completion) applies to the groups, which need not be connected. It uses only the partition of the circuit positions and the zero boundary sum of each part on each circuit. Conservation within the original H-components is preserved. Consequently there are group transformations for which

\[
\sum_{k\in P_a}b_k(0)=0\quad\text{for every }P_a.
\tag{7}
\]

The algebraic ingredient is the three-state parity lemma: reciprocal pair interactions with zero sums over each state argument have a simultaneous zero-parity assignment. This ingredient was already stated in [Ulyanov, Lemma 3.2](https://arxiv.org/html/2607.13225v1#S3); the preceding report proves how the graph boundary data fit its hypotheses.

Suppose additionally that each group's only internal row dependency is its full sum, and that the row spans of different groups remain a direct sum under all their allowed transformations. Then the group indicators span the entire dependency space in (5). Equation (7) therefore guarantees a final offset solution. A singleton zero row counts as a group with its full-sum dependency and rank zero.

This provides a general sufficient condition for more than four components as well. It is not asserted for every boundary table.

## Proof for at most four components

Pad a system with fewer than four components by zero rows and zero obstruction bits. These dummy components have no circuit positions and cause no additional constraint. It suffices to treat four rows a₁,…,a₄ summing to zero.

Identify F₂² with F₄ so that multiplication by its three nonzero scalars acts as I,R,R². This identifies V with F₄ᵗ, while **rank and dependencies below remain over F₂**.

### Full rank and direct sum cases

If the binary rank is three, the offset criterion alone applies. Otherwise, elementary binary linear algebra gives the following exhaustive list, up to reordering rows. In the rank-two rows of the table, x and y are binary linearly independent.

| Binary rank | Row pattern | Treatment |
|---|---|---|
| 0 | 0,0,0,0 | Four singleton groups |
| 1 | v,v,0,0 | One pair group and two singleton groups |
| 1 | v,v,v,v | Collinear case below |
| 2 | x,y,x+y,0 | One triple group and one singleton group |
| 2 | x,x,y,y | Two pair groups, unless x and y are F₄-collinear |

For the pair-plus-zero and triple-plus-zero patterns, the nonzero group retains its rank under every common transformation and the other row spans are zero. The group argument applies.

For x,x,y,y with x and y not F₄-collinear, nonzero scalar multiples of x and y can never become equal. Their binary one-dimensional spans therefore remain independent under all separate group transformations. The group argument again applies.

This leaves exactly the case of four nonzero rows on one F₄-line.

### Four collinear nonzero rows

Independently rotate each component so that all four rows become the same nonzero vector v. This preliminary change is valid: the new column sums are 4v=0, so the F-colors can be reintegrated. Every row still has zero sum across circuits.

There are three ways to split four indices into two pairs. Fix one, P|Q. Apply scalar a∈F₄* on P and b∈F₄* on Q. Each pair has zero aggregate boundary row, so closure holds for all a,b.

The aggregate obstruction on P is a bilinear interaction Bₚ(a,b), by the grouped balanced-boundary calculation. The aggregate obstruction on Q is equal to it. Each row and column of its 3×3 state table sums to zero.

If some pairing admits a≠b with Bₚ(a,b)=0, choose those scalars. The resulting rows are av,av,bv,bv. The two different nonzero vectors av and bv are binary independent. Their only dependencies are the two pair sums, whose obstruction sums vanish. Equation (5) supplies constants that remove all four individual obstructions.

The remaining possibility is that, for every pairing, Bₚ(a,b)=1 whenever a≠b. Zero row sums then force Bₚ(a,a)=0. Use the same scalar on all four components. For this one common configuration, all three pairings have zero aggregate obstruction. Hence

\[
b_1(0)=b_2(0)=b_3(0)=b_4(0).
\]

All boundary rows are the same nonzero vector av. The image of the offset map is precisely the span of (1,1,1,1): its defining linear functional is nonzero and therefore takes both binary values. The common obstruction bit can be canceled.

Every possible four-row configuration has now been handled. The resulting flow has every bₖ=0, so the extra-coordinate lift gives five even layers covering every edge exactly twice, with F as its fifth layer. This proves the theorem. □

## Circuit constants are necessary in an explicit example

The proof's final case is not merely a technical possibility. Build three disjoint four-circuits, with their vertices labeled by k=0,1,2,3 in cyclic orders

```text
0 1 2 3
0 1 3 2
0 2 1 3
```

Add four centers, joining center k to the vertex labeled k on each circuit. This gives a simple cubic graph with 16 vertices. Let F be the union of the three four-circuits. Its complement consists of four three-leaf stars. Color each star's edges 1,2,3 according to their circuit, so all four boundary rows equal (1,2,3).

There are 81 component-rotation assignments. Exactly 21 satisfy closure. **None** succeeds when all circuit constants are zero. Of these 21, the 18 assignments producing rank two cannot be repaired by constants either. The remaining three have four equal rows and admit 32 offset solutions each, for **96** successful rotation-and-offset pairs.

For example, leave the component colors unchanged and set the three circuit constants to (2,0,0). This cancels the initial obstruction vector (1,1,1,1). The script constructs and independently decodes a five-layer cover with the prescribed F.

The saved record includes the graph, all counts, boundary table, final flow, and cover. Direct enumeration checks all 1,344 closed rotation-and-offset pairs without using the linear solver. Thus omitting the circuit constants would incorrectly reject a valid four-component instance.

## Sharpness at five components

Use Petersen and prescribe F to be its two pentagons. H consists of five matching edges. Their colors may initially be 1,1,1,2,3, which have XOR zero on each pentagon and therefore extend to an admissible flow.

Independent cyclic rotations of these one-edge components cover every possible nonzero matching-edge coloring. Of the 3⁵=243 assignments, exactly 60 satisfy closure. Each has 4²=16 possible circuit constants. Directly checking all **960** resulting admissible flows finds no successful lift: 720 have two obstructed components and 240 have four.

The [earlier structural argument](attempt.md#4-second-attempted-proof-repair-the-flow-while-keeping-f-fixed) proves that this F cannot be an entire five-layer cover member, independently of the computation. Thus replacing “at most four” by “at most five” is false. Petersen itself still has five-layer covers with other choices of F.

## Verification and reproduction

The implementation exhausts component rotations and solves (4) for the constants. For fixed input coloring, it searches exactly that family of recolorings and offsets. With h≤4, at most 81 rotation assignments are needed. For arbitrary h the search is exponential in h; failure there does not exclude other internal colorings of H.

Checks on the 26 saved connected bridgeless simple cubic graphs through ten vertices cover all flow classes and normal choices with at most four complement components. Repeated restrictions with identical F and identical q-colors on H are deduplicated, leaving **14,867** inputs:

| Proof case used by the checker | Inputs |
|---|---:|
| Full offset rank | 1,800 |
| Entrywise balanced | 11,438 |
| Stable direct sum groups | 1,391 |
| Four collinear rows | 238 |

Every input is repaired, and every resulting cover is checked by actual edge multiplicities, even vertex degrees, and exact equality of its fifth layer with F. The checker classifies overlapping cases in its stated program order.

An additional **800** seeded systems of circuit words, with one to four components and one to six circuits, test arbitrary boundary tables with zero row and column sums. All rotations are exhausted. The predicted offset coefficients are checked against direct integration, rather than another matrix formulation. These artificial systems test the algebra without assuming that every generated word system is realized by a cubic graph.

The case classification is also checked on all **4,096** four-by-three F₄ boundary tables with zero row and column sums. All sixteen binary bilinear forms in two arguments are checked: ω is the unique one that has no zero on unequal nonzero arguments, confirming the exceptional state-table calculation used in the proof.

The 16-vertex example and the Petersen failure have separate exhaustive offset checks. These finite checks support the implementation; the general four-component statement rests on the proof above.

```bash
python3 research/five-cdc-attempt/coupled_completion.py
```

Results and explicit certificates are in [coupled_completion_results.json](coupled_completion_results.json). The earlier census observation is explained, but the general existence of an appropriate F remains unresolved.
