# A reusable algebraic framework for graph existence problems

Companion to the [research report](README.md), 29 September 2026.

The linear-algebra results below are elementary deductions, not claims of new research theorems. The specialization to CDC follows the supplied OpenAI proof and Oum's exposition. The sheaf terminology is standard; the interpretation of this specific CDC construction in that language is explanatory synthesis.

## 1. Start from a local representation of the desired object

Suppose that at each vertex v, valid local configurations can be described by a parameter x_v in a finite-dimensional vector space V_v, or an affine space modeled on V_v. Choose an origin when necessary.

The parameters need not be the original edge-incidence bits. That flexibility is crucial: exact combinatorial constraints may be nonlinear in the original variables but automatic in an alternative local template.

For every oriented edge e:u→v, suppose agreement of the local descriptions is equivalent to

\[
R_{v,e}x_v-R_{u,e}x_u=b_e\in Q_e,
\tag{A1}
\]

where the R_(v,e) are linear maps and Q_e is a comparison space. An explicit decoder must turn every compatible parameter assignment into a valid graph object. For an equivalence, one additionally needs every desired object to admit such a representation; a sufficient construction needs only the forward decoding implication.

**Scope:** this setup captures local affine agreement. It does not assert that every graph problem has such a representation of manageable size.

## 2. Assemble the equations

Define

\[
C^0=\bigoplus_{v\in V}V_v,
\qquad C^1=\bigoplus_{e\in E}Q_e,
\qquad \delta:C^0\longrightarrow C^1
\]

by (δx)_e=R_(v,e)x_v−R_(u,e)x_u. The graph problem, within the chosen representation, asks for δx=b.

Choose bases if an explicit matrix is wanted. Each edge contributes a block row, with nonzero blocks only at its two endpoints. All graph dependence and all local-template dependence remain visible in the matrix.

## 3. Dual feasibility theorem

Let Q_e* denote the algebraic dual space. A dual assignment y=(y_e) belongs to ker δ* precisely when, at every vertex,

\[
\sum_{e\text{ entering }v}R_{v,e}^*y_e
-\sum_{e\text{ leaving }v}R_{v,e}^*y_e=0.
\tag{A2}
\]

Then

\[
\delta x=b\ \Longleftrightarrow\
\sum_e y_e(b_e)=0\text{ for every }y\text{ satisfying (A2)}.
\tag{A3}
\]

**Proof.** Necessity follows from y(δx)=(δ*y)(x)=0. For sufficiency, if b is outside im δ, extend a basis of im δ by b and then to a basis of C¹. Define a linear functional that is zero on im δ and takes value one on b. It belongs to ker δ* but contradicts the right side of (A3). This works over every field.

For a consistent system, every solution is x₀+z for z∈ker δ. Over F_q the solution count is therefore q^(dim C⁰−rank δ). Gaussian elimination either returns a solution or an explicit dual certificate with y(b)≠0.

The theorem is generic. A universal graph theorem needs additional structure proving that its particular b satisfies (A3).

## 4. A sufficient local cancellation criterion

Write b_e=a_(v,e)−a_(u,e), where a_(v,e)∈Q_e are local offsets. Such offsets normally come from the two local templates being compared. Set σ_(v,e)=+1 at the head and −1 at the tail of e. Then

\[
\langle y,b\rangle
=\sum_v\sum_{e\ni v}\sigma_{v,e}\,y_e(a_{v,e}).
\tag{A4}
\]

Suppose that for every dual assignment satisfying (A2), the local contribution at each vertex can be rewritten as

\[
\sum_{e\ni v}\sigma_{v,e}\,y_e(a_{v,e})
=\sum_{e\ni v}\sigma_{v,e}\,q_e(y_e),
\tag{A5}
\]

where the same edge function q_e is used at both endpoints. The q_e need not be linear. Summing (A5) cancels every edge contribution, so y(b)=0. By (A3), a global solution exists.

Over F₂, signs disappear and the right side contributes the same quantity twice per edge. The useful discovery is the local identity (A5), not the final double count.

This criterion is sufficient, not a claimed classification of all ways to prove feasibility. A different proof may eliminate dual obstructions without such a local decomposition.

## 5. CDC as a specialization

Let Γ=F₂³ and fix a nowhere-zero Γ-flow f on a loopless cubic graph. Put

\[
V_v=\Gamma,\qquad Q_e=\Gamma/\langle f(e)\rangle,
\]

and let R_(v,e) be the quotient map. At v choose c_(v,e) as the flow on either of the other two incident edges. The two choices differ by f(e), so their images in Q_e agree. Set

\[
a_{v,e}=c_{v,e}+\langle f(e)\rangle,
\qquad b_e=a_{u,e}+a_{v,e}.
\]

Equation δt=b means t_u+t_v+c_(u,e)+c_(v,e) lies in ⟨f(e)⟩. This is the edge-pair agreement equation.

A dual functional on Q_e corresponds, via the standard nondegenerate dot product, to a vector h_e∈Γ with h_e·f(e)=0. Condition (A2) becomes

\[
\sum_{e\ni v}h_e=0.
\]

The CDC local identity is

\[
\sum_{e\ni v}h_e\cdot c_{v,e}
=\sum_{e\ni v}\mathbf1_{h_e\ne0}\quad\text{in }\mathbb F_2.
\tag{A6}
\]

Thus q_e(h)=1_(h≠0) supplies (A5). The decoded edge label is the two-element affine line

\[
P_e=t_v+c_{v,e}+\langle f(e)\rangle.
\]

For each s∈Γ, take H_s={e:s∈P_e}. Local validity gives degree zero or two in every H_s, so each H_s splits into circuits; |P_e|=2 gives exact double coverage.

The full proof additionally needs an existence theorem for the input flow and graph reductions preserving the desired cover conclusion. Linear algebra alone does not provide those ingredients. [Supplied proof, Lemmas 2.1–2.2](../cdc_proof.pdf); [Oum, §§2–7](../2607.16356v3.pdf)

## 6. What cohomology records here

The spaces and restriction maps form a cellular sheaf on the graph. With no two-dimensional cells, the cochain complex is

\[
0\longrightarrow C^0\xrightarrow{\delta}C^1\longrightarrow0.
\]

Consequently H⁰=ker δ and H¹=coker δ. The affine problem δx=b asks whether [b]=0 in H¹. Different b can give different answers for the same δ. This is a standard interpretation of local compatibility systems; see [Hansen–Ghrist](https://doi.org/10.1007/s41468-019-00038-7).

For the CDC quotient system on a cubic graph, dim C⁰=dim C¹=3n. Every constant t_v=t lies in ker δ, giving at least three dimensions. Hence H¹ is not zero. The proof singles out a solvable affine translate; it does not eliminate the entire obstruction space.

**Finite-field caution.** Do not replace the duality argument by a real Hodge-Laplacian argument without checking it. Over F₂, AᵀA may have a larger kernel than A. For example A=(1,1)ᵀ has trivial kernel, but AᵀA=(0). The Euclidean identity ker(AᵀA)=ker A relies on positivity, absent here. Work directly with im A, ker Aᵀ, and algebraic dual spaces.

## 7. A graph-level witness that higher-dimensional lifting fails

The following example was generated and verified by the companion script. Write vectors of F₂⁴ as integers 0–15, with addition implemented by XOR. Let G=K₃,₃ with left vertices 0,1,2 and right vertices 3,4,5. At every vertex, cycle through its incident edges in their order in this table when selecting c_(v,e)=f(next edge).

| Edge | Flow f(e) | Dual vector h_e |
|---|---:|---:|
| 0–3 | 15 | 15 |
| 0–4 | 2 | 13 |
| 0–5 | 13 | 2 |
| 1–3 | 5 | 15 |
| 1–4 | 12 | 13 |
| 1–5 | 9 | 2 |
| 2–3 | 10 | 0 |
| 2–4 | 14 | 0 |
| 2–5 | 4 | 0 |

At every vertex both the f-values and h-values sum to zero. Every f(e) is nonzero, and h_e·f(e)=0 for all edges. Nevertheless,

\[
\sum_{e=uv}h_e\cdot(c_{u,e}+c_{v,e})=1.
\]

So h is an explicit certificate that this alignment system is inconsistent. This is an elementary, independently checkable counterexample to universal lifting of arbitrary F₂⁴-flows, not a counterexample to CDC. The JSON records the corresponding scalar equation indices whose XOR gives 0=1.

## 8. A practical workflow for another conjecture

1. Define precisely what must be preserved: coverage, signs, prescribed circuits, number of layers, number of components, or matching degrees.
2. Find local templates that satisfy the difficult exact constraints by construction.
3. Prove the decoder is sound. Check completeness separately if claiming equivalence.
4. Determine which variables must be fixed before compatibility becomes affine.
5. Write the compatibility matrix and describe its left kernel in graph terms.
6. Compute small infeasibility certificates. Use them to reject overly strong claims and to suggest the missing structural hypothesis.
7. Seek a cancellation identity, a structural decomposition of all certificates, or a way to select the auxiliary data so every obstruction vanishes.
8. Prove graph reductions preserve all extra requirements, not just ordinary CDC existence.

The output sought is an implication with explicit hypotheses and a valid decoding argument. A successful encoding, a fast solver on examples, and a proof for every graph are three different achievements.
