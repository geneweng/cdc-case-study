#!/usr/bin/env python3
"""Complete intersection-pair signatures and a secondary minimum on ThreeY1Star130.

The constructor uses only finite-domain XOR propagation and backtracking.
The independent verifier instead exhausts the reduced graph's cycle space.
"""
from collections import Counter
import hashlib
import itertools
import json
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = 'cyclic_five_minimum_obstruction.json'
SOURCE_SHA = 'e8ee46bb12c877499e3b631a3cac412f679b562cce48a9f4484a7e23197e2dd0'
PORT_NAMES = ['alpha', 'beta', 'gamma', 'delta', 'epsilon']
XOR = [[sum(1 << v for v in {a ^ b for a in range(4) if A >> a & 1
                            for b in range(4) if B >> b & 1})
        for B in range(16)] for A in range(16)]


class Constraints:
    """Domains are bitsets of the four labels; dangling ends are numbered -1."""
    def __init__(self, n, edges):
        self.n = n
        self.inc = [[e for e, uv in enumerate(edges) if v in uv] for v in range(n)]
        self.touch = [[v for v in uv if 0 <= v < n] for uv in edges]

    def solve(self, domains):
        def visit(ds, queue):
            todo = set(queue)
            while todo:
                v = min(todo)
                todo.remove(v)
                row = self.inc[v]
                for e in row:
                    allowed = 1
                    for other in row:
                        if other != e:
                            allowed = XOR[allowed][ds[other]]
                    new = ds[e] & allowed
                    if not new:
                        return None
                    if new != ds[e]:
                        ds[e] = new
                        todo.update(self.touch[e])
            undecided = [e for e, d in enumerate(ds) if d.bit_count() > 1]
            if not undecided:
                return [d.bit_length() - 1 for d in ds]
            e = min(undecided, key=lambda e: (
                ds[e].bit_count(),
                sum(ds[f].bit_count() > 1 for v in self.touch[e] for f in self.inc[v]), e))
            for x in range(4):
                if ds[e] >> x & 1:
                    nxt = ds.copy()
                    nxt[e] = 1 << x
                    out = visit(nxt, self.touch[e])
                    if out is not None:
                        return out
            return None
        return visit(domains.copy(), range(self.n))


def xor(values):
    out = 0
    for value in values:
        out ^= value
    return out


def encode(values, base):
    return sum(x * base ** i for i, x in enumerate(values))


def pair(values):
    return [sum((x & 1) << e for e, x in enumerate(values)),
            sum(((x >> 1) & 1) << e for e, x in enumerate(values))]


def local_catalog(Y):
    edges = Y['edges'] + [[v, -1] for v in Y['ports']]
    groups = [[] for _ in range(11)]
    records = []
    solver = Constraints(41, edges)
    for target in range(64):
        ports = [q for q, p in enumerate(Y['ports']) if target < 59 and p in edges[target]]
        assert len(ports) <= 1
        kind = 6 + target - 59 if target >= 59 else 1 + ports[0] if ports else 0
        groups[kind].append(target)
        ranges = [(3,) if target == 59 + q else (1, 2) if q in ports else (0, 1, 2)
                  for q in range(5)]
        for boundary in itertools.product(*ranges):
            if xor(boundary):
                continue
            domains = [8 if e == target else 7 for e in range(64)]
            for q, x in enumerate(boundary):
                domains[59 + q] = 1 << x
            values = solver.solve(domains)
            assert values is not None, (target, boundary)
            records.append([target, encode(boundary, 4), *pair(values)])
    assert [len(g) for g in groups] == [49] + [2] * 5 + [1] * 5
    assert len(records) == 3489
    return groups, records


def assembly(g, Y):
    edges = g['edges']
    maps = []
    for i in range(3):
        ports = [v + 41 * i for v in Y['ports']]
        boundary = []
        for v in ports:
            found = [e for e, uv in enumerate(edges)
                     if v in uv and not all(41 * i <= w < 41 * (i + 1) for w in uv)]
            assert len(found) == 1
            boundary += found
        maps.append(list(range(59 * i, 59 * (i + 1))) + boundary)
    def contracted(v):
        return v // 41 if v < 123 else v - 120
    return maps, [[contracted(u), contracted(v)] for u, v in edges[177:]]


def unmatched_components(edges, matching):
    removed = {v for e in matching for v in edges[e]}
    left = set(range(130)) - removed
    adj = [set() for _ in range(130)]
    for u, v in edges:
        if u in left and v in left:
            adj[u].add(v)
            adj[v].add(u)
    parts = []
    while left:
        part = {min(left)}
        todo = list(part)
        left -= part
        while todo:
            v = todo.pop()
            fresh = adj[v] & left
            left -= fresh
            part |= fresh
            todo.extend(sorted(fresh))
        parts.append(sum(1 << v for v in part))
    return sorted(parts)


def main():
    source_bytes = (HERE / SOURCE).read_bytes()
    assert hashlib.sha256(source_bytes).hexdigest() == SOURCE_SHA
    source = json.loads(source_bytes)
    Y, g = source['local_poles']['Y'], source['graph']
    groups, local = local_catalog(Y)
    maps, reduced = assembly(g, Y)
    solver = Constraints(10, reduced)
    positive, invalid, negative, bad_matchings = [], [], [], []
    counts, weighted = Counter(), Counter()
    for kinds in itertools.product(range(11), repeat=3):
        code = encode(kinds, 11)
        weight = prod(len(groups[t]) for t in kinds)
        matching = [maps[i][groups[t][0]] for i, t in enumerate(kinds)]
        ends = Counter(v for e in matching for v in g['edges'][e])
        collisions = sorted(v for v, count in ends.items() if count > 1)
        if collisions:
            assert all(v >= 123 for v in collisions)
            invalid.append([code, collisions[0]])
            counts['not_matching'] += 1
            weighted['not_matching'] += weight
            continue
        domains = [7] * 18
        for i, t in enumerate(kinds):
            if 1 <= t <= 5:
                domains[maps[i][59 + t - 1] - 177] &= 6
            elif t >= 6:
                domains[maps[i][59 + t - 6] - 177] = 8
        values = solver.solve(domains)
        if values is not None:
            positive.append([code, *pair(values)])
            counts['suitable'] += 1
            weighted['suitable'] += weight
        else:
            parts = unmatched_components(g['edges'], matching)
            singleton = [K.bit_length() - 1 for K in parts if K.bit_count() == 1]
            assert len(singleton) == 1
            negative.append([code, singleton[0]])
            for targets in itertools.product(*(groups[t] for t in kinds)):
                actual = sorted(maps[i][e] for i, e in enumerate(targets))
                parts = unmatched_components(g['edges'], actual)
                assert sorted(K.bit_count() for K in parts) == [1, 123]
                assert 1 << singleton[0] in parts
                bad_matchings.append([actual, singleton[0], parts])
            counts['unsuitable'] += 1
            weighted['unsuitable'] += weight
    assert counts == {'suitable': 1200, 'not_matching': 126, 'unsuitable': 5}
    assert weighted == {'suitable': 261356, 'not_matching': 762, 'unsuitable': 26}
    stages = []
    for name, flow in [('initial', source['initial_flow']),
                       ('after_neutral_switch', source['repair']['moves'][0]['flow_after'])]:
        matching = [e for e, x in enumerate(flow) if x == 4]
        parts = unmatched_components(g['edges'], matching)
        kinds = [next(t for t, group in enumerate(groups)
                      if any(maps[i][e] in matching for e in group)) for i in range(3)]
        stages.append({'stage': name, 'matching': matching, 'types': kinds,
                       'odd_unmatched_components': [K for K in parts if K.bit_count() % 2]})
    result = {
        'date': '2026-10-06',
        'scope': 'Every one-edge-per-region matching on ThreeY1Star130 is suitable exactly when its unmatched induced graph has no odd component.',
        'source': {'file': SOURCE, 'sha256': SOURCE_SHA},
        'encoding': {'local_witness': '[target edge, little-endian base-4 boundary code, F mask, t mask]',
                     'type_code': 't0 + 11*t1 + 121*t2',
                     'outer_witness': '[type code, reduced F mask, reduced t mask]',
                     'reduced_vertices': '0,1,2 are regions; 3,...,9 are original vertices 123,...,129',
                     'reduced_edges': 'Original edge indices 177,...,194, in order'},
        'type_names': ['U'] + ['I_' + p for p in PORT_NAMES] + ['B_' + p for p in PORT_NAMES],
        'local_edge_groups': groups, 'local_witnesses': sorted(local),
        'local_to_global': maps, 'reduced_edges': reduced,
        'outer_witnesses': sorted(positive),
        'invalid_types': sorted(invalid), 'unsuitable_types': sorted(negative),
        'unsuitable_matchings': sorted(bad_matchings),
        'type_counts': dict(sorted(counts.items())), 'weighted_counts': dict(sorted(weighted.items())),
        'secondary_objective_stages': stages}
    path = HERE / 'minimum_matching_secondary.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print('Local witnesses:', len(local))
    print('Type counts:', counts, 'Weighted counts:', weighted)
    print('Secondary objective:', [(len(r['matching']), len(r['odd_unmatched_components'])) for r in stages])
    print('Certificate bytes:', path.stat().st_size, 'SHA256:', hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
