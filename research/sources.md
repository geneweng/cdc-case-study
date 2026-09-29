# Sources, provenance, and status notes

Checked on **2026-09-29**. Primary papers and author/institutional pages were preferred. Search-result dates alone were not treated as theorem dates. This is a focused literature review, not an exhaustive bibliography or formal proof audit.

## Material supplied by the user

| Source | Exact material used |
|---|---|
| [Published case study](https://geneweng.github.io/cdc-case-study/cdc-domain-map.html) / [local HTML](../cdc-domain-map.html) | Domain-transfer map, comparison of proofs, neighboring conjectures, binary linear algebra appendix |
| OpenAI, [A proof of the cycle double cover conjecture](../cdc_proof.pdf), July 2026 | Complete three-page manuscript; especially Lemmas 2.1–2.2, equations (2)–(9) |
| Sang-il Oum, [exposition v3](https://arxiv.org/abs/2607.16356v3), revised August 1, 2026; [local PDF](../2607.16356v3.pdf) | Sections 5–7: symmetric labels and dual criterion. Section 9: remaining conjectures, established consequences, matroid limitations |

The public HTML was fetched directly after the web reader could not open GitHub Pages. The local and public domain-map files both have SHA-256:

```text
0c1a869e7508054866d5254d437f6b0b7b7731c9bcfa24dea3dde58ba9a27627
```

Repository HEAD before this research: `ef9e4eb` (2026-09-05). The relevant proof equations and Oum's Sections 9.1–9.5 were also checked in rendered PDF pages, avoiding dependence on imperfect HTML equation rendering.

This report uses the supplied CDC result as its starting point, consistent with the subsequent papers below. It does not claim to have rerun a Lean formalization or independently established publication/refereeing status for the July proof.

## Additional literature

| ID | Reference and link | Location / role in this review |
|---|---|---|
| HS26 | Radek Hušek and Robert Šámal, *Exponentially Many Circuit Double Covers*, [arXiv:2607.24724v1](https://arxiv.org/abs/2607.24724v1), July 27, 2026; [full text](https://arxiv.org/html/2607.24724v1) | Primary extension paper. Theorems 1.7–1.8; Observation 3.15; Theorem 3.16. A preprint, not treated here as a verified journal publication. |
| HS25 | Radek Hušek and Robert Šámal, *Counting circuit double covers*, Journal of Graph Theory 108 (2025), 374–395, [DOI](https://doi.org/10.1002/jgt.23187) | Original quantitative conjecture and tightness context. |
| Z26 | Jean Paul Zerafa, *A tris of perfect matchings in bridgeless claw-free cubic graphs*, [arXiv:2609.28118v1](https://arxiv.org/abs/2609.28118v1), September 23, 2026 | Fresh explicit open-status evidence for five-layer CDC; context for Berge–Fulkerson. Its special-class result is not a general matching-conjecture resolution. |
| HO12 | Arthur Hoffmann-Ostenhof, *A note on 5-cycle double covers*, [arXiv:1209.0096](https://arxiv.org/abs/1209.0096), 2012 | Precise distinction between strong CDC and a stronger five-layer prescribed-circuit variant. |
| K26 | Shiva Kintali, [*Me, My Math Proofs and AI – Part I*](https://kintali.wordpress.com/2026/07/14/ai-and-math-proofs-part-i/), July 14, 2026 | Author research note explicitly discussing strong CDC as still open. Status corroboration only; its separate proof claims are not used. |
| LL26 | Jiaao Li and Xinyuan Li, *Nowhere-zero 3-flows in graphs with forbidden edge-cuts*, [arXiv:2609.08377v1](https://arxiv.org/abs/2609.08377v1), September 8, 2026 | Tutte 3-flow formulation and current partial-results context. |
| HG19 | Jakob Hansen and Robert Ghrist, *Toward a spectral theory of cellular sheaves*, Journal of Applied and Computational Topology 3 (2019), 315–358, [DOI](https://doi.org/10.1007/s41468-019-00038-7); [arXiv](https://arxiv.org/abs/1808.01513) | Standard language of local vector spaces, restriction maps, global sections, and sheaf cohomology. Our CDC specialization is an explanatory deduction. |
| P26 | Bryce Putman, *A 112-Vertex Counterexample to the Petersen Coloring Conjecture*, [arXiv:2608.10012](https://arxiv.org/abs/2608.10012), August 2026 | Prevents incorrectly recommending Petersen coloring as an open conjecture to prove. No claim here that the reported order is minimal. |
| E26 | Louis Esperet, Kevin Hendrey, Aurélie Lagoutte, Margaux Marseloo, Sergey Norin and Raphael Steiner, *Nowhere-zero flow reconfiguration*, [arXiv:2512.17342v4](https://arxiv.org/html/2512.17342v4), July 3, 2026 | Theorems 3.2 and 6.15 distinguish availability of circuit moves from general connectivity in F₂⁸. Used in the neutral-repair continuation, without inferring potential-controlled connectivity in F₂³. |

## How to read the open-status claims

- **5-CDC:** explicitly still open in a September 23 primary preprint.
- **Exponential counting bound:** stated as a conjecture in the July extension paper, which proves subclasses; no later general resolution found.
- **Berge–Fulkerson:** stated as a conjecture in the supplied August exposition and discussed as a major conjecture in September literature.
- **Orientable 5-CDC / Tutte 5-flow / general small CDC:** retained as conjectures in the supplied exposition and related literature; no later general resolution found. A solved ordinary CDC does not imply these strengthenings.
- **Tutte 3-flow:** September primary research proves special cases, continuing to formulate the universal statement as a conjecture.
- **Strong CDC:** precise statement from an older research paper, with July author-note corroboration; this has weaker recent status documentation than 5-CDC.

## What was produced in this folder

- [README.md](README.md): answers, candidate ranking, explicit remaining obstacles, and recommended research program.
- [algebraic-framework.md](algebraic-framework.md): generic theorem and proof, CDC specialization, sheaf interpretation, and an explicit higher-dimensional obstruction.
- [verify_algebra.py](verify_algebra.py): original standard-library implementation of finite checks and example construction; the five-label specialization is attributed in its module documentation.
- [verification_results.json](verification_results.json): generated results, witnesses, edge ordering, and reproducibility seeds.

The suggested flow-repair project, boundary-condition construction, generic cancellation criterion, and finite examples are analysis supplied for this request. They should not be mistaken for claims that any unresolved conjecture has been proved or for claims of novelty over the complete literature.
