# How cut certificates change under circuit switches

Research date: **5 October 2026**.

**Every individual paired-cut obstruction can be destroyed by one legal circuit switch, even while preserving the chosen first coordinate.** An exact survival rule proves this constructively. However, destroying every certificate for a coordinate pair need not make that pair completable: an explicit Petersen switch removes its entire old certificate family and creates a different one.

A second result gives a way to track the actual lift obstructions. Assign each cubic vertex the unique nonzero dual vector annihilating its three incident flow values. A chosen coordinate succeeds exactly when these vertex vectors sum to zero on every component of its complement. Both vertex vectors and component sums have explicit update formulas under circuit switches.

These results continue the [paired-cut analysis](fiber-cut-obstructions.md). They establish escape from an individual witness and identify why that does not establish escape from all failure. The general five-cycle double cover conjecture and a universal flow-repair theorem remain unproved here.

## 1. A four-cell description of a cut certificate

Throughout, G is a connected loopless cubic graph.

Write a nowhere-zero binary three-bit flow as

\[
f=4F+2y+z.
\]

For the fixed first two coordinates, put T=supp(F)∪supp(y) and S=E∖T. Recall that vertex sets A,X certify failed completion exactly when

\[
\delta(A)\subseteq F,\qquad
\delta(X)\cap T=y\cap\delta(A),\qquad |X|\text{ is odd}.
\tag{1}
\]

Here cycles are identified with their edge supports. The odd-|X| formulation uses cubic degree parity, as proved previously.

Give a vertex v the two-bit label w(v)=(1_A(v),1_X(v)). For an edge e=uv, write Δw(e)=w(u)+w(v). The first two conditions in (1) are precisely the following edge constraints:

| Projection (Fₑ,yₑ) | Allowed Δw(e) |
|---|---|
| (0,0) | (0,0), (0,1) |
| (0,1) | (0,0) |
| (1,0) | (0,0), (1,0) |
| (1,1) | (0,0), (1,1) |

The allowed sets for any two distinct projection values intersect only at (0,0). Thus a certificate is a partition into at most four vertex cells, with tightly specified projection values on edges crossing the cells.

## 2. Exact survival under a switch

Let a legal circuit move add a nonzero vector a on C. Follow the same coordinate functionals before and after the move; let b be the projection of a to the F,y coordinates.

**Survival theorem.** An existing certificate (A,X) remains a certificate after the move if and only if

\[
b=0\quad\text{or}\quad
C\cap\bigl(\delta(A)\cup\delta(X)\bigr)=\varnothing.
\tag{2}
\]

For b≠0 and a connected circuit, survival means that the entire circuit lies in one cell of w.

**Proof.** If b=0, the projection is unchanged. Otherwise every edge of C changes its projection value. Its old and new allowed sets in the table intersect only at zero, so the same certificate can survive exactly when Δw(e)=0 on every edge of C. All other edge constraints are unchanged. The parity of X also stays unchanged. ∎

This theorem concerns the **same vertex sets A,X**, with the coordinate functionals followed through the switch. It does not rule out a replacement certificate with different vertex sets.

## 3. Every individual certificate admits a legal escape

The survival rule can always be violated, even while F stays fixed.

**Single-certificate escape theorem.** Given a nowhere-zero flow f=4F+2y+z and a certificate (A,X), there is a legal circuit switch destroying that certificate and preserving F. Either of the two increment choices 2 and 3 permits such a switch.

**Proof.** Since X has odd size while a cubic graph has an even number of vertices, X is neither empty nor the whole connected graph. Choose an edge

\[
e\in\delta(A)\cup\delta(X).
\]

The table shows that its projection cannot be (0,1), since that projection permits no crossing between certificate cells. Hence f(e) is neither 2 nor 3.

Choose a=2 or a=3, and remove all edges of flow value a. Projecting the flow to the quotient group F₂³/⟨a⟩ gives a nowhere-zero flow on every remaining edge. Such a graph has no bridge: summing conservation on one side of a bridge would force its value to be zero. Thus e belongs to a circuit C avoiding value a.

Adding a on C is legal. It preserves F and changes y, while C meets a certificate cut at e. Equation (2) therefore destroys the certificate. ∎

The proof is constructive: after choosing a and e, find a path between the endpoints of e in the graph with value-a edges and e removed. A shortest path plus e supplies a circuit of length at most |V(G)|. No search for a cover is needed.

For non-three-edge-colorable cores, the new flow still has coordinate rank three. More generally the certificate-destruction statement does not require the rank to stay three; it follows directly from the edge constraints.

## 4. Complete replacement of the obstruction family

The escape theorem cannot be iterated with an automatic conclusion of success. The following example loses **every old certificate**, yet still has no completion for its chosen F.

Use the Petersen edge order and cycle basis in [flow_space_components.json](flow_space_components.json). Let F be its two pentagons, with cycle code 57, and start with y=14 and z=16. The edge flow is

```
4,6,4,6,7,3,2,2,2,1,7,6,5,4,4
```

The zero set of (F,y) is the single matching edge 9. The complete obstruction family, identifying independent complementation of A and X, has just one member:

\[
A=\{4,9\},\qquad X=\{4\}.
\]

Its cuts are δ(A)={3,4,12,14} and δ(X)={3,4,9}. This is the earlier single-edge local obstruction.

Add **2 on the outer pentagon**, edges {0,1,2,3,4}. All five old values are at least four, so the switch is legal. It preserves F and z and changes y from cycle code 14 to 15. The new flow is

```
6,4,6,4,5,3,2,2,2,1,7,6,5,4,4
```

The zero set S remains the same single edge. The old certificate is destroyed because the circuit meets both of its cuts. But two new normalized certificates appear:

| Certificate | A, as a vertex set | X, as a vertex set |
|---|---|---|
| First replacement | {1,2,6,7} | {1,2,6,7,9} |
| Second replacement | {1,2,4,6,7,9} | {1,2,6,7,9} |

For both, δ(X)={0,2,9,10,11}, and the shared part y∩δ(A) is {0,2,10,11}. The remaining edge 9 forces odd parity. There is no single-edge local blocker for this new coordinate pair: the failure has become nonlocal.

To make the word “complete” precise, the enumeration uses representatives with vertex 0 outside both A and X. Complementing either set does not change its cut or validity. Thus the one old representative stands for four literal vertex-set pairs, and the two new representatives stand for eight. Both complete families are saved, and no member survives.

The affine third-coordinate fiber has dimension five before and after. The dual obstruction dimension increases from two to three, and the completion-map rank decreases from three to two. Completion remains inconsistent in both cases.

All **960** nowhere-zero flows with this prescribed first coordinate fail its lift test, checked independently by enumerating their third and fourth coordinates. The earlier [structural argument for the Petersen two-factor](attempt.md#4-second-attempted-proof-repair-the-flow-while-keeping-f-fixed) proves this failure without enumeration. Petersen itself has five-layer covers; both displayed flows succeed with another first coordinate, and the certificate includes a decoded cover for the second flow.

Thus this example concerns a failed fixed-coordinate strategy, not failed cover existence. It proves that even complete destruction of the currently visible obstruction family need not resolve a fixed-coordinate completion problem.

## 5. Vertex vectors encode the actual lift obstruction

For a cubic nowhere-zero three-bit flow f, let ν(v) be the unique nonzero vector in the dual space satisfying

\[
\nu(v)\cdot f(e)=0\quad\text{for all three edges incident to }v.
\]

The incident values are distinct and span a plane, so ν(v) exists uniquely. In fixed binary coordinates, if x,b are any two incident values, ν(v)=x×b, using the usual three-dimensional cross product over F₂. The choice and ordering of the two incident edges do not matter.

Fix a nonzero first-coordinate functional ℓ, put F=ℓ∘f, and let K be a component of H=G−F. Define its **charge** as the vector

\[
Q_\ell(K)=\sum_{v\in K}\nu(v).
\]

**Normal-charge theorem.** Every such charge is either 0 or ℓ. If y,z complete F to flow coordinates, then

\[
Q_\ell(K)=\beta_K(y,z)\,\ell.
\tag{3}
\]

Consequently, this first coordinate admits the five-label lift exactly when every component has zero charge.

**Proof.** Choose coordinates (F,y,z), so ℓ is the first dual basis vector. Vertices internal to H have all three incident F-values zero and ν(v)=ℓ. Every other vertex is a leaf of H.

At a leaf, write its H-edge value as (0,b₁,b₂), and one F-edge value as (1,u₁,u₂). Then

\[
\nu(v)=(u_1b_2+u_2b_1,\ b_2,\ b_1).
\]

The contribution from its two F-edges to the sum of yz is

\[
u_1u_2+(u_1+b_1)(u_2+b_2)
=\nu(v)_1+b_1b_2.
\]

Summing over the leaves counts internal F-edges twice, leaving exactly β_K(y,z). Conservation inside H gives ∑b₁=∑b₂=0 over its leaves. Also, ∑b₁b₂ over its leaves equals the number of internal vertices modulo two: each internal vertex sees the three nonzero two-bit values, whose coordinate products sum to one, and every internal edge is counted twice. Thus the last two coordinates of Q vanish and its first coordinate is β_K(y,z). This is (3). ∎

In particular, the sum of ν over the whole graph is always zero, and obstructed components occur in even number. This total is identically zero for every flow; it is not an invariant that distinguishes exchange components.

### Local and nonlocal obstructions in this description

An obstructed component consisting of a single edge uv has

\[
\nu(u)+\nu(v)=\ell.
\]

Conversely, if an edge has that difference, neither endpoint has normal ℓ and the edge is an isolated component of G−F. Thus these normal differences identify exactly the bad two-vertex components.

The other components contain vertices with ν(v)=ℓ. Their obstruction requires the sum over the entire component; absence of a bad isolated edge does not guarantee success. The paired-cut certificates and these charges answer different questions: a charge tests the current flow, whereas a paired cut can forbid every third-coordinate completion of a fixed pair F,y.

## 6. Exact updates of vertex vectors and component charges

Suppose a legal switch adds a on a circuit C. At a vertex v of C, let bᵥ be the flow value on its unique edge outside C. Then

\[
\nu'(v)=\nu(v)+a\times b_v\quad(v\in C),
\qquad \nu'(v)=\nu(v)\quad(v\notin C).
\tag{4}
\]

Indeed, the two circuit values are x and x+bᵥ, so the normal changes from x×bᵥ to (x+a)×bᵥ.

If ℓ(a)=0, the chosen F and its complement components remain unchanged. Summing (4) gives the exact component update

\[
Q'_\ell(K)=Q_\ell(K)+
a\times\left(\sum_{e\in C\cap\delta(K)}f(e)\right).
\tag{5}
\]

The identity follows by substituting bᵥ as the sum of the two incident circuit values: contributions from circuit edges internal to K cancel. The correction is necessarily 0 or ℓ, consistently with (3).

If ℓ(a)=1, formula (4) still holds, but F changes to F+C and the complement components can merge or split. Their new charges must be summed over the **new** components. Controlling this change of components is the remaining difficulty; reusing the old component partition would be incorrect.

### Tracking the saved J₅ repair

The normal calculation recovers the complete defect vectors for the earlier two-circuit repair on the flower graph. Entries are the numbers of nonzero-charge components for ℓ=1,…,7:

| Stage | Defect vector | Earlier potential Ψ=(minimum, sum) |
|---|---|---|
| Initial | (6,4,6,6,6,4,6) | (4,38) |
| After the six-circuit switch | (6,4,6,4,8,6,4) | (4,38) |
| After the eleven-circuit switch | (2,0,6,2,4,6,2) | (0,22) |

This now verifies that the first switch is neutral for the earlier Ψ, a fact the previous checkpoint did not claim. It is not a proof of a universal nonincreasing repair rule.

At the endpoint, ℓ=2 is the successful choice. Its complement has components of orders 18 and 2, each with zero normal charge. All 610 legal first moves from the initial flow still fail every first-coordinate lift, as checked independently again.

In the Petersen replacement example, F remains fixed and its two charged matching components move from edges {7,9} to {5,7}. The certificate at edge 9 disappears, while the overall obstruction persists.

## 7. Reproduction and limits of the computation

The [constructor](cut_certificate_transport.py) reuses the preceding cycle-space and Gaussian-completion routines. On Petersen it enumerates cut pairs directly as vertex subsets, constructs escape circuits by shortest paths, and computes vertex normals by the binary cross-product formula.

The [independent verifier](verify_cut_certificate_transport.py) imports no constructor code. It reuses the earlier independent cycle/restriction checker, enumerates circuits by graph DFS, rebuilds complete certificate families by signed-edge propagation, and computes vertex normals by testing dual functionals. The normal-charge success tests are checked against all restrictions of a fourth binary cycle. Constructed shortest-path escapes are regenerated by enumerating paths in increasing length.

The checks include:

- All 960 nowhere-zero flows with the Petersen two-factor as first coordinate; none completes for that coordinate.
- Thirty feasible fixed-coordinate tests up to y↔y+F, with 95 normalized cut certificates.
- All 3,390 legal moves from one representative flow per test, giving **10,660 certificate/move comparisons**; 1,590 preserve the specified certificate.
- **190 constructed escapes**, one for each certificate and each increment 2 or 3, all preserving F and destroying the selected certificate.
- **41,110** fixed-component charge updates on those Petersen moves and **13,210** on all 610 initial J₅ moves.
- The complete old and new certificate families in the replacement example, its alternative-coordinate cover, and both actual J₅ repair steps.

The [saved certificate](cut_certificate_transport.json) contains the input hash, exact audit totals and record hashes, the complete replacement example, and vertex normals and component charges along the flower-graph path. Reproduce with Python 3 and the standard library:

```bash
python3 -B research/five-cdc-attempt/cut_certificate_transport.py
python3 -B research/five-cdc-attempt/verify_cut_certificate_transport.py
```

The survival, individual-escape, and charge-update theorems have direct proofs; the numerical audits check their implementations and the explicit examples. They do not establish a general bound on the number of moves to success.

The next structural target is to control charge when the first coordinate changes and complement components are rearranged. A proof must allow replacement certificates and the already demonstrated neutral moves. The ability to destroy a current witness, even the entire current family for a fixed pair, supplies no termination argument on its own.
