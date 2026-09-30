#!/usr/bin/env python3
"""Simultaneous flow/cover extension through Petersen four-poles.

Standard library only. Exhaustive local classification plus executable graph
extensions from covers of the contracted graph. No general 5-CDC proof.
"""
from collections import Counter, defaultdict
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from petersen_flow_repair import masks_and_flows, graph, distances

HERE = Path(__file__).parent
CIRCUITS = [151, 301, 442, 602, 717, 887, 992]
PENTAGONS = [s for s in CIRCUITS if s.bit_count() == 5]
INTERNAL = [(2, 3), (3, 4), (2, 7), (3, 8), (4, 9),
            (5, 7), (6, 8), (7, 9), (8, 5), (9, 6)]
PAIRS = [sum(1 << a for a in p) for p in itertools.combinations(range(5), 2)]
QUOTIENT_COVERS = [
    '321218197773275151784380123509451680123535922002',
    '052363620900036029933223369090322514257799635236',
    '836521310907925710833614410011328723520935891661',
    '406021013357253223389182604598817382694380123590',
    '293893932172873827187979172819833278211331178219',
    '131718388223923562310707316262053003396253290220',
    '548147476305102145120022590303295236630033209674',
]


def word(f):
    return ''.join(map(str, f))


def project(f, normal=1):
    return sum(1 << e for e, a in enumerate(f) if (a & normal).bit_count() % 2)


def load_covers():
    domains, witnesses = defaultdict(set), {}
    with gzip.open(HERE / 'petersen_boundary_relation.txt.gz', 'rt') as stream:
        for line in stream:
            mask, boundary, witness = line.split()
            key = tuple(map(int, boundary))
            domains[key].add(int(mask))
            witnesses[int(mask), key] = witness
    return dict(domains), witnesses


def local_audit(even, fibers, domains):
    by_bits = defaultdict(list)
    for q, masks in domains.items():
        by_bits[tuple(PAIRS[a] & 1 for a in q)].append((q, masks))
    intersections, all_hist, five_hist = Counter(), Counter(), Counter()
    flow_records, exceptions = [], []
    cases = 0
    for p, fs in sorted(fibers.items()):
        masks = [project(f) for f in fs]
        projected = set(masks)
        prescribed_bits = tuple(a & 1 for a in p)
        possible = {s for s in even if tuple(s >> (10+i) & 1 for i in range(4)) == prescribed_bits}
        missing = sorted(possible-projected)
        expected_missing = [0] if not any(prescribed_bits) and p[0] != p[1] else []
        assert missing == expected_missing and len(possible) == 8
        flow_records.append({'boundary': word(p), 'supports': sorted(projected)})
        if missing:
            exceptions.append(word(p))
        all_adj, five_adj = graph(fs, CIRCUITS), graph(fs, PENTAGONS)
        grouped = Counter(tuple(sorted(ss)) for q, ss in by_bits[prescribed_bits])
        for target, multiplicity in grouped.items():
            intersections[len(projected & set(target))] += multiplicity
            sources = [i for i, mask in enumerate(masks) if mask in target]
            da, dp = distances(all_adj, sources), distances(five_adj, sources)
            assert len(da) == len(dp) == len(fs) and max(dp.values()) <= 2
            all_hist.update({d: n*multiplicity for d, n in Counter(da.values()).items()})
            five_hist.update({d: n*multiplicity for d, n in Counter(dp.values()).items()})
            cases += len(fs)*multiplicity
    return {'flow_boundary_supports': flow_records,
            'cover_boundary_supports': [{'boundary': word(q), 'supports': sorted(ss)} for q, ss in sorted(domains.items())],
            'exceptional_flow_boundaries': exceptions, 'missing_support_in_each_exception': 0,
            'flow_count': sum(map(len, fibers.values())),
            'realized_flow_boundary_support_pairs': sum(len(r['supports']) for r in flow_records),
            'cover_boundary_support_pairs': sum(map(len, domains.values())),
            'distinct_cover_support_sets': len({tuple(sorted(ss)) for ss in domains.values()}),
            'compatible_boundary_pairs': sum(intersections.values()),
            'common_support_histogram': sorted(intersections.items()),
            'starting_flow_cover_boundary_cases': cases,
            'all_circuit_distance_histogram': sorted(all_hist.items()),
            'pentagon_distance_histogram': sorted(five_hist.items())}


def joint_repair(start, normal, cover_boundary, fibers, domains, witnesses):
    fs = fibers[tuple(start[10:])]
    masks = [project(f, normal) for f in fs]
    adjacency = graph(fs, PENTAGONS)
    q = tuple(cover_boundary)
    d = distances(adjacency, [i for i, mask in enumerate(masks) if mask in domains[q]])
    at, moves = fs.index(tuple(start)), []
    while d[at]:
        following, circuit, a = min(move for move in adjacency[at] if d[move[0]] == d[at]-1)
        moves.append({'circuit_mask': circuit, 'increment': a})
        at = following
    assert len(moves) <= 2
    return {'initial_flow_word': word(start), 'normal': normal, 'cover_boundary': word(q),
            'moves': moves, 'final_flow_word': word(fs[at]),
            'cover_word': witnesses[masks[at], q], 'final_support': masks[at]}


def sharpness(fibers, domains, witnesses):
    start = tuple(map(int, '35761136574444'))
    result = joint_repair(start, 1, (4, 9, 4, 9), fibers, domains, witnesses)
    fs = fibers[start[10:]]
    at = fs.index(start)
    neighbors = graph(fs, CIRCUITS)[at]
    result.update({'allowed_cover_supports': sorted(domains[(4, 9, 4, 9)]),
                   'initial_support': project(start), 'one_step_flow_count': len(neighbors),
                   'one_step_supports': sorted({project(fs[j]) for j, _, _ in neighbors})})
    assert len(result['moves']) == 2
    return result


def necklace(q, sharp, witnesses):
    edges = [(8*i+x-2, 8*i+y-2) for i in range(q) for x, y in INTERNAL]
    edges += [(8*i+v, 8*((i+1) % q)+w) for i in range(q) for v, w in ((2, 0), (3, 4))]
    start = list(map(int, sharp['initial_flow_word'][:10]))*q+[4]*(2*q)
    flow, moves = start.copy(), []
    for i in range(q):
        for move in sharp['moves']:
            es = [10*i+j for j in range(10) if move['circuit_mask'] >> j & 1]
            for e in es:
                flow[e] ^= move['increment']
            moves.append({'piece': i, 'edges': es, 'increment': move['increment']})
    return {'pieces': q, 'vertices': 8*q, 'edges': edges, 'initial_flow_word': word(start),
            'prescribed_exterior_cover_word': '49'*q,
            'moves': moves, 'final_flow_word': word(flow),
            'cover_word': sharp['cover_word'][:10]*q+'49'*q,
            'initial_cover_with_different_exterior_pairs': witnesses[887, (4, 4, 4, 4)][:10]*q+'44'*q,
            'exact_internal_distance_preserving_prescribed_exterior_cover': 2*q}


def quotient_and_repairs(seed, fibers, domains, witnesses):
    g = seed['examples'][0]
    owner = list(range(72))
    for i, block in enumerate(g['blocks']):
        for v in block['vertices']:
            owner[v] = 12+i
    names = {v: i for i, v in enumerate(sorted(set(owner)))}
    owner = [names[v] for v in owner]
    kept = [e for e, (u, v) in enumerate(g['edges']) if owner[u] != owner[v]]
    quotient = {'vertices': len(names), 'vertex_map': owner, 'kept_edge_ids': kept,
                'edges': [[owner[u], owner[v]] for e, (u, v) in enumerate(g['edges']) if e in kept],
                'flow_word': word([g['flow'][e] for e in kept])}
    results = []
    for normal, qword in enumerate(QUOTIENT_COVERS, 1):
        pairs = {e: int(d) for e, d in zip(kept, qword)}
        blocks = []
        flow, cover, moves = g['flow'].copy(), ['?']*108, []
        for e, digit in pairs.items():
            cover[e] = str(digit)
        for i, b in enumerate(g['blocks']):
            es = b['edge_representatives']
            local = joint_repair([flow[e] for e in es], normal, [pairs[e] for e in es[10:]], fibers, domains, witnesses)
            blocks.append(local)
            for move in local['moves']:
                chosen = [es[j] for j in range(10) if move['circuit_mask'] >> j & 1]
                for e in chosen:
                    flow[e] ^= move['increment']
                moves.append({'piece': i, 'edges': chosen, 'increment': move['increment'],
                              'local_circuit_mask': move['circuit_mask']})
            for e, digit in zip(es[:10], local['cover_word'][:10]):
                cover[e] = digit
        assert len(moves) == 1 and '?' not in cover
        results.append({'normal': normal, 'quotient_cover_word': qword, 'blocks': blocks,
                        'moves': moves, 'final_flow_word': word(flow), 'cover_word': ''.join(cover)})
    return quotient, results


def periodic(seed, repairs, m):
    records = []
    for r in repairs:
        moves = [{'piece': 6*s+move['piece'], 'edges': [108*s+e for e in move['edges']],
                  'increment': move['increment']} for s in range(m) for move in r['moves']]
        records.append({'normal': r['normal'], 'moves': moves,
                        'final_flow_word': r['final_flow_word']*m, 'cover_word': r['cover_word']*m,
                        'support_size': project(tuple(map(int, r['final_flow_word'])), r['normal']).bit_count()*m,
                        'exact_internal_repair_distance_for_this_normal': m})
    return {'repetitions': m, 'vertices': 72*m,
            'initial_flow_word': word(seed['examples'][0]['flow'])*m, 'repairs': records}


def main():
    even, fibers = masks_and_flows()
    domains, witnesses = load_covers()
    source = HERE / 'junction_selection_obstruction.json'
    relation = HERE / 'petersen_boundary_relation.txt.gz'
    seed = json.loads(source.read_text())
    sharp = sharpness(fibers, domains, witnesses)
    quotient, repairs = quotient_and_repairs(seed, fibers, domains, witnesses)
    result = {'date': '2026-09-30',
              'scope': 'Exact joint extension and two-pentagon repair for a prescribed exterior five-layer cover; coordinate-completion reduction and family certificates. No general 5-CDC proof or novelty claim.',
              'sources': [{'file': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in (source, relation)],
              'local_audit': local_audit(even, fibers, domains), 'sharp_local_example': sharp,
              'sharp_graph_examples': [necklace(q, sharp, witnesses) for q in (3, 6, 12)],
              'quotient': quotient, 'seed_coordinate_repairs': repairs,
              'periodic_coordinate_repairs': [periodic(seed, repairs, m) for m in (1, 2, 10)]}
    (HERE / 'joint_boundary_completion.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Verified in construction: 21,640 compatible boundary pairs, 2,455,920 starting-flow cases, at most two pentagons.')
    for r in repairs:
        move = r['moves'][0]
        print('Normal', r['normal'], ': piece', move['piece'], 'local circuit', move['local_circuit_mask'], 'increment', move['increment'])
    print('Saved quotient covers, local sharpness, and graph extensions; standard library only.')


if __name__ == '__main__':
    main()
