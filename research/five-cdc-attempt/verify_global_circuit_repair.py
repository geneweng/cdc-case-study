#!/usr/bin/env python3
"""Independent standard-library checks for global-circuit repair certificates.

No constructor, SAT solver, or earlier verifier is imported. The general
covering and counting deductions are proved in global-circuit-repair.md.
"""
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]
PORTS = [4, 5, 2, 6]
PAIRS = [sum(1 << a for a in p) for p in itertools.combinations(range(5), 2)]


def components(edges):
    adjacency = {}
    for u, v in edges:
        adjacency.setdefault(u, set()).add(v)
        adjacency.setdefault(v, set()).add(u)
    unseen, result = set(adjacency), []
    while unseen:
        found, pending = set(), [min(unseen)]
        while pending:
            v = pending.pop()
            if v not in found:
                found.add(v)
                pending.extend(adjacency[v]-found)
        unseen -= found
        result.append(found)
    return result


def is_circuit(edges):
    return bool(edges) and all(d == 2 for d in Counter(v for uv in edges for v in uv).values()) and len(components(edges)) == 1


def valid_flow(n, edges, flow):
    assert len(edges) == len(flow) and set(flow) <= set(range(1, 8))
    degree, total = [0]*n, [0]*n
    for (u, v), a in zip(edges, flow):
        assert 0 <= u < n and 0 <= v < n and u != v
        for w in (u, v):
            degree[w] += 1
            total[w] ^= a
    assert degree == [3]*n and total == [0]*n


def valid_cover(n, edges, cover, flow, normal):
    assert len(cover) == len(edges) and set(cover) <= set('0123456789')
    degrees = [[0]*5 for _ in range(n)]
    for (u, v), digit, a in zip(edges, cover, flow):
        pair = PAIRS[int(digit)]
        assert bool(pair & 1) == bool((a & normal).bit_count() % 2)
        for w in (u, v):
            for label in range(5):
                degrees[w][label] += pair >> label & 1
    assert all(d in (0, 2) for row in degrees for d in row)


def switch(edges, flow, chosen, increment):
    assert len(chosen) == len(set(chosen)) and increment in range(1, 8)
    assert is_circuit([edges[e] for e in chosen])
    result = flow.copy()
    for e in chosen:
        assert result[e] != increment
        result[e] ^= increment
    return result


def factor_obstructions():
    pe = ([(i, (i+1) % 5) for i in range(5)]+[(i, i+5) for i in range(5)]
          + [(i+5, (i+2) % 5+5) for i in range(5)])
    local_sources = [2, 3, 7, 8, 9, 10, 11, 12, 13, 14, 4, 5, 1, 6]
    # Girth >= 5 is one premise of the dimension-independent Petersen lemma.
    for length in (3, 4):
        assert not any(is_circuit([pe[e] for e in chosen])
                       for chosen in itertools.combinations(range(15), length))
    types = {}
    for chosen in itertools.combinations(range(15), 5):
        if sorted(v for e in chosen for v in pe[e]) != list(range(10)):
            continue
        factor = set(range(15))-set(chosen)
        cc = components([pe[e] for e in factor])
        assert sorted(map(len, cc)) == [5, 5]
        assert all((pe[e][0] in cc[0]) != (pe[e][1] in cc[0]) for e in chosen)
        # Residual circuits alternate factor/matching edges, hence have length
        # divisible by 4. Only 8 fits the girth/order bounds; 8 does not divide 20.
        assert [i for i in range(5, 11) if i % 4 == 0] == [8] and 20 % 8
        mask = sum(1 << i for i, e in enumerate(local_sources) if e in factor)
        bits = [(mask >> (10+i)) & 1 for i in range(4)]
        if 0 in factor:
            assert sum(bits[:2]) == sum(bits[2:]) == 1
            types[mask] = 'W'
        else:
            assert bits == [1, 1, 1, 1]
            types[mask] = 'Z'
    assert types == {15609: 'Z', 16270: 'Z', 6115: 'W', 6782: 'W', 10045: 'W', 10711: 'W'}
    return types


def old_family_edges(k):
    e = {(k+i, k+(i+1) % k) for i in range(k)} | {(i, k+i) for i in range(k)}
    for i in range(k):
        b = {v: 2*k+8*i+v-2 for v in range(2, 10)}
        e.update((b[x], b[y]) for x, y in INTERNAL)
        u, w = 10*k+2*i, 10*k+2*i+1
        nu, nw = 10*k+2*((i+1) % k), 10*k+2*((i+1) % k)+1
        e.update([(i, u), (i, w), (u, b[2]), (w, b[6]), (b[4], nu), (b[5], nw)])
    return {tuple(sorted(uv)) for uv in e}


def audit_local_geometry():
    adjacency = {v: set() for v in range(2, 10)}
    for x, y in INTERNAL:
        adjacency[x].add(y)
        adjacency[y].add(x)
    for p in PORTS:
        distance, queue = {p: 0}, deque([p])
        while queue:
            v = queue.popleft()
            for w in adjacency[v]-distance.keys():
                distance[w] = distance[v]+1
                queue.append(w)
        assert all(distance[q] >= 2 for q in PORTS if q != p)
    assert all(not is_circuit(list(chosen)) for size in (3, 4)
               for chosen in itertools.combinations(INTERNAL, size))


def verify_periodic(data, source, types):
    base = source['examples'][0]
    e0 = [tuple(e) for e in data['seed_edges']]
    assert e0 == [tuple(e) for e in base['edges']]
    voltage = data['edge_voltages']
    assert voltage == [int(e in (5, 106, 107)) for e in range(108)]
    walk, circuit = data['seed_circuit_vertices'], data['seed_circuit_edges']
    assert walk[0] == walk[-1] and len(set(walk[:-1])) == len(circuit) == 13
    winding = 0
    for e, x, y in zip(circuit, walk, walk[1:]):
        assert set(e0[e]) == {x, y}
        winding += voltage[e] if e0[e] == (x, y) else -voltage[e]
    assert winding == data['seed_winding'] == 1
    for row in data['periodic_repairs']:
        m, n, k = row['repetitions'], row['vertices'], 6*row['repetitions']
        assert m >= 1 and n == 72*m
        # Build a cyclic cover from edge incidences; compare it to the earlier
        # family using an explicit vertex isomorphism, not saved graph claims.
        edges = []
        for eid in range(108*m):
            s, e = divmod(eid, 108)
            u, v = e0[e]
            edges.append((72*s+u, 72*((s+voltage[e]) % m)+v))

        def old_vertex(v):
            s, x = divmod(v, 72)
            if x < 6:
                return 6*s+x
            if x < 12:
                return k+6*s+x-6
            if x < 60:
                i, j = divmod(x-12, 8)
                return 2*k+8*(6*s+i)+j
            i, j = divmod(x-60, 2)
            return 10*k+2*(6*s+i)+j
        assert len({old_vertex(v) for v in range(n)}) == n
        assert {tuple(sorted(map(old_vertex, uv))) for uv in edges} == old_family_edges(k)
        assert len(set(tuple(sorted(uv)) for uv in edges)) == 108*m
        for v in range(n):
            star = [e % 108 for e, uv in enumerate(edges) if v in uv]
            assert sorted(star) == [e for e, uv in enumerate(e0) if v % 72 in uv]
        initial = list(map(int, row['initial_flow_word']))
        assert initial == base['flow']*m
        valid_flow(n, edges, initial)
        chosen = row['switch_edges_in_order']
        assert set(chosen) == {108*s+e for s in range(m) for e in circuit}
        assert len(chosen) == 13*m and row['increment'] == row['normal'] == 1
        changed = switch(edges, initial, chosen, 1)
        valid_flow(n, edges, changed)
        assert changed == list(map(int, row['repaired_flow_word']))
        assert row['cover_word'] == data['seed_cover_word']*m
        valid_cover(n, edges, row['cover_word'], changed, 1)
        assert sum(a & 1 for a in changed) == row['support_size'] == 54*m
        assert row['winding_lift_component_sizes'] == [13*m]
        local = [108*s+12+j for s in range(m) for j in (0, 1, 2, 4, 7)]
        assert sorted(map(len, components([edges[e] for e in local]))) == row['local_pentagon_lift_component_sizes'] == [5]*m
        # Independently check the m-pentagon upper bound used for L=5,6,7.
        short_repair = initial.copy()
        for s in range(m):
            short_repair = switch(edges, short_repair,
                                  [108*s+12+j for j in (0, 1, 2, 4, 7)], 4)
            valid_flow(n, edges, short_repair)
        assert short_repair == source['one_switch_escape']['flow']*m
        valid_cover(n, edges, source['one_switch_escape']['cover_word']*m, short_repair, 4)
        piece_edges = {(s, i): [108*s+e for e in b['edge_representatives']]
                       for s in range(m) for i, b in enumerate(base['blocks'])}
        all_local_edges = [e for es in piece_edges.values() for e in es]
        assert len(all_local_edges) == len(set(all_local_edges))
        # Each final normal retains m vertex-disjoint obstructing pairs before
        # any repair. This supplies the counting argument for bounded lengths.
        assert [rec['normal'] for rec in row['disjoint_obstructions']] == list(range(1, 8))
        for rec in row['disjoint_obstructions']:
            normal = rec['normal']
            pairs = rec['piece_pairs']
            assert len(pairs) == m and len({tuple(b) for pair in pairs for b in pair}) == 2*m
            for left, right in pairs:
                ls, li = left
                rs, ri = right
                assert (6*rs+ri) == (6*ls+li+1) % k
                for f in ([initial, changed] if normal != 1 else [initial]):
                    names = []
                    for b in (left, right):
                        mask = sum(1 << j for j, e in enumerate(piece_edges[tuple(b)]) if (f[e] & normal).bit_count() % 2)
                        names.append(types.get(mask))
                    assert 'Z' in names and set(names) <= {'Z', 'W'}
        assert row['unrestricted_repair_distance'] == 1
        assert row['repair_distance_for_length_limits_5_6_7'] == m
        print(f'm={m}: one connected {13*m}-edge switch, {54*m}-edge cover layer, seven initial and six remaining coordinate obstructions.', flush=True)


def verify_necklace(row):
    q, n = row['pieces'], row['vertices']
    assert q >= 3 and n == 8*q
    edges = [tuple(e) for e in row['edges']]
    assert len(edges) == 12*q and len(set(tuple(sorted(e)) for e in edges)) == 12*q
    for i in range(q):
        assert edges[10*i:10*i+10] == [(8*i+x-2, 8*i+y-2) for x, y in INTERNAL]
        assert edges[10*q+2*i:10*q+2*i+2] == [(8*i+2, 8*((i+1) % q)), (8*i+3, 8*((i+1) % q)+4)]
    local = list(map(int, row['blocked_local_word']))
    assert local == list(map(int, '23312221331111'))
    cut_side = set(row['separating_vertex_set'])
    cut = [e for e, (u, v) in enumerate(INTERNAL) if (u in cut_side) != (v in cut_side)]
    assert cut == row['separating_local_edges'] == [0, 4, 5, 6]
    assert all(local[e] == row['blocked_increment'] == 2 for e in cut)
    assert row['selected_ports'] == [0, 2] and PORTS[0] in cut_side and PORTS[2] not in cut_side
    assert local[10:] == [1]*4
    initial = list(map(int, row['initial_flow_word']))
    assert initial == local[:10]*q+[1]*(2*q)
    valid_flow(n, edges, initial)
    current = initial.copy()
    assert len(row['preparations']) == q
    for i, move in enumerate(row['preparations']):
        assert move['piece'] == i and move['increment'] == 4
        assert len(move['edges']) == 5 and all(10*i <= e < 10*i+10 for e in move['edges'])
        current = switch(edges, current, move['edges'], 4)
        valid_flow(n, edges, current)
    assert current == list(map(int, row['prepared_flow_word']))
    assert current[10*q:] == initial[10*q:]
    assert row['quotient_circuit'] == [[i, (i+1) % q] for i in range(q)]
    assert is_circuit([tuple(e) for e in row['quotient_circuit']])
    assert row['quotient_increment'] == 2
    for i, chosen in enumerate(row['internal_paths']):
        assert chosen == [10*i+1, 10*i]
        assert all(current[e] != 2 for e in chosen)
    chosen = row['lifted_circuit_edges']
    assert len(chosen) == 3*q
    assert set(chosen) == {e for path in row['internal_paths'] for e in path} | {10*q+2*i for i in range(q)}
    current = switch(edges, current, chosen, 2)
    valid_flow(n, edges, current)
    assert current == list(map(int, row['final_flow_word']))
    assert current[10*q:] == [3, 1]*q
    assert row['internal_preparation_steps'] == q and row['total_steps_in_displayed_lift'] == q+1
    print(f'q={q}: every selected port pair initially separated by value-2 edges; {q} internal pentagon preparations plus one {3*q}-edge switch lift the quotient move.', flush=True)


def main():
    data = json.loads((HERE / 'global_circuit_repair.json').read_text())
    source_path = HERE / data['source_certificate']
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == data['source_sha256']
    source = json.loads(source_path.read_text())
    types = factor_obstructions()
    audit_local_geometry()
    verify_periodic(data, source, types)
    for row in data['simultaneous_lifting_examples']:
        verify_necklace(row)
    print('All certificates passed. Infinite-family, bounded-length, and simultaneous-lifting conclusions use the accompanying proofs.')


if __name__ == '__main__':
    main()
