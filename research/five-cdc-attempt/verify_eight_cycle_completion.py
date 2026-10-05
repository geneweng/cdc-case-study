#!/usr/bin/env python3
"""Independent standard-library verifier for the single-eight-cycle theorem.

Rebuilds junction relations from vertex triangles, enumerates permutations of
the seven nonzero auxiliary states, and tests swaps directly. No constructor,
previous verifier, SAT solver, or graph library is imported.
"""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
Q = [sum(1 << i for i in ij) for ij in itertools.combinations(range(5), 2)]
AUX = Q[4:]
EVEN = [x for x in range(32) if x.bit_count() % 2 == 0]
SPACE = [x for x in EVEN if not x & 1]
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]


def xor(xs):
    result = 0
    for x in xs:
        result ^= x
    return result


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def stars(n, edges):
    result = [[] for _ in range(n)]
    for e, uv in enumerate(edges):
        for v in uv:
            assert 0 <= v < n
            result[v].append(e)
    return result


def valid(n, edges, values, alphabet):
    assert len(values) == len(edges) and all(a in alphabet for a in values)
    assert all(xor(values[e] for e in s) == 0 for s in stars(n, edges))


def decode(cw):
    return [Q[int(c)] for c in cw]


def circuit(edges):
    neighbors = defaultdict(set)
    degree = Counter(v for uv in edges for v in uv)
    assert degree and set(degree.values()) == {2}
    for u, v in edges:
        neighbors[u].add(v)
        neighbors[v].add(u)
    seen, todo = set(), [next(iter(degree))]
    while todo:
        v = todo.pop()
        if v not in seen:
            seen.add(v)
            todo.extend(neighbors[v]-seen)
    assert seen == set(degree)


def relation(kind, saved):
    triangles = [(a, b, c) for a, b, c in itertools.product(Q, repeat=3) if a ^ b ^ c == 0]
    if kind == 'semi':
        states = [(a, b, c, b, r) for a, c, r in triangles for b in Q]
    else:
        ends = {c: [(a, b) for a, b, d in triangles if c == d] for c in Q}
        states = [(a, b, c, d, x, y, r) for x, y, r in triangles
                  for a, c in ends[x] for b, d in ends[y]]
    table = defaultdict(set)
    for state in states:
        z = sum((a & 1) << i for i, a in enumerate(state[:4]))
        table[state[-1], z].add(state[0] ^ state[1])
    # Check every locally admissible F-pattern, including completeness of keys.
    keys = {(r, z) for r in Q for z in range(16)
            if z.bit_count() % 2 == (r & 1) and (kind != 'semi' or (z >> 1 & 1) == (z >> 3 & 1))}
    assert set(table) == keys
    rows = []
    for r, z in sorted(keys):
        p = (z & 1) ^ (z >> 1 & 1)
        allowed = {h for h in EVEN if h & 1 == p}
        if (z & 1) and (z & 2):
            allowed.discard(30)
        if (z & 4) and (z & 8):
            allowed.discard(30 ^ r)
        assert table[r, z] == allowed
        rows.append([r, z, sorted(allowed)])
    assert len(states) == saved['assignments'] == (2160 if kind == 'blowup' else 600)
    assert len(keys) == saved['keys'] == (80 if kind == 'blowup' else 40)
    assert digest(rows) == saved['relation_sha256']
    return table


def prefixes(rs):
    assert xor(rs) == 0
    return [xor(rs[:i]) for i in range(len(rs))]


def pairings(mask):
    if not mask:
        yield ()
        return
    a = (mask & -mask).bit_length()-1
    rest = mask ^ (1 << a)
    for b in range(a+1, 8):
        if rest >> b & 1:
            for tail in pairings(rest ^ (1 << b)):
                yield ((a, b),)+tail


def swap_test(rs, t):
    affected = [i for i, r in enumerate(rs) if (r & t).bit_count() == 1]
    safe = set()
    for i, j in itertools.combinations(affected, 2):
        changed = [r ^ t if e in (i, j) else r for e, r in enumerate(rs)]
        assert all(r in AUX for r in changed)
        if len(set(prefixes(changed))) == 8:
            safe.add((i, j))
        arc = set(prefixes(rs)[i+1:j+1])
        assert ((i, j) in safe) == ({h ^ t for h in arc} == arc)
    all_pairings = list(pairings(sum(1 << i for i in affected)))
    safe_count = sum(set(p) <= safe for p in all_pairings)
    return affected, safe, all_pairings, safe_count


def boundary_lemma(saved):
    words = []
    for permutation in itertools.permutations(SPACE[1:]):
        vertices = (0,)+permutation
        rs = tuple(vertices[i] ^ vertices[(i+1) % 8] for i in range(8))
        if all(r in AUX for r in rs):
            words.append(rs)
    words.sort()
    assert len(words) == saved['words'] == 1488
    hist, records, pair_count = Counter(), [], 0
    for rs in words:
        results = {t: swap_test(rs, t) for t in AUX}
        hist[sum(d[3] == 0 for d in results.values())] += 1
        records.append([list(rs), [results[t][3] for t in AUX]])
        options = [(len(safe), -len(affected), t) for t, (affected, safe, ps, count) in results.items() if not count]
        _, _, t = min(options)
        affected, safe, ps, count = results[t]
        assert len(safe) <= 1 and len(affected) >= 4
        for p in ps:
            assert any(ij not in safe for ij in p)
        pair_count += len(ps)
    assert saved['forcing_pair_histogram'] == [list(x) for x in sorted(hist.items())]
    assert saved['safe_matching_counts_sha256'] == digest(records)
    assert saved['chosen_pair_matchings_checked'] == pair_count
    covered = set()
    assert len(saved['orbits']) == 11
    for rec in saved['orbits']:
        rs = tuple(rec['boundary_pairs'])
        images = set()
        for p in itertools.permutations(range(1, 5)):
            renamed = tuple(sum(1 << p[i-1] for i in range(1, 5) if r >> i & 1) for r in rs)
            for reflected in (renamed, renamed[::-1]):
                for s in range(8):
                    images.add(reflected[s:]+reflected[:s])
        assert rs == min(images) and not covered & images
        assert len(images) == rec['orbit_size']
        covered |= images
        affected, safe, ps, count = swap_test(rs, rec['swap_pair'])
        assert affected == rec['affected_ports'] and sorted(safe) == [tuple(p) for p in rec['non_escaping_pairs']]
        assert len(ps) == rec['outside_pairings_checked'] and count == 0
    assert covered == set(words)
    print('Checked all 1,488 words, 11 symmetry orbits, and', pair_count, 'chosen-label outside pairings.', flush=True)


def reconstruct(g):
    base, n, cycles = g['base_edges'], g['base_vertices'], g['selected_cycles']
    assert len(cycles) == 1 and cycles[0] == list(range(8))
    assert all(len(s) == 3 for s in stars(n, base))
    assert len({tuple(sorted(e)) for e in base}) == len(base) and all(u != v for u, v in base)
    removed = {tuple(sorted((i, (i+1) % 8))) for i in range(8)}
    outside = [e for e, uv in enumerate(base) if tuple(sorted(uv)) not in removed]
    assert outside == g['outside_base_edge_ids']
    edges = [tuple(base[e]) for e in outside]
    m, q = len(edges), 8
    owner = list(range(n))+[n+i for i in range(q) for _ in range(8)]
    for i in range(q):
        edges.extend((n+8*i+u-2, n+8*i+v-2) for u, v in INTERNAL)
    for i in range(q):
        p = (i-1) % q
        a, b, c, d = n+8*p+2, n+8*p+3, n+8*i, n+8*i+4
        if g['construction'] == 'blowup':
            u, w = n+8*q+2*i, n+8*q+2*i+1
            edges.extend([(a, u), (b, w), (c, u), (d, w), (u, i), (w, i)])
        else:
            edges.extend([(a, i), (b, d), (c, i)])
    if g['construction'] == 'blowup':
        owner.extend(range(n+q, n+3*q))
    assert edges == [tuple(uv) for uv in g['edges']] and len(owner) == g['vertices']
    assert owner == g['vertex_map'] and g['pieces'] == q
    assert all(len(s) == 3 for s in stars(g['vertices'], edges))
    assert len({tuple(sorted(e)) for e in edges}) == len(edges) and all(u != v for u, v in edges)
    kept = list(range(m))+list(range(m+10*q, len(edges)))
    qe = [[owner[edges[e][0]], owner[edges[e][1]]] for e in kept]
    assert g['kept_edge_ids'] == kept and g['quotient_edges'] == qe and g['quotient_vertices'] == max(owner)+1
    for i, b in enumerate(g['blocks']):
        assert b['vertices'] == list(range(n+8*i, n+8*i+8))
        assert b['edge_representatives'][:10] == list(range(m+10*i, m+10*i+10))
        for e, v in zip(b['edge_representatives'][10:], (n+8*i+2, n+8*i+3, n+8*i, n+8*i+4)):
            assert v in edges[e] and e in kept
    for i, j in enumerate(g['junctions']):
        a, b = g['blocks'][(i-1) % 8]['edge_representatives'][10:12]
        c, d = g['blocks'][i]['edge_representatives'][12:14]
        stem = next(e for e in range(m) if i in edges[e])
        js = [a, b, c, d]
        if g['construction'] == 'blowup':
            js += [m+80+6*i+4, m+80+6*i+5]
        js += [stem]
        assert j == {'vertex': i, 'left_piece': (i-1) % 8, 'right_piece': i, 'edges': js}
    co = [0]*8+list(range(1, n-7))
    ce = [[co[u], co[v]] for u, v in edges[:m]]
    assert g['core'] == {'vertices': n-7, 'vertex_map': co, 'edges': ce}
    return m


def no_petersen_four_flow(edges):
    inc = stars(10, edges)
    even = [s for s in range(1 << 15) if all(sum(s >> e & 1 for e in star) % 2 == 0 for star in inc)]
    assert len(even) == 64 and not any(a | b == (1 << 15)-1 for a in even for b in even)


def example(g, table):
    m = reconstruct(g)
    edges, n, core = g['edges'], g['vertices'], g['core']
    f = list(map(int, g['initial_flow_word']))
    valid(n, edges, f, range(1, 8))
    initial = f.copy()
    original, changed = decode(g['original_core_cover_word']), decode(g['changed_core_cover_word'])
    valid(core['vertices'], core['edges'], original, Q)
    valid(core['vertices'], core['edges'], changed, Q)
    assert [a & 1 for a in original] == [a & 1 for a in changed] == [a & 1 for a in f[:m]]
    assert g['hub'] == 0 and g['core_stems'] == [j['edges'][-1] for j in g['junctions']]
    move = g['core_cover_swap']
    t, es = move['swap_pair'], move['edges']
    assert t in AUX and len(es) == len(set(es))
    circuit([core['edges'][e] for e in es])
    assert all((original[e] & t).bit_count() == 1 for e in es)
    assert changed == [a ^ t if e in es else a for e, a in enumerate(original)]
    assert move['ports'] == [i for i, e in enumerate(g['core_stems']) if e in es]
    for cw, key in ((original, 'letters'), (changed, 'changed_letters')):
        letters = [[cw[j['edges'][-1]], sum((f[e] & 1) << i for i, e in enumerate(j['edges'][:4]))]
                   for j in g['junctions']]
        assert letters == g[key]
        pref = prefixes([r for r, z in letters])
        marked = [i for i in range(8) if letters[i][1] & 3 == 3 or letters[i-1][1] & 12 == 12]
        assert marked == g['marked_cuts'] == list(range(8))
        allowed = set(SPACE)
        for at, (r, z) in zip(pref, letters):
            allowed &= {h ^ at for h in table[r, z]}
        assert allowed == set(SPACE)-{30 ^ pref[i] for i in marked}
        if key == 'letters':
            assert not allowed and len(set(pref)) == 8
        else:
            assert allowed and sorted(allowed) == g['surviving_charges'] and g['chosen_charge'] in allowed
    qc = decode(g['quotient_cover_word'])
    valid(g['quotient_vertices'], g['quotient_edges'], qc, Q)
    assert qc[:m] == changed and [a & 1 for a in qc] == [f[e] & 1 for e in g['kept_edge_ids']]
    assert len(g['moves']) <= 2*g['pieces']
    for move in g['moves']:
        es, a = move['edges'], move['increment']
        assert len(es) == len(set(es)) == 5 and 1 <= a <= 7
        assert set(es) <= set(g['blocks'][move['piece']]['edge_representatives'][:10])
        circuit([edges[e] for e in es])
        for e in es:
            assert f[e] != a
            f[e] ^= a
        valid(n, edges, f, range(1, 8))
    assert f == list(map(int, g['final_flow_word']))
    assert all(f[e] == initial[e] for e in g['kept_edge_ids'])
    c = decode(g['cover_word'])
    valid(n, edges, c, Q)
    assert [a & 1 for a in c] == [a & 1 for a in f]
    assert [c[e] for e in g['kept_edge_ids']] == qc
    if g['core_has_four_flow']:
        valid(core['vertices'], core['edges'], list(map(int, g['core_four_flow_word'])), (1, 2, 3))
    else:
        rec = g['petersen_two_sum']
        region = {core['vertex_map'][v] for v in rec['vertices']}
        cut = [e for e, (u, v) in enumerate(core['edges']) if (u in region) != (v in region)]
        assert cut == rec['core_cut_edges'] and len(cut) == 2
        local = {core['vertex_map'][v]: i for i, v in enumerate(rec['vertices'])}
        restored = [tuple(sorted((local[u], local[v]))) for u, v in core['edges'] if u in region and v in region]
        ends = [next(v for v in core['edges'][e] if v in region) for e in cut]
        restored.append(tuple(sorted(local[v] for v in ends)))
        expected = [(i, (i+1) % 5) for i in range(5)]+[(i, i+5) for i in range(5)]
        expected += [(i+5, (i+2) % 5+5) for i in range(5)]
        assert sorted(restored) == sorted(tuple(sorted(e)) for e in expected)
        assert rec['petersen_edges'] == [list(e) for e in expected]
        no_petersen_four_flow(expected)
    print(g['construction'], n, 'vertices:', len(g['moves']), 'B pentagons; fixed quotient layer and full cover verified.', flush=True)


def main():
    saved = json.loads((HERE / 'eight_cycle_completion.json').read_text())
    for src in saved['sources']:
        assert hashlib.sha256((HERE / src['file']).read_bytes()).hexdigest() == src['sha256']
    tables = {k: relation(k, saved['local_relations'][k]) for k in ('blowup', 'semi')}
    boundary_lemma(saved['boundary_lemma'])
    assert len(saved['examples']) == 6
    for g in saved['examples']:
        example(g, tables[g['construction']])
    print('PASS: marked-cut identity, single-eight-cycle boundary escape, and all graph certificates.')


if __name__ == '__main__':
    main()
