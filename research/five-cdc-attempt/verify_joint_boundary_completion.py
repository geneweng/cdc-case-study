#!/usr/bin/env python3
"""Independent verification of joint flow/cover completion.

Enumerates both local relations by spanning-tree elimination. Adjacency comes
from pairwise flow differences. Imports no constructor or previous verifier.
"""
from collections import Counter, defaultdict, deque
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).parent
E = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
     (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]
P = [4, 5, 2, 6]
Q = [sum(1 << a for a in p) for p in itertools.combinations(range(5), 2)]


def project(f, normal=1):
    return sum(1 << i for i, a in enumerate(f) if (a & normal).bit_count() % 2)


def word(f):
    return ''.join(map(str, f))


def is_circuit(edges):
    if not edges or any(d != 2 for d in Counter(v for uv in edges for v in uv).values()):
        return False
    adjacency = defaultdict(set)
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    seen, todo = set(), [next(iter(adjacency))]
    while todo:
        v = todo.pop()
        if v not in seen:
            seen.add(v)
            todo.extend(adjacency[v]-seen)
    return len(seen) == len(adjacency)


def enumerate_relations(alphabet):
    # A DFS spanning tree, with three free chords. Every assignment to these
    # chords determines all tree edges uniquely for the fixed port boundary.
    parent, order, tree = {2: None}, [], set()

    def visit(v):
        order.append(v)
        for e, uv in enumerate(E):
            if v not in uv:
                continue
            w = uv[1] if uv[0] == v else uv[0]
            if w not in parent:
                parent[w] = (v, e)
                tree.add(e)
                visit(w)
    visit(2)
    free = sorted(set(range(10))-tree)
    assert len(free) == 3
    allowed, result = set(alphabet), {}
    for a, b, c in itertools.product(alphabet, repeat=3):
        d = a ^ b ^ c
        if d not in allowed:
            continue
        ports = (a, b, c, d)
        base_demand = [0]*10
        for v, x in zip(P, ports):
            base_demand[v] ^= x
        states = []
        for chosen in itertools.product(alphabet, repeat=3):
            demand, f = base_demand.copy(), [0]*10
            for e, x in zip(free, chosen):
                f[e] = x
                for v in E[e]:
                    demand[v] ^= x
            valid = True
            for v in reversed(order[1:]):
                u, e = parent[v]
                f[e] = demand[v]
                if f[e] not in allowed:
                    valid = False
                    break
                demand[u] ^= f[e]
            if valid:
                assert demand[2] == 0
                states.append(tuple(f)+ports)
        result[ports] = sorted(states)
    return result


def adjacency(fs, circuits):
    full, five = [set() for _ in fs], [set() for _ in fs]
    for i, f in enumerate(fs):
        for j in range(i):
            difference = [a ^ b for a, b in zip(f[:10], fs[j][:10])]
            increments = set(difference)-{0}
            if len(increments) != 1:
                continue
            mask = sum(1 << e for e, a in enumerate(difference) if a)
            if mask in circuits:
                full[i].add(j)
                full[j].add(i)
                if mask.bit_count() == 5:
                    five[i].add(j)
                    five[j].add(i)
    return full, five


def distances(graph, starts):
    result = {i: 0 for i in starts}
    todo = deque(result)
    while todo:
        v = todo.popleft()
        for u in graph[v]-result.keys():
            result[u] = result[v]+1
            todo.append(u)
    return result


def histogram(counter):
    return [list(x) for x in sorted(counter.items())]


def audit_local(saved):
    flows = enumerate_relations(list(range(1, 8)))
    covers = enumerate_relations(Q)
    assert len(flows) == 301 and sum(map(len, flows.values())) == 34230
    assert len(covers) == 640 and sum(map(len, covers.values())) == 14700
    print('Independently enumerated 34,230 local flows and 14,700 local covers by tree elimination.', flush=True)
    domains = {tuple(Q.index(a) for a in p): {project(c) for c in cs} for p, cs in covers.items()}
    circuits = {s for s in range(1, 1024) if is_circuit([E[e] for e in range(10) if s >> e & 1])}
    assert circuits == {151, 301, 442, 602, 717, 887, 992}
    local_edges = E+[(v, -1) for v in P]
    even = [s for s in range(1 << 14) if all(sum(s >> e & 1 for e, uv in enumerate(local_edges) if v in uv) % 2 == 0 for v in range(2, 10))]
    assert len(even) == 64
    flow_records, exceptions = [], []
    compatible = defaultdict(list)
    for q, targets in domains.items():
        compatible[tuple(Q[a] & 1 for a in q)].append(targets)
    common, full_hist, five_hist = Counter(), Counter(), Counter()
    count, graph_cache = 0, {}
    for p, fs in sorted(flows.items()):
        supports = [project(f) for f in fs]
        bits = tuple(a & 1 for a in p)
        candidates = {s for s in even if tuple(s >> (10+i) & 1 for i in range(4)) == bits}
        absent = candidates-set(supports)
        assert len(candidates) == 8
        assert absent == ({0} if not any(bits) and p[0] != p[1] else set())
        if absent:
            exceptions.append(word(p))
        flow_records.append({'boundary': word(p), 'supports': sorted(set(supports))})
        a, b = adjacency(fs, circuits)
        if p == (4, 4, 4, 4):
            graph_cache[p] = a, b
        grouped = Counter(tuple(sorted(s)) for s in compatible[bits])
        for targets, multiplicity in grouped.items():
            common[len(set(supports) & set(targets))] += multiplicity
            ready = [i for i, s in enumerate(supports) if s in targets]
            da, db = distances(a, ready), distances(b, ready)
            assert len(da) == len(db) == len(fs) and max(db.values()) <= 2
            for distance, number in Counter(da.values()).items():
                full_hist[distance] += multiplicity*number
            for distance, number in Counter(db.values()).items():
                five_hist[distance] += multiplicity*number
            count += multiplicity*len(fs)
    computed = {'flow_boundary_supports': flow_records,
                'cover_boundary_supports': [{'boundary': word(q), 'supports': sorted(s)} for q, s in sorted(domains.items())],
                'exceptional_flow_boundaries': exceptions, 'missing_support_in_each_exception': 0,
                'flow_count': sum(map(len, flows.values())),
                'realized_flow_boundary_support_pairs': sum(len(r['supports']) for r in flow_records),
                'cover_boundary_support_pairs': sum(map(len, domains.values())),
                'distinct_cover_support_sets': len({tuple(sorted(s)) for s in domains.values()}),
                'compatible_boundary_pairs': sum(common.values()), 'common_support_histogram': histogram(common),
                'starting_flow_cover_boundary_cases': count,
                'all_circuit_distance_histogram': histogram(full_hist), 'pentagon_distance_histogram': histogram(five_hist)}
    assert computed == saved
    assert len(exceptions) == 12 and min(common) == 2
    assert sum(common.values()) == 21640 and count == 2455920
    print('Verified all 21,640 joint boundaries and all 2,455,920 starting-flow/cover-boundary cases; two pentagons suffice.', flush=True)
    return flows, domains, circuits, graph_cache


def check_local_repair(rec, flows, domains, circuits):
    f = tuple(map(int, rec['initial_flow_word']))
    p, normal = f[10:], rec['normal']
    q = tuple(map(int, rec['cover_boundary']))
    assert f in flows[p] and len(rec['moves']) <= 2
    for move in rec['moves']:
        mask, a = move['circuit_mask'], move['increment']
        assert mask in circuits and mask.bit_count() == 5 and a in range(1, 8)
        f = tuple(x ^ a if mask >> e & 1 else x for e, x in enumerate(f))
        assert f in flows[p]
    assert word(f) == rec['final_flow_word']
    target = project(f, normal)
    assert target == rec['final_support'] and target in domains[q]
    cw = tuple(Q[int(c)] for c in rec['cover_word'])
    assert len(cw) == 14 and tuple(Q.index(a) for a in cw[10:]) == q
    le = E+[(v, -1) for v in P]
    for v in range(2, 10):
        incident = [cw[e] for e, uv in enumerate(le) if v in uv]
        assert len(incident) == 3 and incident[0] ^ incident[1] ^ incident[2] == 0
    assert project(cw) == target


def flow_valid(n, edges, values, cubic=True):
    assert len(values) == len(edges) and set(values) <= set(range(1, 8))
    totals, degrees = [0]*n, [0]*n
    for (u, v), a in zip(edges, values):
        assert u != v and 0 <= u < n and 0 <= v < n
        for x in (u, v):
            totals[x] ^= a
            degrees[x] += 1
    assert totals == [0]*n
    if cubic:
        assert degrees == [3]*n
    return degrees


def cover_valid(n, edges, word0, flow, normal):
    assert len(word0) == len(edges) and set(word0) <= set('0123456789')
    parity = [0]*n
    for (u, v), c, a in zip(edges, word0, flow):
        value = Q[int(c)]
        assert bool(value & 1) == bool((a & normal).bit_count() % 2)
        parity[u] ^= value
        parity[v] ^= value
    assert parity == [0]*n


def apply_switch(n, edges, flow, move):
    chosen, a = move['edges'], move['increment']
    assert len(chosen) == len(set(chosen)) == 5 and a in range(1, 8)
    assert is_circuit([edges[e] for e in chosen])
    for e in chosen:
        assert flow[e] != a
        flow[e] ^= a
    flow_valid(n, edges, flow)


def check_sharpness(data, flows, domains, circuits, cache):
    r = data['sharp_local_example']
    check_local_repair(r, flows, domains, circuits)
    start = tuple(map(int, r['initial_flow_word']))
    fs, (all_adj, _) = flows[start[10:]], cache[start[10:]]
    at = fs.index(start)
    targets = domains[tuple(map(int, r['cover_boundary']))]
    reachable = {project(fs[i]) for i in all_adj[at]}
    assert sorted(targets) == r['allowed_cover_supports'] == [0, 151, 992]
    assert sorted(reachable) == r['one_step_supports'] == [442, 717, 887]
    assert len(all_adj[at]) == r['one_step_flow_count'] == 19
    assert project(start) == r['initial_support'] == 887 and not (reachable | {887}) & targets
    assert len(r['moves']) == 2
    for ex in data['sharp_graph_examples']:
        q, n, edges = ex['pieces'], ex['vertices'], [tuple(e) for e in ex['edges']]
        assert q >= 3 and n == 8*q and len(edges) == 12*q
        for i in range(q):
            assert edges[10*i:10*i+10] == [(8*i+x-2, 8*i+y-2) for x, y in E]
            assert edges[10*q+2*i:10*q+2*i+2] == [(8*i+2, 8*((i+1) % q)), (8*i+3, 8*((i+1) % q)+4)]
        f = list(map(int, ex['initial_flow_word']))
        assert f == list(start[:10])*q+[4]*(2*q)
        flow_valid(n, edges, f)
        cover_valid(n, edges, ex['initial_cover_with_different_exterior_pairs'], f, 1)
        assert ex['initial_cover_with_different_exterior_pairs'][10*q:] == '44'*q
        assert ex['prescribed_exterior_cover_word'] == '49'*q
        assert len(ex['moves']) == ex['exact_internal_distance_preserving_prescribed_exterior_cover'] == 2*q
        for i, move in enumerate(ex['moves']):
            assert move['piece'] == i//2 and all(10*(i//2) <= e < 10*(i//2)+10 for e in move['edges'])
            apply_switch(n, edges, f, move)
        assert word(f) == ex['final_flow_word'] and f[10*q:] == [4]*(2*q)
        assert ex['cover_word'][10*q:] == '49'*q
        cover_valid(n, edges, ex['cover_word'], f, 1)
    print('Verified sharp two-switch local witness and exact 2q distances with prescribed exterior cover pairs for q=3,6,12.', flush=True)


def check_quotient_and_family(data, source, flows, domains, circuits):
    base = source['examples'][0]
    edges0 = [tuple(e) for e in base['edges']]
    quotient = data['quotient']
    owner, kept = quotient['vertex_map'], quotient['kept_edge_ids']
    assert len(owner) == 72 and set(owner) == set(range(30)) and quotient['vertices'] == 30
    parts = {frozenset(v for v in range(72) if owner[v] == i) for i in range(30)}
    expected_parts = {frozenset(b['vertices']) for b in base['blocks']}
    inside = set().union(*(set(b['vertices']) for b in base['blocks']))
    expected_parts |= {frozenset([v]) for v in range(72) if v not in inside}
    assert parts == expected_parts
    assert kept == [e for e, (u, v) in enumerate(edges0) if owner[u] != owner[v]] == list(range(12))+list(range(72, 108))
    qe = [tuple(e) for e in quotient['edges']]
    assert qe == [(owner[edges0[e][0]], owner[edges0[e][1]]) for e in kept]
    qf = list(map(int, quotient['flow_word']))
    assert qf == [base['flow'][e] for e in kept]
    assert Counter(flow_valid(30, qe, qf, cubic=False)) == {3: 24, 4: 6}
    assert [r['normal'] for r in data['seed_coordinate_repairs']] == list(range(1, 8))
    for rec in data['seed_coordinate_repairs']:
        normal = rec['normal']
        cover_valid(30, qe, rec['quotient_cover_word'], qf, normal)
        outside = {e: int(c) for e, c in zip(kept, rec['quotient_cover_word'])}
        assert len(rec['blocks']) == 6
        for b, local in zip(base['blocks'], rec['blocks']):
            es = b['edge_representatives']
            assert local['normal'] == normal
            assert local['initial_flow_word'] == word([base['flow'][e] for e in es])
            assert local['cover_boundary'] == word([outside[e] for e in es[10:]])
            check_local_repair(local, flows, domains, circuits)
        assert len(rec['moves']) == 1
        f = base['flow'].copy()
        move = rec['moves'][0]
        local_edges = base['blocks'][move['piece']]['edge_representatives'][:10]
        assert set(move['edges']) <= set(local_edges)
        apply_switch(72, edges0, f, move)
        assert word(f) == rec['final_flow_word']
        assert all(f[e] == base['flow'][e] for e in kept)
        assert ''.join(rec['cover_word'][e] for e in kept) == rec['quotient_cover_word']
        cover_valid(72, edges0, rec['cover_word'], f, normal)
    types = {15609: 'Z', 16270: 'Z', 6115: 'W', 6782: 'W', 10045: 'W', 10711: 'W'}
    for ex in data['periodic_coordinate_repairs']:
        m, n = ex['repetitions'], ex['vertices']
        assert n == 72*m
        edges = [(72*s+u, 72*((s+int(e in (5, 106, 107))) % m)+v)
                 for s in range(m) for e, (u, v) in enumerate(edges0)]
        initial = list(map(int, ex['initial_flow_word']))
        assert initial == base['flow']*m
        flow_valid(n, edges, initial)
        # Verify the covering map locally, including seam incidences.
        star = [[] for _ in range(n)]
        for e, uv in enumerate(edges):
            for v in uv:
                star[v].append(e % 108)
        for v in range(n):
            assert sorted(star[v]) == [e for e, uv in enumerate(edges0) if v % 72 in uv]
        assert [r['normal'] for r in ex['repairs']] == list(range(1, 8))
        for r, seed_r in zip(ex['repairs'], data['seed_coordinate_repairs']):
            normal, f = r['normal'], initial.copy()
            assert len(r['moves']) == r['exact_internal_repair_distance_for_this_normal'] == m
            assert r['cover_word'] == seed_r['cover_word']*m
            assert r['final_flow_word'] == seed_r['final_flow_word']*m
            for s, move in enumerate(r['moves']):
                sm = seed_r['moves'][0]
                assert move == {'piece': 6*s+sm['piece'], 'edges': [108*s+e for e in sm['edges']], 'increment': sm['increment']}
                apply_switch(n, edges, f, move)
            assert word(f) == r['final_flow_word'] and project(f, normal).bit_count() == r['support_size']
            assert all(f[108*s+e] == initial[108*s+e] for s in range(m) for e in kept)
            cover_valid(n, edges, r['cover_word'], f, normal)
            # Premises for the m lower bound from the prior Z-W charge lemma:
            # m disjoint obstructing piece pairs for THIS specified normal.
            witness = base['normals'][normal-1]['obstruction_junctions'][0]
            touched = set()
            for s in range(m):
                li, ri = witness['left_block'], witness['right_block']
                rs = (s+1) % m if ri == 0 else s
                pair = [(s, li), (rs, ri)]
                assert not touched & set(pair)
                touched.update(pair)
                names = []
                for sheet, i in pair:
                    mask = project([initial[108*sheet+e] for e in base['blocks'][i]['edge_representatives']], normal)
                    names.append(types[mask])
                assert 'Z' in names and set(names) <= {'Z', 'W'}
        print(f'm={m}: verified all seven quotient-guided completions, exactly {m} internal pentagons per selected normal.', flush=True)


def main():
    data = json.loads((HERE / 'joint_boundary_completion.json').read_text())
    for src in data['sources']:
        assert hashlib.sha256((HERE / src['file']).read_bytes()).hexdigest() == src['sha256']
    source = json.loads((HERE / 'junction_selection_obstruction.json').read_text())
    flows, domains, circuits, cache = audit_local(data['local_audit'])
    check_sharpness(data, flows, domains, circuits, cache)
    check_quotient_and_family(data, source, flows, domains, circuits)
    print('All joint-completion certificates passed. General reductions and distance bounds use the accompanying proofs.')


if __name__ == '__main__':
    main()
