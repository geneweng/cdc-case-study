#!/usr/bin/env python3
"""Independent finite certificate check; no constructor or solver imports.

Directly check the full local signature, enumerate all 512^2 reduced cycle
pairs, lift representatives, and verify every actual negative matching.
The earlier certificate is pinned; its connectivity/minimum proof is reused.
"""
from collections import Counter
import hashlib
import itertools
import json
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_SHA = 'e8ee46bb12c877499e3b631a3cac412f679b562cce48a9f4484a7e23197e2dd0'


def decode(code, base, length):
    assert 0 <= code < base ** length
    return tuple(code // base ** i % base for i in range(length))


def code(values, base):
    return sum(value * base ** i for i, value in enumerate(values))


def even(n, edges, mask):
    assert 0 <= mask < 1 << len(edges)
    degrees = [0] * n
    for e, uv in enumerate(edges):
        if mask >> e & 1:
            for v in uv:
                if v >= 0:
                    degrees[v] ^= 1
    return not any(degrees)


def labels(F, t, m):
    return [((F >> e) & 1) + 2 * ((t >> e) & 1) for e in range(m)]


def binary_cycles(n, edges):
    """A spanning-tree parametrization, unrelated to domain propagation."""
    adjacency = [[] for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        adjacency[u].append((v, e))
        adjacency[v].append((u, e))
    parent = {0: (-1, -1)}
    stack = [0]
    tree = set()
    while stack:
        v = stack.pop()
        for w, e in reversed(adjacency[v]):
            if w not in parent:
                parent[w] = (v, e)
                tree.add(e)
                stack.append(w)
    assert len(parent) == n
    def root_path(v):
        mask = 0
        while v:
            v, e = parent[v]
            mask ^= 1 << e
        return mask
    chords = sorted(set(range(len(edges))) - tree)
    basis = [root_path(u) ^ root_path(v) ^ (1 << e)
             for e, (u, v) in enumerate(edges) if e in chords]
    assert all(even(n, edges, C) for C in basis)
    assert all([e for e in chords if C >> e & 1] == [chord] for chord, C in zip(chords, basis))
    space = [0]
    for C in basis:
        space += [D ^ C for D in space]
    assert len(space) == len(set(space)) == 1 << (len(edges) - n + 1)
    return sorted(space)


def components(n, edges, removed):
    """Union-find on the unmatched induced graph."""
    parent = list(range(n))
    def find(v):
        while v != parent[v]:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    for u, v in edges:
        if u not in removed and v not in removed:
            parent[find(u)] = find(v)
    parts = {}
    for v in range(n):
        if v not in removed:
            root = find(v)
            parts[root] = parts.get(root, 0) | (1 << v)
    return sorted(parts.values())


def main():
    data = json.loads((HERE / 'minimum_matching_secondary.json').read_text())
    source_bytes = (HERE / 'cyclic_five_minimum_obstruction.json').read_bytes()
    assert hashlib.sha256(source_bytes).hexdigest() == SOURCE_SHA
    assert data['source'] == {'file': 'cyclic_five_minimum_obstruction.json', 'sha256': SOURCE_SHA}
    source = json.loads(source_bytes)
    Y = source['local_poles']['Y']
    edges = source['graph']['edges']
    assert Y['vertices'] == 41 and len(Y['edges']) == 59
    assert Y['ports'] == [0, 4, 17, 21, 40]
    assert len(edges) == 195 and source['graph']['vertices'] == 130
    assert all(sum(v in uv for uv in edges) == 3 for v in range(130))
    local_edges = Y['edges'] + [[v, -1] for v in Y['ports']]
    groups = [[] for _ in range(11)]
    for e in range(59):
        adjacent_ports = [q for q, p in enumerate(Y['ports']) if p in local_edges[e]]
        assert len(adjacent_ports) <= 1
        groups[1 + adjacent_ports[0] if adjacent_ports else 0].append(e)
    for q in range(5):
        groups[6 + q] = [59 + q]
    assert groups == data['local_edge_groups']
    assert [len(row) for row in groups] == [49] + [2] * 5 + [1] * 5
    assert data['type_names'] == ['U'] + [p + q for p in ('I_', 'B_')
                                        for q in ('alpha', 'beta', 'gamma', 'delta', 'epsilon')]

    # Exhaust all 4^5 boundary words; derive the necessary conditions directly.
    required = set()
    for e in range(64):
        for boundary in itertools.product(range(4), repeat=5):
            if any((value == 3) != (e == 59 + q) for q, value in enumerate(boundary)):
                continue
            total = 0
            for value in boundary:
                total ^= value
            if total:
                continue
            if e < 59 and any(boundary[q] == 0 for q, p in enumerate(Y['ports'])
                              if p in local_edges[e]):
                continue
            required.add((e, code(boundary, 4)))
    lookup = {}
    for e, boundary_code, F, t in data['local_witnesses']:
        assert (e, boundary_code) not in lookup
        assert even(41, local_edges, F) and even(41, local_edges, t)
        assert F & t == 1 << e
        assert tuple(labels(F, t, 64)[59:]) == decode(boundary_code, 4, 5)
        lookup[e, boundary_code] = (F, t)
    assert set(lookup) == required and len(lookup) == 3489
    per_edge = Counter(e for e, _ in required)
    assert Counter(per_edge.values()) == {61: 49, 40: 10, 20: 5}
    for group in groups:
        signatures = [{b for e, b in required if e == target} for target in group]
        assert all(s == signatures[0] for s in signatures)

    # Independently identify the three embedded local pieces and their ports.
    maps = []
    for i in range(3):
        internal = [[u + 41 * i, v + 41 * i] for u, v in Y['edges']]
        assert edges[59 * i:59 * (i + 1)] == internal
        boundary = []
        for p in Y['ports']:
            candidates = [e for e, uv in enumerate(edges)
                          if p + 41 * i in uv and any(v >= 123 for v in uv)]
            assert len(candidates) == 1
            boundary.extend(candidates)
        maps.append(list(range(59 * i, 59 * (i + 1))) + boundary)
    assert maps == data['local_to_global']
    assert len(set(itertools.chain.from_iterable(maps))) == 192
    central = {e for e, uv in enumerate(edges) if 123 in uv}
    assert central == set(range(195)) - set(itertools.chain.from_iterable(maps))
    reduced = [[u // 41 if u < 123 else u - 120,
                v // 41 if v < 123 else v - 120] for u, v in edges[177:]]
    assert reduced == data['reduced_edges']
    assert [sum(v in uv for uv in reduced) for v in range(10)] == [5] * 3 + [3] * 7
    ports = [[e - 177 for e in row[59:]] for row in maps]
    port_masks = [sum(1 << e for e in row) for row in ports]
    central_mask = sum(1 << (e - 177) for e in central)
    outer_stars = [sum(1 << e for e, uv in enumerate(reduced) if v in uv)
                   for v in range(3, 10)]
    space = binary_cycles(10, reduced)
    assert len(space) == 512
    feasible = set()
    for F in space:
        for t in space:
            common = F & t
            if common & central_mask:
                continue
            if any((common & star).bit_count() > 1 for star in outer_stars):
                continue
            options = []
            for i in range(3):
                intersection = common & port_masks[i]
                if intersection.bit_count() > 1:
                    break
                if intersection:
                    options.append([6 + ports[i].index(intersection.bit_length() - 1)])
                else:
                    options.append([0] + [1 + q for q, e in enumerate(ports[i]) if (F | t) >> e & 1])
            if len(options) == 3:
                feasible.update(code(kinds, 11) for kinds in itertools.product(*options))
    positives = {row[0]: row[1:] for row in data['outer_witnesses']}
    invalid = dict(data['invalid_types'])
    negative = dict(data['unsuitable_types'])
    assert len(positives) == len(data['outer_witnesses']) == 1200
    assert len(invalid) == len(data['invalid_types']) == 126
    assert len(negative) == len(data['unsuitable_types']) == 5
    assert feasible == set(positives)
    assert set(positives).isdisjoint(invalid) and set(positives).isdisjoint(negative)
    assert set(invalid).isdisjoint(negative)
    assert set(positives) | set(invalid) | set(negative) == set(range(1331))
    assert {decode(k, 11, 3): v for k, v in negative.items()} == {
        (2, 2, 2): 127, (3, 3, 3): 128, (4, 4, 4): 129,
        (6, 6, 6): 123, (10, 10, 10): 123}

    def glue(kinds, targets, outer_pair):
        F, t = outer_pair
        assert even(10, reduced, F) and even(10, reduced, t)
        values = labels(F, t, 18)
        full_values = [None] * 177 + values
        for i, target in enumerate(targets):
            assert target in groups[kinds[i]]
            boundary = [values[e] for e in ports[i]]
            local_pair = lookup[target, code(boundary, 4)]
            for e, value in enumerate(labels(*local_pair, 64)):
                position = maps[i][e]
                assert full_values[position] is None or full_values[position] == value
                full_values[position] = value
        assert None not in full_values
        A = sum((x & 1) << e for e, x in enumerate(full_values))
        B = sum(((x >> 1) & 1) << e for e, x in enumerate(full_values))
        assert even(130, edges, A) and even(130, edges, B)
        assert A & B == sum(1 << maps[i][e] for i, e in enumerate(targets))

    weights = Counter()
    for kind_code in range(1331):
        kinds = decode(kind_code, 11, 3)
        targets = [groups[t][0] for t in kinds]
        matching = [maps[i][e] for i, e in enumerate(targets)]
        multiplicity = prod(len(groups[t]) for t in kinds)
        counts = Counter(v for e in matching for v in edges[e])
        collision = {v for v, count in counts.items() if count > 1}
        if kind_code in invalid:
            assert collision and invalid[kind_code] in collision
            assert all(v >= 123 for v in collision)
            weights['not_matching'] += multiplicity
        elif kind_code in negative:
            assert not collision
            weights['unsuitable'] += multiplicity
        else:
            assert not collision
            glue(kinds, targets, positives[kind_code])
            weights['suitable'] += multiplicity
    assert dict(weights) == data['weighted_counts'] == {
        'suitable': 261356, 'not_matching': 762, 'unsuitable': 26}
    assert data['type_counts'] == {'suitable': 1200, 'not_matching': 126, 'unsuitable': 5}
    assert sum(weights.values()) == 64 ** 3

    expected_bad = {}
    for kind_code, singleton in negative.items():
        kinds = decode(kind_code, 11, 3)
        for targets in itertools.product(*(groups[t] for t in kinds)):
            M = tuple(sorted(maps[i][e] for i, e in enumerate(targets)))
            expected_bad[M] = singleton
    found_bad = {}
    for matching, singleton, saved_parts in data['unsuitable_matchings']:
        key = tuple(matching)
        assert key not in found_bad and expected_bad[key] == singleton
        removed = {v for e in matching for v in edges[e]}
        assert len(removed) == 6 and singleton not in removed
        neighbors = {v if u == singleton else u for u, v in edges if singleton in (u, v)}
        assert len(neighbors) == 3 and neighbors <= removed
        parts = components(130, edges, removed)
        assert parts == saved_parts and sorted(K.bit_count() for K in parts) == [1, 123]
        assert 1 << singleton in parts
        found_bad[key] = singleton
    assert found_bad == expected_bad and len(found_bad) == 26

    # Verify the earlier neutral switch supplies an attained secondary optimum.
    first = source['repair']['moves'][0]
    before, after = source['initial_flow'], first['flow_after']
    assert first['increment'] == 6
    circuit = set(first['edges'])
    assert len(circuit) == len(first['edges']) == 12
    degrees = [sum(e in circuit and v in uv for e, uv in enumerate(edges)) for v in range(130)]
    assert set(degrees) <= {0, 2} and degrees.count(2) == 12
    touched = {v for v, degree in enumerate(degrees) if degree}
    assert len(components(130, [edges[e] for e in circuit], set(range(130)) - touched)) == 1
    assert after == [x ^ 6 if e in circuit else x for e, x in enumerate(before)]
    assert Counter(before) == Counter(after)
    for j, flow in enumerate((before, after)):
        assert len(flow) == 195 and all(1 <= x <= 7 for x in flow)
        assert all(even(130, edges, sum(((x >> b) & 1) << e for e, x in enumerate(flow))) for b in range(3))
        matching = [e for e, x in enumerate(flow) if x == 4]
        assert len(matching) == min(flow.count(a) for a in range(1, 8)) == 3
        assert all(len(set(matching) & set(row)) == 1 for row in maps)
        targets = [next(e for e, global_e in enumerate(row) if global_e in matching) for row in maps]
        kinds = [next(t for t, group in enumerate(groups) if e in group) for e in targets]
        parts = components(130, edges, {v for e in matching for v in edges[e]})
        odd = [K for K in parts if K.bit_count() % 2]
        assert data['secondary_objective_stages'][j] == {
            'stage': ['initial', 'after_neutral_switch'][j], 'matching': matching,
            'types': kinds, 'odd_unmatched_components': odd}
        assert len(odd) == [2, 0][j]
        if j:
            glue(kinds, targets, positives[code(kinds, 11)])
    print('PASS: all 3,489 local witnesses; exact 61/40/20 signatures.')
    print('PASS: all 262,144 reduced cycle pairs; 1,200 suitable / 126 invalid / 5 unsuitable types.')
    print('PASS: 1,200 representative lifts plus the actual repaired minimum class.')
    print('PASS: 261,356 suitable matchings by gluing; all 26 failures have components of orders 1 and 123.')
    print('PASS: the saved neutral switch changes the objective from (3,2) to (3,0).')
    print('Scope: the 130-vertex graph, using the pinned preceding minimum/connectivity proof.')


if __name__ == '__main__':
    main()
