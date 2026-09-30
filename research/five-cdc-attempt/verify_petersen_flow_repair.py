#!/usr/bin/env python3
"""Independent, standard-library audit; imports no research constructor.

Enumerates local flows by assigning chords of a spanning tree, rather than
triples of even masks. Recognizes switches from differences of flow pairs.
"""
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
E = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
     (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]
P = [4, 5, 2, 6]
PAIRS = [sum(1 << v for v in pair) for pair in itertools.combinations(range(5), 2)]


def circuit(edges):
    if not edges:
        return False
    neighbors = {}
    for u, v in edges:
        neighbors.setdefault(u, []).append(v)
        neighbors.setdefault(v, []).append(u)
    if any(len(vs) != 2 for vs in neighbors.values()):
        return False
    seen, todo = set(), [next(iter(neighbors))]
    while todo:
        v = todo.pop()
        if v not in seen:
            seen.add(v)
            todo.extend(neighbors[v])
    return len(seen) == len(neighbors)


def enumerate_fiber(ports):
    parent, order, tree = {2: None}, [2], set()
    for v in order:
        for e, (x, y) in enumerate(E):
            w = y if x == v else x if y == v else None
            if w is not None and w not in parent:
                parent[w] = (v, e)
                order.append(w)
                tree.add(e)
    chords = sorted(set(range(10))-tree)
    assert len(chords) == 3
    answer = []
    for values in itertools.product(range(1, 8), repeat=3):
        f, residual = [0]*10, {v: 0 for v in range(2, 10)}
        for v, a in zip(P, ports):
            residual[v] ^= a
        for e, a in zip(chords, values):
            f[e] = a
            for v in E[e]:
                residual[v] ^= a
        for v in reversed(order[1:]):
            up, e = parent[v]
            f[e] = residual[v]
            residual[up] ^= f[e]
        assert residual[2] == 0
        if all(f):
            answer.append(tuple(f)+ports)
    return sorted(answer)


def adjacency_from_differences(fs, masks):
    all_edges, five_edges = [set() for _ in fs], [set() for _ in fs]
    for i, f in enumerate(fs):
        for j in range(i):
            difference = [a ^ b for a, b in zip(f, fs[j])]
            values = set(difference)-{0}
            if len(values) != 1:
                continue
            mask = sum(1 << e for e, a in enumerate(difference) if a)
            if mask not in masks:
                continue
            all_edges[i].add(j)
            all_edges[j].add(i)
            if mask.bit_count() == 5:
                five_edges[i].add(j)
                five_edges[j].add(i)
    return all_edges, five_edges


def bfs(adjacency, starts):
    d = {i: 0 for i in starts}
    q = deque(d)
    while q:
        v = q.popleft()
        for w in adjacency[v]-d.keys():
            d[w] = d[v]+1
            q.append(w)
    return d


def is_clear(f, forbidden):
    for l in range(1, 8):
        mask = sum(1 << e for e, a in enumerate(f) if (a & l).bit_count() % 2)
        if mask in forbidden:
            return False
    return True


def check_statistics(fs, adjacency, clean, saved):
    histogram = Counter()
    farthest, witness = -1, None
    for i in range(len(fs)):
        d = bfs(adjacency, [i])
        assert len(d) == len(fs)
        histogram.update(d.values())
        for j in sorted(d):
            if d[j] > farthest:
                farthest, witness = d[j], [''.join(map(str, fs[i])), ''.join(map(str, fs[j]))]
    result = {"edges": sum(map(len, adjacency))//2, "diameter": farthest,
              "diameter_witness": witness, "distance_histogram": [list(x) for x in sorted(histogram.items())],
              "distance_to_clear_histogram": [list(x) for x in sorted(Counter(bfs(adjacency, clean).values()).items())]}
    assert result == saved


def factor_types():
    full = ([(i, (i+1) % 5) for i in range(5)]+[(i, i+5) for i in range(5)]
            + [(i+5, (i+2) % 5+5) for i in range(5)])
    source = [2, 3, 7, 8, 9, 10, 11, 12, 13, 14, 4, 5, 1, 6]
    types = {}
    for matching in itertools.combinations(range(15), 5):
        if sorted(v for e in matching for v in full[e]) != list(range(10)):
            continue
        factor = set(range(15))-set(matching)
        adjacency = {v: [] for v in range(10)}
        for e in factor:
            x, y = full[e]
            adjacency[x].append(y)
            adjacency[y].append(x)
        seen, todo = {0}, [0]
        while todo:
            for w in adjacency[todo.pop()]:
                if w not in seen:
                    seen.add(w)
                    todo.append(w)
        assert len(seen) == 5
        assert all((full[e][0] in seen) != (full[e][1] in seen) for e in matching)
        assert all(not circuit([full[e] for e in selected])
                   for size in (3, 4) for selected in itertools.combinations(range(15), size))
        assert (30-10) % 8 != 0
        local = sum(1 << e for e, original in enumerate(source) if original in factor)
        types[local] = 'W' if 0 in factor else 'Z'
    assert {s for s, t in types.items() if t == 'Z'} == {15609, 16270}
    assert {s for s, t in types.items() if t == 'W'} == {6115, 6782, 10045, 10711}
    return types


def check_local(data, types):
    cycles = {mask for mask in range(1, 1024)
              if circuit([E[e] for e in range(10) if mask >> e & 1])}
    assert sorted(cycles) == data['internal_circuit_masks']
    assert Counter(s.bit_count() for s in cycles) == {5: 4, 6: 2, 8: 1}
    maps = []
    for a, b, c in itertools.product(range(1, 8), repeat=3):
        if b == a or c in {a, b, a ^ b}:
            continue
        maps.append([((a if x & 1 else 0) ^ (b if x & 2 else 0) ^ (c if x & 4 else 0)) for x in range(8)])
    assert len(maps) == 168
    boundaries, total, transitions = set(), 0, 0
    for row in data['canonical_fibers']:
        p = tuple(row['boundary'])
        fs = enumerate_fiber(p)
        assert [''.join(map(str, f)) for f in fs] == row['flow_words']
        orbit = {}
        for transform in maps:
            orbit.setdefault(tuple(transform[a] for a in p), transform)
        assert len(orbit) == row['orbit_size'] and not boundaries & orbit.keys()
        boundaries.update(orbit)
        # Enumerate ALL 301 fibers independently; GL(3,2) then transports the
        # checked reconfiguration, support, and preparation statements.
        for ports, transform in orbit.items():
            actual = enumerate_fiber(ports)
            assert actual == sorted(tuple(transform[a] for a in f) for f in fs)
            total += len(actual)
        all_adj, five_adj = adjacency_from_differences(fs, cycles)
        clean = [i for i, f in enumerate(fs) if is_clear(f, types)]
        assert len(clean) == row['clear_states']
        check_statistics(fs, all_adj, clean, row['all_circuits'])
        check_statistics(fs, five_adj, clean, row['pentagons'])
        assert row['all_circuits']['diameter'] == 3 and row['pentagons']['diameter'] == 4
        for f, repair in zip(fs, row['clear_repairs']):
            assert len(repair) <= 2
            for mask, a in repair:
                assert mask in cycles and mask.bit_count() == 5 and a in range(1, 8)
                f = tuple(v ^ a if mask >> e & 1 else v for e, v in enumerate(f))
                assert f in fs
            assert is_clear(f, types)
        assert len(row['clear_repairs']) == len(fs)
        actual_transitions = []
        for p1, p2 in itertools.combinations(range(4), 2):
            # Independent edge-subset recognition of paths of length <= 3.
            paths = []
            for size in range(1, 4):
                for chosen in itertools.combinations(range(10), size):
                    degree = Counter(v for e in chosen for v in E[e])
                    if {v for v, d in degree.items() if d == 1} == {P[p1], P[p2]} and all(d <= 2 for d in degree.values()):
                        paths.append(chosen)
            for a in range(1, 8):
                if a in (p[p1], p[p2]):
                    continue
                ready = [i for i, f in enumerate(fs) if any(all(f[e] != a for e in path) for path in paths)]
                d = bfs(five_adj, ready)
                assert len(d) == len(fs) and max(d.values()) <= 1
                actual_transitions.append({'ports': [p1, p2], 'increment': a,
                                           'preparation_histogram': [list(x) for x in sorted(Counter(d.values()).items())]})
        assert actual_transitions == row['boundary_transitions']
        transitions += len(actual_transitions)*len(orbit)
    expected = {(a, b, c, a ^ b ^ c) for a, b, c in itertools.product(range(1, 8), repeat=3) if a ^ b ^ c}
    assert boundaries == expected and len(boundaries) == data['boundary_count'] == 301
    assert total == data['flow_count'] == 34230
    assert transitions == data['boundary_transition_count'] == 9324
    edges = E+[(v, -1) for v in P]
    even = [s for s in range(1 << 14) if all(sum(s >> e & 1 for e, uv in enumerate(edges) if v in uv) % 2 == 0 for v in range(2, 10))]
    assert even == data['even_masks'] and len(even) == 64
    print('Verified all 34,230 flows / 301 boundaries, both exact diameters, two-step clearing, and 9,324 boundary transitions.', flush=True)


def family_edges(k):
    edges = [(k+i, k+(i+1) % k) for i in range(k)]+[(i, k+i) for i in range(k)]
    for i in range(k):
        edges.extend((2*k+8*i+x-2, 2*k+8*i+y-2) for x, y in E)
    for i in range(k):
        u, w = 10*k+2*i, 10*k+2*i+1
        nu, nw = 10*k+2*((i+1) % k), 10*k+2*((i+1) % k)+1
        edges.extend([(i, u), (i, w), (u, 2*k+8*i), (w, 2*k+8*i+4),
                      (2*k+8*i+2, nu), (2*k+8*i+3, nw)])
    return edges


def check_flow(edges, values, n):
    assert len(values) == len(edges) and all(0 < a < 8 for a in values)
    totals, degrees = [0]*n, [0]*n
    for (u, v), a in zip(edges, values):
        for w in (u, v):
            totals[w] ^= a
            degrees[w] += 1
    assert totals == [0]*n and degrees == [3]*n


def check_contractions(edges, n, sequence, k):
    # Use explicit vertex sets, independently of the constructor's parent map.
    parts = {v: {v} for v in range(n)}
    counts = Counter()
    for chosen in sequence:
        assert len(chosen) == len(set(chosen)) and 2 <= len(chosen) <= 5
        owner = {v: key for key, members in parts.items() for v in members}
        quotient_edges = [(owner[edges[e][0]], owner[edges[e][1]]) for e in chosen]
        assert all(u != v for u, v in quotient_edges) and circuit(quotient_edges)
        vertices = {v for edge in quotient_edges for v in edge}
        merged = set().union(*(parts.pop(v) for v in vertices))
        parts[min(merged)] = merged
        counts[len(chosen)] += 1
    assert len(parts) == 1 and counts == {2: 3*k, 3: k+1, 4: k-1, 5: k}


def check_family(data, types):
    source = HERE / data['source_certificate']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == data['source_sha256']
    seed = json.loads(source.read_text())
    base_edges = family_edges(6)
    assert base_edges == [tuple(e) for e in seed['examples'][0]['edges']]
    for row in data['periodic_repairs']:
        m = row['repetitions']
        k, n = 6*m, 72*m
        edges = family_edges(k)
        assert n == row['vertices'] and len(set(tuple(sorted(e)) for e in edges)) == 108*m
        check_contractions(edges, n, row['contraction_circuit_edge_ids'], k)
        projected_edges = (list(range(6))*m+list(range(6, 12))*m
                           + list(range(12, 72))*m+list(range(72, 108))*m)

        def vertex(v):
            if v < k:
                return v % 6
            if v < 2*k:
                return 6+(v-k) % 6
            if v < 10*k:
                return 12+8*((v-2*k)//8 % 6)+(v-2*k) % 8
            return 60+2*((v-10*k)//2 % 6)+(v-10*k) % 2
        for e, (u, v) in enumerate(edges):
            assert tuple(sorted((vertex(u), vertex(v)))) == tuple(sorted(base_edges[projected_edges[e]]))
        for v in range(n):
            assert sorted(projected_edges[e] for e, uv in enumerate(edges) if v in uv) == sorted(e for e, uv in enumerate(base_edges) if vertex(v) in uv)
        initial = list(map(int, row['initial_flow_word']))
        assert initial == [seed['examples'][0]['flow'][e] for e in projected_edges]
        check_flow(edges, initial, n)
        current, touched = initial.copy(), set()
        assert len(row['switches']) == row['exact_block_internal_repair_distance'] == m
        for move in row['switches']:
            i, chosen = move['block'], move['edges']
            assert i % 6 == 0 and i not in touched
            touched.add(i)
            assert chosen == [2*k+10*i+j for j in (0, 1, 2, 4, 7)] and move['increment'] == 4
            assert circuit([edges[e] for e in chosen])
            for e in chosen:
                current[e] ^= 4
            check_flow(edges, current, n)
        assert current == list(map(int, row['repaired_flow_word']))
        assert current == [seed['one_switch_escape']['flow'][e] for e in projected_edges]
        assert row['cover_word'] == ''.join(seed['one_switch_escape']['cover_word'][e] for e in projected_edges)
        cover = [PAIRS[int(c)] for c in row['cover_word']]
        assert len(cover) == len(edges)
        for v in range(n):
            pairs = [a for uv, a in zip(edges, cover) if v in uv]
            for label in range(5):
                assert sum(a >> label & 1 for a in pairs) in (0, 2)
        assert row['normal'] == 4
        assert [bool(a & 1) for a in cover] == [bool(a & 4) for a in current]
        assert sum(bool(a & 4) for a in current) == 59*m
        assert [r['normal'] for r in row['lower_bound_witnesses']] == list(range(1, 8))
        for rec in row['lower_bound_witnesses']:
            pairs, normal = rec['disjoint_block_pairs'], rec['normal']
            assert len(pairs) == m and len({i for pair in pairs for i in pair}) == 2*m
            for left, right in pairs:
                assert right == (left+1) % k
                names = []
                for i in (left, right):
                    local = list(range(2*k+10*i, 2*k+10*i+10))+[12*k+6*i+j for j in (4, 5, 2, 3)]
                    mask = sum(1 << e for e, global_e in enumerate(local) if (initial[global_e] & normal).bit_count() % 2)
                    names.append(types.get(mask))
                assert 'Z' in names and set(names) <= {'Z', 'W'}
        print(f'Verified m={m}: {n} vertices, {m} disjoint obstructions per coordinate, {m} valid switches, five-layer completion, {6*k} short-cycle contractions.', flush=True)


def main():
    data = json.loads((HERE / 'petersen_flow_repair.json').read_text())
    assert data['internal_edges'] == [list(e) for e in E] and data['port_vertices'] == P
    types = factor_types()
    check_local(data, types)
    check_family(data, types)
    print('All finite certificates passed. Infinite and contraction deductions are stated with their hypotheses in the report.')


if __name__ == '__main__':
    main()
