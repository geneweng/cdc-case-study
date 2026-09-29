# Balanced boundary colors: a conditional existence proof

**29 September 2026. The general 5-cycle double cover conjecture is not proved here.**

**Further result:** [Four component completion](four-component-completion.md) proves the previously experimental conclusion for admissible first coordinates with at most four complement components, without requiring entrywise balance. It uses independent circuit constants in addition to component rotations and shows that the bound is sharp for prescribed layers.

This continuation replaces the requirement to repair every starting flow by a sufficient condition for constructing one successful flow. A three-state parity argument proves that an admissible first coordinate can be completed whenever its boundary colors balance separately on every circuit and every component of its complement. In particular, the balance condition is automatic for a first coordinate consisting of one circuit.

The restriction to one circuit cannot settle all graphs directly: an explicit 32-vertex bridgeless simple cubic graph has no admissible single-circuit first coordinate, although it has a verified five-layer cover. The missing step concerns multiple circuits and the coupling between their boundary sums.

These deductions are supplied with proofs and reproducible checks, without a claim of novelty over the complete literature. The parity lemma used below is already stated in Ulyanov's July 2026 preprint. The graph application is derived explicitly here; no reliance is placed on that preprint's claimed Lean verification. [Ulyanov, Lemma 3.2](https://arxiv.org/html/2607.13225v1#S3)

## 1. The condition

Let G be a connected loopless cubic graph, let F be a nonempty binary even subgraph, and write its circuit components as C₁,…,Cₜ. Let K₁,…,Kₕ be the components of H=G−E(F).

Start with a nowhere-zero binary 3-flow written as

\[
f=(F,q),\qquad q:E(G)\longrightarrow\mathbb F_2^2.
\]

Here q is a flow and is nonzero on H; it may be zero on F. At a vertex v of F, let d_v be the q-value of its unique incident H-edge. Thus d_v≠0. At every other vertex, the three H-edge colors are the three distinct nonzero elements of F₂².

Define the boundary-sum table

\[
A_{kj}=\sum_{v\in V(K_k)\cap V(C_j)}d_v\in\mathbb F_2^2.
\tag{1}
\]

Every row sum and every column sum of A is zero. For a row, sum conservation over the degree-three vertices of Kₖ; internal edge contributions cancel, leaving its leaf colors. For a column, sum conservation around Cⱼ; the two occurrences of each circuit-edge color cancel.

**Balanced completion theorem.** If every entry Aₖⱼ is zero, there is a five-layer cycle double cover having F itself as one whole layer. More specifically, one can cyclically permute the three nonzero q-colors independently in each Kₖ, then recolor the F-edges, so that all the canonical lift obstructions vanish.

The theorem permits both F and H to be disconnected. It does not assert that the boundary table can always be made zero.

## 2. The parity tool

Use the following form of the cited three-state lemma. Let Ω=F₂²∖{0}. For every unordered pair {k,l}, take a bilinear function Bₖₗ: F₂²×F₂²→F₂, with the convention Bₗₖ(b,a)=Bₖₗ(a,b). There are an odd number of assignments aₖ∈Ω satisfying

\[
\sum_{l\ne k}B_{kl}(a_k,a_l)=0\quad\text{for every }k.
\tag{2}
\]

In particular, an assignment exists. Bilinearity gives the required zero sum over each three-element argument set. A short parity proof expands the indicator product for (2). Terms with a variable in only one factor sum to zero. The surviving terms are directed cycle covers: two-cycles sum to zero, and cycles of length at least three cancel with their reversals. Only the empty term remains, with parity one. This is an existence argument, not an efficient search bound.

## 3. Proof of balanced completion

Write

\[
\omega(x,y)=x_1y_2+x_2y_1,
\qquad R(x_1,x_2)=(x_2,x_1+x_2).
\]

The three invertible maps I,R,R² sum to zero and preserve ω. Choosing one of them is a three-state choice. They can also be parameterized as a₁I+a₂R for a∈Ω, which makes each transformed color linear in the state parameter.

For each component Kₖ choose Tₖ∈{I,R,R²}, and apply Tₖ to all its H-edge colors. The H-colors stay nonzero, and conservation remains true at vertices outside F. Write d′ᵥ=Tₖdᵥ when v∈Kₖ.

Order each circuit Cⱼ cyclically as v₀,…,vₛ₋₁. Give its outgoing edge at vᵢ the color

\[
p_i=\sum_{a=0}^{i}d'_{v_a},\qquad p_{-1}=0.
\tag{3}
\]

The balance hypothesis makes the sum of the d′ values on each circuit zero, for **every** independent choice of the Tₖ. Consequently (3) closes around each circuit and satisfies conservation at its vertices. Combining this q′ with F gives a nowhere-zero 3-flow: H-colors are nonzero and F-edges have first coordinate one.

It remains to choose the Tₖ so that the lift succeeds. Let bₖ be the parity of the zero-colored F-edges across δ(Kₖ). As in the earlier cut criterion, these bₖ are exactly the obstruction bits for the first-coordinate normal. If an F-edge has both ends in Kₖ, counting it twice has no effect.

For p∈F₂² and nonzero d, direct expansion of the indicator of zero gives

\[
\mathbf1_{p=0}+\mathbf1_{p+d=0}=1+\omega(p,d).
\tag{4}
\]

Sum (4) at the circuit vertices belonging to Kₖ, using the strict prefix sum in (3). On one circuit, terms involving two positions from Kₖ, together with the constant terms, cancel. To see this, let n₁,n₂,n₃ be the parities of its three nonzero d′-color counts. Their sum as vectors is zero, so n₁=n₂=n₃=p. The parity of the number of these positions is p, while their unordered pair sum under ω is n₁n₂+n₁n₃+n₂n₃=p.

Only interactions between different components remain:

\[
b_k=\sum_{l\ne k} B_{kl}(T_k,T_l),\qquad
B_{kl}=\sum_j\ \sum_{\substack{v_i\in K_k\cap C_j,\ v_a\in K_l\cap C_j\\a<i}}
\omega(T_kd_{v_i},T_ld_{v_a}).
\tag{5}
\]

These interactions are bilinear in the state parameters. They are reciprocal: Bₖₗ(Tₖ,Tₗ)+Bₗₖ(Tₗ,Tₖ) is, on each Cⱼ,

\[
\omega\!\left(T_k\sum_{v\in K_k\cap C_j}d_v,
              T_l\sum_{v\in K_l\cap C_j}d_v\right)=0.
\]

They therefore satisfy (2). Choose a balanced state assignment, obtaining bₖ=0 for every k. The extra binary coordinate then exists by the [proved cut-completion criterion](attempt.md#2-the-obstruction-can-be-read-on-cuts), and its decoding gives five even layers with exact double coverage. The layer indexed by the fifth label is exactly F. □

### Consequences and known overlap

If F consists of one circuit, the row-sum condition already says every Aₖ₁=0. Thus:

**Single-circuit criterion.** For a circuit C in a loopless cubic graph, the following are equivalent:

1. C is an entire layer of a five-layer CDC.
2. G−E(C) admits a proper three-edge-coloring.
3. G/E(C) admits a nowhere-zero F₂²-flow.
4. Some nowhere-zero F₂³-flow has C as its first-coordinate support.

For (1)⇒(4), use the five-label projection and take C as the fifth layer. Restricting the other two coordinates gives (4)⇒(2). For (2)⇒(4), integrate the leaf demands around C as in (3); their total is zero by conservation in the complement components. The theorem gives (4)⇒(1). Finally, restricting and extending flows across the contracted circuit gives (3)⇔(4). Possible loops and parallel edges created by contraction are retained; loops impose no conservation constraint.

If instead H is connected, its single row and the column-sum identities again give A=0. The nonseparating-even-subgraph sufficient condition is already Theorem 3.1 of Hoffmann-Ostenhof, Zhang and Zhang (2019); this work recovers it in the present coordinates. [*Cycle double covers and non-separating cycles*](https://par.nsf.gov/servlets/purl/10144215)

Neither connectedness condition supplies the initial two-bit coloring by itself. For example, expand one vertex of the Petersen graph into a triangle and prescribe that triangle as F. Its complement is connected, but contracting F gives Petersen, which has no nowhere-zero 4-flow. That F is not admissible.

## 4. The precise difficulty with several circuits

For a general admissible input, A need only have zero row and column sums; its individual entries can be nonzero. Independent component rotations then have to satisfy the additional closure equations

\[
\sum_k T_kA_{kj}=0\qquad\text{for every circuit }C_j.
\tag{6}
\]

The three-state parity lemma chooses states in the full Cartesian product. It gives no guarantee after imposing (6). The cancellation of the within-component terms in the proof also used the stronger, entrywise balance condition.

For the Petersen graph with F equal to its two pentagons, each complement component is a matching edge. It meets each pentagon at exactly one vertex, so each row of A has the form (d,d), d≠0. No proper coloring makes A entrywise zero. This agrees with the already proved failure of those prescribed two-factor layers.

This identifies a concrete next target: handle the coupled closure equations and parity conditions together, or change F so that a balanced configuration exists. It is not justified to discard the closure equations or to extrapolate the parity lemma to their solution set.

## 5. Why choosing one circuit cannot handle every graph

Construct G on 32 vertices as follows. Take two vertices u,v and three disjoint copies of Petersen with one edge ab deleted in each. In each copy connect a to u and b to v. This is a simple connected bridgeless cubic graph.

Every circuit either lies in one copy, or passes through u and v using exactly two copies. It therefore misses an entire third copy, including its two connector edges.

Suppose a nowhere-zero 3-flow had this circuit as first-coordinate support. Its other two coordinates would be nowhere-zero throughout the untouched copy and both connectors. Summing conservation over the copy makes the two connector values equal. Restoring the deleted edge with that common nonzero value would give Petersen a nowhere-zero 4-flow, a contradiction.

Thus **no circuit of this graph is an admissible first coordinate**. Nevertheless, G has a five-layer cover: start with a three-layer cover of the two-vertex graph with three parallel edges, take a five-layer Petersen cover for each inserted copy, and permute its labels so the removed edge's pair agrees with the corresponding original edge's pair. Give both connectors that pair. All vertex parities and edge multiplicities are preserved.

The [saved certificate](completion_certificates.json) includes the 32-vertex edge list and the actual five-layer cover. Independent simple-path DFS enumerates all **2,439 circuits** and checks that each misses a branch. The example has two-edge cuts, so it does not rule out a strategy that first reduces to graphs with larger cyclic edge-connectivity.

## 6. An exact odd-cut certificate for failed completion

There is also a graph interpretation of the earlier linear solver's negative answers. Fix two binary cycles F,y, put H=G−E(F), and R=E∖(F∪y). A third cycle z must contain R and satisfy

\[
\sum_{e\in\delta(K)} y_ez_e=0
\quad\text{for each component }K\text{ of }H.
\]

**Dual certificate.** This system is inconsistent if and only if there exist a vertex set U with odd cardinality and a set S that is a union of components of H such that

\[
\delta(U)\cap(F\cup y)=\delta(S)\cap y.
\tag{7}
\]

All sets in (7) are edge sets. This gives a directly checkable graph certificate, without depending on elimination row numbers.

**Proof.** A linear combination of incidence rows is δ(U). A combination of the component-isotropy rows is δ(S)∩y. Their sum can be canceled by forced-coordinate rows exactly when it is supported in R, which is (7). The resulting right-hand side is |δ(U)∩R| modulo two. Because y is a cycle, |δ(S)∩y| is even. In a cubic graph |δ(U)|≡|U| modulo two, so under (7) the right-hand side equals |U| modulo two. Thus an odd U gives 0=1. Conversely, every inconsistent binary linear system has such a row-combination certificate, yielding U,S of the stated kind. □

Taking S empty includes ordinary failures to extend the forced set R to a cycle. Nonempty component unions can certify the additional isotropy obstruction even when an ordinary nowhere-zero three-bit completion exists.

## 7. Finite checks and their scope

The first-coordinate census covers all **4,461** connected bridgeless simple cubic graphs through 16 vertices, plus the two previously specified 18-vertex and six 20-vertex snarks. It enumerates **97,572,378** flow classes under GL(3,2), and classifies every binary first-coordinate support on those graphs.

| Quantity | Count |
|---|---:|
| Graphs | 4,469 |
| First-coordinate supports, including empty | 2,132,424 |
| Admissible supports | 2,132,185 |
| Supports admitting a five-layer completion | 2,130,736 |
| Admissible supports with no completion | 1,449 |
| Nonseparating supports admitting completion | 126,142 |

All 1,449 failed admissible supports have at least two circuit components and at least five complement components. Every graph in this census has a successful nonseparating support; empty supports are allowed for three-edge-colorable graphs. These last observations are finite evidence, not universal assertions. In particular, the computation does not prove that an admissible support with at most four complement components always succeeds.

The flow-class weights are checked explicitly. Each rank-three class contributes 24 labeled flows for each of its seven normal choices. A rank-two class contributes six per normal, with repeated first-coordinate supports included; this gives its correct total of 42 labeled flows. All subspace enumeration counts match Gaussian binomial coefficients, and all graph flow counts match earlier independent census records. The cube and Petersen completion counts also match the earlier direct pair enumeration.

The constructor checks all **7,905** distinct balanced complement colorings arising on four specified small graphs: K₄, the cube, Petersen, and a two-edge sum of two K₄s. Across them, all **393,561** component-rotation assignments satisfy the predicted interaction equations. For each input coloring, one successful assignment is separately decoded and its cover verified. An additional ten-vertex example has two circuits in F and three complement components; exactly three of its 27 assignments eliminate the obstruction, starting from defect two.

The abstract parity test exhausts all 16 bilinear interaction systems on two variables and all 4,096 on three variables, then checks 40 seeded systems at each of four, five and six variables. The general lemma is justified by proof, not these finite tests.

Finally, the independent odd-cut test agrees with Gaussian elimination on all **5,120** pairs (F,y) for Petersen and the cube. Of the failures, 1,650 on Petersen and 186 on the cube admit an ordinary third-coordinate completion but fail the additional isotropy equations.

Data: [first-coordinate census](first_coordinate_census.json), [balanced construction checks](balanced_completion_results.json), [dual and 32-vertex certificates](completion_certificates.json).

## Reproduction

```bash
python3 research/five-cdc-attempt/first_coordinate_census.py
python3 research/five-cdc-attempt/balanced_completion.py
python3 research/five-cdc-attempt/completion_certificates.py
```

The census requires a C++17 compiler and reads the graph inputs from the earlier saved complete censuses; it does not regenerate their graph sets. The recorded run took about 127 seconds. The Python dependencies are unchanged. No general 5-CDC theorem, new graph-census bound for the original conjecture, or polynomial-time algorithm is claimed.
