#!/usr/bin/env python3
"""Length-ten finite proof and full graph certificates; see independent verifier.

Requires Python 3 and a C++17 compiler. Compiled executables are temporary.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from eight_cycle_completion import example_seed, marked_test
from fourflow_quotient_repair import build, contracted, quotient_flow
from joint_boundary_completion import PAIRS, joint_repair, load_covers, masks_and_flows, word
from nine_cycle_completion import bad_regions, repair_core
from short_cycle_boundary import local_table, quotient_assignment

HERE = Path(__file__).resolve().parent
SPECS = {
    'eight': ([6, 10, 6, 18]*2, [15]*8, (0, 2)),
    'nine_odd': ([3, 6, 10, 6, 18, 6, 10, 6, 17], [14]+[15]*7+[11], (1, 3)),
    'single_forcing_pair': ([6, 6, 10, 6, 18, 6, 6, 10, 6, 18], [15]*10, (1, 3)),
    'four_distinguished_ports': ([3, 6, 10, 6, 3, 17, 6, 10, 6, 17],
                                 [14, 15, 15, 15, 11]*2, (1, 3)),
}


def finite_audit():
    with tempfile.TemporaryDirectory(prefix='cdc-ten-') as tmp:
        binary = str(Path(tmp)/'boundary')
        subprocess.run([os.environ.get('CXX', 'c++'), '-std=c++17', '-O3',
                        str(HERE/'ten_cycle_boundary.cpp'), '-o', binary], check=True)
        rows = subprocess.check_output([binary], text=True).splitlines()
    result = []
    for row in rows:
        marked, odd, groups, total, bad, threats, good, *hist = map(int, row.split())
        assert len(hist) == 7 and hist[0] == 0 and sum(hist) == bad
        result.append({'marked_mask': marked, 'odd_cut_mask': odd,
                       'swap_orbits': groups, 'closed_words': total, 'bad_words': bad,
                       'threat_groups': threats, 'good_states_checked': good,
                       'automatically_safe_good_states': total-bad-good,
                       'forcing_pair_histogram': hist})
        print('Boundary', marked, odd, ':', bad, 'bad;', good, 'protected good cases.', flush=True)
    assert len(result) == 18
    return result


def region_records(g, initial, pairs):
    core = contracted(g)
    records, offset = [], 0
    for cycle in g['selected_cycles']:
        js = g['junctions'][offset:offset+len(cycle)]
        letters = [[pairs[j['edges'][-1]], sum((initial[e] & 1) << i for i, e in enumerate(j['edges'][:4]))]
                   for j in js]
        marked, _ = marked_test(letters)
        hs = [2*j['edges'][-1]+g['edges'][j['edges'][-1]].index(j['vertex']) for j in js]
        assert len(marked) <= 7 or len(cycle) in (8, 9, 10)
        records.append({'hub': core['vertex_map'][cycle[0]], 'incidences': hs,
                        'marked_cuts': marked, 'critical': len(marked) >= 8,
                        'junction_indices': list(range(offset, offset+len(cycle)))})
        offset += len(cycle)
    return records


def seed(kind, profiles, table, fibers, protect_example=False):
    cycles, zs, entries, n = [], [], {}, 0
    for cell, profile in enumerate(profiles):
        rs, bits, _ = SPECS[profile]
        k = len(rs)
        cs = [list(range(n, n+k)), list(range(n+k, n+2*k))]
        cycles.extend(cs)
        zs.extend(bits*2)
        four = [1]*k if k % 2 == 0 else [1]*(k-2)+[2, 3]
        second_positions = list(range(k))
        if protect_example:
            assert profiles == ['four_distinguished_ports']
            second_positions[0], second_positions[5] = 5, 0
        for i, (r, a) in enumerate(zip(rs, four)):
            entries[cell, i] = ([cs[0][i], cs[1][second_positions[i]]], r, a)
        n += 2*k
    joined = []
    for cell in range(len(profiles)-1):
        left = entries.pop((cell, SPECS[profiles[cell]][2][1]))
        right = entries.pop((cell+1, SPECS[profiles[cell+1]][2][0]))
        assert left[1:] == right[1:] == (6, 1)
        (u, v), _, _ = left
        (x, y), _, _ = right
        joined.extend([([u, x], 6, 1), ([v, y], 6, 1)])
    outside = sorted(list(entries.values())+joined, key=lambda row: bool(row[1] & 1))
    base = [(c[i], c[(i+1) % len(c)]) for c in cycles for i in range(len(c))]
    base.extend(uv for uv, _, _ in outside)
    g = build(n, base, cycles, kind)
    quotient_flow(g, [a for _, _, a in outside])
    pairs = [r for _, r, _ in outside]
    letters = [[pairs[j['edges'][-1]], z] for j, z in zip(g['junctions'], zs)]
    support, _ = quotient_assignment(g, letters, table)
    hf = [2*int(a)+(support >> i & 1) for i, a in enumerate(g['quotient_four_flow_word'])]
    values = dict(zip(g['kept_edge_ids'], hf))
    for block in g['blocks']:
        es = block['edge_representatives']
        local = fibers[tuple(values[e] for e in es[10:])][0]
        values.update(zip(es[:10], local[:10]))
    g['initial_flow_word'] = word(values[e] for e in range(len(g['edges'])))
    g['rejected_core_cover_word'] = word(PAIRS.index(a) for a in pairs)
    return g


def full_example(kind, name, profiles, pet, table, fibers, domains, witnesses):
    old = seed(kind, profiles, table, fibers, name == 'protected_four_distinguished_ports')
    g, initial, original = example_seed(old, pet)
    core = contracted(g)
    regions = region_records(g, initial, original)
    changed, cover_moves = repair_core(core, regions, original)
    pairs, charges = dict(enumerate(changed)), []
    for region in regions:
        js = [g['junctions'][i] for i in region['junction_indices']]
        letters = [[changed[j['edges'][-1]], sum((initial[e] & 1) << i for i, e in enumerate(j['edges'][:4]))]
                   for j in js]
        _, allowed = marked_test(letters)
        assert allowed
        h, prefix = min(allowed), 0
        charges.append({'letters': letters, 'surviving_charges': allowed, 'chosen_charge': h})
        for j, (r, z) in zip(js, letters):
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
    g.update({'name': name, 'core': core, 'regions': regions, 'profile_names': [p for p in profiles for _ in range(2)],
              'original_core_cover_word': word(PAIRS.index(a) for a in original),
              'core_cover_moves': cover_moves, 'changed_core_cover_word': word(PAIRS.index(a) for a in changed),
              'regional_extensions': charges, 'initial_flow_word': word(initial),
              'quotient_cover_word': word(PAIRS.index(pairs[e]) for e in g['kept_edge_ids']),
              'moves': moves, 'final_flow_word': word(flow), 'cover_word': ''.join(cover)})
    if name == 'protected_four_distinguished_ports':
        es = [g['junctions'][i]['edges'][-1] for i in (0, 5)]
        naive = [r ^ 18 if e in es else r for e, r in enumerate(original)]
        assert bad_regions(regions, original) == [0] and bad_regions(regions, naive) == [1]
        g['unprotected_exchange'] = {'swap_pair': 18, 'edges': es, 'bad_before': [0], 'bad_after': [1],
                                     'cover_word_after': word(PAIRS.index(a) for a in naive)}
    return g



def main():
    result = {'date': '2026-10-05',
              'scope': 'Conditional fixed-layer core reduction for any number of selected cycles of lengths three through ten. No general 5-CDC proof or result for longer regions with eight or more marked cuts is claimed.',
              'sources': [{'file': name, 'sha256': hashlib.sha256((HERE/name).read_bytes()).hexdigest()}
                          for name in ('nine_cycle_completion.json', 'triangle_quotient_reduction.json',
                                       'petersen_boundary_relation.txt.gz')],
              'local_cases': finite_audit(), 'examples': []}
    domains, witnesses = load_covers()
    _, fibers = masks_and_flows()
    pet = json.loads((HERE/'triangle_quotient_reduction.json').read_text())['petersen']
    for kind in ('blowup', 'semi'):
        table, _ = local_table(kind)
        cases = [('single_forcing_pair', ['single_forcing_pair'], None),
                 ('four_distinguished_ports', ['four_distinguished_ports'], None),
                 ('protected_four_distinguished_ports', ['four_distinguished_ports'], None),
                 ('mixed_eight_nine_ten_no_four_flow', list(SPECS), pet)]
        for name, profiles, attached in cases:
            g = full_example(kind, name, profiles, attached, table, fibers, domains, witnesses)
            result['examples'].append(g)
            print(kind, name, g['vertices'], 'vertices;', len(g['core_cover_moves']),
                  'cover exchanges;', len(g['moves']), 'B pentagons', flush=True)
    (HERE/'ten_cycle_completion.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Saved all 18 length-ten patterns and eight full cubic completions.')


if __name__ == '__main__':
    main()
