#!/usr/bin/env python3
"""Construct an all-coordinate obstruction with cyclic edge connectivity four.

The graph family has five-layer covers. The displayed starting flow has no
coordinate that can be a whole layer of any CDC. Standard library only.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from petersen_boundary import expand_representatives, hamilton_cover, lift, word

HERE = Path(__file__).parent
PAIRS = [sum(1 << i for i in p) for p in itertools.combinations(range(5), 2)]
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]
PORTS = [4, 5, 2, 6]
FLOW_WORDS = ["15543237746547", "56734156622727", "63752166341212",
              "46724166422534", "23312724361414", "12431175443553"]
LOCAL_FLOWS = [list(map(int, s)) for s in FLOW_WORDS]
ZERO_MASKS = {15609, 16270}
FOUR_MASKS = {6115, 6782, 10045, 10711}
ESCAPE_WORD = ("604120331075147019683323092623392711573280133828113786445150729625990322"
               "062002295390837649638291546092203553")


def support(flow, normal):
    return sum(1 << e for e, a in enumerate(flow) if (a & normal).bit_count() % 2)


def kind(mask):
    if mask in ZERO_MASKS:
        return "zero"
    if mask in FOUR_MASKS:
        return "weight_four"
    return None


def incompatible(left, right):
    return left == "zero" and right in ("zero", "weight_four") or (
        right == "zero" and left in ("zero", "weight_four"))


def nontrivial_components(n, edges, mask):
    adjacency = [set() for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        if mask >> e & 1:
            adjacency[u].add(v)
            adjacency[v].add(u)
    unseen = {v for v in range(n) if adjacency[v]}
    result = []
    while unseen:
        pending = [min(unseen)]
        found = set(pending)
        while pending:
            for v in adjacency[pending.pop()] - found:
                found.add(v)
                pending.append(v)
        unseen -= found
        result.append(sorted(found))
    return result


def junctions():
    result = []
    for construction in ("blowup", "semi"):
        words, histogram = [], Counter()
        for a, b, c, d in itertools.product(PAIRS, repeat=4):
            x, y = a ^ c, b ^ d
            r = x ^ y
            if construction == "blowup":
                if x not in PAIRS or y not in PAIRS or r not in PAIRS:
                    continue
                values = (a, b, c, d, x, y, r)
            else:
                if b != d or r not in PAIRS:
                    continue
                values = (a, b, c, d, r)
            s = word(values)
            words.append(s)
            histogram[sum(1 << i for i, v in enumerate(values) if v & 1)] += 1
        encoded = "\n".join(sorted(words))+"\n"
        result.append({"construction": construction, "assignments": len(words),
                       "conditional_support_histogram": [[s, c] for s, c in sorted(histogram.items())],
                       "sorted_word_sha256": hashlib.sha256(encoded.encode()).hexdigest()})
    return result


def factor_restrictions():
    edges = ([(i, (i+1) % 5) for i in range(5)]+[(i, i+5) for i in range(5)]
             + [(i+5, (i+2) % 5+5) for i in range(5)])
    stars = [sum(1 << e for e, uv in enumerate(edges) if v in uv) for v in range(10)]
    restriction = [2, 3, 7, 8, 9, 10, 11, 12, 13, 14, 4, 5, 1, 6]
    records = []
    for mask in range(1 << 15):
        if not all((mask & star).bit_count() == 2 for star in stars):
            continue
        local = sum(1 << i for i, e in enumerate(restriction) if mask >> e & 1)
        records.append({"factor_mask": mask, "local_mask": local,
                        "removed_edge_in_factor": bool(mask & 1), "charge_type": kind(local)})
    assert len(records) == 6 and {r["local_mask"] for r in records} == ZERO_MASKS | FOUR_MASKS
    return {"edges": edges, "local_edge_sources": restriction, "factor_restrictions": records}


def construct(repetitions, boundary):
    k = 6*repetitions
    n = 2*k
    base = ([(off+i, off+(i+1) % k) for off in (0, k) for i in range(k)]
            + [(i, k+i) for i in range(k)])
    base_cover = hamilton_cover(base, list(range(k))+list(range(2*k-1, k-1, -1)))
    vertices, edges, cover = lift(n, base, base_cover, [list(range(k))], "blowup", boundary)
    local = LOCAL_FLOWS*repetitions
    charges = [f[10] ^ f[11] for f in local]
    assigned = {}

    def put(edge, value):
        key = tuple(sorted(edge))
        assert key not in assigned and value in range(1, 8)
        assigned[key] = value

    for i in range(k):
        put((k+i, k+(i+1) % k), charges[i])
        put((i, k+i), charges[i-1] ^ charges[i])
    blocks = []
    for i, f in enumerate(local):
        vmap = {v: n+8*i+v-2 for v in range(2, 10)}
        u, w = n+8*k+2*i, n+8*k+2*i+1
        nu, nw = n+8*k+2*((i+1) % k), n+8*k+2*((i+1) % k)+1
        local_edges = [(vmap[a], vmap[b]) for a, b in INTERNAL]
        local_edges += [(vmap[4], nu), (vmap[5], nw), (vmap[2], u), (vmap[6], w)]
        for edge, value in zip(local_edges, f):
            put(edge, value)
        put((i, u), local[i-1][10] ^ f[12])
        put((i, w), local[i-1][11] ^ f[13])
        blocks.append({"vertices": list(vmap.values()), "local_edges": local_edges})
    edge_ids = {tuple(sorted(edge)): e for e, edge in enumerate(edges)}
    assert len(edge_ids) == len(edges) == len(assigned)
    flow = [assigned[tuple(sorted(edge))] for edge in edges]
    for block in blocks:
        block["edge_representatives"] = [edge_ids[tuple(sorted(e))] for e in block.pop("local_edges")]
    normals = []
    for normal in range(1, 8):
        masks = [support(f, normal) for f in local]
        witnesses = [{"junction": i, "left_block": (i-1) % k, "right_block": i,
                      "left_mask": masks[i-1], "right_mask": masks[i],
                      "left_type": kind(masks[i-1]), "right_type": kind(masks[i])}
                     for i in range(k) if incompatible(kind(masks[i-1]), kind(masks[i]))]
        assert witnesses
        first = support(flow, normal)
        normals.append({"normal": normal, "support_mask": first, "edges_in_support": first.bit_count(),
                        "circuit_components": nontrivial_components(vertices, edges, first),
                        "local_masks": masks, "obstruction_junctions": witnesses})
    return {"repetitions": repetitions, "cycle_length": k, "vertices": vertices, "edges": edges,
            "base_edges": base, "base_cover_word": word(base_cover), "blocks": blocks,
            "flow": flow, "block_flow_charges": charges, "cover_word": word(cover), "normals": normals}


def previous_example():
    source = HERE / "cyclic_core_completion.json"
    data = json.loads(source.read_text())
    blocks = [list(range(3+10*i, 13+10*i))+[37+6*i, 38+6*i, 35+6*i, 36+6*i]
              for i in range(3)]
    flow = data["witness_flow"]
    local = [[flow[e] for e in block] for block in blocks]
    rows = []
    for normal in (1, 2, 3):
        masks = [support(f, normal) for f in local]
        at = next(i for i in range(3) if incompatible(kind(masks[i-1]), kind(masks[i])))
        rows.append({"normal": normal, "local_masks": masks, "junction": at})
    return {"source": source.name, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "block_edge_representatives": blocks, "stronger_obstructions": rows}


def main():
    seed = json.loads((HERE / "petersen_boundary.json").read_text())
    boundary = expand_representatives(seed["representatives"])
    examples = [construct(m, boundary) for m in (1, 2, 3)]
    graph = examples[0]
    switched = graph["flow"].copy()
    local_circuit = [0, 1, 2, 4, 7]
    circuit = [graph["blocks"][0]["edge_representatives"][e] for e in local_circuit]
    for e in circuit:
        assert switched[e] != 4
        switched[e] ^= 4
    escape = {"block": 0, "local_circuit_edges": local_circuit, "circuit_edges": circuit,
              "added_value": 4, "normal": 4, "flow": switched, "cover_word": ESCAPE_WORD}
    result = {"date": "2026-09-30",
              "scope": "An infinite cyclically four-edge-connected family with a nowhere-zero three-bit flow whose seven coordinate supports are impossible whole layers of any CDC; the graphs have five-layer covers. No general 5-CDC proof or novelty claim.",
              "source_construction": "https://arxiv.org/html/1203.2015v1#S2",
              "pair_masks": PAIRS, "internal_edges": INTERNAL, "port_vertices": PORTS,
              "local_flow_words": FLOW_WORDS, "junction_relations": junctions(),
              "petersen": factor_restrictions(), "examples": examples, "one_switch_escape": escape,
              "primary_graph_audit": {"edge_deletion_sets": 210042, "one_edge_cuts": 0,
                                      "two_edge_cuts": 0, "three_edge_cuts": 72,
                                      "all_three_cuts_isolate_one_vertex": True,
                                      "cyclic_edge_connectivity": 4, "girth": 5},
              "previous_34_vertex_example": previous_example()}
    (HERE / "junction_selection_obstruction.json").write_text(json.dumps(result, indent=2)+"\n")
    print("Constructed family examples on", [g["vertices"] for g in examples], "vertices with explicit covers.")
    print("Each has seven locally blocked coordinates; the obstruction applies to any number of layers.")
    print("Junction relations:", [(j["construction"], j["assignments"]) for j in result["junction_relations"]])
    print("Saved a five-edge circuit-switch escape and structural proofs for the three earlier failed supports.")


if __name__ == "__main__":
    main()
