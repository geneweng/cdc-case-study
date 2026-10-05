#!/usr/bin/env python3
"""Independent finite proof and graph checks for eleven-cycle obstruction; stdlib only.

Independently rebuilds graph, layer, exchange, and flow certificates.
Exhausts every outside pairing and every subset; no constructor is imported.
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


def matchings(mask):
    if not mask:
        yield ()
        return
    i = (mask & -mask).bit_length()-1
    rem = mask ^ (1 << i)
    for j in range(i+1, mask.bit_length()):
        if rem >> j & 1:
            for tail in matchings(rem ^ (1 << j)):
                yield ((i, j),)+tail


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
    assert g['pieces'] == q and all(len(c) == 11 for c in cycles)
    assert len(g['blocks']) == len(g['junctions']) == q
    assert len(g['regions']) == len(g['regional_extensions']) == len(g['profile_names']) == len(cycles)
    assert len({v for c in cycles for v in c}) == q
    assert all(len(s) == 3 for s in stars(n, base))
    assert len({tuple(sorted(e)) for e in base}) == len(base) and all(u != v for u, v in base)
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


def classify(records):
    expected = set()
    for digits in itertools.product(range(3), repeat=11):
        if sum(d != 0 for d in digits) <= 3:
            expected.add((sum(1 << i for i, d in enumerate(digits) if d == 0),
                          sum(1 << i for i, d in enumerate(digits) if d == 2)))
    seen, histogram = set(), Counter()
    for rec in records:
        marked, odd = rec['marked_mask'], rec['odd_cut_mask']
        assert odd & marked == 0
        digits = tuple(0 if marked >> i & 1 else 2 if odd >> i & 1 else 1 for i in range(11))
        orbit = set()
        for direction in (digits, digits[::-1]):
            for k in range(11):
                rotated = direction[k:]+direction[:k]
                orbit.add((sum(1 << i for i, d in enumerate(rotated) if d == 0),
                           sum(1 << i for i, d in enumerate(rotated) if d == 2)))
        assert orbit <= expected and not orbit & seen
        assert len(orbit) == rec['labelled_patterns']
        seen |= orbit
        histogram[11-marked.bit_count()] += 1
    assert seen == expected and len(expected) == 1563 and len(records) == 88
    assert histogram == {0: 1, 1: 2, 2: 15, 3: 70}


def survivors(rs, table):
    allowed = {h for h in EVEN if not h & 1}
    prefix = 0
    for r in rs:
        allowed &= {h ^ prefix for h in table[r, 15]}
        prefix ^= r
    assert prefix == 0
    return allowed


def local_witnesses(records, tables):
    expected = {
        'two_trails': [6, 10, 6, 12, 20, 6, 10, 20, 18, 12, 20],
        'blocked_unions': [6, 6, 10, 6, 24, 6, 12, 18, 20, 10, 18],
    }
    tested = 0
    for name, rec in records.items():
        rs = rec['word']
        assert rs == expected[name] and rec['marked_cuts'] == list(range(11))
        assert all(r in AUX for r in rs) and xor(rs) == 0
        assert all(not survivors(rs, table) for table in tables.values())
        assert [s['swap_pair'] for s in rec['swaps']] == [6, 10, 18, 12, 20, 24]
        for saved in rec['swaps']:
            t = saved['swap_pair']
            active = sum(1 << i for i, a in enumerate(rs) if (a & t).bit_count() == 1)
            assert [i for i in range(11) if active >> i & 1] == saved['affected_ports']
            hist, no_single, blocked, cases = Counter(), [], [], 0
            for matching in matchings(active):
                minimum = None
                for use in itertools.product((0, 1), repeat=len(matching)):
                    changed = rs.copy()
                    for include, (i, j) in zip(use, matching):
                        if include:
                            changed[i] ^= t
                            changed[j] ^= t
                    choices = [survivors(changed, table) for table in tables.values()]
                    assert choices[0] == choices[1]
                    assert bool(choices[0]) == (not bad(changed))
                    if choices[0]:
                        minimum = min(minimum if minimum is not None else 99, sum(use))
                    cases += 1
                outcome = minimum if minimum is not None else -1
                hist[outcome] += 1
                if outcome != 1:
                    no_single.append([list(ij) for ij in matching])
                if outcome == -1:
                    blocked.append([list(ij) for ij in matching])
            assert saved['minimum_trails_histogram'] == [list(row) for row in sorted(hist.items())]
            assert saved['no_single_escape_pairings'] == no_single and no_single
            assert saved['fully_blocked_pairings'] == blocked
            assert saved['matchings'] == sum(hist.values()) and cases == saved['subsets_checked']
            tested += cases
        if name == 'blocked_unions':
            assert all(s['fully_blocked_pairings'] for s in rec['swaps'])
            # Complementary swaps have the same affected ports in an all-AUX
            # core, but these two unique blocking pairings are incompatible.
            a = next(s for s in rec['swaps'] if s['swap_pair'] == 18)
            b = next(s for s in rec['swaps'] if s['swap_pair'] == 12)
            assert len(a['fully_blocked_pairings']) == len(b['fully_blocked_pairings']) == 1
            assert a['fully_blocked_pairings'] != b['fully_blocked_pairings']
        else:
            assert [s['swap_pair'] for s in rec['swaps'] if not s['fully_blocked_pairings']] == [18]
            row = next(s for s in rec['swaps'] if s['swap_pair'] == 18)
            assert row['minimum_trails_histogram'] == [[1, 104], [2, 1]]
        print(name, 'all six swaps, all outside pairings and all subsets verified.', flush=True)
    assert tested == 13920
    print('Verified 13,920 matching/subset cases against both junction tables.', flush=True)


def check_trails(core, regions, pairs, rec):
    t, trails, matching = rec['swap_pair'], rec['trails'], rec['outside_matching']
    target, other = regions
    assert t in AUX
    actual_ports, other_ports, edges = [], [], []
    for trail in trails:
        path = trail['incidences']
        assert path
        es = [h//2 for h in path]
        edges.extend(es)
        starts = [core['edges'][h//2][h % 2] for h in path]
        ends = [core['edges'][h//2][1-h % 2] for h in path]
        assert starts[1:] == ends[:-1] and starts[0] == ends[-1] == target['hub']
        assert target['hub'] not in ends[:-1]
        assert all((pairs[e] & t).bit_count() == 1 for e in es)
        ports = [target['incidences'].index(path[0]), target['incidences'].index(path[-1] ^ 1)]
        assert ports == trail['ports']
        actual_ports.append(tuple(sorted(ports)))
        for i in range(1, len(path)):
            if starts[i] == other['hub']:
                a, b = other['incidences'].index(path[i-1] ^ 1), other['incidences'].index(path[i])
                other_ports.append(tuple(sorted((a, b))))
    assert len(edges) == len(set(edges))
    expected = sorted(tuple(p) for p in matching)
    assert sorted(actual_ports) == sorted(other_ports) == expected
    for region in regions:
        active = [i for i, h in enumerate(region['incidences']) if (pairs[h//2] & t).bit_count() == 1]
        assert sorted(i for ij in matching for i in ij) == active
    outcomes = {}
    for use in itertools.product((0, 1), repeat=len(trails)):
        es = {h//2 for include, trail in zip(use, trails) if include for h in trail['incidences']}
        after = [a ^ t if e in es else a for e, a in enumerate(pairs)]
        valid(core['vertices'], core['edges'], after, Q)
        assert [a & 1 for a in after] == [a & 1 for a in pairs]
        outcomes[tuple(i for i, yes in enumerate(use) if yes)] = after
    return outcomes


def example(g, table, local):
    m = reconstruct(g)
    n, edges, core, regions = g['vertices'], g['edges'], g['core'], g['regions']
    initial = list(map(int, g['initial_flow_word']))
    valid(n, edges, initial, range(1, 8))
    pairs = decode(g['original_core_cover_word'])
    valid(core['vertices'], core['edges'], pairs, Q)
    assert [r & 1 for r in pairs] == [a & 1 for a in initial[:m]]
    assert len(regions) == 2 and g['pieces'] == 22 and g['profile_names'] == [g['name']]*2
    for offset, (cycle, r) in zip((0, 11), zip(g['selected_cycles'], regions)):
        ji = list(range(offset, offset+11))
        js = [g['junctions'][i] for i in ji]
        zs = [sum((initial[e] & 1) << i for i, e in enumerate(j['edges'][:4])) for j in js]
        assert zs == [15]*11
        assert [pairs[j['edges'][-1]] for j in js] == local['word']
        hs = [2*j['edges'][-1]+edges[j['edges'][-1]].index(j['vertex']) for j in js]
        assert r == {'hub': core['vertex_map'][cycle[0]], 'incidences': hs,
                     'marked_cuts': list(range(11)), 'critical': True, 'junction_indices': ji}
    assert bad_regions(regions, pairs) == [0, 1]
    if g['name'] == 'blocked_unions':
        assert [r['swap_pair'] for r in g['pairing_trials']] == [6, 10, 18, 12, 20, 24]
        for trial in g['pairing_trials']:
            row = next(s for s in local['swaps'] if s['swap_pair'] == trial['swap_pair'])
            assert trial['outside_matching'] in row['fully_blocked_pairings']
            outcomes = check_trails(core, regions, pairs, trial)
            assert all(bad_regions(regions, after) == [0, 1] for after in outcomes.values())
    else:
        assert g['pairing_trials'] == []
    move = g['core_exchange']
    outcomes = check_trails(core, regions, pairs, move)
    escaping = [len(chosen) for chosen, after in outcomes.items() if not bad_regions(regions, after)]
    assert min(escaping) == (2 if g['name'] == 'two_trails' else 1)
    assert len(move['selected_trails']) == min(escaping)
    pairs = outcomes[tuple(move['selected_trails'])]
    assert move['bad_before'] == [0, 1] and move['bad_after'] == []
    assert not bad_regions(regions, pairs)
    assert pairs == decode(move['cover_word_after']) == decode(g['changed_core_cover_word'])
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
        assert at == 0 and sorted(allowed) == extension['surviving_charges'] and extension['chosen_charge'] in allowed
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
    print(g['construction'], g['name'], n, 'vertices:', len(g['core_exchange']['selected_trails']), 'selected trails,',
          len(g['moves']), 'B pentagons; all values on the quotient preserved.', flush=True)
def main():
    saved = json.loads((HERE/'eleven_cycle_obstruction.json').read_text())
    for src in saved['sources']:
        assert hashlib.sha256((HERE/src['file']).read_bytes()).hexdigest() == src['sha256']
    classify(saved['pattern_classification'])
    tables = {k: junction_table(k) for k in ('blowup', 'semi')}
    local_witnesses(saved['local_witnesses'], tables)
    assert len(saved['examples']) == 8
    for g in saved['examples']:
        example(g, tables[g['construction']], saved['local_witnesses'][g['name']])
    print('PASS: local escape obstruction and all eight positive graph certificates.')


if __name__ == '__main__':
    main()
