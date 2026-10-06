#!/usr/bin/env python3
"""Check the quotient enumeration through projected cycle spaces instead.

No constructor imports. The graph's global minimum and connectivity come
from the pinned, previously verified source; every new claim is checked here.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path

from verify_secondary_minimum_obstruction import Check

HERE = Path(__file__).resolve().parent


def mask(edges):
    return sum(1 << e for e in edges)


def forest_cycles(obj, active):
    parent, tree = {}, set()
    for root in range(obj.n):
        if root in parent:
            continue
        parent[root] = (-1, -1)
        stack = [root]
        while stack:
            v = stack.pop()
            for w, e in reversed(obj.adj[v]):
                if active >> e & 1 and w not in parent:
                    parent[w] = (v, e)
                    tree.add(e)
                    stack.append(w)
    def path(v):
        result = 0
        while parent[v][0] != -1:
            v, e = parent[v]
            result ^= 1 << e
        return result
    chords = [e for e in range(obj.m) if active >> e & 1 and e not in tree]
    basis = [path(obj.edges[e][0]) ^ path(obj.edges[e][1]) ^ (1 << e) for e in chords]
    assert len(basis) == active.bit_count()-obj.n+len(obj.components(active))
    assert all(obj.even(C) and C & ~active == 0 for C in basis)
    assert all([e for e in chords if C >> e & 1] == [chord] for C, chord in zip(basis, chords))
    return basis


def pivots(rows):
    result = {}
    for row in rows:
        while row:
            bit = row.bit_length()-1
            if bit in result:
                row ^= result[bit]
            else:
                result[bit] = row
                break
    return result


def belongs(row, basis):
    while row:
        bit = row.bit_length()-1
        if bit not in basis:
            return False
        row ^= basis[bit]
    return True


def main():
    data = json.loads((HERE / 'neutral_minimum_quotient.json').read_text())
    assert data['sources'] == [
        {'file': 'secondary_minimum_obstruction.json', 'sha256': 'f722b31c3247ef29ad9a7214574a0283dfed1a877c4cc93ea07be75e2b1c87b5'},
        {'file': 'minimum_matching_secondary.json', 'sha256': '32082a951b4c3012b9f8a312e46b5b117490a899e3a3299a35b6f5dc344975ec'}]
    for source in data['sources']:
        assert hashlib.sha256((HERE / source['file']).read_bytes()).hexdigest() == source['sha256']
    source = json.loads((HERE / data['sources'][0]['file']).read_text())
    obj = Check(source['graph'])
    flow = source['initial_flow']
    obj.flow(flow)
    a = data['target_color']
    assert a == 4 and data['minimum_size'] == source['minimum_color_multiplicity'] == 3
    original = tuple(e for e, x in enumerate(flow) if x == a)
    original_mask = mask(original)
    assert list(original) == data['original_matching'] == [178, 183, 189]
    pairs = {}
    for r in data['suitable_replacements']:
        K = tuple(r['matching'])
        assert K not in pairs and len(K) == len(set(K)) == 3
        assert obj.even(r['first']) and obj.even(r['partner'])
        assert r['first'] & r['partner'] == mask(K)
        assert all(P.bit_count() % 2 == 0 for P in obj.unmatched(mask(K))[3])
        pairs[K] = (r['first'], r['partner'])
    assert len(pairs) == 29 and original not in pairs
    union, tagged, successful = set(), 0, 0
    assert [r['increment'] for r in data['fibers']] == [1, 2, 3, 5, 6, 7]
    expected_counts = {1: (12, 5, 4, 128), 2: (13, 5, 2, 64), 3: (14, 7, 2, 256),
                       5: (61, 5, 24, 768), 6: (59, 5, 2, 64), 7: (58, 7, 1, 128)}
    for row in data['fibers']:
        b = row['increment']
        H = mask(e for e, x in enumerate(flow) if x != b)
        cost_edges = [e for e, x in enumerate(flow) if x in (a, a ^ b)]
        cost = mask(cost_edges)
        Z = H ^ cost
        assert row['cost_edges'] == cost_edges and row['zero_edges'] == Z
        parts = sorted(obj.components(Z), key=lambda K: (K & -K).bit_length())
        assert row['zero_components'] == parts
        component = {v: i for i, K in enumerate(parts) for v in range(obj.n) if K >> v & 1}
        columns = [(1 << component[obj.edges[e][0]]) ^ (1 << component[obj.edges[e][1]]) for e in cost_edges]
        assert columns == row['edge_columns']
        terminal = 0
        for e, column in zip(cost_edges, columns):
            if e in original:
                terminal ^= column
        assert terminal == row['terminal_mask']

        # Independent completeness: project a basis of Z(G-M_b) to the
        # prescribed-cost coordinates, then test membership by elimination.
        cycles = forest_cycles(obj, H)
        projected = pivots(C & cost for C in cycles)
        kernel = len(cycles)-len(projected)
        assert kernel == len(forest_cycles(obj, Z)) == row['free_dimension']
        assert len(cycles) == row['fiber_dimension']
        reachable = set()
        for size in range(4):
            for K in combinations(cost_edges, size):
                if belongs(original_mask ^ mask(K), projected):
                    assert size == 3
                    reachable.add(K)
        records = {tuple(r['matching']): r for r in row['replacements']}
        assert len(records) == len(row['replacements']) and set(records) == reachable
        assert original in records
        assert reachable - {original} <= set(pairs)
        for K, r in records.items():
            current = flow
            assert len(r['circuits']) == (0 if K == original else 1)
            for C in r['circuits']:
                assert len(C) == len(set(C)) and len(obj.circuits(mask(C))) == 1
                assert all(current[e] != b for e in C)
                current = [x ^ b if e in C else x for e, x in enumerate(current)]
                obj.flow(current)
                assert current.count(a) == 3
            assert tuple(e for e, x in enumerate(current) if x == a) == K
            assert all(P.bit_count() % 2 == 0 for P in obj.unmatched(mask(K))[3])
        count = len(reachable) * (1 << kernel)
        assert count == row['optimal_flow_count']
        assert (len(cycles), kernel, len(reachable), count) == expected_counts[b]
        union |= reachable
        tagged += count
        successful += (len(reachable)-1) * (1 << kernel)
    assert union == {original} | set(pairs)
    assert len(union) == data['distinct_replacement_matchings'] == 30
    assert tagged == data['tagged_optimal_flow_count'] == 1408
    assert successful == data['suitable_target_flow_count'] == 1024

    lower = []
    for excluded in original:
        u, v = obj.edges[excluded]
        # Breadth-first layers from the opposite endpoint, independent of
        # the constructor's queue and parent traversal.
        seen, frontier, distance = {v}, {v}, 0
        while u not in seen:
            frontier = {w for x in frontier for w, e in obj.adj[x]
                        if e != excluded and w not in seen}
            assert frontier
            seen |= frontier
            distance += 1
        lower.append([excluded, distance+1])
    assert lower == data['matching_edge_cycle_lower_bounds'] == [[178, 13], [183, 9], [189, 6]]
    shortest = data['shortest_neutral_escape']
    assert shortest['increment'] == 1 and shortest['edges'] == [142, 146, 148, 189, 190, 194]
    assert shortest['matching_after'] == [148, 178, 183]
    assert len(shortest['edges']) == min(length for _, length in lower) == 6
    repair = data['repair']
    assert len(repair['moves']) == 2
    assert [len(move['edges']) for move in repair['moves']] == [6, 55]
    assert [move['increment'] for move in repair['moves']] == [1, 4]
    current = flow
    for j, move in enumerate(repair['moves']):
        C, b = move['edges'], move['increment']
        assert len(C) == len(set(C)) and len(obj.circuits(mask(C))) == 1
        assert all(current[e] != b for e in C)
        current = [x ^ b if e in C else x for e, x in enumerate(current)]
        obj.flow(current)
        assert current == move['flow_after'] and move['color_sizes'] == [current.count(x) for x in range(1, 8)]
        assert current.count(a) == min(move['color_sizes']) == 3
        assert [e for e, x in enumerate(current) if x == a] == shortest['matching_after']
        if j == 0:
            assert move['edges'] == shortest['edges'] and move['color_sizes'] == source['initial_color_sizes']
    F, t = repair['intersection_first'], repair['intersection_partner']
    assert (F, t) == pairs[tuple(shortest['matching_after'])]
    assert obj.support(current, 4) == F
    assert repair['coordinate_functionals'] == [2, 1, 4]
    transformed = [sum(((x & ell).bit_count() % 2) << i for i, ell in enumerate([2, 1, 4])) for x in current]
    assert transformed == repair['transformed_flow']
    w = t ^ obj.support(current, 1) ^ obj.support(current, 2)
    assert obj.even(w) and w == repair['fourth_coordinate']
    palette = [4, 5, 6, 15, 8]
    cover = repair['cover_pairs']
    assert len(cover) == obj.m and all(0 <= x < 32 and x.bit_count() == 2 for x in cover)
    for e, value in enumerate(cover):
        i, j = [i for i in range(5) if value >> i & 1]
        assert palette[i] ^ palette[j] == transformed[e] + 8*((w >> e) & 1)
    assert all(obj.even(mask(e for e, value in enumerate(cover) if value >> layer & 1)) for layer in range(5))
    print('PASS: projected cycle spaces independently recover all six quotient replacement sets.')
    print('PASS: 30 distinct minimum matchings; all 29 nontrivial replacements are suitable.')
    print('PASS: each replacement has a single legal neutral circuit witness.')
    print('PASS: exact fiber/kernel dimensions; 1,408 increment-tagged optimal flows, 1,024 with suitable matchings.')
    print('PASS: shortest neutral matching escape has length 6; the entire size vector is preserved.')
    print('PASS: the 6-edge and 55-edge switches construct a five-layer cover.')
    print('Scope: initial saved flow; global minimum/connectivity inherited from its pinned certificate.')


if __name__ == '__main__':
    main()
