# A counterexample to strict repair, and a triangle reduction

**29 September 2026. The lexicographic repair lemma proposed in the earlier notes is false. The 5-cycle double cover conjecture is not refuted or proved by this work.**

**Later continuation:** [Neutral repair and parallel-edge reductions](neutral-repair.md) completes the order-16 census, verifies a neutral escape for every strict local minimum, and proves a parallel-pair normalization lemma while identifying a separate lifting obstruction. The strict-descent counterexample below remains valid.

The counterexample has 16 vertices. Every allowed single-circuit move leaves the potential unchanged or increases it. A neutral move followed by a second move produces a verified five-layer cover. This supplies the missing counterexample to the earlier proof strategy and shows why a repair argument must allow neutral steps, change its potential, or restrict its domain.

There is also a general structural result: a flow on a triangle can be normalized and the triangle contracted without increasing any of the seven defect counts. The proof below explains how neutral steps can be useful. The elementary deductions are supplied without a claim of novelty over the full literature.

## 1. The 16-vertex counterexample

Keep the definitions in [the original attempt](attempt.md): D_ℓ(f) counts obstructed components of H_ℓ=(V,{e:ℓ(f_e)=0}), and

\[
\Psi(f)=\left(\min_{\ell\ne0}D_\ell(f),\sum_{\ell\ne0}D_\ell(f)\right).
\]

An allowed move adds a nonzero vector a to the edge values on a circuit Q, provided a does not already occur on Q. Values are integers 1–7 encoding vectors of F₂³; addition is XOR.

Here is a connected bridgeless simple cubic graph and a nowhere-zero flow:

| Edge index | Edge | Flow | Edge index | Edge | Flow |
|---:|---|---:|---:|---|---:|
| 0 | 0–7 | 3 | 12 | 4–10 | 4 |
| 1 | 0–9 | 5 | 13 | 4–11 | 3 |
| 2 | 0–10 | 6 | 14 | 4–12 | 7 |
| 3 | 1–8 | 5 | 15 | 5–11 | 2 |
| 4 | 1–13 | 7 | 16 | 5–12 | 1 |
| 5 | 1–14 | 2 | 17 | 5–14 | 3 |
| 6 | 2–8 | 3 | 18 | 6–12 | 6 |
| 7 | 2–14 | 1 | 19 | 6–13 | 2 |
| 8 | 2–15 | 2 | 20 | 6–15 | 4 |
| 9 | 3–9 | 7 | 21 | 7–9 | 2 |
| 10 | 3–10 | 2 | 22 | 7–11 | 1 |
| 11 | 3–13 | 5 | 23 | 8–15 | 6 |

Its graph6 encoding is `O???C@_cSo@gB_S_K_@D?`. The defect vector and potential are

\[
(D_1,\ldots,D_7)=(2,4,2,2,2,2,4),\qquad\Psi(f)=(2,18).
\]

There are exactly 229 circuits and 175 distinct allowed neighboring flows. Their complete potential histogram is:

| Neighbor potential | Count |
|---|---:|
| (2,18) | 35 |
| (2,20) | 51 |
| (2,22) | 26 |
| (2,24) | 31 |
| (2,26) | 29 |
| (2,28) | 1 |
| (2,30) | 2 |

Thus **no allowed single-circuit move decreases Ψ**. This is a counterexample to the stated universal repair lemma.

The previous exhaustive check covered every connected bridgeless simple cubic graph of orders 4 through 14. Cubic graphs have even order. Consequently 16 is the smallest possible order for this kind of counterexample within that class, according to the saved exhaustive computations. This minimality conclusion is computational, not a separate structural proof, and makes no claim about multigraphs.

### An explicit escape and cover

First add 5 on circuit edge indices {13,14,15,16}, the four-cycle 4–11–5–12–4. The seven defect counts remain unchanged. Then add 1 on circuit edge indices {1,2,4,5,9,11,12,13,15,17}. This gives

\[
(2,18)\longrightarrow(2,18)\longrightarrow(0,18).
\]

The final defect vector is (0,2,4,2,4,4,2). After a change of coordinates, the extra-coordinate solver constructs these five layers, expressed as edge-index sets:

```text
0: 7 8 9 11 15 17 19 20 21 22
1: 3 4 10 11 12 14 18 20 23
2: 0 1 4 5 6 8 16 17 18 19 21 23
3: 1 2 9 10 13 14 15 16
4: 0 2 3 5 6 7 12 13 22
```

Every edge belongs to exactly two listed layers and every vertex has even degree in each layer. The graph therefore has a five-layer CDC; it is not a counterexample to the original conjecture.

### Independent verification

The C++ search found the example. The older Python implementation then exhausted its neighborhood using fundamental-cycle-space enumeration. A third verifier, [verify_lex_trap.py](verify_lex_trap.py), uses only Python's standard library, enumerates circuits by simple-path depth-first search, and computes the component-cut parities directly. It independently verifies connectedness, absence of bridges, the 229 circuits, all 175 neighbors, the two moves, and the exact cover above.

The complete certificate is [lex_census_trap_certificate.json](lex_census_trap_certificate.json); the independent check is [independent_trap_verification.json](independent_trap_verification.json). No numerical tolerances or randomized assertions are used.

## 2. A structural interpretation of the obstruction

For each vertex v, let p,q be two incident flow values. Define the **vertex normal**

\[
\nu_v=p\times q\in\mathbb F_2^3.
\]

The usual three-coordinate cross product is evaluated in characteristic two. The three incident values are p,q,p+q, so this definition does not depend on the chosen pair. It is the unique nonzero vector orthogonal to their two-dimensional span.

**Component charge identity.** If K is a component of H_ℓ with obstruction bit b_K, then

\[
\sum_{v\in K}\nu_v=b_K\ell.
\tag{1}
\]

**Proof.** Write the three binary flow coordinates as x,y,z. At a cubic vertex, conservation gives

\[
\nu_v=\bigl(B(yz)_v,\ B(zx)_v,\ B(xy)_v\bigr),
\]

where products are coordinatewise on edges. For example, if the first two incident values have y,z coordinates (p_y,p_z),(q_y,q_z), then the sum of yz on all three incident edges is p_yq_z+q_yp_z, the relevant cross-product coordinate. Summing over K leaves only its cut.

Choose coordinates with ℓ selecting the first coordinate x, so x=1 on δ(K). The last two cut sums are then ∑z and ∑y, both zero because y,z are binary cycles. The first cut sum ∑yz is the common parity of the four boundary color counts, namely b_K. Transforming coordinates back proves (1): cross products and normals both transform by the inverse transpose, since every invertible binary matrix has determinant one. □

At a vertex, H_ℓ has degree three if ν_v=ℓ and degree one otherwise. Therefore a component containing no vertex of normal ℓ is a single edge. Such an edge component is obstructed exactly when its endpoint normals differ. Conversely, every edge uv with ν_u≠ν_v gives exactly one such component, for ℓ=ν_u+ν_v.

It follows that the second potential coordinate has the exact decomposition

\[
\sum_\ell D_\ell(f)
=\bigl|\{uv\in E:\nu_u\ne\nu_v\}\bigr|+R(f),
\tag{2}
\]

where R(f) counts obstructed components containing a vertex of their own normal ℓ. In particular 0≤R(f)≤|V|. Equation (2) separates ordinary disagreements of adjacent vertex normals from a component-parity correction. Controlling that correction remains necessary; minimizing adjacent disagreements alone is not a proof of 5-CDC.

## 3. A proved triangle-flattening lemma

Let A,B,C induce a triangle in a bridgeless cubic graph, with one external edge at each vertex. Write their external flow values as a,b,c=a+b. They are distinct and nonzero. The triangle's internal values have the form

\[
f(AB)=t,\qquad f(AC)=t+a,\qquad f(BC)=t+b.
\]

Exactly five choices of t are allowed: t=c and the four vectors outside P=⟨a,b⟩. Call the t=c choice **flat**. Its internal edges equal the opposite external values, and all three vertex normals equal ν=a×b.

**Lemma.** Any nonflat choice can be made flat by one allowed circuit move on the triangle. This move does not increase any D_ℓ; each decreases by either zero or two. The flat triangle can then be contracted to one vertex without changing any D_ℓ.

**Proof of the move.** Add t+c on the triangle. It is nonzero and differs from all three existing internal values, because c is distinct from 0,a,b. The resulting internal values are c,b,a, so the move is allowed and makes the triangle flat.

The three original vertex normals sum to ν. This follows directly from ν_A=a×t, ν_B=b×t and ν_C=c×(t+a). The three flat normals also sum to ν.

Fix ℓ and examine H_ℓ.

- **If ℓ=ν:** all external edges lie in H_ℓ. Before flattening none of the triangle edges does; afterwards all three do. The move merges between one and three old components. Their obstruction bits combine by XOR, because internal cut contributions cancel. The number of obstructions drops from the number of odd old components to its parity, a decrease of zero or two.
- **If ℓ≠ν:** exactly one external edge belongs to H_ℓ; rename its port A, with a,b,c,t renamed accordingly. If ℓ(t)=0, the triangle's H_ℓ-edges initially form the path B–A–C attached to that port. Afterwards B–C is a separate unobstructed edge component, while A remains attached to the external component. The total normal contribution to that external component remains ν, so its obstruction is unchanged by (1).
- In the remaining case, ℓ(t)=1, both before and after the move B–C is a separate edge component and A is attached externally. Initially the B–C component is obstructed; afterwards it is not. The charge of A's component flips by ℓ. If its previous obstruction bit was b, the change in D_ℓ is from 1+b to 1−b, a decrease of 2b.

After flattening, contraction merges the triangle internally when ℓ=ν. When ℓ≠ν it deletes the unobstructed B–C edge component and identifies the remaining port vertex with the contracted vertex. The charge identity shows that the remaining obstruction bits agree with those in the contracted graph. Hence every D_ℓ is preserved by contraction. □

Contraction may introduce parallel edges; the statement allows loopless cubic multigraphs. It does not imply that an arbitrary nonflat triangle gives a *strict* improvement. In the counterexample, flattening triangle {0,7,9} by adding 4 leaves all seven defect counts unchanged.

### Moves on the contracted graph lift back

Suppose the triangle is flat and a circuit move on the contracted graph uses two of its external ports, A and B. Replace the contracted vertex on that circuit by the internal path A–C–B. Those two internal edges carry exactly the old external values at B and A. The move's added vector avoids those values already, so the lifted move is allowed. The internal edges and external ports change together, keeping the triangle flat. If the contracted circuit avoids the vertex, no replacement is needed.

Thus every contracted move lifts to one move preserving flatness and the contracted graph's defect vector. In particular, if the contracted flow has an improving move, the original flow has a sequence of at most two moves—flatten, then lift—in which Ψ never increases and eventually decreases. If flattening is already strict, the first move suffices.

**Inheritance corollary.** Suppose every nowhere-zero three-bit flow on a graph H can reach a successful flow through moves that never increase Ψ. Then the same statement holds for every graph obtained from H by any finite sequence of vertex-to-triangle expansions. For one expansion, normalize its triangle, contract to H, use the assumed sequence on H, and lift every move as above. Induction gives the iterated statement. This is a proved reduction of the reachability property. Combined with the earlier finite checks, it applies to arbitrary iterated triangle expansions of the 587 checked simple cores through 14 vertices, among other cores; this application depends on those computer checks.

This is a valid reduction for repair sequences, not a proof that such sequences always reach a successful flow on triangle-free graphs. In the saved counterexample, the triangle-based construction uses one neutral flattening and two lifted moves to obtain another verified five-layer cover. The separate four-cycle escape in Section 1 uses only two moves in total.

The implementation checks the normal identity and exhausts all five triangle extensions at every vertex of every nowhere-zero flow class on the eight connected bridgeless simple cubic graphs through eight vertices: 195 base flow classes, 7,610 extensions, including 6,088 nonflat cases. The componentwise monotonicity and contraction identity pass in every case. See [triangle_repair_results.json](triangle_repair_results.json). The general lemma rests on the proof above, not on those finite tests.

## 4. What the larger search established

The native engine was first checked against every one of the 589 earlier graph records. Circuit counts, total subspace counts, nowhere-zero flow-class counts, repair-needed counts and outcomes all agree with the independent Python implementation.

It then completed all flow classes on the six 20-vertex snarks of girth at least five and cyclic edge-connectivity at least four. The six graphs were generated locally by `geng`, followed by exact edge-coloring and cut filters. All 3,687,100 flow classes passed the proposed repair rule; 2,985,888 of them required repair. [Results](native_repair_results.json)

Nevertheless, the broader 16-vertex search found the counterexample above. It generated the complete list of 4,060 connected simple cubic graphs, then stopped after inspecting 671 bridgeless graphs, with the last graph's flow enumeration only partial. It checked 15,961,951 flow classes before stopping. **This is not a completed 16-vertex census.** The counterexample is in [native_census_16.json](native_census_16.json).

The contrast matters: millions of successful examples, including harder-looking snarks, did not justify the universal strict-descent lemma. Restricting a new candidate to an appropriate graph class may still be useful, but would require a proof that the reduction preserves the needed property. The triangle lemma supplies one such reduction for nonincreasing sequences; the rest of that program remains unfinished.

The exact alternating-form and linear-completion formulations in [continuation.md](continuation.md) remain valid. What fails is the proposed argument for always reaching a successful flow by strictly decreasing Ψ at every move.

## Reproduce

Fast, standalone verification of the counterexample and its cover:

```bash
python3 research/five-cdc-attempt/verify_lex_trap.py
```

Structural checks and reconstruction of the triangle-based repair:

```bash
python3 research/five-cdc-attempt/triangle_repair.py
```

Native searches require a C++17 compiler, NetworkX 3.6.1 and nauty `geng`:

```bash
python3 research/five-cdc-attempt/native_repair.py
python3 research/five-cdc-attempt/native_census.py --order 16
```

Compilation keeps assertions enabled. The C++ binaries are temporary and are not stored in the repository. Native search ordering differs from the earlier Python search, so neighbor counts examined before finding an improvement need not agree; the complete subspace and flow-class counts do agree.
