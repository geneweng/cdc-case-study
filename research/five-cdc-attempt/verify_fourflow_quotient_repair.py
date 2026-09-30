#!/usr/bin/env python3
"""Independent structural, flow, cover, and switch certificate checks.

Imports no constructor. General two-switch sufficiency uses the preceding
joint-boundary theorem and its separate exhaustive verifier.
"""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
E = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
     (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]
PORTS = [4, 5, 2, 6]
Q = [sum(1 << a for a in p) for p in itertools.combinations(range(5), 2)]


def word(values):
    return ''.join(map(str, values))


def support(values, normal=1):
    return sum(1 << e for e, a in enumerate(values) if (a & normal).bit_count() % 2)


def incidence(n, edges):
    stars = [[] for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        assert 0 <= u < n and 0 <= v < n
        stars[u].append(e)
        stars[v].append(e)
    return stars


def flow_ok(n, edges, values, maximum=7, cubic=False):
    assert len(values) == len(edges) and all(1 <= a <= maximum for a in values)
    stars = incidence(n, edges)
    for star in stars:
        total = 0
        for e in star:
            total ^= values[e]
        assert total == 0
        if cubic:
            assert len(star) == 3


def cover_ok(n, edges, cw, first):
    assert len(cw) == len(edges)
    pairs = [Q[int(c)] for c in cw]
    assert support(pairs) == first
    for star in incidence(n, edges):
        for label in range(5):
            assert sum(pairs[e] >> label & 1 for e in star) % 2 == 0


def circuit(edges):
    degree = Counter(v for uv in edges for v in uv)
    if not degree or set(degree.values()) != {2}:
        return False
    seen, todo = set(), [next(iter(degree))]
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
    return len(seen) == len(degree)


def enumerate_local(boundary, alphabet):
    # Independent elimination on one fixed spanning tree of the internal graph.
    tree = [0, 1, 2, 3, 4, 5, 6]
    adj = defaultdict(list)
    for e in tree:
        u, v = E[e]
        adj[u].append((v, e))
        adj[v].append((u, e))
    order, parent = [2], {2: None}
    for v in order:
        for u, e in adj[v]:
            if u not in parent:
                parent[u] = (v, e)
                order.append(u)
    assert len(order) == 8
    result = []
    for free in itertools.product(alphabet, repeat=3):
        f, demands = [0]*10, [0]*10
        for v, a in zip(PORTS, boundary):
            demands[v] ^= a
        for e, a in zip((7, 8, 9), free):
            f[e] = a
            for v in E[e]:
                demands[v] ^= a
        for v in reversed(order[1:]):
            u, e = parent[v]
            f[e] = demands[v]
            demands[u] ^= f[e]
        if not demands[2] and all(a in alphabet for a in f):
            result.append(tuple(f)+tuple(boundary))
    return result


def check_junctions(saved):
    for kind in ('blowup', 'semi'):
        rows = []
        for a, b, c, d in itertools.product((1, 2, 3), repeat=4):
            x, y, r = a ^ c, b ^ d, a ^ b ^ c ^ d
            if not r:
                continue
            if kind == 'blowup' and x and y:
                rows.append([a ^ b, c ^ d, a, b, c, d, x, y, r])
            if kind == 'semi' and b == d:
                rows.append([a ^ b, c ^ d, a, b, c, d, r])
        assert sorted(rows) == saved[kind]
        counts = Counter(tuple(row[:2]) for row in rows)
        assert set(counts) == set(itertools.permutations(range(4), 2))
        assert all(n == (2 if kind == 'blowup' or 0 in p else 1) for p, n in counts.items())
        assert len(rows) == (24 if kind == 'blowup' else 18)
    # Verify the symmetric-difference cover rule edge by edge, independently.
    for a in (1, 2, 3):
        original = [(a & l).bit_count() % 2 for l in (1, 2, 3)]
        assert sum(original) == 2
        for bit in (0, 1):
            resulting = [bit]+[b ^ bit for b in original]
            assert sum(resulting) == 2
    print('Verified both complete four-flow junction tables and the four-layer cover identity.', flush=True)


def check_structure(g):
    n, base, cycles, kind = g['base_vertices'], g['base_edges'], g['selected_cycles'], g['construction']
    assert all(len(star) == 3 for star in incidence(n, base))
    assert all(len(c) >= 3 and len(c) == len(set(c)) for c in cycles)
    assert len(set(v for c in cycles for v in c)) == sum(map(len, cycles))
    q = sum(map(len, cycles))
    removed = {tuple(sorted((c[i], c[(i+1) % len(c)]))) for c in cycles for i in range(len(c))}
    assert removed <= {tuple(sorted(e)) for e in base}
    outside = [e for e, uv in enumerate(base) if tuple(sorted(uv)) not in removed]
    assert outside == g['outside_base_edge_ids']
    edges = [tuple(e) for e in g['edges']]
    assert edges[:len(outside)] == [tuple(base[e]) for e in outside]
    assert g['pieces'] == q and len(g['blocks']) == len(g['junctions']) == q
    owner = list(range(n))+[n+i for i in range(q) for _ in range(8)]
    if kind == 'blowup':
        owner += list(range(n+q, n+3*q))
    assert owner == g['vertex_map'] and len(owner) == g['vertices']
    internal = set()
    for i, b in enumerate(g['blocks']):
        assert b['vertices'] == list(range(n+8*i, n+8*i+8))
        ids = b['edge_representatives']
        assert ids[:10] == list(range(len(outside)+10*i, len(outside)+10*i+10))
        assert [edges[e] for e in ids[:10]] == [(n+8*i+u-2, n+8*i+v-2) for u, v in E]
        internal.update(ids[:10])
        for v, e in zip(PORTS, ids[10:]):
            assert n+8*i+v-2 in edges[e]
            assert sum(w in b['vertices'] for w in edges[e]) == 1
    offset = 0
    for cycle in cycles:
        for j, v in enumerate(cycle):
            i, prev = offset+j, offset+(j-1) % len(cycle)
            rec = g['junctions'][i]
            assert [rec['vertex'], rec['left_piece'], rec['right_piece']] == [v, prev, i]
            es = rec['edges']
            assert es[:2] == g['blocks'][prev]['edge_representatives'][10:12]
            assert es[2:4] == g['blocks'][i]['edge_representatives'][12:14]
            ports = [n+8*prev+2, n+8*prev+3, n+8*i, n+8*i+4]
            if kind == 'blowup':
                u, w = n+8*q+2*i, n+8*q+2*i+1
                expected = [(ports[0], u), (ports[1], w), (ports[2], u), (ports[3], w), (u, v), (w, v)]
            else:
                expected = [(ports[0], v), (ports[1], ports[3]), (ports[2], v), (ports[1], ports[3])]
                assert es[1] == es[3]
            assert [edges[e] for e in es[:-1]] == expected
            assert es[-1] < len(outside) and v in edges[es[-1]]
        offset += len(cycle)
    kept = [e for e in range(len(edges)) if e not in internal]
    assert kept == g['kept_edge_ids']
    qe = [(owner[u], owner[v]) for e in kept for u, v in [edges[e]]]
    assert qe == [tuple(e) for e in g['quotient_edges']]
    assert set(owner) == set(range(g['quotient_vertices']))
    assert Counter(map(len, incidence(g['quotient_vertices'], qe))) == {3: n+(2*q if kind == 'blowup' else 0), 4: q}
    contracted_owner = list(range(n))
    for c in cycles:
        for v in c:
            contracted_owner[v] = min(c)
    names = {v: i for i, v in enumerate(sorted(set(contracted_owner)))}
    contracted_owner = [names[v] for v in contracted_owner]
    k = g['contracted_base']
    assert contracted_owner == k['vertex_map'] and k['vertices'] == len(names)
    assert k['edges'] == [[contracted_owner[u], contracted_owner[v]] for e in outside for u, v in [base[e]]]
    kflow = list(map(int, k['four_flow_word']))
    flow_ok(k['vertices'], k['edges'], kflow, maximum=3)
    h = list(map(int, g['quotient_four_flow_word']))
    flow_ok(g['quotient_vertices'], qe, h, maximum=3)
    assert h[:len(outside)] == kflow
    values = dict(zip(kept, h))
    assert len(g['piece_charges']) == q
    for i, b in enumerate(g['blocks']):
        a, b1, c, d = [values[e] for e in b['edge_representatives'][10:]]
        assert a ^ b1 == c ^ d == g['piece_charges'][i]
    return edges, qe, h


def prescribed_word(h, first):
    result = []
    for e, a in enumerate(h):
        labels = [j for j in (1, 2, 3) if (a & j).bit_count() % 2]
        if first >> e & 1:
            labels = [0]+[j for j in (1, 2, 3) if j not in labels]
        result.append(Q.index(sum(1 << j for j in labels)))
    return word(result)


def check_examples(examples, source):
    census_total, repair_total = 0, 0
    for g in examples:
        edges, qe, h = check_structure(g)
        n, qn, kept = g['vertices'], g['quotient_vertices'], g['kept_edge_ids']
        initial = list(map(int, g['initial_flow_word']))
        flow_ok(n, edges, initial, cubic=True)
        if g['initial_flow_source'] == 'earlier_obstructed_family':
            assert g['construction'] == 'blowup' and g['pieces'] % 6 == 0
            k = g['pieces']
            local_words = source['local_flow_words']*(k//6)
            charges = [int(w[10]) ^ int(w[11]) for w in local_words]
            assert initial[:2*k] == charges+[charges[i-1] ^ charges[i] for i in range(k)]
            for b, w in zip(g['blocks'], local_words):
                assert word([initial[e] for e in b['edge_representatives']]) == w
        assert [r['normal'] for r in g['repairs']] == list(range(1, 8))
        for r in g['repairs']:
            normal, f = r['normal'], initial.copy()
            first = support([f[e] for e in kept], normal)
            assert r['quotient_cover_word'] == prescribed_word(h, first)
            assert all(not (Q[int(c)] & 16) for c in r['quotient_cover_word'])
            cover_ok(qn, qe, r['quotient_cover_word'], first)
            touched = Counter()
            for move in r['moves']:
                es, a, block = move['edges'], move['increment'], move['piece']
                assert 0 <= block < g['pieces'] and a in range(1, 8)
                assert len(es) == len(set(es)) == 5
                assert set(es) <= set(g['blocks'][block]['edge_representatives'][:10])
                assert circuit([edges[e] for e in es])
                for e in es:
                    assert f[e] != a
                    f[e] ^= a
                flow_ok(n, edges, f, cubic=True)
                touched[block] += 1
            assert not touched or max(touched.values()) <= 2
            assert word(f) == r['final_flow_word'] and len(r['moves']) <= 2*g['pieces']
            assert all(initial[e] == f[e] for e in kept)
            assert ''.join(r['cover_word'][e] for e in kept) == r['quotient_cover_word']
            cover_ok(n, edges, r['cover_word'], support(f, normal))
            # The otherwise unused fifth label is confined to a disjoint union
            # of one internal circuit per piece (or no circuit there).
            for b in g['blocks']:
                extra = [edges[e] for e in b['edge_representatives'][:10]
                         if Q[int(r['cover_word'][e])] & 16]
                assert not extra or len(extra) in (5, 6, 8) and circuit(extra)
            repair_total += 1
        if 'quotient_support_census' in g:
            c = g['quotient_support_census']
            basis = c['cycle_basis']
            # Distinct even vectors with the full cycle-space dimension certify
            # completeness independently of the constructor's spanning tree.
            assert len(basis) == len(qe)-qn+1
            supports = {0}
            for b in basis:
                assert b not in supports and b < 1 << len(qe)
                assert all(sum(b >> e & 1 for e in star) % 2 == 0 for star in incidence(qn, qe))
                supports |= {s ^ b for s in supports}
            ordered = [0]
            for b in basis:
                ordered += [s ^ b for s in ordered]
            assert set(ordered) == supports and len(ordered) == c['even_supports']
            digest = hashlib.sha256()
            for first in ordered:
                cw = prescribed_word(h, first)
                cover_ok(qn, qe, cw, first)
                digest.update(f'{first} {cw}\n'.encode())
            assert digest.hexdigest() == c['cover_sha256']
            census_total += len(ordered)
        print(g['name'], ': verified quotient four-flow and seven internal coordinate repairs.', flush=True)
    assert len(examples) == 20 and repair_total == 140
    print('Verified', repair_total, 'repairs and', census_total, 'quotient even-subgraph completions.', flush=True)


def check_sharpness(r):
    start = tuple(map(int, r['initial_flow_word']))
    boundary = tuple(Q[int(a)] for a in r['cover_boundary'])
    local_covers = enumerate_local(boundary, Q)
    targets = {support(c) for c in local_covers}
    assert sorted(targets) == r['allowed_cover_supports'] == [5123, 5268]
    assert r['cover_boundary'] == prescribed_word(list(map(int, r['four_flow_boundary'])), support(start[10:]))
    fs = enumerate_local(start[10:], list(range(1, 8)))
    assert start in fs and support(start) not in targets
    neighbors = []
    for f in fs:
        changes = [x ^ y for x, y in zip(start[:10], f[:10])]
        nonzero = set(changes)-{0}
        if len(nonzero) == 1 and circuit([E[e] for e, a in enumerate(changes) if a]):
            neighbors.append(f)
    reachable = {support(f) for f in neighbors}
    assert sorted(reachable) == r['one_step_supports'] and not reachable & targets
    assert len(neighbors) == r['one_step_flow_count']
    f = start
    for move in r['moves']:
        mask, a = move['circuit_mask'], move['increment']
        selected = [E[e] for e in range(10) if mask >> e & 1]
        assert len(selected) == 5 and circuit(selected)
        f = tuple(x ^ a if mask >> e & 1 else x for e, x in enumerate(f))
        assert f in fs
    assert len(r['moves']) == 2 and word(f) == r['final_flow_word']
    cw = tuple(Q[int(c)] for c in r['cover_word'])
    assert cw in local_covers and support(cw) == support(f) == r['final_support']
    print('Verified two switches can be necessary even for a boundary produced by the four-flow cover formula.', flush=True)


def check_failure(rec):
    edges, cycles = rec['base_edges'], rec['selected_cycles']
    assert rec['base_vertices'] == 30 and cycles == [list(range(3*i, 3*i+3)) for i in range(10)]
    assert edges[:30] == [[c[j], c[(j+1) % 3]] for c in cycles for j in range(3)]
    assert [[u//3, v//3] for u, v in edges[30:]] == rec['contracted_edges']
    pe = rec['contracted_edges']
    assert pe == [[i, (i+1) % 5] for i in range(5)]+[[i, i+5] for i in range(5)]+[[i+5, (i+2) % 5+5] for i in range(5)]
    assert all(len(s) == 3 for s in incidence(30, edges))
    used = [set() for _ in range(10)]
    leaves = 0

    def search(at):
        nonlocal leaves
        if at == len(pe):
            leaves += 1
            return
        u, v = pe[at]
        for a in {1, 2, 3}-used[u]-used[v]:
            used[u].add(a)
            used[v].add(a)
            search(at+1)
            used[u].remove(a)
            used[v].remove(a)
    search(0)
    assert leaves == 0
    print('Verified the condition can fail: contraction gives Petersen, whose proper three-edge colorings were exhausted.', flush=True)


def main():
    data = json.loads((HERE / 'fourflow_quotient_repair.json').read_text())
    src = data['source']
    assert hashlib.sha256((HERE / src['file']).read_bytes()).hexdigest() == src['sha256']
    check_junctions(data['junction_tables'])
    check_sharpness(data['local_two_switch_example'])
    check_examples(data['examples'], json.loads((HERE / src['file']).read_text()))
    check_failure(data['four_flow_condition_failure'])
    print('All four-flow quotient certificates passed. The universal statements use the report proofs and the prior joint-extension theorem.')


if __name__ == '__main__':
    main()
