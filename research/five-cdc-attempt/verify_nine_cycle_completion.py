#!/usr/bin/env python3
"""Independent finite proof and graph checks for nine-cycle completion; stdlib only.

Enumerates repeated prefix states and recognizes protected pairings by
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


def check_protection(rs, t, matching, marked):
    affected = [i for i, r in enumerate(rs) if (r & t).bit_count() == 1]
    assert sorted(i for ij in matching for i in ij) == affected
    assert not bad(rs, marked)
    for use in itertools.product((False, True), repeat=len(matching)):
        selected = {i for include, ij in zip(use, matching) if include for i in ij}
        after = [r ^ t if i in selected else r for i, r in enumerate(rs)]
        assert all(r in Q for r in after) and not bad(after, marked)
        assert [r & 1 for r in after] == [r & 1 for r in rs]


def local_cases(saved):
    pattern_counts = Counter()
    for missing in (None, *range(9)):
        marked_mask = 511 if missing is None else 511 ^ (1 << missing)
        for parity in range(512):
            if parity & marked_mask:
                continue
            core_bits = [(parity >> i & 1) ^ (parity >> ((i+1) % 9) & 1) for i in range(9)]
            if missing is None:
                assert not any(core_bits)
                pattern_counts['all_marked'] += 1
            else:
                rotated = core_bits[missing:]+core_bits[:missing]
                assert rotated in ([0]*9, [1]+[0]*7+[1])
                pattern_counts['unmarked_odd' if parity else 'unmarked_even'] += 1
    assert pattern_counts == {'all_marked': 1, 'unmarked_even': 9, 'unmarked_odd': 9}
    space = [h for h in EVEN if not h & 1]
    words = {k: set() for k in ('all_marked', 'unmarked_even', 'unmarked_odd')}
    def accept(pref, odd=False):
        rs = tuple(pref[i] ^ pref[(i+1) % 9] for i in range(9))
        if odd:
            if rs[0] in Q[:4] and rs[-1] in Q[:4] and all(r in AUX for r in rs[1:-1]):
                words['unmarked_odd'].add(rs)
        elif all(r in AUX for r in rs):
            words['all_marked'].add(rs)
            if len(set(pref[1:])) == 8:
                words['unmarked_even'].add(rs)
    # In type A, nine prefix slots cover all eight states, so precisely one
    # state is repeated. Enumerate that state and its two positions directly.
    for perm in itertools.permutations(space):
        accept((0,)+perm)
    for repeated in space[1:]:
        remaining = [h for h in space if h not in (0, repeated)]
        for positions in itertools.combinations(range(1, 9), 2):
            for perm in itertools.permutations(remaining):
                it = iter(perm)
                pref = (0,)+tuple(repeated if i in positions else next(it) for i in range(1, 9))
                accept(pref)
    for perm in itertools.permutations([h for h in EVEN if h & 1]):
        accept((0,)+perm, True)
    expected = {'all_marked': (1259520, 33264, 5976, 151920),
                'unmarked_even': (1259520, 7392, 1760, 51328),
                'unmarked_odd': (559872, 2976, 852, 20592)}
    assert set(saved) == set(words)
    for kind, bads in words.items():
        record = saved[kind]
        marked = list(range(9) if kind == 'all_marked' else range(1, 9))
        assert record['marked_cuts'] == marked
        alphabets = [Q[:4] if kind == 'unmarked_odd' and i in (0, 8) else AUX for i in range(9)]
        # Meet-in-the-middle counting, independent of the constructor's walk DP.
        left = Counter(xor(rs) for rs in itertools.product(*alphabets[:4]))
        right = Counter(xor(rs) for rs in itertools.product(*alphabets[4:]))
        total = sum(n*right[s] for s, n in left.items())
        assert total == record['closed_words'] == expected[kind][0]
        assert len(bads) == record['bad_words'] == expected[kind][1]
        ordered = sorted(bads)
        assert hashlib.sha256(json.dumps([list(r) for r in ordered], separators=(',', ':')).encode()).hexdigest() == record['bad_words_sha256']
        groups = defaultdict(set)
        for rs in bads:
            key = tuple(min(r, r ^ 6) if (r & 6).bit_count() == 1 else r for r in rs)
            groups[key].add(sum(1 << i for i, r in enumerate(rs) if r != key[i]))
        rows, hist, states, fixed_counts = [], Counter(), 0, {}
        for key, bad_assignments in groups.items():
            mask = sum(1 << i for i, r in enumerate(key) if (r & 6).bit_count() == 1)
            candidates = list(matchings(mask))
            for bits in range(512):
                if bits & ~mask:
                    continue
                rs = tuple(r ^ 6 if bits >> i & 1 else r for i, r in enumerate(key))
                if xor(rs):
                    continue
                states += 1
                if rs in bads:
                    # Exhaust the outside matchings rather than using the
                    # constructor's dynamic program for perfect matchings.
                    fixed_counts[rs] = sum(all(bits ^ (1 << i) ^ (1 << j) in bad_assignments for i, j in m)
                                           for m in candidates)
                    continue
                dangerous = {bits ^ b for b in bad_assignments}
                safe = [m for m in candidates if all(any(((d >> i) ^ (d >> j)) & 1 for i, j in m) for d in dangerous)]
                assert safe
                chosen = min(safe)
                check_protection(rs, 6, chosen, marked)
                hist[len(safe)] += 1
                rows.append([list(rs), len(safe), [list(ij) for ij in chosen]])
        assert len(groups) == record['threat_groups'] == expected[kind][2]
        assert len(rows) == record['good_states_checked'] == expected[kind][3]
        assert states == record['states_in_threat_groups'] == len(rows)+len(bads)
        assert total-states == record['automatically_safe_good_states']
        assert [list(x) for x in sorted(hist.items())] == record['protected_pairing_count_histogram']
        assert hashlib.sha256(json.dumps(sorted(rows), separators=(',', ':')).encode()).hexdigest() == record['protection_sha256']
        assert [list(x) for x in sorted(Counter(fixed_counts.values()).items())] == record['fixed_pair_nonescaping_matching_histogram']
        escape_rows = [[list(rs), fixed_counts[rs]] for rs in ordered]
        assert hashlib.sha256(json.dumps(escape_rows, separators=(',', ':')).encode()).hexdigest() == record['escape_sha256']
        # Use the last permissible permutation, not the constructor's direct
        # sorted-label map. Counts are invariant under stabilizers of {1,2}.
        maps = {}
        for t in AUX:
            maps[t] = max(p for p in itertools.permutations(range(1, 5))
                          if sum(1 << p[i-1] for i in range(1, 5) if t >> i & 1) == 6)
        forcing = Counter()
        for rs in ordered:
            n = 0
            for t, p in maps.items():
                transformed = tuple((r & 1) | sum(1 << p[i-1] for i in range(1, 5) if r >> i & 1) for r in rs)
                n += fixed_counts[transformed] == 0
            assert n
            forcing[n] += 1
        assert [list(x) for x in sorted(forcing.items())] == record['forcing_pair_histogram']
        print(kind, 'verified', len(bads), 'bad cases and', len(rows), 'protected good cases.', flush=True)

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
    assert g['pieces'] == q and all(3 <= len(c) <= 9 for c in cycles)
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


def example(g, table):
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
        marked = [i for i in range(len(cycle)) if zs[i] & 3 == 3 or zs[i-1] & 12 == 12]
        profile = g['profile_names'][region_index]
        assert profile in ('eight', 'all_marked', 'unmarked_even', 'unmarked_odd')
        assert len(cycle) == (8 if profile == 'eight' else 9)
        assert marked == list(range(len(cycle)) if profile in ('eight', 'all_marked') else range(1, 9))
        core_bits = [pairs[j['edges'][-1]] & 1 for j in js]
        assert core_bits == ([1]+[0]*7+[1] if profile == 'unmarked_odd' else [0]*len(cycle))
        hs = [2*j['edges'][-1]+edges[j['edges'][-1]].index(j['vertex']) for j in js]
        assert r == {'hub': core['vertex_map'][cycle[0]], 'incidences': hs,
                     'marked_cuts': marked, 'critical': len(marked) >= 8, 'junction_indices': ji}
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
        assert initial_bad == rec['bad_before'] == [0] and bad_regions(regions, naive) == rec['bad_after'] == [1]
    else:
        assert initial_bad == list(range(len(regions)))
    protected_visits = 0
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
            check_protection(rs, t, rec['pairs'], r['marked_cuts'])
            changed_ports = {i for i, h in enumerate(r['incidences']) if h//2 in es}
            assert all((i in changed_ports) == (j in changed_ports) for i, j in rec['pairs'])
            protected_visits += bool(changed_ports) and len(r['incidences']) == 9
        following = [r ^ t if e in es else r for e, r in enumerate(pairs)]
        valid(core['vertices'], core['edges'], following, Q)
        assert [r & 1 for r in following] == [r & 1 for r in pairs]
        assert following == decode(move['cover_word_after'])
        after = bad_regions(regions, following)
        assert after == move['bad_after'] and set(after) < set(before) and move['target_region'] not in after
        pairs = following
    assert not bad_regions(regions, pairs) and pairs == decode(g['changed_core_cover_word'])
    if g['name'] == 'protected_distinguished_region':
        assert protected_visits >= 1
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
    saved = json.loads((HERE / 'nine_cycle_completion.json').read_text())
    for src in saved['sources']:
        assert hashlib.sha256((HERE / src['file']).read_bytes()).hexdigest() == src['sha256']
    local_cases(saved['local_cases'])
    tables = {k: junction_table(k) for k in ('blowup', 'semi')}
    assert len(saved['examples']) == 10
    for g in saved['examples']:
        example(g, tables[g['construction']])
    print('PASS: simultaneous completion through length nine and all full graph certificates.')


if __name__ == '__main__':
    main()
