#!/usr/bin/env python3
"""Standard-library-only audit of the all-coordinate obstruction certificate.

Does not import the constructor, its cycle-space enumeration, NetworkX,
the completion solver, or any component-permutation classification.
"""
from collections import Counter
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from verify_lex_trap import circuits_dfs, defects, valid_flow


def components(n, edges, chosen):
    adj = [set() for _ in range(n)]
    for e in chosen:
        u, v = edges[e]
        adj[u].add(v); adj[v].add(u)
    unseen = set(range(n))
    result = []
    while unseen:
        start = min(unseen)
        found, pending = {start}, [start]
        unseen.remove(start)
        while pending:
            for v in adj[pending.pop()] & unseen:
                unseen.remove(v); found.add(v); pending.append(v)
        result.append(sorted(found))
    return result


def cover_ok(n, edges, cover):
    assert len(cover) == 5
    counts = [0]*len(edges)
    for layer in cover:
        assert len(layer) == len(set(layer))
        degree = [0]*n
        for e in layer:
            assert 0 <= e < len(edges)
            counts[e] += 1
            u, v = edges[e]
            degree[u] += 1; degree[v] += 1
        assert all(d in (0, 2) for d in degree)
    assert counts == [2]*len(edges)


def main():
    saved = json.loads((Path(__file__).parent / "layer_selection_obstruction.json").read_text())
    p = saved["petersen"]
    pe = [tuple(e) for e in p["edges"]]
    assert pe == ([(i, (i+1) % 5) for i in range(5)] + [(i, i+5) for i in range(5)]
                  + [(i+5, (i+2) % 5+5) for i in range(5)])
    inc = [sum(1 << e for e, endpoints in enumerate(pe) if v in endpoints) for v in range(10)]
    even = [mask for mask in range(1 << 15) if all((mask & row).bit_count() % 2 == 0 for row in inc)]
    factors = {mask for mask in even if all((mask & row).bit_count() == 2 for row in inc)}
    assert len(even) == 64 and len(factors) == 6
    cs = circuits_dfs(10, pe)
    assert len(cs) == p["circuits"] == 57 and min(map(len, cs)) == 5
    assert {sum(1 << e for e in r["factor_edges"]) for r in p["two_factors"]} == factors
    for record in p["two_factors"]:
        first = set(record["factor_edges"])
        cc = components(10, pe, first)
        assert sorted(map(len, cc)) == [5, 5]
        assert all((u in cc[0]) != (v in cc[0]) for e, (u, v) in enumerate(pe) if e not in first)
        alternating = [c for c in cs if all(
            sum(e in first for e in c if v in pe[e]) == 1
            for v in {v for e in c for v in pe[e]})]
        assert alternating == [tuple(c) for c in record["alternating_circuits"]]
        assert len(alternating) == 5 and {len(c) for c in alternating} == {8}
        assert (2*len(pe)-len(first)) % 8 != 0
    # Independently enumerate every labeled binary three-flow, via even masks.
    histogram = Counter()
    for a, b, c in itertools.product(even, repeat=3):
        if a | b | c == (1 << 15)-1:
            supports = {a, b, c, a ^ b, a ^ c, b ^ c, a ^ b ^ c}
            assert len(supports) == 7 and 0 not in supports
            histogram[len(supports & factors)] += 1
    assert sum(histogram.values()) == 28560
    assert histogram == {int(k): 168*v for k, v in p["two_factor_coordinate_histogram"].items()}
    assert sum(histogram.values()) == 168*p["rank_three_nz_flow_orbits"]
    cover_ok(10, pe, p["cover"])

    g = saved["example"]
    n, edges, flow = g["vertices"], g["edges"], g["flow"]
    assert n == 30 and len(edges) == 45
    assert len({tuple(sorted(e)) for e in edges}) == 45
    assert all(u != v and 0 <= u < n and 0 <= v < n for u, v in edges)
    assert all(sum(v in e for e in edges) == 3 for v in range(n))
    assert len(components(n, edges, range(45))) == 1
    assert all(len(components(n, edges, set(range(45))-{e})) == 1 for e in range(45))
    valid_flow(n, edges, flow)
    cuts = set()
    for cut in g["two_edge_cuts"]:
        leaf = set(g["blocks"][cut["leaf_block"]]["vertices"])
        actual = tuple(e for e, (u, v) in enumerate(edges) if (u in leaf) != (v in leaf))
        assert actual == tuple(cut["cut_edges"]) and len(actual) == 2
        assert len(components(n, edges, set(range(45))-set(actual))) == 2
        cuts.add(actual)
    appearances = Counter()
    blocked_sets = []
    for k, block in enumerate(g["blocks"]):
        vertices = set(block["vertices"])
        assert vertices == set(range(10*k, 10*k+10))
        mapping = block["linear_map"]
        assert sorted(mapping) == list(range(8))
        assert all(mapping[a ^ b] == mapping[a] ^ mapping[b] for a in range(8) for b in range(8))
        local = block["local_flow"]
        assert local == [mapping[a] for a in p["seed_flow"]]
        valid_flow(10, pe, local)
        for e, path in enumerate(block["edge_representatives"]):
            inside = [v-10*k for i in path for v in edges[i] if v in vertices]
            assert sorted(inside) == sorted(pe[e])
            assert all(flow[i] == local[e] for i in path)
            assert len(path) in (1, 2)
            if len(path) == 2:
                assert tuple(path) in cuts and e in block["removed_edges"]
                assert all(sum(v in vertices for v in edges[i]) == 1 for i in path)
            else:
                assert e not in block["removed_edges"]
            appearances.update(path)
        bad = [l for l in range(1, 8) if sum(1 << i for i, a in enumerate(local)
               if (a & l).bit_count() % 2) in factors]
        assert bad == block["two_factor_normals"]
        blocked_sets.append(set(bad))
    connectors = {i for cut in cuts for i in cut}
    assert appearances == {e: 2 if e in connectors else 1 for e in range(45)}
    assert set.union(*blocked_sets) == set(range(1, 8))
    original_supports = []
    for normal, record in enumerate(g["normals"], 1):
        first = [e for e, a in enumerate(flow) if (a & normal).bit_count() % 2]
        assert record["normal"] == normal and first == record["support_edges"]
        original_supports.append(first)
        actual_components = [c for c in components(n, edges, first) if len(c) > 1]
        assert actual_components == [sorted(c) for c in record["support_components"]]
        assert components(n, edges, set(range(45))-set(first)) == [sorted(c) for c in record["complement_components"]]
        witnesses = [k for k, bad in enumerate(blocked_sets) if normal in bad]
        assert witnesses == record["obstruction_blocks"] and witnesses
        block = g["blocks"][witnesses[0]]
        projected = []
        for e, path in enumerate(block["edge_representatives"]):
            assert len({i in first for i in path}) == 1
            if path[0] in first:
                projected.append(e)
        assert projected == record["local_factor_edges"]
        assert sum(1 << e for e in projected) in factors
    assert len({tuple(s) for s in original_supports}) == 7
    assert defects(n, edges, flow) == g["defects"]
    cover_ok(n, edges, g["glued_cover"])
    for k, block in enumerate(g["blocks"]):
        projected = [[] for _ in range(5)]
        perm = g["gluing_layer_permutations"][k]
        assert sorted(perm) == list(range(5))
        for i, layer in enumerate(g["glued_cover"]):
            for e, path in enumerate(block["edge_representatives"]):
                assert len({j in layer for j in path}) == 1
                if path[0] in layer:
                    projected[i].append(e)
        cover_ok(10, pe, projected)
        assert all(projected[perm[i]] == p["cover"][i] for i in range(5))

    escape = g["one_move_escape"]
    circuit = escape["circuit_edges"]
    local_circuit = tuple(escape["local_circuit_edges"])
    assert local_circuit in cs
    block = g["blocks"][escape["block"]]
    assert all(len(block["edge_representatives"][e]) == 1 for e in local_circuit)
    assert circuit == [block["edge_representatives"][e][0] for e in local_circuit]
    degree = Counter(v for e in circuit for v in edges[e])
    assert set(degree.values()) == {2}
    assert len([c for c in components(n, edges, circuit) if len(c) > 1]) == 1
    added = escape["added_value"]
    assert 0 < added < 8 and added not in {flow[e] for e in circuit}
    repaired = [a ^ added if e in circuit else a for e, a in enumerate(flow)]
    assert repaired == escape["flow"]
    valid_flow(n, edges, repaired)
    assert defects(n, edges, repaired) == escape["defects"]
    assert min(escape["defects"]) == 0
    transformed = escape["transformed_flow"]
    valid_flow(n, edges, transformed)
    value_map = {a: b for a, b in zip(repaired, transformed)}
    value_map[0] = 0
    assert len(value_map) == 8 and len(set(value_map.values())) == 8
    assert all(value_map[a] == b for a, b in zip(repaired, transformed))
    assert all(value_map[a ^ b] == value_map[a] ^ value_map[b] for a in range(8) for b in range(8))
    first = [e for e, a in enumerate(repaired) if (a & escape["normal"]).bit_count() % 2]
    assert first == [e for e, a in enumerate(transformed) if a & 4]
    assert first == escape["cover"][4] and first not in original_supports
    cover_ok(n, edges, escape["cover"])
    print("Independent verification passed: all six Petersen factors, 28,560 labeled flows,")
    print("all seven globally impossible layers, both five-layer covers, and the one-move escape.")


if __name__ == "__main__":
    main()
