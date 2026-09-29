# Neutral repair, parallel edges, and the remaining existence gap

**29 September 2026. This continues the proof attempt; it does not prove the general 5-cycle double cover conjecture.**

The complete 16-vertex computation now verifies repair sequences that allow neutral moves. Every starting flow in the census can eventually reach a five-label lift without increasing the potential. There are exactly four flow classes for which the first move cannot improve the potential, and all four admit an improvement after one neutral move.

A second result is a proved normalization lemma for a pair of parallel edges. It reduces all seven obstruction counts simultaneously. However, a concrete example shows why this lemma does not automatically let us lift an entire nonincreasing repair sequence from a smaller graph. The graph-level existence problem does transfer across this reduction; the stronger requirement on every intermediate flow is the difficulty.

The general deductions below are supplied with proofs and no claim of novelty over the complete literature. The finite checks concern this particular repair method, not a new verification bound for the original 5-CDC conjecture.

## 1. The exact condition for neutral repair

For a fixed graph, form its finite reconfiguration graph: vertices are nowhere-zero F₂³-flows, and edges are the allowed circuit moves from the preceding reports. Give each flow the lexicographic potential

\[
\Psi(f)=\left(\min_{\ell\ne0}D_\ell(f),\ \sum_{\ell\ne0}D_\ell(f)\right).
\]

Call a flow successful when its first potential coordinate is zero. A **plateau** is a connected component of flows with the same potential, using only moves that preserve that potential.

**Finite-state criterion.** Every flow can reach a successful flow by a sequence whose potential never increases if and only if every plateau with positive first coordinate has an edge to a smaller potential.

**Proof.** If every unsuccessful plateau has a downward exit, move within the plateau to that exit, then descend. The state space is finite, so repeated strict descents must terminate, and they can terminate only at a successful flow. Conversely, a nonincreasing path from an unsuccessful flow to a successful flow must eventually leave its original potential level downward. Its constant-potential prefix stays inside the original plateau and identifies a downward exit. □

This formulation handles the earlier 16-vertex counterexample: it is a strict local minimum, but its plateau has a downward exit. It also states precisely what a counterexample to nonincreasing repair would need to establish: a whole unsuccessful plateau with no downward exit. Checking the immediate neighbors of one flow is insufficient.

## 2. Complete 16-vertex result

The new search enumerated all 4,060 connected simple cubic graphs of order 16, retained the 3,874 bridgeless graphs, and exhausted their nowhere-zero flow classes under invertible changes of the three coordinates.

| Quantity | Exact count |
|---|---:|
| Bridgeless graphs checked | 3,874 |
| Nowhere-zero flow classes | 91,351,392 |
| Classes requiring repair | 58,864,723 |
| Classes with no immediately improving move | 4 |
| Those four admitting improvement after one neutral move | 4 |
| Closed unsuccessful plateaus found | 0 |

For each unsuccessful class, the program first searches for a strictly improving move. Only when this fails does it explore the neutral plateau by breadth-first search. All four exceptional classes have neutral distance one to a flow with a downward exit. The other unsuccessful classes have a downward exit immediately.

| Graph6 encoding of the exceptional graph | Allowed neighbors of its exceptional flow | Verified escape potentials |
|---|---:|---|
| `O???C@_cSo@gB_S_K_@D?` | 175 | (2,18) → (2,18) → (0,18) |
| `O???E?oBCEKCk?Q_B_?K_` | 179 | (2,18) → (2,18) → (0,16) |
| `O??CAA_EF?CK@oD_J??W_` | 170 | (2,18) → (2,18) → (2,16) |
| ``O??CA?oI@PR?`_S_?iAI?`` | 181 | (2,18) → (2,18) → (2,16) |

The last two displayed paths reach a smaller positive potential. The complete census also covers their endpoints, so repeated improvement reaches a successful flow. The table does not claim that every starting flow reaches a cover in two moves; it establishes a two-move bound to the *next strict improvement* in this finite class.

There are 788 triangle-free graphs among the 3,874, representing 18,673,382 flow classes. None has a strict local minimum with positive first coordinate. All four exceptions contain triangles. This is a finite observation, not a proof that triangle-free graphs always admit strict descent.

Together with the earlier census through 14 vertices, nonincreasing repair is now verified for all 4,461 connected bridgeless simple cubic graphs through 16 vertices. The [proved triangle-expansion inheritance](repair-obstruction.md#moves-on-the-contracted-graph-lift-back) therefore extends this repair property to arbitrary iterated triangle expansions of any of these checked cores. That infinite-family consequence uses both the general reduction proof and the finite core checks.

### Verification and quotienting

The enumeration uses reduced row echelon bases of subspaces of the binary cycle space, with counts checked against Gaussian binomial coefficients, as explained in [continuation.md](continuation.md). The new engine was cross-checked against the existing complete records through order 10. All four exceptional flows and their escape paths were then checked by the separate Python implementation: circuits are enumerated by simple-path DFS, and all neighbor potentials are recomputed directly from component cuts.

The plateau search identifies states under GL(3,2). This is legitimate because coordinate changes preserve the potential and map allowed moves to allowed moves. Any quotient path can be lifted from any representative by transforming the corresponding move values. The implementation additionally keeps an actual reachable flow at every discovered quotient state, so the saved paths contain genuine circuit moves; coordinate changes are not inserted as hidden steps.

Full graph encodings, edges, counts, paths, and independent checks are saved in [plateau_census_16.json](plateau_census_16.json). This completes the order-16 search that [the preceding report](repair-obstruction.md) deliberately stopped at its first strict-descent counterexample. That earlier partial result remains an accurate historical record.

## 3. A proved parallel-pair normalization

Let H contain an edge uv of flow value a. Replace it by external edges us and tv, each of value a, and two parallel edges st of values x and a+x. Call the expanded graph G. The internal choices require x≠0,a; up to swapping the parallel edges, there are three choices. This describes every nowhere-zero flow on such a two-vertex piece, since its two external values must agree by conservation.

**Suppression lemma.** For every nonzero normal ℓ,

\[
D_\ell(H)\le D_\ell(G),\qquad
D_\ell(G)-D_\ell(H)\in\{0,2\}.
\tag{1}
\]

**Proof.** The two inserted vertices have the same normal, so their total charge is zero. Use the component charge identity from [the previous report](repair-obstruction.md#2-a-structural-interpretation-of-the-obstruction).

- If ℓ(a)=1, both external edges are absent from the zero-coordinate subgraph and exactly one parallel edge is present. It forms an isolated, unobstructed two-vertex component. Suppression removes that component and changes no other obstruction.
- If ℓ(a)=0 and ℓ(x)=0, every edge of the inserted piece is present. Suppression replaces the connected piece by the edge uv. Removing two equal vertex normals does not change its component charge.
- If ℓ(a)=0 and ℓ(x)=1, both parallel edges are absent, leaving two external leaf edges. Suppression joins the corresponding components. If they were already connected, their charge is unchanged. Otherwise their two obstruction bits combine by XOR, so their contribution decreases by zero or two.

This proves (1). □

Now let b,c be the other two incident values at u, so b+c=a. Set the parallel-edge values to b,c. This is an **endpoint-normalized** expansion.

**Normalization lemma.** An endpoint-normalized expansion has exactly the same seven defect counts as H. Any other expansion can reach this one in at most one allowed move on the two-edge circuit, without increasing any defect count. Either endpoint can be used.

**Proof.** The cases ℓ(a)=1 and ℓ(a)=ℓ(b)=0 are already equalities in the suppression proof. In the remaining case, u has degree one in H_ℓ. In the expansion, us becomes a separate unobstructed edge component: u and s have the same normal. In the old component, the leaf u is replaced by t with that same normal, preserving its charge. Hence every defect count agrees.

To normalize an arbitrary internal pair x,a+x to b,c, add x+b on the two-edge circuit. Unless no change is needed, this is an allowed nonzero move: x+b equals neither x nor a+x because b≠0,a. Its endpoint has exactly the suppressed defect vector, which by (1) is componentwise no larger than the initial vector. □

The implementation checked every edge of the 195 flow classes on connected bridgeless simple cubic graphs through eight vertices. This gives 2,283 base-flow/edge pairs and all 6,849 unordered internal color-pair choices. Normalization at either endpoint and (1) pass in every case. See [parallel_reduction_results.json](parallel_reduction_results.json). As with the triangle lemma, the universal statement rests on the proof, not on these tests.

## 4. Why normalization does not settle the lifting problem

A smaller graph's repair move need not lift to a nonincreasing sequence in the expanded graph by the obvious construction. Here is a verified example.

On a ten-vertex base graph, the saved flow has potential (2,16). Adding 5 on the circuit with edge indices

```text
0 2 3 5 7 8 9 10 13 14
```

changes the potential to (0,14). Expand edge 6, the edge 2–5 of value 3, by a parallel pair of values 1 and 2. This is endpoint-normalized, so the expanded starting potential is also (2,16).

The base circuit avoids the expanded edge but visits both its endpoints. To preserve endpoint normalization after the base move, the parallel values must also be changed by adding 5, from {1,2} to {4,7}. The two updates are allowed circuit moves on disjoint circuit supports. In **both orders**, their potentials are

\[
(2,16)\longrightarrow(2,18)\longrightarrow(0,14).
\tag{2}
\]

Thus this direct lift crosses an increase, despite the strictly improving base move and the normalization lemma. A single circuit move cannot combine those two disjoint supports. This refutes that particular automatic lifting argument; it does not refute every possible inheritance theorem.

Indeed, the expanded graph has a different immediately improving move: add 3 on edge indices {4,5,7,8}. It reaches a successful flow and a verified five-layer cover. Consequently this example is not a closed unsuccessful plateau and is not a counterexample to the original conjecture.

The complete graphs, flows and both intermediate states are in [parallel_lift_obstruction.json](parallel_lift_obstruction.json); the verifier and alternative cover are in [parallel_reduction_results.json](parallel_reduction_results.json).

### Graph-level existence transfers without this difficulty

For the original existence problem, a five-layer cover of H extends directly to G. If uv belongs to layers i and j, give both external edges the same pair {i,j}. Choose a third layer k and give the two parallel edges the pairs {i,k} and {j,k}. Every inserted vertex has even degree in each layer and every edge is covered twice.

Conversely, a cover of G uses the same two layer indices on its two external edges: every even layer meets their two-edge cut evenly. Replacing them by uv with that layer pair gives a cover of H. Thus H has a five-layer cover if and only if G does.

This distinction matters for the research direction. We can perform graph reductions before choosing a starting flow and then extend a cover. Proving nonincreasing repair from *every* prescribed flow is a stronger requirement, and a failure of one such lifting argument need not block a proof of the original existence statement.

## 5. Two further limits on easy repairs

**Allowing a disconnected even subgraph in one same-value update does not restore strict descent.** On the earlier 16-vertex counterexample, I enumerated all 512 binary even subgraphs, including the empty one. There are 417 legal nonempty updates: 175 on single circuits and 242 on disconnected even subgraphs. None strictly improves (2,18). The same counterexample therefore defeats this enlarged strict-update rule. The complete check is included in [parallel_reduction_results.json](parallel_reduction_results.json).

**An available move does not imply a useful move.** Esperet and coauthors prove that nowhere-zero F₂³-flows cannot be isolated in the unrestricted reconfiguration graph. Their general connectivity theorem uses F₂⁸, not F₂³. Neither statement gives the potential-controlled paths needed here. [*Nowhere-zero flow reconfiguration*, Theorems 3.2 and 6.15, v4, July 3, 2026](https://arxiv.org/html/2512.17342v4)

The current missing theorem is still substantial: exclude every unsuccessful closed plateau on the relevant graph class, find a different repair method, or prove existence directly through the alternating-form formulation. The 16-vertex census and the local reduction lemmas do not settle that universal step.

## Reproduce

The complete 16-vertex plateau search requires Python, NetworkX 3.6.1, nauty `geng`, and a C++17 compiler:

```bash
python3 research/five-cdc-attempt/plateau_search.py --order 16
```

The recorded run took about 69 seconds on the current machine. Every graph's rank-two and rank-three subspace counts are checked, and the four actual escape paths and immediate neighborhoods are verified separately in Python.

Parallel-pair proofs' finite checks, the failed lift and its alternative cover, and the 417-update test:

```bash
python3 research/five-cdc-attempt/parallel_reduction.py
```

The latter command verifies the saved obstruction certificate directly; it does not need to repeat the exploratory search that located it.
