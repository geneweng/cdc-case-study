# Five component completion and the remaining rank one obstruction

**29 September 2026. A conditional existence proof is supplied below. The general 5-cycle double cover conjecture remains unproved by this work. No claim of novelty over the complete literature is made.**

The preceding result completes every admissible prescribed layer whose complement has at most four components. At five components, a further algebraic condition suffices: the boundary rows must span at least two dimensions over the four-element field. The proof works with any number of circuits in the prescribed layer.

Consequently, a prescribed layer with five complement components can fail only if **every witnessing boundary coloring has rank exactly one over the four-element field**. Rank zero is covered by the earlier balanced theorem. Rank one does not itself imply failure: many such inputs succeed, but Petersen supplies a failure.

This narrows the obstruction that a layer-selection argument would need to avoid. It does not yet supply that selection argument or handle arbitrary numbers of complement components.

## The theorem and its assumptions

Let G be a connected loopless cubic graph, and let F be an even subgraph. Suppose there is a nowhere-zero flow

\[
f=(F,q):E(G)\longrightarrow\mathbb F_2^3,
\]

where q is a two-bit flow, nonzero on H=G−E(F). Write C₁,…,Cₜ for the circuits of F and K₁,…,K₅ for the five components of H. At a vertex v on F, let dᵥ be the nonzero q-color of the incident H-edge. Define

\[
A_{kj}=\sum_{v\in V(K_k)\cap V(C_j)}d_v,
\qquad a_k=(A_{k1},\ldots,A_{kt}).
\tag{1}
\]

Every row and every column of A sums to zero. Identify the two-bit color space with F₄, so multiplication by its nonzero elements gives the three cyclic permutations of its nonzero colors. In particular, regard each aₖ as a vector in F₄ᵗ.

**Five component theorem.** If the rows of A have rank at least two over F₄, then G has a five-layer cycle double cover with F itself as one whole layer. Starting from the given f, it suffices to multiply q by a nonzero scalar independently on each Kₖ, then recolor the F-edges by integrating their demands with a freely chosen constant on each circuit.

A layer is an even subgraph and may contain several circuits. The theorem makes no assertion about a sequence of moves with nonincreasing potential. Its rank hypothesis concerns the displayed boundary table for a witnessing flow, not an ordinary incidence matrix of G.

The proof below distinguishes the two ranks carefully. Binary rank controls circuit-offset solvability. Rank over F₄ controls which binary spans can meet after component rotations.

## Two tools from the preceding proof

Choose nonzero scalars tₖ on the components of H and put a′ₖ=tₖaₖ. The transformed demands close around all circuits exactly when

\[
\sum_k a'_k=0.
\tag{2}
\]

For such a choice, integrate from constant zero around each circuit, and let bₖ be the parity of zero-colored F-edges across δ(Kₖ). Their total is zero. Changing the starting constants sⱼ changes these bits by

\[
b_k(s)=b_k+\sum_j\omega(s_j,A'_{kj}),
\qquad \omega(x,y)=x_1y_2+x_2y_1.
\tag{3}
\]

The offset map has binary rank equal to the binary rank of its boundary rows. Thus the offsets remove all obstructions if and only if every binary dependency among the a′ₖ is also a dependency among the bₖ. In particular, binary rank four suffices: the total sum is then the only nonzero dependency. These facts are proved in [Four component completion](four-component-completion.md#circuit-constants-give-a-linear-completion-problem).

The second tool concerns a partition into groups whose row sums are separately zero. A common scalar on each group preserves (2). If each group's only internal dependency is its full sum, and the spans of different groups stay independent under all their scalar choices, then the grouped balancing argument supplies scalars and offsets making every obstruction zero. This uses the three-state parity lemma, as explained in the [grouped construction](four-component-completion.md#recoloring-groups-of-components). The selection lemma is already stated in [Ulyanov, Lemma 3.2](https://arxiv.org/html/2607.13225v1#S3); its graph application is developed in the preceding reports.

For a partition into two zero-sum groups P and Q, the aggregate obstruction on P, with scalars a on P and b on Q, is a bilinear function Bₚ(a,b) of the two-bit scalar parameters. Its three-by-three table on nonzero scalars has zero sum in every row and column. The aggregate on Q is the same. This calculation uses zero boundary sum on every circuit for each group, including when a group contains several H-components.

## The exceptional pattern can always be completed

First handle the following five boundary rows:

\[
x,\ x,\ x,\ y,\ x+y,
\tag{4}
\]

where x and y are independent over F₄. The conclusion in this section uses no further assumption on the circuit words that produce these rows.

Choose any pair P from the first three indices; let Q be the other three indices. Both groups have zero row sum. For scalars a on P and b on Q with a≠b, the transformed rows have binary rank three. Indeed ax and bx are independent binary vectors on the F₄-line of x, while by is outside that line. The two group sums are therefore the complete set of independent dependencies.

If any one of the three pair choices has Bₚ(a,b)=0 for unequal nonzero a,b, the two aggregate obstruction bits vanish. The offset criterion then removes all individual obstructions.

Suppose no pair choice has such an off-diagonal zero. For each pair, every off-diagonal entry of its table is one. Zero row sums force all diagonal entries to be zero. Use the same scalar, say 1, on all five components. The three pair sums among the first three obstruction bits all vanish, so

\[
b_1=b_2=b_3=u.
\]

Since the total obstruction is zero, b₄+b₅=u. Hence the vector has the form

\[
b=(u,u,u,v,u+v).
\tag{5}
\]

This is exactly the image of the offset map for the rows (4). The two linear functionals defined by pairing with x and y are independent over F₂, so their values u and v can be chosen arbitrarily. Offsets therefore cancel (5).

Both alternatives give a completion. The second alternative is essential: the graph example below has no successful rank-three rotation assignment.

## Classification of all five row systems of field rank at least two

Let r be the binary rank of the five rows. Their sum is zero, so r≤4. Their F₄-rank is at least two, so r≥2.

### Binary rank four

Equation (3) already supplies the offsets. No rotation is needed.

### Binary rank three

The binary dependency space has dimension two. Any proper nonzero dependency partitions the five rows into two zero-sum groups. Each group is minimally dependent: a further proper dependency within one group would raise the total nullity. The group sizes are either 1 and 4, or 2 and 3.

The 1 and 4 case consists of one zero row and a minimally dependent four-row group. Their spans remain independent under all group rotations, so the grouped construction applies.

In the 2 and 3 case, write the rows as

\[
x,x,y,z,y+z,
\tag{6}
\]

with y,z binary independent and x outside their binary plane W. If neither nontrivial scalar multiple of x lies in W, the pair and triple spans stay independent under every relative rotation. The grouped construction again applies.

Otherwise exactly one nontrivial scalar multiple of x belongs to W. There cannot be two: their sum would be x, contradicting x∉W. Rotate the pair so its repeated row becomes that vector v∈W. Because the nonzero vectors of W are y,z,y+z, the resulting multiset is

\[
v,v,v,w,v+w.
\]

Here v and w are independent over F₄. If they lay on one F₄-line, W would equal that line and would contain the original x, again a contradiction. Closure is preserved by the pair rotation. The exceptional-pattern argument therefore applies.

### Binary rank two

Let x,y be a binary basis for the rows. They must be independent over F₄, since otherwise all rows would have F₄-rank one. The possible nonzero rows are x,y,x+y.

The zero total sum says that the three multiplicities have the same parity. With five rows in total and rank two, this gives exactly the following patterns, up to ordering and renaming the basis:

| Rows | Completion |
|---|---|
| x,y,x+y,0,0 | A triple group and two zero singleton groups |
| x,x,y,y,0 | Two pair groups and one zero singleton group |
| x,x,x,y,x+y | The exceptional-pattern argument |

The pair spans in the second row remain independent because x and y are independent over F₄. Thus the first two patterns satisfy the grouped construction. This exhausts all possible ranks and proves the theorem. □

## A graph where larger boundary rank prevents completion

An explicit simple cubic graph on 16 vertices realizes the exceptional boundary rows

\[
a_1=a_2=a_3=x=(1,2,3),\qquad a_4=y=(1,1,0),\qquad a_5=x+y=(0,3,3).
\]

Its prescribed F consists of circuits

```text
0 1 2 3 0
4 5 6 7 8 4
9 10 11 12 9
```

The five H-components are the stars centered at 13, 14, and 15, with respective leaf sets {0,4,9}, {1,5,11}, and {2,8,10}, and the two edges {3,6} and {7,12}. Color each star's edge to the first, second, and third F-circuit by 1,2,3 respectively. Color {3,6} by 1 and {7,12} by 3.

Of the 243 component rotation assignments, 21 satisfy closure. Their outcomes are:

| Boundary binary rank | Closed assignments | Assignments admitting offsets |
|---|---:|---:|
| 3 | 18 | 0 |
| 2 | 3 | 3 |

There is no successful assignment with all circuit constants zero. With unchanged component colors, the initial obstruction is (1,1,1,0,1). Constants (0,1,0) remove it. Each of the three successful rotation assignments admits 16 choices of constants, giving 48 successful rotation-and-offset pairs.

Direct enumeration of all 21·4³=1,344 closed rotation-and-offset pairs confirms the counts without solving the offset system. A decoded five-layer cover is stored in the results. Thus a strategy that insists on maximizing boundary rank before solving the parity equations can reject a valid completion.

## What the remaining failures say about layer selection

Rank zero is already handled by balanced completion. Combined with the present theorem, this proves a necessary condition for a prescribed F with five complement components to have no completion: **every** nowhere-zero three-bit flow with first support F must produce a boundary matrix of F₄-rank one.

It is not enough to require three circuits in F. The earlier census contains six failed prescribed supports with three circuits and five complement components, on two 16-vertex graphs. An independent enumeration here checks 1,572,864 two-bit flows across these six supports. Exactly 76,800 are admissible. All are obstructed, and all 1,200 distinct restrictions to H have boundary rank one. For the saved representatives, the first boundary column is zero and the other two are equal. These are genuine prescribed-layer failures, while the graphs themselves have five-layer covers with other choices of F.

For two circuits, every row has the form (d,d), so F₄-rank at most one is automatic. The new rank condition therefore addresses interactions among at least three circuits; it does not bypass Petersen's two-factor obstruction.

The remaining existence step is now sharper: choose F and a witnessing coloring whose complement has at most four components, or five components with boundary rank zero or at least two; alternatively, solve appropriate rank-one or larger-component cases. No universal way to make this choice is established here.

## Verification and reproduction

The constructor follows the proof's cases. It does not simply exhaust all rotations and call a successful search a proof. The general result rests on the case argument above; the finite checks audit the classification, construction, and decoding.

| Check | Scope and result |
|---|---|
| Boundary tables | All 65,536 five-by-three F₄ tables with zero row and column sums; 64,260 satisfy the rank hypothesis and are classified |
| Independent rank calculation | Every table checked both by binary span expansion and direct Gaussian elimination over F₄ |
| Circuit words | 6,000 seeded systems with two through six circuits; all 4,821 in the theorem's scope completed |
| Inputs outside the rank hypothesis | Of 1,179 tested word systems, 1,177 completed and two failed; neither outcome is generalized |
| Actual graph constructions | 144 instances on 16 vertices and 576 on 18 vertices; all 720 completed, including 56 requiring the common-state fallback |
| Independent offset enumeration | Four saved graph examples checked by all 1,344 closed rotation-and-offset pairs each |
| Earlier failed supports | All six saved three-circuit, five-component failures independently checked; all admissible boundary colorings have F₄-rank one |

The graph instances vary circuit orders in two specified constructions. They may include isomorphic or identically labeled duplicates and are not a census of all graphs of those orders. The artificial word systems test the algebra; no claim is made that every such system is realized by a cubic graph. All constructed graphs were checked to be simple, connected, bridgeless, and cubic. Every output cover was checked by exact edge multiplicity, even degrees, and equality of its fifth layer with F.

The table classification counts are 20,160 full binary rank, 31,500 stable group partitions, 1,800 initial exceptional patterns, 10,800 patterns normalized to an exceptional pattern, and 1,276 outside the rank hypothesis. These numbers concern the finite five-by-three audit. The mathematical classification allows arbitrary t.

```bash
python3 research/five-cdc-attempt/five_component_completion.py
```

The [implementation](five_component_completion.py) and [saved results](five_component_completion_results.json) include the proof cases, starting flows, component rotations, circuit constants, and verified covers. This continuation narrows a conditional obstruction; it does not prove the general conjecture.
