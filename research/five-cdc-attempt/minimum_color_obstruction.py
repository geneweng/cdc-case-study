#!/usr/bin/env python3
"""Certify a globally minimum color class with no successful incident fiber.

The flow and intersection pair are fixed discovery witnesses. All generated
certificates and the elementary lower bound use only the standard library.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

from fiber_cut_obstructions import eliminate
from flow_space_components import cycle_basis, circuit_components

HERE = Path(__file__).resolve().parent
INTERNAL = [(2,3),(3,4),(2,7),(3,8),(4,9),(5,7),(6,8),(7,9),(8,5),(9,6)]
SPOKES = [(0,10),(5,10),(2,10),(1,11),(6,11),(8,11),(3,12),(7,12),(4,13),(9,13)]
INITIAL = [2,4,6,3,5,6,6,5,1,2,3,3,6,7,5,3,5,2,2,7,1,6,1,5,7,7,3,6,6,1,1,6,1,7,7,7,6,5,1,2,6,2,3,5,1,6,6,6,3,7,5,5,7,6,2,6,1,7,7,5,1,5,7,4,3,5,2,6,5,3,7,6,2,7,1,1,3,6,4,1,7,7,3,5,1,6,7,3,6,1,4,5,7,7,2,6,2,5,5,7,3,4,1,2,5,2,5,2,7,7,5,2,1,7,3,2,2,6,5,5,7,7,6,3,1,3,5,3,6,2,5,7,1,1,6,6,6,7,7,1,1,5,1,2,6,1,5,7,2,6,7,3,2,6,3,5,1,3,7,7,1,4,6,5,7,3,1,6,6,7,7]
FIRST_CIRCUIT = [11,14,17,61,62,63,64]
INTERSECTION = (1149039833540733743438802862584251342053628920875206,
                1698995659070370239468476443645301808823510261989419)


def digest(value):
    return hashlib.sha256(json.dumps(value,separators=(',',':')).encode()).hexdigest()


def graph():
    edges = list(SPOKES)+[(12,13)]
    next_vertex = 14
    regions = []
    for region in range(2):
        blocks = [{v:next_vertex+8*j+v-2 for v in range(2,10)} for j in range(5)]
        next_vertex += 40
        junctions = [(next_vertex+2*j,next_vertex+2*j+1) for j in range(5)]
        next_vertex += 10
        for b in blocks: edges += [(b[u],b[v]) for u,v in INTERNAL]
        for j,(u,w) in enumerate(junctions):
            nu,nw = junctions[(j+1)%5]; b = blocks[j]
            edges += [(5*region+j,u),(5*region+j,w),(u,b[2]),(w,b[6]),(b[4],nu),(b[5],nw)]
        regions.append({'base_vertices':list(range(5*region,5*region+5)),
                        'blocks':[{str(v):w for v,w in b.items()} for b in blocks],
                        'junctions':junctions})
    index = {tuple(sorted(edge)):e for e,edge in enumerate(edges)}
    for region in regions:
        block_edges = []
        for j,raw in enumerate(region['blocks']):
            b = {int(v):w for v,w in raw.items()}
            u,w = region['junctions'][j]; nu,nw = region['junctions'][(j+1)%5]
            local = [(b[x],b[y]) for x,y in INTERNAL]+[(b[4],nu),(b[5],nw),(b[2],u),(b[6],w)]
            block_edges.append([index[tuple(sorted(e))] for e in local])
        spokes = [next(e for e,uv in enumerate(SPOKES) if v in uv) for v in region['base_vertices']]
        constraints = [sorted(set(block_edges[j-1]+block_edges[j]+[spokes[j]])) for j in range(5)]
        region.update(block_edges=block_edges, spoke_edges=spokes, zero_hitting_sets=constraints,
                      charged_edges=sorted(set(e for row in constraints for e in row)), lower_bound=3)
    return {'name':'TwoPentagonBlowup114','vertices':next_vertex,'edges':edges,
            'base_edges':list(SPOKES)+[(12,13)]+[(off+j,off+(j+1)%5) for off in (0,5) for j in range(5)],
            'regions':regions}


class Graph:
    def __init__(self,g):
        self.n,self.edges = g['vertices'],g['edges']
        self.m = len(self.edges); self.full = (1 << self.m)-1
        self.incident = [[e for e,uv in enumerate(self.edges) if v in uv] for v in range(self.n)]

    def cut(self,A):
        return sum(((((A >> u) ^ (A >> v)) & 1) << e) for e,(u,v) in enumerate(self.edges))

    def components(self,mask):
        seen,out = set(),[]
        for v in range(self.n):
            if v in seen: continue
            queue = [v]; seen.add(v)
            for u in queue:
                for e in self.incident[u]:
                    x,y = self.edges[e]; w = x ^ y ^ u
                    if mask >> e & 1 and w not in seen:
                        seen.add(w); queue.append(w)
            out.append(sum(1 << u for u in queue))
        return out

    def support(self,flow,normal):
        return sum(((x & normal).bit_count()%2) << e for e,x in enumerate(flow))

    def even(self,mask):
        return all(sum((mask >> e)&1 for e in es)%2 == 0 for es in self.incident)

    def valid_flow(self,flow):
        return len(flow) == self.m and all(1 <= x <= 7 for x in flow) and all(flow[a] ^ flow[b] ^ flow[c] == 0 for a,b,c in self.incident)

    def matching_failure(self,flow,a):
        M = sum((x == a) << e for e,x in enumerate(flow))
        D = sum(1 << v for v in {v for e,uv in enumerate(self.edges) if M >> e & 1 for v in uv})
        B = ((1 << self.n)-1) ^ D
        free = sum(1 << e for e,(u,v) in enumerate(self.edges) if B >> u & 1 and B >> v & 1)
        odd = [K for K in self.components(free) if K & B and K.bit_count()%2]
        assert odd
        K = min(odd,key=lambda k:(k.bit_count(),k))
        return {'color':a,'matching':M,'size':M.bit_count(),'odd_unmatched_component':K,
                'component_vertices':[v for v in range(self.n) if K >> v & 1]}

    def failed_flags(self,flow):
        rows = []
        for a,b in itertools.combinations(range(1,8),2):
            if a ^ b < b: continue
            for ell in sorted((a,b,a ^ b)):
                other = a if ell != a else b
                F,y = self.support(flow,ell),self.support(flow,other)
                S = self.full & ~(F | y)
                forced = [e for e in range(self.m) if S >> e & 1]
                components = self.components(self.full ^ F)
                equations = [(sum(1 << e for e in es),0) for es in self.incident]
                equations += [(1 << e,1) for e in forced]
                equations += [(self.cut(K) & y,0) for K in components]
                result = eliminate(equations,self.m)
                assert 'contradiction' in result
                tag = result['contradiction']
                X = tag & ((1 << self.n)-1)
                A = 0
                for i,K in enumerate(components):
                    if tag >> (self.n+len(forced)+i) & 1: A ^= K
                assert self.cut(A) & ~F == 0 and self.cut(X) & ~S == self.cut(A) & y
                assert (self.cut(X) & S).bit_count()%2 == X.bit_count()%2 == 1
                rows.append({'plane_functionals':[a,b],'first':ell,'second':other,'A':A,'X':X})
        return rows

    def switch(self,flow,a,es):
        C = sum(1 << e for e in es)
        assert self.even(C) and len(circuit_components(C,self.n,self.edges)) == 1
        assert all(flow[e] != a for e in es)
        after = [x ^ a if C >> e & 1 else x for e,x in enumerate(flow)]
        assert self.valid_flow(after)
        return {'increment':a,'edges':es,'flow_after':after,
                'color_sizes':[after.count(b) for b in range(1,8)]}


def local_fourpole():
    edges = INTERNAL+[(4,-1),(5,-1),(2,-1),(6,-1)]
    stars = [sum(1 << e for e,uv in enumerate(edges) if v in uv) for v in range(2,10)]
    binary = [mask for mask in range(1 << 14) if all((mask & star).bit_count()%2 == 0 for star in stars)]
    rows, boundary = [], Counter()
    for y in binary:
        for z in binary:
            if y | z != (1 << 14)-1: continue
            values = [((y >> e)&1)+2*((z >> e)&1) for e in range(14)]
            assert values[10] == values[11] and values[12] == values[13]
            rows.append(values); boundary[tuple(values[10:])] += 1
    return {'binary_flows':len(binary),'nowhere_zero_two_bit_flows':len(rows),
            'records_sha256':digest(sorted(rows)),
            'boundary_histogram':[list(k)+[v] for k,v in sorted(boundary.items())]}


def connectivity(obj):
    basis = cycle_basis(obj.n,obj.edges)
    columns = [sum(((C >> e)&1) << i for i,C in enumerate(basis)) for e in range(obj.m)]
    assert all(columns) and len(set(columns)) == obj.m
    index = {col:e for e,col in enumerate(columns)}
    triples = [[i,j,index[columns[i] ^ columns[j]]] for i in range(obj.m) for j in range(i+1,obj.m)
               if columns[i] ^ columns[j] in index and index[columns[i] ^ columns[j]] > j]
    assert sorted(triples) == sorted([sorted(es) for es in obj.incident])
    block = sum(1 << v for v in range(14,22))
    boundary = obj.cut(block); assert boundary.bit_count() == 4
    assert len(obj.components(obj.full ^ boundary)) == 2
    return {'cycle_dimension':len(basis),'distinct_nonzero_columns':len(columns),
            'three_edge_cuts':len(triples),'three_cut_records_sha256':digest(sorted(triples)),
            'four_cut_side':block,'four_cut_edges':boundary,'cyclic_edge_connectivity':4}


def repair(obj):
    first = obj.switch(INITIAL,6,FIRST_CIRCUIT)
    F,t = INTERSECTION; ell = 6
    before = first['flow_after']
    M = sum((x == 4) << e for e,x in enumerate(before))
    assert obj.even(F) and obj.even(t) and F & t == M and M.bit_count() == 6
    difference = F ^ obj.support(before,ell)
    circuits = circuit_components(difference,obj.n,obj.edges)
    assert len(circuits) == 1 and len(circuits[0]) == 77
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
    sources = ['matching_terminal_flow.json','matching_fiber_repair.json']
    result = {'date':'2026-10-06',
              'scope':'Global minimum color multiplicity does not force a suitable matching or a successful incident fiber, even on a cyclically four-edge-connected cubic graph.',
              'sources':[{'file':name,'sha256':hashlib.sha256((HERE/name).read_bytes()).hexdigest()} for name in sources],
              'graph':g,'local_fourpole_audit':local_fourpole(),'connectivity':connectivity(obj),
              'minimum_color_multiplicity':6,'initial_flow':INITIAL,
              'initial_color_sizes':[INITIAL.count(a) for a in range(1,8)],
              'matching_failures':[obj.matching_failure(INITIAL,a) for a in range(1,8)],
              'failed_flags':obj.failed_flags(INITIAL),'repair':repair(obj)}
    (HERE/'minimum_color_obstruction.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Local four-pole:',result['local_fourpole_audit'])
    print('Connectivity:',result['connectivity'])
    print('Global lower bound: 6; initial color sizes:',result['initial_color_sizes'])
    print('Odd unmatched components:',[r['component_vertices'] for r in result['matching_failures']])
    print('Failed flags:',len(result['failed_flags']))
    print('Repair lengths:',[len(m['edges']) for m in result['repair']['moves']])


if __name__ == '__main__':
    main()
