# Beyond CDC: which graph problems admit a useful algebraic translation?

Research date: **29 September 2026**.

Follow-up: [A proof attempt for the 5-cycle double cover conjecture](five-cdc-attempt/attempt.md), including an exact extra-coordinate formulation, failed shortcuts, and reproducible certificates. The general conjecture is not proved by that attempt.

Continuation: [Exhaustive repair checks and alternating bilinear forms](five-cdc-attempt/continuation.md). An exact formulation makes the third flow coordinate a linear completion once the first two are chosen; the general existence step remains open.

Earlier result: [A counterexample to strict repair, and a proved triangle reduction](five-cdc-attempt/repair-obstruction.md). The proposed strictly decreasing repair rule fails on an explicit 16-vertex graph, despite all the earlier positive checks. Neutral moves escape the example and yield a verified five-layer cover. The original conjecture remains unresolved by this work.

Further result: [Neutral repair and parallel-edge reductions](five-cdc-attempt/neutral-repair.md). The completed 16-vertex census verifies nonincreasing repair for 91,351,392 flow classes; exactly four need a neutral first step. A parallel-pair normalization lemma is proved, and an explicit example identifies a limitation of lifting repair moves through that reduction. The general existence gap remains.

Further result: [Balanced boundary colors and a conditional existence proof](five-cdc-attempt/balanced-completion.md). A known three-state parity lemma completes any admissible single-circuit first coordinate, and more generally any componentwise balanced boundary coloring. A 32-vertex example shows why a single-circuit restriction cannot handle all graphs directly. The report also gives exact odd-cut certificates and a census of 2,132,424 prescribed first coordinates.

Latest result: [Four component completion for a prescribed layer](five-cdc-attempt/four-component-completion.md). Adding circuit constants turns the remaining repair into linear algebra. A proof handles every admissible first coordinate whose complement has at most four components, even with multiple circuits. The Petersen two-factor shows the bound cannot be increased to five. The general conjecture remains unproved; the missing step is selecting a suitable first coordinate or handling larger complements.

Graphs are finite. The local lifting discussion uses loopless cubic graphs; the quantitative counting conjecture below is stated for simple graphs, as in the cited counting papers.

**Yes to both questions, with a qualification: the mapping generalizes much more broadly than the proof that the resulting equations have a solution.** The most promising next conjectures are the **5-cycle double cover conjecture** and the **exponential circuit-double-cover counting conjecture**. Prescribing a circuit, imposing orientations, and constructing perfect-matching covers are further plausible directions, each with an identifiable extra obstruction.

There is already a generic mathematical framework: **local affine constraints on a graph, assembled into one linear map, with global feasibility tested by its dual obstruction space**. Cellular sheaves provide a standard language for this framework. The CDC-specific achievement is a local identity that annihilates every obstruction for a particular right-hand side. Merely translating a problem into algebra does not supply that identity.

This report separates **established results**, **elementary deductions supplied here**, and **proposed research directions**. It does not claim a proof of any remaining conjecture. “Open” means reported as open in the cited literature, with no later resolution located in this search; publication dates and limits of status verification are recorded below and in [sources.md](sources.md).

## 1. Review of the case study

I reviewed the [published domain map](https://geneweng.github.io/cdc-case-study/cdc-domain-map.html), its local HTML, and the two PDFs in this repository. The live domain-map HTML and local file have the same SHA-256 hash, recorded in [sources.md](sources.md). The discussion below follows the supplied proof and Oum's exposition, especially Sections 5–7 and 9. [Oum, v3](https://arxiv.org/abs/2607.16356v3)

The route is correctly identified:

```text
bridgeless graph
    -> reduction to cubic graphs
    -> nowhere-zero F_2^3-flow
    -> locally valid two-label edge templates
    -> affine equations making the templates agree across edges
    -> dual certificates of inconsistency
    -> a local parity identity makes every certificate vanish
    -> globally consistent labels
    -> Eulerian layers, decomposed into circuits
```

Three details matter when exporting this method.

1. **Eight layers need not mean eight individual circuits.** A k-cycle double cover, in the convention used here, consists of at most k even subgraphs. Each may contain many circuit components. A circuit is a connected 2-regular subgraph. Bounds on layers and bounds on circuits are different problems.
2. **Exact multiplicity is built into the labels.** An edge receives a two-element set, so it is covered exactly twice as an ordinary integer count. Parity alone would also permit zero or four occurrences.
3. **Dimension three is essential to this proof.** The website's explanation involving double coverage, characteristic two, and two edge endpoints captures the final cancellation. It also needs the fact that the orthogonal complement of a two-dimensional vertex-flow space in F₂³ is one-dimensional. In dimension four, the crucial local identity can fail.

For a loopless cubic graph, fix a nowhere-zero flow f:E→Γ, where Γ=F₂³. At a vertex v with incident edges e,a,b, define

\[
P_{v,e}=\{t_v+f(a),\ t_v+f(b)\}.
\]

The three local sets automatically use every label zero or twice. Choose either of a,b and call its flow value c_(v,e). Agreement at the ends of e=uv is equivalent to

\[
t_u+t_v+\varepsilon_e f(e)=d_e,
\qquad d_e=c_{u,e}+c_{v,e},\quad \varepsilon_e\in\mathbb F_2.
\tag{1}
\]

Once f is fixed, this is linear. If f is also unknown, the product ε_e f(e) is bilinear. That distinction becomes central for the open problems.

## 2. Question 1: the best remaining problems

The ranking is a judgment of **compatibility with this method**, not a prediction of how soon a conjecture will be solved.

| Priority | Problem | What can be reused | What still needs a new idea |
|---|---|---|---|
| 1 | 5-cycle double cover | The same flow and alignment equations | Choose a flow permitting only five labels |
| 1 | Exponentially many circuit double covers | Affine solution spaces, ranks, and flow families | Count distinct circuit systems after forgetting labels |
| 2 | Strong CDC: include a prescribed circuit | Append linear boundary conditions | Prove feasibility for a suitable flow; unrestricted feasibility is insufficient |
| 2 | Berge–Fulkerson | Even-subgraph covers and complements | Enforce six spanning 2-factors with exact multiplicity four |
| 3 | Orientable 5-CDC / Tutte 5-flow | Local conservation and dual obstructions | Preserve signs, nonzero values, and the five-label restriction |
| 3 | Tutte 3-flow | Incidence matrices and finite-field flows | Find a full-support kernel vector over F₃ |
| 3 | Bondy's small CDC, general graphs | Construct an initial cover | Bound the number of circuit components through graph reductions |

### 2.1. Five-cycle double covers: the closest existence problem

**Conjecture.** Every bridgeless graph has a double cover by at most five even subgraphs. The supplied exposition proves eight layers and lists five as open. A September 23, 2026 paper explicitly still describes the five-layer problem as open. [Oum, §9.2](https://arxiv.org/abs/2607.16356v3); [Zerafa](https://arxiv.org/abs/2609.28118)

Keep Γ=F₂³ and ask for all edge labels to lie in a five-element subset S. This preserves the successful three-dimensional setting. Replacing Γ by F₂² cannot settle the general problem: for cubic graphs, a four-layer CDC is equivalent to 3-edge-colorability, and the Petersen graph is not 3-edge-colorable. Replacing Γ by F₅ changes the local construction and its proof. [Oum, Theorem 19](https://arxiv.org/abs/2607.16356v3)

**A particularly useful existing extension.** Hušek–Šámal already reuse the CDC equations. Their Observation 3.15 turns restriction to S={000,001,010,011,100} into additional linear equations for a fixed flow. Theorem 3.16 gives an equivalent test: put F={e:f(e)'s first coordinate is 1}, M=f⁻¹(100), and let Z be the endpoints of M. The restriction is feasible exactly when every component of (V,E∖F) contains an even number of vertices of Z. Their Theorems 1.7–1.8 also establish the sharp counting bound below for 3-edge-colorable cubic graphs, and an exponential bound for 3-edge-connected cubic graphs of girth at least 16. [Hušek–Šámal, §§3.1–3.4](https://arxiv.org/html/2607.24724v1)

**Research direction, inferred from that criterion.** Search for a way to choose or modify f so the component parity conditions hold. For example, adding a constant vector a along a circuit preserves flow conservation; it preserves nonzero values if no modified edge originally has value a. The missing result would show how such moves, or a more flexible construction, can produce a flow meeting all required parities.

The remaining theorem concerns the existence of a suitable flow on every graph. Gaussian elimination tests each fixed flow, leaving that choice unresolved.

Our saved Petersen examples demonstrate this distinction: the unrestricted system is feasible for both flows, but the chosen five-label restriction succeeds for one and fails for the other. Failure for a fixed flow and fixed S says nothing against the graph-level conjecture; a different flow, or a different palette for the same flow, may work.

### 2.2. Counting circuit double covers: the closest quantitative problem

**Conjecture.** Every simple 2-connected cubic graph on n vertices has at least 2^(n/2−1) distinct circuit double covers. The original counting paper gives the conjecture and a family attaining the bound. [Hušek–Šámal, *Counting circuit double covers*, JGT 2025](https://doi.org/10.1002/jgt.23187)

The algebraic opportunity is immediate. A consistent binary system Ax=b with N variables and rank r has exactly 2^(N−r) solutions. Instead of proving that a solution exists, try to prove that there are many solutions and that enough of them decode to different circuit systems.

**The gap:** changing labels may leave the underlying collection of circuits unchanged. Neither eight global label translations nor arbitrary permutations of layer names should count as new circuit covers. Varying flows introduces further possible repetitions. A valid counting proof needs an injective construction or an upper bound on the number of algebraic descriptions of each circuit cover.

**Suggested target.** Extend the known subclasses by controlling short circuits and the number of labelings of the same cover. This is especially attractive because the method has already produced nontrivial results, rather than merely a reformulation.

### 2.3. Strong CDC: require a chosen circuit to occur

**Conjecture.** Given a bridgeless cubic graph G and a circuit C, there is a circuit double cover containing C. This is distinct from the strong embedding conjecture and from a five-layer cover. The precise prescribed-circuit formulation appears in [Hoffmann-Ostenhof](https://arxiv.org/abs/1209.0096). A July 2026 [author research note](https://kintali.wordpress.com/2026/07/14/ai-and-math-proofs-part-i/) still calls it open; this status is less directly documented in recent primary research papers than the five-layer problem.

**Elementary deduction from (1).** Fix a label s. At v on C, let r_v be the unique incident edge outside C. In the symmetric local construction, the common label on the two C-edges is t_v+f(r_v). Therefore append

\[
t_v=s+f(r_v)\qquad(v\in V(C)).
\tag{2}
\]

For fixed f these are linear boundary conditions. If they are compatible with (1), C is a component of the s-layer: that layer uses the two C-edges and not r_v at each vertex of C. Other disjoint components in the same layer are harmless after decomposition into circuits.

**Research direction.** Characterize the new left-nullspace certificates of the augmented system, and choose f to eliminate them. This gives a precise sufficient approach. It does not show that every prescribed circuit can occur in an eight-layer cover, which would be stronger than the unbounded-layer strong CDC conjecture. Increasing the number of labels also requires care because unrestricted alignment is no longer automatic in higher dimension.

### 2.4. Berge–Fulkerson: the best matching-related target

**Conjecture.** Every bridgeless cubic graph has six perfect matchings, with repetition allowed, such that each edge is in exactly two. Equivalently, it has six even subgraphs covering every edge exactly four times. [Oum, §9.4](https://arxiv.org/abs/2607.16356v3). Its continued role as an unresolved matching conjecture is reflected in [Zerafa, September 2026](https://arxiv.org/abs/2609.28118).

The equivalence has useful content. Complementing the matchings gives six spanning 2-factors with multiplicity four. Conversely, in a cubic graph a six-layer even 4-cover has total layer-degree 12 at each vertex. Each of six layers has degree at most two, so all six have degree exactly two. Their complements are perfect matchings.

**Elementary algebraic formulation.** Let x_(e,i)∈{0,1} indicate membership in layer i. Then require

\[
\sum_{e\ni v}x_{e,i}=2\quad\text{for every }v,i,
\qquad
\sum_{i=1}^{6}x_{e,i}=4\quad\text{for every }e.
\tag{3}
\]

These are integer equalities with binary variables. Reducing them modulo two discards the essential requirements. A CDC-style breakthrough would find a template whose decoded configurations satisfy these exact counts automatically, leaving only affine agreement constraints.

The nearby established seven-layer 4-cover is suggestive, but deleting or merging a layer is not a proof: it can destroy exact coverage. The main research challenge is **designing the local template**, before trying to imitate the final parity argument.

### 2.5. Orientable covers and Tutte's flow conjectures

An orientable five-layer CDC requires each edge to be traversed once in each direction. It implies a nowhere-zero Z₅-flow: assigning distinct coefficients to the five directed even layers gives edge values ±(i−j), which are nonzero modulo five. This implication and the orientable conjecture are recorded in [Oum, §9.3](https://arxiv.org/abs/2607.16356v3). Ordinary five-layer CDC does not supply that orientation condition.

Tutte's **5-flow conjecture** asks for a nowhere-zero 5-flow in every bridgeless graph. Tutte's **3-flow conjecture** asks for a nowhere-zero 3-flow in every 4-edge-connected graph; a September 2026 paper proves additional special cases of the latter. [Li–Li](https://arxiv.org/abs/2609.08377)

For a chosen orientation and prime p=3 or 5, the group-flow formulation is

\[
Bf=0\quad\text{over }\mathbb F_p,
\qquad f_e\ne0\quad\text{for all }e,
\tag{4}
\]

where B is the signed incidence matrix. Conservation is linear; simultaneously avoiding every coordinate hyperplane is the difficult part. Over F_p, the additional equations f_e^(p−1)=1 enforce nonzero coordinates, giving an exact polynomial encoding but not a general existence proof.

These problems fit the broad strategy of local algebra and global obstructions. They are weaker matches for the particular binary CDC identity: signs and nonzero constraints cannot simply be erased. A useful project would first identify a signed local template or a new nonvanishing argument.

### 2.6. Bondy's small CDC: a different quantity to control

The general conjecture asks for at most n−1 individual circuits in a CDC of every simple 2-edge-connected n-vertex graph. Eight even layers do not bound their total number of components. The cubic version, with at most n/2 circuits except K₄, already follows from CDC together with a previous theorem of Lai–Yu–Zhang. It should not be proposed as still open. [Oum, §9.1](https://arxiv.org/abs/2607.16356v3)

A new approach to the general version would need to control how circuit components split or merge when reversing the reductions to cubic graphs. This is a global component-count problem, so it is less directly captured by the alignment matrix.

## 3. Question 2: what general connection can be established?

### 3.1. A useful classification by the constraints that remain

| Graph requirement | Natural algebraic object | What algebra gives immediately | What it does not give automatically |
|---|---|---|---|
| Even degree at every vertex | Kernel of the binary incidence matrix | The cycle space and a basis | Exact cover multiplicities |
| Flow conservation | Kernel of a signed incidence matrix over a field/group | All flows | A nowhere-zero flow |
| Affine local choices with linear agreement | A block matrix δ and equation δx=b | Complete feasibility test, witnesses, solution count | A theorem that every graph-induced b is feasible |
| Cover each edge an exact number of times | Binary/integer incidence equations | Exact encoding | Integrality or a suitable automatic-count template |
| Restrict labels or forbid coincidences | Domain restrictions or polynomial equations | Exact finite constraint model | Affine structure or tractable search |
| A single connected circuit / few components | Degree constraints plus connectivity or component control | Some necessary local conditions | The global connectedness requirement |
| Abstract circuit systems | Binary matroids and linear codes | Cycle/cocycle duality | Graphic incidence properties or uniform layer bounds |

The most useful class for **the same proof architecture** is:

> Problems in which valid local configurations can be parameterized by affine spaces, consistency across adjacent pieces is linear, and the resulting dual obstructions admit a local cancellation law.

This is substantially more specific than “graph problems can be written with matrices.”

### 3.2. The general feasibility theorem

Give each vertex v a finite-dimensional vector space V_v and each edge e a comparison space Q_e. Give every incident pair v,e a linear map R_(v,e):V_v→Q_e. Orient e from u to v and set

\[
(\delta x)_e=R_{v,e}x_v-R_{u,e}x_u.
\]

For prescribed discrepancies b_e, the local choices fit together exactly when δx=b. Finite-dimensional duality gives

\[
\boxed{\delta x=b\text{ is solvable}
\iff \langle y,b\rangle=0\text{ for every }y\in\ker\delta^*.}
\tag{5}
\]

This is an elementary theorem over any field. Over a finite field F_q, a nonempty solution set has q^(dim C⁰−rank δ) elements, where C⁰=⊕_v V_v. The detailed proof and a sufficient local cancellation criterion are in [algebraic-framework.md](algebraic-framework.md).

For CDC, take V_v=Γ and Q_e=Γ/⟨f(e)⟩, with the quotient maps as restrictions. In characteristic two the endpoint difference becomes a sum. Equation (5) is precisely the column-space/left-nullspace step of the proof.

### 3.3. Connection to sheaves and cohomology

Vector spaces attached to graph vertices and edges, together with these restriction maps, form a **cellular sheaf**. Its degree-zero coboundary is δ. The usual definitions give H⁰=ker δ and, for a graph with no higher-dimensional cells, H¹=C¹/im δ. The general framework is established mathematics, not a new conjecture. [Hansen–Ghrist](https://doi.org/10.1007/s41468-019-00038-7)

**Our interpretation of CDC:** the discrepancy b determines a class [b] in H¹. The CDC parity identity proves that this particular class vanishes. It does not prove H¹=0.

In fact, for a connected cubic graph with n vertices and m=3n/2 edges, the CDC quotient formulation has dim C⁰=3n and dim C¹=2m=3n. Constant translations give at least three dimensions in ker δ. Rank-nullity therefore gives dim H¹=dim H⁰≥3. Nonzero obstruction classes exist; the special CDC discrepancy avoids them.

That distinction suggests a useful research program: characterize **which graph-generated discrepancies are forced to have zero obstruction class**, rather than trying to make every possible local constraint system solvable.

### 3.4. The matroid connection is real, but has sharp limits

The supplied exposition records the Jamshy–Tarsi transfer: CDC implies that every coloop-free binary matroid with no F₇* minor has a cycle double cover. In particular, this includes coloop-free regular matroids. This extends the conclusion beyond graphs. [Oum, §9.5](https://arxiv.org/abs/2607.16356v3)

It does not extend to all binary matroids. An elementary obstruction is F₇*: its seven nonempty binary cycles all have size four. A double cover would have total size 14, which cannot be a sum of fours. Nor does a fixed layer bound transfer to all regular matroids: the cographic matroid of K_n requires n layers for n≥5, as recorded in Oum using Linial–Meshulam–Tarsi.

Thus there are two distinct generalizations: a broadly valid **algebraic language**, and a more restricted **cover-existence theorem**.

## 4. What blocks an automatic generalization?

**Higher dimension.** At a cubic vertex, the three nonzero flow values span a plane. Its annihilator has dimension k−2 in F₂^k. For k=3, the zero-sum dual triple has the special parity property used by the proof. For k=4, take

\[
(p_1,p_2,p_3)=(e_1,e_2,e_1+e_2),\qquad
(h_1,h_2,h_3)=(e_3,e_4,e_3+e_4).
\]

All required pairings h_i·p_i vanish, both triples sum to zero, and all cross-pairings vanish. Yet three dual vectors are nonzero. The claimed parity identity would read 0=1.

This local failure is not by itself a graph counterexample. Our separate K₃,₃ computation supplies a global inconsistent alignment system, together with a verified linear combination of equations giving 0=1. It disproves the statement that every four-dimensional nowhere-zero flow admits the same lift; it does not dispute that K₃,₃ has a CDC.

**Extra restrictions.** Appending equations can create new infeasibility certificates. The original proof eliminates certificates for its original system, not for every augmented system.

**Exact counts versus parity.** The allowed four-bit vectors of weight exactly two are not affine: 1100, 1010, and 1001 are allowed, but their XOR is 1111. Affine subsets over F₂ are closed under XOR of three members. Since projections of affine sets are affine, simply adding existential binary variables and linear equations cannot encode this exact relation while retaining the original bits as projected coordinates. A different representation or nonlinear decoding, as in CDC, can escape this limitation.

**Other fields.** Signed incidence cancellation works over any field, but that alone does not reproduce the local CDC template. A one-dimensional affine line over F_p has p points, not two; modular degree constraints also do not automatically impose exact degrees. Replacing “two” everywhere by p is therefore not a proof of a p-cover theorem.

## 5. Reproducible checks and the next research step

The standard-library script [verify_algebra.py](verify_algebra.py) produced [verification_results.json](verification_results.json). It verifies each decoded cover's exact edge multiplicity and vertex degrees, and each inconsistency certificate by XORing the indicated original equations.

| Check performed | Result | Interpretation |
|---|---|---|
| Every admissible local flow/dual configuration in F₂³ | 336 cases; zero parity failures | Exhaustive verification of the small local identity |
| Every analogous local configuration in F₂⁴ | 6,720 cases; 1,260 failures | The dimension-three argument cannot be copied verbatim |
| Two explicit flows on the Petersen graph | Both ordinary lifts exist; one selected five-label lift fails and one succeeds | Flow/palette choice remains a substantive issue |
| One explicit F₂⁴-flow on K₃,₃ | Alignment inconsistent; dual certificate verified | Higher-dimensional universal lifting is false |
| Binary cycle space of F₇* | All seven nonzero cycle weights equal four | Arbitrary binary matroids need not have CDCs |

Reproduce from the repository root:

```bash
python3 research/verify_algebra.py > research/verification_results.json
```

The graph searches use a fixed seed and stop when examples are found. Their sample sizes are not prevalence estimates, and these finite checks do not establish an open graph theorem.

**Recommended next project:** focus on the five-layer problem and the flow-dependent component parity criterion in Section 2.1. Build a catalog of violating components on snarks; investigate which flow changes repair them without creating zero edges; then formulate and prove a structural repair lemma for a meaningful graph class. Keep the counting problem as a second track, where rank and multiplicity arguments may yield progress before a universal five-layer theorem.

For the generic theory, use the precise statement in [algebraic-framework.md](algebraic-framework.md): local affine parameterization + linear agreement + a dual cancellation identity gives a constructive existence theorem. The major discovery task is to find parameterizations and cancellation identities for new combinatorial constraints.

## 6. Status corrections that affect the research agenda

The **Petersen coloring conjecture should not be listed as an open target**: an August 2026 preprint gives explicit counterexamples with checked SAT certificates. Its failure does not refute weaker cover conjectures that it would have implied. [Putman](https://arxiv.org/abs/2608.10012)

Similarly, the cubic small-CDC consequence and the coloop-free regular-matroid CDC consequence are already accounted for by Oum. They are examples of successful transfer, not remaining conjectures.

Source dates, theorem locations, evidence limitations, and the distinction between published papers and recent preprints are collected in [sources.md](sources.md).
