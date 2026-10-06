#!/usr/bin/env python3
"""Independent checks for the secondary-minimum counterexample.

No constructor imports. Reuses the preceding independent local-piece audit;
checks new cuts, forced parity, flow switches and cover directly.
"""
from collections import deque
from itertools import combinations
import hashlib
import json
from math import comb
from pathlib import Path

from verify_cyclic_five_minimum_obstruction import local_structure, local_audit

HERE = Path(__file__).resolve().parent


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


class Check:
    def __init__(self, g):
        self.n, self.edges = g['vertices'], g['edges']
        self.m = len(self.edges)
        self.full = (1 << self.m)-1
        assert (self.n, self.m) == (138, 207)
        assert all(0 <= u < self.n and 0 <= v < self.n and u != v for u, v in self.edges)
        assert len({tuple(sorted(uv)) for uv in self.edges}) == self.m
        self.adj = [[(u ^ v ^ w, e) for e, (u, v) in enumerate(self.edges) if w in (u, v)]
                    for w in range(self.n)]
        assert all(len(row) == 3 for row in self.adj)
        assert len(self.components(self.full)) == 1

    def components(self, mask):
        assert 0 <= mask <= self.full
        parent = list(range(self.n))
        def root(v):
            while parent[v] != v:
                parent[v] = parent[parent[v]]
                v = parent[v]
            return v
        for e, (u, v) in enumerate(self.edges):
            if mask >> e & 1:
                parent[root(u)] = root(v)
        parts = {}
        for v in range(self.n):
            r = root(v)
            parts[r] = parts.get(r, 0) | (1 << v)
        return sorted(parts.values())

    def cut(self, X):
        return sum((((X >> u) ^ (X >> v)) & 1) << e for e, (u, v) in enumerate(self.edges))

    def even(self, mask):
        assert 0 <= mask <= self.full
        return all(sum((mask >> e) & 1 for _, e in row) % 2 == 0 for row in self.adj)

    def circuits(self, mask):
        assert self.even(mask)
        parts = self.components(mask)
        return sorted(sorted(e for e, (u, _) in enumerate(self.edges) if mask >> e & 1 and K >> u & 1)
                      for K in parts if any(mask >> e & 1 and K >> u & 1 for e, (u, _) in enumerate(self.edges)))

    def flow(self, values):
        assert len(values) == self.m and all(1 <= x <= 7 for x in values)
        for row in self.adj:
            total = 0
            for _, e in row:
                total ^= values[e]
            assert total == 0

    def support(self, values, ell):
        return sum(((x & ell).bit_count() % 2) << e for e, x in enumerate(values))

    def unmatched(self, M):
        endpoints = [v for e, uv in enumerate(self.edges) if M >> e & 1 for v in uv]
        assert len(endpoints) == len(set(endpoints))
        D = sum(1 << v for v in endpoints)
        B = ((1 << self.n)-1) ^ D
        induced = sum((bool(B >> u & 1 and B >> v & 1)) << e for e, (u, v) in enumerate(self.edges))
        return D, B, induced, sorted(K for K in self.components(induced) if K & B)

    def connectivity(self, record):
        parent = {0: (-1, -1)}
        stack, tree = [0], set()
        while stack:
            v = stack.pop()
            for w, e in reversed(self.adj[v]):
                if w not in parent:
                    parent[w] = (v, e)
                    tree.add(e)
                    stack.append(w)
        assert len(parent) == self.n
        def root_path(v):
            mask = 0
            while v:
                v, e = parent[v]
                mask ^= 1 << e
            return mask
        chords = sorted(set(range(self.m)) - tree)
        basis = [root_path(self.edges[e][0]) ^ root_path(self.edges[e][1]) ^ (1 << e) for e in chords]
        assert len(basis) == 70 and all(self.even(C) for C in basis)
        assert all([e for e in chords if C >> e & 1] == [chord] for chord, C in zip(chords, basis))
        columns = [sum(((C >> e) & 1) << i for i, C in enumerate(basis)) for e in range(self.m)]
        assert 0 not in columns and len(set(columns)) == self.m
        triples = [[a, b, c] for a, b, c in combinations(range(self.m), 3)
                   if columns[a] ^ columns[b] ^ columns[c] == 0]
        assert triples == sorted(sorted(e for _, e in row) for row in self.adj)
        quads = [[a, b, c, d] for a, b, c, d in combinations(range(self.m), 4)
                 if columns[a] ^ columns[b] ^ columns[c] ^ columns[d] == 0]
        expected = sorted(sorted({e for _, e in self.adj[u]} ^ {e for _, e in self.adj[v]})
                          for u, v in self.edges)
        assert quads == expected
        side = (1 << 41)-1
        boundary = self.cut(side)
        parts = self.components(self.full ^ boundary)
        assert boundary.bit_count() == 5 and len(parts) == 2 and side in parts
        assert all(sum(bool(K >> u & 1 and K >> v & 1) for u, v in self.edges) >= K.bit_count() for K in parts)
        assert record == {'cycle_dimension': 70, 'distinct_nonzero_columns': 207,
                          'three_edge_cuts': 138, 'three_cut_records_sha256': digest(triples),
                          'four_edge_cuts': 207, 'four_cut_records_sha256': digest(quads),
                          'five_cut_side': side, 'five_cut_edges': boundary, 'cyclic_edge_connectivity': 5}
        girth = self.n
        for start in range(self.n):
            distance, previous = {start: 0}, {start: -1}
            queue = deque([start])
            while queue:
                v = queue.popleft()
                for w, _ in self.adj[v]:
                    if w not in distance:
                        distance[w], previous[w] = distance[v]+1, v
                        queue.append(w)
                    elif previous[v] != w and previous[w] != v:
                        girth = min(girth, distance[v]+distance[w]+1)
        assert girth == 5
        return comb(self.m, 3), comb(self.m, 4)


def main():
    path = HERE / 'secondary_minimum_obstruction.json'
    data = json.loads(path.read_text())
    assert data['sources'] == [
        {'file': 'cyclic_five_minimum_obstruction.json', 'sha256': 'e8ee46bb12c877499e3b631a3cac412f679b562cce48a9f4484a7e23197e2dd0'},
        {'file': 'minimum_matching_secondary.json', 'sha256': '32082a951b4c3012b9f8a312e46b5b117490a899e3a3299a35b6f5dc344975ec'}]
    for source in data['sources']:
        assert hashlib.sha256((HERE / source['file']).read_bytes()).hexdigest() == source['sha256']
    poles = data['local_poles']
    local_structure(poles)
    assert local_audit(poles) == data['local_audits']
    obj = Check(data['graph'])
    g, Y = data['graph'], poles['Y']
    expected = [[u+41*i, v+41*i] for i in range(3) for u, v in Y['edges']]
    used = [0, 0, 0]
    for u, v in g['quotient_edges']:
        assert 0 <= u < 18 and 3 <= v < 18 and u != v
        if u < 3:
            expected.append([41*u+Y['ports'][used[u]], v+120])
            used[u] += 1
        else:
            expected.append([u+120, v+120])
    assert used == [5, 5, 5] and obj.edges == expected
    charged = []
    assert len(g['regions']) == 3
    for i, region in enumerate(g['regions']):
        vertices = set(range(41*i, 41*(i+1)))
        assert region['vertices'] == sorted(vertices)
        assert region['ports'] == [41*i+p for p in Y['ports']]
        row = {e for e, uv in enumerate(obj.edges) if vertices.intersection(uv)}
        assert len(row) == 64 and sorted(row) == region['charged_edges']
        charged.append(row)
    assert all(a.isdisjoint(b) for a, b in combinations(charged, 2))
    # The independent local audit excludes zero-free projections in each Y.
    # Disjoint charged sets therefore force every three-bit color to occur >=3 times.
    f = data['initial_flow']
    obj.flow(f)
    assert data['initial_color_sizes'] == [f.count(a) for a in range(1, 8)] == [58, 58, 56, 3, 9, 11, 12]
    assert data['minimum_color_multiplicity'] == 3 and data['secondary_minimum'] == [3, 0]
    triples, quads = obj.connectivity(data['connectivity'])
    girth = data['girth_certificate']
    assert girth['girth'] == 5 and len(girth['shortest_circuit_edges']) == 5
    assert len(obj.circuits(sum(1 << e for e in girth['shortest_circuit_edges']))) == 1

    r = data['obstruction']
    M = sum((x == 4) << e for e, x in enumerate(f))
    assert M == r['matching'] and r['matching_edges'] == [178, 183, 189]
    assert M == sum(1 << e for e in r['matching_edges'])
    assert all(len(set(r['matching_edges']) & row) == 1 for row in charged)
    D, B, induced, parts = obj.unmatched(M)
    assert r['endpoints'] == [v for v in range(obj.n) if D >> v & 1] == [4, 45, 99, 124, 130, 134]
    assert r['unmatched_vertices'] == B and r['unmatched_components'] == parts == [B]
    assert B.bit_count() == 132 and r['odd_component_count'] == 0
    assert induced.bit_count() == r['unmatched_internal_edges'] == 192
    forced = sum((not (M >> e & 1) and bool(D >> u & 1 or D >> v & 1)) << e
                 for e, (u, v) in enumerate(obj.edges))
    assert forced == r['forced_edges']
    vertices, cycle = r['forced_circuit_vertices'], r['forced_circuit_edges']
    assert len(vertices) == len(set(vertices)) == len(cycle) == len(set(cycle)) == 6
    assert all(set(obj.edges[e]) == {u, v} for e, u, v in zip(cycle, vertices, vertices[1:]+vertices[:1]))
    C = sum(1 << e for e in cycle)
    assert C & forced == C and obj.even(C)
    assert all(bool(D >> v & 1) == (i % 2 == 0) for i, v in enumerate(vertices))
    assert sum(bool(D >> v & 1) for v in vertices) == r['forced_circuit_terminal_count'] == 3
    # Any even candidate containing these six forced edges must retain this
    # whole circuit component, whose three terminals violate circuit parity.
    L = r['candidate']
    assert obj.even(L) and L & M == 0 and L & forced == forced
    circuits = obj.circuits(L)
    assert circuits == r['candidate_circuits'] and sorted(cycle) in circuits
    counts = [len({v for e in row for v in obj.edges[e] if D >> v & 1}) for row in circuits]
    assert counts == r['candidate_terminal_counts'] == [1, 1, 1, 3]
    assert r['candidate_dimension'] == induced.bit_count()-B.bit_count()+len(parts) == 61

    cuts = r['terminal_cut_obstruction']
    assert len(cuts) == 3
    terminal_pairs = set()
    for cut in cuts:
        X = sum(1 << v for v in cut['vertices'])
        pair = tuple(v for v in r['endpoints'] if X >> v & 1)
        terminal_pairs.add(pair)
        assert list(pair) == cut['terminal_vertices'] and len(pair) == 2
        boundary = obj.cut(X) & ~M
        assert cut['boundary_in_H'] == [e for e in range(obj.m) if boundary >> e & 1]
        assert boundary.bit_count() == 3
    assert terminal_pairs == {(124, 130), (124, 134), (130, 134)}
    signings = 0
    for tail in combinations(r['endpoints'][1:], 2):
        S = sum(1 << v for v in (r['endpoints'][0],)+tail)
        deficits = []
        for cut in cuts:
            X = sum(1 << v for v in cut['vertices'])
            imbalance = abs((X & S).bit_count()-(X & (D ^ S)).bit_count())
            deficits.append(2*imbalance-len(cut['boundary_in_H']))
        assert max(deficits) > 0
        signings += 1
    assert signings == r['balanced_signings_excluded'] == 10

    repair = data['repair']
    assert len(repair['moves']) == 3
    assert [len(move['edges']) for move in repair['moves']] == [40, 30, 25]
    assert [move['increment'] for move in repair['moves']] == [1, 4, 4]
    for j, move in enumerate(repair['moves']):
        edge_ids, a = move['edges'], move['increment']
        assert len(set(edge_ids)) == len(edge_ids)
        mask = sum(1 << e for e in edge_ids)
        assert len(obj.circuits(mask)) == 1 and all(f[e] != a for e in edge_ids)
        f = [x ^ a if mask >> e & 1 else x for e, x in enumerate(f)]
        obj.flow(f)
        assert f == move['flow_after'] and move['color_sizes'] == [f.count(a) for a in range(1, 8)]
        matching = sum((x == 4) << e for e, x in enumerate(f))
        assert matching.bit_count() == min(move['color_sizes']) == 3
        assert all(K.bit_count() % 2 == 0 for K in obj.unmatched(matching)[3])
        assert matching == sum(1 << e for e in [181, 183, 189])
        if j == 0:
            F, t = repair['intersection_first'], repair['intersection_partner']
            assert obj.even(F) and obj.even(t) and F & t == matching
    assert repair['first_functional'] == repair['target_color'] == 4
    assert obj.support(f, 4) == F
    lift = repair['final_lift']
    assert lift['coordinate_functionals'] == [2, 1, 4]
    transformed = [sum(((x & ell).bit_count() % 2) << i for i, ell in enumerate([2, 1, 4])) for x in f]
    assert transformed == lift['transformed_flow']
    fourth = t ^ obj.support(f, 1) ^ obj.support(f, 2)
    assert fourth == lift['fourth_coordinate'] and obj.even(fourth)
    palette = [4, 5, 6, 15, 8]
    cover = lift['cover_pairs']
    assert len(cover) == obj.m and all(0 <= x < 32 and x.bit_count() == 2 for x in cover)
    for e, mask in enumerate(cover):
        i, j = [i for i in range(5) if mask >> i & 1]
        assert palette[i] ^ palette[j] == transformed[e] + 8*((fourth >> e) & 1)
    assert all(obj.even(sum(((mask >> layer) & 1) << e for e, mask in enumerate(cover))) for layer in range(5))
    print('PASS: local zero-free audit and three disjoint regions prove global minimum 3.')
    print(f'PASS: {triples:,} edge triples and {quads:,} quadruples; girth 5, cyclic connectivity 5.')
    print('PASS: unmatched graph connected on 132 vertices; global secondary optimum (3,0).')
    print('PASS: forced hexagon has 3 terminals; every one of the 2^61 candidates fails.')
    print('PASS: three explicit terminal cuts exclude all 10 balanced signings.')
    print('PASS: circuit switches of lengths 40, 30, 25 retain (3,0) and construct a five-layer cover.')


if __name__ == '__main__':
    main()
