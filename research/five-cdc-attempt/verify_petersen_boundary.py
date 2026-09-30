#!/usr/bin/env python3
"""Independent, solver-free verification of petersen_boundary.json.

Does not import the constructor. Exhaustion chooses binary even layers,
whereas the constructor assigns label triangles at vertices.
"""
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
PAIR_SETS = list(itertools.combinations(range(5), 2))
MASKS = [sum(1 << i for i in p) for p in PAIR_SETS]
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]
PORT_VERTICES = [4, 5, 2, 6]
POLE_EDGES = INTERNAL+[(v, None) for v in PORT_VERTICES]


def decode(word):
    assert all(c in "0123456789" for c in word)
    return [MASKS[int(c)] for c in word]


def check_assignment(vertices, edges, word):
    values = decode(word)
    assert len(values) == len(edges)
    for v in vertices:
        incident = [values[e] for e, ends in enumerate(edges) if v in ends]
        assert len(incident) == 3
        for label in range(5):
            assert sum((a >> label) & 1 for a in incident) in (0, 2)
    return values


def binary_layers():
    incidence = [sum(1 << e for e, ends in enumerate(POLE_EDGES) if v in ends)
                 for v in range(2, 10)]
    return [s for s in range(1 << 14)
            if all((s & star).bit_count() % 2 == 0 for star in incidence)]


def enumerate_by_layers(evens, labels):
    """Select labels-2 even layers; exact multiplicity determines the last two."""
    full = (1 << 14)-1
    even_set = set(evens)

    def visit(rows, once, twice):
        if len(rows) == labels-2:
            zero = full ^ (once | twice)
            for a in evens:
                if a & twice or a & zero != zero:
                    continue
                b = a ^ once
                if b in even_set:
                    yield rows+[a, b]
            return
        for a in evens:
            if a & twice == 0:
                yield from visit(rows+[a], once ^ a, twice | (once & a))

    yield from visit([], 0, 0)


def projected_key(rows):
    values = [sum(1 << i for i, s in enumerate(rows) if s >> e & 1) for e in range(14)]
    assert all(a.bit_count() == 2 for a in values)
    return rows[0], tuple(MASKS.index(a) for a in values[-4:])


def check_local_lifts():
    checks = 0
    for s, t in itertools.product(MASKS, repeat=2):
        if (s ^ t) not in MASKS:
            continue
        a, b, c = s & t, s & ~t, t & ~s
        assert a.bit_count() == b.bit_count() == c.bit_count() == 1
        for d in [1 << j for j in range(5) if not (s | t) >> j & 1]:
            left, right = (b | d, a | d), (c | d, a | d)
            assert all(v in MASKS for v in left+right)
            assert left[0] ^ left[1] == s and right[0] ^ right[1] == t
            assert left[1] == right[1] and left[0] ^ right[0] == s ^ t
            checks += 1
            left, right = (a | d, b | d), (a | b, c | b)
            x, y = b | d, c | d
            assert all(v in MASKS for v in left+right+(x, y))
            assert left[0] ^ left[1] == s and right[0] ^ right[1] == t
            assert left[0] ^ right[0] ^ x == left[1] ^ right[1] ^ y == 0
            assert x ^ y == s ^ t
            checks += 1
    assert checks == 240
    return checks


def check_example(rec):
    n = rec["base_vertices"]
    base = rec["base_edges"]
    values = check_assignment(range(n), base, rec["base_cover_word"])
    actual = check_assignment(range(rec["vertices"]), rec["edges"], rec["cover_word"])
    edge_key = lambda e: tuple(sorted(e))
    assert len(set(map(edge_key, base))) == len(base)
    assert len(set(map(edge_key, rec["edges"]))) == len(rec["edges"])
    cycles, kind = rec["cycles"], rec["kind"]
    used = [v for cycle in cycles for v in cycle]
    assert len(used) == len(set(used)) and kind in ("semi", "blowup")
    removed = {edge_key((v, cycle[(i+1) % len(cycle)]))
               for cycle in cycles for i, v in enumerate(cycle)}
    assert removed <= set(map(edge_key, base))
    expected = [tuple(e) for e in base if edge_key(e) not in removed]
    assigned = {edge_key(e): a for e, a in zip(rec["edges"], actual)}
    for e, a in zip(base, values):
        if edge_key(e) not in removed:
            assert assigned[edge_key(e)] == a
    offset = n
    for cycle in cycles:
        k = len(cycle)
        assert k >= 3
        blocks = [{v: offset+8*i+v-2 for v in range(2, 10)} for i in range(k)]
        offset += 8*k
        aux = [(offset+2*i, offset+2*i+1) for i in range(k)]
        if kind == "blowup":
            offset += 2*k
        for i, v in enumerate(cycle):
            b = blocks[i]
            j = (i+1) % k
            expected.extend((b[u], b[w]) for u, w in INTERNAL)
            if kind == "semi":
                expected.extend([(v, b[2]), (b[4], cycle[j]), (b[5], blocks[j][6])])
            else:
                u, w = aux[i]
                expected.extend([(v, u), (v, w), (u, b[2]), (w, b[6]),
                                 (b[4], aux[j][0]), (b[5], aux[j][1])])
    assert offset == rec["vertices"]
    assert Counter(map(edge_key, expected)) == Counter(map(edge_key, rec["edges"]))


def main():
    data = json.loads((HERE / "petersen_boundary.json").read_text())
    assert data["edges"] == [list(e) for e in POLE_EDGES]
    assert data["vertices"] == list(range(2, 10)) and data["pair_masks"] == MASKS
    assert data["port_order"] == ["a1", "a2", "b1", "b2"]
    allowed = {b for b in itertools.product(range(10), repeat=4)
               if MASKS[b[0]] ^ MASKS[b[1]] ^ MASKS[b[2]] ^ MASKS[b[3]] == 0}
    expanded, orbit_keys = set(), []
    for rec in data["representatives"]:
        check_assignment(range(2, 10), POLE_EDGES, rec["cover_word"])
        assert list(map(int, rec["cover_word"][-4:])) == rec["boundary"]
        orbit = set()
        for perm in itertools.permutations(range(5)):
            mapping = [MASKS.index(sum(1 << perm[i] for i in pair)) for pair in PAIR_SETS]
            w = "".join(str(mapping[int(c)]) for c in rec["cover_word"])
            check_assignment(range(2, 10), POLE_EDGES, w)
            orbit.add(tuple(map(int, w[-4:])))
        assert not (expanded & orbit)
        expanded |= orbit
        orbit_keys.append(min(orbit))
        assert tuple(rec["boundary"]) == min(orbit)
    assert expanded == allowed and len(allowed) == data["boundary_states"] == 640
    assert len(orbit_keys) == 10
    print("Ten explicit covers and their label permutations realize all 640 boundary states.")

    states = list(itertools.product(range(10), repeat=2))
    charges = [MASKS[a] ^ MASKS[b] for a, b in states]
    matrix = [[int(left+right in allowed) for right in states] for left in states]
    assert all(matrix[i][j] == (charges[i] == charges[j])
               for i in range(100) for j in range(100))
    sizes = sorted(Counter(charges).values(), reverse=True)
    assert data["boundary_matrix"] == {"dimension": 100, "charge_classes": 16,
                                       "class_sizes": sizes, "boolean_idempotent": True,
                                       "square_over_F2_is_zero": True}
    assert sizes == [10]+[6]*15
    for i in range(100):
        for j in range(100):
            entry = sum(matrix[i][k]*matrix[k][j] for k in range(100))
            assert bool(entry) == bool(matrix[i][j]) and entry % 2 == 0
    print("Boundary matrix: 16 charge classes; Boolean idempotence and F2 square-zero verified.")

    evens = binary_layers()
    assert len(evens) == data["fixed_layer_states"] == 64
    expected_relation = set()
    total = 0
    for rows in enumerate_by_layers(evens, 5):
        total += 1
        expected_relation.add(projected_key(rows))
    assert total == data["named_partial_covers"] == 14700
    assert len(expected_relation) == data["fixed_layer_relation_size"] == 4220
    path = HERE / data["relation_file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == data["relation_sha256"]
    saved_relation = set()
    with gzip.open(path, "rt") as stream:
        for line in stream:
            f, b, w = line.split()
            values = check_assignment(range(2, 10), POLE_EDGES, w)
            first = sum(1 << e for e, a in enumerate(values) if a & 1)
            key = (int(f), tuple(map(int, b)))
            assert first == int(f) and w[-4:] == b and key not in saved_relation
            saved_relation.add(key)
    assert saved_relation == expected_relation
    assert sorted(map(tuple, data["fixed_layer_boundary_counts"])) == sorted(
        Counter(f for f, _ in saved_relation).items())
    candidates = {(f, b) for f in evens for b in allowed
                  if all(bool(f >> (10+i) & 1) == bool(MASKS[b[i]] & 1) for i in range(4))}
    assert expected_relation <= candidates and len(candidates) == 5120
    assert Counter((f >> 10).bit_count() for f, _ in candidates) == {0: 1344, 2: 3456, 4: 320}
    assert Counter((f >> 10).bit_count() for f, _ in expected_relation) == {0: 1020, 2: 2976, 4: 224}
    for f in (15609, 16270):
        actual = {b for g, b in saved_relation if g == f}
        required = {(a, a, b, b) for a in range(4) for b in range(4)}
        assert actual == required
    print("Independent layer exhaustion:", total, "partial covers; 4,220 of 5,120 fixed-layer states realized.")

    four_boundary = {projected_key(rows)[1] for rows in enumerate_by_layers(evens, 4)}
    assert (0, 1, 0, 1) not in four_boundary
    print("Four-label obstruction checked;", len(four_boundary), "boundary states realized with labels 0..3.")
    print("Checked", check_local_lifts(), "local attachment formulas for the two constructions.")
    for rec in data["examples"]:
        check_example(rec)
    assert len(data["examples"]) == 16
    print("Verified 16 constructed graph covers, their graph topology, and preservation of every retained edge label.")


if __name__ == "__main__":
    main()
