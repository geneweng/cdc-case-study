#!/usr/bin/env python3
"""Independent checks for triangle quotient reduction certificates.

Uses row elimination for local even spaces and enumerates Petersen flows from
a different cycle-space basis. Imports no constructors or previous verifiers.
General nonexistence conclusions use the structural proofs in the reports.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]
PORTS = [4, 5, 2, 6]
PAIRS = [sum(1 << i for i in p) for p in itertools.combinations(range(5), 2)]


def word(values):
    return ''.join(map(str, values))


def support(f, normal=1):
    return sum(1 << e for e, a in enumerate(f) if (a & normal).bit_count() % 2)


def stars(n, edges):
    result = [[] for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        assert 0 <= u < n and 0 <= v < n and u != v
        result[u].append(e)
        result[v].append(e)
    return result


def xor(values):
    result = 0
    for v in values:
        result ^= v
    return result


def flow_ok(n, edges, f, maximum=7):
    assert len(f) == len(edges) and all(1 <= a <= maximum for a in f)
    assert all(xor(f[e] for e in s) == 0 for s in stars(n, edges))


def cover_ok(n, edges, cw, first=None):
    assert len(cw) == len(edges) and set(cw) <= set('0123456789')
    pairs = [PAIRS[int(c)] for c in cw]
    if first is not None:
        assert support(pairs) == first
    for s in stars(n, edges):
        for label in range(5):
            assert sum(pairs[e] >> label & 1 for e in s) % 2 == 0


def rank(values):
    pivots = {}
    for v in values:
        while v:
            p = v.bit_length()-1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                break
    return len(pivots)


def even_space(n, edges):
    rows = [sum(1 << e for e in s) for s in stars(n, edges)]
    pivots, at = [], 0
    for column in range(len(edges)):
        found = next((i for i in range(at, len(rows)) if rows[i] >> column & 1), None)
        if found is None:
            continue
        rows[at], rows[found] = rows[found], rows[at]
        for i in range(len(rows)):
            if i != at and rows[i] >> column & 1:
                rows[i] ^= rows[at]
        pivots.append(column)
        at += 1
    basis = []
    for free in set(range(len(edges)))-set(pivots):
        b = 1 << free
        for i, p in enumerate(pivots):
            if rows[i] >> free & 1:
                b |= 1 << p
        basis.append(b)
    result = [0]
    for b in basis:
        result += [s ^ b for s in result]
    assert len(set(result)) == 2**(len(edges)-at)
    return sorted(result)


def is_circuit(edges):
    degrees = Counter(v for uv in edges for v in uv)
    if not degrees or set(degrees.values()) != {2}:
        return False
    reached, todo = set(), [next(iter(degrees))]
    while todo:
        v = todo.pop()
        if v in reached:
            continue
        reached.add(v)
        for u, w in edges:
            if u == v and w not in reached:
                todo.append(w)
            if w == v and u not in reached:
                todo.append(u)
    return len(reached) == len(degrees)


def check_caps(caps):
    total = 0
    boundaries = [p for p in itertools.product(range(10), repeat=3)
                  if xor(PAIRS[i] for i in p) == 0]
    assert len(boundaries) == 60
    for kind, cap in caps.items():
        n, edges = cap['vertices'], cap['edges']
        assert n == (13 if kind == 'blowup' else 7)
        assert edges[:3] == [[0, 3], [1, 3], [2, 3]]
        expected = []
        for i in range(3):
            prev = (i-1) % 3
            if kind == 'blowup':
                u, w = 7+2*i, 8+2*i
                expected += [[4+prev, u], [4+prev, w], [4+i, u], [4+i, w], [u, i], [w, i]]
            else:
                expected += [[4+prev, i], [4+prev, 4+i], [4+i, i]]
        assert edges[3:] == expected
        flow_ok(n, edges, list(map(int, cap['four_flow_word'])), maximum=3)
        even = even_space(n, edges)
        assert [r[0] for r in cap['canonical_covers']] == even
        assert len(even) == cap['even_supports'] == (512 if kind == 'blowup' else 64)
        bit_counts = Counter(s & 7 for s in even)
        assert bit_counts == {0: len(even)//4, 3: len(even)//4, 5: len(even)//4, 6: len(even)//4}
        assert cap['supports_per_boundary_pattern'] == len(even)//4
        cases = 0
        for first, cw in cap['canonical_covers']:
            cover_ok(n, edges, cw, first)
            assert all(not (PAIRS[int(c)] & 16) for c in cw)
            desired = {p for p in boundaries
                       if all(bool(PAIRS[p[i]] & 1) == bool(first >> i & 1) for i in range(3))}
            found = {}
            for p in itertools.permutations(range(1, 5)):
                perm = (0,)+p
                translated = [PAIRS.index(sum(1 << perm[i] for i in range(5) if PAIRS[int(c)] >> i & 1)) for c in cw]
                found[tuple(translated[:3])] = word(translated)
            assert set(found) == desired
            for translated in found.values():
                cover_ok(n, edges, translated, first)
            cases += len(found)
        assert cases == cap['compatible_boundary_states'] == (7680 if kind == 'blowup' else 960)
        total += cases
    print('Verified 576 local even supports and all', total, 'compatible prescribed-layer boundary states.', flush=True)


def check_petersen(p):
    edges = p['edges']
    assert edges == [[i, (i+1) % 5] for i in range(5)]+[[i, i+5] for i in range(5)]+[[i+5, (i+2) % 5+5] for i in range(5)]
    even = even_space(10, edges)
    assert even == p['even_supports'] and len(even) == 64
    ss = stars(10, edges)
    factors = [s for s in even if all(sum(s >> e & 1 for e in star) == 2 for star in ss)]
    assert factors == p['two_factors'] and len(factors) == 6
    assert xor(factors) == 0 and all(rank(list(sub)) == 5 for sub in itertools.combinations(factors, 5))
    for first in factors:
        # Each remaining cover layer must alternate with the complementary
        # matching. Exhaust all possible binary layers under that rule.
        alternating = []
        for other in even:
            valid = True
            for star in ss:
                if any(other >> e & 1 for e in star):
                    valid &= sum((other >> e & 1)*(first >> e & 1) for e in star) == 1
                    valid &= sum((other >> e & 1)*(1-(first >> e & 1)) for e in star) == 1
            if valid and other:
                alternating.append(other)
        assert alternating and {s.bit_count() for s in alternating} == {8}
        assert (2*len(edges)-first.bit_count()) % 8 != 0
    cover_supports = set()
    for r in p['positive_covers']:
        cover_ok(10, edges, r['cover_word'], r['support'])
        cover_supports.add(r['support'])
    assert cover_supports == set(even)-set(factors)-{0} and len(cover_supports) == 57
    histogram, count = Counter(), 0
    pentagons = [s for s in even if s.bit_count() == 5]
    assert len(pentagons) == 12 and all(is_circuit([edges[e] for e in range(15) if s >> e & 1]) for s in pentagons)
    escape_cases, escape_digest = 0, hashlib.sha256()
    for a, b, c in itertools.product(even, repeat=3):
        if a | b | c != (1 << 15)-1:
            continue
        span = [a, b, a ^ b, c, a ^ c, b ^ c, a ^ b ^ c]
        assert len(set(span)) == 7 and 0 not in span
        histogram[sum(s in factors for s in span)] += 1
        count += 1
        if a in factors:
            f = [(a >> e & 1)+2*(b >> e & 1)+4*(c >> e & 1) for e in range(15)]
            choices = [(s, inc) for s in pentagons for inc in (1, 3, 5, 7)
                       if a ^ s in cover_supports and not any(f[e] == inc for e in range(15) if s >> e & 1)]
            assert choices
            s, inc = min(choices)
            changed = [x ^ inc if s >> e & 1 else x for e, x in enumerate(f)]
            flow_ok(10, edges, changed)
            assert support(changed) == a ^ s and support(changed) in cover_supports
            escape_digest.update(f'{word(f)} {s} {inc}\n'.encode())
            escape_cases += 1
    assert count == p['nowhere_zero_flow_count'] == 28560
    assert [list(r) for r in sorted(histogram.items())] == p['blocked_normal_histogram']
    assert histogram == {0: 5040, 1: 10080, 2: 10080, 3: 3360}
    assert escape_cases == p['normal_one_pentagon_escape_cases'] == 5760
    assert escape_digest.hexdigest() == p['normal_one_pentagon_escape_sha256']
    # F=empty would require a four-flow. Directly exhaust all pairs of binary
    # even supports; no pair covers all edges of Petersen.
    assert not any(a | b == (1 << 15)-1 for a, b in itertools.product(even, repeat=2))
    for row in p['representative_flows']:
        f = list(map(int, row['flow_word']))
        flow_ok(10, edges, f)
        assert sum(support(f, l) in factors for l in range(1, 8)) == row['blocked_normals']
    print('Verified all 64 Petersen supports, 57 covers, six structural factor obstructions, all 28,560 flows, and 5,760 normalized one-pentagon escapes.', flush=True)


def check_topology(g, cap):
    cn, core, n, edges = g['core_vertices'], g['core_edges'], g['vertices'], g['edges']
    assert all(len(s) == 3 for s in stars(cn, core))
    assert n == cn*(33 if g['construction'] == 'blowup' else 27)
    assert g['pieces'] == 3*cn and len(g['blocks']) == 3*cn
    assert all(len(s) == 3 for s in stars(n, edges))
    owner, interiors = g['vertex_map'], set()
    classes = {}
    for v, name in enumerate(owner):
        classes.setdefault(name, set()).add(v)
    assert len(owner) == n and set(classes) == set(range(g['quotient_vertices']))
    for b in g['blocks']:
        vs, es = b['vertices'], b['edge_representatives']
        assert len(vs) == 8 and classes[owner[vs[0]]] == set(vs)
        assert [edges[e] for e in es[:10]] == [[vs[u-2], vs[v-2]] for u, v in INTERNAL]
        for port, e in zip(PORTS, es[10:]):
            assert vs[port-2] in edges[e] and sum(v in vs for v in edges[e]) == 1
        assert not interiors & set(es[:10])
        interiors.update(es[:10])
    assert sorted(map(len, classes.values())).count(8) == 3*cn
    assert all(len(vs) in (1, 8) for vs in classes.values())
    kept = [e for e in range(len(edges)) if e not in interiors]
    assert kept == g['kept_edge_ids'] and kept[:len(core)] == list(range(len(core)))
    qe = [[owner[edges[e][0]], owner[edges[e][1]]] for e in kept]
    assert qe == g['quotient_edges']
    assert g['quotient_vertices'] == (cap['vertices']-1)*cn
    assert len(qe) == len(core)+(len(cap['edges'])-3)*cn
    mapped_vertices, mapped_edges = set(), set()
    patch_owner = {}
    for v, patch in enumerate(g['patches']):
        vm, reps = patch['quotient_vertex_map'], patch['edge_representatives']
        assert patch['core_vertex'] == v and len(vm) == cap['vertices'] and vm[3] is None
        vs = set(vm)-{None}
        assert len(vs) == cap['vertices']-1 and not mapped_vertices & vs
        mapped_vertices |= vs
        patch_owner.update({w: v for w in vs})
        assert reps[:3] == [e for e, uv in enumerate(core) if v in uv]
        assert len(reps) == len(cap['edges'])
        for e, (a, b) in zip(reps[3:], cap['edges'][3:]):
            assert set(qe[e]) == {vm[a], vm[b]} and e not in mapped_edges
            mapped_edges.add(e)
        for i, e in enumerate(reps[:3]):
            assert vm[i] in qe[e] and sum(w in vs for w in qe[e]) == 1
    assert mapped_vertices == set(range(g['quotient_vertices']))
    assert mapped_edges == set(range(len(core), len(qe)))
    assert [[patch_owner[u], patch_owner[v]] for u, v in qe[:len(core)]] == core
    # The full cubic patches have exactly the three original core links as a
    # boundary. Both sides contain cycles in these examples.
    for v in range(cn):
        region = {x for x in range(n) if patch_owner[owner[x]] == v}
        cut = [e for e, (u, w) in enumerate(edges) if (u in region) != (w in region)]
        assert cut == [e for e, uv in enumerate(core) if v in uv]
        inside = sum(u in region and w in region for u, w in edges)
        outside = len(edges)-inside-len(cut)
        assert inside >= len(region) and outside >= n-len(region)
    return qe


def inherited_obstructions(old):
    types = {15609: 'Z', 16270: 'Z', 6115: 'W', 6782: 'W', 10045: 'W', 10711: 'W'}
    f = old['flow']
    flow_ok(old['vertices'], old['edges'], f)
    for l in range(1, 8):
        witness = old['normals'][l-1]['obstruction_junctions'][0]
        left, right = witness['left_block'], witness['right_block']
        assert right == (left+1) % 6
        names = []
        for i, side in ((left, 'left'), (right, 'right')):
            mask = support([f[e] for e in old['blocks'][i]['edge_representatives']], l)
            assert mask == witness[side+'_mask']
            names.append(types[mask])
        assert 'Z' in names and set(names) <= {'Z', 'W'}
    # The prior report proves that precisely these adjacent restrictions
    # contradict every cover, independent of its number of labels.


def check_escape(g, escape_source):
    ex = g['escape']
    move, r = ex['global_switch'], ex['completion']
    n, edges, kept = g['vertices'], g['edges'], g['kept_edge_ids']
    m, initial = len(g['core_edges']), list(map(int, g['instances'][0]['initial_flow_word']))
    assert move['core_edges'] == escape_source['circuit_edges']
    assert move['increment'] == escape_source['added_value']
    assert r['normal'] == escape_source['normal'] == 4
    assert r['core_cover_word'] == escape_source['cover_word']
    assert ex['exact_minimum_switches_touching_core_edges'] == 1
    chosen = move['edges']
    assert len(chosen) == len(set(chosen)) and is_circuit([edges[e] for e in chosen])
    assert sorted(e for e in chosen if e < m) == sorted(move['core_edges'])
    vertex_owner = {v: p['core_vertex'] for p in g['patches']
                    for v in p['quotient_vertex_map'] if v is not None}
    full_owner = [vertex_owner[v] for v in g['vertex_map']]
    paths = []
    for p in move['internal_paths']:
        v, links, path = p['core_vertex'], p['core_edges'], p['internal_path']
        assert len(links) == 2 and all(e in move['core_edges'] and v in g['core_edges'][e] for e in links)
        ends = [next(x for x in edges[e] if full_owner[x] == v) for e in links]
        at, visited = ends[0], {ends[0]}
        for e in path:
            assert e >= m and at in edges[e]
            at = next(x for x in edges[e] if x != at)
            assert full_owner[at] == v and at not in visited
            visited.add(at)
        assert at == ends[1]
        paths += path
    assert chosen == move['core_edges']+paths
    f = initial.copy()
    for e in chosen:
        assert f[e] != move['increment']
        f[e] ^= move['increment']
    flow_ok(n, edges, f)
    assert word(f) == move['flow_after_switch_word']
    assert f[:m] == escape_source['flow']
    normal = r['normal']
    cover_ok(g['core_vertices'], g['core_edges'], r['core_cover_word'], support(f[:m], normal))
    cover_ok(g['quotient_vertices'], g['quotient_edges'], r['quotient_cover_word'], support([f[e] for e in kept], normal))
    assert r['quotient_cover_word'][:m] == r['core_cover_word']
    after_global, touched = f.copy(), Counter()
    for step in r['moves']:
        es, a, b = step['edges'], step['increment'], step['piece']
        assert a in range(1, 8) and 0 <= b < g['pieces']
        assert len(es) == len(set(es)) == 5 and all(e >= m for e in es)
        assert set(es) <= set(g['blocks'][b]['edge_representatives'][:10])
        assert is_circuit([edges[e] for e in es])
        for e in es:
            assert f[e] != a
            f[e] ^= a
        flow_ok(n, edges, f)
        touched[b] += 1
    assert max(touched.values(), default=0) <= 2 and len(r['moves']) <= 2*g['pieces']
    assert all(f[e] == after_global[e] for e in kept) and word(f) == r['final_flow_word']
    cover_ok(n, edges, r['cover_word'], support(f, normal))
    assert ''.join(r['cover_word'][e] for e in kept) == r['quotient_cover_word']
    print('Verified one global escape of length', len(chosen), 'followed by', len(r['moves']), 'internal pentagons.', flush=True)


def check_examples(data, old, escape_source):
    positive, negative = 0, 0
    pet = data['petersen']
    allowed = {r['support'] for r in pet['positive_covers']}
    inherited_obstructions(old)
    for g in data['examples']:
        cap = data['caps'][g['construction']]
        qe = check_topology(g, cap)
        n, edges, kept = g['vertices'], g['edges'], g['kept_edge_ids']
        cn, core = g['core_vertices'], g['core_edges']
        if g['core_name'] == 'Petersen':
            assert cn == 10 and core == pet['edges'] and len(g['instances']) == 4
        else:
            assert cn == old['vertices'] == 72 and core == old['edges']
            assert len(g['instances']) == 1
        for instance in g['instances']:
            cf = list(map(int, instance['core_flow_word']))
            initial = list(map(int, instance['initial_flow_word']))
            flow_ok(cn, core, cf)
            flow_ok(n, edges, initial)
            assert initial[:len(core)] == cf
            flow_ok(g['quotient_vertices'], qe, [initial[e] for e in kept])
            assert [r['normal'] for r in instance['normals']] == list(range(1, 8))
            blocked = 0
            for r in instance['normals']:
                l, first = r['normal'], support(cf, r['normal'])
                assert first == r['core_support']
                if r['status'] == 'blocked_under_all_internal_repairs':
                    if cn == 10:
                        assert first in pet['two_factors']
                    else:
                        assert cf == old['flow'] and first == old['normals'][l-1]['support_mask']
                    blocked += 1
                    negative += 1
                    continue
                assert r['status'] == 'repairable' and cn == 10 and first in allowed
                cover_ok(cn, core, r['core_cover_word'], first)
                qfirst = support([initial[e] for e in kept], l)
                cover_ok(g['quotient_vertices'], qe, r['quotient_cover_word'], qfirst)
                assert r['quotient_cover_word'][:len(core)] == r['core_cover_word']
                f, touched = initial.copy(), Counter()
                for move in r['moves']:
                    es, a, b = move['edges'], move['increment'], move['piece']
                    assert a in range(1, 8) and 0 <= b < g['pieces']
                    assert len(es) == len(set(es)) == 5
                    assert set(es) <= set(g['blocks'][b]['edge_representatives'][:10])
                    assert is_circuit([edges[e] for e in es])
                    for e in es:
                        assert f[e] != a
                        f[e] ^= a
                    flow_ok(n, edges, f)
                    touched[b] += 1
                assert max(touched.values(), default=0) <= 2 and len(r['moves']) <= 60
                assert all(initial[e] == f[e] for e in kept) and word(f) == r['final_flow_word']
                cover_ok(n, edges, r['cover_word'], support(f, l))
                assert ''.join(r['cover_word'][e] for e in kept) == r['quotient_cover_word']
                positive += 1
            assert blocked == instance['blocked_normals']
        if 'unrestricted_cover' in g:
            c = g['unrestricted_cover']
            assert c['core_cover_word'] == old['cover_word']
            cover_ok(cn, core, c['core_cover_word'])
            cover_ok(g['quotient_vertices'], qe, c['quotient_cover_word'])
            cover_ok(n, edges, c['cover_word'])
            assert c['quotient_cover_word'][:len(core)] == c['core_cover_word']
            assert ''.join(c['cover_word'][e] for e in kept) == c['quotient_cover_word']
            check_escape(g, escape_source)
        print(g['construction'], g['core_name'], ': verified graph with', n, 'vertices and every coordinate record.', flush=True)
    assert positive == 44 and negative == 26
    print('Verified 44 successful repairs and the inherited obstruction premises for 26 blocked coordinates.', flush=True)


def main():
    data = json.loads((HERE / 'triangle_quotient_reduction.json').read_text())
    src = data['source']
    assert hashlib.sha256((HERE / src['file']).read_bytes()).hexdigest() == src['sha256']
    source = json.loads((HERE / src['file']).read_text())
    old = source['examples'][0]
    check_caps(data['caps'])
    check_petersen(data['petersen'])
    check_examples(data, old, source['one_switch_escape'])
    print('All triangle-quotient certificates passed. General equivalences and impossibility of arbitrary repair sequences use the accompanying proofs.')


if __name__ == '__main__':
    main()
