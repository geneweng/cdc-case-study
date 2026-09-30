# A finite algebra for prescribed layers in Petersen chains

**30 September 2026. The general 5-cycle double cover conjecture remains unproved here. The results below concern serial chains of one specified four-pole and their closure into rings. The finite classification is proved by exhaustive, independently checked local enumeration; no claim of novelty over the complete literature is made.**

**Subsequent result:** [All seven coordinates can fail at cyclic edge connectivity four](junction-selection-obstruction.md) supplies exact junction constraints and uses a charge contradiction to block all seven coordinates on a 72-vertex graph and an infinite family. These graphs have five-layer covers. The serial-chain results here remain valid; branching attachments introduce the additional obstruction.

The [previous report](petersen-boundary.md) showed that a Petersen four-pole accepts every parity-compatible boundary for an unrestricted five-layer cover. Prescribing the internal edges of one layer leaves 900 impossible boundary states. This report controls how those conditional constraints compose:

> The 64 possible prescribed layers in one Petersen four-pole give 27 distinct boundary relations. All nonempty compatible serial chains give exactly 36 distinct relations. Each is already realized by a chain of at most three pieces, and some require three.

Adjoining the empty relation gives a **37-element semigroup** under Boolean composition. Swapping the two edges at any join introduces no additional relation types. Consequently the exact boundary behavior of an arbitrarily long chain, with a prescribed layer, has a constant-size description.

The classification has two complementary consequences. A particular boundary obstruction remembers the parity of chain length indefinitely. Nevertheless, in a **closed ring consisting only of these pieces, every even subgraph can be one whole layer of a five-layer cover**, including disconnected and empty subgraphs. A direct construction proves the latter for rings of arbitrary length, with arbitrary twists at the joins.

The piece is Hägglund's four-pole obtained by deleting two adjacent Petersen vertices. His blowup constructions also contain attachment vertices; the ring theorem here does not apply to those constructions with their attachment vertices retained. Related cover results for superpositions have an established literature. [Hägglund, Section 2](https://arxiv.org/html/1203.2015v1#S2); [Liu–Hao–Luo–Zhang, 2023, abstract](https://doi.org/10.1137/22M1472425)

## 1. The conditional relation

Use the same piece B, vertex labels, edge order, and pair dictionary as before:

```text
Internal edges, positions 0,...,9:
(2,3), (3,4), (2,7), (3,8), (4,9),
(5,7), (6,8), (7,9), (8,5), (9,6).

Ports, positions 10,...,13:
a1 at 4, a2 at 5, b1 at 2, b2 at 6.

Pair indices:
0=01, 1=02, 2=03, 3=04, 4=12,
5=13, 6=14, 7=23, 8=24, 9=34.
```

Here `13`, for example, denotes the two layer names {1,3}, not the integer thirteen. A pair is also its five-bit incidence vector. Let Q be the ten pairs. A five-layer cover assigns a member of Q to every edge, with XOR zero at every cubic vertex. Each edge then has exact multiplicity two, and every named layer is even.

Let F be a binary even subgraph of B, counting the semiedges in the parity conditions at internal vertices. Its mask has bit e set precisely when edge e belongs to F. There are 64 such masks: the 14-edge incidence system has eight independent vertex equations.

Require layer 0 to be **exactly** F, including on the internal edges. Define a 100-by-100 Boolean matrix

\[
T_F[(p,q),(r,s)] =
[\text{there is a five-layer assignment with boundary }(p,q,r,s)
\text{ and layer 0 equal to }F].
\tag{1}
\]

Rows correspond to the ordered a-port pair, columns to the ordered b-port pair. States are indexed by 10p+q using the displayed dictionary. These matrices retain named layer labels; the classification does not quotient by layer permutations or port permutations.

Each true entry conserves the **charge** p⊕q=r⊕s. It also fixes which of the two ports on each side belong to layer 0. The sum of the 64 matrix sizes is 4,220, recovering the preceding conditional relation exactly.

Join b1,b2 of one piece to a1,a2 of the next. For local masks F and H, a valid global prescribed layer requires their memberships on the joined ports to agree. The joined boundary relation is

\[
T_F\odot T_H,
\tag{2}
\]

where multiplication is Boolean: an entry is true if some intermediate pair of edge labels works. Witnesses on the two pieces glue because they assign the same pair to each joined edge. Conversely every global cover restricts to such matching witnesses. Thus (2) is an exact equivalence, not a sufficient relaxation.

## 2. Closure after three pieces

Of the 64 matrices T_F, exactly 27 are distinct. Starting with them, repeatedly multiply on the right by every one-piece matrix and retain each newly encountered nonzero matrix. The layers of this exhaustive search are:

| Shortest realizing chain | New nonzero relations | Total |
|---|---:|---:|
| One piece | 27 | 27 |
| Two pieces | 7 | 34 |
| Three pieces | 2 | 36 |
| Four pieces | 0 | 36 |

The nine additional matrices have the following shortest representative words. Each number is a local mask in the 14-edge order above.

| Representative masks, in chain order | Accepted ordered boundaries |
|---|---:|
| (0, 12361) | 24 |
| (151, 151) | 168 |
| (887, 887) | 120 |
| (3111, 0) | 24 |
| (12361, 3111) | 132 |
| (12787, 3709) | 84 |
| (12787, 4039) | 84 |
| (0, 12361, 3111) | 36 |
| (887, 887, 887) | 120 |

Equal numbers of accepted boundaries need not mean equal relations. In particular the last matrix and the square of T₈₈₇ differ, as Section 4 explains.

**Finite-classification proof.** The constructor reads the exact local relation from the preceding checkpoint and multiplies bitset matrices. An independent verifier rebuilds every local matrix from scratch: it enumerates all 64 binary even supports and selects five named supports with ordinary edge multiplicity exactly two. This gives 14,700 partial covers and precisely the same 4,220 projected states. It then composes relations as sets of ordered pairs, independently exhausts the breadth-first closure, and checks the saved matrices and all 37²=1,369 products, including zero. Distinctness and breadth-first discovery certify the minimum lengths. Since every state in the finite list is closed under appending a generator, induction covers chains of every length. Associativity follows from relational composition. □

The [certificate](petersen_chain_algebra.json) contains all 36 matrices, their shortest representatives, the map from each of the 64 local masks to its type, and the full multiplication table. This is a finite computational proof with a reproducible verifier; it is not a proof-assistant formalization.

An incompatible joined membership pattern gives the zero relation. Every compatible chain gives a nonzero relation, as the safe-charge argument below also proves. Swapping the two input ports or the two output ports permutes the set of 27 generators, and also permutes the 36 nonzero chain types. A crossed join can therefore be absorbed into an adjacent matrix. The same classification applies with any sequence of straight and crossed joins.

**Boundary replacement consequence.** Any valid chain with its prescribed local masks can be replaced by the saved representative of its matrix type, using at most three pieces and the representative's prescribed layer. In any fixed outside graph, a five-layer completion exists before replacement exactly when it exists afterward; all outside pairs can be retained. This replaces the prescribed subgraph *inside* the chain and preserves its external completion relation. It does not claim to preserve the original internal circuits or individual internal edges. Local witness backtracking lifts any accepted boundary to the original chain in linear time in its length.

## 3. Charges that always allow extension

Write the membership pattern on one pair of ports as 00, 10, 01, or 11, in port order. Evenness of F says that the parity of this two-bit pattern is the same on both sides. It stays constant along a compatible chain, including crossed joins.

The exact local relation gives the following facts, checked for all 64 masks:

* **Even parity.** Charge zero is always available. Its state set has six possibilities for pattern 00, namely (p,p) with p avoiding label 0, and four for pattern 11, with p containing label 0. The relation between these state sets is complete unless both sides have pattern 00. In that case every row and column contains at least five of the six possible states.
* **Odd parity.** Every weight-four charge containing label 0 is available. For each such charge and each of patterns 10 or 01 there are three ordered states. Every local relation contains the complete 3-by-3 block between its appropriate state sets.

These facts prove a useful extension lemma:

> In a compatible chain of at least two pieces, every pair of endpoint states of charge zero extends when the pair-membership parity is even. When that parity is odd, every pair of endpoint states with the same weight-four charge containing label 0 extends, already through one piece.

For the even case, choose the intermediate state between two pieces. If its membership is 11, both relevant blocks are complete on four states. If it is 00, the two sets of usable intermediate states each have at least five members of a six-element set, so they intersect. The two-piece product is therefore complete at charge zero. Appending another piece preserves completeness since the relevant local block has no empty column. The odd case is immediate from the complete local blocks. Swapping port order preserves these statements. □

The verifier also directly checks all 1,024 compatible ordered pairs of local masks, covering 2,560 safe charge blocks when all four odd charges are included. Other charges can still impose restrictions; the next example does so at every length.

## 4. A persistent parity obstruction

Take F with mask 887. It is the internal eight-cycle

\[
2,3,4,9,6,8,5,7,2,
\]

with no port in layer 0. Fix charge {1,2}, whose five-bit mask is 6. The four possible ordered states, all avoiding layer 0, split into

\[
A=\{(13,23),(23,13)\},\qquad
D=\{(14,24),(24,14)\}.
\]

The restriction of T₈₈₇ to these states is exactly

\[
\begin{pmatrix}0&J_2\\J_2&0\end{pmatrix},
\tag{3}
\]

where J₂ is the two-by-two all-ones Boolean matrix. Thus one piece changes which of A and D contains the boundary state, while allowing either order within the destination class. Squaring (3) gives the two diagonal J₂ blocks; multiplying again returns (3).

Consequently, prescribe this eight-cycle in every piece of a straight chain of length k. Then the boundary

\[
(a_1,a_2,b_1,b_2)=(13,23,13,23)
\tag{4}
\]

extends **if and only if k is even**. Replacing the last two pairs by (14,24) gives extension exactly when k is odd. This is an unrestricted five-layer nonexistence statement for the specified F and boundary, not merely failure of a particular repair procedure. Necessity and sufficiency follow from the complete local relation and exact composition.

Adding more pieces therefore does not eventually erase every boundary obstruction. The state space stays finite while a parity distinction persists. This explains why a bound of three on *shortest representatives* is different from stabilization of every matrix power.

## 5. Every even subgraph extends on a Petersen necklace

Define a **Petersen necklace** by taking k≥1 disjoint copies of B and, cyclically, joining each b-port pair to the next a-port pair. At each join either matching is allowed. There are no other vertices or edges. The resulting cubic graph has 8k vertices and 12k edges.

**Necklace theorem.** Every binary even subgraph F of such a graph is exactly one layer of a five-layer cycle double cover.

Here is a direct construction. Restrict F to each piece, including its ports. The parity of the number of F-edges in each joined pair is constant around the necklace.

* If this parity is even, assign pair 01 to every joining edge in F, and pair 12 to every joining edge outside F.
* If it is odd, assign pair 01 to every joining edge in F, and pair 23 to every joining edge outside F.

These rules give consistent labels on joined edges even when the join is crossed. They use charge zero in the even case and charge {0,1,2,3} in the odd case. The following table gives the resulting boundary on any one piece:

| F-membership on (a1,a2,b1,b2) | Assigned boundary pairs |
|---|---|
| 0000 | (12,12,12,12) |
| 1100 | (01,01,12,12) |
| 1010 | (01,23,01,23) |
| 0110 | (23,01,01,23) |
| 1001 | (01,23,23,01) |
| 0101 | (23,01,23,01) |
| 0011 | (12,12,01,01) |
| 1111 | (01,01,01,01) |

For **every** local mask with the listed port membership, the assigned boundary has an extension with layer 0 exactly that mask. The certificate supplies a directly checkable 14-digit cover word for each of the 64 masks. The extra assertion in the 0000 case is that its specified diagonal state is always allowed; a minimum-degree bound alone would not establish this.

Fill each piece with its corresponding local witness. Joined edges agree, all internal vertex equations hold, every edge has exactly two labels, and layer 0 is F on both internal and joining edges. This proves the theorem for arbitrary k. The lookup and assembly take linear time in graph size. □

This family is three-edge-colorable. In the displayed pair dictionary the verified local word `57745554774444` uses only pairs 12,13,23, with all four ports equal to 12. Repeating it around the necklace gives a proper three-edge coloring by these three pairs. The necklace result concerns preserving **any specified even subgraph**, rather than the existence of some cover on an uncolorable graph. It does not resolve the remaining snark case or the seven-coordinate selection question for general cyclically four-edge-connected graphs.

## 6. Certificates, reproduction, and the remaining step

```bash
python3 research/five-cdc-attempt/petersen_chain_algebra.py
python3 research/five-cdc-attempt/verify_petersen_chain_algebra.py
```

Both scripts use only Python's standard library. The [constructor](petersen_chain_algebra.py) saves the [finite algebra and witnesses](petersen_chain_algebra.json). The [independent verifier](verify_petersen_chain_algebra.py) imports no constructor or earlier verifier and uses a different local enumeration and representation of relational composition. It checks:

* All 64 even supports, 14,700 partial covers, 4,220 conditional states, and 27 distinct local relations.
* All 36 nonzero chain relations, shortest representative lengths, 1,369 multiplication entries, and both port-swap operations.
* The local safe-charge bounds, 2,560 two-piece charge blocks, and 64 universal local cover words.
* The exact parity obstruction, six reconstructed open-chain covers up to 64 pieces, and 74 closed-necklace covers from 8 to 248 vertices. These examples include twists and every local mask.

The infinite statements follow from closure, Boolean multiplication, and the local construction, not from merely testing these finite graph examples. The general 5-CDC conjecture remains unproved by this work.

The next structural obstacle is branching attachment. In the blowup constructions, pairs of ports meet additional cubic vertices rather than simply the next pair of ports. Those vertices couple several charges, so the serial-chain semigroup alone does not decide their prescribed-layer problem. The [next report](junction-selection-obstruction.md) supplies their exact local relations and uses them to disprove universal coordinate selection even after eliminating small cyclic cuts. A general existence proof would still need a way to choose or change the flow while controlling these coupled constraints.
