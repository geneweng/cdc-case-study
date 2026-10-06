#!/usr/bin/env python3
"""Construct exact matching criteria for the missing half of fiber repair."""
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from fiber_cut_obstructions import Analysis, planes
from flow_space_components import circuit_components

HERE = Path(__file__).resolve().parent
SOURCE = HERE/'flow_space_components.json'
CUT_SOURCE = HERE/'fiber_cut_obstructions.json'


def digest(rows):
    return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()


class Matching(Analysis):
    def __init__(self,g):
        super().__init__(g)
        self.code = {mask:c for c,mask in enumerate(self.cycles)}
        self.adj = [[] for _ in range(self.n)]
        for e,(u,v) in enumerate(self.edges):
            self.adj[u].append((v,e)); self.adj[v].append((u,e))

    def endpoint_mask(self,M):
        ends = 0
        for e,(u,v) in enumerate(self.edges):
            if M >> e & 1:
                assert not (ends >> u & 1 or ends >> v & 1)
                ends |= (1 << u) | (1 << v)
        return ends

    def split_circuit(self,C,ends):
        first = min(C); start,at = self.edges[first]
        part = 1 << first; used = {first}; color = 1
        while at != start:
            if ends >> at & 1: color ^= 1
            following = [(w,e) for w,e in self.adj[at] if e in C and e not in used]
            assert len(following) == 1
            at,e = following[0]; used.add(e)
            if color: part |= 1 << e
        assert used == set(C)
        assert color ^ ((ends >> start)&1) == 1
        return part

    @lru_cache(None)
    def matching(self,M):
        ends = self.endpoint_mask(M)
        unmatched=((1 << self.n)-1) ^ ends
        free=sum(1 << e for e,(u,v) in enumerate(self.edges) if unmatched >> u & 1 and unmatched >> v & 1)
        free_components=[K for K in self.components(free) if K & unmatched]
        odd_components=[K for K in free_components if K.bit_count()%2]
        free_dimension=free.bit_count()-unmatched.bit_count()+len(free_components)
        required = sum(1 << e for e,(u,v) in enumerate(self.edges) if not (M >> e & 1) and ((ends >> u)&1 or (ends >> v)&1))
        branches = [v for v in range(self.n) if sum(bool(required >> e & 1) for _,e in self.adj[v]) == 3]
        candidates,good,pairs = [],[],set()
        for code,L in enumerate(self.cycles):
            if L & M or L & required != required: continue
            components = circuit_components(L,self.n,self.edges)
            touched = [sum(1 << v for v in {w for e in C for w in self.edges[e]} if ends >> v & 1) for C in components]
            record = {'cycle_code':code,'circuit_edges':components,'matching_endpoint_counts':[x.bit_count() for x in touched]}
            candidates.append(record)
            if any(x.bit_count()%2 for x in touched): continue
            good.append(code)
            parts = [self.split_circuit(C,ends) for C in components]
            masks = [sum(1 << e for e in C) for C in components]
            for assignment in range(1 << len(components)):
                F = M
                for i,part in enumerate(parts): F |= part ^ (masks[i] if assignment >> i & 1 else 0)
                t = F ^ L
                assert F & t == M and F in self.code and t in self.code
                pairs.add((self.code[F],self.code[t]))
        firsts = sorted({F for F,t in pairs})
        assert len(candidates) == (0 if odd_components else 1 << free_dimension)
        assert len(pairs) == sum(1 << len(r['circuit_edges']) for r in candidates if r['cycle_code'] in good)
        return {'matching_mask':M,'matching_edges':[e for e in range(self.m) if M >> e & 1],
                'endpoint_mask':ends,'required_edges':[e for e in range(self.m) if required >> e & 1],
                'unmatched_components':free_components,'odd_unmatched_components':odd_components,
                'unmatched_cycle_dimension':free_dimension,
                'forced_degree_three_vertices':branches,'candidate_even_subgraphs':candidates,
                'admissible_even_subgraph_codes':good,'intersection_pairs':[list(x) for x in sorted(pairs)],
                'admissible_first_cycles':firsts,'repairable':bool(firsts)}

    def plane_rows(self,plane_list):
        out=[]
        for a,b in sorted(set(plane_list)):
            M=self.all & ~(self.cycles[a] | self.cycles[b]); rec=self.matching(M)
            marked=self.plane(a,b)['marked']
            out.append([a,b,M,int(marked),int(rec['repairable']),len(rec['admissible_first_cycles']),len(rec['intersection_pairs'])])
        return out


def audit(analysis,plane_list):
    rows=analysis.plane_rows(plane_list); matchings=sorted({r[2] for r in rows}); classes=Counter((r[3],r[4]) for r in rows)
    matching_rows=[[M,int(analysis.matching(M)['repairable']),len(analysis.matching(M)['admissible_first_cycles']),
                    len(analysis.matching(M)['intersection_pairs']),len(analysis.matching(M)['candidate_even_subgraphs']),
                    analysis.matching(M)['unmatched_cycle_dimension'],len(analysis.matching(M)['odd_unmatched_components'])] for M in matchings]
    return {'planes':len(rows),'distinct_matchings':len(matchings),'marked_and_matching_histogram':[list(k)+[v] for k,v in sorted(classes.items())],
            'repairable_matchings':sum(r[1] for r in matching_rows),
            'matchings_without_candidate':sum(r[4]==0 for r in matching_rows),
            'matchings_failing_only_circuit_parity':sum(r[4]>0 and not r[1] for r in matching_rows),
            'plane_records_sha256':digest(rows),'matching_records_sha256':digest(matching_rows)}


def cover_from_intersection(a,flow,increment,first,Fcode,tcode):
    fixed=[x for x in range(1,8) if (x & increment).bit_count()%2 == 0]
    second,third=fixed[:2]
    assert first not in fixed and second ^ third == fixed[2]
    oldF=sum(((first & x).bit_count()%2) << e for e,x in enumerate(flow))
    difference=oldF ^ a.cycles[Fcode]
    moves=[]; current=list(flow)
    for C in circuit_components(difference,a.n,a.edges):
        assert all(current[e] != increment for e in C)
        current=[x ^ increment if e in C else x for e,x in enumerate(current)]
        moves.append({'increment':increment,'edges':C,'flow_after':current})
    ys=[sum(((normal & x).bit_count()%2) << e for e,x in enumerate(current)) for normal in (second,third)]
    M=sum(1 << e for e,x in enumerate(current) if x == increment)
    assert a.cycles[Fcode] & a.cycles[tcode] == M
    fourth=a.cycles[tcode] ^ ys[0] ^ ys[1]
    transformed=[4*((first & x).bit_count()%2)+2*((second & x).bit_count()%2)+(third & x).bit_count()%2 for x in current]
    palette=(4,5,6,15,8); decode={u ^ v:(1 << i)|(1 << j) for i,u in enumerate(palette) for j,v in enumerate(palette) if i < j}
    cover=[decode[x+8*((fourth >> e)&1)] for e,x in enumerate(transformed)]
    return {'initial_flow':flow,'increment':increment,'first_functional':first,'target_first_cycle':Fcode,'intersection_partner':tcode,
            'difference_cycle_code':a.code[difference],'moves':moves,
            'final_lift':{'flow':current,'coordinate_functionals':[third,second,first],
                          'transformed_flow':transformed,'fourth_coordinate_mask':fourth,'cover_pairs':cover}}


def main():
    old=json.loads(SOURCE.read_text()); p=Matching(next(g for g in old['graphs'] if g['name']=='Petersen'))
    g=next(g for g in old['graphs'] if g['name']=='Snark20_0'); j=Matching(g)
    pplanes=list(p.feasible_planes()); repair=g['hard_flow_repair']
    keys=[repair['initial_space']]+[r['target_space'] for r in repair['rounds']]
    neighbors=j.neighbors(keys[0]); jplanes=[ab for key in keys+neighbors for ab in planes(key)]
    flows=[repair['initial_flow']]+[m['flow_after'] for m in repair['moves']]
    path=[]
    for key,flow in zip(keys,flows):
        matchings=[dict(increment=inc,**j.matching(sum(1 << e for e,x in enumerate(flow) if x==inc))) for inc in range(1,8)]
        path.append({'space_key':key,'flow':flow,'marked_planes':sum(j.plane(a,b)['marked'] for a,b in planes(key)),
                     'repairable_increments':[m['increment'] for m in matchings if m['repairable']], 'matchings':matchings})
    witness=cover_from_intersection(j,flows[1],2,2,577,996)
    assert witness['final_lift']['flow'] == flows[2]
    assert len(witness['moves']) == 1 and witness['moves'][0]['edges'] == repair['moves'][1]['edges']
    singleton_rows=[]
    for a in (p,j):
        for e in range(a.m):
            rec=a.matching(1 << e)
            # Both audited graphs stay bridgeless after deleting a single edge.
            assert rec['repairable']
            singleton_rows.append([a.g['name'],e,len(rec['admissible_first_cycles'])])
    result={'date':'2026-10-05','sources':[{'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in (SOURCE,CUT_SOURCE)],
            'scope':'Exact fiber success: linear plane marks or a color matching that is an intersection of two binary cycles.',
            'petersen_audit':audit(p,pplanes),'flower_audit':audit(j,jplanes),'flower_path':path,
            'intersection_repair':witness,'singleton_matching_audit':{'matchings':len(singleton_rows),'records_sha256':digest(singleton_rows)}}
    (HERE/'matching_fiber_repair.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('petersen_audit','flower_audit','singleton_matching_audit')},indent=2))
    print('Path repairable increments:',[r['repairable_increments'] for r in path])


if __name__ == '__main__':
    main()
