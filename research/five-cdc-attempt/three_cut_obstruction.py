#!/usr/bin/env python3
"""Three-edge-cut composition, a 26-vertex obstruction, and boundary states.

Disproves coordinate selection for arbitrary flows even on 3-edge-connected
cubic graphs. The graph has an explicit five-layer cover; see the report.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import networkx as nx
import explore as x
from first_coordinate_census import components
from layer_selection_obstruction import SEED, P_COVER, check_cover, support
from verify_lex_trap import valid_flow

HERE = Path(__file__).parent
MAPS = [list(range(8)), [0, 3, 1, 2, 4, 7, 5, 6], [0, 5, 2, 7, 1, 4, 3, 6]]


def boundary_states():
    pairs = list(itertools.combinations(range(5), 2))
    records = []
    for width in (2, 3, 4):
        valid = 0
        histogram = Counter()
        examples = {}
        for ports in itertools.product(pairs, repeat=width):
            counts = Counter(label for pair in ports for label in pair)
            if any(count % 2 for count in counts.values()):
                continue
            valid += 1
            if width == 2:
                assert ports[0] == ports[1]
            elif width == 3:
                assert len(counts) == 3 and set(counts.values()) == {2}
                assert len(set(ports)) == 3
            else:
                signature = tuple(sorted(len(set(ports[0]) ^ set(ports[i])) for i in (1, 2, 3)))
                histogram[signature] += 1
                examples.setdefault(signature, ports)
        records.append({"cut_size": width, "assignments_examined": 10**width,
                        "parity_valid_assignments": valid,
                        "four_port_classes": [{"cap_multiplicities": sig, "count": count,
                                                "example": examples[sig]}
                                               for sig, count in sorted(histogram.items())]})
    assert [r["parity_valid_assignments"] for r in records] == [10, 60, 640]
    return records


def census_audit():
    path = HERE / "first_coordinate_census.json"
    raw = path.read_bytes()
    source = json.loads(raw)
    graph_counts = Counter()
    failure_counts = Counter()
    nz = Counter()
    pairs_checked = total_bad = nonempty = 0
    violations = []
    for graph in source["graphs"]:
        graph_counts[graph["vertices"]] += 1
        nz.update(graph["nz_orbits_by_rank"])
        bad = {r["support_mask"] for r in graph["failed_admissible_first_coordinates"]}
        assert len(bad) == len(graph["failed_admissible_first_coordinates"])
        total_bad += len(bad)
        nonempty += bool(bad)
        failure_counts[len(bad)] += 1
        for a, b in itertools.combinations(sorted(bad), 2):
            pairs_checked += 1
            if a ^ b in bad:
                violations.append({"graph6": graph["graph6"], "supports": [a, b, a ^ b]})
    assert not violations and pairs_checked == 31068 and total_bad == 1449
    assert sum(nz.values()) == 97572378
    return {"source": path.name, "source_sha256": hashlib.sha256(raw).hexdigest(),
            "scope": "Audit of saved failed-support sets; the original flow enumeration is not rerun.",
            "graphs": len(source["graphs"]), "graph_orders": dict(sorted(graph_counts.items())),
            "nonempty_failure_sets": nonempty, "failed_admissible_supports": total_bad,
            "failure_set_size_histogram": dict(sorted(failure_counts.items())),
            "distinct_support_pairs_checked": pairs_checked,
            "sum_free_violations": violations, "saved_nz_flow_orbits_by_rank": dict(nz)}


def four_cut_examples():
    """Realize both boundary types with no valid two-vertex cap, on the cube."""
    edges = [(offset+i, offset+(i+1) % 4) for offset in (0, 4) for i in range(4)]
    edges += [(i, i+4) for i in range(4)]
    records = []
    for ports in ([3, 3, 3, 3], [3, 3, 12, 12]):
        last = (1 << 0) | (1 << 2)
        value = last
        internal = []
        for port in ports:
            value ^= port
            assert value.bit_count() == 2
            internal.append(value)
        assert value == last
        masks = internal+internal+ports
        cover = [[e for e, mask in enumerate(masks) if mask >> i & 1] for i in range(5)]
        check_cover(8, edges, cover)
        cap_counts = [(ports[0] ^ ports[i]).bit_count() for i in (1, 2, 3)]
        assert 2 not in cap_counts
        records.append({"vertices": 8, "edges": edges, "cut_edges": [8, 9, 10, 11],
                        "edge_label_masks": masks, "cover": cover,
                        "cap_multiplicities": cap_counts})
    return records


def construct():
    _, pe = x.petersen()
    inc = x.BASE.incidence(10, pe)
    blocks, edges, flow = [], [], []
    offset = 0
    for k, linear in enumerate(MAPS):
        removed = [0, 2] if k == 0 else [0]
        kept = [v for v in range(10) if v not in removed]
        vertex_map = [None]*10
        for j, v in enumerate(kept):
            vertex_map[v] = offset+j
        offset += len(kept)
        local = [linear[a] for a in SEED]
        valid_flow(10, pe, local)
        representatives = [None]*15
        for e, (u, v) in enumerate(pe):
            if u in removed or v in removed:
                continue
            representatives[e] = len(edges)
            edges.append((vertex_map[u], vertex_map[v]))
            flow.append(local[e])
        bad = [l for l in range(1, 8) if all(sum(x.dot(l, local[e]) for e in es) == 2 for es in inc)]
        blocks.append({"index": k, "vertex_map": vertex_map, "removed_vertices": removed,
                       "linear_map": linear, "local_flow": local,
                       "edge_representatives": representatives, "two_factor_normals": bad})
    cuts = []
    for child, root_vertex in ((1, 0), (2, 2)):
        ports = []
        for e in inc[root_vertex]:
            value = blocks[0]["local_flow"][e]
            other_e = next(j for j in inc[0] if blocks[child]["local_flow"][j] == value)
            u = next(v for v in pe[e] if v != root_vertex)
            v = next(v for v in pe[other_e] if v != 0)
            index = len(edges)
            edges.append((blocks[0]["vertex_map"][u], blocks[child]["vertex_map"][v]))
            flow.append(value)
            blocks[0]["edge_representatives"][e] = index
            blocks[child]["edge_representatives"][other_e] = index
            ports.append({"central_edge": e, "leaf_edge": other_e, "global_edge": index})
        cuts.append({"leaf_block": child, "central_vertex": root_vertex,
                     "leaf_vertex": 0, "ports": ports})
    assert offset == 26 and len(edges) == 39
    assert all(None not in b["edge_representatives"] for b in blocks)
    graph = nx.Graph(edges)
    assert len(graph) == 26 and graph.number_of_edges() == 39
    assert nx.is_connected(graph) and all(d == 3 for _, d in graph.degree())
    assert nx.edge_connectivity(graph) == 3
    valid_flow(26, edges, flow)
    assert [b["two_factor_normals"] for b in blocks] == [[1, 3, 7], [1, 2, 5], [3, 4, 6]]
    normals = []
    for normal in range(1, 8):
        first = support(flow, normal)
        mask = sum(1 << e for e in first)
        witnesses = [b["index"] for b in blocks if normal in b["two_factor_normals"]]
        assert witnesses
        normals.append({"normal": normal, "support_edges": first,
                        "support_components": components(26, edges, mask),
                        "complement_components": components(26, edges, mask, keep=False),
                        "obstruction_blocks": witnesses,
                        "local_factor_edges": support(blocks[witnesses[0]]["local_flow"], normal)})

    # Align the three boundary layer pairs of each leaf with the central cover.
    pairs = [{i for i, layer in enumerate(P_COVER) if e in layer} for e in range(15)]
    permutations = [list(range(5))]
    for cut in cuts:
        perm = next(perm for perm in itertools.permutations(range(5)) if all(
            {perm[i] for i in pairs[p["leaf_edge"]]} == pairs[p["central_edge"]]
            for p in cut["ports"]))
        permutations.append(list(perm))
    edge_pairs = [None]*39
    for block, perm in zip(blocks, permutations):
        for e, global_e in enumerate(block["edge_representatives"]):
            pair = sorted(perm[i] for i in pairs[e])
            assert edge_pairs[global_e] in (None, pair)
            edge_pairs[global_e] = pair
    cover = [[e for e, pair in enumerate(edge_pairs) if i in pair] for i in range(5)]
    check_cover(26, edges, cover)
    # The standard five-label projection gives another nowhere-zero 3-flow.
    labels = [4, 5, 6, 7, 0]
    good_flow = [labels[p[0]] ^ labels[p[1]] for p in edge_pairs]
    valid_flow(26, edges, good_flow)
    assert support(good_flow, 4) == cover[4]
    assert x.defect(26, edges, good_flow, 4) == 0
    assert all(layer not in [r["support_edges"] for r in normals] for layer in cover)
    return {"vertices": 26, "edges": edges, "flow": flow, "blocks": blocks,
            "three_edge_cuts": cuts, "edge_connectivity": 3, "normals": normals,
            "defects": x.defects_fast(26, edges, flow), "gluing_layer_permutations": permutations,
            "cover": cover, "cover_induced_flow": good_flow,
            "cover_induced_defects": x.defects_fast(26, edges, good_flow)}


def main():
    _, pe = x.petersen()
    result = {"date": "2026-09-29", "scope": "A 3-edge-connected counterexample to fixed-flow coordinate selection; the graph has a five-layer cover.",
              "petersen": {"edges": pe, "seed_flow": SEED, "cover": P_COVER},
              "example": construct(), "boundary_states": boundary_states(),
              "four_cut_cap_counterexamples": four_cut_examples(), "saved_census_audit": census_audit()}
    (HERE / "three_cut_obstruction.json").write_text(json.dumps(result, indent=2)+"\n")
    g = result["example"]
    print("26 vertices, 39 edges, edge connectivity 3; all seven coordinate layers obstructed.")
    print("Glued five-layer cover verified; induced-flow defects:", g["cover_induced_defects"])
    print("Parity-valid boundary assignments for cut sizes 2, 3, 4:", [r["parity_valid_assignments"] for r in result["boundary_states"]])
    print("Saved census: 4,469 sum-free failure sets; 31,068 support pairs checked.")


if __name__ == "__main__":
    main()
