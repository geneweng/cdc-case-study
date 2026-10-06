#!/usr/bin/env python3
"""Independent matching/fiber verification by component parity, direct
intersection tests, and complete fourth-cycle restrictions. No constructor imports.
"""
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from verify_fiber_cut_obstructions import Check, canonical, planes, digest

HERE=Path(__file__).resolve().parent


def xor(values):
    answer=0
    for value in values: answer ^= value
    return answer


class Verify(Check):
    def __init__(self,g):
        super().__init__(g)
        self.name=g['name']; self.incident=[[e for e,edge in enumerate(self.edges) if v in edge] for v in range(self.n)]
        self.hcomponents=[self.components(self.full ^ F) for F in self.cycles]
        self.outside_checks=0; self.extensions=set()

    def endpoints(self,M):
        vertices=[]
        for e,edge in enumerate(self.edges):
            if M >> e & 1: vertices.extend(edge)
        assert len(vertices) == len(set(vertices))
        return sum(1 << v for v in vertices)

    @lru_cache(None)
    def matching(self,M):
        ends=self.endpoints(M); firsts=[]; pairs=0
        for code,F in enumerate(self.cycles):
            if F & M != M: continue
            comps=self.hcomponents[code]
            # Prescribing t=1 on M and t=0 on F\M is possible exactly when
            # every component of G-F has even M-boundary.
            if any((K & ends).bit_count()%2 for K in comps): continue
            firsts.append(code)
            free_dimension=(self.full ^ F).bit_count()-self.n+len(comps)
            assert free_dimension >= 0
            pairs += 1 << free_dimension
        return firsts,pairs

    def unmatched_data(self,M):
        ends=self.endpoints(M); unmatched=((1 << self.n)-1) ^ ends
        free=sum(1 << e for e,(u,v) in enumerate(self.edges) if unmatched >> u & 1 and unmatched >> v & 1)
        comps=sorted((K for K in self.components(free) if K & unmatched),key=lambda K:(K & -K).bit_length())
        odd=[K for K in comps if K.bit_count()%2]
        dim=free.bit_count()-unmatched.bit_count()+len(comps)
        return comps,odd,dim

    @lru_cache(None)
    def success(self,key):
        return self.good_firsts(key)

    def plane_audit(self,a,b):
        M=self.full & ~(self.cycles[a] | self.cycles[b]); firsts,pairs=self.matching(M)
        marked=any(f['completions'] for _,f in self.plane(a,b))
        inside=outside=False
        U={a,b,a ^ b}
        extensions={canonical((a,b,F)) for F in self.feasible(a,b)}
        for key in extensions:
            successes=self.success(key)
            inside |= any(F in U for F in successes)
            outside |= any(F not in U for F in successes)
        self.extensions.update(extensions)
        assert inside == marked and outside == bool(firsts)
        assert any(self.success(key) for key in extensions) == (marked or bool(firsts))
        good=set(firsts)
        for F in self.feasible(a,b):
            required=self.cycles[F] & ~(self.cycles[a] & self.cycles[b])
            passes=required in self.restrictions[F]
            assert passes == (F in good)
            self.outside_checks += 1
        return [a,b,M,int(marked),int(bool(firsts)),len(firsts),pairs]

    def detailed(self,record):
        M=record['matching_mask']; ends=self.endpoints(M)
        assert record['matching_edges'] == [e for e in range(self.m) if M >> e & 1]
        assert ends == record['endpoint_mask']
        required=[e for e,(u,v) in enumerate(self.edges) if not (M >> e & 1) and ((ends >> u)&1 or (ends >> v)&1)]
        assert required == record['required_edges']
        assert record['forced_degree_three_vertices'] == [v for v,es in enumerate(self.incident) if all(e in required for e in es)]
        candidates=[]; good=[]
        for code,L in enumerate(self.cycles):
            if L & M: continue
            if any(sum((L >> e)&1 for e in self.incident[v]) != 2 for v in range(self.n) if ends >> v & 1): continue
            pieces=[]
            for K in self.components(L):
                es=[e for e,(u,v) in enumerate(self.edges) if L >> e & 1 and K >> u & 1]
                if es: pieces.append(es)
            pieces.sort(key=lambda es:min(es))
            counts=[len({v for e in es for v in self.edges[e]} & {v for v in range(self.n) if ends >> v & 1}) for es in pieces]
            candidates.append({'cycle_code':code,'circuit_edges':pieces,'matching_endpoint_counts':counts})
            if not any(c%2 for c in counts): good.append(code)
        assert candidates == record['candidate_even_subgraphs']
        assert good == record['admissible_even_subgraph_codes']
        comps,odd,dim=self.unmatched_data(M)
        assert record['unmatched_components'] == comps and record['odd_unmatched_components'] == odd
        assert record['unmatched_cycle_dimension'] == dim
        assert len(candidates) == (0 if odd else 1 << dim)
        firsts,count=self.matching(M)
        pairs=[[F,t] for F in firsts for t,mask in enumerate(self.cycles) if self.cycles[F] & mask == M]
        assert pairs == record['intersection_pairs'] and len(pairs) == count
        assert firsts == record['admissible_first_cycles']
        assert record['repairable'] == bool(firsts) == bool(good)
        assert count == sum(1 << len(r['circuit_edges']) for r in candidates if r['cycle_code'] in good)


def audit(g,plane_list):
    rows=[g.plane_audit(a,b) for a,b in sorted(set(plane_list))]
    matchings=sorted({r[2] for r in rows}); classes=Counter((r[3],r[4]) for r in rows)
    mrows=[]
    for M in matchings:
        comps,odd,dim=g.unmatched_data(M)
        mrows.append([M,int(bool(g.matching(M)[0])),len(g.matching(M)[0]),g.matching(M)[1],0 if odd else 1 << dim,dim,len(odd)])
    return {'planes':len(rows),'distinct_matchings':len(matchings),'marked_and_matching_histogram':[list(k)+[v] for k,v in sorted(classes.items())],
            'repairable_matchings':sum(r[1] for r in mrows),'matchings_without_candidate':sum(r[4]==0 for r in mrows),
            'matchings_failing_only_circuit_parity':sum(r[4]>0 and not r[1] for r in mrows),
            'plane_records_sha256':digest(rows),'matching_records_sha256':digest(mrows)}


def verify_repair(j,w):
    before=w['initial_flow']; a=w['increment']; ell=w['first_functional']
    F=j.cycles[w['target_first_cycle']]; t=j.cycles[w['intersection_partner']]
    M=sum(1 << e for e,x in enumerate(before) if x==a)
    assert F & t == M and (a & ell).bit_count()%2 == 1
    oldF=sum(((ell & x).bit_count()%2) << e for e,x in enumerate(before))
    assert oldF ^ F == j.cycles[w['difference_cycle_code']]
    changed=0; flow=before
    for move in w['moves']:
        C=sum(1 << e for e in move['edges']); assert C in j.cycles
        assert not (changed & C); changed |= C
        degrees=Counter(v for e in move['edges'] for v in j.edges[e]); assert set(degrees.values()) == {2}
        assert sum(bool(K & sum(1 << v for v in degrees)) for K in j.components(C)) == 1
        assert move['increment'] == a and all(flow[e] != a for e in move['edges'])
        flow=[x ^ a if C >> e & 1 else x for e,x in enumerate(flow)]
        assert flow == move['flow_after']
    assert changed == oldF ^ F
    out=w['final_lift']; assert flow == out['flow']
    third,second,first=out['coordinate_functionals']; assert first == ell
    assert all((form & a).bit_count()%2 == 0 for form in (second,third))
    assert len({0,first,second,third,first^second,first^third,second^third,first^second^third}) == 8
    projected=[sum(((form & x).bit_count()%2) << e for e,x in enumerate(flow)) for form in (second,third)]
    fourth=t ^ projected[0] ^ projected[1]
    assert fourth == out['fourth_coordinate_mask'] and fourth in j.cycles
    transformed=[sum(((form & x).bit_count()%2) << k for k,form in enumerate((third,second,first))) for x in flow]
    assert transformed == out['transformed_flow']
    palette=[4,5,6,15,8]
    decode={u ^ v:(1 << i)|(1 << k) for i,u in enumerate(palette) for k,v in enumerate(palette) if i < k}
    pairs=[decode[x+8*((fourth >> e)&1)] for e,x in enumerate(transformed)]
    assert pairs == out['cover_pairs'] and all(p.bit_count()==2 for p in pairs)
    assert all(xor(pairs[e] for e in es) == 0 for es in j.incident)


def main():
    data=json.loads((HERE/'matching_fiber_repair.json').read_text())
    for source in data['sources']:
        assert hashlib.sha256((HERE/source['file']).read_bytes()).hexdigest() == source['sha256']
    old=json.loads((HERE/'flow_space_components.json').read_text())
    p=Verify(next(g for g in old['graphs'] if g['name']=='Petersen'))
    pplanes=[(a,b) for a in range(1,len(p.cycles)) for b in range(a+1,len(p.cycles)) if b < a ^ b and p.feasible(a,b)]
    assert audit(p,pplanes) == data['petersen_audit']
    print('Petersen: all 400 feasible planes and 295 color matchings checked against complete flow extensions.',flush=True)
    g=next(g for g in old['graphs'] if g['name']=='Snark20_0'); j=Verify(g)
    repair=g['hard_flow_repair']; keys=[repair['initial_space']]+[r['target_space'] for r in repair['rounds']]
    neighbors=sorted({canonical((a,b,z)) for a,b in planes(keys[0]) for z in j.feasible(a,b)}-{keys[0]})
    assert len(neighbors) == 185
    jplanes=[ab for key in keys+neighbors for ab in planes(key)]
    assert audit(j,jplanes) == data['flower_audit']
    expected_flows=[repair['initial_flow']]+[m['flow_after'] for m in repair['moves']]
    for key,flow,rec in zip(keys,expected_flows,data['flower_path'],strict=True):
        assert rec['space_key'] == key and rec['flow'] == flow
        assert rec['marked_planes'] == j.marked_count(key)
        assert [m['increment'] for m in rec['matchings']] == list(range(1,8))
        for m in rec['matchings']:
            assert m['matching_mask'] == sum(1 << e for e,x in enumerate(flow) if x==m['increment'])
            j.detailed(m)
        assert rec['repairable_increments'] == [m['increment'] for m in rec['matchings'] if m['repairable']]
    initial=data['flower_path'][0]['matchings']
    assert [m['increment'] for m in initial if m['forced_degree_three_vertices']] == [1,2,3,4,6,7]
    assert len(initial[4]['candidate_even_subgraphs']) == 1
    assert initial[4]['candidate_even_subgraphs'][0]['matching_endpoint_counts'] == [5,3]
    verify_repair(j,data['intersection_repair'])
    assert data['intersection_repair']['initial_flow'] == expected_flows[1]
    assert data['intersection_repair']['final_lift']['flow'] == expected_flows[2]
    assert len(data['intersection_repair']['moves']) == 1
    # Compare the actual circuit and values, omitting the prior round annotation.
    actual=data['intersection_repair']['moves'][0]
    assert all(actual[k] == repair['moves'][1][k] for k in ('increment','edges','flow_after'))
    rows=[]
    for obj in (p,j):
        for e in range(obj.m):
            firsts,_=obj.matching(1 << e); assert firsts
            rows.append([obj.name,e,len(firsts)])
    assert {'matchings':len(rows),'records_sha256':digest(rows)} == data['singleton_matching_audit']
    print('J5: all 1,076 selected planes and 937 color matchings verified; complete fiber criterion agrees in every case.')
    print('Initial obstruction: six forced branches and one unique candidate with odd endpoint counts 5 and 3.')
    print('Intersection cycles 577 and 996 reconstruct the saved eleven-circuit repair and a valid five-layer cover.')
    print('Independent outside-coordinate tests:',p.outside_checks+j.outside_checks,'distinct extension spaces:',len(p.extensions)+len(j.extensions))
    print('All 45 singleton matchings and all detailed circuit-parity/intersection witnesses verified.')


if __name__ == '__main__':
    main()
