# A four-flow criterion removes the quotient-cover search

**30 September 2026. The general 5-cycle double cover conjecture remains unproved here.** The preceding reduction left a prescribed-layer cover problem on the graph obtained by contracting the Petersen pieces. For both blowups and semiblowups, a four-flow gives an explicit solution to that quotient problem for **every even subgraph**, and its existence has an exact characterization in the original graph.

Let S be a connected simple cubic graph, let D be a nonempty union of vertex-disjoint cycles, and put q=|V(D)|. Let X be either Blowup(S,D) or SemiBlowup(S,D), and let H be obtained from X by contracting each of its q Petersen four-poles. Put K=S/E(D), deleting the selected cycle edges after contraction but retaining all other edges, including loops and parallel edges.

**Four-flow quotient theorem.** H has a nowhere-zero F₂²-flow if and only if K does. If this condition holds, then, for **every** nowhere-zero F₂³-flow f on X and **every chosen** nonzero functional ℓ, at most **2q internal pentagon switches** produce a flow g whose ℓ-support is a whole layer of a five-layer cycle double cover. Every flow value outside the piece interiors remains fixed.

The output cover has a further property: its fifth label is absent outside the Petersen interiors. That layer is a vertex-disjoint union of at most q circuits, each of length 5, 6, or 8. The selected-coordinate layer and this additional layer are different named layers.

This replaces a separate quotient-cover search with a construction whenever K has a four-flow. In particular it applies to every prism with one rim selected, of any length k≥3, giving a bound of 2k moves. On the earlier 72m-vertex family this is a **12m bound for every starting flow and every chosen normal**. The sharper exact m bound from the previous report still applies to its particular obstructed starting flow. Different chosen normals may require different resulting flows.

The graph constructions are Hägglund's, using his Petersen four-pole and attachment conventions. They are not new graph families. [Hägglund, *On snarks that are far from being 3-edge colorable*, Constructions 1–2](https://arxiv.org/html/1203.2015v1#S2)

**Continuation:** [Triangle quotient reduction](triangle-quotient-reduction.md) handles the explicit Petersen contraction even though it has no four-flow. It gives an exact prescribed-layer and circuit-repair reduction to the cubic core, classifies every Petersen-core flow, and constructs larger examples where all seven coordinates survive every internal repair until a core edge changes.

## 1. A four-flow completes every prescribed even subgraph

Let h be a nowhere-zero F₂²-flow on any finite graph H. Loops are allowed and count twice in vertex parity. For the three nonzero linear functionals λ on F₂², put

\[
C_\lambda=\{e:\lambda(h(e))=1\}.
\]

Each Cλ is even. A nonzero two-bit vector has value one under exactly two of the three functionals, so these three layers cover every edge exactly twice.

Now let F be **any** even subgraph of H. The four layers

\[
F,\qquad C_1\mathbin\triangle F,\qquad
C_2\mathbin\triangle F,\qquad C_3\mathbin\triangle F
\tag{1}
\]

form a four-layer CDC with F as a whole layer. An edge outside F remains in two old layers. An edge in F belongs to just one of the three toggled layers and to F itself. Symmetric difference preserves evenness.

This elementary identity does not require F to be a single circuit, spanning, connected, or a coordinate of h. It is valid at the degree-four vertices of H; a layer may have degree four there. Empty layers are allowed. Adding an empty fifth layer gives a five-layer cover with label 4 unused everywhere on H.

For completeness, the existence of a four-layer CDC is itself equivalent to a four-flow. Name its four layers by the four distinct elements of F₂², and assign each edge the sum of its two layer names. Distinct names give a nonzero value, and even layer degrees give flow conservation. Consequently, having a five-layer completion for **every even F including F=∅** is equivalent to having a four-flow. This observation does not say that a particular nonempty F requires a four-flow to have a five-layer completion.

## 2. The exact quotient four-flow condition

Write a selected cycle as v₀,…,vₖ₋₁, with piece Bᵢ attached between junctions i and i+1. In each piece use port order (a₁,a₂,b₁,b₂), as in the [joint-boundary theorem](joint-boundary-completion.md). Let rᵢ be the value of the one original edge at vᵢ outside D.

For a prospective four-flow on H, let hᵢ be the sum of the two port values from Bᵢ toward either neighboring junction. These sums agree because Bᵢ is now one degree-four vertex. The charges hᵢ may be zero even though all edge values must be nonzero.

At junction i, the four port values in the order

\[
(a,b,c,d)=(a_1^{i-1},a_2^{i-1},b_1^i,b_2^i)
\]

have charges L=a+b=hᵢ₋₁ and R=c+d=hᵢ. In a blowup the two attachment edges to vᵢ have values x=a+c and y=b+d. Thus

\[
r_i=x+y=L+R.
\tag{2}
\]

In a semiblowup, b and d are the same joining edge, so b=d and again rᵢ=a+c=L+R.

Every ordered pair of **different** charges L,R∈F₂² can be realized with all actual edge values nonzero, in either construction. It suffices to display two representatives for each construction; invertible linear maps permute the three nonzero colors, and exchanging left and right covers the other cases.

| Construction | L | R | a | b | c | d | x | y | r |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Blowup | 0 | 1 | 1 | 1 | 2 | 3 | 3 | 2 | 1 |
| Blowup | 1 | 2 | 2 | 3 | 3 | 1 | 1 | 2 | 3 |
| Semiblowup | 0 | 1 | 2 | 2 | 3 | 2 | — | — | 1 |
| Semiblowup | 1 | 2 | 2 | 3 | 1 | 3 | — | — | 3 |

Here addition is XOR on the integer encodings 0,1,2,3. The table is an analytic local existence proof. Exhaustive checks additionally find exactly two realizations per ordered unequal charge pair for blowups, and two for semiblowups when one charge is zero, one when both are nonzero: 24 and 18 assignments respectively.

**Necessity.** A four-flow on H restricts to nonzero values on the original edges outside D. At an unchanged vertex these conserve flow. Summing conservation over the region corresponding to one selected cycle gives ∑ᵢrᵢ=0, also directly obtained by summing (2). This is precisely conservation at the contracted vertex of K. An original chord of a selected cycle becomes a loop and contributes twice, hence zero, as required. Thus the restricted values give a four-flow on K.

**Sufficiency.** Start with any four-flow on K and retain its values on all original edges outside D. On each selected cycle choose an arbitrary initial charge, say hₖ₋₁=0, and integrate

\[
h_i=h_{i-1}+r_i.
\tag{3}
\]

Conservation at the corresponding vertex of K gives ∑ᵢrᵢ=0, so the charges close around the cycle. Since rᵢ≠0, adjacent charges differ. At each junction independently select a nonzero local realization from the table and its symmetries. At a contracted piece, the two pairs have the same charge hᵢ, so its four incident values sum to zero. All cubic junction equations and all unchanged vertex equations hold. In a semiblowup the directly joined ports have the same value by construction. This yields a nowhere-zero four-flow on H. □

No four-flow through the uncontracted Petersen piece is asserted. Indeed, the blowup graphs can be snarks even though H has a four-flow.

## 3. Prescribed-coordinate repair for every starting flow

Let E₀ be the edges of X outside the Petersen interiors, which are exactly the edges retained in H. Start with any nowhere-zero F₂³-flow f on X and choose ℓ≠0. The projected support

\[
\bar F=\{e\in E_0:\ell(f(e))=1\}
\]

is even on H by summed conservation in each piece. Its membership need not come from the separately constructed four-flow h.

Use h and F̄ in (1), with F̄ named label 0 and an empty label 4. This produces an explicit five-label quotient cover. The [joint extension and repair theorem](joint-boundary-completion.md#2-the-exact-local-extension-theorem) now supplies at most two internal pentagon switches per piece, preserving its four three-bit port values and the chosen quotient cover pairs. Choices in different pieces glue, including across direct joins in a semiblowup. The resulting cover of X contains the ℓ-support of the repaired flow as label 0.

Because label 4 never appears on E₀, it lies entirely inside the pieces. The seven nonempty binary even subgraphs of the internal Petersen four-pole are its four pentagons, two six-cycles, and one eight-cycle. Thus label 4 has the stated form. It can become nonempty inside a piece even though it was empty on the quotient; the final cover need not be a four-layer cover of X.

Given a four-flow on K, the construction takes linear time in the size of the graph when the fixed local repair tables are precomputed. The bound is a sufficient repair bound, not a claim that this algorithm minimizes the total number of moves. It preserves the chosen coordinate **on E₀**, not its original support inside the pieces. It also does not impose monotonicity of the earlier palette-dependent defect potential.

There is an additional extension statement without an initial flow: every even subgraph F̄ of H is the restriction of a whole layer in a five-layer cover of X. Apply (1) and then the unconditional Petersen boundary extension theorem. When a starting flow is supplied, the repair theorem realizes this extension while preserving its exact exterior values.

## 4. Explicit sufficient classes and a genuine limitation

**Prisms with one rim selected.** For S=Cₖ×K₂ and D one rim, K is the wheel with rim length k. Choose nonzero two-bit colors t₀,…,tₖ₋₁ with consecutive colors different cyclically. For even k alternate 1 and 2. For odd k alternate 1 and 2 on the first k−1 positions and use 3 on the last. Give rim edge i value tᵢ and spoke i value tᵢ₋₁+tᵢ. Every value is nonzero, each rim vertex conserves flow, and the spoke sum at the hub telescopes to zero.

Both prism constructions therefore satisfy the theorem for all k≥3: the blowup has 12k vertices and the semiblowup 10k, with at most 2k internal repairs for any initial flow and selected normal. For k=6m the blowup is the earlier Gₘ. The former contraction/reconfiguration argument guaranteed eventual access to some completable coordinate; the present argument fixes the selected normal and preserves every exterior flow value.

**Hamiltonian selected cycle.** If D is one Hamiltonian cycle of S, then K consists of one vertex and the remaining edges as loops. Any nonzero values on those loops give a four-flow. The result applies to both constructions with at most 2|V(S)| internal pentagons.

**An uncolorable original graph is allowed.** Take S to be Petersen and D its two pentagons. Then K has two vertices joined by five parallel edges. Values (1,1,1,2,3) sum to zero at both vertices, so they give a four-flow. The corresponding 110-vertex blowup and 90-vertex semiblowup are included in the certificates. The assumption concerns K, not three-edge colorability of S.

**The condition can fail.** Replace each vertex of Petersen by a triangle, attaching its three old incident edges at the three distinct triangle vertices. Let S be the resulting 30-vertex cubic graph and D the ten triangles. Then K is Petersen, which has no four-flow: at a cubic vertex such a flow is exactly a proper three-edge coloring, and Petersen is not three-edge-colorable. Hence the two contracted-piece quotients H also have no four-flow. The verifier exhausts all proper three-edge colorings of this explicit K and finds none.

This is a failure of the four-flow sufficient condition, not a counterexample to five-layer existence or to coordinate repair. A selected nonempty projected coordinate might still have a five-layer cover on H without a four-flow. That remaining quotient problem is not settled here.

## 5. The local two-switch bound still cannot be replaced by one

Even when the quotient cover is produced by (1), a specified local boundary can require two moves. In the established fourteen-edge ordering, use initial flow

```text
52473145361212
```

and normal 1. Give the four quotient ports four-flow values `2323`. Formula (1) produces cover boundary `0404`, using the standard pair dictionary: 0=01 and 4=12. The only possible label-0 support masks with this boundary are **5123 and 5268**.

The initial support is neither target. All fifteen valid one-switch neighbors over all seven internal circuits have support among

```text
5422, 5561, 5721, 5838, 6004, 6115.
```

Two pentagon switches suffice: add 7 on circuit mask 151, then add 5 on circuit mask 301. The final flow is `75624442661212`, and the cover word `23596679850404` has its label-0 support, mask 5123.

The verifier independently enumerates all local covers for this fixed boundary and all local flows for the fixed flow boundary. This sharpness concerns preserving the **specified quotient cover pairs**. It does not establish a 2q global lower bound when the quotient cover may be chosen differently.

## 6. Certificates and scope of verification

The [constructor](fourflow_quotient_repair.py) writes [explicit certificates](fourflow_quotient_repair.json). The [independent verifier](verify_fourflow_quotient_repair.py) imports no constructor and checks graph structure, contraction, flow conservation, circuit switches, exact exterior preservation, and actual cover-layer parity and membership.

There are **20 graph examples and 140 coordinate repairs**, with graph orders through 720 vertices. Each example checks all seven normals separately. They include both constructions on a selected K₄ triangle, a K₄ Hamiltonian cycle, two cube faces, the Petersen two-factor, and one rim of prisms of lengths 3,4,5,6,12,60. The prism blowups of lengths 6,12,60 reuse the earlier obstructed initial flow; the other initial flows come from seeded valid switches on the quotient followed by local extensions.

Eight small quotients also have complete even-subgraph censuses:

| Original graph and selected cycles | Blowup quotient supports | Semiblowup quotient supports |
|---|---:|---:|
| K₄, one triangle | 512 | 64 |
| Prism, rim length 3 | 1,024 | 128 |
| Prism, rim length 4 | 8,192 | 512 |
| Prism, rim length 5 | 65,536 | 2,048 |
| **Total** | **75,264** | **2,752** |

All **78,016** supports have their formula-generated covers checked. Completeness follows from an independently checked basis of the full cycle space. These finite checks exercise the implementation; the results for arbitrary graphs in the stated class follow from the proofs above and the prior exhaustive joint-extension theorem.

```bash
python3 research/five-cdc-attempt/fourflow_quotient_repair.py
python3 research/five-cdc-attempt/verify_fourflow_quotient_repair.py
python3 research/five-cdc-attempt/verify_joint_boundary_completion.py
```

All three commands use the Python standard library. The final command checks the general local two-switch theorem on which the repair guarantee depends. Its 2,455,920 cases are separate from the new graph certificates and support censuses.

Four-flow and reduction methods for five-cycle covers of superpositions already occur in the literature; no priority claim is made for the elementary identities or sufficient cover-existence consequences here. The contribution recorded in this checkpoint is the explicit quotient characterization combined with a quantitative, exterior-preserving repair of an arbitrary selected coordinate. [Liu–Hao–Luo–Zhang, *5-Cycle Double Covers, 4-Flows, and Catlin Reduction*, 2023](https://epubs.siam.org/doi/10.1137/22M1472425)

The next unresolved step is to handle projected coordinates on quotients with no four-flow, or find another reduction that supplies their five-layer covers. Local Petersen flexibility and the sufficient condition above do not resolve that case or the general 5-cycle double cover conjecture.

Subsequent results address one part of this gap: the [triangle reduction](triangle-quotient-reduction.md) and its [extension through cycle lengths seven](short-cycle-boundary.md) reduce prescribed-layer completion exactly to the contracted core, without assuming a core four-flow. The latter gives a linear-time test for any specified cycle-region boundary and a sharp eight-cycle failure of universal boundary preservation; the general core completion problem remains.
