#!/usr/bin/env python3
"""An actual core requiring a neutral auxiliary exchange before repair.

One exchange may use any even edge subgraph, but only one auxiliary label
pair. The explicit witness needs exactly two such exchanges. Standard library.
"""
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from core_component_exchange import (attempt, initialize, realize_mask,
                                     regions_for, split_forest)
from eight_cycle_completion import example_seed, marked_test
from fourflow_quotient_repair import build, contracted
from joint_boundary_completion import PAIRS, joint_repair, load_covers, masks_and_flows, word
from nine_cycle_completion import AUX, bad_regions
from short_cycle_boundary import local_table

HERE = Path(__file__).resolve().parent
BOUNDARY = [6, 6, 10, 6, 24, 6, 12, 18, 20, 10, 18]
# Endpoints in the 22-vertex cubic base, cover-pair mask, two-bit flow value.
# Edge zero meets port 2, so the Petersen attachment is visited by the
# neutral circuit in the attached examples.
OUTSIDE = [
    (2, 11, 10, 2), (0, 19, 6, 3), (1, 13, 6, 1), (3, 12, 6, 1),
    (4, 16, 24, 3), (5, 20, 6, 1), (6, 11, 12, 3), (7, 13, 18, 2),
    (8, 20, 20, 3), (9, 17, 10, 3), (10, 15, 18, 2), (11, 21, 6, 1),
    (12, 16, 18, 2), (12, 18, 20, 3), (13, 21, 20, 3), (14, 15, 24, 3),
    (14, 17, 9, 2), (14, 18, 17, 1), (15, 16, 10, 1), (17, 19, 3, 1),
    (18, 19, 5, 2), (20, 21, 18, 2),
]


def seed(kind, table, fibers):
    base = [(i, (i+1) % 11) for i in range(11)]+[(u, v) for u, v, _, _ in OUTSIDE]
    g = build(22, base, [list(range(11))], kind)
    return initialize(g, [r for _, _, r, _ in OUTSIDE], [15]*11,
                      [f for _, _, _, f in OUTSIDE], table, fibers)


def full_example(kind, attached, table, fibers, domains, witnesses):
    g, initial, original = example_seed(seed(kind, table, fibers), attached)
    core = contracted(g)
    regions = regions_for(g, initial, original)
    assert [original[h//2] for h in regions[0]['incidences']] == BOUNDARY
    blocked = []
    for t in AUX:
        rec, changed = attempt(core, regions, original, 0, t, [])
        assert changed is None
        blocked.append(rec)
    # First change the boundary without repairing it. Both affected ports
    # meet the same outside cubic vertex in the unattached core.
    blocks, terminals, forest = split_forest(core, regions, original, 0, 6, [])
    mask = (1 << 2) | (1 << 6)
    edges = realize_mask(mask, terminals, forest)
    neutral = [a ^ 6 if e in edges else a for e, a in enumerate(original)]
    assert bad_regions(regions, original) == bad_regions(regions, neutral) == [0]
    first = {'swap_pair': 6, 'selected_ports': [2, 6], 'edges': edges,
             'cover_word_after': word(PAIRS.index(a) for a in neutral),
             'bad_before': [0], 'bad_after': [0]}
    rec, changed = attempt(core, regions, neutral, 0, 10, [])
    assert changed is not None and not bad_regions(regions, changed)
    g.update({'name': 'petersen_attachment' if attached else 'native',
              'core': core, 'regions': regions, 'profile_names': ['11'],
              'blocked_attempts': blocked, 'neutral_exchange': first,
              'repair_exchange': rec, 'minimum_auxiliary_exchanges': 2})
    pairs = dict(enumerate(changed))
    letters = [[changed[j['edges'][-1]], 15] for j in g['junctions']]
    _, allowed = marked_test(letters)
    h, prefix = min(allowed), 0
    charges = [{'letters': letters, 'surviving_charges': allowed, 'chosen_charge': h}]
    for j, (r, z) in zip(g['junctions'], letters):
        for e, a in zip(j['edges'], table[r, z][h ^ prefix]):
            assert e not in pairs or pairs[e] == a
            pairs[e] = a
        prefix ^= r
    cover = ['?']*len(g['edges'])
    for e, a in pairs.items():
        cover[e] = str(PAIRS.index(a))
    flow, moves = initial.copy(), []
    for i, block in enumerate(g['blocks']):
        es = block['edge_representatives']
        repair = joint_repair([flow[e] for e in es], 1, [PAIRS.index(pairs[e]) for e in es[10:]],
                              fibers, domains, witnesses)
        for move in repair['moves']:
            selected = [es[j] for j in range(10) if move['circuit_mask'] >> j & 1]
            moves.append({'piece': i, 'edges': selected, 'increment': move['increment']})
            for e in selected:
                flow[e] ^= move['increment']
        for e, a in zip(es[:10], repair['cover_word'][:10]):
            cover[e] = a
    g.update({'original_core_cover_word': word(PAIRS.index(a) for a in original),
              'changed_core_cover_word': word(PAIRS.index(a) for a in changed),
              'regional_extensions': charges, 'initial_flow_word': word(initial),
              'quotient_cover_word': word(PAIRS.index(pairs[e]) for e in g['kept_edge_ids']),
              'moves': moves, 'final_flow_word': word(flow), 'cover_word': ''.join(cover)})
    return g


def main():
    result = {'date': '2026-10-05',
              'scope': 'An actual cubic-core realization blocks every one-step auxiliary-label exchange, including arbitrary even-subgraph unions. A neutral exchange followed by a repair proves distance exactly two. No obstruction to cover existence is asserted.',
              'sources': [{'file': name, 'sha256': hashlib.sha256((HERE/name).read_bytes()).hexdigest()}
                          for name in ('core_component_exchange.json', 'triangle_quotient_reduction.json',
                                       'petersen_boundary_relation.txt.gz')],
              'base_vertices': 22, 'selected_cycle': list(range(11)),
              'outside_edges_pairs_four_flow': [list(row) for row in OUTSIDE],
              'boundary_word': BOUNDARY, 'examples': []}
    domains, witnesses = load_covers()
    _, fibers = masks_and_flows()
    pet = json.loads((HERE/'triangle_quotient_reduction.json').read_text())['petersen']
    for kind in ('blowup', 'semi'):
        table, _ = local_table(kind)
        for attached in (None, pet):
            g = full_example(kind, attached, table, fibers, domains, witnesses)
            result['examples'].append(g)
            print(kind, g['name'], g['vertices'], 'vertices;',
                  len(g['neutral_exchange']['edges']), '+', len(g['repair_exchange']['edges']),
                  'core-circuit edges;', len(g['moves']), 'B pentagons', flush=True)
    (HERE/'actual_core_exchange_obstruction.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
