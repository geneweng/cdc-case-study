# Cut certificates for failed coordinate completion

Research date: **5 October 2026**.

The [coordinate-fiber approach](flow-space-components.md) now has a structural description of its failed linear tests. **Fixing two coordinates fails for a chosen first coordinate exactly when a pair of vertex cuts carries an odd forced parity.** This is an if-and-only-if theorem, with a direct graph certificate. The same dual space gives the exact number of completions when they exist. A single edge can sometimes supply the whole obstruction.

The limitation is equally concrete. An unmarked coordinate plane can still contain successful flow spaces: one explicit plane on the flower graph J₅ has **nine successful extensions among 64**, although all three first-coordinate tests inside the plane fail. Along the previously constructed two-circuit repair, the numbers of marked incident planes are **0, 0, 3**. Thus a failed plane test is not a certificate that its entire flow fiber avoids success.

This advances the obstruction analysis, without proving an escape theorem for arbitrary cores or the general 5-cycle double cover conjecture. No starting cover is assumed.

## 1. The fixed-coordinate problem

Let G be a connected loopless cubic graph, Z its binary cycle space, and F,y∈Z independent. Put

\[
T=\operatorname{supp}(F)\cup\operatorname{supp}(y),\qquad S=E(G)\setminus T.
\]

Assume the plane U=⟨F,y⟩ is **feasible**: there is a binary cycle z₀ equal to one on S. Its possible third coordinates form the affine space z₀+Z(T). Write d=dim Z(T). The associated flow is f=4F+2y+z.

For each component K of H=G−F, the canonical five-label lift requires

\[
\beta_K(y,z)=\sum_{e\in\delta_G(K)}y_ez_e=0.
\tag{1}
\]

These are linear conditions on z once F,y are fixed. The pair (F,U) specifies a test; replacing y by y+F leaves it unchanged, because a binary cycle meets every cut evenly. U is **marked** if at least one of its three choices of nonzero F passes its test.

A successful flow space need only have a successful first coordinate somewhere among its seven nonzero cycles. That coordinate need not lie in a particular incident plane U.

## 2. An exact paired-cut obstruction

For a vertex set A write δ(A)=δ_G(A); write δ_T(X)=δ_G(X)∩T. A set A is a union of components of H exactly when δ(A)⊆supp(F).

**Cut theorem.** The fixed-coordinate completion problem (1) has no solution in z₀+Z(T) if and only if there are vertex sets A,X with

\[
\begin{aligned}
\delta(A)&\subseteq\operatorname{supp}(F),\\
\delta_T(X)&=\operatorname{supp}(y)\cap\delta(A),\\
|\delta(X)\cap S|&\equiv1\pmod2.
\end{aligned}
\tag{2}
\]

In a cubic graph the last condition is equivalently **|X| odd**. Both formulations are checked in the saved certificates.

**Why a certificate forbids completion.** Put q=supp(y)∩δ(A). Summing (1) over the components contained in A gives q·z=0. On the other hand, a cycle z meets δ(X) evenly and equals one on S, so

\[
0=z\cdot\delta(X)=z\cdot q+|\delta(X)\cap S|=1,
\]

which is impossible.

**Why every failure has a certificate.** Define the linear map

\[
L:Z(T)\longrightarrow\mathbb F_2^{\,c(H)},\qquad
L(h)_K=\beta_K(y,h).
\]

Completion asks whether L(h)=L(z₀), where the same coordinate formulas define L(z₀). If this is inconsistent, elementary linear duality supplies a sum of output coordinates which vanishes on every L(h) but evaluates to one on L(z₀). Let A be the union of the corresponding components of H. Then q=supp(y)∩δ(A) is orthogonal to Z(T). The orthogonal complement of the cycle space of (V,T) is its cut space, so q=δ_T(X) for some X. Since z₀ is a cycle, q·z₀=|δ(X)∩S|, giving (2).

Finally, |q| is even because y is a cycle and δ(A) is a cut. Cubic degree parity gives |δ(X)|≡|X|. Hence |δ(X)∩S|≡|X|, proving the odd-vertex formulation. ∎

The certificate concerns the whole affine fiber for the specified F: changing z while keeping F,y cannot remove it. Changing the plane or using a first coordinate outside it can remove its relevance.

## 3. The dual space also counts completions

Let h=c(H), and identify unions of components of H with vectors in F₂ʰ. Define

\[
D_{F,y}=\{A:\delta(A)\subseteq\operatorname{supp}(F),\quad
\operatorname{supp}(y)\cap\delta(A)\text{ is a cut of }(V,T)\}.
\]

This is a binary vector space. For A∈D choose X with δ_T(X)=supp(y)∩δ(A), and set

\[
\chi(A)=|\delta(X)\cap S|\pmod2.
\]

This is well-defined: two choices of X differ by components of (V,T), and every such component has an even S-boundary because the feasible cycle z₀ equals one there. Equivalently, χ(A)=β_A(y,z₀), which also proves linearity and independence from the choice of feasible z₀.

The dual of L has kernel D, so

\[
\rho=\operatorname{rank}L=h-\dim D_{F,y}.
\]

Consequently the exact number of third-coordinate cycles completing this test is

\[
\boxed{\quad
N(F,y)=
\begin{cases}
2^{\,d-h+\dim D_{F,y}},&\chi\equiv0,\\
0,&\chi\not\equiv0.
\end{cases}\quad}
\tag{3}
\]

When completion fails, exactly half the elements of D have odd certificates. When it succeeds, a uniformly selected feasible z passes this fixed-F test with probability $2^{-\rho}$.

A useful sufficient condition follows immediately: **if D consists only of ∅ and V(G), completion succeeds.** Both have χ=0. More generally, success requires χ to vanish on all of D; it does not require the dual space to have its minimum dimension.

The formula counts third-coordinate cycles. On the non-three-edge-colorable cores considered here, each extension space ⟨F,y,z⟩ has four representatives z+U, so a successful fixed-F test yields N(F,y)/4 distinct extension spaces. Counts for different F can overlap.

## 4. A local obstruction on a single zero-projection edge

View the fixed projection U as a two-bit flow p=(F,y), allowing zero values. Feasibility forces its zero set S to be a matching: three zero projection values at a cubic vertex would force all three z-values to one, contradicting parity.

At a zero edge uv, the other two incident edges at u have the same nonzero projection color a; those at v have the same nonzero color b.

**Local obstruction lemma.** If a≠b, this edge blocks the unique nonzero first-coordinate functional ℓ with ℓ(a)=ℓ(b)=1.

**Proof.** Use ℓ as the first coordinate F and choose an independent second coordinate y. The two y-values on the F-edges at one end of uv are zero, and those at the other end are one. Take A={u,v}, and let X be the endpoint whose two y-values are one. Then δ(A) lies in F, δ_T(X)=y∩δ(A), and δ(X)∩S={uv}. This is (2), with X a single vertex. ∎

Thus three zero edges realizing all three unordered pairs of distinct nonzero projection colors block all three first-coordinate choices and certify that U is unmarked.

This is a sufficient local explanation, not a complete one. In the J₅ audit below, **315 failed tests have no such local blocker**. The plane with cycle codes (983,1465) has no local blockers at all but fails all three tests. The general paired-cut theorem detects these failures as well.

## 5. What happens on the two-circuit flower-graph repair

Use the edge order and fundamental cycle basis in [flow_space_components.json](flow_space_components.json). A cycle code is the bitmask of its coefficients in that basis; it is not an edge mask.

The previous certificate supplies a starting flow, a six-circuit switch, and then an eleven-circuit switch reaching success. Here are the new tests on those same states:

| State space key | Successful flow space? | Marked incident planes | Consistent fixed-F tests out of 21 |
|---|---|---:|---:|
| 4565596897686, initial | No | 0 | 0 |
| 4599956636054, after first switch | No | 0 | 0 |
| 4599947788694, after second switch | Yes | 3 | 3 |

Every failed test in this table has an explicit paired-cut certificate. Every passing test has a third coordinate, fourth coordinate, and independently checked decoded five-layer cover.

### An unmarked fiber containing successful extensions

The second switch preserves U=⟨406,1071⟩. Its three nonzero cycles are 406,1071,1465. The zero set is S={2,19,26}, and dim Z(T)=8, giving 2⁸/4=64 extension spaces.

All three fixed-F tests fail. Their dual dimensions are respectively 2,3,5; their completion-map ranks are 5,4,5. Nevertheless **nine of the 64 extension spaces are successful**. The saved endpoint succeeds with first cycle **577**, which lies outside U.

For F=1465 and y=406, the failure already has the local certificate

\[
A=\{0,12\},\qquad X=\{12\}.
\]

Its cuts in the saved edge order are

\[
\delta(A)=\{0,1,4,7\},\quad
\delta(X)=\{2,4,7\},\quad
y\cap\delta(A)=\{4,7\},\quad
\delta(X)\cap S=\{2\}.
\]

The other two first-coordinate failures in this plane require the more general certificates; its three local blockers all block F=1465.

### A usable alternative, with an explicit scope limit

The initial state has exactly 185 distinct neighboring spaces under a whole fiber round. None is already successful, as independently checked. Of these neighbors, **181 have at least one marked incident plane**; the remaining four include the intermediate state used by the saved repair.

Therefore, on this particular state, one can first reach a neighbor with a marked plane and then solve its linear completion system. This is an alternative two-round repair, with the earlier bound of at most eight actual circuits. It does not prove that every unsuccessful state on an arbitrary core has such a neighbor.

The path 0→0→3 does not refute every rule that strictly increases the number of marked planes: this initial state has many alternative neighbors which do increase it. It shows precisely that having no marked incident plane does not distinguish fiber distance one from fiber distance two to success.

## 6. Independent checks

The [constructor](fiber_cut_obstructions.py) uses Gaussian elimination on the component-cut equations. An inconsistent row combination supplies A and X. It obtains completion ranks from linear equations.

The [independent verifier](verify_fiber_cut_obstructions.py) imports no constructor code. It enumerates binary cycles z and all possible restrictions of a fourth cycle to F, counting completions directly. It computes the image of the homogeneous completion map by enumeration. For all 63 saved path tests it also enumerates every union A of complement components and solves the signed edge conditions for X by graph traversal, independently checking the dual dimension and the odd/even split. Local blockers are rebuilt from endpoint incidence conditions, without using the constructor's projection-functional selection.

| Audit scope | Feasible planes | Marked planes | Fixed-F tests | Passing tests | Failed tests with a local blocker | Failed tests without one |
|---|---:|---:|---:|---:|---:|---:|
| All feasible Petersen planes | 400 | 335 | 1,200 | 375 | 600 | 225 |
| J₅ planes incident to the initial state, its 185 neighbors, and the saved path | 1,076 | 532 | 3,228 | 594 | 2,319 | 315 |

Petersen supplies another sharp distinction: all its 170 full-support three-spaces are successful, although 65 feasible planes are unmarked. The J₅ audit is a specified neighborhood, not a census of all its 252,490 feasible planes.

The [certificate](fiber_cut_obstructions.json) records source hashes, exact counts, hashes of ordered test records, all 63 path tests, every local blocker on those path planes, the 185-neighbor distribution, and all nine successful extensions of the highlighted unmarked fiber. The verifier also checks the two actual circuit moves and their state keys. Reproduce with Python 3 and the standard library:

```bash
python3 -B research/five-cdc-attempt/fiber_cut_obstructions.py
python3 -B research/five-cdc-attempt/verify_fiber_cut_obstructions.py
```

## 7. The remaining structural task

The existence target can now be stated entirely in graph terms: **find a feasible plane and a nonzero F in it for which every paired cut has even X**. By the earlier five-label encoding this supplies a cover, and every five-layer cover supplies such a choice. No theorem here guarantees that choice on an arbitrary core.

For the stronger all-starting-flow repair approach, a closed incidence component avoiding marked planes remains the relevant obstruction. Paired cuts explain every failed mark inside a component, but they do not yet give a way to change planes that must eventually reach a mark. The next useful step is to understand how these certificates behave under plane changes, including the nonlocal certificates that survive after the single-edge blockers have disappeared. An unmarked plane by itself must not be pruned as a fiber without successful states.

Follow-up: [How cut certificates change under circuit switches](cut-certificate-transport.md) proves an exact survival rule and escape from every individual certificate. An explicit complete replacement example shows why that escape does not guarantee completion; vertex-normal charges provide an exact way to track the current flow under switches.
