# Two local circuits repair every placement of the six-port star

Research date: **5 October 2026**.

The port-order restriction in the [preceding structural theorem](auxiliary-exchange-orbit.md) can be removed. If an eleven-region has a four-vertex cubic star attached through six of its ports, and all its core ports avoid the distinguished layer, **every compatible core cover can be repaired by at most two circuit exchanges confined to that star**, regardless of the six ports' positions or pairing. Each circuit has length two or four. No other selected region's boundary changes.

The stronger move set matters. For two placement classes, holding the central pairs fixed leaves entire cubes of 64 rejected covers. Circuits through the center escape those cubes. The exhaustive calculation covers all **6,930 placements**, represented by **350 symmetry classes** and **21,504,000 normalized boundary states**. An independent implementation verifies every distance. This extends the conditional core reduction; arbitrary eleven-regions and the general 5-CDC conjecture remain unresolved.

## 1. Structure and permitted moves

Let v be the core vertex obtained by contracting a selected eleven-cycle, with cyclic ports 0 through 10. Suppose four distinct unselected cubic vertices a, b, c, d form a component of K−v: d joins a, b, c, and each of a, b, c has two edges to v. The three disjoint port pairs may occur anywhere around the cycle. All eleven target edges must avoid distinguished layer 0. The other five target edges may meet an arbitrary outside core.

Call each leaf with its two target edges a cherry. A circuit contained in the star and v is either:

- A two-edge circuit through one leaf, changing only its two target pairs.
- A four-edge circuit through two leaves and d, also changing their central pairs.

There are 15 possible circuits, one for each pair of the six target edges. A circuit supports an auxiliary swap exactly when every edge on it contains precisely one of the two swapped labels. We permit one circuit per move.

At each leaf, its central edge pair is the XOR of its two target pairs, and hence also avoids label 0. Conservation at d makes the three central pairs an ordered triangle. Relabeling the four auxiliary labels uniquely normalizes them to 12, 13, 23, represented by masks 6, 10, 12. The 24 ordered triangles are all covered by this normalization.

For a fixed incoming pair, a leaf has four assignments, connected by two independent two-edge swaps. Fixing all three incoming pairs therefore gives a six-dimensional cube of 64 covers. Allowing central pairs to change gives **24 × 64 = 1,536** covers of the star. Their circuit exchange graph is connected.

The remaining five pairs must XOR to zero. There are **960** such ordered words. The census includes all of them, whether or not a particular outside core realizes them, so its positive bound applies to every actual outside context.

## 2. Complete placement and distance classification

Choosing six ports and pairing them gives 6,930 placements: binomial(11,6) × 15. Rotation and reflection leave 350 classes: 280 orbits of size 22 and 70 of size 11. Leaf names are immaterial because their permutation can be absorbed into the central triangle's normalization.

For every representative, we enumerate 960 outside words and 64 initial leaf assignments. All eleven cuts are marked. A boundary word r extends precisely when some even auxiliary charge h avoids every forbidden value 30 XOR Rᵢ, where Rᵢ is the prefix XOR before port i. Equivalently, the eleven prefixes must not visit all eight even auxiliary charges.

These counts sum over the **350 representative placements**, not uniformly over all 6,930 numbered placements:

| Minimum exchanges | Cherry circuits only | All star circuits |
|---|---:|---:|
| 0 | 19,167,748 | 19,167,748 |
| 1 | 2,324,263 | 2,336,224 |
| 2 | 10,235 | 28 |
| 3 | 410 | 0 |
| No reachable good state | 1,344 | 0 |
| **Total** | **21,504,000** | **21,504,000** |

Weighting by orbit size gives **425,779,200** normalized cases on numbered placements. For all star circuits, their distance histogram is 379,363,072 at zero, 46,415,512 at one, and 616 at two. The certificate records both counting conventions separately.

For **343** placement classes every boundary needs at most one star circuit. The remaining seven have these numbers of distance-two states among their 61,440 normalized cases:

| Three port pairs, up to rotation and reflection | Distance-two states |
|---|---:|
| (0,1), (2,3), (6,7) | 8 |
| (0,1), (2,4), (3,6) | 2 |
| (0,1), (2,5), (3,6) | 4 |
| (0,1), (2,10), (4,5) | 4 |
| (0,2), (1,3), (4,6) | 2 |
| (0,3), (1,6), (2,7) | 4 |
| (0,3), (1,7), (2,6) | 4 |

The last row is the preceding report's original placement after a symmetry and leaf renaming. Its seventeen states requiring two cherry moves shrink to four when central circuits are allowed.

**Local star repair theorem.** Under the hypotheses of Section 1, at most two auxiliary circuit exchanges confined to the star make the target boundary extend. Outside the seven listed placement classes, one exchange suffices.

**Proof.** Normalize the central triangle and transform the port pairing to its dihedral representative. The other five pairs form one of the 960 closed words. The independently verified finite classification supplies a good star cover within the asserted distance from each of the 64 normalized initial states. Undoing the relabeling and port symmetry gives legal circuits in the actual core.

The all-marked test suffices for any compatible prescribed regional layer. With no distinguished-label target ports, cut-charge parity is constant. If any cut is marked, that parity is even; removing marks only removes forbidden charges. If parity is odd, no cut is marked and extension is automatic. Exchanges stay on the star's nine edges, preserving the distinguished layer and every other selected boundary. ∎

Two is sharp even when exchanges elsewhere are allowed: the [earlier actual-core obstruction](actual-core-exchange-obstruction.md) belongs to this class and excludes every one-step auxiliary exchange, including even-subgraph unions. The current census measures distances for circuits confined to the star; it does not assert that every listed distance-two state resists exchanges elsewhere.

## 3. Why cherry-only repair can fail permanently

Exactly two placement classes have closed bad cherry cubes:

| Port pairs | Closed outside words with all 64 leaf states rejected |
|---|---:|
| (0,1), (2,3), (5,6) | 9 |
| (0,1), (2,3), (6,7) | 12 |

These 21 cubes account for the 1,344 unreachable cases. Of the other 348 classes, 167 have maximum cherry distance one, 167 have maximum two, and 14 have maximum three. The two classes with closed cubes also contain finitely repairable states, including some requiring three moves.

A concrete example uses pairs (0,1), (2,3), (6,7), with the other five pairs, at ports 4,5,8,9,10, equal to `(6,24,6,12,20)`. Its initial boundary is

```
(10,12,18,24,6,24,10,6,6,12,20).
```

Every cherry-only sequence stays inside a rejected 64-state cube. Every single star circuit also fails from this particular initial state. Two four-edge circuits repair it:

1. Swap auxiliary labels 2 and 3 along the circuit through target ports 0 and 3 and leaves a,b.
2. Swap auxiliary labels 1 and 2 along the circuit through target ports 1 and 6 and leaves a,c.

The first move is neutral. After the second, the boundary is

```
(6,10,18,20,6,24,12,6,6,12,20),
```

with surviving all-marked charge 12.

This is realized by a valid five-layer core cover. Attach the other five target edges to a five-cycle whose edges carry the distinguished label. The certificate gives all 19 core edges and their pairs. Expanding the target to its eleven-cycle produces a **simple cubic base on 20 vertices**. The verifier checks that contraction, layer parity, all 64 rejected leaf states, every one-step star circuit, and both repairing circuits.

This particular core also has a one-move repair through the other component: a 13-swap on the triangle through target ports 5 and 9. That shortcut is included and verified. The example establishes cherry-only trapping and the need for two moves **within its star**; the older obstruction supplies sharpness against unrestricted outside exchanges.

## 4. A broader conditional core reduction

Let X be a Blowup or SemiBlowup of a simple cubic base along disjoint selected cycles. Contract its q Petersen four-poles to obtain H, then contract the selected regions to obtain K. Fix a prescribed even layer F on H and its core restriction F_K.

**Theorem.** Suppose each selected cycle has length three through ten, or has length eleven with the attached star of Section 1 in any port placement. Suppose all target edges of these eleven-regions avoid F_K. Then H has a five-layer cover containing F as a whole layer **if and only if** K has a five-layer cover containing F_K as a whole layer.

Given a core cover, let b count the initially rejected short regions, r the star-supported eleven-regions, and h those eleven-regions belonging to the seven exceptional placement classes. At most **b+r+h ≤ b+2r auxiliary cover exchanges** suffice. The first b may be closed trails; each remaining exchange is a circuit of length two or four.

**Proof.** Necessity is restriction under contraction. For sufficiency, apply the [length-ten escape and protection lemmas](ten-cycle-completion.md) to repair short regions, protecting only good short regions and leaving eleven-regions unprotected. This takes at most b exchanges. Then repair each eleven-region inside its own star. These moves affect no other selected boundary, so completed regions stay good. The local star theorem gives the bound. Finally extend all regional boundaries with F fixed. ∎

For a starting nowhere-zero three-bit flow whose chosen coordinate projects to F, the [joint Petersen completion lemma](joint-boundary-completion.md) realizes the cover with at most **2q internal pentagon switches**, preserving every E₀ flow value. Auxiliary cover exchanges themselves change no flow values. A compatible core cover remains a hypothesis.

The theorem removes the former port-order restriction. It retains the attached-star structure and the absence of distinguished-layer target ports.

## 5. Certificates and independent verification

The [constructor](cherry_port_placements.py) writes the [certificate](cherry_port_placements.json). It enumerates central triangles and leaf assignments, tests the prefix obstruction, and uses breadth-first search for shortest exchanges. Each placement record contains distance histograms for both move sets, maxima over fixed outside words, all closed bad cherry cubes, and a digest of its 960 × 128 distance entries. Unreachable cherry distances use −1 in histograms and byte 255 in digests.

The [independent verifier](verify_cherry_port_placements.py) imports no constructor or earlier verifier. It:

- Partitions disjoint triples of chords into dihedral orbits, independently of the constructor's six-port subset and matching enumeration.
- Reconstructs star covers from three binary cycles, forcing the fourth auxiliary layer by XOR, rather than assigning vertex triangles.
- Obtains exchange circuits from the incidence cycle space, checking degree two and connectedness, rather than enumerating paths between port pairs.
- Rebuilds the Blowup and SemiBlowup junction relations separately and uses their allowed-charge masks to test extension.
- Computes cherry distances by minimum Hamming distance and star distances by exhaustive one- and two-step neighborhoods, rather than breadth-first search.
- Verifies every placement digest, both aggregate counting conventions, move witnesses, and the realized 20-vertex cubic base.

Reproduce from the repository root with Python 3 and its standard library:

```bash
python3 -B research/five-cdc-attempt/cherry_port_placements.py
python3 -B research/five-cdc-attempt/verify_cherry_port_placements.py
```

The new explicit graph certificate concerns the contracted core and its cubic base. The exhaustive junction relations certify regional extension; the mixed-region conclusion follows from the phase-ordering proof. The preceding report retains the full Blowup/SemiBlowup graph and flow certificates for the original placement.

The remaining questions include other outside tree shapes, distinguished-layer target ports, and eventual auxiliary escape in arbitrary cores. This result does not settle those general cases or prove the 5-CDC conjecture.

Strategic continuation: [Flow components through affine coordinate fibers](flow-space-components.md) returns to flow repair on the cores themselves. It proves an exact component reduction and checks a Petersen-piece-free, cyclically 5-edge-connected core without assuming a starting cover.
