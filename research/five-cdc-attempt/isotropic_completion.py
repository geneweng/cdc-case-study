#!/usr/bin/env python3
"""Exact linear completion after choosing two binary cycles; see continuation.md.

The general existence of a successful choice is NOT established.
Run this file to cross-check the reformulation on Petersen and the cube.
"""
from collections import Counter
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import networkx as nx
import explore as x

HERE = Path(__file__).parent


def cut_masks(n, edges, first):
    h = nx.Graph()
    h.add_nodes_from(range(n))
    h.add_edges_from(e for i, e in enumerate(edges) if not (first >> i & 1))
    return [sum(1 << i for i, (u, v) in enumerate(edges) if (u in k) != (v in k))
            for k in nx.connected_components(h)]


def complete(n, edges, first, second, cuts=None):
    """Return a third binary cycle or a verified linear inconsistency witness.

    first and second are edge-support bitmasks of binary cycles.
    All three coordinates are allowed to be linearly dependent.
    """
    incidence = [sum(1 << e for e in es) for es in x.BASE.incidence(n, edges)]
    assert all((first & row).bit_count() % 2 == (second & row).bit_count() % 2 == 0
               for row in incidence)
    if cuts is None:
        cuts = cut_masks(n, edges, first)
    rows = [(row, 0) for row in incidence]
    rows += [(1 << e, 1) for e in range(len(edges)) if not ((first | second) >> e & 1)]
    rows += [(cut & second, 0) for cut in cuts]
    result, third = x.BASE.solve(rows, len(edges))
    return result, third


def verify_graph(name, n, edges):
    supports = x.all_even_subgraphs(n, edges)
    basis = [sum(1 << e for e in c) for c in x.BASE.cycle_basis(n, edges)]
    success = flows = form_checks = 0
    bad_first = []
    counts = Counter()
    witness = failure = None
    for first in supports:
        cuts = cut_masks(n, edges, first)
        first_successes = 0
        for b in basis:
            assert all((cut & b).bit_count() % 2 == 0 for cut in cuts)  # Alternating.
            assert all((cut & first & b).bit_count() % 2 == 0 for cut in cuts)  # F in radical.
            for c in basis:
                assert sum((cut & b & c).bit_count() % 2 for cut in cuts) % 2 == 0
                form_checks += 1  # The sum of the component forms is zero.
        for second in supports:
            result, third = complete(n, edges, first, second, cuts)
            if third is None:
                assert result["certificate_verified"]
                if failure is None and first and second:
                    failure = {"first_cycle_edges": [e for e in range(len(edges)) if first >> e & 1],
                               "second_cycle_edges": [e for e in range(len(edges)) if second >> e & 1],
                               "linear_system_inconsistency": result}
                continue
            success += 1
            first_successes += 1
            multiplicity = 1 << result["affine_dimension"]
            flows += multiplicity
            counts[result["affine_dimension"]] += 1
            f = [4 * ((first >> e) & 1) + 2 * ((second >> e) & 1) + ((third >> e) & 1)
                 for e in range(len(edges))]
            assert 0 not in f and x.defect(n, edges, f, 4) == 0
            lift = x.extra_coordinate_lift(n, edges, f)
            assert lift["cover"] is not None
            if witness is None and first:
                witness = {"first_cycle_edges": [e for e in range(len(edges)) if first >> e & 1],
                           "second_cycle_edges": [e for e in range(len(edges)) if second >> e & 1],
                           "third_cycle_edges": [e for e in range(len(edges)) if third >> e & 1],
                           "flow": f, "linear_system": result, "lift": lift}
        if not first_successes:
            bad_first.append([e for e in range(len(edges)) if first >> e & 1])
    if name == "Petersen":
        assert flows == 4560  # Separate full 8^6 enumeration in run_experiments.py.
        assert len(bad_first) == 7 and [] in bad_first  # Six 2-factors, and zero.
    direct_cube = None
    if name == "Cube":
        # Separate enumeration and fourth-coordinate solver check the affine counts.
        cycle_basis = x.BASE.cycle_basis(n, edges)
        nz = successful = 0
        for coefficients in itertools.product(range(8), repeat=len(cycle_basis)):
            f = [0] * len(edges)
            for circuit, a in zip(cycle_basis, coefficients):
                for e in circuit:
                    f[e] ^= a
            if 0 in f:
                continue
            nz += 1
            successful += x.extra_coordinate_lift(n, edges, f)["cover"] is not None
        assert nz == 5712 and successful == flows == 2784
        direct_cube = {"all_three_coordinate_flows_examined": 8 ** len(cycle_basis),
                       "nowhere_zero_flows": nz, "canonical_lifts": successful}
    return {"name": name, "vertices": n, "edges": edges, "cycle_dimension": len(basis),
            "pairs_examined": len(supports) ** 2, "consistent_pairs": success,
            "successful_labeled_flows_counted_by_affine_dimension": flows,
            "affine_dimension_histogram": dict(sorted(counts.items())),
            "first_cycles_with_no_completion": bad_first,
            "form_identity_basis_checks": form_checks,
            "every_consistent_pair_decoded_and_checked": True, "example": witness,
            "inconsistency_example": failure, "independent_cube_enumeration": direct_cube}


if __name__ == "__main__":
    cube = nx.cubical_graph()
    graphs = [("Petersen", *x.petersen()),
              ("Cube", 8, sorted(tuple(sorted(e)) for e in cube.edges()))]
    results = [verify_graph(*g) for g in graphs]
    (HERE / "isotropic_completion_results.json").write_text(json.dumps(results, indent=2) + "\n")
    for r in results:
        print(r["name"], r["pairs_examined"], "pairs;", r["consistent_pairs"],
              "consistent;", r["successful_labeled_flows_counted_by_affine_dimension"], "successful flows")
