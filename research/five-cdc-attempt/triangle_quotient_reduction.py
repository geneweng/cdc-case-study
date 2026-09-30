#!/usr/bin/env python3
"""Exact prescribed-layer reduction through triangle quotient patches.

Produces local extension tables, a complete Petersen classification, positive
internal repairs, and obstructions that survive every interior-only repair.
Standard library only; general statements are proved in the companion report.
"""
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
from fourflow_quotient_repair import build, cycle_basis, four_cover, quotient_flow
from joint_boundary_completion import PAIRS, joint_repair, load_covers, masks_and_flows, project, word

HERE = Path(__file__).parent
PERMS = [(0,)+p for p in itertools.permutations(range(1, 5))]
PAIR_PERMS = [[PAIRS.index(sum(1 << p[i] for i in range(5) if a >> i & 1))
               for a in PAIRS] for p in PERMS]


def even_supports(n, edges):
    values = [0]
    for b in cycle_basis(n, edges):
        values += [s ^ b for s in values]
    return sorted(values)


def cap_record(kind):
    g = build(4, list(itertools.combinations(range(4), 2)), [[0, 1, 2]], kind)
    quotient_flow(g, [1, 2, 3])
    n, edges = g['quotient_vertices'], g['quotient_edges']
    h = list(map(int, g['quotient_four_flow_word']))
    rows = [[s, four_cover(h, s)] for s in even_supports(n, edges)]
    return {'construction': kind, 'vertices': n, 'edges': edges,
            'cap_vertex': 3, 'boundary_edge_ids': [0, 1, 2],
            'four_flow_word': word(h), 'canonical_covers': rows,
            'even_supports': len(rows), 'supports_per_boundary_pattern': len(rows)//4,
            'compatible_boundary_states': len(rows)//4*60}


def extend_local(cap, support, boundary):
    cw = dict(cap['canonical_covers'])[support]
    old = list(map(int, cw))
    perm = next(p for p in PAIR_PERMS if [p[x] for x in old[:3]] == list(boundary))
    return word([perm[x] for x in old])


def expanded_graph(n, edges, kind, cap):
    stars = [[e for e, uv in enumerate(edges) if v in uv] for v in range(n)]
    slots = {(v, e): 3*v+j for v in range(n) for j, e in enumerate(stars[v])}
    cycles = [list(range(3*v, 3*v+3)) for v in range(n)]
    base = [(c[i], c[(i+1) % 3]) for c in cycles for i in range(3)]
    base += [(slots[u, e], slots[v, e]) for e, (u, v) in enumerate(edges)]
    g = build(3*n, base, cycles, kind)
    g['core_vertices'], g['core_edges'] = n, edges
    assert g['outside_base_edge_ids'] == list(range(3*n, 3*n+len(edges)))
    lookup = {tuple(sorted(uv)): e for e, uv in enumerate(g['quotient_edges'])}
    patches = []
    for v in range(n):
        mapping = [3*v+i for i in range(3)]+[None]+[3*n+3*v+i for i in range(3)]
        if kind == 'blowup':
            mapping += [6*n+6*v+i for i in range(6)]
        reps = stars[v].copy()
        reps += [lookup[tuple(sorted((mapping[u], mapping[w])))] for u, w in cap['edges'][3:]]
        patches.append({'core_vertex': v, 'quotient_vertex_map': mapping, 'edge_representatives': reps})
    g['patches'] = patches
    return g


def lift_flow(g, cap, core_flow, fibers, rng):
    h = list(map(int, cap['four_flow_word']))
    qflow = [None]*len(g['quotient_edges'])
    for patch in g['patches']:
        reps = patch['edge_representatives']
        p = [core_flow[e] for e in reps[:3]]
        assert p[0] ^ p[1] == p[2] and len(set(p)) == 3
        linear = [0, p[0], p[1], p[2]]
        for e, a in zip(reps, h):
            if qflow[e] is not None:
                assert qflow[e] == linear[a]
            qflow[e] = linear[a]
    values = dict(zip(g['kept_edge_ids'], qflow))
    for b in g['blocks']:
        es = b['edge_representatives']
        f = rng.choice(fibers[tuple(values[e] for e in es[10:])])
        values.update(zip(es[:10], f[:10]))
    return [values[e] for e in range(len(g['edges']))]


def quotient_cover(g, cap, first, core_cover):
    result = ['?']*len(g['quotient_edges'])
    for patch in g['patches']:
        reps = patch['edge_representatives']
        local = sum(1 << i for i, e in enumerate(reps) if first >> e & 1)
        boundary = [int(core_cover[e]) for e in reps[:3]]
        cw = extend_local(cap, local, boundary)
        for e, a in zip(reps, cw):
            assert result[e] in ('?', a)
            result[e] = a
    assert '?' not in result
    return ''.join(result)


def repair(g, cap, initial, normal, core_cover, fibers, domains, witnesses):
    kept = g['kept_edge_ids']
    first = project([initial[e] for e in kept], normal)
    qc = quotient_cover(g, cap, first, core_cover)
    values = dict(zip(kept, map(int, qc)))
    flow, cover, moves = initial.copy(), ['?']*len(initial), []
    for e, a in values.items():
        cover[e] = str(a)
    for i, b in enumerate(g['blocks']):
        es = b['edge_representatives']
        local = joint_repair([initial[e] for e in es], normal,
                             [values[e] for e in es[10:]], fibers, domains, witnesses)
        for move in local['moves']:
            chosen = [es[j] for j in range(10) if move['circuit_mask'] >> j & 1]
            moves.append({'piece': i, 'edges': chosen, 'increment': move['increment']})
            for e in chosen:
                flow[e] ^= move['increment']
        for e, a in zip(es[:10], local['cover_word'][:10]):
            cover[e] = a
    assert '?' not in cover
    return {'normal': normal, 'status': 'repairable', 'core_cover_word': core_cover,
            'quotient_cover_word': qc, 'moves': moves, 'final_flow_word': word(flow),
            'cover_word': ''.join(cover)}


def unrestricted_cover(g, cap, core_cover, domains, witnesses):
    # Choose any even local support matching each core layer-0 boundary.
    first = 0
    for patch in g['patches']:
        reps = patch['edge_representatives']
        bits = [PAIRS[int(core_cover[e])] & 1 for e in reps[:3]]
        local = next(s for s, _ in cap['canonical_covers']
                     if [s >> i & 1 for i in range(3)] == bits)
        for i, e in enumerate(reps):
            if local >> i & 1:
                first |= 1 << e
    qc = quotient_cover(g, cap, first, core_cover)
    values = dict(zip(g['kept_edge_ids'], map(int, qc)))
    cw = ['?']*len(g['edges'])
    for e, a in values.items():
        cw[e] = str(a)
    for b in g['blocks']:
        es = b['edge_representatives']
        q = tuple(values[e] for e in es[10:])
        local = witnesses[min(domains[q]), q]
        for e, a in zip(es[:10], local[:10]):
            cw[e] = a
    return {'core_cover_word': core_cover, 'quotient_cover_word': qc, 'cover_word': ''.join(cw)}


def lifted_switch(g, initial, core_edges, increment):
    # Work inside each full three-terminal region, with the original core
    # edges deleted. The quotient-by-increment argument guarantees the paths.
    owner = {}
    for patch in g['patches']:
        owner.update({v: patch['core_vertex'] for v in patch['quotient_vertex_map'] if v is not None})
    full_owner = [owner[v] for v in g['vertex_map']]
    adj = [[] for _ in range(g['vertices'])]
    m = len(g['core_edges'])
    for e, (u, v) in enumerate(g['edges']):
        if e >= m and initial[e] != increment:
            assert full_owner[u] == full_owner[v]
            adj[u].append((v, e))
            adj[v].append((u, e))
    selected, paths = list(core_edges), []
    touched = sorted({v for e in core_edges for v in g['core_edges'][e]})
    for v in touched:
        links = [e for e in core_edges if v in g['core_edges'][e]]
        assert len(links) == 2
        endpoints = [next(x for x in g['edges'][e] if full_owner[x] == v) for e in links]
        start, goal = endpoints
        previous, queue = {start: None}, deque([start])
        while goal not in previous:
            u = queue.popleft()
            for w, e in adj[u]:
                if w not in previous:
                    previous[w] = (u, e)
                    queue.append(w)
        path, at = [], goal
        while at != start:
            at, e = previous[at]
            path.append(e)
        path.reverse()
        selected += path
        paths.append({'core_vertex': v, 'core_edges': links, 'internal_path': path})
    after = initial.copy()
    for e in selected:
        assert after[e] != increment
        after[e] ^= increment
    return {'core_edges': core_edges, 'increment': increment, 'edges': selected,
            'internal_paths': paths, 'flow_after_switch_word': word(after)}, after


def petersen():
    edges = [(i, (i+1) % 5) for i in range(5)]+[(i, i+5) for i in range(5)]
    edges += [(i+5, (i+2) % 5+5) for i in range(5)]
    even = even_supports(10, edges)
    covers = []
    for target in even:
        capacity = [2-(target >> e & 1) for e in range(15)]

        def visit(start, chosen, cap):
            if len(chosen) == 3:
                if any(n not in (0, 1) for n in cap):
                    return None
                last = sum(1 << e for e, n in enumerate(cap) if n)
                return chosen+[last] if last in even and last >= even[start] else None
            for j in range(start, len(even)):
                s = even[j]
                if any(s >> e & 1 and not cap[e] for e in range(15)):
                    continue
                rem = [n-(s >> e & 1) for e, n in enumerate(cap)]
                if max(rem) > 3-len(chosen):
                    continue
                found = visit(j, chosen+[s], rem)
                if found is not None:
                    return found
            return None
        other = visit(0, [], capacity)
        if other is not None:
            layers = [target]+other
            cw = word([PAIRS.index(sum(1 << i for i, s in enumerate(layers) if s >> e & 1)) for e in range(15)])
            covers.append({'support': target, 'cover_word': cw})
    bad = [s for s in even if s.bit_count() == 10]
    assert len(covers) == 57 and {r['support'] for r in covers} == set(even)-set(bad)-{0}
    histogram, representatives, count = Counter(), {}, 0
    pentagons = [s for s in even if s.bit_count() == 5]
    positive = {r['support'] for r in covers}
    escape_cases, escape_digest = 0, hashlib.sha256()
    for a, b, c in itertools.product(even, repeat=3):
        if a | b | c != (1 << 15)-1:
            continue
        f = [(a >> e & 1)+2*(b >> e & 1)+4*(c >> e & 1) for e in range(15)]
        nb = sum(project(f, l) in bad for l in range(1, 8))
        histogram[nb] += 1
        representatives.setdefault(nb, word(f))
        count += 1
        if a in bad:
            chosen, increment = next((s, inc) for s in pentagons for inc in (1, 3, 5, 7)
                                     if a ^ s in positive and all(f[e] != inc for e in range(15) if s >> e & 1))
            escape_digest.update(f'{word(f)} {chosen} {increment}\n'.encode())
            escape_cases += 1
    return {'vertices': 10, 'edges': edges, 'even_supports': even,
            'two_factors': bad, 'positive_covers': covers, 'nowhere_zero_flow_count': count,
            'blocked_normal_histogram': sorted(histogram.items()),
            'normal_one_pentagon_escape_cases': escape_cases,
            'normal_one_pentagon_escape_sha256': escape_digest.hexdigest(),
            'representative_flows': [{'blocked_normals': n, 'flow_word': f} for n, f in sorted(representatives.items())]}


def main():
    caps = {k: cap_record(k) for k in ('blowup', 'semi')}
    pet = petersen()
    _, fibers = masks_and_flows()
    domains, witnesses = load_covers()
    rng = random.Random(20260930)
    pcover = {r['support']: r['cover_word'] for r in pet['positive_covers']}
    examples = []
    for kind, cap in caps.items():
        g = expanded_graph(10, pet['edges'], kind, cap)
        g['core_name'] = 'Petersen'
        g['instances'] = []
        for row in pet['representative_flows']:
            core_flow = list(map(int, row['flow_word']))
            initial = lift_flow(g, cap, core_flow, fibers, rng)
            records = []
            for l in range(1, 8):
                first = project(core_flow, l)
                if first in pcover:
                    rec = repair(g, cap, initial, l, pcover[first], fibers, domains, witnesses)
                else:
                    assert first in pet['two_factors']
                    rec = {'normal': l, 'status': 'blocked_under_all_internal_repairs', 'reason': 'Petersen two-factor'}
                rec['core_support'] = first
                records.append(rec)
            g['instances'].append({'core_flow_word': word(core_flow), 'initial_flow_word': word(initial),
                                   'blocked_normals': row['blocked_normals'], 'normals': records})
            print(kind, 'Petersen, blocked normals:', row['blocked_normals'], 'repair moves:',
                  [len(r['moves']) for r in records if 'moves' in r], flush=True)
        examples.append(g)
    source = HERE / 'junction_selection_obstruction.json'
    source_data = json.loads(source.read_text())
    old = source_data['examples'][0]
    for kind, cap in caps.items():
        g = expanded_graph(old['vertices'], old['edges'], kind, cap)
        g['core_name'] = '72_vertex_all_coordinate_obstruction'
        initial = lift_flow(g, cap, old['flow'], fibers, rng)
        g['instances'] = [{'core_flow_word': word(old['flow']), 'initial_flow_word': word(initial),
                          'blocked_normals': 7,
                          'normals': [{'normal': l, 'core_support': project(old['flow'], l),
                                       'status': 'blocked_under_all_internal_repairs',
                                       'reason': 'Inherited Z-W obstruction on the core'} for l in range(1, 8)]}]
        g['unrestricted_cover'] = unrestricted_cover(g, cap, old['cover_word'], domains, witnesses)
        escape = source_data['one_switch_escape']
        move, after = lifted_switch(g, initial, escape['circuit_edges'], escape['added_value'])
        finish = repair(g, cap, after, escape['normal'], escape['cover_word'], fibers, domains, witnesses)
        g['escape'] = {'global_switch': move, 'completion': finish,
                       'exact_minimum_switches_touching_core_edges': 1}
        examples.append(g)
        print(kind, 'all seven blocked, vertices:', g['vertices'], 'global escape length:', len(move['edges']),
              'then internal moves:', len(finish['moves']), flush=True)
    result = {'date': '2026-09-30',
              'scope': 'Exact prescribed-layer reduction through triangle quotient patches; complete Petersen-core classification and all-coordinate obstructions to interior-only repair. No general 5-CDC proof or novelty claim.',
              'source': {'file': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()},
              'caps': caps, 'petersen': pet, 'examples': examples}
    (HERE / 'triangle_quotient_reduction.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Saved local boundary tables, the complete Petersen classification, 44 internal repairs, 26 blocked-coordinate records, and two global escapes.')


if __name__ == '__main__':
    main()
