#!/usr/bin/env python3
"""Independent standard-library audit of the three-cut construction.

Checks all edge deletions of size at most three, the Petersen projections,
the actual cover, boundary patterns, and the saved-census deduction.
Does not import the constructor, NetworkX, or a flow completion solver.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from verify_lex_trap import circuits_dfs, defects, valid_flow
from verify_layer_selection_obstruction import components, cover_ok


def main():
    directory = Path(__file__).parent
    saved = json.loads((directory / "three_cut_obstruction.json").read_text())
    p, g = saved["petersen"], saved["example"]
    pe = [tuple(e) for e in p["edges"]]
    assert pe == ([(i, (i+1) % 5) for i in range(5)] + [(i, i+5) for i in range(5)]
                  + [(i+5, (i+2) % 5+5) for i in range(5)])
    valid_flow(10, pe, p["seed_flow"])
    cover_ok(10, pe, p["cover"])
    cs = circuits_dfs(10, pe)
    assert len(cs) == 57 and min(map(len, cs)) == 5
    n, edges, flow = g["vertices"], g["edges"], g["flow"]
    assert n == 26 and len(edges) == 39 and g["edge_connectivity"] == 3
    assert len({tuple(sorted(e)) for e in edges}) == 39
    assert all(u != v and 0 <= u < n and 0 <= v < n for u, v in edges)
    assert all(sum(v in e for e in edges) == 3 for v in range(n))
    assert len(components(n, edges, range(39))) == 1
    valid_flow(n, edges, flow)

    # This proves edge connectivity 3 for the saved graph, and locates every
    # nontrivial three-edge cut. No connectivity library is used.
    cut_histogram = Counter()
    cyclic_cuts = []
    examined = 0
    for size in (1, 2, 3):
        for removed in itertools.combinations(range(39), size):
            examined += 1
            cc = components(n, edges, set(range(39))-set(removed))
            if len(cc) == 1:
                continue
            assert size == 3 and len(cc) == 2
            cut_histogram[tuple(sorted(map(len, cc)))] += 1
            if all(sum(u in part and v in part for u, v in edges) >= len(part) for part in cc):
                cyclic_cuts.append(removed)
    assert examined == 9919
    assert cut_histogram == {(1, 25): 26, (9, 17): 2}
    expected_cuts = {tuple(sorted(p["global_edge"] for p in cut["ports"])) for cut in g["three_edge_cuts"]}
    assert set(cyclic_cuts) == expected_cuts

    all_vertices = []
    appearances = Counter()
    blocked = []
    for k, block in enumerate(g["blocks"]):
        vm = block["vertex_map"]
        assert len(vm) == 10
        assert [i for i, v in enumerate(vm) if v is None] == block["removed_vertices"]
        assert block["removed_vertices"] == ([0, 2] if k == 0 else [0])
        vertices = {v for v in vm if v is not None}
        all_vertices.extend(vertices)
        linear = block["linear_map"]
        assert sorted(linear) == list(range(8))
        assert all(linear[a ^ b] == linear[a] ^ linear[b] for a in range(8) for b in range(8))
        local = block["local_flow"]
        assert local == [linear[a] for a in p["seed_flow"]]
        valid_flow(10, pe, local)
        assert len(block["edge_representatives"]) == 15
        for e, global_e in enumerate(block["edge_representatives"]):
            assert flow[global_e] == local[e]
            intended = {vm[v] for v in pe[e] if vm[v] is not None}
            assert intended and set(edges[global_e]) & vertices == intended
            appearances[global_e] += 1
        bad = []
        for normal in range(1, 8):
            selected = {i for i, a in enumerate(local) if (a & normal).bit_count() % 2}
            if not all(sum(v in pe[e] for e in selected) == 2 for v in range(10)):
                continue
            bad.append(normal)
            cc = components(10, pe, selected)
            assert sorted(map(len, cc)) == [5, 5]
            assert all((u in cc[0]) != (v in cc[0]) for e, (u, v) in enumerate(pe) if e not in selected)
            alternating = [c for c in cs if all(sum(e in selected for e in c if v in pe[e]) == 1
                           for v in {v for e in c for v in pe[e]})]
            assert len(alternating) == 5 and {len(c) for c in alternating} == {8}
            assert (30-len(selected)) % 8 != 0
        assert bad == block["two_factor_normals"]
        blocked.append(set(bad))
    assert sorted(all_vertices) == list(range(26))
    connector_edges = {e for cut in expected_cuts for e in cut}
    assert appearances == {e: 2 if e in connector_edges else 1 for e in range(39)}
    for cut in g["three_edge_cuts"]:
        child = cut["leaf_block"]
        leaf = {v for v in g["blocks"][child]["vertex_map"] if v is not None}
        actual = {e for e, (u, v) in enumerate(edges) if (u in leaf) != (v in leaf)}
        assert actual == {p["global_edge"] for p in cut["ports"]}
        for side, k, vertex in (("central", 0, cut["central_vertex"]), ("leaf", child, cut["leaf_vertex"])):
            assert {p[side+"_edge"] for p in cut["ports"]} == {e for e, endpoints in enumerate(pe) if vertex in endpoints}
            assert all(g["blocks"][k]["edge_representatives"][p[side+"_edge"]] == p["global_edge"] for p in cut["ports"])
    assert set.union(*blocked) == set(range(1, 8))
    original_supports = []
    for normal, record in enumerate(g["normals"], 1):
        selected = [e for e, a in enumerate(flow) if (a & normal).bit_count() % 2]
        assert normal == record["normal"] and selected == record["support_edges"]
        original_supports.append(selected)
        assert [c for c in components(n, edges, selected) if len(c) > 1] == [sorted(c) for c in record["support_components"]]
        assert components(n, edges, set(range(39))-set(selected)) == [sorted(c) for c in record["complement_components"]]
        witnesses = [k for k, bad in enumerate(blocked) if normal in bad]
        assert witnesses == record["obstruction_blocks"] and witnesses
        block = g["blocks"][witnesses[0]]
        assert [e for e, global_e in enumerate(block["edge_representatives"]) if global_e in selected] == record["local_factor_edges"]
    assert len({tuple(s) for s in original_supports}) == 7
    assert defects(n, edges, flow) == g["defects"]
    cover = g["cover"]
    cover_ok(n, edges, cover)
    for k, block in enumerate(g["blocks"]):
        projected = [[e for e, global_e in enumerate(block["edge_representatives"]) if global_e in layer] for layer in cover]
        cover_ok(10, pe, projected)
        perm = g["gluing_layer_permutations"][k]
        assert sorted(perm) == list(range(5))
        assert all(projected[perm[i]] == p["cover"][i] for i in range(5))
    labels = [4, 5, 6, 7, 0]
    good = []
    for e in range(39):
        i, j = [i for i, layer in enumerate(cover) if e in layer]
        good.append(labels[i] ^ labels[j])
    assert good == g["cover_induced_flow"]
    valid_flow(n, edges, good)
    assert defects(n, edges, good) == g["cover_induced_defects"]
    assert g["cover_induced_defects"][3] == 0
    assert [e for e, a in enumerate(good) if a & 4] == cover[4]
    assert all(layer not in original_supports for layer in cover)

    # Boundary enumeration uses bit masks and XOR, independently of the
    # constructor's per-label occurrence counts.
    pairs = [m for m in range(32) if m.bit_count() == 2]
    for rec in saved["boundary_states"]:
        width = rec["cut_size"]
        valid = 0
        histogram = Counter()
        for ports in itertools.product(pairs, repeat=width):
            parity = 0
            for mask in ports:
                parity ^= mask
            if parity:
                continue
            valid += 1
            if width == 2:
                assert ports[0] == ports[1]
            elif width == 3:
                assert ports[0] ^ ports[1] == ports[2]
                assert (ports[0] | ports[1] | ports[2]).bit_count() == 3
            else:
                signature = tuple(sorted((ports[0] ^ ports[i]).bit_count() for i in (1, 2, 3)))
                histogram[signature] += 1
        assert valid == rec["parity_valid_assignments"]
        assert histogram == {tuple(r["cap_multiplicities"]): r["count"] for r in rec["four_port_classes"]}

    assert len(saved["four_cut_cap_counterexamples"]) == 2
    for rec in saved["four_cut_cap_counterexamples"]:
        ce, cc = rec["edges"], rec["cover"]
        assert rec["vertices"] == 8 and len(ce) == 12
        assert len({tuple(sorted(e)) for e in ce}) == 12
        assert all(sum(v in e for e in ce) == 3 for v in range(8))
        assert len(components(8, ce, range(12))) == 1
        assert {e for e, (u, v) in enumerate(ce) if (u < 4) != (v < 4)} == set(rec["cut_edges"])
        cover_ok(8, ce, cc)
        masks = [sum(1 << i for i, layer in enumerate(cc) if e in layer) for e in range(12)]
        assert masks == rec["edge_label_masks"]
        ports = [masks[e] for e in rec["cut_edges"]]
        multiplicities = [(ports[0] ^ ports[j]).bit_count() for j in (1, 2, 3)]
        assert multiplicities == rec["cap_multiplicities"] and 2 not in multiplicities

    audit = saved["saved_census_audit"]
    raw = (directory / audit["source"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == audit["source_sha256"]
    census = json.loads(raw)["graphs"]
    nz, orders, histogram = Counter(), Counter(), Counter()
    comparisons = nonempty = bad_count = 0
    for graph in census:
        bad = {r["support_mask"] for r in graph["failed_admissible_first_coordinates"]}
        for a in bad:
            assert not bad.intersection(a ^ b for b in bad)
            comparisons += len(bad)-1
        nonempty += bool(bad)
        bad_count += len(bad)
        histogram[len(bad)] += 1
        nz.update(graph["nz_orbits_by_rank"])
        orders[graph["vertices"]] += 1
    assert len(census) == audit["graphs"] == 4469
    assert nonempty == audit["nonempty_failure_sets"] == 40
    assert bad_count == audit["failed_admissible_supports"] == 1449
    assert comparisons == 2*audit["distinct_support_pairs_checked"] == 62136
    assert not audit["sum_free_violations"]
    assert nz == audit["saved_nz_flow_orbits_by_rank"]
    assert sum(nz.values()) == 97572378
    assert orders == {int(k): v for k, v in audit["graph_orders"].items()}
    assert histogram == {int(k): v for k, v in audit["failure_set_size_histogram"].items()}
    print("Independent checks passed: 9,919 edge-deletion sets; edge connectivity 3;")
    print("exactly two cyclic three-edge cuts; all seven blocked supports; explicit cover;")
    print("boundary states and both cube cap obstructions; all 4,469 saved failure sets are sum-free.")


if __name__ == "__main__":
    main()
