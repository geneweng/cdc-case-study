# Cycle regions through length seven preserve prescribed cover boundaries

**30 September 2026.** The triangle completion reduction extends to selected cycles of lengths **three through seven**, for both Blowup and SemiBlowup. Every compatible specified five-layer cover boundary extends through the contracted-piece region while preserving an arbitrary prescribed even layer. At length **eight**, this stronger boundary-preservation property first fails.

The failure at eight concerns a **particular supplied core cover**. It does not establish failure of existential completion equivalence: the two cubic examples here have alternative covers and successful internal repairs. The general 5-cycle double cover conjecture remains unproved here, and no claim of novelty is made.

The proof combines an exact eight-charge extension criterion with a finite exhaustive computation. An independent, standard-library verifier reconstructs all junction relations and all **16,384 automaton states**. It also checks explicit covers, rejected boundaries, and full cubic graph certificates.

## 1. Two contractions and the extension question

Use the graph and port conventions in the [four-flow quotient report](fourflow-quotient-repair.md). Let S be a simple cubic graph, D a union of vertex-disjoint selected cycles, and X either Blowup(S,D) or SemiBlowup(S,D). Write q for the total number of vertices in D, hence the number of inserted Petersen four-poles B.

Contract each B to one degree-four vertex to obtain H. Contract the selected cycle regions further to obtain K=S/D. All edges of S outside D are retained as **core edges**, including loops created by contraction; each loop has two incidences at its vertex. Let E₀ be the edges of X retained in H. Thus E(K) is a subset of E₀.

A length-k selected cycle gives a k-port region in H: it contains k contracted B vertices, k original cycle vertices, and, in Blowup, 2k auxiliary vertices. Cutting its core edges into ports gives 4k vertices and 6k internal edges for Blowup, or 2k vertices and 3k internal edges for SemiBlowup. Attaching the k ports to a new cap vertex gives respectively 4k+1 or 2k+1 vertices. The cap is only a convenient way to record summed boundary parity; for k>3 it is not cubic.

Throughout, a five-layer CDC means at most five even subgraphs, possibly disconnected or empty, covering every edge exactly twice. Equivalently each edge receives a pair from

\[
Q=\{\{i,j\}:0\le i<j\le4\},
\]

and each label has even degree at every vertex. A prescribed layer F is named label 0. A boundary is compatible if its pairs XOR to zero and contain 0 exactly on the ports belonging to F.

The [triangle report](triangle-quotient-reduction.md) proved universal boundary extension for k=3 by a four-flow and a symmetry argument. That symmetry argument does not apply unchanged to higher-degree cap vertices. The following exact criterion treats every k.

## 2. An exact extension test with eight possible charges

Represent label sets as five-bit integers; XOR is symmetric difference. At junction i, write

\[
(a,b,c,d)=(a_{1,i-1},a_{2,i-1},b_{1,i},b_{2,i}),
\qquad r_i=a\oplus b\oplus c\oplus d.
\]

Here r_i is the prescribed core-edge pair. The local constraints are:

| Construction | Additional constraints | Ordered edge-pair representatives |
|---|---|---|
| Blowup | a⊕c and b⊕d belong to Q | a,b,c,d,a⊕c,b⊕d,r_i |
| SemiBlowup | b=d, representing one shared edge | a,b,c,d,r_i |

All a,b,c,d,r_i belong to Q. These equations impose the five parity conditions at each cubic junction vertex. Encode membership of a,b,c,d in F by

\[
z_i=1_{0\in a}+2\,1_{0\in b}+4\,1_{0\in c}+8\,1_{0\in d}.
\]

The other F-memberships follow by parity. Define the **left charge** L_i=a⊕b and the right charge c⊕d=L_i⊕r_i. At the contracted B_i vertex, the right charge of junction i must equal the left charge of junction i+1. This is sufficient for parity of all five labels there; it is an exact condition because B has already been contracted.

For each admissible (r,z), let M(r,z) be the set of left charges realized by a local junction assignment. Direct enumeration gives:

| Construction | Junction assignments | (r,z) keys | Keys with 6 charges | With 7 | With 8 |
|---|---:|---:|---:|---:|---:|
| Blowup | 2,160 | 80 | 6 | 28 | 46 |
| SemiBlowup | 600 | 40 | 6 | 8 | 26 |

These are all admissible keys: r's label-0 bit equals the parity of z, and SemiBlowup additionally requires z's b and d bits to agree. The table includes a junction witness for every allowed charge.

Every charge is an even-cardinality subset of the five labels. Its label-0 bit is fixed by the first two bits of z. Consequently there are just eight possible initial charges h. Set

\[
R_0=0,\qquad R_i=r_0\oplus\cdots\oplus r_{i-1},
\qquad p=1_{0\in a_0}\oplus1_{0\in b_0}.
\]

**Exact charge criterion.** For any length k, a compatible specified boundary extends with layer 0 exactly F if and only if

\[
\boxed{\ \{h: |h|\text{ even},\ 1_{0\in h}=p\}
\ \cap\ \bigcap_{i=0}^{k-1}\bigl(M(r_i,z_i)\oplus R_i\bigr)\ne\varnothing.\ }
\tag{1}
\]

Here |h| counts labels, and M⊕R means {m⊕R:m∈M}.

**Proof.** Any extension has L_i=h⊕R_i by charge propagation, so it satisfies every intersection condition. Conversely choose a surviving h and the saved local witness with left charge h⊕R_i at each junction. Adjacent charges agree at each contracted B vertex. Boundary compatibility gives R_k=0, closing the cycle. The witnesses realize exactly the prescribed F-bits and boundary pairs, so they glue to the required cover. □

After precomputing the constant-size table, testing (1) and constructing a cover take O(k) time: retain eight candidates and eliminate those failing each junction. This charge-only description applies to H; the uncontracted B with a fixed internal layer has additional restrictions, addressed by the [joint flow-cover repair theorem](joint-boundary-completion.md).

## 3. Exhaustive proof of the short-cycle threshold

For fixed initial parity p, use automaton states (R,A), where R is the current prefix XOR and A is the set of surviving initial charges. There are 16 possible even R values and 256 subsets of the eight initial candidates, hence 4,096 states. Start at (0,A₀), with all eight candidates.

A letter (r,z) is allowed when the label-0 bit of its left charge is p⊕1_{0∈R}. Its transition is

\[
(R,A)\longmapsto
\bigl(R\oplus r,\{h\in A:h\oplus R\in M(r,z)\}\bigr).
\tag{2}
\]

A closed boundary has R=0. A closed word is rejected exactly when A is empty. Every actual even F with a compatible boundary produces an allowed closed word; conversely every allowed closed word constructs consistent junction F-bits and boundary parity. Thus this automaton is an exact finite model, not a relaxation.

Breadth-first search reaches all 4,096 states in each of the four combinations of construction and initial parity. The shortest closed words with each survivor count are the same for both constructions:

| Initial parity p | 0 survivors | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | **8** | 7 | 6 | 5 | 4 | 3 | 2 | 2 | 0 |
| 1 | **9** | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 0 |

The zero in the final column is the empty word. Parity p refers to a chosen starting cut; it is not a rotation-invariant property of an arbitrary region. The universal minimum rejecting length is eight.

**Short-cycle boundary theorem (finite verified proof).** For either construction, if 3≤k≤7, every even F in the k-port region and every compatible specified boundary extend to a five-layer cover with layer 0 exactly F.

This follows from the exact model and the absence of a shorter path to (0,∅). The saved certificate records all distance histograms, a digest of the entire distance function, and shortest rejected words. The independent verifier reconstructs the junction relation using cubic-vertex label triangles, then recomputes all distances with sets of charges rather than the constructor's bitmasks. No SAT solver or graph library is used.

Twenty explicit positive cap covers accompany the exhaustive proof: lengths three through seven for both parities and both constructions. At length seven, the p=0 examples have a **unique** possible initial charge.

## 4. Completion and internal repair reduce to the core

**Reduction theorem.** Suppose all selected cycles in D have lengths three through seven. For any even subgraph F of H,

\[
F\text{ is a whole layer of a five-layer CDC of }H
\quad\Longleftrightarrow\quad
F\cap E(K)\text{ is a whole layer of one on }K.
\tag{3}
\]

Moreover, every supplied core cover witnessing the right side lifts while preserving all its edge pairs.

**Proof.** Restriction to core edges preserves double coverage and summed parity at every contracted vertex, proving the forward implication. For the reverse implication, the supplied cover gives a compatible boundary at each selected region. Apply the short-cycle boundary theorem to the actual F in that region. Unselected vertices keep their original pairs. The local covers glue on every core edge, including edges between two selected regions or loops arising from chords. □

Let f be any nowhere-zero F₂³-flow on X and ℓ any nonzero linear functional. Restriction gives a flow f_K on K and a coordinate support on H. Combining (3) with joint Petersen completion yields

\[
\ell(f_K)\text{ is five-layer completable on }K
\quad\Longleftrightarrow\quad
\ell(f)\text{ can become completable on }X
\text{ after switches inside the B pieces.}
\tag{4}
\]

If a core cover is supplied, at most **2q internal pentagon switches** suffice. They preserve every E₀ flow value, and the final cover preserves the supplied core edge pairs. If core completion fails, no repair preserving all core-edge values can succeed, since any resulting cover would restrict to a forbidden core cover.

Unlike the earlier four-flow criterion, this reduction does not assume that K has a nowhere-zero four-flow. Its unresolved part is the prescribed-layer completion problem on K, whose contracted vertices may now have degrees up to seven.

## 5. Explicit failure at an eight-cycle

Use the following boundary pairs, written as five-bit integer masks:

\[
(r_0,\ldots,r_7)=(6,10,6,18,6,10,6,18).
\]

They are the pairs {1,2}, {1,3}, {1,2}, {1,4}, repeated; no pair contains label 0, and their XOR is zero. The prefix values before the eight junctions are

\[
(R_0,\ldots,R_7)=(0,6,12,10,24,30,20,18),
\]

all eight even subsets of labels {1,2,3,4}.

**Blowup.** Set z_i=3 at every junction: a,b belong to F and c,d do not. Then a⊕c and b⊕d belong to F, while r_i does not. The resulting F consists of eight disjoint four-cycles, one at each junction. For these letters M(r_i,3) contains all eight even auxiliary-label charges except 30. Equation (1) therefore excludes h=30⊕R_i at junction i. The eight junctions exclude all eight candidates.

**SemiBlowup.** Alternate z_i=0,15,0,15,0,15,0,15. This F consists of four disjoint triangles. At a z=0 junction all eight charges are allowed. At a z=15 junction the excluded charges are 30 and 30⊕r_i. Translated back to initial charges, the four active junctions exclude

\[
\{24,18\},\quad\{20,6\},\quad\{0,10\},\quad\{12,30\},
\]

again exhausting the eight candidates. Thus neither specified boundary extends with its prescribed F.

### Cubic graph certificates and an alternative cover

To place each obstruction in a cubic graph, take two disjoint eight-cycles and join their vertices by a perfect matching. Number top vertices 0,…,7 and bottom vertices 8,…,15. Around the bottom cycle the matched top vertices occur in the order

\[
(0,1,5,2,3,7,4,6).
\]

Select the top cycle for replacement. This gives a **96-vertex Blowup** and an **80-vertex SemiBlowup**, both simple cubic graphs. Their core K has nine vertices: an eight-cycle and a hub joined to each of its vertices.

Assign the hub-edge pairs r_i above, ordered by top vertex. In bottom-cycle order, assign rim pairs

\[
(12,6,12,10,24,10,12,10).
\]

These pairs form a valid core five-layer cover with empty label 0. Take F on H as in the rejected region and empty on all core edges. That particular core cover cannot lift preserving F.

Nevertheless, alternating four-flow values 1,2 on the bottom rim and assigning 3 to every hub edge gives a four-flow on K. The earlier quotient theorem supplies one on H. The symmetric-difference construction from that report completes every even F on H using four labels. The certificates give an explicit **different core cover** and full covers of X after **four internal pentagon switches** for Blowup and **zero** for SemiBlowup, from the saved input flows. Both use the same prescribed coordinate on E₀ throughout.

These examples disprove universal preservation of a supplied core cover at length eight. They do **not** disprove (3) or (4) at that length when the choice of core cover is free.

## 6. Circuit lifting already changes at four ports

The extension of the completion theorem must be kept separate from the triangle report's circuit-lifting lemma. That lemma uses exactly three ports. At four ports, a valid core circuit switch need not lift immediately through a region from the current flow.

The saved square SemiBlowup quotient cap has nine vertices and sixteen edges. Its first four edges are the cap spokes. A nowhere-zero flow is

```text
1111223233223233
```

Contract the region to obtain two vertices joined by four parallel core edges, all carrying value 1. Switching core edges 0 and 2 by increment 2 is valid. But after deleting internal edges with value 2, the region's port components are {0,1} and {2,3}. There is no allowed internal path between the selected ports, so no single lifted circuit can induce exactly that core switch.

One internal preparation is sufficient: switch the triangle on edge indices 4,5,6 by increment 1. Then edges 4,14,12 form an internal path from port 0 to port 2 avoiding value 2. Together with core edges 0 and 2, they give the required lifted circuit. The verifier checks both switches and every intermediate flow. Thus this particular lift needs exactly one internal preparation.

This is a counterexample to preparation-free lifting, not a counterexample to a particular equality of repair distances. A global circuit may also meet a higher-port region more than twice, so the triangle projection argument cannot simply be reused. No extension of the triangle distance theorem is claimed here.

## 7. Reproduction and scope

From this directory:

```bash
python3 -B short_cycle_boundary.py
python3 -B verify_short_cycle_boundary.py
python3 -B verify_joint_boundary_completion.py
```

- [Constructor](short_cycle_boundary.py): junction witnesses, exact automata, boundary filters, and graph certificates.
- [Certificates](short_cycle_boundary.json): deterministic data, finite-state distance digests, 20 positive caps, two rejected octagons, two cubic completions, and the square switching example.
- [Independent verifier](verify_short_cycle_boundary.py): rebuilds the finite model and checks all graph, flow, cover, obstruction, and switch certificates without importing the constructor or prior verifiers.

The final command separately verifies the earlier joint boundary theorem used for the uniform 2q repair bound. The new verifier checks the actual repairs saved here directly. The universal short-cycle statement is an exhaustive finite proof through the exact junction model; the general reduction follows by gluing. The existence problem on unrestricted cores, the possible existential reduction for longer selected cycles, and a useful replacement for the three-port distance theorem remain unresolved here.
