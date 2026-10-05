#!/usr/bin/env python3
"""Fixed-layer completion for any number of selected cycles through length nine.

Standard-library finite classification, protected cover exchanges, and full
cubic graph certificates. See the independent verifier and accompanying proof.
"""
from collections import Counter
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from eight_cycle_completion import (AUX, digest, example_seed, hamiltonian_words,
                                   marked_test, matchings, prefixes)
from fourflow_quotient_repair import build, contracted, quotient_flow
from joint_boundary_completion import PAIRS, joint_repair, load_covers, masks_and_flows, word
from short_cycle_boundary import local_table, quotient_assignment

HERE = Path(__file__).parent
KINDS = ('all_marked', 'unmarked_even', 'unmarked_odd')
SPECS = {
    'eight': ([6, 10, 6, 18]*2, [15]*8, (0, 2)),
    'all_marked': ([6, 6, 10, 6, 18, 6, 10, 6, 20], [15]*9, (1, 3)),
    'unmarked_even': ([6, 6, 10, 6, 18, 6, 10, 6, 20], [0]+[15]*7+[0], (1, 3)),
    'unmarked_odd': ([3, 6, 10, 6, 18, 6, 10, 6, 17], [14]+[15]*7+[11], (1, 3)),
}


def rejected(rs, marked):
    pref = prefixes(rs)
    return len({pref[i] for i in marked}) == 8


@lru_cache(None)
def pairing_spans(active):
    result = []
    for matching in matchings(list(active)):
        span = [0]
        for i, j in matching:
            span += [s ^ (1 << i) ^ (1 << j) for s in span]
        result.append((tuple(matching), tuple(sorted(span))))
    return result


def matching_count(active, safe_pairs):
    adjacency = {i: sum(1 << j for j in active if i != j and tuple(sorted((i, j))) in safe_pairs) for i in active}
    @lru_cache(None)
    def count(mask):
        if not mask:
            return 1
        i = (mask & -mask).bit_length()-1
        return sum(count(mask ^ (1 << i) ^ (1 << j))
                   for j in active if mask >> j & 1 and adjacency[i] >> j & 1)
    return count(sum(1 << i for i in active))


@lru_cache(None)
def protected_pairing(rs, t, marked):
    assert not rejected(rs, marked)
    active = tuple(i for i, r in enumerate(rs) if (r & t).bit_count() == 1)
    for matching, span in pairing_spans(active):
        if all(not rejected([r ^ t if s >> i & 1 else r for i, r in enumerate(rs)], marked) for s in span):
            return matching
    raise AssertionError('No protected matching')


def choose_exchange(rs, marked):
    options = []
    for t in AUX:
        active = tuple(i for i, r in enumerate(rs) if (r & t).bit_count() == 1)
        safe = {ij for ij in itertools.combinations(active, 2)
                if rejected([r ^ t if i in ij else r for i, r in enumerate(rs)], marked)}
        if not matching_count(active, safe):
            options.append((len(safe), -len(active), t))
    return min(options)[2]


def bad_words():
    result = {k: [] for k in KINDS}
    for first in itertools.product(AUX, repeat=8):
        at, pref = 0, [0]
        for r in first:
            at ^= r
            pref.append(at)
        if at not in AUX or len(set(pref)) != 8:
            continue
        rs = first+(at,)
        result['all_marked'].append(rs)
        if len(set(pref[1:])) == 8:
            result['unmarked_even'].append(rs)
    # Subdivide the closing edge of an eight-state Hamiltonian word by two
    # distinguished-label pairs. The unmarked cut is between those new ports.
    for rs in hamiltonian_words():
        for bit in (2, 4, 8, 16):
            if rs[-1] & bit:
                result['unmarked_odd'].append((1 | bit,)+rs[:-1]+(1 | (rs[-1] ^ bit),))
    return {k: sorted(v) for k, v in result.items()}


def closed_count(kind):
    counts = {0: 1}
    for i in range(9):
        following = Counter()
        alphabet = PAIRS[:4] if kind == 'unmarked_odd' and i in (0, 8) else AUX
        for at, n in counts.items():
            for r in alphabet:
                following[at ^ r] += n
        counts = following
    return counts[0]


def normalize_pair(r, t):
    order = [i for i in range(1, 5) if t >> i & 1]+[i for i in range(1, 5) if not (t >> i & 1)]
    return (r & 1) | sum(1 << (j+1) for j, old in enumerate(order) if r >> old & 1)


def local_audit(words):
    result = {}
    for kind, bads in words.items():
        groups, marked = {}, tuple(range(9) if kind == 'all_marked' else range(1, 9))
        for rs in bads:
            active = tuple(i for i, r in enumerate(rs) if (r & 6).bit_count() == 1)
            key = tuple(min(r, r ^ 6) if i in active else r for i, r in enumerate(rs))
            bits = sum(1 << i for i, r in enumerate(rs) if r != key[i])
            groups.setdefault((key, active), set()).add(bits)
        rows, hist, fixed_counts, states = [], Counter(), {}, 0
        for (key, active), bad_bits in sorted(groups.items()):
            mask, base = sum(1 << i for i in active), min(bad_bits)
            for bits in range(512):
                if bits & ~mask or (bits ^ base).bit_count() % 2:
                    continue
                states += 1
                rs = tuple(r ^ 6 if bits >> i & 1 else r for i, r in enumerate(key))
                if bits in bad_bits:
                    safe = {ij for ij in itertools.combinations(active, 2)
                            if bits ^ (1 << ij[0]) ^ (1 << ij[1]) in bad_bits}
                    fixed_counts[rs] = matching_count(active, safe)
                    continue
                safe = [m for m, span in pairing_spans(active) if all(bits ^ s not in bad_bits for s in span)]
                assert safe
                hist[len(safe)] += 1
                rows.append([list(rs), len(safe), [list(ij) for ij in safe[0]]])
        forcing_hist = Counter()
        for rs in bads:
            n = sum(fixed_counts[tuple(normalize_pair(r, t) for r in rs)] == 0 for t in AUX)
            assert n
            forcing_hist[n] += 1
        total = closed_count(kind)
        result[kind] = {'marked_cuts': list(marked), 'closed_words': total, 'bad_words': len(bads),
                        'bad_words_sha256': digest([list(rs) for rs in bads]),
                        'threat_groups': len(groups), 'states_in_threat_groups': states,
                        'good_states_checked': len(rows), 'automatically_safe_good_states': total-states,
                        'protected_pairing_count_histogram': sorted(hist.items()),
                        'protection_sha256': digest(sorted(rows)),
                        'fixed_pair_nonescaping_matching_histogram': sorted(Counter(fixed_counts.values()).items()),
                        'forcing_pair_histogram': sorted(forcing_hist.items()),
                        'escape_sha256': digest([[list(rs), fixed_counts[rs]] for rs in bads])}
        print(kind, len(bads), 'bad cases;', len(rows), 'protected good cases; both lemmas passed.', flush=True)
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
        critical = len(marked) >= 8
        assert not critical or len(cycle) in (8, 9)
        assert critical or len(marked) <= 7
        records.append({'hub': core['vertex_map'][cycle[0]], 'incidences': hs,
                        'marked_cuts': marked, 'critical': critical,
                        'junction_indices': list(range(offset, offset+len(cycle)))})
        offset += len(cycle)
    return records


def bad_regions(regions, pairs):
    return [i for i, r in enumerate(regions) if r['critical'] and
            rejected([pairs[h//2] for h in r['incidences']], r['marked_cuts'])]


def repair_core(core, regions, original):
    pairs, moves = original.copy(), []
    endpoints = [v for uv in core['edges'] for v in uv]
    at_vertex = [[] for _ in range(core['vertices'])]
    for h, v in enumerate(endpoints):
        at_vertex[v].append(h)
    while before := bad_regions(regions, pairs):
        target = before[0]
        rec = regions[target]
        hub, hs = rec['hub'], rec['incidences']
        rs = [pairs[h//2] for h in hs]
        t = choose_exchange(rs, rec['marked_cuts'])
        protected, mate = [], {}
        for i, region in enumerate(regions):
            if not region['critical'] or i in before:
                continue
            ws = tuple(pairs[h//2] for h in region['incidences'])
            matching = protected_pairing(ws, t, tuple(region['marked_cuts']))
            protected.append({'region': i, 'pairs': [list(ij) for ij in matching]})
            for a, b in matching:
                u, v = region['incidences'][a], region['incidences'][b]
                mate[u], mate[v] = v, u
        for v in range(core['vertices']):
            if v == hub:
                continue
            at = [h for h in at_vertex[v] if (pairs[h//2] & t).bit_count() == 1]
            assert len(at) % 2 == 0
            if at and at[0] in mate:
                assert all(h in mate for h in at)
                continue
            for a, b in zip(at[::2], at[1::2]):
                mate[a], mate[b] = b, a
        terminals = {h: i for i, h in enumerate(hs) if (pairs[h//2] & t).bit_count() == 1}
        consumed, chosen = set(), None
        for start in sorted(terminals):
            if start in consumed:
                continue
            h, path = start, []
            while True:
                path.append(h)
                h ^= 1
                if h in terminals:
                    break
                h = mate[h]
                assert len(path) <= len(pairs)
            consumed.update((start, h))
            i, j = terminals[start], terminals[h]
            changed = rs.copy()
            changed[i] ^= t
            changed[j] ^= t
            if not rejected(changed, rec['marked_cuts']):
                chosen = (path, [i, j])
                break
        assert chosen is not None
        path, ports = chosen
        es = [h//2 for h in path]
        assert len(es) == len(set(es))
        for e in es:
            pairs[e] ^= t
        after = bad_regions(regions, pairs)
        assert set(after) < set(before) and target not in after
        moves.append({'target_region': target, 'swap_pair': t, 'trail_incidences': path,
                      'ports': ports, 'protected_pairings': protected,
                      'bad_before': before, 'bad_after': after,
                      'cover_word_after': word(PAIRS.index(a) for a in pairs)})
    return pairs, moves


def seed(kind, profiles, table, fibers, protect_example=False):
    cycles, zs, entries, n = [], [], {}, 0
    for cell, profile in enumerate(profiles):
        rs, bits, connectors = SPECS[profile]
        k = len(rs)
        cs = [list(range(n, n+k)), list(range(n+k, n+2*k))]
        cycles.extend(cs)
        zs.extend(bits*2)
        four = [1]*k if k == 8 else [1]*7+[2, 3]
        second_positions = list(range(k))
        if protect_example:
            assert len(profiles) == 1 and profile == 'unmarked_odd'
            second_positions[6], second_positions[7] = 7, 6
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
    # Keep a non-F edge first, for the optional Petersen two-edge sum.
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
    old = seed(kind, profiles, table, fibers, name == 'protected_distinguished_region')
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
    if name == 'protected_distinguished_region':
        es = [g['junctions'][i]['edges'][-1] for i in (6, 7)]
        naive = [r ^ 12 if e in es else r for e, r in enumerate(original)]
        assert bad_regions(regions, original) == [0] and bad_regions(regions, naive) == [1]
        g['unprotected_exchange'] = {'swap_pair': 12, 'edges': es, 'bad_before': [0], 'bad_after': [1],
                                     'cover_word_after': word(PAIRS.index(a) for a in naive)}
    return g



def main():
    domains, witnesses = load_covers()
    _, fibers = masks_and_flows()
    pet = json.loads((HERE / 'triangle_quotient_reduction.json').read_text())['petersen']
    result = {'date': '2026-10-05',
              'scope': 'Prescribed-layer completion reduces exactly to the core for any number of selected cycles of lengths three through nine. Additional regions of arbitrary length are allowed if they have at most seven marked cuts. No result for obstructed longer regions or general 5-CDC proof is claimed.',
              'sources': [{'file': name, 'sha256': hashlib.sha256((HERE / name).read_bytes()).hexdigest()}
                          for name in ('simultaneous_eight_completion.json', 'triangle_quotient_reduction.json',
                                       'petersen_boundary_relation.txt.gz')],
              'local_cases': local_audit(bad_words()), 'examples': []}
    for kind in ('blowup', 'semi'):
        table, _ = local_table(kind)
        for name, profiles, attached in [(k, [k], None) for k in KINDS]+[
                ('protected_distinguished_region', ['unmarked_odd'], None),
                ('mixed_eight_nine_no_four_flow', ['eight', *KINDS], pet)]:
            g = full_example(kind, name, profiles, attached, table, fibers, domains, witnesses)
            result['examples'].append(g)
            print(kind, name, g['vertices'], 'vertices;', len(g['core_cover_moves']),
                  'cover exchanges;', len(g['moves']), 'B pentagons', flush=True)
    (HERE / 'nine_cycle_completion.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Saved all three nine-cycle cases and ten full cubic completions.')


if __name__ == '__main__':
    main()
