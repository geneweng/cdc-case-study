#!/usr/bin/env python3
"""Solver-free independent verification of the junction obstruction.

Imports no constructor or previous verifier. Negative certificates use the
Petersen factor lemma and charge identity, not a solver's UNSAT status.
"""
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
PAIRS = [sum(1 << i for i in p) for p in itertools.combinations(range(5), 2)]
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]
PORTS = [4, 5, 2, 6]


def components(n, edges, chosen):
    adjacency = [set() for _ in range(n)]
    for e in chosen:
        u, v = edges[e]
        adjacency[u].add(v)
        adjacency[v].add(u)
    remaining = set(range(n))
    answer = []
    while remaining:
        todo = [min(remaining)]
        seen = set(todo)
        while todo:
            for v in adjacency[todo.pop()] - seen:
                seen.add(v)
                todo.append(v)
        remaining -= seen
        answer.append(sorted(seen))
    return answer


def girth(n, edges):
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    shortest = n+1
    for root in range(n):
        dist, parent = {root: 0}, {root: None}
        queue = deque([root])
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                if v not in dist:
                    dist[v], parent[v] = dist[u]+1, u
                    queue.append(v)
                elif parent[u] != v:
                    shortest = min(shortest, dist[u]+dist[v]+1)
    return shortest


def valid_flow(n, edges, values):
    assert len(values) == len(edges) and set(values) <= set(range(1, 8))
    totals, degrees = [0]*n, [0]*n
    for (u, v), value in zip(edges, values):
        for end in (u, v):
            totals[end] ^= value
            degrees[end] += 1
    assert totals == [0]*n and degrees == [3]*n


def valid_cover(n, edges, word):
    assert len(word) == len(edges) and set(word) <= set("0123456789")
    values = [PAIRS[int(c)] for c in word]
    for v in range(n):
        incident = [a for edge, a in zip(edges, values) if v in edge]
        assert len(incident) == 3
        for label in range(5):
            assert sum(a >> label & 1 for a in incident) in (0, 2)
    return values


def project(flow, normal):
    return sum(1 << e for e, value in enumerate(flow) if (value & normal).bit_count() % 2)


def verify_factors(data):
    edges = ([(i, (i+1) % 5) for i in range(5)]+[(i, i+5) for i in range(5)]
             + [(i+5, (i+2) % 5+5) for i in range(5)])
    assert data["edges"] == [list(e) for e in edges] and girth(10, edges) == 5
    local_sources = [2, 3, 7, 8, 9, 10, 11, 12, 13, 14, 4, 5, 1, 6]
    assert data["local_edge_sources"] == local_sources
    assert [edges[e] for e in local_sources[:10]] == INTERNAL
    for i, e in enumerate(local_sources[10:]):
        assert PORTS[i] in edges[e] and (0 if i < 2 else 1) in edges[e]
    records, types = [], {}
    for selected in itertools.combinations(range(15), 10):
        degree = [0]*10
        for e in selected:
            for v in edges[e]:
                degree[v] += 1
        if degree != [2]*10:
            continue
        cc = components(10, edges, selected)
        assert sorted(map(len, cc)) == [5, 5]
        complement = set(range(15))-set(selected)
        assert all((edges[e][0] in cc[0]) != (edges[e][1] in cc[0]) for e in complement)
        # Alternating circuits cross between the pentagons at every matching
        # edge, so their length is divisible by four. Girth 5 and order 10
        # force length 8, which cannot sum to the 20 residual occurrences.
        assert [k for k in range(5, 11) if k % 4 == 0] == [8]
        assert (2*15-len(selected)) % 8 != 0
        mask = sum(1 << e for e in selected)
        local = sum(1 << i for i, e in enumerate(local_sources) if e in selected)
        central = 0 in selected
        port_bits = [(local >> (10+i)) & 1 for i in range(4)]
        if central:
            assert sum(port_bits[:2]) == sum(port_bits[2:]) == 1
        else:
            assert port_bits == [1, 1, 1, 1]
        name = "weight_four" if central else "zero"
        records.append({"factor_mask": mask, "local_mask": local,
                        "removed_edge_in_factor": central, "charge_type": name})
        types[local] = name
    assert len(records) == 6
    assert sorted(records, key=lambda r: r["factor_mask"]) == data["factor_restrictions"]
    assert {f for f, t in types.items() if t == "zero"} == {15609, 16270}
    assert {f for f, t in types.items() if t == "weight_four"} == {6115, 6782, 10045, 10711}
    return types


def verify_junctions(records):
    triangles = [(x, y, x ^ y) for x in PAIRS for y in PAIRS if x ^ y in PAIRS]
    assert len(triangles) == 60
    for rec, construction in zip(records, ("blowup", "semi")):
        assert rec["construction"] == construction
        assignments = set()
        if construction == "blowup":
            for x, y, r in triangles:
                for a in PAIRS:
                    c = a ^ x
                    if c not in PAIRS:
                        continue
                    for b in PAIRS:
                        d = b ^ y
                        if d in PAIRS:
                            assignments.add((a, b, c, d, x, y, r))
            possible_masks = {f for f in range(128)
                              if all(sum(f >> e & 1 for e in star) % 2 == 0
                                     for star in ((0, 2, 4), (1, 3, 5), (4, 5, 6)))}
            assert len(assignments) == 2160 and len(possible_masks) == 16
        else:
            for a, c, r in triangles:
                for b in PAIRS:
                    assignments.add((a, b, c, b, r))
            possible_masks = {f for f in range(32) if (f >> 1 & 1) == (f >> 3 & 1)
                              and sum(f >> e & 1 for e in (0, 2, 4)) % 2 == 0}
            assert len(assignments) == 600 and len(possible_masks) == 8
        histogram = Counter()
        words = []
        for values in assignments:
            assert values[0] ^ values[1] ^ values[2] ^ values[3] == values[-1]
            histogram[sum(1 << e for e, v in enumerate(values) if v & 1)] += 1
            words.append("".join(str(PAIRS.index(v)) for v in values))
        assert set(histogram) == possible_masks and len(assignments) == rec["assignments"]
        assert [[f, count] for f, count in sorted(histogram.items())] == rec["conditional_support_histogram"]
        encoded = "\n".join(sorted(words))+"\n"
        assert hashlib.sha256(encoded.encode()).hexdigest() == rec["sorted_word_sha256"]
    assert len(records) == 2


def blocked(left, right):
    return (left, right) in {("zero", "zero"), ("zero", "weight_four"), ("weight_four", "zero")}


def verify_example(rec, seed, types):
    m, k = rec["repetitions"], rec["cycle_length"]
    assert m in (1, 2, 3) and k == 6*m and rec["vertices"] == 12*k
    base = [[off+i, off+(i+1) % k] for off in (0, k) for i in range(k)]
    base += [[i, k+i] for i in range(k)]
    assert base == rec["base_edges"]
    valid_cover(2*k, base, rec["base_cover_word"])
    expected = base[k:]
    for i in range(k):
        expected.extend([[2*k+8*i+a-2, 2*k+8*i+b-2] for a, b in INTERNAL])
    for i in range(k):
        off = 2*k+8*i-2
        u, w = 10*k+2*i, 10*k+2*i+1
        nu, nw = 10*k+2*((i+1) % k), 10*k+2*((i+1) % k)+1
        expected.extend([[i, u], [i, w], [u, off+2], [w, off+6], [off+4, nu], [off+5, nw]])
    n, edges, flow = rec["vertices"], rec["edges"], rec["flow"]
    assert edges == expected and len(edges) == 18*k
    assert all(u != v and 0 <= u < n and 0 <= v < n for u, v in edges)
    assert len({tuple(sorted(e)) for e in edges}) == len(edges)
    assert len(components(n, edges, range(len(edges)))) == 1
    valid_flow(n, edges, flow)
    valid_cover(n, edges, rec["cover_word"])
    locals_ = []
    for i, block in enumerate(rec["blocks"]):
        assert block["vertices"] == list(range(2*k+8*i, 2*k+8*i+8))
        representatives = list(range(2*k+10*i, 2*k+10*i+10))
        representatives += [12*k+6*i+j for j in (4, 5, 2, 3)]
        assert block["edge_representatives"] == representatives
        local = [flow[e] for e in representatives]
        assert local == seed[i % 6]
        locals_.append(local)
    assert len(locals_) == k
    charges = [f[10] ^ f[11] for f in locals_]
    assert charges == rec["block_flow_charges"] == [3, 5, 3, 7, 5, 6]*m
    assert flow[:k] == charges and flow[k:2*k] == [charges[i-1] ^ charges[i] for i in range(k)]
    supports = []
    for normal, row in enumerate(rec["normals"], 1):
        first = project(flow, normal)
        assert row["normal"] == normal and row["support_mask"] == first
        assert row["edges_in_support"] == first.bit_count() < n
        assert first.bit_count() == [57, 63, 60, 60, 63, 67, 62][normal-1]*m
        cc = [c for c in components(n, edges, [e for e in range(len(edges)) if first >> e & 1]) if len(c) > 1]
        assert cc == row["circuit_components"] and len(cc) >= 2
        local_masks = [project(f, normal) for f in locals_]
        assert local_masks == row["local_masks"]
        witnesses = [{"junction": i, "left_block": (i-1) % k, "right_block": i,
                      "left_mask": local_masks[i-1], "right_mask": local_masks[i],
                      "left_type": types.get(local_masks[i-1]), "right_type": types.get(local_masks[i])}
                     for i in range(k) if blocked(types.get(local_masks[i-1]), types.get(local_masks[i]))]
        assert witnesses == row["obstruction_junctions"] and witnesses
        supports.append(first)
    assert len(supports) == len(set(supports)) == 7


def audit_cuts(rec, audit):
    n, edges = rec["vertices"], rec["edges"]
    adjacency = [0]*n
    for u, v in edges:
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
    examined, stars = 0, 0
    full = (1 << n)-1
    for size in (1, 2, 3):
        for removed in itertools.combinations(edges, size):
            examined += 1
            current = adjacency.copy()
            for u, v in removed:
                current[u] ^= 1 << v
                current[v] ^= 1 << u
            reached = pending = 1
            while pending:
                bit = pending & -pending
                pending ^= bit
                new = current[bit.bit_length()-1] & ~reached
                reached |= new
                pending |= new
            if reached != full:
                assert size == 3 and reached.bit_count() in (1, n-1)
                isolated = reached if reached.bit_count() == 1 else full ^ reached
                v = isolated.bit_length()-1
                assert all(v in edge for edge in removed)
                stars += 1
    assert examined == 210042 and stars == 72
    for block in rec["blocks"]:
        inside = set(block["vertices"])
        cut = [e for e, (u, v) in enumerate(edges) if (u in inside) != (v in inside)]
        assert len(cut) == 4
        cc = components(n, edges, set(range(len(edges)))-set(cut))
        assert sorted(map(len, cc)) == [8, 64]
        assert all(sum(u in c and v in c for u, v in edges) >= len(c) for c in cc)
    assert girth(n, edges) == 5
    assert audit == {"edge_deletion_sets": examined, "one_edge_cuts": 0, "two_edge_cuts": 0,
                     "three_edge_cuts": stars, "all_three_cuts_isolate_one_vertex": True,
                     "cyclic_edge_connectivity": 4, "girth": 5}


def verify_old(rec, types):
    source = HERE / rec["source"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == rec["source_sha256"]
    old = json.loads(source.read_text())
    edges, flow = old["edges"], old["witness_flow"]
    expected = [[i, 3] for i in range(3)]
    for i in range(3):
        expected.extend([[4+8*i+a-2, 4+8*i+b-2] for a, b in INTERNAL])
    for i in range(3):
        off = 4+8*i-2
        u, w = 28+2*i, 29+2*i
        nu, nw = 28+2*((i+1) % 3), 29+2*((i+1) % 3)
        expected.extend([[i, u], [i, w], [u, off+2], [w, off+6], [off+4, nu], [off+5, nw]])
    assert old["vertices"] == 34 and edges == expected
    valid_flow(34, edges, flow)
    reps = [list(range(3+10*i, 13+10*i))+[37+6*i, 38+6*i, 35+6*i, 36+6*i] for i in range(3)]
    assert rec["block_edge_representatives"] == reps
    assert len(rec["stronger_obstructions"]) == 3
    for normal, row in enumerate(rec["stronger_obstructions"], 1):
        local = [project([flow[e] for e in es], normal) for es in reps]
        assert row["normal"] == normal and row["local_masks"] == local
        i = row["junction"]
        assert i in range(3) and blocked(types.get(local[i-1]), types.get(local[i]))


def main():
    data = json.loads((HERE / "junction_selection_obstruction.json").read_text())
    assert data["pair_masks"] == PAIRS and data["internal_edges"] == [list(e) for e in INTERNAL]
    assert data["port_vertices"] == PORTS
    types = verify_factors(data["petersen"])
    verify_junctions(data["junction_relations"])
    print("Verified the six Petersen factor restrictions and both exact junction relations.", flush=True)
    seed = [list(map(int, word)) for word in data["local_flow_words"]]
    assert len(seed) == 6 and all(len(f) == 14 for f in seed)
    examples = data["examples"]
    assert [g["repetitions"] for g in examples] == [1, 2, 3]
    for graph in examples:
        verify_example(graph, seed, types)
    print("Verified flows, covers, and seven local obstructions on 72, 144, and 216 vertices.", flush=True)
    g = examples[0]
    audit_cuts(g, data["primary_graph_audit"])
    print("Checked all 210,042 deletions of at most three edges: only 72 vertex stars disconnect.", flush=True)
    print("A cyclic four-edge cut and girth five are verified directly.", flush=True)
    escape = data["one_switch_escape"]
    chosen = escape["circuit_edges"]
    assert escape["block"] == 0 and escape["local_circuit_edges"] == [0, 1, 2, 4, 7]
    assert chosen == [g["blocks"][0]["edge_representatives"][e] for e in escape["local_circuit_edges"]]
    degree = Counter(v for e in chosen for v in g["edges"][e])
    assert len(chosen) == len(set(chosen)) == len(degree) == 5 and set(degree.values()) == {2}
    assert len([c for c in components(72, g["edges"], chosen) if len(c) > 1]) == 1
    assert escape["added_value"] == escape["normal"] == 4
    changed = [value ^ (4 if e in chosen else 0) for e, value in enumerate(g["flow"])]
    assert changed == escape["flow"] and 0 not in changed
    valid_flow(72, g["edges"], changed)
    cover_values = valid_cover(72, g["edges"], escape["cover_word"])
    first = sum(1 << e for e, value in enumerate(cover_values) if value & 1)
    assert first == project(changed, 4) and first.bit_count() == 59
    verify_old(data["previous_34_vertex_example"], types)
    print("Verified the five-edge switch and its 59-edge prescribed layer in an explicit five-layer cover.")
    print("The same structural obstruction verifies all three earlier failed supports on the 34-vertex graph.")


if __name__ == "__main__":
    main()
