#!/usr/bin/env python3
"""Exact Petersen four-pole relations and constructive blowup inheritance.

Standard library only. This proves a closure result, not the 5-CDC conjecture.
See petersen-boundary.md for the local proof and precise hypotheses.
"""
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
PAIRS = [sum(1 << i for i in p) for p in itertools.combinations(range(5), 2)]
PETERSEN = ([(i, (i+1) % 5) for i in range(5)] + [(i, i+5) for i in range(5)]
            + [(i+5, (i+2) % 5+5) for i in range(5)])
# Semiedges, last four in order a1,a2,b1,b2; None denotes the open end.
EDGES = [(u, v) for u, v in PETERSEN if min(u, v) >= 2]
EDGES += [(4, None), (5, None), (2, None), (6, None)]
INC = [[e for e, ends in enumerate(EDGES) if v in ends] for v in range(2, 10)]
TRIPLES = [(a, b, a ^ b) for a in PAIRS for b in PAIRS if a ^ b in PAIRS]


def word(values):
    return "".join(str(PAIRS.index(a)) for a in values)


def enumerate_covers():
    """Exhaust assignments of label triangles at the eight internal vertices."""
    values = [0]*14

    def visit(left):
        if not left:
            yield tuple(values)
            return
        v = max(sorted(left), key=lambda v: sum(values[e] != 0 for e in INC[v]))
        es = INC[v]
        for triple in TRIPLES:
            if any(values[e] and values[e] != a for e, a in zip(es, triple)):
                continue
            fresh = [e for e in es if not values[e]]
            for e, a in zip(es, triple):
                values[e] = a
            yield from visit(left-{v})
            for e in fresh:
                values[e] = 0

    yield from visit(set(range(8)))


def label_maps():
    for pi in itertools.permutations(range(5)):
        yield [PAIRS.index(sum(1 << pi[i] for i in range(5) if a >> i & 1)) for a in PAIRS]


def expand_representatives(representatives):
    result = {}
    for rec in representatives:
        for pi in label_maps():
            transformed = "".join(str(pi[int(c)]) for c in rec["cover_word"])
            result.setdefault(tuple(int(c) for c in transformed[-4:]), transformed)
    return result


def valid_cover(n, edges, values):
    assert len(edges) == len(values)
    parity, degrees = [0]*n, [0]*n
    for (u, v), a in zip(edges, values):
        assert u != v and a in PAIRS
        for x in (u, v):
            parity[x] ^= a
            degrees[x] += 1
    assert degrees == [3]*n and parity == [0]*n


def lift(n, edges, values, cycles, kind, boundary):
    """Lift a given five-layer cover through Construction 1 or 2 of Hagglund."""
    valid_cover(n, edges, values)
    assert kind in ("semi", "blowup")
    lookup = {tuple(sorted(e)): i for i, e in enumerate(edges)}
    assert len(lookup) == len(edges)  # This implementation takes simple base graphs.
    vertices = [v for cycle in cycles for v in cycle]
    assert len(set(vertices)) == len(vertices)
    removed = set()
    for cycle in cycles:
        assert len(cycle) >= 3
        removed.update(lookup[tuple(sorted((v, cycle[(i+1) % len(cycle)])))]
                       for i, v in enumerate(cycle))
    result_edges = [e for i, e in enumerate(edges) if i not in removed]
    result_values = [a for i, a in enumerate(values) if i not in removed]
    next_vertex = n
    for cycle in cycles:
        k = len(cycle)
        blocks = []
        for _ in cycle:
            blocks.append({v: next_vertex+v-2 for v in range(2, 10)})
            next_vertex += 8
        aux = []
        if kind == "blowup":
            for _ in cycle:
                aux.append((next_vertex, next_vertex+1))
                next_vertex += 2
        ports = [[None]*4 for _ in cycle]
        spokes = []
        for i, v in enumerate(cycle):
            s = values[lookup[tuple(sorted((cycle[i-1], v)))]]
            t = values[lookup[tuple(sorted((v, cycle[(i+1) % k])))]]
            common = s & t
            assert common.bit_count() == 1 and (s ^ t) in PAIRS
            a = common.bit_length()-1
            b = (s ^ common).bit_length()-1
            c = (t ^ common).bit_length()-1
            d = min(set(range(5))-{a, b, c})
            pair = lambda x, y: (1 << x) | (1 << y)
            if kind == "semi":
                ports[i-1][:2] = [pair(b, d), pair(a, d)]
                ports[i][2:] = [pair(c, d), pair(a, d)]
            else:
                ports[i-1][:2] = [pair(a, d), pair(b, d)]
                ports[i][2:] = [pair(a, b), pair(c, b)]
            spokes.append((pair(b, d), pair(c, d)))
        for i, block in enumerate(blocks):
            key = tuple(PAIRS.index(p) for p in ports[i])
            extension = [PAIRS[int(c)] for c in boundary[key]]
            assert extension[-4:] == ports[i]
            result_edges.extend((block[u], block[v]) for u, v in EDGES[:10])
            result_values.extend(extension[:10])
        for i, v in enumerate(cycle):
            j = (i+1) % k
            a1, a2, b1, b2 = ports[i]
            block = blocks[i]
            if kind == "semi":
                assert a2 == ports[j][3]
                result_edges.extend([(v, block[2]), (block[5], blocks[j][6]),
                                     (block[4], cycle[j])])
                result_values.extend([b1, a2, a1])
            else:
                u, w = aux[i]
                nu, nw = aux[j]
                result_edges.extend([(v, u), (v, w), (u, block[2]), (w, block[6]),
                                     (block[4], nu), (block[5], nw)])
                result_values.extend([*spokes[i], b1, b2, a1, a2])
    valid_cover(next_vertex, result_edges, result_values)
    return next_vertex, result_edges, result_values


def hamilton_cover(edges, circuit):
    colors = {tuple(sorted((v, circuit[(i+1) % len(circuit)]))): i % 2
              for i, v in enumerate(circuit)}
    return [PAIRS[[0, 1, 4][colors.get(tuple(sorted(e)), 2)]] for e in edges]


def examples(boundary):
    records = []

    def add(name, n, edges, values, cycles, kind):
        nn, ee, vv = lift(n, edges, values, cycles, kind, boundary)
        records.append({"name": name, "kind": kind, "base_vertices": n,
                        "base_edges": edges, "base_cover_word": word(values), "cycles": cycles,
                        "vertices": nn, "edges": ee, "cover_word": word(vv)})
        return nn, ee, vv

    edges = list(itertools.combinations(range(4), 2))
    values = hamilton_cover(edges, list(range(4)))
    for kind in ("semi", "blowup"):
        lifted = add("K4 triangle", 4, edges, values, [[0, 1, 2]], kind)
        if kind == "blowup":
            first_blowup = lifted
    for k in (3, 4, 5, 7):
        edges = ([(off+i, off+(i+1) % k) for off in (0, k) for i in range(k)]
                 + [(i, i+k) for i in range(k)])
        values = hamilton_cover(edges, list(range(k))+list(range(2*k-1, k-1, -1)))
        for kind in ("semi", "blowup"):
            add(f"prism {k}, one ring", 2*k, edges, values, [list(range(k))], kind)
            if k == 3:
                add("prism 3, both rings", 2*k, edges, values,
                    [list(range(k)), list(range(k, 2*k))], kind)
    prior = json.loads((HERE / "layer_selection_obstruction.json").read_text())["petersen"]
    values = [sum(1 << j for j, layer in enumerate(prior["cover"]) if e in layer)
              for e in range(15)]
    for kind in ("semi", "blowup"):
        add("Petersen, spanning two-factor", 10, PETERSEN, values,
            [[0, 1, 2, 3, 4], [5, 7, 9, 6, 8]], kind)
        # Internal 5-circuit in the first inserted B of Blowup(K4,C3).
        add("iterated K4 blowup", *first_blowup, [[4, 5, 6, 11, 9]], kind)
    return records


def main():
    relation, boundaries = {}, {}
    total = 0
    for values in enumerate_covers():
        total += 1
        first = sum(1 << e for e, a in enumerate(values) if a & 1)
        ports = tuple(PAIRS.index(a) for a in values[-4:])
        w = word(values)
        relation.setdefault((first, ports), w)
        boundaries[ports] = min(w, boundaries.get(ports, w))
    maps = list(label_maps())
    representatives = [{"boundary": list(b), "cover_word": w}
                       for b, w in sorted(boundaries.items())
                       if b == min(tuple(pi[i] for i in b) for pi in maps)]
    assert len(representatives) == 10 and len(boundaries) == 640
    expanded = expand_representatives(representatives)
    assert set(expanded) == set(boundaries)
    path = HERE / "petersen_boundary_relation.txt.gz"
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as stream:
            for (first, ports), w in sorted(relation.items()):
                stream.write(f"{first} {''.join(map(str, ports))} {w}\n".encode("ascii"))
    counts = Counter(first for first, _ in relation)
    result = {"date": "2026-09-29", "scope": "Exact boundary relation and conditional cover inheritance; no proof of the general 5-CDC conjecture and no novelty claim.",
              "vertices": list(range(2, 10)), "edges": EDGES, "port_order": ["a1", "a2", "b1", "b2"],
              "pair_masks": PAIRS, "representatives": representatives,
              "named_partial_covers": total, "boundary_states": len(boundaries),
              "boundary_matrix": {"dimension": 100, "charge_classes": 16,
                                  "class_sizes": [10]+[6]*15,
                                  "boolean_idempotent": True, "square_over_F2_is_zero": True},
              "fixed_layer_states": len(counts), "fixed_layer_relation_size": len(relation),
              "relation_file": path.name, "relation_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "fixed_layer_boundary_counts": [[f, c] for f, c in sorted(counts.items())],
              "examples": examples(expanded)}
    (HERE / "petersen_boundary.json").write_text(json.dumps(result, indent=2)+"\n")
    print("Partial covers:", total, "; boundary states:", len(boundaries),
          "; representatives:", len(representatives), "; prescribed-layer states:", len(relation))
    print("Constructed", len(result["examples"]), "covers by boundary substitution.")


if __name__ == "__main__":
    main()
