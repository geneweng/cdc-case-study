#!/usr/bin/env python3
"""Independent verification of joint regional extension and flow repairs.

Enumerates cubic-vertex triangles, checks all joint boundary/charge states,
and validates every contraction, circuit switch, flow and cover from incidences.
Imports no constructors or earlier verifiers. Standard library only.
"""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
Q = [sum(1 << i for i in pair) for pair in itertools.combinations(range(5), 2)]
EVEN = {h for h in range(32) if h.bit_count() % 2 == 0}


def xor(values):
    r = 0
    for a in values:
        r ^= a
    return r


def stars(n, edges):
    result = [[] for _ in range(n)]
    for e, uv in enumerate(edges):
        for v in uv:
            assert 0 <= v < n
            result[v].append(e)
    return result


def flow_ok(n, edges, values):
    assert len(values) == len(edges) and all(1 <= a <= 7 for a in values)
    assert all(xor(values[e] for e in star) == 0 for star in stars(n, edges))


def support(values):
    return sum(1 << e for e, a in enumerate(values) if a & 1)


def cover_ok(n, edges, cw, flow):
    assert len(cw) == len(edges) and set(cw) <= set('0123456789')
    pairs = [Q[int(a)] for a in cw]
    assert support(pairs) == support(flow)
    assert all(xor(pairs[e] for e in star) == 0 for star in stars(n, edges))


def circuit(edges):
    degrees = Counter(v for uv in edges for v in uv)
    if not degrees or set(degrees.values()) != {2}:
        return False
    seen, todo = set(), [next(iter(degrees))]
    while todo:
        v = todo.pop()
        if v in seen:
            continue
        seen.add(v)
        for u, w in edges:
            if u == v and w not in seen:
                todo.append(w)
            if w == v and u not in seen:
                todo.append(u)
    return len(seen) == len(degrees)


def apply(n, edges, flow, move, forbidden):
    ids, a = move['edges'], move['increment']
    assert 1 <= a <= 7 and len(ids) == len(set(ids)) and not set(ids) & forbidden
    assert all(0 <= e < len(edges) for e in ids)
    assert circuit([edges[e] for e in ids])
    for e in ids:
        assert flow[e] != a
        flow[e] ^= a
    flow_ok(n, edges, flow)


def junction_assignments(kind, alphabet):
    triangles = [(a, b, c) for a in alphabet for b in alphabet for c in alphabet if a ^ b ^ c == 0]
    by_third = {c: [(a, b) for a, b, d in triangles if c == d] for c in alphabet}
    result = []
    if kind == 'semi':
        for a, c, r in triangles:
            result.extend([a, b, c, b, r] for b in alphabet)
    else:
        for x, y, r in triangles:
            for a, c in by_third[x]:
                for b, d in by_third[y]:
                    result.append([a, b, c, d, x, y, r])
    return result


def check_joint(kind, rows):
    fs = junction_assignments(kind, range(1, 8))
    cs = junction_assignments(kind, Q)
    assert len(fs) == (1512 if kind == 'blowup' else 294)
    assert len(cs) == (2160 if kind == 'blowup' else 600)
    grouped = defaultdict(list)
    for c in cs:
        grouped[tuple(a & 1 for a in c)].append(c)
    realized = set()
    for f in fs:
        for c in grouped[tuple(a & 1 for a in f)]:
            realized.add((f[-1], c[-1], f[0] ^ f[1], c[0] ^ c[1]))
    expected = {(p, r, h, c) for p in range(1, 8) for r in Q for h in range(8) for c in EVEN
                if (p & 1) == (r & 1) and (h & 1) == (c & 1)}
    assert len(rows) == len(expected) == 2176 and realized == expected
    assert {tuple(row[:4]) for row in rows} == expected
    fset, cset = {tuple(f) for f in fs}, {tuple(c) for c in cs}
    for p, r, h, c, fv, cv in rows:
        assert tuple(fv) in fset and tuple(cv) in cset
        assert (fv[-1], cv[-1], fv[0] ^ fv[1], cv[0] ^ cv[1]) == (p, r, h, c)
        assert [a & 1 for a in fv] == [a & 1 for a in cv]
    print(kind, 'all 2176 compatible joint boundary/charge states independently realized.', flush=True)


def check_short_cycles(saved):
    assert [r['cycle_length'] for r in saved] == [2, 3, 4]
    for rec in saved:
        size, hist = rec['cycle_length'], Counter()
        for values in itertools.product(range(1, 8), repeat=size):
            for start in range(size):
                for length in range(1, size//2+1):
                    path_values = [values[(start+i) % size] for i in range(length)]
                    for a in range(1, 8):
                        forbidden = set(values) | {x ^ a for x in path_values}
                        allowed = set(range(8))-forbidden
                        assert len(forbidden) <= size+length < 8 and allowed
                        hist[len(allowed), int(0 in forbidden)] += 1
        assert rec['cases'] == sum(hist.values()) == (7**size)*size*(size//2)*7
        assert rec['allowed_count_preparation_histogram'] == [[*key, n] for key, n in sorted(hist.items())]
    assert sum(r['cases'] for r in saved) == 142345


def check_plan(n, edges, plan, core_count, expected_owner):
    current = dict(enumerate(map(tuple, edges)))
    owner = list(range(n))
    for ids in plan:
        assert 1 <= len(ids) <= 4 and len(ids) == len(set(ids))
        assert set(ids) <= set(current) and all(e >= core_count for e in ids)
        chosen = [current[e] for e in ids]
        assert circuit(chosen)
        vertices = {v for uv in chosen for v in uv}
        root = min(vertices)
        owner = [root if v in vertices else v for v in owner]
        current = {e: tuple(root if v in vertices else v for v in uv)
                   for e, uv in current.items() if e not in ids}
    assert set(current) == set(range(core_count))
    for u in range(n):
        for v in range(n):
            assert (owner[u] == owner[v]) == (expected_owner[u] == expected_owner[v])
    assert [current[e] for e in range(core_count)] == [tuple(owner[v] for v in uv) for uv in edges[:core_count]]


def cap_edges(kind, k):
    edges = [[i, k] for i in range(k)]
    junctions = []
    for i in range(k):
        left, right = k+1+(i-1) % k, k+1+i
        at = len(edges)
        if kind == 'blowup':
            u, w = 2*k+1+2*i, 2*k+2+2*i
            edges += [[left, u], [left, w], [right, u], [right, w], [u, i], [w, i]]
            junctions.append(list(range(at, at+6))+[i])
        else:
            edges += [[left, i], [left, right], [right, i]]
            junctions.append([at, at+1, at+2, at+1, i])
    return edges, junctions


def check_caps(kind, records):
    assert [r['length'] for r in records] == [3, 4, 5, 7, 8, 9, 16, 31, 64]
    for rec in records:
        k, n = rec['length'], rec['vertices']
        edges, junctions = cap_edges(kind, k)
        assert edges == rec['edges'] and n == (4*k+1 if kind == 'blowup' else 2*k+1)
        f, c = list(map(int, rec['flow_word'])), [Q[int(a)] for a in rec['cover_word']]
        flow_ok(n, edges, f)
        cover_ok(n, edges, rec['cover_word'], f)
        assert [f[junctions[0][0]] ^ f[junctions[0][1]], c[junctions[0][0]] ^ c[junctions[0][1]]] == rec['initial_charges']
        owner = [0]*n
        owner[k] = 1
        check_plan(n, edges, rec['contractions'], k, owner)
        expected = {4: k-1, 2: k+2} if kind == 'blowup' else {3: k-2, 2: 3}
        assert Counter(map(len, rec['contractions'])) == expected


def check_repair(rec, previous):
    kind = rec['construction']
    g = next(g for g in previous['cubic_examples'] if g['construction'] == kind)
    assert rec['source_example'] == kind and rec['normal'] == 1
    n, edges = g['vertices'], g['edges']
    qn, qe, kept = g['quotient_vertices'], g['quotient_edges'], g['kept_edge_ids']
    m = len(g['outside_base_edge_ids'])
    assert rec['core_cover_word'] == g['rejected_core_cover_word']
    old_rejection = previous['constructions'][kind]['rejected_octagon']
    assert not old_rejection['survivor_trace'][-1]  # Recomputed by the preceding verifier.
    owner = [0 if v < 8 or v >= 16 else v-7 for v in range(qn)]
    check_plan(qn, qe, rec['contractions'], m, owner)
    qf = [int(g['initial_flow_word'][e]) for e in kept]
    flow_ok(qn, qe, qf)
    for move in rec['quotient_moves']:
        apply(qn, qe, qf, move, set(range(m)))
    assert qf == list(map(int, rec['target_quotient_flow_word']))
    cover_ok(qn, qe, rec['quotient_cover_word'], qf)
    assert rec['quotient_cover_word'][:m] == rec['core_cover_word']
    initial = list(map(int, g['initial_flow_word']))
    f = initial.copy()
    flow_ok(n, edges, f)
    qindex, completed, counts = 0, False, Counter()
    for move in rec['moves']:
        stage = move['kind']
        assert stage in ('piece_preparation', 'lifted_quotient', 'piece_completion')
        if stage == 'piece_completion':
            assert qindex == len(rec['quotient_moves'])
            completed = True
        else:
            assert not completed
        if stage in ('piece_preparation', 'piece_completion'):
            assert len(move['edges']) == 5 and 0 <= move['piece'] < 8
            assert set(move['edges']) <= set(g['blocks'][move['piece']]['edge_representatives'][:10])
            counts[stage, move['piece']] += 1
        else:
            qm = rec['quotient_moves'][qindex]
            assert move['increment'] == qm['increment']
            assert set(move['edges']) & set(kept) == {kept[e] for e in qm['edges']}
            qindex += 1
        apply(n, edges, f, move, set(range(m)))
        assert f[:m] == initial[:m]
    assert qindex == len(rec['quotient_moves'])
    assert max((v for (s, _), v in counts.items() if s == 'piece_completion'), default=0) <= 2
    assert f == list(map(int, rec['final_flow_word']))
    assert [f[e] for e in kept] == qf
    assert support(qf) != g['quotient_support']
    cover_ok(n, edges, rec['cover_word'], f)
    assert ''.join(rec['cover_word'][e] for e in kept) == rec['quotient_cover_word']
    assert rec['cover_word'][:m] == rec['core_cover_word']
    print(kind, n, 'vertices:', len(rec['moves']), 'valid switches preserve all core flow values and realize the formerly rejected core cover.', flush=True)


def main():
    data = json.loads((HERE / 'region_joint_repair.json').read_text())
    for src in data['sources']:
        assert hashlib.sha256((HERE / src['file']).read_bytes()).hexdigest() == src['sha256']
    assert set(data['junctions']) == set(data['caps']) == {'blowup', 'semi'}
    for kind in ('blowup', 'semi'):
        check_joint(kind, data['junctions'][kind])
        check_caps(kind, data['caps'][kind])
    check_short_cycles(data['short_cycle_audit'])
    previous = json.loads((HERE / 'short_cycle_boundary.json').read_text())
    assert [r['construction'] for r in data['repairs']] == ['blowup', 'semi']
    for rec in data['repairs']:
        check_repair(rec, previous)
    print('All 4352 joint states, 142345 short-cycle preparation cases, 18 cap contractions, and both complete regional repairs passed.')
    print('General statements follow from the accompanying gluing and contraction proofs. Fixed-layer completion at length eight is not settled.')


if __name__ == '__main__':
    main()
