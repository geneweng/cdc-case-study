#!/usr/bin/env python3
"""Linear, bounded-circuit regional repair with an exact junction distance.

Standard library only. The companion verifier rebuilds the local relations
and distances independently and checks every saved graph-level operation.
"""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
from fourflow_quotient_repair import build, quotient_flow
from short_cycle_boundary import EVEN, cap, local_table, quotient_assignment
from region_joint_repair import apply, finish, path_in_edges
from joint_boundary_completion import INTERNAL, PAIRS, PENTAGONS, load_covers, masks_and_flows, word

HERE = Path(__file__).parent
POSITIONS = {'blowup': [[0, 1, 4, 5], [2, 3, 4, 5], [0, 1, 2, 3]],
             'semi': [[0, 1, 2, 3]]}


def flow_fibers(kind):
    result = defaultdict(list)
    for a, b, c, d in itertools.product(range(1, 8), repeat=4):
        p = a ^ b ^ c ^ d
        if not p or (kind == 'semi' and b != d):
            continue
        if kind == 'blowup' and (a == c or b == d):
            continue
        values = [a, b, c, d]+([a ^ c, b ^ d] if kind == 'blowup' else [])+[p]
        result[p, a ^ b].append(values)
    return dict(result)


def zbits(values):
    return sum((a & 1) << i for i, a in enumerate(values[:4]))


def local_repair(kind, table, initial, r, charge):
    def cover(values):
        return table[r, zbits(values)].get(charge)
    cw = cover(initial)
    if cw is not None:
        return initial.copy(), cw, None
    for positions in POSITIONS[kind]:
        for a in range(1, 8):
            if any(initial[j] == a for j in positions):
                continue
            after = [v ^ a if j in positions else v for j, v in enumerate(initial)]
            cw = cover(after)
            if cw is not None:
                return after, cw, {'positions': positions, 'increment': a}
    raise AssertionError((kind, initial, r, charge))


def audit(kind, table, fibers):
    records, histogram, sharp = [], Counter(), None
    for (p, h), fs in sorted(fibers.items()):
        for f in fs:
            for r in PAIRS:
                if (p & 1) != (r & 1):
                    continue
                for c in EVEN:
                    if (h & 1) != (c & 1):
                        continue
                    after, cw, move = local_repair(kind, table, f, r, c)
                    d = int(move is not None)
                    histogram[d] += 1
                    records.append([p, h, word(f), r, c, d])
                    if d and sharp is None:
                        sharp = {'initial_flow': f, 'boundary_pair': r, 'cover_charge': c,
                                 'move': move, 'final_flow': after, 'cover_pairs': cw}
    digest = hashlib.sha256(json.dumps(sorted(records), separators=(',', ':')).encode()).hexdigest()
    return {'flow_count': sum(map(len, fibers.values())),
            'fiber_size_histogram': sorted(Counter(map(len, fibers.values())).items()),
            'compatible_cases': len(records), 'distance_histogram': sorted(histogram.items()),
            'distance_sha256': digest, 'sharp_one_move': sharp}


def repair_quotient(g, initial, core_cover, table):
    kind, kept = g['construction'], g['kept_edge_ids']
    index = {e: i for i, e in enumerate(kept)}
    junctions = [[index[e] for e in j['edges']] for j in g['junctions']]
    flow, pairs, moves, cycles = initial.copy(), list(map(int, core_cover)), [], []
    pairs += [None]*(len(kept)-len(pairs))
    offset = 0
    for cycle in g['selected_cycles']:
        js = junctions[offset:offset+len(cycle)]
        h = flow[js[0][0]] ^ flow[js[0][1]]
        candidates = [c for c in EVEN if (c & 1) == (h & 1)]
        costs = []
        for c in candidates:
            at, bad = c, 0
            for ids in js:
                r = PAIRS[int(core_cover[ids[-1]])]
                bad += at not in table[r, zbits([flow[e] for e in ids])]
                at ^= r
            assert at == c
            costs.append(bad)
        delta = min(costs)
        chosen = candidates[costs.index(delta)]
        assert delta <= len(cycle)//4
        cycles.append({'length': len(cycle), 'initial_flow_charge': h,
                       'initial_cover_charges': candidates, 'incompatible_junction_counts': costs,
                       'chosen_cover_charge': chosen, 'delta': delta})
        at = chosen
        for j, ids in enumerate(js, offset):
            r = PAIRS[int(core_cover[ids[-1]])]
            _, cw, move = local_repair(kind, table, [flow[e] for e in ids], r, at)
            if move is not None:
                chosen_edges = sorted({ids[i] for i in move['positions']})
                apply(flow, chosen_edges, move['increment'])
                moves.append({'junction': j, 'edges': chosen_edges, 'increment': move['increment']})
            for e, c in zip(ids, cw):
                digit = PAIRS.index(c)
                assert pairs[e] is None or pairs[e] == digit
                pairs[e] = digit
            at ^= r
        offset += len(cycle)
    assert all(p is not None for p in pairs)
    assert len(moves) == sum(c['delta'] for c in cycles)
    return {'initial_flow_word': word(initial), 'core_cover_word': core_cover,
            'cycles': cycles, 'moves': moves, 'final_flow_word': word(flow),
            'cover_word': word(pairs), 'junction_distance': len(moves)}


def bounded_lift(g, initial, quotient_moves):
    flow, moves = initial.copy(), []
    edges = dict(enumerate(INTERNAL))
    ports = [4, 5, 2, 6]
    for move in quotient_moves:
        ids = [g['kept_edge_ids'][e] for e in move['edges']]
        lifted, a = ids.copy(), move['increment']
        junction = g['junctions'][move['junction']]
        for i in sorted({junction['left_piece'], junction['right_piece']}):
            block = g['blocks'][i]
            es = block['edge_representatives']
            selected = [j for j, e in enumerate(es[10:]) if e in ids]
            if not selected:
                continue
            assert len(selected) == 2
            endpoints = [ports[j] for j in selected]
            local = {j: flow[e] for j, e in enumerate(es[:10])}
            path = path_in_edges(edges, range(10), *endpoints, local, a)
            if path is None or len(path) > 3:
                found = False
                for mask, t in itertools.product(PENTAGONS, range(1, 8)):
                    cs = [e for e in range(10) if mask >> e & 1]
                    if any(local[e] == t for e in cs):
                        continue
                    after = local.copy()
                    apply(after, cs, t)
                    candidate = path_in_edges(edges, range(10), *endpoints, after, a)
                    if candidate is not None and len(candidate) <= 3:
                        selected_edges = [es[e] for e in cs]
                        apply(flow, selected_edges, t)
                        moves.append({'kind': 'piece_preparation', 'piece': i,
                                      'edges': selected_edges, 'increment': t})
                        path, found = candidate, True
                        break
                assert found
            lifted.extend(es[e] for e in path)
        assert len(lifted) <= (10 if g['construction'] == 'blowup' else 9)
        apply(flow, lifted, a)
        moves.append({'kind': 'lifted_junction', 'junction': move['junction'],
                      'edges': lifted, 'increment': a})
    return flow, moves


def full_repair(g, initial, core_cover, table, fibers, domains, witnesses):
    qf = [initial[e] for e in g['kept_edge_ids']]
    qr = repair_quotient(g, qf, core_cover, table)
    flow, moves = bounded_lift(g, initial, qr['moves'])
    flow, cw, tail = finish(g, flow, qr['cover_word'], fibers, domains, witnesses)
    moves += tail
    assert len(moves) <= 2*g['pieces']+3*qr['junction_distance']
    return {'quotient_repair': qr, 'moves': moves, 'final_flow_word': word(flow),
            'cover_word': cw, 'switch_bound': 2*g['pieces']+3*qr['junction_distance']}


def sharp_graph(kind, m, fibers):
    k = 8*m
    permutation = [8*j+i for j in range(m) for i in (0, 1, 5, 2, 3, 7, 4, 6)]
    inverse = {v: i for i, v in enumerate(permutation)}
    base = [(off+i, off+(i+1) % k) for off in (0, k) for i in range(k)]
    base += [(i, k+inverse[i]) for i in range(k)]
    g = build(2*k, base, [list(range(k))], kind)
    quotient_flow(g, [1, 2]*(k//2)+[3]*k)
    boundary = [6, 10, 6, 18, 6, 10, 6, 18]*m
    first, _ = quotient_assignment(g, [[r, 15] for r in boundary], None)
    four = list(map(int, g['quotient_four_flow_word']))
    values = {e: 2*a+(first >> i & 1) for i, (e, a) in enumerate(zip(g['kept_edge_ids'], four))}
    for b in g['blocks']:
        es = b['edge_representatives']
        local = fibers[tuple(values[e] for e in es[10:])][0]
        values.update(zip(es[:10], local[:10]))
    initial = [values[e] for e in range(len(g['edges']))]
    rim = [12, 6, 12, 10, 24, 10, 12, 10]*m
    g['initial_flow_word'] = word(initial)
    return g, word(PAIRS.index(a) for a in rim+boundary)


def cap_examples(kind, table, fibers, source, rng):
    records = []
    for old in source['caps'][kind]:
        k = old['length']
        g = cap(kind, k)
        p = list(map(int, old['flow_word'][:k]))
        hf = rng.randrange(8)
        index = {e: i for i, e in enumerate(g['kept_edge_ids'])}
        values = dict(enumerate(p))
        for junction in g['junctions']:
            ids = [index[e] for e in junction['edges']]
            fv = rng.choice(fibers[values[ids[-1]], hf])
            for e, a in zip(ids, fv):
                assert e not in values or values[e] == a
                values[e] = a
            hf ^= fv[-1]
        qr = repair_quotient(g, [values[e] for e in range(len(g['quotient_edges']))], old['cover_word'][:k], table)
        records.append({'length': k, 'vertices': g['quotient_vertices'],
                        'edges': g['quotient_edges'], 'repair': qr})
    return records


def main():
    previous = json.loads((HERE / 'short_cycle_boundary.json').read_text())
    regional = json.loads((HERE / 'region_joint_repair.json').read_text())
    _, fibers = masks_and_flows()
    domains, witnesses = load_covers()
    rng = random.Random(20261001)
    result = {'date': '2026-09-30',
              'scope': 'Exact distance for quotient switches confined to single junctions; linear full-region repair using circuits of length at most ten. The supplied core cover is an input, not a general existence proof.',
              'sources': [{'file': name, 'sha256': hashlib.sha256((HERE / name).read_bytes()).hexdigest()}
                          for name in ('short_cycle_boundary.json', 'region_joint_repair.json',
                                       'petersen_flow_repair.json', 'joint_boundary_completion.json')],
              'local_audits': {}, 'caps': {}, 'previous_examples': [], 'sharp_family': []}
    for kind in ('blowup', 'semi'):
        table, _ = local_table(kind)
        jf = flow_fibers(kind)
        result['local_audits'][kind] = audit(kind, table, jf)
        result['caps'][kind] = cap_examples(kind, table, jf, regional, rng)
        g = next(g for g in previous['cubic_examples'] if g['construction'] == kind)
        rec = full_repair(g, list(map(int, g['initial_flow_word'])), g['rejected_core_cover_word'], table, fibers, domains, witnesses)
        result['previous_examples'].append({'construction': kind, 'repair': rec})
        print(kind, 'previous octagon:', rec['quotient_repair']['junction_distance'],
              'junction switch;', len(rec['moves']), 'full switches', flush=True)
        for m in (1, 2, 4, 8):
            g, cw = sharp_graph(kind, m, fibers)
            rec = full_repair(g, list(map(int, g['initial_flow_word'])), cw, table, fibers, domains, witnesses)
            assert rec['quotient_repair']['junction_distance'] == 2*m
            result['sharp_family'].append({'construction': kind, 'repetitions': m, 'graph': g, 'repair': rec})
            print(kind, 'm =', m, 'vertices', g['vertices'], 'junction distance', 2*m,
                  'full switches', len(rec['moves']), 'max length', max(map(lambda x: len(x['edges']), rec['moves'])), flush=True)
    (HERE / 'linear_region_repair.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Saved all 70,176 local cases as distance digests, 18 caps, and ten complete cubic repairs.')


if __name__ == '__main__':
    main()
