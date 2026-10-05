#!/usr/bin/env python3
"""Construct complete coordinate-fiber component certificates on saved cores.

C++ enumerates full-support subspaces. This driver supplies graph data and
actual flow/cover witnesses. Standard library plus a C++17 compiler.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
SOURCES = ('snark_repair_results.json', 'native_repair_results.json')


def cycle_basis(n, edges):
    adjacency = [[] for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        adjacency[u].append((v,e)); adjacency[v].append((u,e))
    parent, queue, tree = {0: (-1,-1)}, [0], set()
    for v in queue:
        for w, e in adjacency[v]:
            if w not in parent:
                parent[w] = (v,e); tree.add(e); queue.append(w)
    assert len(parent) == n
    def path(v):
        mask = 0
        while v:
            v, e = parent[v]; mask ^= 1 << e
        return mask
    return [path(u) ^ path(v) ^ (1 << e) for e, (u,v) in enumerate(edges) if e not in tree]


def supports(basis):
    out = [0]
    for b in basis:
        out += [s ^ b for s in out]
    return out


def unpack(key, dimension=3):
    return tuple(key >> (16*i) & 65535 for i in range(dimension))


def span(rows):
    out = [0]
    for row in rows:
        out += [v ^ row for v in out]
    return sorted(out)


def key(rows):
    points = span(rows)
    return sum(points[1 << i] << (16*i) for i in range(len(rows)))


def values(rows, cycles, m):
    return [sum(((cycles[row] >> e) & 1) << i for i, row in enumerate(rows)) for e in range(m)]


def solve(equations, variables):
    pivots = {}
    for row, rhs in equations:
        for p in sorted(pivots, reverse=True):
            if row >> p & 1:
                other, value = pivots[p]; row ^= other; rhs ^= value
        if not row:
            if rhs: return None
            continue
        pivots[row.bit_length()-1] = (row,rhs)
    value = 0
    for p in sorted(pivots):
        row, rhs = pivots[p]
        if (row & value).bit_count() % 2 != rhs: value |= 1 << p
    assert value < 1 << variables
    return value


def lift(flow, basis):
    r, m = len(basis), len(flow)
    edge_rows = [sum(((b >> e) & 1) << i for i,b in enumerate(basis)) for e in range(m)]
    palette = (4,5,6,15,8)
    decode = {a ^ b: (1 << i) | (1 << j) for i,a in enumerate(palette) for j,b in enumerate(palette) if i < j}
    for first in range(1,8):
        second = next(x for x in range(1,8) if x != first)
        third = next(x for x in range(1,8) if x not in (first,second,first ^ second))
        transformed = [4*((x & first).bit_count() % 2)+2*((x & second).bit_count() % 2)+(x & third).bit_count() % 2 for x in flow]
        extra = solve([(edge_rows[e],int(x != 7)) for e,x in enumerate(transformed) if x >= 4],r)
        if extra is None: continue
        extra_mask = 0
        for i,b in enumerate(basis):
            if extra >> i & 1: extra_mask ^= b
        cover = [decode[x ^ (8*((extra_mask >> e) & 1))] for e,x in enumerate(transformed)]
        return {'flow': flow, 'coordinate_functionals': [third,second,first], 'transformed_flow': transformed,
                'fourth_coordinate_mask': extra_mask, 'cover_pairs': cover}
    raise AssertionError('No five-label lift')


def circuit_components(mask, n, edges):
    pending = {e for e in range(len(edges)) if mask >> e & 1}
    result = []
    while pending:
        todo = [min(pending)]; pending.remove(todo[0])
        vertices = set(edges[todo[0]])
        for e in todo:
            for f in sorted(pending.copy()):
                if vertices & set(edges[f]):
                    vertices.update(edges[f]); todo.append(f); pending.remove(f)
        result.append(sorted(todo))
    return result


def fiber_witness(initial, distances, cycles, n, edges, basis):
    rows, current = unpack(initial), initial
    moves, rounds = [], []
    while distances[current]:
        points = span(rows)[1:]
        found = None
        for a,b in itertools.combinations(points,2):
            if a ^ b < b: continue
            uncovered = ((1 << len(edges))-1) & ~(cycles[a] | cycles[b])
            for z, support in enumerate(cycles):
                if support & uncovered != uncovered or z > min(z ^ a,z ^ b,z ^ a ^ b): continue
                nxt = key((a,b,z))
                if distances[nxt] == distances[current]-1:
                    found = (a,b,z,nxt); break
            if found: break
        assert found
        a,b,z,nxt = found
        coordinates = {0: 0}
        for code in range(1,8):
            x = 0
            for i,row in enumerate(rows):
                if code >> i & 1: x ^= row
            coordinates[x] = code
        left, right = coordinates[a], coordinates[b]
        increment = next(t for t in range(1,8) if (left & t).bit_count() % 2 == (right & t).bit_count() % 2 == 0)
        last = next(t for t in range(1,8) if t not in (left,right,left ^ right))
        old_z = 0
        for i,row in enumerate(rows):
            if last >> i & 1: old_z ^= row
        difference = cycles[old_z ^ z]
        before = len(moves)
        for circuit in circuit_components(difference,n,edges):
            mask = sum(1 << e for e in circuit)
            code = cycles.index(mask)
            flow = values(rows,cycles,len(edges))
            assert all(flow[e] != increment for e in circuit)
            rows = tuple(row ^ code if increment >> i & 1 else row for i,row in enumerate(rows))
            moves.append({'round':len(rounds)+1,'increment':increment,'edges':circuit,'flow_after':values(rows,cycles,len(edges))})
        assert key(rows) == nxt
        rounds.append({'fixed_cycles':[a,b],'target_space':nxt,'circuits':len(moves)-before})
        current = nxt
    return {'initial_space':initial,'initial_flow':values(unpack(initial),cycles,len(edges)),
            'rounds':rounds,'moves':moves,'final_lift':lift(values(rows,cycles,len(edges)),basis)}


def petersen_piece_count(n, edges):
    pattern_edges = [(0,1),(1,2),(0,5),(1,6),(2,7),(3,5),(4,6),(5,7),(6,3),(7,4)]
    pattern = [set() for _ in range(8)]
    for u,v in pattern_edges: pattern[u].add(v); pattern[v].add(u)
    adj = [set() for _ in range(n)]; bits = [0]*n
    for u,v in edges: adj[u].add(v); adj[v].add(u); bits[u] |= 1 << v; bits[v] |= 1 << u
    order = sorted(range(8),key=lambda v:-len(pattern[v]))
    count = 0
    for subset in itertools.combinations(range(n),8):
        mask = sum(1 << v for v in subset)
        degrees = {v:(bits[v] & mask).bit_count() for v in subset}
        if sorted(degrees.values()) != [2]*4+[3]*4: continue
        mapping = {}
        def search(i):
            if i == 8: return True
            v = order[i]
            for w in subset:
                if w in mapping.values() or degrees[w] != len(pattern[v]): continue
                if any((u in pattern[v]) != (ww in adj[w]) for u,ww in mapping.items()): continue
                mapping[v] = w
                if search(i+1): return True
                del mapping[v]
            return False
        count += search(0)
    return count


def gaussian(n,k):
    numerator = denominator = 1
    for i in range(k): numerator *= (1 << n)-(1 << i); denominator *= (1 << k)-(1 << i)
    return numerator // denominator


def input_text(g):
    return '\n'.join([f"{g['vertices']} {len(g['edges'])} {len(g['cycle_basis'])} {g['flow_dimension']}"]+
                     [f'{u} {v}' for u,v in g['edges']]+list(map(str,g['cycle_basis'])))+'\n'


def main():
    compiler = shutil.which('c++') or shutil.which('g++')
    assert compiler, 'A C++17 compiler is required'
    graphs = [{'name':'K4','vertices':4,'edges':list(itertools.combinations(range(4),2)),'flow_dimension':2},
              {'name':'K3,3','vertices':6,'edges':[(u,v) for u in range(3) for v in range(3,6)],'flow_dimension':2},
              {'name':'Petersen','vertices':10,'edges':[(i,(i+1)%5) for i in range(5)]+[(i,i+5) for i in range(5)]+
               [(i+5,(i+2)%5+5) for i in range(5)],'flow_dimension':3}]
    for source in SOURCES:
        for i,old in enumerate(json.loads((HERE/source).read_text())['graphs']):
            graphs.append({'name':f"Snark{old['vertices']}_{i}",'vertices':old['vertices'],'edges':old['edges'],
                           'graph6':old['graph6'],'flow_dimension':3,'prior_source':source,
                           'prior_flow_classes':old['nz_orbits_by_rank']['3'],
                           'prior_successful_classes':old['nz_orbits_by_rank']['3']-old['bad_orbits_checked']})
    result = {'date':'2026-10-05','scope':'Exact flow components via coordinate fibers; one Petersen-piece-free 20-vertex core is the principal test.',
              'sources':[{'file':s,'sha256':hashlib.sha256((HERE/s).read_bytes()).hexdigest()} for s in SOURCES],
              'literature':{'url':'https://arxiv.org/html/2512.17342v4','checked':'2026-10-05','relevant_sections':['2.2','6.3']},'graphs':[]}
    with tempfile.TemporaryDirectory(prefix='cdc-flow-components-') as directory:
        binary, records = Path(directory)/'constructor', Path(directory)/'states.bin'
        subprocess.run([compiler,'-std=c++17','-O3','-Wall','-Wextra','-pedantic',str(HERE/'flow_space_components.cpp'),'-o',str(binary)],check=True)
        for g in graphs:
            g['cycle_basis'] = cycle_basis(g['vertices'],g['edges'])
            g['petersen_four_poles'] = petersen_piece_count(g['vertices'],g['edges'])
            census = json.loads(subprocess.check_output([str(binary),str(records)],input=input_text(g),text=True))
            assert census['subspaces_enumerated'] == gaussian(len(g['cycle_basis']),g['flow_dimension'])
            census['components'].sort(key=lambda c:c[2])
            data = records.read_bytes()
            census['state_records_sha256'] = hashlib.sha256(data).hexdigest()
            census['record_format'] = 'Sorted little-endian uint64 triples: space key, least component key, fiber distance + 1.'
            census['hard_spaces'] = [s for s,c,d in struct.iter_unpack('<QQQ',data) if d > 2]
            g['census'] = census
            cycles = supports(g['cycle_basis'])
            first_good = {}
            for state,component,dist in struct.iter_unpack('<QQQ',data):
                if dist == 1: first_good.setdefault(component,state)
            g['component_cover_witnesses'] = [dict(component_key=c,space_key=s,**lift(values(unpack(s,g['flow_dimension']),cycles,len(g['edges'])),g['cycle_basis']))
                                             for c,s in sorted(first_good.items())]
            if g['name'] == 'Snark20_0':
                assert g['petersen_four_poles'] == 0
                g['flower5_vertex_map'] = [2,3,1,16,15,14,13,8,6,7,5,19,0,18,17,12,10,11,4,9]
                g['cyclic_edge_connectivity'] = 5
                distances = {s:d-1 for s,c,d in struct.iter_unpack('<QQQ',data)}
                g['hard_flow_repair'] = fiber_witness(census['hard_spaces'][0],distances,cycles,g['vertices'],g['edges'],g['cycle_basis'])
                del distances
            if 'prior_flow_classes' in g:
                assert census['full_support_spaces'] == g['prior_flow_classes']
                assert sum(c[1] for c in census['components']) == g['prior_successful_classes']
            result['graphs'].append(g)
            print(g['name'],census['full_support_spaces'],'spaces;',len(census['components']),'components;',census['fiber_distance_histogram'],flush=True)
    (HERE/'flow_space_components.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    main()
