#!/usr/bin/env python3
"""Certify minimum-color failure without any Petersen four-pole.

The discovery witnesses are fixed; reproduction uses only the standard library.
"""
from collections import Counter, deque
import hashlib
import json
from pathlib import Path

from minimum_color_obstruction import Graph, SPOKES, digest
from flow_space_components import cycle_basis, circuit_components, supports

HERE = Path(__file__).resolve().parent
FLOWER = [(0, 1), (0, 2), (0, 3), (4, 5), (4, 6), (4, 7), (8, 9), (8, 10), (8, 11), (12, 13), (12, 14), (12, 15), (16, 17), (16, 18), (16, 19), (1, 5), (5, 9), (9, 13), (13, 17), (17, 1), (2, 6), (3, 7), (6, 10), (7, 11), (10, 14), (11, 15), (14, 18), (15, 19), (18, 3), (19, 2)]
INTERNAL = [uv for uv in FLOWER if all(v not in (0,1) for v in uv)]
PORTS = (2,3,5,17)
INITIAL = [3, 4, 7, 1, 6, 7, 7, 2, 2, 7, 5, 6, 7, 1, 1, 3, 2, 5, 2, 7, 3, 2, 1, 3, 2, 7, 5, 2, 2, 3, 1, 1, 3, 6, 1, 7, 3, 2, 1, 7, 1, 6, 3, 1, 2, 7, 6, 1, 6, 1, 2, 5, 2, 7, 3, 6, 5, 7, 7, 1, 6, 1, 2, 3, 2, 4, 6, 6, 7, 1, 2, 1, 3, 7, 5, 3, 7, 6, 5, 5, 1, 3, 6, 2, 7, 1, 2, 1, 3, 6, 1, 7, 2, 5, 7, 6, 5, 3, 1, 7, 5, 3, 5, 2, 6, 3, 1, 6, 6, 3, 5, 1, 7, 6, 7, 1, 6, 6, 5, 3, 2, 1, 3, 2, 5, 3, 5, 1, 2, 7, 3, 1, 6, 2, 7, 1, 1, 2, 5, 4, 2, 3, 7, 6, 5, 5, 3, 3, 5, 2, 6, 1, 6, 1, 5, 2, 3, 3, 6, 6, 5, 7, 3, 1, 4, 6, 6, 1, 7, 6, 5, 3, 2, 5, 7, 6, 1, 7, 1, 7, 5, 7, 5, 6, 2, 3, 1, 6, 6, 7, 1, 2, 5, 7, 2, 1, 3, 3, 2, 1, 1, 6, 7, 7, 5, 6, 3, 6, 6, 1, 7, 2, 5, 3, 3, 4, 5, 3, 6, 2, 3, 1, 2, 3, 1, 5, 3, 6, 3, 1, 3, 6, 1, 5, 7, 6, 6, 5, 7, 6, 1, 4, 1, 5, 7, 2, 5, 2, 7, 5, 6, 7, 1, 6, 1, 3, 6, 3, 7, 6, 5, 3, 2, 6, 5, 7, 1, 7, 6, 5, 6, 3, 1, 2, 3, 5, 7, 2, 2, 7, 6, 2, 3, 5, 5, 3, 6, 1, 5, 6, 7, 2, 6, 7, 3, 6, 2, 3, 5, 5, 7, 7, 5, 1, 3, 6, 6, 7, 7, 5, 2, 2, 5, 1, 6, 2, 5, 3, 3, 5, 5]
FIRST_CIRCUIT = [112, 113, 126, 127, 136, 137, 164, 165]
INTERSECTION = (1643258275432148292561964872197835609892432459910502613139562947052031564027383357574672025485339, 2469735018248495334227969771927559860596605998963915947737130544006360886063678178021798624369414)


def graph():
    edges = list(SPOKES)+[(12,13)]
    next_vertex = 14
    regions = []
    for region in range(2):
        blocks = [{v:next_vertex+18*j+v-2 for v in range(2,20)} for j in range(5)]
        next_vertex += 90
        junctions = [(next_vertex+2*j,next_vertex+2*j+1) for j in range(5)]
        next_vertex += 10
        for b in blocks: edges += [(b[u],b[v]) for u,v in INTERNAL]
        for j,(u,w) in enumerate(junctions):
            nu,nw = junctions[(j+1)%5]; b = blocks[j]
            edges += [(5*region+j,u),(5*region+j,w),(u,b[5]),(w,b[17]),(b[2],nu),(b[3],nw)]
        regions.append({'base_vertices':list(range(5*region,5*region+5)),
                        'blocks':[{str(v):w for v,w in b.items()} for b in blocks],
                        'junctions':junctions})
    index = {tuple(sorted(edge)):e for e,edge in enumerate(edges)}
    for region in regions:
        block_edges = []
        for j,raw in enumerate(region['blocks']):
            b = {int(v):w for v,w in raw.items()}
            u,w = region['junctions'][j]; nu,nw = region['junctions'][(j+1)%5]
            local = [(b[x],b[y]) for x,y in INTERNAL]+[(b[2],nu),(b[3],nw),(b[5],u),(b[17],w)]
            block_edges.append([index[tuple(sorted(e))] for e in local])
        spokes = [next(e for e,uv in enumerate(SPOKES) if v in uv) for v in region['base_vertices']]
        constraints = [sorted(set(block_edges[j-1]+block_edges[j]+[spokes[j]])) for j in range(5)]
        region.update(block_edges=block_edges, spoke_edges=spokes, zero_hitting_sets=constraints,
                      charged_edges=sorted(set(e for row in constraints for e in row)), lower_bound=3)
    return {'name':'TwoFlowerPentagonBlowup214','vertices':next_vertex,'edges':edges,
            'base_edges':list(SPOKES)+[(12,13)]+[(off+j,off+(j+1)%5) for off in (0,5) for j in range(5)],
            'regions':regions,'flower_edges':FLOWER,'deleted_flower_vertices':[0,1],
            'fourpole_internal_edges':INTERNAL,'ports':PORTS}


def local_fourpole():
    # Identify the four outer ends at a hub. Their binary parity equation is
    # already implied by the eighteen internal vertex equations.
    edges = [(u-1,v-1) for u,v in INTERNAL]+[(v-1,0) for v in PORTS]
    binary = supports(cycle_basis(19,edges))
    rows, boundary = [], Counter()
    full = (1 << len(edges))-1
    for y in binary:
        for z in binary:
            if y | z != full: continue
            values = [((y >> e)&1)+2*((z >> e)&1) for e in range(len(edges))]
            assert values[25] == values[26] and values[27] == values[28]
            rows.append(values); boundary[tuple(values[25:])] += 1
    return {'binary_flows':len(binary),'nowhere_zero_two_bit_flows':len(rows),
            'records_sha256':digest(sorted(rows)),
            'boundary_histogram':[list(k)+[v] for k,v in sorted(boundary.items())]}


def girth_certificate(obj):
    best = None
    for excluded,(start,end) in enumerate(obj.edges):
        parent = {start:(-1,-1)}; queue = deque([start])
        while queue and end not in parent:
            v = queue.popleft()
            for e in obj.incident[v]:
                if e == excluded: continue
                u,w = obj.edges[e]; w ^= u ^ v
                if w not in parent:
                    parent[w] = (v,e); queue.append(w)
        assert end in parent
        path = [excluded]; v = end
        while v != start:
            v,e = parent[v]; path.append(e)
        row = sorted(path)
        if best is None or (len(row),row) < (len(best),best): best = row
    assert len(best) == 6
    return {'girth':len(best),'shortest_circuit_edges':best,
            'petersen_four_poles':0,'exclusion_reason':'A Petersen four-pole contains a pentagon.'}


def connectivity(obj):
    basis = cycle_basis(obj.n,obj.edges)
    columns = [sum(((C >> e)&1) << i for i,C in enumerate(basis)) for e in range(obj.m)]
    assert all(columns) and len(set(columns)) == obj.m
    index = {col:e for e,col in enumerate(columns)}
    triples = [[i,j,index[columns[i] ^ columns[j]]] for i in range(obj.m) for j in range(i+1,obj.m)
               if columns[i] ^ columns[j] in index and index[columns[i] ^ columns[j]] > j]
    assert sorted(triples) == sorted([sorted(es) for es in obj.incident])
    block = sum(1 << v for v in range(14,32))
    boundary = obj.cut(block); assert boundary.bit_count() == 4
    assert len(obj.components(obj.full ^ boundary)) == 2
    return {'cycle_dimension':len(basis),'distinct_nonzero_columns':len(columns),
            'three_edge_cuts':len(triples),'three_cut_records_sha256':digest(sorted(triples)),
            'four_cut_side':block,'four_cut_edges':boundary,'cyclic_edge_connectivity':4}


def repair(obj):
    first = obj.switch(INITIAL,3,FIRST_CIRCUIT)
    F,t = INTERSECTION; ell = 4
    before = first['flow_after']
    M = sum((x == 4) << e for e,x in enumerate(before))
    assert obj.even(F) and obj.even(t) and F & t == M and M.bit_count() == 6
    difference = F ^ obj.support(before,ell)
    circuits = circuit_components(difference,obj.n,obj.edges)
    assert len(circuits) == 1 and len(circuits[0]) == 155
    second = obj.switch(before,4,circuits[0]); final = second['flow_after']
    assert obj.support(final,ell) == F
    y,z = obj.support(final,1),obj.support(final,2)
    fourth = t ^ y ^ z
    forms = [2,1,ell]
    transformed = [sum(((x & normal).bit_count()%2) << i for i,normal in enumerate(forms)) for x in final]
    palette = (4,5,6,15,8)
    decode = {x ^ y:(1 << i)|(1 << j) for i,x in enumerate(palette) for j,y in enumerate(palette) if i < j}
    cover = [decode[x+8*((fourth >> e)&1)] for e,x in enumerate(transformed)]
    assert obj.even(fourth)
    assert all(cover[a] ^ cover[b] ^ cover[c] == 0 for a,b,c in obj.incident)
    assert all(min(move['color_sizes']) == move['color_sizes'][3] == 6 for move in (first,second))
    return {'moves':[first,second],'intersection_first':F,'intersection_partner':t,
            'first_functional':ell,'target_color':4,
            'final_lift':{'coordinate_functionals':forms,'transformed_flow':transformed,
                          'fourth_coordinate':fourth,'cover_pairs':cover}}


def main():
    g = graph(); obj = Graph(g)
    assert obj.valid_flow(INITIAL)
    charged = [set(r['charged_edges']) for r in g['regions']]
    assert charged[0].isdisjoint(charged[1])
    for region in g['regions']:
        counts = Counter(e for row in region['zero_hitting_sets'] for e in row)
        assert max(counts.values()) == 2 and len(region['zero_hitting_sets']) == 5
        assert sum(INITIAL[e] == 4 for e in region['charged_edges']) == 3
    sources = ['minimum_color_obstruction.json','flow_space_components.json']
    result = {'date':'2026-10-06',
              'scope':'Global minimum color multiplicity does not force a suitable matching or successful incident fiber, even with girth six and no Petersen four-pole.',
              'sources':[{'file':name,'sha256':hashlib.sha256((HERE/name).read_bytes()).hexdigest()} for name in sources],
              'graph':g,'local_fourpole_audit':local_fourpole(),'connectivity':connectivity(obj),
              'girth_certificate':girth_certificate(obj),
              'minimum_color_multiplicity':6,'initial_flow':INITIAL,
              'initial_color_sizes':[INITIAL.count(a) for a in range(1,8)],
              'matching_failures':[obj.matching_failure(INITIAL,a) for a in range(1,8)],
              'failed_flags':obj.failed_flags(INITIAL),'repair':repair(obj)}
    destination = HERE/'petersen_free_minimum_obstruction.json'
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print('Local flower four-pole:',result['local_fourpole_audit'])
    print('Connectivity:',result['connectivity'])
    print('Girth:',result['girth_certificate'])
    print('Minimum: 6; initial color sizes:',result['initial_color_sizes'])
    print('Odd unmatched components:',[r['component_vertices'] for r in result['matching_failures']])
    print('Repair lengths:',[len(r['edges']) for r in result['repair']['moves']])
    print('Certificate bytes:',destination.stat().st_size,'SHA256:',hashlib.sha256(destination.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
