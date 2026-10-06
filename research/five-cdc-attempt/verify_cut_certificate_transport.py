#!/usr/bin/env python3
"""Independent transport audit using DFS circuits, dual-vector lookup, and
signed-edge certificate enumeration. Reuses only the earlier independent
cycle/restriction checker; imports no constructor code.
"""
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from verify_fiber_cut_obstructions import Check, digest

HERE = Path(__file__).resolve().parent


def xor(values):
    out = 0
    for x in values: out ^= x
    return out


def dot(a,b):
    return (a & b).bit_count()%2


def annihilator(a,b):
    if not a or not b or a == b: return 0
    return next(t for t in range(1,8) if dot(t,a) == dot(t,b) == 0)


class Verify(Check):
    def __init__(self,g):
        super().__init__(g)
        self.incident = [[e for e,edge in enumerate(self.edges) if v in edge] for v in range(self.n)]
        self.adj = [[] for _ in range(self.n)]
        for e,(u,v) in enumerate(self.edges):
            self.adj[u].append((v,e)); self.adj[v].append((u,e))
        found = set()
        for start in range(self.n):
            def walk(v,visited,mask):
                for w,e in self.adj[v]:
                    if w == start and len(visited) >= 3: found.add(mask | (1 << e))
                    elif w > start and w not in visited: walk(w,visited|{w},mask | (1 << e))
            walk(start,{start},0)
        self.circuits = sorted((self.cycles.index(C),C) for C in found)

    def flow(self,F,y,z):
        return [4*((self.cycles[F] >> e)&1)+2*((self.cycles[y] >> e)&1)+((self.cycles[z] >> e)&1) for e in range(self.m)]

    def certificates(self,Fcode,ycode):
        F,y = self.cycles[Fcode],self.cycles[ycode]; T = F | y
        components = self.components(self.full ^ F); answer = []
        for selector in range(1 << len(components)):
            A = sum(K for j,K in enumerate(components) if selector >> j & 1)
            if A & 1: continue
            q = y & self.cut(A)
            labeled = {}; blocks = []; valid = True
            for root in range(self.n):
                if root in labeled: continue
                labeled[root] = 0; queue = [root]
                for v in queue:
                    for w,e in self.adj[v]:
                        if not (T >> e & 1): continue
                        want = labeled[v] ^ ((q >> e)&1)
                        if w in labeled:
                            if labeled[w] != want: valid = False; break
                        else: labeled[w] = want; queue.append(w)
                    if not valid: break
                if not valid: break
                blocks.append(sum(1 << v for v in queue))
            if not valid: continue
            base = sum(bit << v for v,bit in labeled.items())
            for flips in range(1 << len(blocks)):
                X = base ^ sum(K for j,K in enumerate(blocks) if flips >> j & 1)
                if X & 1 or X.bit_count()%2 != 1: continue
                S = self.full ^ T
                if (self.cut(X)&S).bit_count()%2 != 1: continue
                answer.append({'A':A,'X':X,'cut_A':self.cut(A),'cut_X':self.cut(X)})
        return sorted(answer,key=lambda w:(w['A'],w['X']))

    def valid(self,F,y,w):
        ca,cx = self.cut(w['A']),self.cut(w['X']); S = self.full & ~(F | y)
        return ca & ~F == 0 and cx & (F | y) == y & ca and (cx & S).bit_count()%2 == 1

    @lru_cache(None)
    def normal_record(self,flow):
        assert len(flow) == self.m and all(1 <= x <= 7 for x in flow)
        normals = []
        for es in self.incident:
            assert xor(flow[e] for e in es) == 0
            normals.append(next(t for t in range(1,8) if all(dot(t,flow[e]) == 0 for e in es)))
        tests = []
        for ell in range(1,8):
            second = next(x for x in range(1,8) if x != ell)
            third = next(x for x in range(1,8) if x not in (ell,second,ell ^ second))
            F,y,z = [sum(dot(t,x) << e for e,x in enumerate(flow)) for t in (ell,second,third)]
            required = F & ~(y & z)
            components = sorted(self.components(self.full ^ F),key=lambda K:(K & -K).bit_length())
            charges = []
            for K in components:
                charge = xor(normals[v] for v in range(self.n) if K >> v & 1)
                odd = (required & self.cut(K)).bit_count()%2
                assert charge == (ell if odd else 0)
                charges.append(charge)
            bad = [K for K,q in zip(components,charges) if q]
            local = [e for e,(u,v) in enumerate(self.edges) if normals[u] ^ normals[v] == ell]
            # These are precisely the obstructed two-vertex components.
            assert sorted(sum(1 << v for v in self.edges[e]) for e in local) == sorted(K for K in bad if K.bit_count() == 2)
            assert (not bad) == (required in self.restrictions[self.cycles.index(F)])
            tests.append({'first_functional':ell,'components':components,'charges':charges,
                          'bad_components':bad,'bad_isolated_edges':local})
        return {'flow':list(flow),'vertex_normals':normals,'tests':tests,
                'successful_firsts':[t['first_functional'] for t in tests if not t['bad_components']]}

    def check_move(self,flow,C,inc):
        assert C in (mask for _,mask in self.circuits)
        assert all(flow[e] != inc for e in range(self.m) if C >> e & 1)
        after = tuple(x ^ inc if C >> e & 1 else x for e,x in enumerate(flow))
        old,new = self.normal_record(tuple(flow)),self.normal_record(after)
        ns,nt = old['vertex_normals'],new['vertex_normals']
        for v,es in enumerate(self.incident):
            touched = [e for e in es if C >> e & 1]
            expected = ns[v]
            if touched:
                assert len(touched) == 2
                off = next(e for e in es if e not in touched)
                expected ^= annihilator(inc,flow[off])
            assert nt[v] == expected
        count = 0
        for t in old['tests']:
            ell = t['first_functional']
            if dot(ell,inc): continue
            other = new['tests'][ell-1]; assert t['components'] == other['components']
            for K,q0,q1 in zip(t['components'],t['charges'],other['charges'],strict=True):
                crossing = xor(flow[e] for e in range(self.m) if (C & self.cut(K)) >> e & 1)
                assert q1 == q0 ^ annihilator(inc,crossing); count += 1
        return list(after),count

    def legal_moves(self,flow):
        return [(code,C,inc) for code,C in self.circuits for inc in range(1,8)
                if all(flow[e] != inc for e in range(self.m) if C >> e & 1)]

    def canonical_escape(self,flow,inc,edge):
        # Enumerate shortest simple paths; adjacency/edge ordering gives the
        # same deterministic witness as constructor BFS, without its queue logic.
        u,v = self.edges[edge]
        paths = [(u,(u,),())]
        while paths:
            following = []
            for at,visited,es in paths:
                if at == v: return sum(1 << e for e in es+(edge,))
                for w,e in self.adj[at]:
                    if e != edge and flow[e] != inc and w not in visited:
                        following.append((w,visited+(w,),es+(e,)))
            paths = following
        raise AssertionError('Projected flow would have a bridge')

    def cover(self,w):
        f=w['flow']; forms=w['coordinate_functionals']
        transformed = [sum(dot(t,x) << j for j,t in enumerate(forms)) for x in f]
        assert transformed == w['transformed_flow']
        t=w['fourth_coordinate_mask']; assert t in self.cycles
        palette=(4,5,6,15,8)
        decode={a ^ b:(1 << i)|(1 << j) for i,a in enumerate(palette) for j,b in enumerate(palette) if i < j}
        pairs=[decode[x+8*((t >> e)&1)] for e,x in enumerate(transformed)]
        assert pairs == w['cover_pairs']
        assert all(xor(pairs[e] for e in es) == 0 for es in self.incident)
        assert all(pair.bit_count() == 2 for pair in pairs)


def main():
    result = json.loads((HERE/'cut_certificate_transport.json').read_text())
    source = HERE/result['source']['file']; assert hashlib.sha256(source.read_bytes()).hexdigest() == result['source']['sha256']
    graphs = json.loads(source.read_text())['graphs']
    p=Verify(next(g for g in graphs if g['name']=='Petersen'))
    expected=result['petersen_audit']; F=expected['prescribed_first_cycle']; Fmask=p.cycles[F]
    assert Fmask == sum(1 << e for e in list(range(5))+list(range(10,15)))
    total = 0
    for y in range(len(p.cycles)):
        for z in p.feasible(F,y):
            total += 1
            assert Fmask & ~(p.cycles[y] & p.cycles[z]) not in p.restrictions[F]
    assert total == expected['nowhere_zero_flows_with_prescribed_first'] == 960
    records,escapes=[],[]; flags=cert_count=moves=fixed_count=0; dims=Counter()
    for y in range(1,len(p.cycles)):
        if y == F or y > y ^ F: continue
        zs=p.feasible(F,y)
        if not zs: continue
        flags += 1; fl=p.flag(F,y); dims[fl['dual_dimension']] += 1
        certs=p.certificates(F,y); cert_count += len(certs)
        assert len(certs) == 1 << (fl['dual_dimension']-2)
        flow=p.flow(F,y,zs[0])
        for code,C,inc in p.legal_moves(flow):
            after,fixed=p.check_move(flow,C,inc); moves += 1; fixed_count += fixed
            nf,ny=F ^ (code if inc & 4 else 0),y ^ (code if inc & 2 else 0)
            for w in certs:
                valid=p.valid(p.cycles[nf],p.cycles[ny],w)
                prediction=not (inc & 6) or not (C & (w['cut_A'] | w['cut_X']))
                assert valid == prediction
                records.append([F,y,zs[0],w['A'],w['X'],code,inc,int(valid)])
        for w in certs:
            boundary=w['cut_A']|w['cut_X']; edge=(boundary & -boundary).bit_length()-1
            for inc in (2,3):
                C=p.canonical_escape(flow,inc,edge); code=p.cycles.index(C)
                p.check_move(flow,C,inc)
                assert not p.valid(Fmask,p.cycles[y ^ code],w)
                assert p.flag(F,y ^ code)['completions'] == 0
                escapes.append([F,y,zs[0],w['A'],w['X'],inc,edge,code])
    rebuilt={'prescribed_first_cycle':F,'feasible_flags_mod_y_plus_F':flags,
             'nowhere_zero_flows_with_prescribed_first':total,'completable_flows_with_prescribed_first':0,
             'dual_dimension_histogram':[list(x) for x in sorted(dims.items())],'normalized_certificate_count':cert_count,
             'representative_flow_legal_moves':moves,'certificate_move_checks':len(records),
             'surviving_certificate_move_pairs':sum(row[-1] for row in records),
             'certificate_move_records_sha256':digest(records),'constructed_single_certificate_escapes':len(escapes),
             'escape_records_sha256':digest(escapes),'fixed_component_charge_updates':fixed_count}
    assert rebuilt == expected
    w=result['petersen_turnover']; before=p.flow(**w['initial_coordinates']); final=p.flow(**w['final_coordinates'])
    assert w['initial_coordinates']['F'] == w['final_coordinates']['F'] == F
    C=sum(1 << e for e in w['circuit_edges']); assert C == p.cycles[w['circuit_code']]
    after,_=p.check_move(before,C,w['increment']); assert after == final
    for side,flow in (('initial',before),('final',final)):
        coordinates=w[side+'_coordinates']; y=coordinates['y']
        assert p.certificates(F,y) == w[side+'_certificates']
        assert p.local_blockers(F,y) == w[side+'_local_blockers']
        assert p.normal_record(tuple(flow)) == w[side+'_normals']
        # Verify the selected Gaussian certificate too, without calling its constructor.
        fl=w[side+'_flag']; assert all(fl[k] == v for k,v in p.flag(F,y).items())
        q=fl['obstruction']; assert p.valid(Fmask,p.cycles[y],q)
        assert q['cut_A'] == p.cut(q['A']) and q['cut_X'] == p.cut(q['X'])
        assert q['shared_cut'] == p.cut(q['A']) & p.cycles[y]
        assert q['forced_odd_cut'] == p.cut(q['X']) & ~(Fmask | p.cycles[y])
    assert len(w['initial_certificates']) == 1 and len(w['final_certificates']) == 2
    assert len(w['initial_local_blockers']) == 1 and not w['final_local_blockers']
    assert all(not p.valid(Fmask,p.cycles[w['final_coordinates']['y']],q) for q in w['initial_certificates'])
    p.cover(w['cover_using_another_first_coordinate'])
    assert w['cover_using_another_first_coordinate']['flow'] == after
    print('Petersen: 960 fixed-F flows reject completion; all 10,660 certificate/move pairs and 190 constructed escapes verified.',flush=True)
    g=next(g for g in graphs if g['name']=='Snark20_0'); j=Verify(g)
    repair=g['hard_flow_repair']; flows=[repair['initial_flow']]+[m['flow_after'] for m in repair['moves']]
    assert [j.normal_record(tuple(flow)) for flow in flows] == result['flower_path']
    moves=fixed=0
    for code,C,inc in j.legal_moves(flows[0]):
        after,checks=j.check_move(flows[0],C,inc); moves += 1; fixed += checks
        assert not j.normal_record(tuple(after))['successful_firsts']
    assert {'initial_legal_moves':moves,'fixed_component_charge_updates':fixed} == result['flower_move_audit']
    for before,move in zip(flows,repair['moves']):
        C=sum(1 << e for e in move['edges']); after,_=j.check_move(before,C,move['increment'])
        assert after == move['flow_after']
    print('J5: all 610 initial circuit moves checked; saved repair has defects (4,38), (4,38), (0,22).')
    print('Vertex-normal charges agree with independent fourth-cycle restrictions, including all audited move endpoints.')
    print('Complete paired-cut replacement: one normalized certificate disappears; two new ones appear.')


if __name__ == '__main__':
    main()
