#!/usr/bin/env python3
"""Construct quotient four-flows and prescribed-coordinate repairs.

Standard library only. General claims are proved in fourflow-quotient-repair.md;
the saved examples are certificates, not an exhaustive graph census.
"""
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
from joint_boundary_completion import (
    CIRCUITS, INTERNAL, PAIRS, graph, joint_repair,
    load_covers, masks_and_flows, project, word,
)

HERE = Path(__file__).parent


def junction_states(kind):
    states = []
    for a, b, c, d in itertools.product(range(1, 4), repeat=4):
        left, right, r = a ^ b, c ^ d, a ^ b ^ c ^ d
        if not r:
            continue
        if kind == 'blowup' and a != c and b != d:
            states.append([left, right, a, b, c, d, a ^ c, b ^ d, r])
        if kind == 'semi' and b == d:
            states.append([left, right, a, b, c, d, r])
    return sorted(states)


def four_cover(flow, support):
    # Three nonzero linear functionals of F_2^2 give a 3-CDC.
    # Add support as label 0 and toggle it in each of the three old layers.
    pairs = []
    for e, a in enumerate(flow):
        bit = support >> e & 1
        mask = bit + sum(1 << j for j in (1, 2, 3)
                         if (a & j).bit_count() % 2 != bit)
        pairs.append(PAIRS.index(mask))
    return word(pairs)


def build(base_n, base_edges, cycles, kind):
    removed = {tuple(sorted((c[i], c[(i+1) % len(c)])))
               for c in cycles for i in range(len(c))}
    outside = [e for e, uv in enumerate(base_edges) if tuple(sorted(uv)) not in removed]
    q = sum(map(len, cycles))
    edges = [tuple(base_edges[e]) for e in outside]
    blocks = []
    for i in range(q):
        es = list(range(len(edges), len(edges)+10))
        vertices = [base_n+8*i+j for j in range(8)]
        edges.extend((base_n+8*i+u-2, base_n+8*i+v-2) for u, v in INTERNAL)
        blocks.append({'vertices': vertices, 'edge_representatives': es+[None]*4})
    junctions = []
    offset = 0
    for cycle in cycles:
        for j, v in enumerate(cycle):
            i, prev = offset+j, offset+(j-1) % len(cycle)
            ports = [base_n+8*prev+2, base_n+8*prev+3,
                     base_n+8*i, base_n+8*i+4]
            stem = next(e for e in range(len(outside)) if v in edges[e])
            start = len(edges)
            if kind == 'blowup':
                u, w = base_n+8*q+2*i, base_n+8*q+2*i+1
                edges.extend([(ports[0], u), (ports[1], w),
                              (ports[2], u), (ports[3], w), (u, v), (w, v)])
                js = list(range(start, start+6))+[stem]
            else:
                edges.extend([(ports[0], v), (ports[1], ports[3]), (ports[2], v)])
                js = [start, start+1, start+2, start+1, stem]
            blocks[prev]['edge_representatives'][10:12] = js[:2]
            blocks[i]['edge_representatives'][12:14] = js[2:4]
            junctions.append({'vertex': v, 'left_piece': prev, 'right_piece': i, 'edges': js})
        offset += len(cycle)
    n = base_n+8*q+(2*q if kind == 'blowup' else 0)
    owner = list(range(base_n))
    owner += [base_n+i for i in range(q) for _ in range(8)]
    if kind == 'blowup':
        owner += list(range(base_n+q, base_n+3*q))
    kept = list(range(len(outside)))+list(range(len(outside)+10*q, len(edges)))
    qe = [(owner[edges[e][0]], owner[edges[e][1]]) for e in kept]
    return {'construction': kind, 'base_vertices': base_n, 'base_edges': base_edges,
            'selected_cycles': cycles, 'pieces': q, 'vertices': n, 'edges': edges,
            'outside_base_edge_ids': outside, 'blocks': blocks, 'junctions': junctions,
            'quotient_vertices': max(owner)+1, 'vertex_map': owner,
            'kept_edge_ids': kept, 'quotient_edges': qe}


def contracted(g):
    owner = list(range(g['base_vertices']))
    for cycle in g['selected_cycles']:
        for v in cycle:
            owner[v] = min(cycle)
    names = {v: i for i, v in enumerate(sorted(set(owner)))}
    owner = [names[v] for v in owner]
    return {'vertices': len(names), 'vertex_map': owner,
            'edges': [[owner[u], owner[v]] for e in g['outside_base_edge_ids']
                      for u, v in [g['base_edges'][e]]]}


def quotient_flow(g, outside_flow):
    flow = {e: a for e, a in enumerate(outside_flow)}
    charges, offset = [], 0
    for cycle in g['selected_cycles']:
        previous = 0
        for j in range(len(cycle)):
            previous ^= outside_flow[g['junctions'][offset+j]['edges'][-1]]
            charges.append(previous)
        assert previous == 0
        offset += len(cycle)
    table = junction_states(g['construction'])
    for j in g['junctions']:
        left, right = charges[j['left_piece']], charges[j['right_piece']]
        row = next(row for row in table if row[:2] == [left, right])
        for e, a in zip(j['edges'], row[2:]):
            if e in flow:
                assert flow[e] == a
            flow[e] = a
    assert set(flow) == set(g['kept_edge_ids'])
    g['contracted_base'] = contracted(g)
    g['contracted_base']['four_flow_word'] = word(outside_flow)
    g['piece_charges'] = charges
    g['quotient_four_flow_word'] = word([flow[e] for e in g['kept_edge_ids']])


def cycle_basis(n, edges):
    parent = list(range(n))
    tree, chords = [[] for _ in range(n)], []

    def root(v):
        while parent[v] != v:
            v = parent[v]
        return v
    for e, (u, v) in enumerate(edges):
        a, b = root(u), root(v)
        if a == b:
            chords.append(e)
        else:
            parent[a] = b
            tree[u].append((v, e))
            tree[v].append((u, e))
    paths = {}
    for start in range(n):
        if start in paths:
            continue
        paths[start] = 0
        todo = [start]
        while todo:
            v = todo.pop()
            for w, e in tree[v]:
                if w not in paths:
                    paths[w] = paths[v] ^ (1 << e)
                    todo.append(w)
    return [paths[edges[e][0]] ^ paths[edges[e][1]] ^ (1 << e) for e in chords]


def initial_flow(g, fibers, rng, obstruction=None):
    if obstruction is not None:
        k = g['pieces']
        local = [list(map(int, s)) for s in obstruction['local_flow_words']]*(k//6)
        values = {}
        for b, f in zip(g['blocks'], local):
            for e, a in zip(b['edge_representatives'], f):
                values[e] = a
        charges = [f[10] ^ f[11] for f in local]
        for e, (u, v) in enumerate(g['edges'][:2*k]):
            values[e] = charges[u-k] if u >= k else charges[u-1] ^ charges[u]
        for j in g['junctions']:
            a, b, c, d, x, y, r = j['edges']
            values[x], values[y] = values[a] ^ values[c], values[b] ^ values[d]
        return [values[e] for e in range(len(g['edges']))]
    flow = list(map(int, g['quotient_four_flow_word']))
    basis = cycle_basis(g['quotient_vertices'], g['quotient_edges'])
    for _ in range(200):
        circuit = rng.choice(basis)
        chosen = [e for e in range(len(flow)) if circuit >> e & 1]
        available = sorted(set(range(1, 8))-{flow[e] for e in chosen})
        if available:
            a = rng.choice(available)
            for e in chosen:
                flow[e] ^= a
    values = dict(zip(g['kept_edge_ids'], flow))
    for b in g['blocks']:
        es = b['edge_representatives']
        p = tuple(values[e] for e in es[10:])
        chosen = rng.choice(fibers[p])
        values.update(zip(es[:10], chosen[:10]))
    return [values[e] for e in range(len(g['edges']))]


def repair(g, initial, normal, fibers, domains, witnesses):
    kept = g['kept_edge_ids']
    first = project([initial[e] for e in kept], normal)
    qword = four_cover(list(map(int, g['quotient_four_flow_word'])), first)
    pairs = dict(zip(kept, map(int, qword)))
    flow, cover, moves = initial.copy(), ['?']*len(initial), []
    for e, a in pairs.items():
        cover[e] = str(a)
    for i, b in enumerate(g['blocks']):
        es = b['edge_representatives']
        local = joint_repair([initial[e] for e in es], normal,
                             [pairs[e] for e in es[10:]], fibers, domains, witnesses)
        for move in local['moves']:
            selected = [es[j] for j in range(10) if move['circuit_mask'] >> j & 1]
            moves.append({'piece': i, 'edges': selected, 'increment': move['increment']})
            for e in selected:
                flow[e] ^= move['increment']
        for e, c in zip(es[:10], local['cover_word'][:10]):
            cover[e] = c
    assert '?' not in cover
    return {'normal': normal, 'quotient_cover_word': qword, 'moves': moves,
            'final_flow_word': word(flow), 'cover_word': ''.join(cover)}


def prism(k):
    edges = [(off+i, off+(i+1) % k) for off in (0, k) for i in range(k)]
    edges += [(i, k+i) for i in range(k)]
    colors = [1+(i % 2) for i in range(k)]
    if k % 2:
        colors[-1] = 3
    return 2*k, edges, [list(range(k))], colors+[colors[i-1] ^ colors[i] for i in range(k)]


def specs():
    k4 = list(itertools.combinations(range(4), 2))
    yield 'K4_triangle', 4, k4, [[0, 1, 2]], [1, 2, 3], False
    yield 'K4_hamiltonian', 4, k4, [[0, 1, 2, 3]], [1, 1], False
    n, edges, _, _ = prism(4)
    yield 'cube_two_faces', n, edges, [list(range(4)), list(range(4, 8))], [1]*4, False
    pe = [(i, (i+1) % 5) for i in range(5)]+[(i, i+5) for i in range(5)]
    pe += [(i+5, (i+2) % 5+5) for i in range(5)]
    yield 'Petersen_two_factors', 10, pe, [list(range(5)), [5, 7, 9, 6, 8]], [1, 1, 1, 2, 3], False
    for k in (3, 4, 5, 6, 12, 60):
        n, edges, cycles, flow = prism(k)
        yield f'prism_{k}', n, edges, cycles, flow, k % 6 == 0


def census(g):
    basis = cycle_basis(g['quotient_vertices'], g['quotient_edges'])
    assert len(basis) <= 16
    supports = [0]
    for b in basis:
        supports += [s ^ b for s in supports]
    digest = hashlib.sha256()
    four = list(map(int, g['quotient_four_flow_word']))
    for s in supports:
        digest.update(f'{s} {four_cover(four, s)}\n'.encode())
    return {'cycle_basis': basis, 'even_supports': len(supports), 'cover_sha256': digest.hexdigest()}


def sharpness(fibers, domains, witnesses):
    f = tuple(map(int, '52473145361212'))
    q = (0, 4, 0, 4)
    rec = joint_repair(f, 1, q, fibers, domains, witnesses)
    fs = fibers[f[10:]]
    neighbors = graph(fs, CIRCUITS)[fs.index(f)]
    rec.update({'four_flow_boundary': '2323', 'allowed_cover_supports': sorted(domains[q]),
                'one_step_flow_count': len(neighbors),
                'one_step_supports': sorted({project(fs[j]) for j, _, _ in neighbors})})
    assert len(rec['moves']) == 2
    return rec


def negative_spec():
    pe = [(i, (i+1) % 5) for i in range(5)]+[(i, i+5) for i in range(5)]
    pe += [(i+5, (i+2) % 5+5) for i in range(5)]
    available = {v: iter(range(3*v, 3*v+3)) for v in range(10)}
    cycles = [list(range(3*v, 3*v+3)) for v in range(10)]
    edges = [(c[j], c[(j+1) % 3]) for c in cycles for j in range(3)]
    edges += [(next(available[u]), next(available[v])) for u, v in pe]
    return {'base_vertices': 30, 'base_edges': edges, 'selected_cycles': cycles,
            'contracted_edges': pe, 'reason': 'The contracted graph is Petersen, which has no nowhere-zero four-flow.'}


def main():
    _, fibers = masks_and_flows()
    domains, witnesses = load_covers()
    source = HERE / 'junction_selection_obstruction.json'
    obstruction = json.loads(source.read_text())
    rng, examples = random.Random(20260930), []
    for name, n, edges, cycles, flow, use_old in specs():
        for kind in ('blowup', 'semi'):
            g = build(n, edges, cycles, kind)
            g['name'] = name+'_'+kind
            quotient_flow(g, flow)
            initial = initial_flow(g, fibers, rng, obstruction if use_old and kind == 'blowup' else None)
            g['initial_flow_word'] = word(initial)
            g['initial_flow_source'] = 'earlier_obstructed_family' if use_old and kind == 'blowup' else 'seeded_valid_switches_and_local_extensions'
            g['repairs'] = [repair(g, initial, l, fibers, domains, witnesses) for l in range(1, 8)]
            if name in ('K4_triangle', 'prism_3', 'prism_4', 'prism_5'):
                g['quotient_support_census'] = census(g)
            examples.append(g)
            print(g['name'], 'vertices', g['vertices'], 'moves', [len(r['moves']) for r in g['repairs']], flush=True)
    result = {'date': '2026-09-30',
              'scope': 'Four-flow criterion for contracted blowup and semiblowup quotients; any starting three-bit flow and any selected normal can be repaired within two pentagons per piece under that criterion. No general 5-CDC proof or novelty claim.',
              'source': {'file': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()},
              'junction_tables': {k: junction_states(k) for k in ('blowup', 'semi')},
              'local_two_switch_example': sharpness(fibers, domains, witnesses),
              'examples': examples, 'four_flow_condition_failure': negative_spec()}
    (HERE / 'fourflow_quotient_repair.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Saved', len(examples), 'graph examples and', 7*len(examples), 'coordinate repairs.')


if __name__ == '__main__':
    main()
