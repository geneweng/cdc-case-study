#!/usr/bin/env python3
"""Independent check of a genuine one-step auxiliary exchange obstruction.

Reconstructs all four cubic graphs, computes full binary exchange kernels,
checks every projected port set, and verifies neutral moves and final covers.
Imports no constructor or earlier verifier; Python standard library only.
"""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
Q = [sum(1 << i for i in p) for p in itertools.combinations(range(5), 2)]
AUX = Q[4:]
EVEN = [h for h in range(32) if h.bit_count() % 2 == 0]
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]


def xor(xs):
    a = 0
    for x in xs:
        a ^= x
    return a


def prefixes(rs):
    assert xor(rs) == 0
    return [xor(rs[:i]) for i in range(len(rs))]


def bad(rs, marked=None):
    p = prefixes(rs)
    return len({p[i] for i in (range(len(rs)) if marked is None else marked)}) == 8


def decode(cw):
    return [Q[int(c)] for c in cw]


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


def circuit(edges):
    degree = Counter(v for uv in edges for v in uv)
    assert degree and set(degree.values()) == {2}
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
    assert seen == set(degree)


def junction_table(kind):
    triangles = [(a, b, c) for a, b, c in itertools.product(Q, repeat=3) if a ^ b ^ c == 0]
    if kind == 'semi':
        states = [(a, b, c, b, r) for a, c, r in triangles for b in Q]
    else:
        ends = {r: [(a, b) for a, b, c in triangles if c == r] for r in Q}
        states = [(a, b, c, d, x, y, r) for x, y, r in triangles
                  for a, c in ends[x] for b, d in ends[y]]
    table = defaultdict(set)
    for row in states:
        z = sum((a & 1) << i for i, a in enumerate(row[:4]))
        table[row[-1], z].add(row[0] ^ row[1])
    for (r, z), allowed in table.items():
        p = (z & 1) ^ (z >> 1 & 1)
        expected = {h for h in EVEN if h & 1 == p}
        if z & 3 == 3:
            expected.discard(30)
        if z & 12 == 12:
            expected.discard(30 ^ r)
        assert allowed == expected
    assert len(table) == (80 if kind == 'blowup' else 40)
    return table


def reconstruct(g):
    n, base, cycles = g['base_vertices'], g['base_edges'], g['selected_cycles']
    q = sum(map(len, cycles))
    assert g['pieces'] == q and all(3 <= len(c) <= 11 for c in cycles)
    assert len(g['blocks']) == len(g['junctions']) == q
    assert len(g['regions']) == len(g['regional_extensions']) == len(g['profile_names']) == len(cycles)
    assert len({v for c in cycles for v in c}) == q
    assert all(len(s) == 3 for s in stars(n, base))
    assert len({tuple(sorted(e)) for e in base}) == len(base) and all(u != v for u, v in base)
    seen, todo = {0}, [0]
    adjacency = [[] for _ in range(n)]
    for u, v in base:
        adjacency[u].append(v)
        adjacency[v].append(u)
    for u in todo:
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    assert len(seen) == n
    removed = {tuple(sorted((c[i], c[(i+1) % len(c)]))) for c in cycles for i in range(len(c))}
    outside = [i for i, uv in enumerate(base) if tuple(sorted(uv)) not in removed]
    assert outside == g['outside_base_edge_ids']
    edges, js = [tuple(base[e]) for e in outside], []
    m = len(edges)
    for i in range(q):
        edges.extend((n+8*i+u-2, n+8*i+v-2) for u, v in INTERNAL)
    offset = 0
    for cycle in cycles:
        for j, v in enumerate(cycle):
            i, prev = offset+j, offset+(j-1) % len(cycle)
            a, b, c, d = n+8*prev+2, n+8*prev+3, n+8*i, n+8*i+4
            start = len(edges)
            stem = next(e for e in range(m) if v in edges[e])
            if g['construction'] == 'blowup':
                u, w = n+8*q+2*i, n+8*q+2*i+1
                edges.extend([(a, u), (b, w), (c, u), (d, w), (u, v), (w, v)])
                ids = list(range(start, start+6))+[stem]
            else:
                edges.extend([(a, v), (b, d), (c, v)])
                ids = [start, start+1, start+2, start+1, stem]
            js.append({'vertex': v, 'left_piece': prev, 'right_piece': i, 'edges': ids})
        offset += len(cycle)
    owner = list(range(n))+[n+i for i in range(q) for _ in range(8)]
    if g['construction'] == 'blowup':
        owner.extend(range(n+q, n+3*q))
    assert g['edges'] == [list(uv) for uv in edges] and g['junctions'] == js
    assert g['vertices'] == len(owner) and g['vertex_map'] == owner
    assert all(len(s) == 3 for s in stars(len(owner), edges))
    assert len({tuple(sorted(e)) for e in edges}) == len(edges) and all(u != v for u, v in edges)
    for i, b in enumerate(g['blocks']):
        assert b['vertices'] == list(range(n+8*i, n+8*i+8))
        assert b['edge_representatives'][:10] == list(range(m+10*i, m+10*i+10))
        for e, v in zip(b['edge_representatives'][10:], (n+8*i+2, n+8*i+3, n+8*i, n+8*i+4)):
            assert v in edges[e] and e >= m+10*q
    kept = list(range(m))+list(range(m+10*q, len(edges)))
    assert g['kept_edge_ids'] == kept
    assert g['quotient_edges'] == [[owner[edges[e][0]], owner[edges[e][1]]] for e in kept]
    assert g['quotient_vertices'] == max(owner)+1
    co = list(range(n))
    for c in cycles:
        for v in c:
            co[v] = min(c)
    names = {v: i for i, v in enumerate(sorted(set(co)))}
    co = [names[v] for v in co]
    assert g['core'] == {'vertices': len(names), 'vertex_map': co,
                         'edges': [[co[u], co[v]] for u, v in edges[:m]]}
    return m


def bad_regions(regions, pairs):
    return [i for i, r in enumerate(regions) if r['critical'] and bad([pairs[h//2] for h in r['incidences']], r['marked_cuts'])]


def survivors(rs, table):
    allowed = {h for h in EVEN if not h & 1}
    at = 0
    for r in rs:
        allowed &= {h ^ at for h in table[r, 15]}
        at ^= r
    assert at == 0
    return allowed


def protection(rs, marked, t, matching):
    active = [i for i, a in enumerate(rs) if (a & t).bit_count() == 1]
    assert sorted(i for p in matching for i in p) == active and not bad(rs, marked)
    for use in itertools.product((0, 1), repeat=len(matching)):
        ports = {i for yes, pair in zip(use, matching) if yes for i in pair}
        after = [a ^ t if i in ports else a for i, a in enumerate(rs)]
        assert not bad(after, marked)


def kernel_image(core, regions, pairs, rec):
    t, target = rec['swap_pair'], regions[rec['target_region']]
    affected = [e for e, a in enumerate(pairs) if (a & t).bit_count() == 1]
    index = {e: j for j, e in enumerate(affected)}
    rows = []
    for star in stars(core['vertices'], core['edges']):
        rows.append(xor(1 << index[e] for e in star if e in index))
    for fixed in rec['protected_pairings']:
        hs = regions[fixed['region']]['incidences']
        rows.extend((1 << index[hs[i]//2]) ^ (1 << index[hs[j]//2]) for i, j in fixed['pairs'])
    echelon = {}
    for row in rows:
        while row:
            pivot = row.bit_length()-1
            if pivot in echelon:
                row ^= echelon[pivot]
            else:
                echelon[pivot] = row
                break
    image = {0}
    for free in range(len(affected)):
        if free in echelon:
            continue
        vector = 1 << free
        for pivot in sorted(echelon):
            if (vector & echelon[pivot]).bit_count() % 2:
                vector |= 1 << pivot
        assert all((vector & row).bit_count() % 2 == 0 for row in rows)
        boundary = sum(1 << i for i, h in enumerate(target['incidences'])
                       if h//2 in index and vector >> index[h//2] & 1)
        image |= {s ^ boundary for s in image}
    return image, affected, index, rows


def verify_attempt(core, regions, pairs, before, rec, stats, table):
    t, target_id = rec['swap_pair'], rec['target_region']
    assert t in AUX and target_id in before
    target = regions[target_id]
    protected_ids = [i for i, r in enumerate(regions) if r['critical'] and i not in before]
    assert [r['region'] for r in rec['protected_pairings']] == protected_ids
    for fixed in rec['protected_pairings']:
        region = regions[fixed['region']]
        rs = [pairs[h//2] for h in region['incidences']]
        protection(rs, region['marked_cuts'], t, fixed['pairs'])
    image, affected, index, constraints = kernel_image(core, regions, pairs, rec)
    active = {i for i, h in enumerate(target['incidences']) if h//2 in index}
    remaining, blocks = active.copy(), []
    while remaining:
        i = min(remaining)
        block = {i} | {j for j in remaining if (1 << i) ^ (1 << j) in image}
        assert len(block) % 2 == 0
        remaining -= block
        blocks.append(sorted(block))
    assert blocks == rec['component_ports']
    expected = {s for s in range(1 << len(target['incidences']))
                if not s & ~sum(1 << i for i in active)
                and all(sum(s >> i & 1 for i in b) % 2 == 0 for b in blocks)}
    assert image == expected and len(image) == rec['reachable_masks'] == 1 << (len(active)-len(blocks))
    rs = [pairs[h//2] for h in target['incidences']]
    escaping = set()
    for mask in image:
        after = [a ^ t if mask >> i & 1 else a for i, a in enumerate(rs)]
        allowed = survivors(after, table)
        assert bool(allowed) == (not bad(after, target['marked_cuts']))
        if allowed:
            escaping.add(mask)
    assert len(escaping) == rec['escaping_masks']
    assert [list(r) for r in sorted(Counter(s.bit_count() for s in escaping).items())] == rec['escape_size_histogram']
    assert [r[0] for r in rec['realizations']] == sorted(image)
    for mask, edges in rec['realizations']:
        assert edges == sorted(set(edges)) and set(edges) <= set(affected)
        vector = sum(1 << index[e] for e in edges)
        assert all((vector & row).bit_count() % 2 == 0 for row in constraints)
        actual = sum(1 << i for i, h in enumerate(target['incidences']) if h//2 in edges)
        assert actual == mask
        changed = [a ^ t if e in edges else a for e, a in enumerate(pairs)]
        valid(core['vertices'], core['edges'], changed, Q)
        assert [a & 1 for a in changed] == [a & 1 for a in pairs]
        assert not (set(bad_regions(regions, changed))-set(before))
        stats['realizations'] += 1
        stats['realizations_using_target_loop'] += any(core['edges'][e] == [target['hub']]*2 for e in edges)
    stats['attempts'] += 1
    if not escaping:
        assert not any(k in rec for k in ('edges', 'selected_ports', 'cover_word_after'))
        stats['failed_attempts'] += 1
        return None
    mask = sum(1 << i for i in rec['selected_ports'])
    assert mask == min(escaping, key=lambda s: (s.bit_count(), s))
    assert rec['edges'] == dict(rec['realizations'])[mask]
    following = [a ^ t if e in rec['edges'] else a for e, a in enumerate(pairs)]
    assert following == decode(rec['cover_word_after'])
    for fixed in rec['protected_pairings']:
        region = regions[fixed['region']]
        changed = {i for i, h in enumerate(region['incidences']) if h//2 in rec['edges']}
        assert all((i in changed) == (j in changed) for i, j in fixed['pairs'])
        stats['protected_visits'] += bool(changed)
    return following


def example(g, table, stats):
    m = reconstruct(g)
    n, edges, core, regions = g['vertices'], g['edges'], g['core'], g['regions']
    initial = list(map(int, g['initial_flow_word']))
    valid(n, edges, initial, range(1, 8))
    pairs = decode(g['original_core_cover_word'])
    valid(core['vertices'], core['edges'], pairs, Q)
    assert [r & 1 for r in pairs] == [a & 1 for a in initial[:m]]
    offset = 0
    for region_index, (cycle, r) in enumerate(zip(g['selected_cycles'], regions)):
        ji = list(range(offset, offset+len(cycle)))
        js = [g['junctions'][i] for i in ji]
        zs = [sum((initial[e] & 1) << i for i, e in enumerate(j['edges'][:4])) for j in js]
        assert zs == [15]*len(cycle) and g['profile_names'][region_index] == str(len(cycle))
        assert len(cycle) == 11
        expected = [6, 6, 10, 6, 24, 6, 12, 18, 20, 10, 18]
        assert [pairs[j['edges'][-1]] for j in js] == expected
        hs = [2*j['edges'][-1]+edges[j['edges'][-1]].index(j['vertex']) for j in js]
        assert r == {'hub': core['vertex_map'][cycle[0]], 'incidences': hs,
                     'marked_cuts': list(range(len(cycle))), 'critical': True, 'junction_indices': ji}
        offset += len(cycle)
    initial_bad = bad_regions(regions, pairs)
    assert len(regions) == 1 and initial_bad == [0]
    assert [r['swap_pair'] for r in g['blocked_attempts']] == AUX
    for rec in g['blocked_attempts']:
        assert verify_attempt(core, regions, pairs, [0], rec, stats, table) is None
    first = g['neutral_exchange']
    assert first['swap_pair'] == 6 and first['selected_ports'] == [2, 6]
    selected = first['edges']
    assert selected == sorted(set(selected))
    assert all((pairs[e] & 6).bit_count() == 1 for e in selected)
    circuit([core['edges'][e] for e in selected])
    assert [i for i,h in enumerate(regions[0]['incidences']) if h//2 in selected] == [2,6]
    neutral = [a ^ 6 if e in selected else a for e,a in enumerate(pairs)]
    valid(core['vertices'], core['edges'], neutral, Q)
    assert [a & 1 for a in neutral] == [a & 1 for a in pairs]
    assert neutral == decode(first['cover_word_after'])
    assert not survivors([neutral[h//2] for h in regions[0]['incidences']], table)
    assert first['bad_before'] == first['bad_after'] == bad_regions(regions, neutral) == [0]
    assert len(selected) == (2 if g['name'] == 'native' else 7)
    if g['name'] == 'petersen_attachment':
        assert set(g['petersen_two_sum']['core_cut_edges']) <= set(selected)
    second = g['repair_exchange']
    assert second['swap_pair'] == 10 and second['selected_ports'] == [3,4]
    pairs = verify_attempt(core, regions, neutral, [0], second, stats, table)
    assert pairs is not None and len(second['edges']) == 3
    circuit([core['edges'][e] for e in second['edges']])
    assert g['minimum_auxiliary_exchanges'] == 2
    assert not bad_regions(regions, pairs) and pairs == decode(g['changed_core_cover_word'])
    qc = decode(g['quotient_cover_word'])
    valid(g['quotient_vertices'], g['quotient_edges'], qc, Q)
    assert qc[:m] == pairs and [r & 1 for r in qc] == [initial[e] & 1 for e in g['kept_edge_ids']]
    for region, extension in zip(regions, g['regional_extensions']):
        js = [g['junctions'][i] for i in region['junction_indices']]
        letters = [[pairs[j['edges'][-1]], sum((initial[e] & 1) << i for i, e in enumerate(j['edges'][:4]))] for j in js]
        assert letters == extension['letters']
        z0 = letters[0][1]
        p = (z0 & 1) ^ (z0 >> 1 & 1)
        allowed = {h for h in EVEN if h & 1 == p}
        at = 0
        for r, z in letters:
            allowed &= {h ^ at for h in table[r, z]}
            at ^= r
        assert at == 0 and sorted(allowed) == extension['surviving_charges'] == [20]
        assert extension['chosen_charge'] == 20
    f = initial.copy()
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
    assert f == list(map(int, g['final_flow_word'])) and all(f[e] == initial[e] for e in g['kept_edge_ids'])
    cover = decode(g['cover_word'])
    valid(n, edges, cover, Q)
    assert [r & 1 for r in cover] == [a & 1 for a in f] and [cover[e] for e in g['kept_edge_ids']] == qc
    if g['core_has_four_flow']:
        valid(core['vertices'], core['edges'], list(map(int, g['core_four_flow_word'])), (1, 2, 3))
    else:
        rec = g['petersen_two_sum']
        local = {core['vertex_map'][v]: i for i, v in enumerate(rec['vertices'])}
        cut = [e for e, (u, v) in enumerate(core['edges']) if (u in local) != (v in local)]
        assert cut == rec['core_cut_edges'] and len(cut) == 2
        restored = [tuple(sorted((local[u], local[v]))) for u, v in core['edges'] if u in local and v in local]
        restored.append(tuple(sorted(local[next(v for v in core['edges'][e] if v in local)] for e in cut)))
        pet = [(i, (i+1) % 5) for i in range(5)]+[(i, i+5) for i in range(5)]
        pet += [(i+5, (i+2) % 5+5) for i in range(5)]
        assert sorted(restored) == sorted(tuple(sorted(e)) for e in pet)
        inc = stars(10, pet)
        even = [s for s in range(1 << 15) if all(sum(s >> e & 1 for e in star) % 2 == 0 for star in inc)]
        assert len(even) == 64 and not any(a | b == (1 << 15)-1 for a in even for b in even)
    print(g['construction'], g['name'], n, 'vertices:', 2, 'core exchanges,',
          len(g['moves']), 'B pentagons; all values on the quotient preserved.', flush=True)


def main():
    saved = json.loads((HERE/'actual_core_exchange_obstruction.json').read_text())
    for src in saved['sources']:
        assert hashlib.sha256((HERE/src['file']).read_bytes()).hexdigest() == src['sha256']
    assert saved['base_vertices'] == 22 and saved['selected_cycle'] == list(range(11))
    assert saved['boundary_word'] == [6,6,10,6,24,6,12,18,20,10,18]
    rows = saved['outside_edges_pairs_four_flow']
    assert len(rows) == 22
    base = [[i,(i+1)%11] for i in range(11)]+[row[:2] for row in rows]
    expected = {
        6: [[2,6],[7,8],[9,10]],
        10: [[0,10],[1,7],[3,4],[5,6]],
        18: [[0,9],[1,2],[3,4],[5,8]],
        12: [[0,3],[1,2],[4,9],[5,8]],
        20: [[0,10],[1,7],[3,4],[5,6]],
        24: [[2,6],[7,8],[9,10]],
    }
    tables = {k:junction_table(k) for k in ('blowup','semi')}
    stats = Counter()
    assert [(g['construction'],g['name']) for g in saved['examples']] == [
        (kind,name) for kind in ('blowup','semi') for name in ('native','petersen_attachment')]
    for g in saved['examples']:
        if g['name'] == 'native':
            assert g['base_vertices'] == 22 and g['base_edges'] == base
            assert decode(g['original_core_cover_word']) == [row[2] for row in rows]
            assert list(map(int,g['core_four_flow_word'])) == [row[3] for row in rows]
        for rec in g['blocked_attempts']:
            assert rec['component_ports'] == expected[rec['swap_pair']]
        example(g,tables[g['construction']],stats)
    assert stats['attempts'] == 28 and stats['failed_attempts'] == 24
    assert stats['realizations'] == 384
    print('Independent checks:',dict(stats))
    print('PASS: all one-step auxiliary exchanges fail; distance two and all four full covers verified.')


if __name__ == '__main__':
    main()
