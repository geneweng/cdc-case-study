# Two local exchanges suffice for a structural eleven-cycle class

Research date: **5 October 2026**.

The [actual-core obstruction](actual-core-exchange-obstruction.md) can be overcome uniformly when the target has its three small attached branches. **Every compatible eleven-port boundary with this attachment pattern can be repaired by at most two local auxiliary circuit exchanges.** The first move may be neutral. No other selected region's boundary changes.

This gives a conditional core reduction for any mixture of selected cycles of lengths three through ten and eleven-cycles having the specified structure and no distinguished-layer core ports. It retains the prescribed whole layer on H and the bound of two internal pentagon switches per Petersen four-pole.

Separately, the entire fixed-layer cover space of the preceding explicit core contains **1,327,104 covers**, all in one auxiliary exchange component. Exactly **48** need two exchanges to extend over the selected region; every other cover needs at most one. This holds even when every exchange must be a single circuit. Eight full graph certificates verify both hardest label classes, with and without a Petersen attachment. General length-eleven completion and general escape under neutral exchanges remain unresolved.

## 1. The structural hypothesis

Let v be the core vertex obtained by contracting a selected eleven-cycle, with ports numbered 0 through 10 in cyclic order. Suppose there are four distinct unselected cubic vertices a, b, c, and d outside that region:

| Outside vertex | Two target ports | Third neighbor |
|---|---|---|
| a | 2 and 6 | d |
| b | 1 and 7 | d |
| c | 5 and 8 | d |

Thus K−v has a four-vertex tree component: d is adjacent to a, b, and c, and each leaf has two edges back to v. We call a leaf with its two target edges a **cherry**. Each cherry gives a two-edge circuit in K. The other five ports, at positions 0, 3, 4, 9, and 10, may connect to an arbitrary outside core. Rotation or reflection of this numbered configuration is allowed.

Assume none of the eleven target edges belongs to distinguished cover layer 0. At each leaf, conservation forces the incoming pair on its edge to d to be auxiliary as well. At d, its three pairs form a triangle on three auxiliary labels. An auxiliary relabeling therefore normalizes the incoming pairs at a, b, c to 12, 13, 23 respectively, while fixing label 0. All 24 ordered labeled triangles are covered by this normalization.

The hypothesis is structural and includes a restriction on the prescribed layer. It is not a claim about every eleven-cycle. In the preceding native example, the four vertices are a=11, b=13, c=20, d=21.

## 2. A six-dimensional cube of legal local changes

For an incoming pair {α,β} at a cherry, its two target pairs must be

\[
\{\alpha,\gamma\},\quad\{\beta,\gamma\},
\]

in either order, where γ is one of the other two auxiliary labels. There are four possibilities. Two legal circuit exchanges connect them:

- Swap α and β on the two target edges, reversing their order.
- Swap the other two auxiliary labels on those edges, changing γ.

The edge to d is unaffected by either swap. Each operation preserves the core cover, distinguished layer, and every other boundary. Together they give a square. Three cherries give a six-dimensional cube with 64 states; each cube edge is one two-edge circuit exchange.

The three incoming pairs XOR to zero. Consequently the other five target pairs must form a closed auxiliary word: their XOR is zero. There are **960** such ordered five-pair words. Enumerating them and all 64 cherry states gives **61,440 normalized boundary configurations**, including every possible outside context under the hypothesis.

The following exact distances are to a boundary that extends when all eleven cuts are marked:

| Minimum cherry circuit exchanges | Normalized states |
|---|---:|
| 0 | 53,314 |
| 1 | 8,109 |
| 2 | 17 |
| **Total** | **61,440** |

Of the 960 fixed outside words, 65 have every cube state already good, 886 have maximum distance one, and nine have maximum distance two. None has a closed bad cube.

The constructor computes distances by breadth-first search from all good states. The independent verifier reconstructs the four leaf assignments from the pair equations, checks every cube edge as an actual auxiliary exchange, and calculates the minimum Hamming distance to the good states. Its good-state test uses independently rebuilt Blowup and SemiBlowup junction relations. The certificate includes explicit two-move witnesses for all seventeen hardest normalized states.

**Local repair theorem.** Under the structural and layer hypotheses of Section 1, every supplied compatible core cover can be changed at those six target edges alone so that the target region extends, using at most two auxiliary circuit exchanges.

**Proof.** Normalize the central triangle and encode the three leaf choices by six bits. The remaining five pairs form one of the 960 closed words. The verified finite table supplies a good state within two cube edges. Undoing the normalization turns these into legal auxiliary exchanges in the original labeling, affecting only the indicated target edges.

The all-marked calculation is the strongest obstruction in this setting. Because target ports do not carry label 0, the parity of the regional cut charges is constant. If any cut is marked, this parity is even, and deleting marked restrictions only removes forbidden charges. If the parity is odd, there are no marked restrictions and extension is automatic. Thus the all-marked repair also suffices for every compatible actual junction pattern. ∎

The bound two is sharp even allowing a move to use an arbitrary even edge subgraph: the preceding actual-core example has this structure and admits no one-step auxiliary repair anywhere in its core.

## 3. A conditional reduction including these eleven-regions

Let X be a Blowup or SemiBlowup of a simple cubic base along disjoint selected cycles. Let H be obtained by contracting the q Petersen four-poles, and K by further contracting the selected regions. Let F be the prescribed even layer on H and F_K its restriction to core edges.

**Theorem.** Suppose every selected cycle has length three through ten, or has length eleven with the attachment pattern of Section 1. Suppose also that F_K contains no target edge of any of these eleven-regions. Then H has a five-layer cover containing F as a whole layer **if and only if** K has a five-layer cover containing F_K as a whole layer.

Given a core cover, at most b+2r auxiliary-label exchanges suffice, where b is the number of initially bad regions of length at most ten and r is the number of selected eleven-regions of this type. The first phase uses at most b closed-trail exchanges, which may revisit vertices; the second uses at most 2r two-edge circuit exchanges. Some of the latter may be neutral.

**Proof.** Necessity follows by contracting the selected regions and restricting the cover to core edges.

For sufficiency, first process only the bad regions of length at most ten, using the established [length-ten escape and protection lemmas](ten-cycle-completion.md). Protect every good region of those lengths. Leave the eleven-regions unprotected during this phase; they may improve or deteriorate without affecting its progress. The short-region proof permits arbitrary even transitions at unprotected core vertices, so at most b exchanges make all short regions good.

Then process the eleven-regions. The local theorem repairs each in at most two exchanges. These exchanges use only the two target edges of one of its unselected cubic leaves. They change no boundary at another selected region, so the short regions and all already processed eleven-regions stay good. All boundaries now extend with F fixed. ∎

For any starting nowhere-zero three-bit flow on X whose chosen coordinate projects to F, the [joint Petersen completion lemma](joint-boundary-completion.md) then realizes the cover after at most **2q B-internal pentagon switches**, preserving every E₀ flow value. The auxiliary cover exchanges themselves change no flow values.

This ordering avoids assuming a universal protection lemma for eleven-regions. The local structure makes it possible to postpone them and repair them without disturbing their neighbors. A compatible core cover is still required.

## 4. The complete cover space of the explicit core

Fix the native 12-vertex core from the preceding report and its distinguished four-cycle (14,17,19,18), using original base vertex names. All target edges are outside that layer. We enumerate every compatible core cover, without fixing its target word.

Removing the target gives two outside components. For a component W, retain its edges to the target and identify their external ends with one vertex. A cover on the whole core restricts to a cover on each such factor: conservation at the vertices in W forces even parity of every label on its boundary. Conversely, factor covers combine freely.

The same argument applies to even-subgraph auxiliary exchanges. A move restricts to legal moves on the factors, and a factor move extends by the identity on the other factors. Therefore exchange components of the full cover space are products of factor components. Single circuits are confined to one factor; an exchange on an arbitrary even subgraph can act on both factors with the same auxiliary label pair.

### Counting the two factors

The tree factor has four cubic outside vertices and six target ports. Its central triangle has 24 labelings; each leaf has four completions for its incoming pair. Hence it has

\[
24\cdot4^3=1536
\]

covers.

The other factor has seven cubic outside vertices and five target ports. Its four distinguished edges form a cycle. Their auxiliary labels are a proper four-coloring of that cycle, with 84 possibilities. These determine the auxiliary pair at each incident non-distinguished edge. The remaining three cubic vertices form a path between two of those pairs. For 36 cycle colorings the endpoint pairs coincide, giving eight path assignments; for 48 they share one label, giving twelve. Thus this factor has

\[
36\cdot8+48\cdot12=864
\]

covers. The independent cycle-space enumeration recovers both counts without using this vertex-assignment argument.

Both factor exchange graphs are connected. Their product contains

\[
1536\cdot864=1\,327\,104
\]

compatible covers and is connected under single auxiliary circuit exchanges.

### Exact distances for all covers

| Distance to an extendible target boundary | Single-circuit moves | Arbitrary even-subgraph moves |
|---|---:|---:|
| 0 | 1,143,336 | 1,143,336 |
| 1 | 183,720 | 183,720 |
| 2 | 48 | 48 |

The auxiliary label group acts freely, giving 55,296 classes under global relabeling. The 48 hardest covers form exactly **two classes of 24**. The old explicit cover belongs to one; the census identifies the other. This is an exhaustive result for one fixed graph and one fixed distinguished layer, not a census of all graphs or layers.

For each hardest representative, two exchanges on separate cherries suffice: a 12-swap at ports 1 and 7, followed by a 23-swap at ports 5 and 8, in the representative's labeling. Each circuit has two edges. Every possible first auxiliary exchange still fails, including unions of circuits, as independently checked from the full binary exchange kernel.

Compatible covered two-edge insertions preserve the distance to an outside boundary condition by the [preceding insertion lemma](actual-core-exchange-obstruction.md). Thus the two-move upper bound also holds for every compatible cover projecting into this fixed-layer native space after any such insertions. In particular it applies to the Petersen-attached cores, which have no four-flow. This transfers the boundary-distance bound; it does not assert that all covers of an inserted graph belong to one exchange component.

## 5. A general connectedness lemma for the tree factors

**Lemma.** Take a cubic tree with n internal vertices and attach every dangling edge to one common target vertex. Assume label 0 is absent. Its compatible four-auxiliary-label covers are connected under auxiliary circuit exchanges, with cover-to-cover distance at most 2n+1.

**Proof.** For n=1, all 24 assignments of the three pairs are related by auxiliary permutations. Any permutation of four labels is a product of at most three transpositions, each acting on a two-edge circuit at this vertex.

For n>1, choose a leaf of the outside tree, which has two edges to the target. Remove that leaf and replace its edge to its parent by an edge from the parent to the target. Restricting a cover preserves its label on this replacement edge. A circuit exchange in the smaller core lifts through the leaf when it uses the replacement edge: exactly one of the leaf's two target edges is then affected by the same swap, giving the continuation of the circuit.

After lifting a sequence that aligns the smaller cover, the incoming leaf pair is correct. At most two cherry swaps align the remaining leaf choice and its order, leaving all other edges fixed. The induction gives 3+2(n−1)=2n+1. ∎

This connectedness statement allows a boundary condition to change during the sequence. It alone does not bound the distance to an arbitrary regional extension condition. The two-move repair theorem uses the particular interleaving of the six cherry ports and its complete finite boundary calculation.

## 6. Full certificates and independent checks

Both hardest representatives are completed in both constructions, with and without a Petersen two-edge insertion. Each row below represents two certificates, one per label class.

| Construction and core | Vertices | Core circuit lengths | B-internal pentagons |
|---|---:|---|---:|
| Blowup, native | 132 | 2 then 2 | 8 |
| Blowup, Petersen-attached | 142 | 2 then 2 | 8 |
| SemiBlowup, native | 110 | 2 then 2 | 9 |
| SemiBlowup, Petersen-attached | 120 | 2 then 2 | 9 |

All original quotient flow values and the whole prescribed layer on H remain fixed. The eight final five-layer covers and every intermediate internal flow are checked. The displayed flow-switch counts are constructive bounds, not minimum flow distances. These graph certificates have one eleven-region; the mixed-region conclusion in Section 3 follows from the phase-ordering proof and the previously verified short-region lemmas.

The [constructor](auxiliary_exchange_orbit.py) writes the [certificate](auxiliary_exchange_orbit.json). The [independent verifier](verify_auxiliary_exchange_orbit.py) imports no constructor or earlier verifier. Its separate checks include:

- Reconstructing all factor covers from three independently chosen binary cycles, with the fourth auxiliary layer forced by their XOR and the distinguished layer. The constructor instead assigns vertex triangles.
- Computing all exchange neighbors from binary incidence kernels, rather than the constructor's split paths and cycles.
- Testing all 1,327,104 target boundaries against the local junction relation, checking a one-circuit escape for every distance-one state, and excluding every even-subgraph escape from the 48 hardest states.
- Checking the 61,440 normalized cherry states by local relations and Hamming distance, independently of the constructor's breadth-first search.
- Reconstructing the cubic graphs for all eight cover certificates, checking 640 initial swap/port-set cases, both cover exchanges, every internal pentagon switch, and every final flow and cover. Petersen two-edge cuts certify the stated lack of four-flows.

Reproduce from the repository root with Python 3 and its standard library:

```bash
python3 -B research/five-cdc-attempt/auxiliary_exchange_orbit.py
python3 -B research/five-cdc-attempt/verify_auxiliary_exchange_orbit.py
```

The next questions are whether other attachment patterns admit equally local neutral repairs, and whether neutral auxiliary exchanges eventually escape in arbitrary cores. The structural eleven-cycle result does not cover targets with distinguished-layer ports or arbitrary outside attachments. No general length-eleven reduction or proof of the 5-CDC conjecture is claimed.
