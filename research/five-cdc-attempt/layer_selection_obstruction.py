#!/usr/bin/env python3
"""Construct a flow whose seven coordinate supports cannot be CDC layers.

Three Petersen blocks, joined by two edge sums, give a 30-vertex example.
The graph still has a five-layer cover, including after one circuit switch.
See layer-selection-obstruction.md for the proof, which excludes even covers
with arbitrarily many layers containing any of the original seven supports.
"""
from collections import Counter
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import networkx as nx
import explore as x
from exhaustive_repair import OrbitSearch, subspaces
from first_coordinate_census import components
from verify_lex_trap import circuits_dfs, valid_flow

HERE = Path(__file__).parent
SEED = [2, 7, 2, 7, 1, 3, 5, 5, 5, 6, 2, 4, 7, 1, 1]
MAPS = [list(range(8)), [0, 3, 2, 1, 4, 7, 6, 5],
        [0, 4, 7, 3, 2, 6, 5, 1]]
P_COVER = [[2, 4, 5, 7, 8, 9, 10, 11, 14], [1, 6, 7, 12, 14],
           [0, 5, 6, 11, 13], [3, 8, 9, 10, 12, 13], [0, 1, 2, 3, 4]]


def support(flow, normal):
    return [i for i, a in enumerate(flow) if x.dot(a, normal)]


def check_cover(n, edges, cover):
    assert len(cover) == 5
    assert all(len(layer) == len(set(layer)) for layer in cover)
    assert all(set(layer) <= set(range(len(edges))) for layer in cover)
    assert all(sum(e in layer for layer in cover) == 2 for e in range(len(edges)))
    for layer in cover:
        degrees = [0]*n
        for e in layer:
            for v in edges[e]:
                degrees[v] += 1
        assert all(d in (0, 2) for d in degrees)


def petersen_checks():
    n, edges = x.petersen()
    inc = x.BASE.incidence(n, edges)
    factors = [mask for mask in x.all_even_subgraphs(n, edges)
               if all(sum(mask >> i & 1 for i in es) == 2 for es in inc)]
    cs = circuits_dfs(n, edges)
    records = []
    for first in factors:
        alternating = [c for c in cs if all(
            sum(bool(first >> i & 1) for i in c if v in edges[i]) == 1
            for v in {v for i in c for v in edges[i]})]
        assert len(alternating) == 5 and all(len(c) == 8 for c in alternating)
        records.append({"factor_edges": [i for i in range(15) if first >> i & 1],
                        "alternating_circuits": alternating})
    search = OrbitSearch(n, edges)
    histogram = Counter()
    for rows in subspaces(search.r, 3):
        flow = search.flow(rows)
        if 0 not in flow:
            bad = sum(sum(1 << i for i in support(flow, normal)) in factors
                      for normal in range(1, 8))
            histogram[bad] += 1
    assert histogram == {0: 30, 1: 60, 2: 60, 3: 20}
    check_cover(n, edges, P_COVER)
    return {"vertices": n, "edges": edges, "seed_flow": SEED,
            "cover": P_COVER, "two_factors": records,
            "circuits": len(cs), "rank_three_nz_flow_orbits": sum(histogram.values()),
            "two_factor_coordinate_histogram": dict(sorted(histogram.items()))}


def construct():
    _, pe = x.petersen()
    edges, flow, blocks = [], [], []
    for k, mapping in enumerate(MAPS):
        assert len(set(mapping)) == 8
        assert all(mapping[a ^ b] == mapping[a] ^ mapping[b]
                   for a in range(8) for b in range(8))
        local = [mapping[a] for a in SEED]
        valid_flow(10, pe, local)
        removed = [0, 1] if k == 0 else [0]
        paths = [None]*15
        for e, (u, v) in enumerate(pe):
            if e in removed:
                continue
            paths[e] = [len(edges)]
            edges.append((10*k+u, 10*k+v))
            flow.append(local[e])
        blocks.append({"index": k, "vertices": list(range(10*k, 10*k+10)),
                       "linear_map": mapping, "local_flow": local,
                       "removed_edges": removed, "edge_representatives": paths})
    cuts = []
    for child, parent_edge in ((1, 0), (2, 1)):
        u, v = pe[parent_edge]
        a, b = pe[0]
        cut = [len(edges), len(edges)+1]
        value = blocks[0]["local_flow"][parent_edge]
        assert value == blocks[child]["local_flow"][0]
        edges.extend([(u, 10*child+a), (v, 10*child+b)])
        flow.extend([value, value])
        blocks[0]["edge_representatives"][parent_edge] = cut
        blocks[child]["edge_representatives"][0] = cut
        cuts.append({"leaf_block": child, "central_edge": parent_edge,
                     "leaf_edge": 0, "cut_edges": cut})
    g = nx.Graph(edges)
    assert len(edges) == g.number_of_edges() == 45 and len(g) == 30
    assert nx.is_connected(g) and not list(nx.bridges(g))
    assert all(d == 3 for _, d in g.degree())
    valid_flow(30, edges, flow)
    inc = x.BASE.incidence(10, pe)
    for block in blocks:
        block["two_factor_normals"] = [normal for normal in range(1, 8) if all(
            sum(x.dot(block["local_flow"][e], normal) for e in es) == 2 for es in inc)]
    assert [b["two_factor_normals"] for b in blocks] == [[1, 3, 7], [1, 2, 6], [4, 5, 7]]
    normals = []
    for normal in range(1, 8):
        selected = support(flow, normal)
        mask = sum(1 << e for e in selected)
        witnesses = [b["index"] for b in blocks if normal in b["two_factor_normals"]]
        assert witnesses
        normals.append({"normal": normal, "support_edges": selected,
                        "support_components": components(30, edges, mask),
                        "complement_components": components(30, edges, mask, keep=False),
                        "obstruction_blocks": witnesses,
                        "local_factor_edges": support(blocks[witnesses[0]]["local_flow"], normal)})
    assert len({tuple(r["support_edges"]) for r in normals}) == 7

    # Glue three independently known Petersen covers. Only layer names change.
    pairs = [[i for i, layer in enumerate(P_COVER) if e in layer] for e in range(15)]
    permutations = [list(range(5))]
    for cut in cuts:
        target = pairs[cut["central_edge"]]
        source = pairs[0]
        perm = dict(zip(source, target))
        perm.update(zip([i for i in range(5) if i not in source],
                        [i for i in range(5) if i not in target]))
        permutations.append([perm[i] for i in range(5)])
    global_pairs = [None]*len(edges)
    for block, perm in zip(blocks, permutations):
        for e, path in enumerate(block["edge_representatives"]):
            pair = sorted(perm[i] for i in pairs[e])
            for global_e in path:
                assert global_pairs[global_e] in (None, pair)
                global_pairs[global_e] = pair
    glued_cover = [[e for e, pair in enumerate(global_pairs) if i in pair] for i in range(5)]
    check_cover(30, edges, glued_cover)

    # A circuit switch inside the third block changes the flow subspace.
    local_circuit = [1, 2, 6, 8, 10, 12, 13, 14]
    assert tuple(local_circuit) in circuits_dfs(10, pe)
    circuit = [blocks[2]["edge_representatives"][e][0] for e in local_circuit]
    assert all(len(blocks[2]["edge_representatives"][e]) == 1 for e in local_circuit)
    added = 3
    assert added not in {flow[e] for e in circuit}
    repaired = flow[:]
    for e in circuit:
        repaired[e] ^= added
    valid_flow(30, edges, repaired)
    normal = 5
    transformed = x.transform(repaired, normal)
    lift = x.extra_coordinate_lift(30, edges, transformed)
    assert lift["cover"] is not None
    cover = [lift["cover"][str(i)] for i in range(5)]
    check_cover(30, edges, cover)
    assert cover[4] == support(repaired, normal)
    assert cover[4] not in [r["support_edges"] for r in normals]
    initial_defects = x.defects_fast(30, edges, flow)
    final_defects = x.defects_fast(30, edges, repaired)
    assert initial_defects == [4, 6, 6, 4, 2, 6, 6]
    assert final_defects == [4, 6, 6, 4, 0, 6, 6]
    return {"vertices": 30, "edges": edges, "flow": flow, "blocks": blocks,
            "two_edge_cuts": cuts, "normals": normals, "defects": initial_defects,
            "glued_cover": glued_cover, "gluing_layer_permutations": permutations,
            "one_move_escape": {"block": 2, "local_circuit_edges": local_circuit,
                                "circuit_edges": circuit, "added_value": added,
                                "flow": repaired, "defects": final_defects,
                                "normal": normal, "transformed_flow": transformed,
                                "cover": cover}}


def main():
    result = {"date": "2026-09-29",
              "scope": "A counterexample to coordinate selection for an arbitrary fixed flow; not to the 5-CDC conjecture.",
              "petersen": petersen_checks(), "example": construct()}
    (HERE / "layer_selection_obstruction.json").write_text(json.dumps(result, indent=2)+"\n")
    graph = result["example"]
    print("30 vertices, 45 edges; all seven supports have Petersen obstruction certificates.")
    print("Two five-layer covers verified; one circuit switch changes defects:",
          graph["defects"], "->", graph["one_move_escape"]["defects"])
    print("Petersen census:", result["petersen"]["two_factor_coordinate_histogram"])


if __name__ == "__main__":
    main()
