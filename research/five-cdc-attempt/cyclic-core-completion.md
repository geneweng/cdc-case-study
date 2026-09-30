# Coordinate selection on a cyclically four-edge-connected graph

**29 September 2026. The general 5-cycle double cover conjecture remains unproved here. This report gives a certified result for one specified graph and a counterexample to a stronger proposed algebraic shortcut. No claim of novelty over the complete literature is made.**

The next test is Hägglund's 34-vertex graph Blowup(K₄,C₃), which has no cyclic edge cut of size below four. The outcome separates two possible selection rules:

- **The sum-free shortcut fails.** There is a nowhere-zero F₂³-flow with three supports F₁,F₂,F₃ satisfying F₁△F₂=F₃, none of which can be a whole layer of a five-layer cover. All three are nonspanning even subgraphs. Independently checked nonexistence proofs are supplied.
- **The seven-choice rule holds on this entire graph.** Every nowhere-zero F₂³-flow on it has at least one coordinate support that is a whole layer of a five-layer cover. This is proved by an exhaustive certificate over its binary cycle space, without enumerating all three-bit flows.

The second conclusion is specific to this graph. It does not prove the seven-choice rule for all cyclically 4-edge-connected graphs, or the general 5-CDC conjecture.

## The graph and why it is a useful test

Use Hägglund's [Construction 2](https://arxiv.org/html/1203.2015v1#S2), applied to the triangle 0,1,2 of K₄. Each of three four-poles Bᵢ is a Petersen graph with adjacent vertices 0,1 removed. In the repository's Petersen labeling, its port pairs are a=(4,5) and b=(2,6). Delete the base triangle edges, add vertices uᵢ,wᵢ, and connect

\[
v_i u_i,\quad v_i w_i,\quad u_i b_1^i,\quad w_i b_2^i,
\quad a_1^i u_{i+1},\quad a_2^i w_{i+1},
\]

with indices modulo three. Together with the retained K₄ edges and internal four-pole edges, this gives 34 vertices and 51 edges. The complete ordered edge list is in the certificate.

This is a known graph. Hägglund reports that no spanning 2-factor of it can be a member of a 5-CDC, and also reports the stronger obstruction for unrestricted CDCs. We do not claim either result as new. [Hägglund, §4](https://arxiv.org/html/1203.2015v1#S4)

Our verifier independently examines all **22,151 sets of one, two, or three deleted edges**. Exactly 34 disconnect the graph, all consisting of the three edges incident with one vertex. Each displayed Petersen four-pole has a four-edge boundary separating an eight-vertex side from a 26-vertex side, both containing circuits. Thus the cyclic edge connectivity is exactly four. The two- and three-edge-cut mechanisms from the preceding reports do not apply.

## Three failed coordinates in one actual flow

In the certificate's edge order, the three binary coordinates of the witness flow have the following support masks. Bit e denotes membership of edge e:

\[
A=\mathtt{0x2b7fbbfc67ce},\qquad
B=\mathtt{0x799f87cb3bc70},\qquad
C=\mathtt{0x544a000da125}.
\]

Define

\[
f(e)=\mathbf1_A(e)+2\mathbf1_B(e)+4\mathbf1_C(e).
\]

Direct verification checks XOR conservation and nonzero values on every edge. The complete seven-coordinate classification for this flow is:

| Normal ℓ | Edges in Fℓ | Circuit components | Components of G−E(Fℓ) | Five-layer completion |
|---|---:|---:|---:|---|
| 1 | 33 | 4 | 16 | Impossible, proof supplied |
| 2 | 30 | 3 | 13 | Impossible, proof supplied |
| 3 | 33 | 4 | 16 | Impossible, proof supplied |
| 4 | 15 | 1 | 2 | Explicit cover supplied |
| 5 | 32 | 3 | 15 | Explicit cover supplied |
| 6 | 31 | 1 | 14 | Explicit cover supplied |
| 7 | 30 | 2 | 13 | Explicit cover supplied |

In particular F₁=A, F₂=B, and F₃=A△B are all failed **admissible** supports from the same flow. None is a spanning 2-factor, which would have 34 edges. Their failures therefore require more than citing the known spanning-2-factor obstruction.

This disproves the conjectural sum-free property of failed admissible supports even on cyclically 4-edge-connected graphs. That property held in the [previous saved census](three-cut-completion.md#the-saved-census-implies-much-stronger-finite-success). It also disproves the rule that every two-dimensional subspace of an admissible three-flow's coordinate space must contain a completable nonzero support.

It does **not** disprove selection among all seven coordinates: the other four succeed in this witness. Nor do the supplied negative proofs exclude covers with more than five layers containing A, B, or A△B.

## A precise encoding of nonexistence

Introduce Boolean variables xₑ,ᵢ for the five named layers i=0,…,4. The formula requires:

1. Exactly two of xₑ,₀,…,xₑ,₄ are true for each edge e.
2. For each vertex and each layer, the three incident variables have even parity.
3. xₑ,₀ is fixed to the prescribed support F.

Because the graph is cubic, even parity means degree zero or two. Thus satisfying assignments are **exactly** five-layer CDCs with F as one whole layer; disconnected and empty layers are allowed. There is no assumption that the cover arises from a particular flow, component coloring, or repair family.

For an edge, the five positive clauses obtained by omitting one variable at a time enforce at least two true variables. The ten negative clauses on all triples enforce at most two. Four clauses forbid the odd assignments at each vertex-layer triple. There are 255 variables and 1,445 clauses before the 51 fixed-layer units are added.

Glucose produces a DRUP proof for each of the three failed supports. A separate standard-library checker reconstructs the formula and verifies every added clause by **reverse unit propagation**: negate the proposed clause and propagate unit clauses until a contradiction occurs. Each proof ends by deriving the empty clause. In total it verifies **1,695 clause additions**. It safely retains clauses that the solver's log deletes; all retained clauses have already been justified.

The checker also exhausts the small truth tables for the edge and vertex encodings. Consequently the negative conclusions depend on these explicit encodings and checked deductions, rather than merely on a solver reporting “UNSAT.” DRUP logging is documented by the [PySAT solver API](https://pysathq.github.io/docs/html/api/solvers.html).

## Certifying the seven-choice rule through the binary cycle space

Let Z be the binary cycle space of a cubic graph, and let \(\mathcal C\subseteq Z\) be any collection of supports for which explicit five-layer completions have been supplied. Put R=Z∖\(\mathcal C\). Members of R may be treated as unknown; no nonexistence assertion is necessary.

**Cycle-space criterion.** If R contains no nonzero part of a two- or three-dimensional binary subspace whose union is the entire edge set, then every nowhere-zero F₂³-flow has a coordinate support in \(\mathcal C\).

**Proof.** The three coordinate rows of a flow span a subspace W⊆Z. Since the flow is nowhere zero, the union of W's supports contains every edge. Its rank is two or three: rank one would put the same nonzero value on all edges, violating conservation at a cubic vertex. Every nonzero member of W is a coordinate support for some nonzero normal. If none belonged to \(\mathcal C\), its whole nonzero part would lie in R, contrary to the hypothesis. □

This is a reusable algebraic certificate for a graph-level selection statement. It separates finding completions from checking whether the remaining cycles can form a full-support flow space. It is a sufficient criterion for the strong rule concerning **every starting flow**, and is stronger than what is needed merely to construct one five-layer cover.

### Exhaustive certificate for the 34 vertex graph

The cycle-space dimension is 51−34+1=18. The constructor tests all 2¹⁸=262,144 even subgraphs. It saves one explicit completion for **257,638** of them. The remaining **4,506** supports form R.

The positive theorem does not trust the solver's negative answers on R. The independent verifier treats all those supports as unclassified and checks only the following:

- The supplied 18 cycles form a basis, so all binary even subgraphs are accounted for.
- Every saved cover has even layer degrees, exact edge multiplicity two, and precisely its claimed first layer.
- Every code outside R appears exactly once in the cover table.
- No two- or three-dimensional subspace with its nonzero part in R has full edge support.

The final exhaustive subspace counts are:

| Dimension | Subspaces whose nonzero members all lie in R | Have full edge support |
|---|---:|---:|
| 2 | 299,591 | 0 |
| 3 | 1,657,689 | 0 |

Every listed three-dimensional subspace misses at least two edges. Such subspaces therefore do exist inside R, but none defines a nowhere-zero flow on the entire graph. Ignoring the full-support condition would produce false counterexamples to selection.

For completeness of the subspace enumeration, order cycles by their binary basis codes. In each subspace choose a as its least nonzero member, b as the least member outside ⟨a⟩, and c as the least member outside ⟨a,b⟩. For a candidate a, form R∩(R+a). A rank-three candidate must contain b,c in this intersection and also b+c in it. These tests account for all seven required members. The least-member conditions give exactly one visit per subspace. Both implementations check the full edge union explicitly.

The cycle-space criterion now proves the stated finite theorem: **every nowhere-zero F₂³-flow on this graph has a coordinate admitting a five-layer completion**. This is more than testing a sample of flows, but remains a theorem about this one graph.

## Files and independent verification

```bash
python3 research/five-cdc-attempt/cyclic_core_completion.py
python3 research/five-cdc-attempt/verify_cyclic_core_completion.py
```

The constructor requires NetworkX and python-sat, with versions recorded in the repository. The verifier uses only Python's standard library and earlier standard-library graph helpers. It does not import the constructor, PySAT, a SAT solver, or a completion algorithm.

Files: [constructor](cyclic_core_completion.py), [graph, flow, and census metadata](cyclic_core_completion.json), [compressed table of 257,638 covers](cyclic_core_covers.txt.gz), and [independent verifier](verify_cyclic_core_completion.py). The three negative proofs are [normal 1](cyclic_core_proofs/normal-1.drup), [normal 2](cyclic_core_proofs/normal-2.drup), and [normal 3](cyclic_core_proofs/normal-3.drup). Hashes are included in the metadata. The compressed cover table is about 1.6 MB.

Each cover record stores its support code and 51 digits, one per edge, indexing the ten possible pairs of five labels. The verifier decodes these pairs and checks the actual graph conditions. No proof-assistant verification is claimed.

The search used preliminary sampling to locate a failed triple, but the reported positive result rests on the complete support certificate, not on that sampling. Exploratory sample counts are not used as evidence of exhaustive coverage.

## What this changes

The general sum-free shortcut is now ruled out even after eliminating cyclic cuts of size two and three. The weaker seven-choice rule survives a complete check on a graph already known to resist all spanning-2-factor choices.

The useful remaining distinction is between **failed cycles forming a subspace** and **failed cycles forming a subspace that covers every edge**. A structural argument excluding the latter on all cyclically 4-edge-connected cubic graphs would establish the stronger selection rule there; no such argument is proved in this report. The exact small-cut composition results would then transfer independently constructed covers to larger decomposable graphs. That general existence step remains open here.
