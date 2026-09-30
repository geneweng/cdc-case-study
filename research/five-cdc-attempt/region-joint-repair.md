# Repairs inside full cycle regions reduce exactly to the core

**30 September 2026.** The cycle-length restriction disappears if repairs may use the **whole replacement region**, including junction edges. For either Blowup or SemiBlowup, along selected cycles of any length at least three:

> A selected coordinate can be completed after circuit switches preserving every core-edge flow value if and only if that coordinate's restriction is completable on the core. Any supplied core cover witnessing completion can be preserved by the final cover.

This strengthens the scope of the [short-cycle report](short-cycle-boundary.md) by allowing a broader class of repairs. It does not preserve the initial coordinate on junction edges, and it does not settle the still-open question in that report about keeping the entire prescribed quotient layer fixed at lengths eight and above.

The proof has two ingredients: **every compatible flow boundary and cover boundary extends jointly through a region**, and **all flows with the same core-edge values are connected by internal circuit switches**. The latter follows from explicit contractions of circuits of length two, three, and four, together with the earlier Petersen-piece preparation theorem.

The former eight-cycle obstruction becomes a useful test. On its 96-vertex Blowup and 80-vertex SemiBlowup, verified sequences of **13 and 11 switches**, respectively, now realize the *same core cover that previously failed to lift*. All core-edge flow values remain fixed at every step. These are constructive lengths, not claims of minimum distance.

The general 5-cycle double cover conjecture remains unproved here. No literature-wide novelty claim is made.

## 1. Which edges and which layer are fixed?

Use the construction and edge conventions of the [preceding reports](fourflow-quotient-repair.md). Start from a simple cubic graph S and a union D of disjoint selected cycles. Let X be Blowup(S,D) or SemiBlowup(S,D). Contract each inserted Petersen four-pole B to obtain H; contracting each full cycle region of H gives K=S/D. Nonselected edges of S survive as **core edges**, including loops created by contraction, with two incidences per loop.

Write E₀ for the edges retained in X→H. A **full region** of X consists of the Petersen pieces, junction vertices, and junction edges replacing one selected cycle. Distinct full regions meet only through core edges. Let k_j be the selected cycle lengths and q=∑k_j the number of Petersen pieces.

Given a nowhere-zero flow f:E(X)→F₂³ and a nonzero functional ℓ, the selected layer is F_ℓ={e:ℓ(f(e))=1}. A circuit switch adds a nonzero vector a on one connected circuit, with a absent from its current edge values. Every intermediate flow must remain nowhere-zero. Loops and pairs of parallel edges count as circuits of lengths one and two in the contracted multigraphs.

The preceding short-cycle theorem kept every E₀ value fixed and used switches only inside individual B pieces. The present theorem fixes **only the core-edge values**. It permits switches crossing several B pieces and junctions inside one full region. Their changes to F_ℓ there are essential to the new result.

## 2. Joint junction extension has no missing charge states

Normalize ℓ to the least-significant bit by an invertible linear change of flow coordinates. Cover pairs are two-element subsets of {0,1,2,3,4}, encoded as five-bit integers; their set is Q. Layer 0 must coincide with the normalized coordinate.

At one junction use the ordered variables a,b,c,d and exterior value r from the short-cycle report. Flow values and cover pairs satisfy the same XOR equations, but belong to different alphabets. For flow values they must be nonzero members of F₂³; for cover values they must be members of Q.

| Construction | Junction equations | Ordered representatives |
|---|---|---|
| Blowup | x=a⊕c, y=b⊕d, r=x⊕y | a,b,c,d,x,y,r |
| SemiBlowup | b=d, r=a⊕c | a,b,c,d,r |

Let p be the exterior flow value and r the exterior cover pair. Their coordinate memberships must agree: p₀=r₀. Prescribe a left **flow charge** h=a_f⊕b_f and a left **cover charge** c=a_C⊕b_C. The cover charge is an even subset of the five labels, and compatibility requires h₀=c₀. Zero charges are allowed even though individual edges have nonzero values or two labels.

**Joint junction lemma (finite verified).** Every such compatible quadruple (p,r,h,c) has a joint junction assignment, with matching distinguished membership on **every** representative edge.

There are 34 possible exterior pairs (p,r): 4·4 with distinguished bit one and 3·6 with bit zero. For each, all 64 compatible charge pairs (h,c) occur. Thus there are exactly **2,176 states per construction** and no omitted states.

| Construction | Flow assignments before matching | Cover assignments before matching | Compatible boundary/charge states realized |
|---|---:|---:|---:|
| Blowup | 1,512 | 2,160 | 2,176 of 2,176 |
| SemiBlowup | 294 | 600 | 2,176 of 2,176 |

The constructor joins the separate flow and cover tables by their distinguished membership patterns. The independent verifier instead enumerates XOR-zero triangles at the cubic junction vertices, joins complete assignments with identical membership on every edge, and rebuilds the realized state set. It also checks an explicit joint witness for every state.

Unlike the previous charge test, this table does **not** prescribe the internal membership pattern in advance. Choosing that pattern jointly is what removes the missing states.

## 3. Joint extension through a cycle of any length

Consider a length-k region with fixed exterior flow values p_i and cover pairs r_i, where

\[
p_i\ne0,\qquad r_i\in Q,\qquad (p_i)_0=(r_i)_0,
\qquad \bigoplus_i p_i=\bigoplus_i r_i=0.
\tag{1}
\]

Choose any compatible initial charges h₀,c₀, for example both zero. Propagate

\[
h_{i+1}=h_i\oplus p_i,\qquad c_{i+1}=c_i\oplus r_i.
\tag{2}
\]

Compatibility of their distinguished bits persists. Apply the joint junction lemma at i using (p_i,r_i,h_i,c_i). The resulting right charges are h_{i+1},c_{i+1}; thus both flow and cover parity hold at the next contracted B vertex. Equation (1) closes both charge sequences around the selected cycle.

This constructs a nowhere-zero flow and a five-layer cover on the region of H, agreeing on their distinguished coordinate and matching **all** supplied exterior flow values and cover pairs. The work is O(k) after the fixed junction table is computed. The initial region layer is free to change.

At each B vertex the constructed flow and cover boundaries are parity-valid and have matching memberships. The [joint Petersen completion theorem](joint-boundary-completion.md) extends them to an actual B interior, again sharing the distinguished coordinate. Hence the same joint extension statement holds for the full region of X, at every k≥3.

**Joint lifting theorem.** If f_K is a nowhere-zero three-bit flow on K and C_K is any five-layer cover whose layer 0 is ℓ(f_K), there is a lift to a flow g and cover C on X such that

\[
g|_{E(K)}=f_K,\qquad C|_{E(K)}=C_K,
\qquad C_0=\ell(g).
\tag{3}
\]

Apply the construction independently in each selected region. Unselected vertices already have their given flow and cover assignments. A general ℓ follows by changing the flow basis before construction and changing it back afterward.

The saved examples directly check joint flows and covers on 18 capped quotient regions: lengths 3,4,5,7,8,9,16,31,64 for both constructions. These are implementation checks; the all-length result follows from (1)–(2) and the exhaustive junction lemma.

## 4. An elementary short-circuit contraction lemma

Let C be a circuit of length m≤4 in a multigraph G, and contract its edges to obtain G/C. Other edges remain, including chords that become loops. Work with nowhere-zero F₂³-flows.

**Extension and fixed-boundary connectivity.** Any quotient flow extends over C. Solve its vertex equations cyclically. The values on C have the form b_e⊕t for a single t∈F₂³. At most m choices of t create a zero, so at least 8−m choices remain. Any two extensions with the same exterior values differ by one constant on all of C, and therefore by one valid circuit switch, unless already equal.

**Lifting one quotient switch.** A quotient circuit either avoids the contracted vertex or has two incidences there. In the latter case let P be a shortest path in C between the original incidence vertices. It has at most ⌊m/2⌋ edges; coincident endpoints give an empty path. A loop in the quotient is handled by its two endpoint incidences in the same way.

If the quotient increment is a, prepare C by adding t. To preserve nonzero values on C and make P avoid a, exclude

\[
t\in\{f(e):e\in C\}\ \cup\ \{f(e)\oplus a:e\in P\}.
\tag{4}
\]

There are at most m+⌊m/2⌋≤6 forbidden values, fewer than eight. Choose another t. If t=0, no preparation is needed; otherwise the switch on C is valid. Then lift the quotient circuit by replacing its passage through the contracted vertex by P. Its edges avoid a, so it is one valid circuit switch. Thus **at most one internal preparation** suffices.

Conversely, restricting a switch to retained edges gives an even edge set in the quotient. Decompose it into edge-disjoint circuits and apply the same increment to each. Every intermediate edge retains either its original or its final nonzero value. Projection therefore preserves reconfiguration components.

Together with extension and connected fibers, these arguments prove that restriction induces a **bijection between flow-reconfiguration components** of G and G/C. The proofs also hold with any set of exterior edge values fixed. No general reconfiguration-connectedness theorem is assumed.

The saved audit additionally exhausts 142,345 choices of cycle edge values, short arc, and increment for m=2,3,4, verifying that the allowed preparation set in (4) is never empty. This finite check supplements the counting proof.

## 5. Every full region has connected fixed-core flow fibers

After contracting the B pieces, all internal edges of a selected region can be eliminated by the preceding short-circuit lemma.

**SemiBlowup.** Its internal graph is a ring of k contracted B vertices, with each consecutive pair joined by a direct edge and a two-edge path through an original cycle vertex. Contract k−2 successive triangles. Two B vertices remain, with two parallel direct edges; contract that two-edge circuit. Each of the last two original cycle vertices now has a parallel pair to the merged vertex. Contract those pairs as well.

**Blowup.** At junction i the two B vertices and auxiliaries u_i,w_i form a four-cycle. Contract k−1 successive such four-cycles, merging all B vertices. Each of their original cycle vertices is now attached by a parallel pair. At the remaining junction, merge each auxiliary into the B vertex along its parallel pair, then merge its original cycle vertex along the final parallel pair.

| Construction | Four-cycle contractions | Triangle contractions | Two-edge contractions | Total r(k) |
|---|---:|---:|---:|---:|
| Blowup | k−1 | 0 | k+2 | 2k+1 |
| SemiBlowup | 0 | k−2 | 3 | k+1 |

Core edges are never contracted or switched by these internal preparations. After the contractions a region is one vertex. Fixing its core-edge values leaves a single quotient flow, so the short-circuit lemma proves that **every regional fiber in H is connected**.

The [Petersen preparation theorem](petersen-flow-repair.md) supplies the corresponding statements for X→H: all local B fibers are connected, any quotient switch lifts after at most one internal pentagon preparation per visited B, and final alignment to a specified local flow needs at most three internal circuit switches. Combining the two levels proves:

**Regional fiber theorem.** All nowhere-zero flows on X with the same core-edge values lie in one reconfiguration component using only circuits inside full regions. More generally, restriction X→K induces a bijection of flow-reconfiguration components.

The generalized statement follows by composing the component bijections for the B contractions and for the short-circuit contractions. This does not assert equality of circuit-switch distances. A full circuit can project to several core circuits, and lifting can require internal preparations.

## 6. Exact criterion for repair preserving core values

Let f be an initial nowhere-zero three-bit flow on X and fix ℓ≠0. Then

\[
\boxed{\begin{aligned}
&\ell(f|_{E(K)})\text{ is a whole layer of a five-layer cover on }K\\
&\quad\Longleftrightarrow\quad
\text{some flow reachable from }f\text{ by switches inside full regions}\\
&\hspace{112pt}\text{has a five-layer-completable }\ell\text{-coordinate.}
\end{aligned}}
\tag{5}
\]

**Proof.** For sufficiency, take a core cover and use the joint lifting theorem to obtain a successful flow g with exactly the same core values as f. The regional fiber theorem connects f to g without changing those values. For necessity, a successful final cover restricts to a core cover with the unchanged selected core coordinate, by summing each label's parity inside each region. □

Every supplied core cover can be realized by this procedure. Internal flow values, including junction values, may change. This is why (5) survives the eight-cycle fixed-layer boundary obstruction.

There is also a componentwise criterion when core values may change: the reconfiguration component of f on X contains a successful selected coordinate **if and only if** the corresponding component of f_K on K contains one. The forward direction projects a successful flow and its cover. For the reverse direction, the successful core flow has a successful joint lift, lying in the corresponding component by the component bijection. This transfers the remaining core problem; it does not solve it for arbitrary K.

### A finite but coarse switch bound

The contraction proof gives an explicit, inefficient bound. For a quotient region with r short-circuit contractions, its fixed-boundary diameter is at most 2ʳ−1: lift each move recursively in at most two switches, then align the final contracted circuit in at most one switch.

For repair with a supplied core cover, construct its target joint flow and cover on H. Reconfigure each quotient region, lift each move through at most k_j Petersen pieces, and finally use joint Petersen completion in at most two pentagons per piece. This gives

\[
\sum_j (k_j+1)\bigl(2^{r(k_j)}-1\bigr)+2q
\tag{6}
\]

as an upper bound on the number of switches. It is not a useful estimate of observed distances or an optimality claim. The certified examples below are much shorter. Establishing a sharp or polynomial regional bound remains a separate problem.

## 7. Realizing the previously rejected eight-cycle cover

Reuse exactly the graphs, initial flows, and rejected core covers from the [eight-cycle certificates](short_cycle_boundary.json). Their initial quotient supports are eight disjoint four-cycles in Blowup and four disjoint triangles in SemiBlowup, with empty core restriction. The earlier eight-charge proof excludes the specified cover as long as those whole quotient supports remain fixed.

The new constructor first builds a compatible target quotient flow and cover using the joint junction table. It then contracts short circuits and lifts a reverse reconfiguration sequence, always fixing the core edges. Quotient moves are lifted through the B pieces using the local preparation lemma. Final joint completion inside each B supplies the full cover.

| Construction | Vertices | Quotient switches | B preparations for lifting | Final B pentagons | Total full-graph switches |
|---|---:|---:|---:|---:|---:|
| Blowup | 96 | 8 | 0 | 5 | **13** |
| SemiBlowup | 80 | 5 | 4 | 2 | **11** |

The verifier checks each switch is a connected circuit, its increment is absent, all intermediate values are nonzero and conserved, and every core value stays fixed. It checks that the final quotient support differs from the initial one, the final full cover has the selected coordinate as label 0, and its core pairs equal the **originally rejected** supplied pairs.

These examples show precisely what the extra freedom buys. The obstruction to keeping the region's initial layer is real, but it does not prevent a regional repair preserving the exterior flow and the desired final exterior cover.

## 8. Reproduction and limits

From this directory:

```bash
python3 -B region_joint_repair.py
python3 -B verify_region_joint_repair.py
python3 -B verify_petersen_flow_repair.py
python3 -B verify_joint_boundary_completion.py
python3 -B verify_short_cycle_boundary.py
```

- [Constructor](region_joint_repair.py) and [certificates](region_joint_repair.json): both complete joint junction tables, 18 cap examples and contraction sequences through length 64, the short-cycle preparation audit, and the two full repairs.
- [Independent verifier](verify_region_joint_repair.py): rebuilds all 4,352 joint states from cubic-vertex triangles, checks all 142,345 short-cycle cases, and checks the actual contraction and repair certificates without importing constructors or earlier verifiers.

The remaining commands verify the prior local B lifting/completion results and the original eight-cycle obstruction and graph structures. Every script uses the standard library. General all-length statements use the propagation and contraction proofs above, not extrapolation from the saved examples.

The theorem is about changing a selected coordinate **inside full regions**. It leaves unresolved fixed-layer completion equivalence for long regions, efficient regional repair distances, and the existence of a successful flow in every relevant core component. In particular it provides no general proof of the 5-CDC conjecture.
