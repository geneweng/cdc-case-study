#!/usr/bin/env python3
"""Independent verifier for linear regional repair.

Reconstructs junction states from cubic-vertex triangles, recognizes adjacency
from pairwise flow differences, and recomputes all local distances by BFS.
Imports no constructor or previous verifier. Standard library only.
"""
from collections import Counter, defaultdict, deque
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
Q = [sum(1 << a for a in p) for p in itertools.combinations(range(5), 2)]
EVEN = [h for h in range(32) if h.bit_count() % 2 == 0]
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]


def xor(values):
    r = 0
    for a in values:
        r ^= a
    return r


def word(values):
    return ''.join(map(str, values))


def stars(n, edges):
    result = [[] for _ in range(n)]
    for e, uv in enumerate(edges):
        for v in uv:
            assert 0 <= v < n
            result[v].append(e)
    return result


def flow_ok(n, edges, f):
    assert len(f) == len(edges) and all(1 <= a <= 7 for a in f)
    assert all(xor(f[e] for e in s) == 0 for s in stars(n, edges))


def cover_ok(n, edges, cw, f):
    assert len(cw) == len(edges) and set(cw) <= set('0123456789')
    c = [Q[int(a)] for a in cw]
    assert [a & 1 for a in c] == [a & 1 for a in f]
    assert all(xor(c[e] for e in s) == 0 for s in stars(n, edges))


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


def switch(n, edges, f, move, core_count):
    es, a = move['edges'], move['increment']
    assert len(es) == len(set(es)) and all(core_count <= e < len(edges) for e in es)
    assert 1 <= a <= 7 and circuit([edges[e] for e in es])
    for e in es:
        assert f[e] != a
        f[e] ^= a
    flow_ok(n, edges, f)


def states(kind, alphabet):
    triangles = [(a, b, c) for a, b, c in itertools.product(alphabet, repeat=3) if a ^ b ^ c == 0]
    if kind == 'semi':
        return sorted((a, b, c, b, r) for a, c, r in triangles for b in alphabet)
    ends = {r: [(a, b) for a, b, c in triangles if c == r] for r in alphabet}
    return sorted((a, b, c, d, x, y, r) for x, y, r in triangles
                  for a, c in ends[x] for b, d in ends[y])


def zbits(values):
    return sum((a & 1) << i for i, a in enumerate(values[:4]))


def local_audit(kind, saved):
    fs, cs = states(kind, range(1, 8)), states(kind, Q)
    fibers, table = defaultdict(list), defaultdict(set)
    for f in fs:
        fibers[f[-1], f[0] ^ f[1]].append(f)
    for c in cs:
        table[c[-1], zbits(c)].add(c[0] ^ c[1])
    assert all(6 <= len(allowed) <= 8 for allowed in table.values())
    for r in Q:
        if not r & 1:
            assert table[r, 15] == {c for c in EVEN if not c & 1}-{30, 30 ^ r}
    patterns = ({(0, 1, 4, 5), (2, 3, 4, 5), (0, 1, 2, 3)} if kind == 'blowup' else {(0, 1, 2, 3)})
    records, hist = [], Counter()
    for (p, h), values in sorted(fibers.items()):
        adjacency = [[] for _ in values]
        for i, f in enumerate(values):
            for j, g in enumerate(values):
                differences = [a ^ b for a, b in zip(f, g)]
                support = tuple(e for e, a in enumerate(differences) if a)
                if support in patterns and len({a for a in differences if a}) == 1:
                    adjacency[i].append(j)
        for r in Q:
            if (r & 1) != (p & 1):
                continue
            for charge in EVEN:
                if (charge & 1) != (h & 1):
                    continue
                sources = [i for i, f in enumerate(values) if charge in table[r, zbits(f)]]
                distance, todo = {i: 0 for i in sources}, deque(sources)
                while todo:
                    i = todo.popleft()
                    for j in adjacency[i]:
                        if j not in distance:
                            distance[j] = distance[i]+1
                            todo.append(j)
                assert len(distance) == len(values) and max(distance.values()) <= 1
                for i, f in enumerate(values):
                    records.append([p, h, word(f), r, charge, distance[i]])
                    hist[distance[i]] += 1
    assert saved['flow_count'] == len(fs) == (1512 if kind == 'blowup' else 294)
    assert saved['fiber_size_histogram'] == [list(x) for x in sorted(Counter(map(len, fibers.values())).items())]
    assert saved['compatible_cases'] == len(records) == (58752 if kind == 'blowup' else 11424)
    assert saved['distance_histogram'] == [list(x) for x in sorted(hist.items())]
    assert hist == ({0: 54000, 1: 4752} if kind == 'blowup' else {0: 10464, 1: 960})
    digest = hashlib.sha256(json.dumps(sorted(records), separators=(',', ':')).encode()).hexdigest()
    assert digest == saved['distance_sha256']
    sharp = saved['sharp_one_move']
    f, g = sharp['initial_flow'], sharp['final_flow']
    assert tuple(f) in fs and tuple(g) in fs and tuple(sharp['cover_pairs']) in cs
    r, charge = sharp['boundary_pair'], sharp['cover_charge']
    assert charge not in table[r, zbits(f)] and charge in table[r, zbits(g)]
    positions, a = sharp['move']['positions'], sharp['move']['increment']
    assert tuple(positions) in patterns and 1 <= a <= 7
    assert [v ^ a if e in positions else v for e, v in enumerate(f)] == g
    cover = sharp['cover_pairs']
    assert cover[-1] == r and cover[0] ^ cover[1] == charge
    assert [v & 1 for v in cover] == [v & 1 for v in g]
    print(kind, 'rebuilt all', len(records), 'local distances:', dict(hist), flush=True)
    return table


def check_quotient(kind, n, edges, junctions, lengths, rec, table, initial=None):
    f = list(map(int, rec['initial_flow_word']))
    if initial is not None:
        assert f == initial
    flow_ok(n, edges, f)
    original = f.copy()
    m = len(rec['core_cover_word'])
    core_pairs = [Q[int(a)] for a in rec['core_cover_word']]
    assert len(rec['cycles']) == len(lengths)
    bad_all, offset = set(), 0
    for k, saved in zip(lengths, rec['cycles']):
        js = junctions[offset:offset+k]
        h = f[js[0][0]] ^ f[js[0][1]]
        candidates = [c for c in EVEN if (c & 1) == (h & 1)]
        counts, bad_sets = [], []
        deficiency = sum(8-len(table[core_pairs[ids[-1]], zbits([f[e] for e in ids])]) for ids in js)
        for c in candidates:
            at, bad = c, []
            for j, ids in enumerate(js, offset):
                r = core_pairs[ids[-1]]
                assert (r & 1) == (f[ids[-1]] & 1)
                if at not in table[r, zbits([f[e] for e in ids])]:
                    bad.append(j)
                at ^= r
            assert at == c
            counts.append(len(bad))
            bad_sets.append(bad)
        assert saved['length'] == k and saved['initial_flow_charge'] == h
        assert saved['initial_cover_charges'] == candidates and saved['incompatible_junction_counts'] == counts
        delta = min(counts)
        assert saved['delta'] == delta and 8*delta <= sum(counts) == deficiency <= 2*k
        chosen = candidates.index(saved['chosen_cover_charge'])
        assert counts[chosen] == delta
        bad_all.update(bad_sets[chosen])
        offset += k
    assert len(rec['moves']) == rec['junction_distance'] == sum(c['delta'] for c in rec['cycles'])
    assert {move['junction'] for move in rec['moves']} == bad_all
    charges = [(f[js[0]] ^ f[js[1]], f[js[2]] ^ f[js[3]]) for js in junctions]
    for move in rec['moves']:
        js = junctions[move['junction']]
        assert set(move['edges']) <= set(js[:-1])
        assert len(move['edges']) == (4 if kind == 'blowup' else 3)
        switch(n, edges, f, move, m)
        assert [(f[js[0]] ^ f[js[1]], f[js[2]] ^ f[js[3]]) for js in junctions] == charges
    assert f == list(map(int, rec['final_flow_word'])) and f[:m] == original[:m]
    cover_ok(n, edges, rec['cover_word'], f)
    assert rec['cover_word'][:m] == rec['core_cover_word']
    pairs = [Q[int(a)] for a in rec['cover_word']]
    offset = 0
    for k, c in zip(lengths, rec['cycles']):
        at = c['chosen_cover_charge']
        for js in junctions[offset:offset+k]:
            assert pairs[js[0]] ^ pairs[js[1]] == at
            at ^= pairs[js[-1]]
        assert at == c['chosen_cover_charge']
        offset += k


def cap_edges(kind, k):
    edges, junctions = [[i, k] for i in range(k)], []
    for i in range(k):
        left, right, at = k+1+(i-1) % k, k+1+i, len(edges)
        if kind == 'blowup':
            u, w = 2*k+1+2*i, 2*k+2+2*i
            edges += [[left, u], [left, w], [right, u], [right, w], [u, i], [w, i]]
            junctions.append(list(range(at, at+6))+[i])
        else:
            edges += [[left, i], [left, right], [right, i]]
            junctions.append([at, at+1, at+2, at+1, i])
    return edges, junctions


def check_sharp_graph(g, m):
    kind, k = g['construction'], 8*m
    perm = [8*j+i for j in range(m) for i in (0, 1, 5, 2, 3, 7, 4, 6)]
    base = [[off+i, off+(i+1) % k] for off in (0, k) for i in range(k)]
    base += [[i, k+perm.index(i)] for i in range(k)]
    assert g['base_vertices'] == 2*k and g['base_edges'] == base
    assert g['selected_cycles'] == [list(range(k))] and g['pieces'] == k
    assert g['outside_base_edge_ids'] == list(range(k, 3*k))
    edges, reps = base[k:].copy(), []
    for i in range(k):
        reps.append(list(range(len(edges), len(edges)+10))+[None]*4)
        edges += [[2*k+8*i+u-2, 2*k+8*i+v-2] for u, v in INTERNAL]
    for i, js in enumerate(g['junctions']):
        prev, at = (i-1) % k, len(edges)
        a, b, c, d = 2*k+8*prev+2, 2*k+8*prev+3, 2*k+8*i, 2*k+8*i+4
        if kind == 'blowup':
            u, w = 10*k+2*i, 10*k+2*i+1
            edges += [[a, u], [b, w], [c, u], [d, w], [u, i], [w, i]]
            ids = list(range(at, at+6))+[k+i]
        else:
            edges += [[a, i], [b, d], [c, i]]
            ids = [at, at+1, at+2, at+1, k+i]
        assert js == {'vertex': i, 'left_piece': prev, 'right_piece': i, 'edges': ids}
        reps[prev][10:12], reps[i][12:14] = ids[:2], ids[2:4]
    assert len(g['blocks']) == len(g['junctions']) == k
    for i, b in enumerate(g['blocks']):
        assert b == {'vertices': list(range(2*k+8*i, 2*k+8*i+8)), 'edge_representatives': reps[i]}
    n = (12 if kind == 'blowup' else 10)*k
    assert edges == g['edges'] and g['vertices'] == n
    assert len({tuple(sorted(e)) for e in edges}) == len(edges)
    assert set(map(len, stars(n, edges))) == {3}
    owner = list(range(2*k))+[2*k+i for i in range(k) for _ in range(8)]
    if kind == 'blowup':
        owner += list(range(3*k, 5*k))
    kept = list(range(2*k))+list(range(12*k, len(edges)))
    qe = [[owner[u], owner[v]] for e in kept for u, v in [edges[e]]]
    assert owner == g['vertex_map'] and kept == g['kept_edge_ids'] and qe == g['quotient_edges']
    assert g['quotient_vertices'] == max(owner)+1
    co = [0]*k+list(range(1, k+1))
    core = g['contracted_base']
    assert core['vertices'] == k+1 and core['vertex_map'] == co
    assert core['edges'] == [[co[u], co[v]] for u, v in base[k:]]
    flow_ok(k+1, core['edges'], list(map(int, core['four_flow_word'])))
    qf = list(map(int, g['quotient_four_flow_word']))
    flow_ok(g['quotient_vertices'], qe, qf)
    assert set(qf) <= {1, 2, 3} and qf[:2*k] == list(map(int, core['four_flow_word']))
    initial = list(map(int, g['initial_flow_word']))
    for js in g['junctions']:
        assert zbits([initial[e] for e in js['edges']]) == 15


def check_full(kind, g, rec, table):
    n, edges, kept = g['vertices'], g['edges'], g['kept_edge_ids']
    m, q = len(g['outside_base_edge_ids']), g['pieces']
    initial = list(map(int, g['initial_flow_word']))
    flow_ok(n, edges, initial)
    index = {e: i for i, e in enumerate(kept)}
    js = [[index[e] for e in j['edges']] for j in g['junctions']]
    qr = rec['quotient_repair']
    assert len(qr['core_cover_word']) == m
    check_quotient(kind, g['quotient_vertices'], g['quotient_edges'], js,
                   list(map(len, g['selected_cycles'])), qr, table, [initial[e] for e in kept])
    def charges(f):
        result = []
        for b in g['blocks']:
            es = b['edge_representatives']
            a = f[es[10]] ^ f[es[11]]
            assert a == f[es[12]] ^ f[es[13]]
            result.append(a)
        return result
    wanted = charges(initial)
    f, at, prepared, finished = initial.copy(), 0, set(), Counter()
    completion_started = False
    for move in rec['moves']:
        stage = move['kind']
        assert stage in ('piece_preparation', 'lifted_junction', 'piece_completion')
        if stage == 'piece_completion':
            completion_started = True
            assert at == len(qr['moves']) and not prepared
        else:
            assert not completion_started and at < len(qr['moves'])
        if stage != 'piece_completion':
            qm = qr['moves'][at]
            outside = {kept[e] for e in qm['edges']}
            visited = {i for i, b in enumerate(g['blocks']) if outside & set(b['edge_representatives'][10:])}
            assert len(visited) <= 2
        if stage in ('piece_preparation', 'piece_completion'):
            i = move['piece']
            assert 0 <= i < q and len(move['edges']) == 5
            assert set(move['edges']) <= set(g['blocks'][i]['edge_representatives'][:10])
            if stage == 'piece_preparation':
                assert i in visited and i not in prepared
                prepared.add(i)
            else:
                finished[i] += 1
        else:
            assert move['junction'] == qm['junction'] and move['increment'] == qm['increment']
            assert set(move['edges']) & set(kept) == outside
            assert len(move['edges']) <= (10 if kind == 'blowup' else 9)
            for i, b in enumerate(g['blocks']):
                inside = set(move['edges']) & set(b['edge_representatives'][:10])
                assert len(inside) <= (3 if i in visited else 0)
            at += 1
            prepared = set()
        switch(n, edges, f, move, m)
        assert f[:m] == initial[:m] and charges(f) == wanted
    assert at == qr['junction_distance'] and not prepared and max(finished.values(), default=0) <= 2
    assert f == list(map(int, rec['final_flow_word']))
    assert [f[e] for e in kept] == list(map(int, qr['final_flow_word']))
    cover_ok(n, edges, rec['cover_word'], f)
    assert ''.join(rec['cover_word'][e] for e in kept) == qr['cover_word']
    assert rec['cover_word'][:m] == qr['core_cover_word']
    assert rec['switch_bound'] == 2*q+3*qr['junction_distance'] >= len(rec['moves'])
    assert len(rec['moves']) <= 2*q+3*sum(len(c)//4 for c in g['selected_cycles'])


def main():
    data = json.loads((HERE / 'linear_region_repair.json').read_text())
    for src in data['sources']:
        assert hashlib.sha256((HERE / src['file']).read_bytes()).hexdigest() == src['sha256']
    tables = {kind: local_audit(kind, data['local_audits'][kind]) for kind in ('blowup', 'semi')}
    for kind, records in data['caps'].items():
        assert [r['length'] for r in records] == [3, 4, 5, 7, 8, 9, 16, 31, 64]
        for rec in records:
            k = rec['length']
            edges, js = cap_edges(kind, k)
            assert rec['edges'] == edges and rec['vertices'] == (4*k+1 if kind == 'blowup' else 2*k+1)
            check_quotient(kind, rec['vertices'], edges, js, [k], rec['repair'], tables[kind])
    old = json.loads((HERE / 'short_cycle_boundary.json').read_text())
    assert [r['construction'] for r in data['previous_examples']] == ['blowup', 'semi']
    for rec in data['previous_examples']:
        kind = rec['construction']
        g = next(g for g in old['cubic_examples'] if g['construction'] == kind)
        check_full(kind, g, rec['repair'], tables[kind])
        assert rec['repair']['quotient_repair']['core_cover_word'] == g['rejected_core_cover_word']
        assert rec['repair']['quotient_repair']['junction_distance'] == 1
        print(kind, 'original octagon:', len(rec['repair']['moves']), 'full switches.', flush=True)
    assert [(r['construction'], r['repetitions']) for r in data['sharp_family']] == [(kind, m) for kind in ('blowup', 'semi') for m in (1, 2, 4, 8)]
    for rec in data['sharp_family']:
        kind, m, g = rec['construction'], rec['repetitions'], rec['graph']
        assert g['construction'] == kind
        check_sharp_graph(g, m)
        check_full(kind, g, rec['repair'], tables[kind])
        qr = rec['repair']['quotient_repair']
        expected = [12, 6, 12, 10, 24, 10, 12, 10]*m+[6, 10, 6, 18, 6, 10, 6, 18]*m
        assert [Q[int(c)] for c in qr['core_cover_word']] == expected
        assert qr['cycles'][0]['incompatible_junction_counts'] == [2*m]*8
        assert qr['junction_distance'] == 2*m
        print(kind, 'm =', m, 'verified', g['vertices'], 'vertices; exact junction distance', 2*m,
              'and', len(rec['repair']['moves']), 'full switches.', flush=True)
    print('All 70,176 local cases, 18 quotient repairs and ten cubic repairs passed, including every preserved core value, piece charge and circuit-length bound.')
    print('Exact distance concerns single-junction quotient moves; no minimum full-graph distance or general 5-CDC existence claim is made.')


if __name__ == '__main__':
    main()
