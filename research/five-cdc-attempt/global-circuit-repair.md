# One global circuit repairs every repetition

**30 September 2026. The general 5-cycle double cover conjecture remains unproved here.** The obstructed flow on the preceding 72m-vertex family has **unrestricted repair distance exactly one**, for every m≥1. A single circuit of length 13m changes it to a flow with an explicit five-layer-completable coordinate.

This sharpens the [previous repair result](petersen-flow-repair.md), which established distance m when every switch stays inside one Petersen piece. The distinction persists even after allowing other short circuits: **if every switch has length at most 5, 6, or 7, the distance is still exactly m**. A general counting bound quantifies this dependence on allowed circuit length.

The report also extends the local lifting lemma to an arbitrary collection of disjoint Petersen pieces, with a bound in terms of how many pieces each quotient circuit visits. All new certificates use only the Python standard library. No literature-wide novelty or minimum-length claim is made.

A switch adds a nonzero vector a∈F₂³ on a single connected circuit C, requiring a to be absent from C. A successful flow has at least one nonzero linear coordinate support that is a whole layer of a CDC. For the positive witnesses here, five layers suffice; the negative witnesses exclude any number of layers. Layers may be disconnected even subgraphs.

## 1. The explicit switch

Let Gₘ be the earlier Blowup(C₆ₘ□K₂, top ring), with k=6m. Keep the notation vᵢ,tᵢ for the prism vertices, Bᵢ for the Petersen pieces, and uᵢ,wᵢ for the junction vertices. The original flow fₘ repeats the six local words and junction values from the [obstruction report](junction-selection-obstruction.md#3-a-flow-that-blocks-all-seven-coordinates).

Start with the bottom circuit t₀,t₁,…,tₖ₋₁,t₀. For each r=0,…,m−1, replace its edge t₆ᵣt₆ᵣ₊₁ by the path

\[
t_{6r},v_{6r},u_{6r},
(2\text{ in }B_{6r}),
(7\text{ in }B_{6r}),
(5\text{ in }B_{6r}),
w_{6r+1},v_{6r+1},t_{6r+1}.
\]

These replacement paths have disjoint interiors. The result Cₘ is therefore **one simple circuit**, not a disjoint union. Each replacement adds seven edges, giving

\[
|C_m|=6m+7m=13m.
\]

In each period its flow values, starting with the replacement path and then taking the next five bottom edges, are

```text
5, 7, 4, 5, 2, 5, 2, 6, 5, 3, 7, 5, 6.
```

Value 1 is absent. Thus

\[
g_m=f_m+1_{C_m}
\]

is a valid nowhere-zero three-bit flow after **one** switch. Exactly eight of those thirteen initial values are odd. Consequently the normal-1 support changes from 57m edges to

\[
57m+13m-2(8m)=54m.
\]

On G₁, in the earlier edge order, C₁ has ordered edge list

```text
6, 72, 74, 14, 17, 77, 79, 7, 1, 2, 3, 4, 5.
```

An explicit five-layer cover of g₁'s normal-1 support is encoded by the following 108 pair indices. Concatenate the two lines; the pair dictionary is 01,02,03,04,12,13,14,23,24,34, indexed 0,…,9.

```text
068471434652235910223718036114885022419735891763889441108267391873111287
680186604343100618843652200539932233
```

The verifier checks that each edge has exactly two labels, every label has degree zero or two at every vertex, and label 0 agrees exactly with the switched normal-1 support. This positive word was discovered using the existing SAT cover solver during exploration; reproduction and verification of the saved result require no solver.

The natural covering map Gₘ→G₁ reduces all ring and piece indices modulo six. Pull back the displayed cover. Vertex stars map bijectively, so the layer degrees and edge multiplicity remain valid. Cₘ is the full preimage of C₁, hence gₘ is the pullback of g₁ and its normal-1 support is the pulled-back cover layer.

Every coordinate of fₘ is initially impossible by the previous Z–W charge witnesses, so zero moves cannot suffice. The explicit successful switch therefore proves that the unrestricted distance is **exactly one**. In fact, all other six coordinates of gₘ still have surviving charge obstructions: normal 1 is its only completable nonzero coordinate, even if more than five cover layers are allowed.

This proves an exact number of moves. It does not assert that 13m is the shortest possible length of a single successful circuit.

## 2. Why a winding circuit lifts differently from a local pentagon

There is a general mechanism behind the two repair constructions.

Consider an m-sheeted cyclic graph cover specified by integer edge voltages. After choosing an orientation for every base edge e=uv, its lift joins (s,u) to (s+zₑ mod m,v). For an oriented base circuit C, let w be the sum of its signed voltages around the circuit.

**Cyclic-cover lifting lemma.** The full preimage of C consists of

\[
d=\gcd(m,w)
\]

circuits, each of length |C|m/d, taking gcd(m,0)=m. If adding a on C is a valid flow switch and the resulting flow has a specified CDC layer, then adding a on each of those d lifted circuits produces a flow with the lifted CDC layer in at most d switches.

**Proof.** One traversal of C advances the sheet index by w. Addition by w on ℤ/mℤ has d orbits, each of size m/d. Each orbit gives one lifted circuit. Simplicity of C ensures no vertex repeats before that orbit closes. The lifted circuits are disjoint, and a is absent from all their edges. Switch them in any order. The result and the cover are the pullbacks of their base counterparts; exact multiplicity and even layer degrees follow from the bijection on vertex stars. □

In the edge orientation used here, the only nonzero voltages are +1 on edges 5,106,107: the bottom seam and the two a-port seams from B₅. The earlier repairing pentagon lies inside B₀ and has winding zero, so its preimage has m components and gives m switches. C₁ has winding one, so its entire preimage is one circuit for every m.

The new certificate numbers vertices and edges by sheet: vertex 72s+v and edge 108s+e. This differs from the earlier block-by-block family numbering. The independent verifier checks an explicit graph isomorphism between the two conventions; the graphs and starting flows are the same up to that numbering change.

## 3. A lower bound for bounded circuit length

Let d_L(fₘ) be the minimum number of valid switches needed to reach any completable coordinate, restricting every switched circuit to length at most L. For integer L≥5,

\[
\boxed{\left\lceil\frac{m}{\lfloor L/4\rfloor}\right\rceil
\ \le\ d_L(f_m)\ \le\ m.}
\]

In particular,

\[
d_5(f_m)=d_6(f_m)=d_7(f_m)=m,
\qquad d_L(f_m)=1\quad\text{when }L\ge13m.
\]

**Proof of the lower bound.** For each normal ℓ, the earlier certificate contains m obstructing adjacent pairs of pieces, pairwise disjoint as sets of pieces. At least one piece in every such pair must have its local support changed before that normal can become completable. Thus a repair must touch at least m distinct pieces, for whichever normal succeeds at the endpoint.

A circuit meeting Bᵢ either lies entirely inside it or enters and leaves it. An internal circuit has at least five edges. Otherwise its intersection contains a path between two distinct port vertices, together with their two port edges. The port vertices have pairwise internal distance at least two, so at least four of Bᵢ's fourteen local edges lie on the circuit.

In this Blowup family, those fourteen-edge sets are disjoint for distinct pieces: every port edge joins a piece to a junction vertex. Hence a circuit of length at most L can touch at most ⌊L/4⌋ pieces. After fewer than the displayed lower-bound number of switches, some original obstructing pair remains untouched for every candidate normal. This argument allows the successful normal to be selected at the end and allows all intermediate flows permitted by the switch rule. □

The upper bound m is the earlier repair using m internal pentagons. For L=5,6,7 the bounds coincide. The global construction supplies the final assertion for L≥13m. For L<5 no move exists, since Gₘ has girth five.

The same counting argument gives a bound on total changed-edge work for any successful sequence C₁,…,Cₜ:

\[
\sum_{j=1}^{t}|C_j|\ge4m.
\]

The local construction uses 5m changed-edge occurrences across m moves; the global construction uses 13m in one move. Thus the number of moves and the amount of edge modification measure different costs. The lower bound is specific to this family and its disjoint obstruction witnesses; it is not a bound for arbitrary graph covers or arbitrary collections of four-poles.

## 4. Simultaneous lifting through several Petersen pieces

Now let G be any loopless graph containing q vertex-disjoint induced copies B₁,…,B_q of the Petersen four-pole interior, each with exactly its four port edges leaving it. Direct edges between different pieces are allowed. Contract all the pieces to obtain H. No edge joins two vertices of the same piece except its ten specified internal edges.

The preceding finite theorem supplies two facts: fixed-boundary local flows have switch diameter three; and a switch between two ports can be prepared by at most one internal pentagon, after which an increment-avoiding internal path of length at most three is available. [Local classification and preparation lemma](petersen-flow-repair.md#2-switches-through-a-contracted-piece-can-be-lifted)

Suppose the restrictions of flows f,g on G are joined in H by a sequence of d circuit switches C₁,…,C_d. Let rⱼ be the number of contracted piece vertices visited by Cⱼ.

**Simultaneous lifting bound.** The sequence lifts to a path from f to g of length at most

\[
\boxed{d+\sum_{j=1}^{d}r_j+3q\ \le\ (q+1)d+3q.}
\]

For each quotient move, there are at most rⱼ preparatory pentagons and one circuit switch whose length is at most |Cⱼ|+3rⱼ. Restriction gives a bijection between the connected components of the two flow reconfiguration graphs.

**Proof.** A quotient circuit visits each of its contracted vertices once, selecting two ports there. Prepare these pieces independently. Preparations alter only internal edges, so they preserve all boundary values, including edges joining two pieces. Replace each contracted vertex's passage by its prepared internal path. The paths lie in disjoint pieces, and the quotient circuit is simple; their union with its uncontracted edges is one simple circuit. The increment is absent everywhere. Perform that switch.

After all d quotient moves, the exterior and port values agree with those of g. Each piece can then be aligned independently in at most three internal switches. This proves the bound. Every quotient flow extends since every nonzero zero-sum four-port tuple extends. Conversely, projecting a circuit of G gives an even subgraph of H, which can be decomposed into edge-disjoint circuits and switched with the same increment. Intermediate edge values remain either their original or final nonzero values. This gives the component bijection. □

The bound concerns flow reachability. It does not assert that prescribed CDC layers, or the original defect potential, are preserved during the moves.

## 5. Preparation can be necessary in every visited piece

A concrete example prevents treating an arbitrary quotient switch as immediately liftable.

Take q≥3 copies of B in a closed necklace, joining a₁ of Bᵢ to b₁ of Bᵢ₊₁ and a₂ to b₂. In every piece use the local flow word

```text
23312221331111
```

All port values are 1. After contracting the pieces, the quotient is a circuit of q vertices with two parallel edges between successive vertices. Adding 2 on the first rail is a valid quotient switch, changing those edge values from 1 to 3.

Inside each starting piece, however, the cut separating {3,4,5,8} from {2,6,7,9} consists of local edges 0,4,5,6, **all of value 2**. It separates a₁ at vertex 4 from b₁ at vertex 2. Therefore no internal path of any length between the selected ports avoids the quotient increment. There is no immediate circuit lift with the prescribed exterior change.

In each piece, first add 4 on the pentagon with local edge indices 0,1,2,4,7. The path 4–3–2 then has values 7,6 and avoids 2. The q prepared paths and the first-rail joining edges form a single circuit of length 3q. Adding 2 on it performs the desired quotient move.

This uses q preparatory pentagons and one final circuit switch. **Within the model of piece-internal preparations followed by one lift of the prescribed quotient switch, q preparations are necessary:** every piece initially has the separating cut, and an internal preparation in one piece cannot change another. Thus the rⱼ preparation term can be attained. This does not establish a q+1 lower bound for unrestricted paths that may temporarily change other exterior edges.

The certificate gives complete graphs, initial and intermediate flows, separating cuts, and switches for q=3,6,12. These graphs serve as lifting examples, not as new CDC obstructions.

## 6. Reproduction and the remaining gap

```bash
python3 research/five-cdc-attempt/global_circuit_repair.py
python3 research/five-cdc-attempt/verify_global_circuit_repair.py
```

The [constructor](global_circuit_repair.py) saves the [certificate](global_circuit_repair.json). The [independent verifier](verify_global_circuit_repair.py) imports no constructor, earlier verifier, or solver. It checks the Petersen factor-obstruction premises, local port distances, graph isomorphisms and covering maps, the winding circuit, all initial and repaired flows, exact cover multiplicities and degrees, all seven initial coordinate obstructions, the six remaining obstructions, and the necklace lifting examples. It also independently checks the m-pentagon repair and its cover, supplying the upper bound for the short-circuit distances.

The periodic examples use m=1,2,3,10,31, reaching **2,232 vertices**. On the largest example the successful circuit has 403 edges and the prescribed cover layer has 1,674 edges. The general winding, counting, and simultaneous-lifting conclusions follow from the proofs above; these five examples audit their implementation rather than justify an extrapolation.

The repeated family now gives an exact separation between unrestricted and short-circuit repair. It cannot disprove a one-switch existence claim by merely increasing the number of repetitions. Conversely, its one-switch repair does not establish such a claim on arbitrary cubic graphs, or from every flow even on this family. The general 5-CDC existence step and general nonincreasing repair remain unresolved by this work.
