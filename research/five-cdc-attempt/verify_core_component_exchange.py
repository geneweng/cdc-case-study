#!/usr/bin/env python3
"""Independent partition and linear-algebra checks for core component exchanges.

Independently rebuilds graph, layer, exchange, and flow certificates.
Computes the binary kernel of exchange constraints; no constructor is imported.
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
    assert g['pieces'] == q and all(3 <= len(c) <= 11 for c in cycles)
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


def survivors(rs, table):
    allowed = {h for h in EVEN if not h & 1}
    at = 0
    for r in rs:
        allowed &= {h ^ at for h in table[r, 15]}
        at ^= r
    assert at == 0
    return allowed


def partitions(active):
    def assign(i, blocks):
        if i == len(active):
            if all(len(b) % 2 == 0 for b in blocks):
                yield tuple(tuple(b) for b in blocks)
            return
        for j in range(len(blocks)):
            blocks[j].append(active[i])
            yield from assign(i+1, blocks)
            blocks[j].pop()
        yield from assign(i+1, blocks+[[active[i]]])
    yield from assign(0, [])


def verify_partitions(saved, tables):
    expected = {
        'two_trails': [6, 10, 6, 12, 20, 6, 10, 20, 18, 12, 20],
        'blocked_unions': [6, 6, 10, 6, 24, 6, 12, 18, 20, 10, 18],
    }
    total_partitions = total_subsets = 0
    for name, rec in saved.items():
        rs = rec['word']
        outcomes = {}
        assert rs == expected[name]
        assert [r['swap_pair'] for r in rec['swaps']] == [6, 10, 18, 12, 20, 24]
        for row in rec['swaps']:
            t = row['swap_pair']
            active = [i for i, a in enumerate(rs) if (a & t).bit_count() == 1]
            assert active == row['affected_ports']
            blocked, histogram, count, checked = [], Counter(), 0, 0
            for blocks in partitions(active):
                count += 1
                masks = [sum(1 << i for i in b) for b in blocks]
                minimum = None
                # Direct subset/parity enumeration, without the constructor's
                # star-generated subspaces or even-block-first recursion.
                for subset in range(1 << len(active)):
                    mask = sum(1 << i for j, i in enumerate(active) if subset >> j & 1)
                    if any((mask & b).bit_count() % 2 for b in masks):
                        continue
                    after = [a ^ t if mask >> i & 1 else a for i, a in enumerate(rs)]
                    answers = [survivors(after, table) for table in tables.values()]
                    assert answers[0] == answers[1] and bool(answers[0]) == (not bad(after))
                    if answers[0]:
                        minimum = min(minimum if minimum is not None else 99, mask.bit_count()//2)
                    checked += 1
                histogram[minimum if minimum is not None else -1] += 1
                if t in (18, 12):
                    outcomes[t, blocks] = minimum
                if minimum is None:
                    blocked.append([list(b) for b in blocks])
            assert count == row['partitions'] and checked == row['subsets_checked']
            assert sorted(blocked) == row['blocked_partitions']
            assert [list(r) for r in sorted(histogram.items())] == row['minimum_terminal_pairs_histogram']
            total_partitions += count
            total_subsets += checked
        joint = Counter()
        for t, blocks in outcomes:
            if t == 18:
                choices = [outcomes[s, blocks] for s in (18, 12) if outcomes[s, blocks] is not None]
                assert choices
                joint[min(choices)] += 1
        assert rec['shared_partition_14_23_histogram'] == [list(r) for r in sorted(joint.items())] == [[1, 378], [2, 1]]
        print(name, 'all component partitions and admissible port subsets verified.', flush=True)
    assert total_partitions == 3156 and total_subsets == 102048


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


def verify_rim_census(saved):
    rs = saved['boundary_word']
    assert rs == [6, 6, 10, 6, 24, 6, 12, 18, 20, 10, 18]
    colors = (2, 4, 8, 16)
    options = [list(matchings(sum(1 << i for i, a in enumerate(rs) if a & c))) for c in colors]
    escaping = {t: {sum(1 << i for i in p) for p in itertools.combinations(
                       [i for i, a in enumerate(rs) if (a & t).bit_count() == 1], 2)
                   if not bad([a ^ t if i in p else a for i, a in enumerate(rs)])} for t in AUX}
    candidates, simple, histogram, hardest = 0, 0, Counter(), []
    for choice in itertools.product(*options):
        candidates += 1
        rim = [(i, j, c) for c, matching in zip(colors, choice) for i, j in matching]
        if len({frozenset((i, j)) for i, j, _ in rim}) != 11:
            continue
        simple += 1
        core = {'vertices': 12, 'edges': [[0, i+1] for i in range(11)]+[[i+1, j+1] for i, j, _ in rim]}
        pairs = rs+[1 | c for _, _, c in rim]
        valid(12, core['edges'], pairs, Q)
        regions = [{'incidences': [2*i for i in range(11)]}]
        choices, rows = 0, []
        for t in (6, 10, 18, 12, 20, 24):
            rec = {'swap_pair': t, 'target_region': 0, 'protected_pairings': []}
            image, _, _, _ = kernel_image(core, regions, pairs, rec)
            # Recover terminal paths from the projected binary cycle space,
            # without the constructor's colored-rim path walk.
            blocks = [tuple(i for i in range(11) if s >> i & 1) for s in image if s.bit_count() == 2]
            blocks.sort()
            active = [i for i, a in enumerate(rs) if (a & t).bit_count() == 1]
            assert sorted(i for b in blocks for i in b) == active
            assert len(image) == 1 << len(blocks)
            good = sorted(tuple(i for i in range(11) if s >> i & 1) for s in image & escaping[t])
            choices += bool(good)
            rows.append({'swap_pair': t, 'component_ports': [list(b) for b in blocks],
                         'escaping_single_pairs': [list(p) for p in good]})
        assert choices >= 2
        histogram[choices] += 1
        if choices == 2:
            hardest.append({'rim_edges': [list(e) for e in rim], 'swaps': rows})
    assert candidates == saved['colored_pairings'] == 14175
    assert simple == saved['simple_rim_realizations'] == 10812
    assert saved['single_escape_swap_histogram'] == [list(r) for r in sorted(histogram.items())]
    assert saved['single_escape_swap_histogram'] == [[2, 1], [3, 34], [4, 427], [5, 2874], [6, 7476]]
    assert hardest == [saved['hardest']]
    assert [r['swap_pair'] for r in hardest[0]['swaps'] if r['escaping_single_pairs']] == [10, 20]
    # Certify the stronger claim for the hardest rim: its other four swaps
    # fail for every union of terminal paths, not just for single paths.
    for row in hardest[0]['swaps']:
        t, blocks = row['swap_pair'], row['component_ports']
        minimum = None
        for use in itertools.product((0, 1), repeat=len(blocks)):
            ports = {i for yes, block in zip(use, blocks) if yes for i in block}
            if not bad([a ^ t if i in ports else a for i, a in enumerate(rs)]):
                minimum = min(minimum if minimum is not None else 99, len(ports)//2)
        assert minimum == (1 if t in (10, 20) else None)
    print('All 10,812 simple colored rims verified with 64,872 binary-kernel projections.', flush=True)


def verify_attempt(core, regions, pairs, before, rec, stats):
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
    escaping = {s for s in image if not bad([a ^ t if s >> i & 1 else a for i, a in enumerate(rs)], target['marked_cuts'])}
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
        expected = {8: [6, 10, 6, 18]*2,
                    10: [6, 6, 10, 6, 18, 6, 6, 10, 6, 18],
                    11: [6, 6, 10, 6, 24, 6, 12, 18, 20, 10, 18]}[len(cycle)]
        if g['name'] == 'protected_neighbor' and region_index == 1:
            expected[0], expected[2] = expected[2], expected[0]
        assert [pairs[j['edges'][-1]] for j in js] == expected
        hs = [2*j['edges'][-1]+edges[j['edges'][-1]].index(j['vertex']) for j in js]
        assert r == {'hub': core['vertex_map'][cycle[0]], 'incidences': hs,
                     'marked_cuts': list(range(len(cycle))), 'critical': True, 'junction_indices': ji}
        offset += len(cycle)
    initial_bad = bad_regions(regions, pairs)
    if 'unprotected_exchange' in g:
        rec = g['unprotected_exchange']
        naive = [a ^ rec['swap_pair'] if e in rec['edges'] else a for e, a in enumerate(pairs)]
        valid(core['vertices'], core['edges'], naive, Q)
        assert naive == decode(rec['cover_word_after'])
        assert initial_bad == rec['bad_before'] == [0]
        assert bad_regions(regions, naive) == rec['bad_after'] == [1]
    else:
        assert initial_bad == list(range(len(regions)))
    if g['name'].startswith('native_rim'):
        rec = g['core_cover_moves'][0]['attempts'][0]
        assert rec['swap_pair'] == 18 and rec['protected_pairings'] == []
        assert rec['component_ports'] == [[0, 9], [1, 2], [3, 4], [5, 8]]
        assert rec['reachable_masks'] == 16 and rec['escaping_masks'] == 0
    assert len(g['core_cover_moves']) <= len(initial_bad)
    for move in g['core_cover_moves']:
        before = bad_regions(regions, pairs)
        assert before == move['bad_before']
        assert move['attempts'] and len({r['swap_pair'] for r in move['attempts']}) == len(move['attempts'])
        for rec in move['attempts'][:-1]:
            assert verify_attempt(core, regions, pairs, before, rec, stats) is None
        following = verify_attempt(core, regions, pairs, before, move['attempts'][-1], stats)
        assert following is not None
        after = bad_regions(regions, following)
        assert after == move['bad_after'] and set(after) < set(before)
        pairs = following
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
    print(g['construction'], g['name'], n, 'vertices:', len(g['core_cover_moves']), 'core exchanges,',
          len(g['moves']), 'B pentagons; all values on the quotient preserved.', flush=True)


def main():
    saved = json.loads((HERE/'core_component_exchange.json').read_text())
    for src in saved['sources']:
        assert hashlib.sha256((HERE/src['file']).read_bytes()).hexdigest() == src['sha256']
    tables = {k: junction_table(k) for k in ('blowup', 'semi')}
    verify_partitions(saved['component_partitions'], tables)
    verify_rim_census(saved['rim_census'])
    assert len(saved['examples']) == 12
    stats = Counter()
    for g in saved['examples']:
        example(g, tables[g['construction']], stats)
    assert stats['protected_visits'] > 0 and stats['realizations_using_target_loop'] > 0
    print('Independent kernel checks:', dict(stats), flush=True)
    print('PASS: exact component reachability and all twelve full graph certificates.')


if __name__ == '__main__':
    main()
