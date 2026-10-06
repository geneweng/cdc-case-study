#!/usr/bin/env python3
"""A globally minimizing, fully blocked flow with cyclic connectivity five.

Local five-poles follow Mattiolo--Negrini--Pagani, arXiv:2604.22501v1,
Section 3. The outer assembly and fixed flow/repair witnesses are supplied here.
Reproduction uses only Python's standard library.
"""
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path

from minimum_color_obstruction import Graph, digest
from flow_space_components import cycle_basis, circuit_components, supports

HERE = Path(__file__).resolve().parent
M = {'vertices':7,'edges':[(0,1),(0,2),(1,3),(2,6),(3,6),(2,5),(3,4),(4,5)],'ports':[0,4,1,5,6]}
N = {'vertices':9,'edges':[(0,2),(0,5),(1,4),(1,6),(2,7),(4,8),(3,5),(3,6),(5,8),(6,7),(7,8)],'ports':[0,1,2,3,4]}
INITIAL = [3, 2, 1, 3, 2, 1, 3, 2, 1, 3, 1, 2, 2, 2, 2, 3, 1, 1, 3, 2, 3, 1, 3, 7, 1, 1, 3, 2, 2, 3, 1, 1, 7, 1, 2, 2, 2, 6, 3, 1, 1, 3, 6, 3, 1, 3, 6, 7, 3, 1, 5, 6, 6, 5, 3, 1, 3, 5, 2, 3, 5, 5, 7, 6, 2, 3, 1, 3, 5, 1, 2, 6, 3, 7, 5, 2, 7, 1, 6, 3, 1, 2, 1, 2, 2, 5, 3, 7, 1, 2, 2, 1, 2, 7, 3, 7, 7, 5, 6, 2, 1, 3, 5, 6, 5, 5, 7, 7, 5, 1, 2, 6, 3, 5, 2, 1, 2, 3, 2, 1, 3, 2, 1, 3, 2, 1, 6, 7, 3, 1, 5, 2, 6, 7, 1, 6, 3, 1, 2, 3, 1, 2, 7, 7, 2, 1, 5, 6, 7, 6, 3, 7, 5, 1, 6, 6, 7, 5, 2, 3, 5, 2, 3, 1, 6, 7, 7, 5, 1, 2, 6, 5, 3, 1, 7, 1, 2, 4, 6, 2, 1, 6, 2, 4, 3, 7, 2, 3, 3, 4, 1, 5, 3, 5, 1]
FIRST_CIRCUIT = [119, 123, 129, 133, 138, 165, 167, 173, 184, 185, 189, 191]
INTERSECTION = (9093334202154902477696747075051056032113828337972704771665, 12594718827481672415870838694324089607298511120473127911424)


def shifted(pole,offset):
    return ([(u+offset,v+offset) for u,v in pole['edges']],
            [v+offset for v in pole['ports']])


def local_poles():
    e,p = shifted(M,0); ee,q = shifted(N,7)
    Z = {'vertices':17,'edges':e+ee+[(p[2],q[0]),(p[3],q[1]),(p[4],16),(q[4],16)],
         'ports':[p[0],p[1],q[2],q[3],16]}
    e,p = shifted(Z,0); ee,q = shifted(Z,17); eee,r = shifted(M,34)
    Y = {'vertices':41,'edges':e+ee+eee+[(p[2],r[1]),(p[3],r[0]),(r[3],q[2]),(r[2],q[3]),(p[4],q[4])],
         'ports':[p[0],p[1],q[0],q[1],r[4]]}
    return {'M':M,'N':N,'Z':Z,'Y':Y}


def graph(poles):
    Y = poles['Y']; edges,regions = [],[]
    for i in range(3):
        es,ps = shifted(Y,41*i); edges += es
        regions.append({'vertices':list(range(41*i,41*i+41)),'ports':ps})
    for i,region in enumerate(regions):
        p = region['ports']; following = regions[(i+1)%3]['ports']; x = 124+i
        edges += [(p[4],x),(following[0],x),(x,123),(p[1],127),(p[2],128),(p[3],129)]
    for region in regions:
        vs = set(region['vertices'])
        region['charged_edges'] = [e for e,uv in enumerate(edges) if vs.intersection(uv)]
    return {'name':'ThreeY1Star130','vertices':130,'edges':edges,'regions':regions,
            'center':123,'center_neighbors':[124,125,126],'other_junctions':[127,128,129]}


def local_audit(poles):
    audits,boundaries = {},{}
    for name in ('M','N','Z'):
        pole = poles[name]; n = pole['vertices']
        es = pole['edges']+[(v,n) for v in pole['ports']]
        binary = supports(cycle_basis(n+1,es)); full = (1 << len(es))-1
        rows,hist = [],Counter()
        for y in binary:
            for z in binary:
                if y | z != full: continue
                values = [((y >> e)&1)+2*((z >> e)&1) for e in range(len(es))]
                rows.append(values); hist[tuple(values[-5:])] += 1
        boundaries[name] = sorted(hist)
        audits[name] = {'binary_flows':len(binary),'nowhere_zero_two_bit_flows':len(rows),
                        'records_sha256':digest(sorted(rows)),
                        'boundary_histogram':[list(k)+[v] for k,v in sorted(hist.items())]}
    assert all(p[0] == p[1] or p[2] == p[3] for p in boundaries['M'])
    assert all(p[0] != p[1] for p in boundaries['N'])
    assert all(p[0] == p[1] and set(p[2:]) == {1,2,3} for p in boundaries['Z'])
    combinations = 0; compatible = 0
    for p,q,r in itertools.product(boundaries['Z'],boundaries['Z'],boundaries['M']):
        combinations += 1
        compatible += p[2] == r[1] and p[3] == r[0] and r[3] == q[2] and r[2] == q[3] and p[4] == q[4]
    assert compatible == 0
    audits['Y'] = {'boundary_combinations':combinations,'zero_free_compatible_combinations':compatible}
    return audits


def connectivity(obj):
    basis = cycle_basis(obj.n,obj.edges)
    columns = [sum(((C >> e)&1) << i for i,C in enumerate(basis)) for e in range(obj.m)]
    assert all(columns) and len(set(columns)) == obj.m
    index = {col:e for e,col in enumerate(columns)}
    triples = [[i,j,index[columns[i] ^ columns[j]]] for i,j in itertools.combinations(range(obj.m),2)
               if columns[i] ^ columns[j] in index and index[columns[i] ^ columns[j]] > j]
    assert sorted(triples) == sorted([sorted(es) for es in obj.incident])
    pair_table,quads = {},set()
    for a,b in itertools.combinations(range(obj.m),2):
        value = columns[a] ^ columns[b]
        for c,d in pair_table.get(value,[]):
            if len({a,b,c,d}) == 4: quads.add(tuple(sorted((a,b,c,d))))
        pair_table.setdefault(value,[]).append((a,b))
    adjacent_pairs = {tuple(sorted(set(obj.incident[u]) ^ set(obj.incident[v]))) for u,v in obj.edges}
    assert quads == adjacent_pairs
    side = (1 << 41)-1; boundary = obj.cut(side)
    assert boundary.bit_count() == 5 and len(obj.components(obj.full ^ boundary)) == 2
    return {'cycle_dimension':len(basis),'distinct_nonzero_columns':len(columns),
            'three_edge_cuts':len(triples),'three_cut_records_sha256':digest(sorted(triples)),
            'four_edge_cuts':len(quads),'four_cut_records_sha256':digest(sorted(quads)),
            'five_cut_side':side,'five_cut_edges':boundary,'cyclic_edge_connectivity':5}


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
    assert len(best) == 5
    return {'girth':len(best),'shortest_circuit_edges':best}


def repair(obj):
    first = obj.switch(INITIAL,6,FIRST_CIRCUIT)
    F,t = INTERSECTION; ell = 4
    before = first['flow_after']
    M = sum((x == 4) << e for e,x in enumerate(before))
    assert obj.even(F) and obj.even(t) and F & t == M and M.bit_count() == 3
    difference = F ^ obj.support(before,ell)
    circuits = circuit_components(difference,obj.n,obj.edges)
    assert len(circuits) == 1 and len(circuits[0]) == 101
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
    assert all(min(move['color_sizes']) == move['color_sizes'][3] == 3 for move in (first,second))
    return {'moves':[first,second],'intersection_first':F,'intersection_partner':t,
            'first_functional':ell,'target_color':4,
            'final_lift':{'coordinate_functionals':forms,'transformed_flow':transformed,
                          'fourth_coordinate':fourth,'cover_pairs':cover}}



def main():
    poles = local_poles(); g = graph(poles); obj = Graph(g)
    assert obj.valid_flow(INITIAL)
    charged = [set(r['charged_edges']) for r in g['regions']]
    assert all(len(row) == 64 for row in charged)
    assert all(a.isdisjoint(b) for a,b in itertools.combinations(charged,2))
    assert all(sum(INITIAL[e] == 4 for e in row) == 1 for row in charged)
    source = HERE/'petersen_free_minimum_obstruction.json'
    result = {'date':'2026-10-06',
              'scope':'Global minimum color multiplicity three can block every incident fiber even with cyclic edge connectivity five.',
              'sources':[{'file':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}],
              'literature':{'url':'https://arxiv.org/html/2604.22501v1','authors':'Mattiolo, Negrini, Pagani',
                            'used':'The M, N, Z and Y1 five-poles in Section 3. The outer assembly and flow certificates are computed here.'},
              'local_poles':poles,'local_audits':local_audit(poles),'graph':g,
              'connectivity':connectivity(obj),'girth_certificate':girth_certificate(obj),
              'minimum_color_multiplicity':3,'initial_flow':INITIAL,
              'initial_color_sizes':[INITIAL.count(a) for a in range(1,8)],
              'matching_failures':[obj.matching_failure(INITIAL,a) for a in range(1,8)],
              'failed_flags':obj.failed_flags(INITIAL),'repair':repair(obj)}
    path = HERE/'cyclic_five_minimum_obstruction.json'
    path.write_text(json.dumps(result,indent=2)+'\n')
    print('Local zero-free counts:',{k:v.get('nowhere_zero_two_bit_flows',0) for k,v in result['local_audits'].items()})
    print('Connectivity:',result['connectivity'])
    print('Girth:',result['girth_certificate'])
    print('Global minimum 3; sizes:',result['initial_color_sizes'])
    print('Odd components:',[r['component_vertices'] for r in result['matching_failures']])
    print('Switch lengths:',[len(m['edges']) for m in result['repair']['moves']])
    print('Certificate bytes:',path.stat().st_size,'SHA256:',hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
