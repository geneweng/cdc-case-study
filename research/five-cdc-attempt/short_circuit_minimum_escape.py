#!/usr/bin/env python3
"""Certify short-circuit escape and every minimum matching on ThreeY1Hexagon138."""
from collections import Counter
from itertools import product
from math import prod
import hashlib
import json
from pathlib import Path

from minimum_color_obstruction import Graph
from minimum_matching_secondary import Constraints, encode, pair
from neutral_minimum_quotient import mask, intersection_builder, cover, cycle_lower_bounds
from prepared_minimum_exchange import source_cycles, rank_basis

HERE = Path(__file__).resolve().parent
SOURCES = [
    ('secondary_minimum_obstruction.json', 'f722b31c3247ef29ad9a7214574a0283dfed1a877c4cc93ea07be75e2b1c87b5'),
    ('minimum_matching_secondary.json', '32082a951b4c3012b9f8a312e46b5b117490a899e3a3299a35b6f5dc344975ec'),
    ('neutral_minimum_quotient.json', 'cd19d33ccb19649d6f39b5daf8d7b74d76317f9f2c328d9eb059c27e083ed754')]
MATCHING = [178, 183, 189]
CIRCUIT = [142, 146, 148, 189, 190, 194]
PATH = [142, 146, 148, 190, 194]
# Discovery witnesses: the two binary supports of each projected flow.
PROJECTED_WITNESSES = [
    (48150844568910032950013896915775578131149165756201416621247987, 166781722253374150504140191707362287711765940704507100464395982),
    (192693592669873169336195418763321209774875190862366393165106675, 22238974152411014117958669859816656068039915598342123920537294),
    (166781722261493286782973378495914332593901060048747929169294646, 93598633573318408294117414966560895489493223581015562144030457),
    (150994189012244250502813799753366756957357890987134057444122355, 93598633573318408294117414966560895489493311203076291752782653),
    (93598633574185224977139606882820048104599586637103654481163574, 166781722253377421978859325708216774655068461635082492134137593),
    (196441978017519442528894510502465869555510885832721263339762998, 22238974152414285592677816156030104021814348511167173303836409),
]


def census(source, catalog):
    groups = catalog['local_edge_groups']
    maps = [list(range(59*i, 59*(i+1))) + list(range(177+5*i, 182+5*i)) for i in range(3)]
    solver = Constraints(18, source['graph']['quotient_edges'])
    positive, invalid, negative = [], [], []
    type_counts, weights = Counter(), Counter()
    for kinds in product(range(11), repeat=3):
        code = encode(kinds, 11)
        K = [maps[i][groups[t][0]] for i, t in enumerate(kinds)]
        multiplicity = prod(len(groups[t]) for t in kinds)
        counts = Counter(v for e in K for v in source['graph']['edges'][e])
        collisions = [v for v, count in counts.items() if count > 1]
        if collisions:
            assert all(v >= 123 for v in collisions)
            invalid.append([code, min(collisions)])
            status = 'not_matching'
        else:
            domains = [7] * 30
            for i, t in enumerate(kinds):
                if 1 <= t <= 5:
                    domains[5*i+t-1] = 6
                elif t >= 6:
                    domains[5*i+t-6] = 8
            values = solver.solve(domains)
            if values is None:
                assert K == MATCHING and multiplicity == 1
                negative.append([code, K])
                status = 'unsuitable'
            else:
                positive.append([code, *pair(values)])
                status = 'suitable'
        type_counts[status] += 1
        weights[status] += multiplicity
    assert type_counts == {'suitable': 1286, 'not_matching': 44, 'unsuitable': 1}
    assert weights == {'suitable': 261887, 'not_matching': 256, 'unsuitable': 1}
    return {'local_to_global': maps, 'reduced_edges': source['graph']['quotient_edges'],
            'outer_witnesses': sorted(positive), 'invalid_types': sorted(invalid),
            'unsuitable_types': negative, 'type_counts': dict(sorted(type_counts.items())),
            'weighted_counts': dict(sorted(weights.items()))}


def choose_escape(flow):
    assert [e for e, x in enumerate(flow) if x == 4] == MATCHING
    projected = [flow[e] & 3 for e in PATH]
    assert set(projected) == {1, 2, 3}
    singletons = [e for e, x in zip(PATH, projected) if projected.count(x) == 1]
    assert singletons and 194 not in singletons
    new = singletons[0]
    return {'increment': 4 ^ flow[new], 'edges': CIRCUIT,
            'matching_after': sorted([178, 183, new])}


def finite_words():
    general = []
    decreasing, total = 0, 0
    for length in range(2, 7):
        counts = Counter()
        for values in product([1, 2, 3, 5, 6, 7], repeat=length-1):
            total += 1
            projected = [x & 3 for x in values]
            if set(projected) != {1, 2, 3}:
                missing = next(p for p in (1, 2, 3) if p not in projected)
                assert missing not in (4,) + values
                assert all((x ^ missing) != 4 for x in (4,) + values)
                decreasing += 1
                continue
            singletons = [i for i, x in enumerate(projected) if projected.count(x) == 1]
            assert singletons
            for i in singletons:
                b = 4 ^ values[i]
                assert b not in (4,) + values
                assert sum((x ^ b) == 4 for x in (4,) + values) == 1
            counts[len(singletons)] += 1
        if length >= 4:
            general.append({'circuit_length': length, 'cases': sum(counts.values()),
                            'singleton_counts': [[k, count] for k, count in sorted(counts.items())]})
    projected_words, branches = [], Counter()
    for word in product(range(1, 4), repeat=5):
        if set(word) != {1, 2, 3} or any(x == y for x, y in zip(word, word[1:])):
            continue
        singletons = [i for i, x in enumerate(word) if word.count(x) == 1]
        if 4 in singletons:
            continue
        projected_words.append(word)
        branches[PATH[singletons[0]]] += 32
    normalized = [list(word) for word in projected_words if word[:2] == (1, 2)]
    return {'general_audit': general, 'total_word_cases': total, 'decreasing_word_cases': decreasing,
            'normalized_projection_words': normalized,
            'projection_word_count': len(projected_words),
            'full_word_count': 32*len(projected_words),
            'chosen_target_counts': [[e, count] for e, count in sorted(branches.items())]}


def main():
    for name, sha in SOURCES:
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == sha
    source, catalog, previous = [json.loads((HERE / name).read_text()) for name, _ in SOURCES]
    obj = Graph(source['graph'])
    classification = census(source, catalog)
    words = finite_words()
    builder = intersection_builder(source, catalog, obj)
    targets = {e: builder(sorted([178, 183, e])) for e in [142, 146, 148, 190]}
    high = obj.support(source['initial_flow'], 4)
    examples = []
    for y, z in PROJECTED_WITNESSES:
        flow = [((y >> e) & 1) + 2*((z >> e) & 1) + 4*((high >> e) & 1) for e in range(obj.m)]
        assert obj.valid_flow(flow)
        first = choose_escape(flow)
        new = next(e for e in first['matching_after'] if e not in MATCHING)
        repair = cover(obj, flow, first, targets[new])
        examples.append({'projected_coordinates': [y, z], 'flow': flow,
                         'projection_word': [flow[e] & 3 for e in PATH],
                         'added_matching_edge': new, 'repair': repair})
    assert [r['projection_word'] for r in examples] == words['normalized_projection_words']
    assert len(examples) == 6 and {r['added_matching_edge'] for r in examples} == set(targets)
    cycles = source_cycles(obj, MATCHING)
    assert len(cycles) == 67
    assert len(rank_basis(C & mask(PATH) for C in cycles)) == 5
    result = {'date': '2026-10-06',
              'scope': 'Every globally minimizing marked flow on ThreeY1Hexagon138 reaches a suitable minimum matching and a five-layer cover; no restriction on its projection.',
              'sources': [{'file': name, 'sha256': sha} for name, sha in SOURCES],
              'minimum_size': 3, 'classification': classification,
              'unique_unsuitable_matching': MATCHING,
              'forced_obstruction_circuit': source['obstruction']['forced_circuit_edges'],
              'escape_circuit': CIRCUIT, 'escape_path_order': PATH,
              'matching_edge_cycle_lower_bounds': cycle_lower_bounds(obj, MATCHING),
              'escape_targets': [{'added_edge': e, 'matching': sorted([178, 183, e]),
                                  'first': F, 'partner': t} for e, (F, t) in targets.items()],
              'local_words': words, 'source_fiber_dimension': 67,
              'path_restriction_rank': 5, 'examples': examples,
              'maximum_matching_escape_switches': 1, 'maximum_cover_fiber_rounds': 2,
              'maximum_cover_circuit_switches': 1 + obj.n//5}
    assert result['matching_edge_cycle_lower_bounds'] == previous['matching_edge_cycle_lower_bounds']
    path = HERE / 'short_circuit_minimum_escape.json'
    path.write_text(json.dumps(result, indent=2)+'\n')
    print('Type counts:', classification['type_counts'])
    print('Weighted counts:', classification['weighted_counts'])
    print('General short-circuit cases:', sum(r['cases'] for r in words['general_audit']))
    print('All local projection/full words:', words['projection_word_count'], words['full_word_count'])
    print('Repair lengths:', [[len(move['edges']) for move in r['repair']['moves']] for r in examples])
    print('Bytes:', path.stat().st_size, 'SHA256:', hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
