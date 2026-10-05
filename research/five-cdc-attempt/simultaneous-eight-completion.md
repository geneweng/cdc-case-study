# Simultaneous fixed-layer completion through eight-cycle regions

**5 October 2026.** Prescribed-layer completion reduces exactly to the core for **any number of selected cycles of lengths three through eight**, in both Blowup and SemiBlowup. There is no longer a restriction to one eight-cycle region. Starting from a compatible core cover, a sequence of auxiliary-label exchanges fixes every rejected boundary while preserving the entire prescribed quotient layer.

The new ingredient is a way to protect boundaries that already extend. Pair their affected ports so that exchanging any collection of those pairs keeps them extendible. These local pairings fit together into closed trails on the core. Each chosen trail fixes a bad region and leaves every good region good, so at most the initial number of bad regions need be processed.

This is a conditional completion theorem for the specified graph constructions. It still requires a core cover containing the restricted prescribed layer. Regions longer than eight with at least eight marked cuts, and the general 5-cycle double cover conjecture, remain unresolved by this work. No literature novelty is claimed.

Follow-up: [Fixed-layer completion through length nine](nine-cycle-completion.md) handles all three new marked-boundary types at length nine, including two distinguished-layer ports. The same protected-trail argument then gives simultaneous completion for any mixture of selected lengths three through nine.

## 1. The reduction and repair bounds

As in the [single-eight-cycle report](eight-cycle-completion.md), let X be either Blowup(S,D) or SemiBlowup(S,D) for a simple cubic base S and vertex-disjoint selected cycles D. Contract every inserted Petersen four-pole B to obtain H, and contract each selected cycle region to obtain K=S/D. Let E₀ be the edges retained in H, including the core edges E(K). Loops and parallel edges in K are allowed; a loop has two incidences.

A five-layer CDC consists of at most five even subgraphs, possibly disconnected or empty, covering every edge exactly twice. Equivalently every edge has a two-label subset of {0,1,2,3,4}, and the XOR of incident label sets is zero at each vertex. Let the prescribed even subgraph F of H be label 0.

**Simultaneous eight-cycle theorem.** If every selected cycle has length between three and eight, then

\[
\boxed{\quad
F\text{ extends to a five-layer CDC of }H
\iff
F\cap E(K)\text{ extends to a five-layer CDC of }K.
\quad}
\tag{1}
\]

Here “extends” means that F itself is one whole layer. The core cover may change during the construction, but its label-0 support remains fixed on every edge.

If b regions reject the initially supplied compatible core cover, at most **b auxiliary-label exchanges on closed trails** produce a core cover that extends through all regions. Each trail uses every edge at most once and visits its target core vertex just once. It may revisit other vertices. The proof does not assert that each exchange can be chosen on a single simple circuit while preserving all good boundaries at every intermediate step.

**Flow repair consequence.** Let f be any nowhere-zero three-bit flow on X, and ℓ any nonzero coordinate. Completion of ℓ(f)|E(K) on the core is equivalent to completion after switches confined to the inserted B pieces. Once a compatible core cover is supplied, **at most 2q internal pentagon switches** suffice, where q is the number of pieces. Every E₀ flow value stays fixed.

The cover exchanges select the desired quotient cover; they do not switch the given flow. After constructing that cover, [joint Petersen completion](joint-boundary-completion.md) supplies the at-most-two-pentagon repair in each B. The distinction matters: the label exchanges may traverse long core trails, while the actual flow switches remain five-edge circuits inside individual pieces.

The theorem also permits additional selected regions of arbitrary length when each has at most seven marked cuts for the prescribed F, as defined below.

## 2. Which regions need protection?

Use the [marked-cut criterion](eight-cycle-completion.md#3-marked-cuts-and-a-shorter-proof-of-the-length-threshold). At junction i, rᵢ is the core pair and a,b,c,d are its four B-port representatives, with left charge a⊕b and right charge c⊕d=(a⊕b)⊕rᵢ. A cut between consecutive junctions is **marked** if either adjacent port pair consists entirely of F-edges. Its marked status depends only on F.

Put U={1,2,3,4}, represented by mask 30, and Rᵢ=⊕ⱼ<ᵢrⱼ. If the initial charge has label-0 parity p, the eight candidate charges are the even label sets of that parity. The forbidden candidates are exactly

\[
\{U\oplus R_i:i\text{ is marked}\}.
\tag{2}
\]

Thus every compatible boundary extends when there are at most seven marked cuts. If a region of length eight can fail, all eight cuts must be marked. In that case every core port lies outside F, every rᵢ is a two-element subset of U, and the boundary fails exactly when its eight prefix values R₀,…,R₇ are distinct.

Call an eight-cycle region with all eight cuts marked **critical**. This designation is fixed by F. Its current boundary is **bad** when those prefixes are distinct, and **good** otherwise. Noncritical regions covered by the theorem always extend, whatever compatible core cover is chosen.

The bad words are exactly the 1,488 Hamiltonian boundary words classified previously. They trace all eight even subsets of U using auxiliary pairs as successive differences. The preceding finite lemma gives, for any bad word, an auxiliary pair t={α,β} such that at least four ports contain exactly one of α,β, and at most one pair of these ports fails to escape when both port labels are exchanged. Every perfect matching of the affected ports therefore contains an escaping pair.

This handles a chosen bad region. The missing step was keeping other good critical regions good.

## 3. Protected pairings at a good boundary

Fix an auxiliary pair t and a good closed auxiliary boundary word r=(r₀,…,r₇). Let

\[
I_t(r)=\{i:|r_i\cap t|=1\}.
\]

This set has even size: its parity is the sum of the incidence parities of the two exchanged labels. On an affected edge, exchanging the labels replaces rᵢ by rᵢ⊕t, another auxiliary pair.

A perfect matching P of Iₜ is **protected** if toggling the endpoints of any subset of its matched pairs leaves the boundary good. This includes the empty subset and the whole matching. Since the endpoints are toggled in pairs, every such boundary remains closed.

**Protected-pairing lemma.** Every good closed auxiliary boundary word of length eight has a protected matching for every auxiliary pair t.

### Exhaustive finite proof

Permuting the four auxiliary labels reduces the lemma to t={1,2}, mask 6. There are exactly **210,048** closed auxiliary words of length eight, found by enumerating the first seven pairs and taking their XOR as the required last pair when it is an auxiliary pair. Of these words, 1,488 are bad and 208,560 are good.

For fixed t, the affected positions of a word do not change under any label exchanges. Replace the pair at each affected position by the smaller integer mask in {rᵢ,rᵢ⊕t}; retain the other pairs. This gives a canonical word k. A bit mask x on the affected positions recovers r by toggling those positions of k. The closed words in such a class have one specified parity of x.

Only **462** such classes contain any bad word. Together they contain **10,848** closed words: the 1,488 bad words and **9,360** good words needing a protection check. Every other good word—**199,200** of them—has no bad word reachable by any allowed even set of port toggles, so any perfect matching is protected.

For a threatened good word with bit assignment x, enumerate all perfect matchings of its at most eight affected positions. For each matching P, its possible toggle sets form

\[
L(P)=\left\{\bigcup_{\{i,j\}\in A}\{i,j\}:A\subseteq P\right\}.
\]

The matching is protected exactly when x⊕s is not a bad assignment for every s∈L(P). The exhaustive count is:

| Protected matchings for a threatened good word | Number of words |
|---:|---:|
| 1 | 192 |
| 2 | 864 |
| 5 | 192 |
| 6 | 384 |
| 9 | 1,536 |
| 10 | 1,152 |
| 12 | 2,880 |
| 60 | 464 |
| 61 | 960 |
| 68 | 576 |
| 75 | 160 |

Every count is positive; the word counts sum to 9,360. This proves the finite lemma. The 192 cases with just one protected matching also show that an arbitrary pairing is insufficient.

For example, for the good boundary word

```text
12,13,12,14,23,12,13,34
```

and t=12, the affected positions are {1,3,4,6}, indexed from zero. The unique protected matching is {(1,3),(4,6)}.

The independent verifier takes a different route through the finite check. It first enumerates every closed word, then recognizes protection by a cut condition: for each dangerous difference d between the current assignment and a bad assignment, at least one matched pair must have one endpoint in d and the other outside d. Otherwise d is a union of whole matched pairs and would be reachable. It also checks every subset of the chosen matching directly by rebuilding the changed prefixes. A digest of all 9,360 witness rows makes the result reproducible.

## 4. A global exchange that preserves all good regions

Take a current core cover and choose a bad critical region at vertex v. Choose t={α,β} using the escaping-pair lemma. Let T be the symmetric difference of core layers α and β. Its edges contain exactly one of these labels. T is even at every vertex.

Specify a pairing of the T-incidences at every vertex except v:

* At every good critical region, use a protected matching in its cyclic port order.
* At every other vertex, pair its T-incidences arbitrarily.

Split v into one terminal for each T-incidence. Following a core edge and then the specified local pairing decomposes T into terminal-to-terminal trails and closed trails. Each terminal trail uses no edge twice. The terminal trails induce a perfect matching of the affected incidences at v, including pairs joined by a loop at v.

By the escaping-pair lemma, some terminal trail joins an escaping pair at v. Restoring v makes this a closed trail with exactly two incidences at v. Exchange α and β on all of its edges.

Every changed edge still has two distinct labels. At each vertex the trail uses an even number of incidences, so the parities of both exchanged labels remain even. Label 0 is unchanged edge by edge. Thus the result is another core cover with the same distinguished layer.

At v, exactly the selected escaping pair changes, making its boundary good. At every previously good critical region, the trail uses the endpoints of a subset of its local matched pairs. Its protected matching guarantees that it remains good, even if the trail passes through that vertex more than once. Noncritical regions with at most seven marked cuts remain extendible as well.

Consequently the new bad-region set is a **proper subset** of the old one. Repeating this construction terminates after at most b exchanges, where b is the initial number of bad regions. All regional boundaries then extend with the same prescribed F by (2). Their local covers agree on the shared core edges and glue to a cover of H. Restricting a cover of H to core edges proves the other direction of (1). □

No assumption is made that a core trail has bounded length. Each exchange uses at most |E(K)| edges. With the constant finite tables precomputed, the pairing, trail search, and cover update take O(|V(K)|+|E(K)|) per exchange; final regional extension takes O(q). The theorem gives a terminating construction, not an optimum number of cover exchanges.

## 5. Why protecting a good region matters

The saved two-region example has core vertices 0 and 1 joined by eight parallel edges. Edge e has auxiliary pair

```text
e:     0  1  2  3  4  5  6  7
pair: 12 13 12 14 12 13 12 14
```

The cyclic incidence orders at the two vertices are

```text
vertex 0: 4,5,6,7,0,1,2,3
vertex 1: 0,1,3,2,5,4,7,6.
```

Initially only vertex 0 is bad. Exchanging labels 2 and 3 on the two-edge circuit {0,1} fixes vertex 0 but makes vertex 1 bad: the bad set changes from {0} to {1}. This verifies the interference anticipated at the previous checkpoint. It is not a counterexample to completion.

The protected construction instead exchanges those labels on edges {0,2}, making both boundaries good in one step. The certificate verifies both the unsuccessful unprotected step and the successful protected one.

A separate three-region example explicitly exercises a closed trail that visits a good region twice. Its selected core edge sequence is 0,5,6,2, following vertices 0,1,2,1,0. The four changed incidences at vertex 1 are two pairs of its protected matching. This is why the finite lemma checks every subset of pairs, rather than only individual pair exchanges.

## 6. Full cubic graph certificates

The base family starts with m disjoint eight-cycles. Its contracted core has four parallel edges from hub i to hub i+1 modulo m, with pairs 12,13,12,14 on each group of four. A specified permutation assigns the eight incidences to each cycle's vertices. Before any Petersen attachment, the core has the constant four-flow value 1, and all regional port representatives belong to the prescribed F. The construction gives explicit initial three-bit flows on the full cubic graphs.

The largest examples attach Petersen by a two-edge sum along a core edge outside the distinguished layer. Their cores have no nowhere-zero four-flow: such a flow would have equal nonzero values across the two-edge cut and would restore a four-flow on Petersen. The verifier independently checks this by restoring Petersen and testing all 4,096 pairs of its 64 even supports. Hence the largest examples do not fall under the earlier four-flow sufficient condition.

| Example | Regions | Initial bad regions | Cover exchanges | Blowup vertices / B pentagons | SemiBlowup vertices / B pentagons |
|---|---:|---:|---:|---:|---:|
| Two bad regions | 2 | 2 | 1 | 176 / 14 | 144 / 8 |
| A fragile good region | 2 | 1 | 1 | 176 / 13 | 144 / 7 |
| Repeated visit to a good region | 3 | 1 | 1 | 264 / 20 | 216 / 11 |
| Eight bad regions, no core four-flow | 8 | 8 | 4 | 714 / 51 | 586 / 28 |

In the last row, the bad-region counts are 8→6→4→2→0. The cover trails have lengths 2,28,28,28. All actual flow switches are B-internal pentagons, and every quotient edge retains its original flow value. All final covers have the prescribed quotient layer. These are constructed switch counts, not minimum distances.

## 7. Verification and the next boundary

From this directory:

```bash
python3 -B simultaneous_eight_completion.py
python3 -B verify_simultaneous_eight_completion.py
python3 -B verify_joint_boundary_completion.py
```

* [Constructor](simultaneous_eight_completion.py) and [certificate](simultaneous_eight_completion.json) contain the protected-pairing audit, all cover exchanges, and eight full graph completions.
* [Independent verifier](verify_simultaneous_eight_completion.py) imports no constructor or earlier verifier. It enumerates all closed boundary words, checks every target's escaping-choice lemma, verifies the protected matchings, reconstructs all full graphs and quotients, and checks every cover exchange, intermediate flow, fixed quotient value, and final cover.

The finite lemma and the transition-pairing proof resolve simultaneous fixed-layer completion for cycles through length eight. The next unresolved boundary is **length nine with at least eight marked cuts**. A rejected word there may have a different pattern of distinguished-layer ports or repeated marked prefix states, so neither the Hamiltonian-word classification nor its protected-pairing lemma automatically applies.
