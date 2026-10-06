# Every globally minimizing flow escapes on the 138-vertex graph

Research date: **6 October 2026**.

**The fixed-projection restriction is removed.** For every nowhere-zero three-bit flow on the saved 138-vertex graph, any marked color class of globally minimum size three is either suitable already or becomes suitable after one six-edge circuit switch. This holds for every projection and every lift. The resulting matching permits a five-layer cover within two fiber rounds and at most 28 actual circuit switches in total.

Two ingredients prove this. First, a complete census shows that among **261,888 one-edge-per-region matchings, exactly one is unsuitable**. Second, a general short-circuit lemma forces a neutral replacement of that matching independently of the surrounding flow.

This resolves neutral repair for all globally minimizing marked flows on this particular graph. It does not prove the five-cycle double cover conjecture or a universal escape theorem.

## 1. A general short-circuit alternative

Let f be a nowhere-zero F₂³-flow on a loopless cubic graph, let a be a nonzero color, and let M=f⁻¹(a). A switch adds a fixed nonzero increment b to every edge of a circuit C; it is legal precisely when C has no edge of color b.

**Short-circuit alternative.** If C has at most six edges and meets M in exactly one edge e, then a legal switch on C either:

1. removes e from M and adds no new a-edge, decreasing |M| by one; or
2. replaces e by one other edge of C, preserving |M| and changing the matching.

**Proof.** Project the flow values modulo the line ⟨a⟩. The edge e has projection zero. The other at most five edges have one of the three nonzero projection values. At least one such value occurs zero or one time on C∖{e}.

If it is absent, choose either full value b in that nonzero coset. Both b and a+b are absent from C. Switching by b is legal, removes e from the a-class, and adds no a-edge.

If the coset occurs exactly once, at an edge e′ with value x, choose b=a+x. No edge of C has value b: e′ is the only edge of that coset and has its other value x. The switch is legal and replaces e by e′. ∎

**Neutral escape corollary.** If no legal circuit switch can reduce |M|, then any circuit of length at most six meeting M once permits a neutral single-edge replacement. In particular, this holds when |M| is the global minimum color multiplicity μ(G).

At such a minimum every nonzero projection value must occur on C∖{e}; otherwise the decreasing case would apply. For a six-edge circuit, the three projection multiplicities are therefore either (3,1,1) or (2,2,1), up to order. There are respectively two or one singleton cosets furnishing neutral replacements.

The conclusion changes the matching. It does not by itself make that matching suitable. Nor does it supply a short circuit when none is available. In particular, this argument cannot directly handle graphs of girth at least seven.

The short-circuit corollary differs from the [previous fiber transport lemma](prepared-minimum-exchange.md): the circuit stays fixed across projections, but the singleton coset and exchanged edge may change. No preparation is needed.

## 2. Exactly one unsuitable candidate matching

Use the graph **ThreeY1Hexagon138** from the [secondary-minimum obstruction](secondary-minimum-obstruction.md). It has 138 vertices, 207 edges, girth five, cyclic edge connectivity five, and global minimum color multiplicity three.

The previous local obstruction proof gives three disjoint charged edge sets, each containing 64 edges incident with one uncolorable 41-vertex five-pole. Every nonzero color must occur at least once in each charged set. Consequently every color class of size three contains **exactly one edge from each charged set and no other edges**.

There are 64³=262,144 choices before enforcing the matching condition. The complete classification is:

| Status | Type triples | Actual choices |
|---|---:|---:|
| Suitable matching | 1,286 | 261,887 |
| Not a matching | 44 | 256 |
| Unsuitable matching | 1 | 1 |
| Total | 1,331 | 262,144 |

Thus there are **261,888 actual matchings** in this family, of which just one is unsuitable:

\[
M_* = \{178,183,189\}
=\{(4,134),(45,130),(99,124)\}.
\tag{1}
\]

This census includes every globally minimum color class. We do not assert that every matching in the census is realizable as a color class of a nowhere-zero three-bit flow.

### How the complete census is certified

The [local intersection table](minimum-matching-secondary.md) groups the 64 possible edges of a five-pole into eleven types: one group of 49 interior edges away from the ports, five groups of two interior edges incident with a specified port, and five single boundary edges. Every edge in a type has the same permitted boundary signatures for an intersection pair F,t with F∩t equal to that edge.

Contracting the three pieces leaves an 18-vertex, 30-edge graph. For each of the 1,286 positive type triples, the certificate supplies a pair of binary cycles on this reduced graph. Its boundary values match an explicitly verified local intersection pair for **every** choice of actual edge in each selected type. Gluing these pairs supplies F,t with F∩t=K for every one of the 261,887 positive matchings.

The 44 invalid types have an explicit shared outside endpoint. The verifier separately enumerates all 262,144 actual choices, rather than relying on the constructor's type weights.

The single negative type is (Bβ,Bβ,Bγ), with only the matching (1). Its existing forced-hexagon certificate is checked directly: every candidate even subgraph avoiding \(M_*\) and covering its endpoints must contain a whole hexagon with exactly three such endpoints. The odd terminal count on that circuit excludes suitability. Its unmatched induced graph is nevertheless connected on 132 vertices, so it attains the secondary optimum (3,0).

No inference from a solver's failure is needed for the negative conclusion. Positive witnesses and this explicit obstruction account for every type.

## 3. One fixed circuit works for every obstructed minimum

The circuit

\[
C=(99,101,104,103,123,124,99)
\tag{2}
\]

has edge set

```text
142, 146, 148, 189, 190, 194.
```

It meets \(M_*\) exactly once, at edge 189. The neutral escape corollary therefore applies to **every** nowhere-zero flow having a-class \(M_*\), whatever its projection modulo a.

A legal neutral switch produces a different three-edge a-class. It still has one edge in each charged set, so the census makes it suitable. In particular, the edge 194=(124,123), outside all three charged sets, cannot be the newly added edge: such a switch would leave the third region without any occurrence of a, contradicting the local lower bound.

There are exactly four possible new edges, and the certificate provides an explicit intersection pair for each resulting matching:

| New edge | Endpoints | New matching |
|---|---|---|
| 142 | (99,101) | {142,178,183} |
| 146 | (101,104) | {146,178,183} |
| 148 | (103,104) | {148,178,183} |
| 190 | (103,123) | {178,183,190} |

All four possibilities occur in actual flows on the full graph.

The shortest circuit lengths through the three edges of \(M_*\) are independently checked to be 13, 9, and 6. Any cardinality-neutral change of \(M_*\) must remove an edge of it, so the six-edge move is shortest possible for changing this matching in every such flow.

This establishes matching-repair distance exactly one when the marked minimum class is \(M_*\), and zero for every other minimum class. It does not claim a minimum number of switches to a successful cover, which could use a different mark.

## 4. The complete local flow-pattern check

Choose linear coordinates so that a=4. This loses no generality: an invertible linear relabeling preserves flows, legal switches, and all color-class sizes.

In path order, the five nonmatching edges of C are

```text
142, 146, 148, 190, 194.
```

Their projected values are the lower two bits of the flow. Three necessary conditions describe their possibilities:

- all three nonzero values occur, by global minimality;
- adjacent path values differ, because each internal path vertex has three nonzero projected incident values;
- the final edge 194 does not have a singleton projection value, by the charged-region argument above.

These conditions leave **36 projected words**. Up to a permutation of the three nonzero projected values, there are six, normalized by making the first two values 1 and 2:

```text
1 2 1 3 1       1 2 1 3 2       1 2 3 1 2
1 2 3 1 3       1 2 3 2 1       1 2 3 2 3
```

Each of these six has an explicit full-graph flow witness. For the fixed matching \(M_*\), the cycle space of G−\(M_*\) has dimension 67, and restriction to these five path edges has rank **five**. Hence every choice of their five high bits occurs within every such projection's lift family. All 36×32=**1,152 full local words** are therefore realized on the graph; there are no additional local restrictions hidden outside C.

For a deterministic rule, take the first path edge whose projection value occurs once, say e′, and switch by

\[
b=4+f(e').
\tag{3}
\]

The verifier constructs a full flow realizing every local word, checks (3), and completes each result to a five-layer cover. The chosen-edge counts are:

| Chosen new edge | Full local words |
|---|---:|
| 142 | 192 |
| 146 | 384 |
| 148 | 384 |
| 190 | 192 |

These count local words, not proportions of all globally minimizing flows. We have not enumerated the total number of full projections.

As a separate check of the general lemma, the verifier exhausts all **9,330** ordered local words on circuits of lengths two through six with exactly one occurrence of a fixed color. Of these, 3,906 permit a decrease because a projection value is missing. The remaining 5,424 all permit a neutral replacement. The proof in Section 1, rather than this finite audit, establishes the general statement.

## 5. Repair of every globally minimizing marked flow

**Graph-specific theorem.** Let f be any nowhere-zero F₂³-flow on ThreeY1Hexagon138, and let a be any color with |f⁻¹(a)|=3. Then a suitable a-class can be reached by at most one cardinality-neutral circuit switch, and a five-layer cover can be constructed within two fiber rounds and at most 28 circuit switches.

**Proof.** Every size-three class lies in the census. If its matching is suitable, no matching exchange is needed. Otherwise it is \(M_*\), and Section 3 gives a six-edge neutral switch to a suitable matching K.

Normalize a to 4 and choose a certified intersection pair F,t with F∩t=K. For the current flow g, write h for its high-bit support. Both h and F contain K, so h△F is a binary cycle avoiding K. Its circuit components give legal switches by 4, leaving the a-class exactly K and setting the high-bit support to F.

The [matching-fiber completion construction](matching-fiber-repair.md) then supplies a fourth coordinate and a five-layer cover. Explicitly, if y,z are the two low-bit supports, use w=t△y△z and the previously verified five-label decoding. This applies to every projection, not only the six representative flows.

The binary cycle h△F has vertex-disjoint circuit components. There are at most ⌊138/5⌋=27 of them, since the graph has girth five. Including the optional first escape gives at most 28 actual circuit switches. ∎

All these moves keep the marked class at global minimum size three. They also retain the secondary optimum (3,0): the exceptional matching has an even unmatched graph, and every suitable matching has no odd unmatched component. Preparation within its own fiber leaves the matching fixed.

The bound is deliberately coarse. The six saved representative repairs use circuit lengths

```text
6,16,15,5,6    6,68    6,55
6,16,15,5,6    6,55    6,62,6,5.
```

The theorem concerns flows containing a globally minimum color class. A flow whose smallest class is larger than three is outside its hypothesis; reaching a global minimum from such a flow is not established here.

## 6. What remains of the general gap

The 138-vertex example disproves suitability of arbitrary secondary minimizers, but it does **not** obstruct neutral escape: every globally minimizing marked flow on that graph is now covered, across all projections.

The general short-circuit alternative is reusable. Its limitations identify two distinct remaining issues: an obstructed minimum may lack a circuit of length at most six meeting it once, or a neutral single-edge replacement may lead to another unsuitable matching. The complete census eliminates the second problem on this graph, and the fixed six-circuit eliminates the first.

A sharper next test should target one of those two failures, rather than vary the lift or projection of this already-resolved exceptional matching. The prepared quotient remains available for longer circuits and for sequences passing through several unsuitable matchings. No argument here excludes a closed collection of such minima in an arbitrary cubic graph, and the general conjecture remains unresolved by this work.

## 7. Reproducibility

The [constructor](short_circuit_minimum_escape.py), [certificate](short_circuit_minimum_escape.json), and [independent verifier](verify_short_circuit_minimum_escape.py) use only Python's standard library and existing repository modules.

```bash
python3 -B research/five-cdc-attempt/short_circuit_minimum_escape.py
python3 -B research/five-cdc-attempt/verify_short_circuit_minimum_escape.py
```

The constructor uses finite-domain propagation to find the reduced positive witnesses. The verifier imports no constructor or solver: it directly checks all 3,489 local intersection witnesses, all 1,286 reduced positive witnesses, their gluing, all 262,144 actual edge choices, and the explicit negative obstruction. It also checks the general local-word alternative, constructs all 1,152 full-graph realizations of the local patterns and their covers, verifies the six saved circuit sequences, and recomputes the shortest-cycle lower bounds.

The graph's minimum-color lower bound, girth, and connectivity are inherited from pinned source certificates; the unchanged 74-million-subset connectivity audit is not repeated. The new certificate has **227,437 bytes** and SHA-256 `b104de72f86ffebf9645dc50f0d34ee6a3884b22da0475645d01dbe954880b5e`. Regeneration is byte-identical. No literature-novelty claim is made.
