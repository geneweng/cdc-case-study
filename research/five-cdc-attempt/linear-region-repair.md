# Linear regional repair using circuits of length at most ten

**30 September 2026.** The exponential repair bound in the [regional repair report](region-joint-repair.md) can be replaced by a **linear bound**, using only short circuits. The construction also preserves more of the input flow: every core-edge value and the flow charge of every Petersen piece remain fixed throughout.

Let the selected cycle lengths be k₁,…,k_s and q=∑k_j. Given a core cover containing the selected coordinate, either Blowup or SemiBlowup can realize that same core cover after at most

\[
\boxed{\quad 2q+3\sum_j\left\lfloor\frac{k_j}{4}\right\rfloor
\ \le\ \frac{11q}{4}\quad}
\tag{1}
\]

valid circuit switches. Each switch has length at most **10 for Blowup** and **9 for SemiBlowup**. A sharper bound is 2q+3δ, where δ is computed in linear time from eight candidate cover charges per region.

The number δ is the **exact minimum** when working on the contracted-piece quotient and allowing switches confined to individual junctions. A repeated family has δ=k/4 for every k divisible by eight, making this junction bound sharp. Neither the full-graph bound (1) nor the lengths of the displayed full repairs are claimed optimal.

The proof uses a complete finite classification of **70,176 local repair cases**, followed by an averaging argument and the previously verified Petersen lifting and completion lemmas. Certificates include ten full cubic repairs through **768 vertices**. The general 5-cycle double cover conjecture remains unproved here; the core cover is a supplied input. No literature-wide novelty claim is made.

## 1. Setup and the additional invariant

Use the construction from the preceding reports. A simple cubic graph S has disjoint selected cycles D. Replace them by Blowup or SemiBlowup to obtain X; contract the Petersen four-poles B to obtain H; contract the full selected regions to obtain the core K=S/D. All edges of S outside D are retained as core edges, including loops created by contraction, counted twice in vertex incidences.

Start from a nowhere-zero flow f:E(X)→F₂³ and fix a nonzero functional ℓ. A supplied five-layer core cover has layer 0 exactly ℓ(f|E(K)). A five-layer cover means at most five even subgraphs, possibly empty or disconnected, covering every edge exactly twice. A circuit switch adds one nonzero vector along one connected circuit on which that vector is absent.

At a B piece, its four port flow values obey

\[
h=f(a_1)\oplus f(a_2)=f(b_1)\oplus f(b_2).
\tag{2}
\]

Call h its flow charge. The preceding general repair algorithm could change these charges. The new algorithm preserves **all of them**, as well as every core-edge value.

Normalize ℓ to the least-significant bit by an invertible linear change of coordinates. This changes neither valid circuit switches nor their lengths. Convert back at the end. The certificates use the normalized coordinate ℓ=1.

## 2. Every incompatible junction is one switch from a joint extension

At junction i use the representatives a,b,c,d from the [boundary report](short-cycle-boundary.md). The left and right flow charges are h=a⊕b and h⊕p=c⊕d, where p is the exterior flow value. For cover pairs, the analogous charges are c₀ and c₀⊕r, with exterior pair r.

The internal graph of a Blowup junction is K₂,₃, with auxiliaries u,w joined to the two adjacent contracted B vertices and the original cycle vertex v. Its three internal circuits are four-cycles. With representatives a,b,c,d,x=a⊕c,y=b⊕d,p=x⊕y, their position sets are

\[
\{a,b,x,y\},\quad\{c,d,x,y\},\quad\{a,b,c,d\}.
\tag{3}
\]

The first two meet one contracted B vertex; the last meets two. Every circuit preserves the two flow charges and the exterior value p. In SemiBlowup, b=d is one physical edge. Its junction is a triangle on the two B vertices and v, and switching its three edges also preserves both charges and p.

Let Q be the ten two-element subsets of the five cover labels. Recall the exact local relation M(r,z), where z records membership of a,b,c,d in the distinguished layer: M lists the possible left cover charges. For each compatible key it contains six, seven, or eight of the eight charges with the required distinguished bit.

**One-junction repair lemma (finite verified).** Fix any valid junction flow, an exterior cover pair r with the same distinguished membership as p, and any even cover charge c₀ whose distinguished bit matches h. Without changing p or h, at most **one** valid internal junction circuit switch produces a flow whose selected coordinate is compatible with a local cover having exterior pair r and left charge c₀.

Zero switches suffice precisely when c₀∈M(r,z) for the initial flow. Otherwise one switch is necessary and sufficient.

The exhaustive classification is:

| Construction | Local flows | Charge fibers | Compatible starting-flow/cover-data cases | Distance 0 | Distance 1 |
|---|---:|---:|---:|---:|---:|
| Blowup | 1,512 | 56 | 58,752 | 54,000 | 4,752 |
| SemiBlowup | 294 | 56 | 11,424 | 10,464 | 960 |
| **Total** | **1,806** | **112** | **70,176** | **64,464** | **5,712** |

The fibers fix the exterior flow value p and left charge h. For Blowup, 14 fibers have 30 flows and 42 have 26; for SemiBlowup, 14 have six flows and 42 have five.

The constructor tests the permitted circuit switches directly. The independent verifier builds the flow and cover assignments from XOR-zero triangles at the cubic vertices, recognizes adjacency by pairwise flow differences, and runs breadth-first search from every compatible target set. It checks all named flow values and cover labels; there is no unverified symmetry reduction. The saved distance digests cover every case, and explicit local examples attain distance one.

This lemma chooses a compatible target flow rather than an arbitrary preselected target flow. That freedom is important: it supplies a one-switch repair even though exact flow-to-flow alignment can take more moves.

## 3. Eight charge choices give the exact junction distance

Fix the supplied core cover. On one length-k region, let r_i be its exterior pairs, z_i the initial distinguished membership pattern at junction i, and

\[
R_0=0,\qquad R_i=r_0\oplus\cdots\oplus r_{i-1}.
\]

The compatible initial cover charges form an eight-element set A. Its distinguished bit is the bit of the initial left flow charge at the chosen starting cut. For c∈A, define

\[
b(c)=\#\{i:c\oplus R_i\notin M(r_i,z_i)\},
\qquad \delta_P=\min_{c\in A}b(c).
\tag{4}
\]

For multiple regions put δ=∑δ_P. Both the eight counts and a minimizing charge can be found in O(k) time for a region.

**Exact junction-distance theorem.** On H, the minimum number of switches confined to individual junctions that permits a completion with the supplied core cover is δ. Every such switch can be a triangle in SemiBlowup or a four-cycle in Blowup. All flow charges stay fixed.

**Upper bound.** Choose a minimizing c for each region. Leave every compatible junction flow unchanged. At each incompatible junction, use the one-junction repair lemma to realize exterior pair r_i and left cover charge c⊕R_i in one switch. Its right charge is c⊕R_{i+1}, so adjacent junction covers agree in parity at their shared B vertex. Since the core cover is even, R_k=0 and the cycle closes. Junction interiors have disjoint edge sets, so their switches do not interfere.

**Lower bound.** Any successful final cover has some initial charge c∈A. Every junction counted in b(c) was incompatible with that final charge and supplied boundary before repair. At least one switch must have changed the flow in each of those junctions. A permitted move changes only one junction's internal edges, so at least b(c)≥δ_P moves are necessary in that region. Summing gives δ. □

The lower bound is for the stated move rule. A longer circuit passing through several junctions might do better, as might a different supplied core cover; neither is included in this exact-distance claim.

### The averaging bound

For a fixed junction i, translating by R_i bijects A with the eight compatible charges at i. It excludes exactly 8−|M(r_i,z_i)| candidates, at most two. Therefore

\[
\sum_{c\in A}b(c)
=\sum_i\bigl(8-|M(r_i,z_i)|\bigr)\le2k.
\]

The smallest of eight integer counts consequently satisfies

\[
\boxed{\delta_P\le\left\lfloor
\frac{1}{8}\sum_i\bigl(8-|M(r_i,z_i)|\bigr)
\right\rfloor\le\left\lfloor\frac{k}{4}\right\rfloor.}
\tag{5}
\]

For lengths three through seven, the stronger prior boundary theorem gives δ_P=0. Equation (5) handles arbitrary lengths without a search over global covers: the core cover is already supplied.

## 4. Lifting to the full cubic graph gives short, linear repairs

Each quotient junction circuit meets at most two contracted B vertices. The [Petersen preparation lemma](petersen-flow-repair.md) makes the selected pair of ports ready for its increment after at most one internal pentagon switch, with a connecting path of length at most three. Apply it independently to the visited pieces, then perform the lifted junction circuit switch.

Thus each of the δ quotient switches costs at most **three** full-graph switches: two preparations and the lifted circuit. Its length is at most

- 4+2·3=10 in Blowup; a four-cycle meeting only one B needs at most seven edges;
- 3+2·3=9 in SemiBlowup.

The preparations have length five. After all junction switches, the quotient flow has a cover with its selected coordinate as layer 0 and exactly the supplied core edge pairs. The [joint Petersen completion theorem](joint-boundary-completion.md) finishes each B in at most two internal pentagon switches, preserving all quotient-edge values and cover pairs. This adds at most 2q switches.

These steps prove (1), with the sharper bound **2q+3δ**. The algorithm maintains both invariants claimed at the start: all core-edge flow values are fixed; each lifted junction move changes either both a-port values or both b-port values of a visited B by the same increment, preserving (2). Internal preparations and final pentagons do not change any port value.

After precomputing the fixed local tables, the repair construction takes linear time in the input/output graph size. There are eight constant-size charge tests per junction, at most one selected junction move per incompatible junction, at most two adjacent B pieces to inspect for its lift, and one constant-size completion problem per B. The saved implementation visits only the adjacent pieces when lifting each junction move.

This proves a linear bound for reaching **some compatible completion of a supplied core cover**. It does not prove a linear diameter for arbitrary specified pairs of full flows.

## 5. The one-quarter junction bound is sharp

Take k=8m and repeat the eight exterior pair masks

\[
(6,10,6,18,6,10,6,18)
\tag{6}
\]

m times. They exclude the distinguished label 0. Prescribe z_i=15 at every junction, so all four port representatives a,b,c,d belong to the selected coordinate. In Blowup the x,y edges do not; in SemiBlowup all three physical junction edges do. These memberships are even on the region.

For both constructions and every exterior pair r excluding label 0, the independently rebuilt local table gives the exact identity

\[
M(r,15)=A\setminus\{30,30\oplus r\},
\tag{7}
\]

where A is the eight even subsets of the four auxiliary labels and 30 denotes all four of them.

The eight prefix values of one block of (6) are

\[
0,6,12,10,24,30,20,18,
\]

each member of A exactly once, and the final XOR is zero. By (7), junction i rejects initial charge c exactly when c⊕30 is R_i or R_{i+1}. In the repeated closed walk each member of A occurs m times, with two incident junctions per occurrence. Therefore

\[
b(c)=2m\quad\text{for every }c\in A,
\qquad\boxed{\delta_P=2m=k/4.}
\tag{8}
\]

The one-junction lemma attains this lower bound, so it holds for every m, not only the saved examples.

### Cubic realizations

Use two disjoint cycles of length k=8m, joined by a perfect matching. Around the bottom cycle, the matched top vertices appear in successive blocks

```text
8j + (0,1,5,2,3,7,4,6),   j=0,...,m-1.
```

Replace the top cycle. This gives simple cubic graphs on **96m vertices** for Blowup and **80m** for SemiBlowup. Their core is the bottom cycle with all its vertices joined to a hub. Assign the spoke pairs (6) in top order and repeat bottom rim pairs (12,6,12,10,24,10,12,10). These form the supplied core cover with empty distinguished layer.

A four-flow h on the quotient exists: use alternating values 1,2 on the bottom rim and value 3 on each spoke, then the earlier quotient extension. If F is the regional membership specified above, set the quotient three-bit flow to 2h+1_F, meaning shift h left by one bit and append the F-bit. It is nowhere-zero and conserved, with coordinate F. Every B boundary extends, giving a full initial flow on X for every m.

The certificates construct and repair the cases below. The quotient distance is exact; the full switch totals are the algorithm's output.

| m | Exact junction distance | Blowup vertices | Full switches | SemiBlowup vertices | Full switches |
|---|---:|---:|---:|---:|---:|
| 1 | 2 | 96 | 8 | 80 | 6 |
| 2 | 4 | 192 | 16 | 160 | 12 |
| 4 | 8 | 384 | 32 | 320 | 24 |
| 8 | 16 | 768 | 64 | 640 | 48 |

The largest circuit actually used in these Blowup examples has length seven; in SemiBlowup it has length nine. The bound ten is a general upper bound, not claimed attained by this family.

## 6. Revisiting the earlier rejected eight-cycle covers

The earlier two examples used different initial membership patterns: z=3 throughout in Blowup and alternating z=0,15 in SemiBlowup. For those exact graphs, initial flows, and originally rejected supplied covers, the eight-count test gives δ=1 in both constructions.

One quotient junction switch therefore suffices in each. After bounded-length lifting and B completion, the new saved sequences use **four full switches on the 96-vertex Blowup** and **five on the 80-vertex SemiBlowup**, improving the previous constructed sequences of 13 and 11. All core values and B charges remain fixed, and the final core pairs equal the originally rejected pairs. This comparison concerns the same prescribed final core covers; no unrestricted minimum full-graph distance is asserted.

There are also 18 independently checked quotient examples, using lengths 3,4,5,7,8,9,16,31,64 in both constructions with separately chosen initial local flows. The two length-64 cases need respectively three and four junction switches for their supplied boundaries.

## 7. Reproduction and remaining limits

From this directory:

```bash
python3 -B linear_region_repair.py
python3 -B verify_linear_region_repair.py
python3 -B verify_petersen_flow_repair.py
python3 -B verify_joint_boundary_completion.py
python3 -B verify_short_cycle_boundary.py
```

- [Constructor](linear_region_repair.py) and [certificates](linear_region_repair.json): complete local distance digests, sharp local witnesses, eight-charge distance certificates, 18 quotient repairs, and ten full cubic repairs.
- [Independent verifier](verify_linear_region_repair.py): reconstructs all 70,176 local cases, computes their shortest distances independently, verifies the sharp-family topology and charge counts, and checks every full circuit, intermediate flow, preserved core value, preserved B charge, and final cover.

The preceding verifiers establish the general one-preparation/three-edge-path lemma and two-pentagon completion bound used in the lifting proof, as well as the earlier octagon graph structures and obstruction. All scripts use the standard library.

This resolves the previous exponential-bound limitation for the stated completion task. It does not solve how to find a compatible core cover in every case, fixed-layer completion equivalence for long regions, exact unrestricted repair distances, or the general 5-CDC existence conjecture.
