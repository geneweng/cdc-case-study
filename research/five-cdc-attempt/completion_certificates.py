#!/usr/bin/env python3
"""Check odd-cut duality and the obstruction to restricting F to one circuit."""
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import networkx as nx
import explore as x
from first_coordinate_census import components
from isotropic_completion import complete, cut_masks
from snark_repair import three_edge_colorable
from verify_lex_trap import circuits_dfs

HERE = Path(__file__).parent


def cut(edges, vertices):
    return sum(1 << e for e, (u, v) in enumerate(edges) if (u in vertices) != (v in vertices))


def dual_checks():
    results = []
    for name, n, edges in [("Petersen", *x.petersen()),
                           ("Cube", 8, sorted(tuple(sorted(e)) for e in nx.cubical_graph().edges()))]:
        supports = x.all_even_subgraphs(n, edges)
        # U and its complement have the same cut; fix vertex zero outside U.
        odd = [(cut(edges, {v for v in range(n) if mask >> v & 1}), mask)
               for mask in range(1 << n) if mask.bit_count() % 2 and not mask & 1]
        odd.sort(key=lambda row: (row[1].bit_count(), row[1]))
        inc = [(sum(1 << e for e in es), 0) for es in x.BASE.incidence(n, edges)]
        failures = ordinary_failures = pairs = 0; witness = None
        for first in supports:
            hc = components(n, edges, first, keep=False)
            unions = []
            for mask in range(1 << (len(hc)-1)):
                vs = set(v for k, comp in enumerate(hc[1:]) if mask >> k & 1 for v in comp)
                unions.append((cut(edges, vs), sorted(vs)))
            cuts = cut_masks(n, edges, first)
            for second in supports:
                pairs += 1
                free = first | second
                signatures = {}
                for boundary, umask in odd:
                    signatures.setdefault(boundary & free, umask)
                cert = None
                for boundary_s, vertices_s in unions:
                    target = boundary_s & second
                    if target in signatures:
                        umask = signatures[target]
                        vertices_u = {v for v in range(n) if umask >> v & 1}
                        boundary_u = cut(edges, vertices_u)
                        forced = boundary_u & ~free
                        assert len(vertices_u) % 2 == forced.bit_count() % 2 == 1
                        assert boundary_u & free == boundary_s & second
                        cert = {"odd_vertex_set_U": sorted(vertices_u), "component_union_S": vertices_s,
                                "cut_U_edges": [e for e in range(len(edges)) if boundary_u >> e & 1],
                                "forced_edges_in_cut_U": [e for e in range(len(edges)) if forced >> e & 1]}
                        break
                info, third = complete(n, edges, first, second, cuts)
                assert (third is None) == (cert is not None)
                if cert is not None:
                    failures += 1
                    ordinary, z = x.BASE.solve(inc + [(1 << e, 1) for e in range(len(edges)) if not free >> e & 1], len(edges))
                    ordinary_failures += z is None
                    if z is not None and witness is None:
                        witness = {"vertices": n, "edges": edges, "first_coordinate_edges": [e for e in range(len(edges)) if first >> e & 1],
                                   "second_coordinate_edges": [e for e in range(len(edges)) if second >> e & 1],
                                   "ordinary_third_coordinate": z, "dual_cut_certificate": cert,
                                   "matrix_contradiction": info}
        results.append({"name": name, "pairs_checked": pairs, "failed_pairs": failures,
                        "ordinary_full_support_failures": ordinary_failures,
                        "additional_isotropy_failures": failures-ordinary_failures,
                        "every_dual_outcome_matches_linear_solver": True, "example": witness})
    return results


def no_single_circuit_example():
    n0, pe = x.petersen()
    assert not three_edge_colorable(n0, pe)
    saved = json.loads((HERE / "isotropic_completion_results.json").read_text())
    p = next(g for g in saved if g["name"] == "Petersen")
    assert list(map(tuple, p["edges"])) == pe
    layers = p["example"]["lift"]["cover"]
    pairs = [[i for i in range(5) if e in layers[str(i)]] for e in range(len(pe))]
    removed = 0; a, b = pe[removed]
    edges = []; edge_pairs = []; branches = []
    for k, target in enumerate(((0, 1), (1, 2), (0, 2))):
        mapping = dict(zip(pairs[removed], target))
        mapping.update(zip([i for i in range(5) if i not in mapping], [i for i in range(5) if i not in target]))
        offset = 2 + 10*k
        branch = []
        for e, (u, v) in enumerate(pe):
            if e == removed:
                continue
            branch.append(len(edges)); edges.append((u+offset, v+offset))
            edge_pairs.append([mapping[i] for i in pairs[e]])
        for e in ((0, a+offset), (1, b+offset)):
            branch.append(len(edges)); edges.append(e); edge_pairs.append(list(target))
        branches.append(branch)
    n = 32
    inc = x.BASE.incidence(n, edges)
    g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(edges)
    assert g.number_of_edges() == 48 and nx.is_connected(g) and not list(nx.bridges(g))
    assert all(len(pair) == len(set(pair)) == 2 for pair in edge_pairs)
    assert all(sum(i in edge_pairs[e] for e in es) in (0, 2) for i in range(5) for es in inc)
    circuits = circuits_dfs(n, edges)
    for c in circuits:
        assert any(not set(c).intersection(branch) for branch in branches)
    return {"vertices": n, "edges": edges, "branches_including_connectors": branches,
            "simple_connected_bridgeless_cubic_verified": True,
            "circuits_enumerated_by_independent_dfs": len(circuits),
            "every_circuit_misses_an_entire_Petersen_branch": True,
            "Petersen_non_three_edge_colorability_checked": True,
            "cover": {str(i): [e for e, pair in enumerate(edge_pairs) if i in pair] for i in range(5)},
            "exact_double_coverage_and_even_degrees_verified": True}


if __name__ == "__main__":
    result = {"dual_checks": dual_checks(), "no_admissible_single_circuit": no_single_circuit_example()}
    (HERE / "completion_certificates.json").write_text(json.dumps(result, indent=2)+"\n")
    print([(r["name"], r["pairs_checked"], r["additional_isotropy_failures"]) for r in result["dual_checks"]])
    print("32-vertex example:", result["no_admissible_single_circuit"]["circuits_enumerated_by_independent_dfs"], "circuits checked; five-layer cover verified.")
