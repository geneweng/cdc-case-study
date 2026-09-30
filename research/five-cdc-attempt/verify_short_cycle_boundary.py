#!/usr/bin/env python3
"""Independent, solver-free verification of short-cycle boundary certificates.

Rebuilds junction relations from cubic-vertex triangles; searches sets of
charges rather than constructor bitmasks; checks graph incidences and every
flow, cover and switch directly. Imports no constructor or other verifier.
"""
from collections import Counter, defaultdict, deque
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
Q = [sum(1 << i for i in p) for p in itertools.combinations(range(5), 2)]
EVEN = {h for h in range(32) if h.bit_count() % 2 == 0}
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]


def xor(values):
    result = 0
    for v in values:
        result ^= v
    return result


def stars(n, edges):
    result = [[] for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        assert 0 <= u < n and 0 <= v < n and u != v
        result[u].append(e)
        result[v].append(e)
    return result


def support(values):
    return sum(1 << e for e, a in enumerate(values) if a & 1)


def flow_ok(n, edges, values, maximum=7):
    assert len(values) == len(edges) and all(1 <= a <= maximum for a in values)
    assert all(xor(values[e] for e in star) == 0 for star in stars(n, edges))


def cover_ok(n, edges, cw, first):
    assert len(cw) == len(edges) and set(cw) <= set('0123456789')
    values = [Q[int(c)] for c in cw]
    assert support(values) == first
    assert all(xor(values[e] for e in star) == 0 for star in stars(n, edges))


def circuit(edges):
    degrees = Counter(v for uv in edges for v in uv)
    if not degrees or set(degrees.values()) != {2}:
        return False
    reached, todo = set(), [next(iter(degrees))]
    while todo:
        u = todo.pop()
        if u in reached:
            continue
        reached.add(u)
        for v, w in edges:
            if v == u and w not in reached:
                todo.append(w)
            if w == u and v not in reached:
                todo.append(v)
    return len(reached) == len(degrees)


def switch(n, edges, flow, move):
    ids, a = move['edges'], move['increment']
    assert len(ids) == len(set(ids)) and 1 <= a <= 7
    assert circuit([edges[e] for e in ids])
    for e in ids:
        assert flow[e] != a
        flow[e] ^= a
    flow_ok(n, edges, flow)


def relation(kind, saved):
    triangles = [(a, b, c) for a, b, c in itertools.product(Q, repeat=3) if a ^ b ^ c == 0]
    assert len(triangles) == 60
    split = {c: [(a, b) for a, b, r in triangles if r == c] for c in Q}
    assignments = []
    if kind == 'semi':
        for a, c, r in triangles:
            assignments.extend([a, b, c, b, r] for b in Q)
    else:
        for x, y, r in triangles:
            for a, c in split[x]:
                for b, d in split[y]:
                    assignments.append([a, b, c, d, x, y, r])
    table = defaultdict(set)
    for values in assignments:
        a, b, c, d = values[:4]
        z = sum((v & 1) << j for j, v in enumerate(values[:4]))
        table[values[-1], z].add(a ^ b)
    expected_keys = {(r, z) for r in Q for z in range(16)
                     if (z.bit_count() % 2 == (r & 1))
                     and (kind == 'blowup' or (z >> 1 & 1) == (z >> 3 & 1))}
    assert set(table) == expected_keys
    assert len(assignments) == saved['junction_assignments'] == (2160 if kind == 'blowup' else 600)
    assert len(table) == saved['local_key_count'] == (80 if kind == 'blowup' else 40)
    assert sorted(Counter(map(len, table.values())).items()) == [tuple(x) for x in saved['domain_size_histogram']]
    assert len(saved['local_table']) == len(table)
    assert {(row['r'], row['z']) for row in saved['local_table']} == expected_keys
    valid = {tuple(row) for row in assignments}
    for row in saved['local_table']:
        r, z = row['r'], row['z']
        assert [h for h, _ in row['witnesses']] == sorted(table[r, z])
        for h, values in row['witnesses']:
            assert tuple(values) in valid and values[-1] == r and values[0] ^ values[1] == h
            assert sum((v & 1) << j for j, v in enumerate(values[:4])) == z
    return table


def parity(z):
    return (z & 1) ^ (z >> 1 & 1)


def filter_word(table, letters):
    p = parity(letters[0][1])
    allowed = {h for h in EVEN if h & 1 == p}
    prefix, trace = 0, [sorted(allowed)]
    for r, z in letters:
        assert (r, z) in table and parity(z) == p ^ (prefix & 1)
        allowed = {h for h in allowed if h ^ prefix in table[r, z]}
        prefix ^= r
        trace.append(sorted(allowed))
    assert prefix == 0
    return trace


def check_automaton(table, audit):
    p = audit['initial_parity']
    start = (0, frozenset(h for h in EVEN if h & 1 == p))
    distance, queue = {start: 0}, deque([start])
    while queue:
        prefix, allowed = queue.popleft()
        for (r, z), domain in table.items():
            if parity(z) != p ^ (prefix & 1):
                continue
            following = (prefix ^ r, frozenset(h for h in allowed if h ^ prefix in domain))
            if following not in distance:
                distance[following] = distance[prefix, allowed]+1
                queue.append(following)
    assert len(distance) == audit['reachable_states'] == 16*256
    hist = sorted(Counter(distance.values()).items())
    assert hist == [tuple(x) for x in audit['distance_histogram']]
    shortest = [min(d for (r, allowed), d in distance.items() if r == 0 and len(allowed) == n)
                for n in range(9)]
    assert shortest == audit['shortest_closed_by_survivor_count']
    assert shortest == ([8, 7, 6, 5, 4, 3, 2, 2, 0] if p == 0 else [9, 8, 7, 6, 5, 4, 3, 2, 0])
    records = sorted((r, sorted(allowed), d) for (r, allowed), d in distance.items())
    digest = hashlib.sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest()
    assert digest == audit['distance_sha256']
    assert len(audit['shortest_rejected_word']) == shortest[0]
    assert not filter_word(table, audit['shortest_rejected_word'])[-1]


def cap_edges(kind, k):
    edges = [[i, k] for i in range(k)]
    junctions = []
    for i in range(k):
        left, right = k+1+(i-1) % k, k+1+i
        start = len(edges)
        if kind == 'blowup':
            u, w = 2*k+1+2*i, 2*k+2+2*i
            edges += [[left, u], [left, w], [right, u], [right, w], [u, i], [w, i]]
            junctions.append(list(range(start, start+6))+[i])
        else:
            edges += [[left, i], [left, right], [right, i]]
            junctions.append([start, start+1, start+2, start+1, i])
    return edges, junctions


def check_letters_on_graph(kind, letters, junctions, first):
    for ids, (r, z) in zip(junctions, letters):
        bits = [first >> e & 1 for e in ids]
        assert bits[-1] == r & 1
        assert sum(bits[i] << i for i in range(4)) == z
        if kind == 'blowup':
            assert bits[4] == bits[0] ^ bits[2] and bits[5] == bits[1] ^ bits[3]
        else:
            assert bits[1] == bits[3]


def check_cap(kind, table, rec):
    k, n, first = rec['length'], rec['vertices'], rec['support']
    assert len(rec['letters']) == k
    edges, junctions = cap_edges(kind, k)
    assert n == (4*k+1 if kind == 'blowup' else 2*k+1)
    assert edges == rec['edges'] and len(edges) == (7*k if kind == 'blowup' else 4*k)
    assert 0 <= first < 1 << len(edges)
    assert all(sum(first >> e & 1 for e in star) % 2 == 0 for star in stars(n, edges))
    check_letters_on_graph(kind, rec['letters'], junctions, first)
    trace = filter_word(table, rec['letters'])
    assert trace == rec['survivor_trace']
    if trace[-1]:
        cover_ok(n, edges, rec['cover_word'], first)
        assert [Q[int(c)] for c in rec['cover_word'][:k]] == [r for r, _ in rec['letters']]
    else:
        assert rec['cover_word'] is None
        components = []
        unused = {e for e in range(len(edges)) if first >> e & 1}
        while unused:
            selected = {min(unused)}
            vertices = set(edges[min(unused)])
            while True:
                following = {e for e in unused if vertices.intersection(edges[e])}
                if following <= selected:
                    break
                selected |= following
                vertices.update(v for e in selected for v in edges[e])
            assert circuit([edges[e] for e in selected])
            components.append(len(selected))
            unused -= selected
        assert sorted(components) == ([4]*8 if kind == 'blowup' else [3]*4)


def check_cubic(g, table):
    kind, base_n, q = g['construction'], 16, 8
    perm = [0, 1, 5, 2, 3, 7, 4, 6]
    base = [[off+i, off+(i+1) % 8] for off in (0, 8) for i in range(8)]
    base += [[i, 8+perm.index(i)] for i in range(8)]
    assert g['base_vertices'] == base_n and g['base_edges'] == base
    assert g['selected_cycles'] == [list(range(8))] and g['pieces'] == q
    assert g['outside_base_edge_ids'] == list(range(8, 24))
    expected = base[8:]
    for i in range(q):
        expected += [[16+8*i+u-2, 16+8*i+v-2] for u, v in INTERNAL]
    assert len(g['blocks']) == len(g['junctions']) == 8
    expected_reps = [list(range(16+10*i, 26+10*i))+[None]*4 for i in range(8)]
    for i, junction in enumerate(g['junctions']):
        prev = (i-1) % 8
        assert [junction['vertex'], junction['left_piece'], junction['right_piece']] == [i, prev, i]
        a, b, c, d = [16+8*prev+2, 16+8*prev+3, 16+8*i, 16+8*i+4]
        start = len(expected)
        if kind == 'blowup':
            u, w = 80+2*i, 81+2*i
            expected += [[a, u], [b, w], [c, u], [d, w], [u, i], [w, i]]
            ids = list(range(start, start+6))+[8+i]
        else:
            expected += [[a, i], [b, d], [c, i]]
            ids = [start, start+1, start+2, start+1, 8+i]
        assert ids == junction['edges']
        expected_reps[prev][10:12] = ids[:2]
        expected_reps[i][12:14] = ids[2:4]
    for i, block in enumerate(g['blocks']):
        assert block['vertices'] == list(range(16+8*i, 24+8*i))
        assert block['edge_representatives'] == expected_reps[i]
    n, edges = g['vertices'], g['edges']
    assert edges == expected and n == (96 if kind == 'blowup' else 80)
    assert len(set(tuple(sorted(e)) for e in edges)) == len(edges)
    assert set(map(len, stars(n, edges))) == {3}
    owner = list(range(16))+[16+i for i in range(8) for _ in range(8)]
    if kind == 'blowup':
        owner += list(range(24, 40))
    kept = list(range(16))+list(range(96, len(edges)))
    qe = [[owner[u], owner[v]] for e in kept for u, v in [edges[e]]]
    assert owner == g['vertex_map'] and kept == g['kept_edge_ids'] and qe == g['quotient_edges']
    qn = max(owner)+1
    assert qn == g['quotient_vertices']
    core_owner = [0]*8+list(range(1, 9))
    core = g['contracted_base']
    assert core['vertices'] == 9 and core['vertex_map'] == core_owner
    assert core['edges'] == [[core_owner[u], core_owner[v]] for u, v in base[8:]]
    cover_ok(9, core['edges'], g['rejected_core_cover_word'], 0)
    assert [Q[int(c)] for c in g['rejected_core_cover_word'][8:]] == [r for r, _ in g['rejected_letters']]
    assert not filter_word(table, g['rejected_letters'])[-1]
    four = list(map(int, g['quotient_four_flow_word']))
    flow_ok(qn, qe, four, 3)
    flow_ok(9, core['edges'], list(map(int, core['four_flow_word'])), 3)
    assert four[:16] == list(map(int, core['four_flow_word']))
    f = list(map(int, g['initial_flow_word']))
    initial = f.copy()
    flow_ok(n, edges, f)
    first = support([f[e] for e in kept])
    assert first == g['quotient_support'] and first & ((1 << 16)-1) == 0
    assert [f[e] for e in kept] == [2*a+(first >> i & 1) for i, a in enumerate(four)]
    qids = {e: i for i, e in enumerate(kept)}
    js = [[qids[e] for e in j['edges']] for j in g['junctions']]
    check_letters_on_graph(kind, g['rejected_letters'], js, first)
    result = g['alternative_completion']
    assert result['normal'] == 1
    cover_ok(qn, qe, result['quotient_cover_word'], first)
    assert result['quotient_cover_word'][:16] != g['rejected_core_cover_word']
    cover_ok(9, core['edges'], result['quotient_cover_word'][:16], 0)
    touched = Counter()
    for move in result['moves']:
        assert 0 <= move['piece'] < 8 and len(move['edges']) == 5
        assert set(move['edges']) <= set(g['blocks'][move['piece']]['edge_representatives'][:10])
        touched[move['piece']] += 1
        switch(n, edges, f, move)
    assert max(touched.values(), default=0) <= 2 and len(result['moves']) <= 16
    assert f == list(map(int, result['final_flow_word']))
    assert all(f[e] == initial[e] for e in kept)
    cover_ok(n, edges, result['cover_word'], support(f))
    assert ''.join(result['cover_word'][e] for e in kept) == result['quotient_cover_word']
    print(kind, n, 'vertices: rejected specified core cover; alternative completion verified with',
          len(result['moves']), 'internal pentagons.', flush=True)


def check_square(rec):
    edges, _ = cap_edges('semi', 4)
    assert edges == rec['edges'] and rec['vertices'] == 9 and rec['cap_vertex'] == 4
    f = list(map(int, rec['flow_word']))
    flow_ok(9, edges, f)
    assert rec['core_edges'] == [0, 1, 2, 3] and rec['selected_core_edges'] == [0, 2]
    a = rec['increment']
    assert a == 2 and f[:4] == [1]*4
    # The selected two parallel edges are a valid circuit in the two-vertex core.
    flow_ok(2, [[0, 1]]*4, f[:4])
    components, unseen = [], set(range(9))-{4}
    while unseen:
        found, todo = set(), [min(unseen)]
        while todo:
            u = todo.pop()
            if u in found:
                continue
            found.add(u)
            for e, (v, w) in enumerate(edges):
                if e < 4 or f[e] == a:
                    continue
                if v == u and w not in found:
                    todo.append(w)
                if w == u and v not in found:
                    todo.append(v)
        components.append(sorted(found & set(range(4))))
        unseen -= found
    assert components == rec['initial_port_components_avoiding_increment'] == [[0, 1], [2, 3]]
    assert set(rec['preparation']['edges']).isdisjoint(range(4))
    switch(9, edges, f, rec['preparation'])
    assert f == list(map(int, rec['prepared_flow_word']))
    assert set(rec['lifted_switch']['edges']) & set(range(4)) == {0, 2}
    assert rec['lifted_switch']['increment'] == a
    switch(9, edges, f, rec['lifted_switch'])
    assert f == list(map(int, rec['final_flow_word']))
    assert rec['minimum_internal_preparations_for_this_lift'] == 1


def main():
    data = json.loads((HERE / 'short_cycle_boundary.json').read_text())
    for src in data['sources']:
        assert hashlib.sha256((HERE / src['file']).read_bytes()).hexdigest() == src['sha256']
    tables = {}
    assert set(data['constructions']) == {'blowup', 'semi'}
    for kind, saved in data['constructions'].items():
        table = tables[kind] = relation(kind, saved)
        assert [a['initial_parity'] for a in saved['automata']] == [0, 1]
        for audit in saved['automata']:
            check_automaton(table, audit)
        assert [rec['length'] for rec in saved['positive_caps']] == list(range(3, 8))*2
        for rec in saved['positive_caps']:
            check_cap(kind, table, rec)
        bad = saved['rejected_octagon']
        assert bad['length'] == 8 and not bad['survivor_trace'][-1]
        assert [r for r, z in bad['letters']] == [6, 10, 6, 18, 6, 10, 6, 18]
        assert [z for r, z in bad['letters']] == ([3]*8 if kind == 'blowup' else [0, 15]*4)
        check_cap(kind, table, bad)
        print(kind, 'junction relation and both 4096-state automata rebuilt; minimum rejecting length 8.', flush=True)
    assert [g['construction'] for g in data['cubic_examples']] == ['blowup', 'semi']
    for g in data['cubic_examples']:
        assert g['rejected_letters'] == data['constructions'][g['construction']]['rejected_octagon']['letters']
        check_cubic(g, tables[g['construction']])
    check_square(data['square_switch'])
    print('Verified all 16,384 automaton states, 20 positive caps, two octagon obstructions, two cubic repairs, and the square preparation diagnostic.')
    print('The theorem concerns prescribed boundaries; existential equivalence at length 8 and the general 5-CDC conjecture are not settled.')


if __name__ == '__main__':
    main()
