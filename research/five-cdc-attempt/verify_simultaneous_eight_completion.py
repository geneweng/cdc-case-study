#!/usr/bin/env python3
"""Independent checks of simultaneous eight-cycle completion; stdlib only.

Enumerates all closed words directly and recognizes protected pairings by
crossing every dangerous flip cut. Imports no constructor or earlier verifier.
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


def bad(rs):
    return len(set(prefixes(rs))) == 8


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
    for j in range(i+1, 8):
        if rem >> j & 1:
            for tail in matchings(rem ^ (1 << j)):
                yield ((i, j),)+tail


def check_protection(rs, t, matching):
    affected = [i for i, r in enumerate(rs) if (r & t).bit_count() == 1]
    assert sorted(i for ij in matching for i in ij) == affected
    assert not bad(rs)
    for use in itertools.product((False, True), repeat=len(matching)):
        selected = {i for include, ij in zip(use, matching) if include for i in ij}
        after = [r ^ t if i in selected else r for i, r in enumerate(rs)]
        assert all(r in AUX for r in after) and not bad(after)


def local_protection(saved):
    t, closed, bad_words = 6, 0, set()
    for seven in itertools.product(AUX, repeat=7):
        last = xor(seven)
        if last in AUX:
            closed += 1
            rs = seven+(last,)
            if bad(rs):
                bad_words.add(rs)
    assert saved['swap_pair'] == t
    assert closed == saved['closed_boundary_words'] == 210048
    assert len(bad_words) == saved['bad_words'] == 1488
    groups = defaultdict(set)
    for rs in bad_words:
        # Also independently establish the escaping-choice lemma used at a target.
        choices = []
        for swap in AUX:
            active = [i for i, r in enumerate(rs) if (r & swap).bit_count() == 1]
            nonescaping = sum(bad(tuple(r ^ swap if k in (i, j) else r for k, r in enumerate(rs)))
                              for i, j in itertools.combinations(active, 2))
            if len(active) >= 4 and nonescaping <= 1:
                choices.append(swap)
        assert choices
        key = tuple(min(r, r ^ t) if (r & t).bit_count() == 1 else r for r in rs)
        groups[key].add(sum(1 << i for i, r in enumerate(rs) if r != key[i]))
    rows, hist, states = [], Counter(), 0
    for key, bad_assignments in groups.items():
        active = sum(1 << i for i, r in enumerate(key) if (r & t).bit_count() == 1)
        all_matchings = list(matchings(active))
        for bits in range(256):
            if bits & ~active:
                continue
            rs = tuple(r ^ t if bits >> i & 1 else r for i, r in enumerate(key))
            if xor(rs):
                continue
            states += 1
            if rs in bad_words:
                assert bits in bad_assignments
                continue
            dangerous = {bits ^ b for b in bad_assignments}
            # A union of matched pairs is constant on every pair. A matching
            # is protected iff it crosses each dangerous subset's cut.
            safe = [matching for matching in all_matchings
                    if all(any(((d >> i) ^ (d >> j)) & 1 for i, j in matching) for d in dangerous)]
            assert safe
            chosen = min(safe)
            check_protection(rs, t, chosen)
            hist[len(safe)] += 1
            rows.append([list(rs), len(safe), [list(ij) for ij in chosen]])
    assert len(groups) == saved['threat_groups'] == 462
    assert states == saved['states_in_threat_groups'] == 10848
    assert len(rows) == saved['good_states_requiring_check'] == 9360
    assert closed-states == saved['automatically_safe_good_states'] == 199200
    assert [list(x) for x in sorted(hist.items())] == saved['protected_pairing_count_histogram']
    encoded = json.dumps(sorted(rows), separators=(',', ':')).encode()
    assert hashlib.sha256(encoded).hexdigest() == saved['witness_sha256']
    unique = saved['unique_pairing_example']
    rec = next(row for row in rows if row[0] == unique['boundary_pairs'])
    assert unique['swap_pair'] == t and rec[1] == 1 and rec[2] == unique['pairing']
    print('Verified 210,048 closed words, all 1,488 escaping choices, and all 9,360 threatened good states.', flush=True)


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
    assert g['pieces'] == q and all(len(c) == 8 for c in cycles)
    assert len(g['blocks']) == len(g['junctions']) == q
    assert len(g['regions']) == len(g['regional_extensions']) == len(g['port_orders']) == len(cycles)
    assert all(sorted(order) == list(range(8)) for order in g['port_orders'])
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
    return [i for i, r in enumerate(regions) if r['critical'] and bad([pairs[h//2] for h in r['incidences']])]


def example(g, table):
    m = reconstruct(g)
    n, edges, core, regions = g['vertices'], g['edges'], g['core'], g['regions']
    initial = list(map(int, g['initial_flow_word']))
    valid(n, edges, initial, range(1, 8))
    pairs = decode(g['original_core_cover_word'])
    valid(core['vertices'], core['edges'], pairs, Q)
    assert [r & 1 for r in pairs] == [a & 1 for a in initial[:m]]
    offset = 0
    for cycle, r in zip(g['selected_cycles'], regions):
        ji = list(range(offset, offset+len(cycle)))
        js = [g['junctions'][i] for i in ji]
        zs = [sum((initial[e] & 1) << i for i, e in enumerate(j['edges'][:4])) for j in js]
        marked = [i for i in range(len(cycle)) if zs[i] & 3 == 3 or zs[i-1] & 12 == 12]
        hs = [2*j['edges'][-1]+edges[j['edges'][-1]].index(j['vertex']) for j in js]
        assert r == {'hub': core['vertex_map'][cycle[0]], 'incidences': hs,
                     'marked_cuts': marked, 'critical': len(cycle) == len(marked) == 8, 'junction_indices': ji}
        offset += len(cycle)
    initial_bad = bad_regions(regions, pairs)
    assert len(g['core_cover_moves']) <= len(initial_bad)
    if 'unprotected_exchange' in g:
        rec = g['unprotected_exchange']
        es, t = rec['edges'], rec['swap_pair']
        circuit([core['edges'][e] for e in es])
        assert all((pairs[e] & t).bit_count() == 1 for e in es)
        naive = [r ^ t if e in es else r for e, r in enumerate(pairs)]
        valid(core['vertices'], core['edges'], naive, Q)
        assert naive == decode(rec['cover_word_after'])
        assert rec['bad_before'] == initial_bad == [0] and rec['bad_after'] == bad_regions(regions, naive) == [1]
    repeated_protected = False
    for move in g['core_cover_moves']:
        before = bad_regions(regions, pairs)
        assert before == move['bad_before'] and move['target_region'] in before
        target, t = regions[move['target_region']], move['swap_pair']
        assert t in AUX
        path = move['trail_incidences']
        es = [h//2 for h in path]
        assert len(es) == len(set(es)) and es
        starts = [core['edges'][h//2][h % 2] for h in path]
        ends = [core['edges'][h//2][1-h % 2] for h in path]
        assert starts[1:] == ends[:-1] and starts[0] == ends[-1] == target['hub']
        assert target['hub'] not in ends[:-1]
        assert all((pairs[e] & t).bit_count() == 1 for e in es)
        assert move['ports'] == [target['incidences'].index(path[0]), target['incidences'].index(path[-1] ^ 1)]
        protected = [i for i, r in enumerate(regions) if r['critical'] and i not in before]
        assert [r['region'] for r in move['protected_pairings']] == protected
        for rec in move['protected_pairings']:
            r = regions[rec['region']]
            rs = [pairs[h//2] for h in r['incidences']]
            check_protection(rs, t, rec['pairs'])
            changed_ports = {i for i, h in enumerate(r['incidences']) if h//2 in es}
            assert all((i in changed_ports) == (j in changed_ports) for i, j in rec['pairs'])
            repeated_protected |= len(changed_ports) >= 4
        following = [r ^ t if e in es else r for e, r in enumerate(pairs)]
        valid(core['vertices'], core['edges'], following, Q)
        assert [r & 1 for r in following] == [r & 1 for r in pairs]
        assert following == decode(move['cover_word_after'])
        after = bad_regions(regions, following)
        assert after == move['bad_after'] and set(after) < set(before) and move['target_region'] not in after
        pairs = following
    assert not bad_regions(regions, pairs) and pairs == decode(g['changed_core_cover_word'])
    if g['name'] == 'repeated_good_vertex':
        assert repeated_protected
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
    print(g['construction'], g['name'], n, 'vertices:', len(g['core_cover_moves']), 'protected exchanges,',
          len(g['moves']), 'B pentagons; all values on the quotient preserved.', flush=True)


def main():
    saved = json.loads((HERE / 'simultaneous_eight_completion.json').read_text())
    for src in saved['sources']:
        assert hashlib.sha256((HERE / src['file']).read_bytes()).hexdigest() == src['sha256']
    local_protection(saved['local_protection'])
    tables = {k: junction_table(k) for k in ('blowup', 'semi')}
    assert len(saved['examples']) == 8
    for g in saved['examples']:
        example(g, tables[g['construction']])
    print('PASS: simultaneous eight-cycle completion and all full graph certificates.')


if __name__ == '__main__':
    main()
