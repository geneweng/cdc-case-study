# Cycle Double Cover: a domain-mapping case study

A study of the 2026 proof of the cycle double cover conjecture, read as a chain of
domain transfers: the question is carried out of graphs, through flows and edge labels,
into linear algebra over the two-element field, and settled there by a parity count.

## Files

| File | What it is |
| --- | --- |
| `cdc_proof.pdf` | OpenAI, "A proof of the cycle double cover conjecture" (July 2026). Three pages. |
| `2607.16356v3.pdf` | Sang-il Oum, "A proof of the cycle double cover conjecture by OpenAI: an exposition" (arXiv 2607.16356v3, August 2026). |
| `cdc-domain-map.html` | The case-study document: a diagram of every domain the proof passes through and the mapping between each pair, a table explaining each mapping, a comparison of where the two writeups differ, and a second diagram of neighbouring domains. |

Open `cdc-domain-map.html` in a browser. It is a single self-contained page with inline SVG diagrams and no build step.

A published copy is available as a Claude artifact: https://claude.ai/code/artifact/72388a03-ca59-450f-94fc-1327c731c4f5

## The route

1. Bridgeless graph → cubic 3-edge-connected graph (minimum counterexample, Fleischner splitting).
2. Cubic graph → three spanning trees with no common edge (double every edge, Tutte–Nash-Williams packing).
3. Three trees → nowhere-zero F₂³-flow (symmetric differences of fundamental cycles).
4. Flow → linear system over F₂ (local label sets must agree at both ends of every edge).
5. Linear system → orthogonality check (column space is the orthogonal complement of the left nullspace).
6. Orthogonality check → parity at one vertex (a single bit counts the nonzero certificate vectors).
7. Parity → solvability (each edge is counted at both ends, and 2 = 0 in F₂).
8. Solution → two-element edge labels (a relaxed 3-edge-colouring).
9. Edge labels → cycle double cover (one Eulerian layer per value of F₂³, giving an 8-cycle double cover).

## Where the two papers differ

Both follow the same route. Oum's exposition derives the flow from tree packing instead of citing the
8-flow theorem, makes the local labels symmetric so no extra bit per edge is needed, and replaces
dual vector spaces with an explicit matrix and the column-space identity.
