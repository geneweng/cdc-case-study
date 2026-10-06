#!/usr/bin/env python3
"""Construct circuit transport checks and a complete certificate-turnover example."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from fiber_cut_obstructions import Analysis, eliminate
from flow_space_components import circuit_components, lift

HERE = Path(__file__).resolve().parent
SOURCE = HERE/'flow_space_components.json'


def digest(rows):
    return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()


def cross(a,b):
    return sum(((((a >> j)&1)*((b >> k)&1)) ^ (((a >> k)&1)*((b >> j)&1))) << i
               for i,j,k in ((0,1,2),(1,2,0),(2,0,1)))


def xor(xs):
    out = 0
    for x in xs: out ^= x
    return out


class Transport(Analysis):
    def __init__(self,g):
        super().__init__(g)
        self.incident = [[e for e,edge in enumerate(self.edges) if v in edge] for v in range(self.n)]
        self.circuits = [(c,s) for c,s in enumerate(self.cycles) if s and len(circuit_components(s,self.n,self.edges)) == 1]
        self.cut_masks = [self.cut(A) for A in range(1 << self.n)] if self.n <= 10 else None

    def flow(self,F,y,z):
        return [4*((self.cycles[F] >> e)&1)+2*((self.cycles[y] >> e)&1)+((self.cycles[z] >> e)&1) for e in range(self.m)]

    def normals(self,flow):
        ns = []
        for es in self.incident:
            assert len(es) == 3 and xor(flow[e] for e in es) == 0
            assert all(flow[e] for e in es)
            ns.append(cross(flow[es[0]],flow[es[1]]))
        return ns

    def normal_record(self,flow):
        ns = self.normals(flow); tests = []
        for ell in range(1,8):
            F = sum(((ell & x).bit_count()%2) << e for e,x in enumerate(flow))
            comps = self.components(self.all ^ F)
            charges = [xor(ns[v] for v in range(self.n) if K >> v & 1) for K in comps]
            assert all(q in (0,ell) for q in charges)
            bad = [K for K,q in zip(comps,charges) if q]
            local = [e for e,(u,v) in enumerate(self.edges) if ns[u] ^ ns[v] == ell]
            tests.append({'first_functional':ell,'components':list(comps),'charges':charges,
                          'bad_components':bad,'bad_isolated_edges':local})
        return {'flow':flow,'vertex_normals':ns,'tests':tests,
                'successful_firsts':[t['first_functional'] for t in tests if not t['bad_components']]}

    def check_normal_update(self,flow,C,increment):
        after = [x ^ increment if C >> e & 1 else x for e,x in enumerate(flow)]
        before_ns,after_ns = self.normals(flow),self.normals(after)
        for v,es in enumerate(self.incident):
            touched = [e for e in es if C >> e & 1]
            assert len(touched) in (0,2)
            want = before_ns[v]
            if touched:
                off = next(e for e in es if e not in touched)
                want ^= cross(increment,flow[off])
            assert want == after_ns[v]
        fixed = 0
        for ell in range(1,8):
            if (ell & increment).bit_count()%2: continue
            F = sum(((ell & x).bit_count()%2) << e for e,x in enumerate(flow))
            for K in self.components(self.all ^ F):
                old = xor(before_ns[v] for v in range(self.n) if K >> v & 1)
                new = xor(after_ns[v] for v in range(self.n) if K >> v & 1)
                crossing = xor(flow[e] for e in range(self.m) if (C & self.cut(K)) >> e & 1)
                assert new == old ^ cross(increment,crossing)
                fixed += 1
        return after,fixed

    def certificate_valid(self,F,y,A,X):
        T = F | y; S = self.all ^ T
        ca,cx = self.cut(A),self.cut(X)
        return not (ca & ~F) and (cx & T) == (ca & y) and (cx & S).bit_count()%2 == 1

    def certificates(self,Fcode,ycode):
        assert self.cut_masks is not None
        F,y = self.cycles[Fcode],self.cycles[ycode]
        out = []
        # A and X exclude vertex 0: quotient by their independent complements.
        for A in range(0,1 << self.n,2):
            if self.cut_masks[A] & ~F: continue
            for X in range(0,1 << self.n,2):
                if X.bit_count()%2 and self.certificate_valid(F,y,A,X):
                    out.append({'A':A,'X':X,'cut_A':self.cut_masks[A],'cut_X':self.cut_masks[X]})
        return out

    def legal_moves(self,flow):
        for code,C in self.circuits:
            present = {flow[e] for e in range(self.m) if C >> e & 1}
            for inc in range(1,8):
                if inc not in present: yield code,C,inc

    def circuit_through(self,flow,increment,edge):
        u,v = self.edges[edge]
        assert flow[edge] != increment
        adj = [[] for _ in range(self.n)]
        for e,(a,b) in enumerate(self.edges):
            if e != edge and flow[e] != increment:
                adj[a].append((b,e)); adj[b].append((a,e))
        parent = {u:None}; queue = [u]
        for a in queue:
            if v in parent: break
            for b,e in adj[a]:
                if b not in parent: parent[b] = (a,e); queue.append(b)
        assert v in parent
        C = 1 << edge
        while v != u:
            v,e = parent[v]; C |= 1 << e
        assert any(mask == C for _,mask in self.circuits)
        return C


def main():
    old = json.loads(SOURCE.read_text())
    p = Transport(next(g for g in old['graphs'] if g['name']=='Petersen'))
    Fmask = sum(1 << e for e in list(range(5))+list(range(10,15)))
    F = p.cycles.index(Fmask)
    records,escapes = [],[]
    flags,certificate_count,moves_count,normal_checks = 0,0,0,0
    dimensions = Counter(); fixed_flow_count = 0
    for y in range(1,len(p.cycles)):
        if y == F or y > y ^ F: continue
        S = p.all & ~(Fmask | p.cycles[y])
        zs = [z for z,s in enumerate(p.cycles) if s & S == S]
        if not zs: continue
        result = p.flag(F,y); assert result['completions'] == 0
        flags += 1; fixed_flow_count += 2*len(zs); dimensions[result['dual_dimension']] += 1
        certs = p.certificates(F,y); certificate_count += len(certs)
        assert len(certs) == 1 << (result['dual_dimension']-2)
        flow = p.flow(F,y,zs[0])
        for code,C,inc in p.legal_moves(flow):
            after,fixed = p.check_normal_update(flow,C,inc); normal_checks += fixed; moves_count += 1
            nf,ny = F ^ (code if inc & 4 else 0),y ^ (code if inc & 2 else 0)
            for w in certs:
                valid = p.certificate_valid(p.cycles[nf],p.cycles[ny],w['A'],w['X'])
                predicted = (inc & 6) == 0 or (C & (w['cut_A'] | w['cut_X'])) == 0
                assert valid == predicted
                records.append([F,y,zs[0],w['A'],w['X'],code,inc,int(valid)])
        for w in certs:
            boundary = w['cut_A'] | w['cut_X']; edge = (boundary & -boundary).bit_length()-1
            for inc in (2,3):
                C = p.circuit_through(flow,inc,edge); code = p.cycles.index(C)
                assert not p.certificate_valid(Fmask,p.cycles[y ^ code],w['A'],w['X'])
                assert p.flag(F,y ^ code)['completions'] == 0
                escapes.append([F,y,zs[0],w['A'],w['X'],inc,edge,code])
    initial = {'F':F,'y':14,'z':16}
    code,inc = 1,2; C = p.cycles[code]
    before = p.flow(**initial)
    after,fixed = p.check_normal_update(before,C,inc)
    final = {'F':F,'y':initial['y'] ^ code,'z':initial['z']}
    assert after == p.flow(**final)
    cert0,cert1 = p.certificates(F,initial['y']),p.certificates(F,final['y'])
    assert len(cert0) == 1 and len(cert1) == 2
    assert all(C & (w['cut_A'] | w['cut_X']) for w in cert0)
    assert not {(w['cut_A'],w['cut_X']) for w in cert0} & {(w['cut_A'],w['cut_X']) for w in cert1}
    turnover = {'initial_coordinates':initial,'final_coordinates':final,'increment':inc,'circuit_code':code,
                'circuit_edges':[e for e in range(p.m) if C >> e & 1],
                'initial_certificates':cert0,'final_certificates':cert1,
                'initial_local_blockers':p.plane(F,initial['y'])['local_blockers'],
                'final_local_blockers':p.plane(F,final['y'])['local_blockers'],
                'initial_flag':p.flag(F,initial['y']),'final_flag':p.flag(F,final['y']),
                'initial_normals':p.normal_record(before),'final_normals':p.normal_record(after),
                'cover_using_another_first_coordinate':lift(after,p.basis)}
    g = next(g for g in old['graphs'] if g['name']=='Snark20_0'); j = Transport(g)
    repair = g['hard_flow_repair']; flows = [repair['initial_flow']]+[m['flow_after'] for m in repair['moves']]
    jrecords = [j.normal_record(flow) for flow in flows]
    jchecks = jfixed = 0
    for code,C,increment in j.legal_moves(flows[0]):
        _,fixed = j.check_normal_update(flows[0],C,increment); jfixed += fixed; jchecks += 1
    for flow,move in zip(flows,repair['moves']):
        C = sum(1 << e for e in move['edges'])
        after,_ = j.check_normal_update(flow,C,move['increment']); assert after == move['flow_after']
    out = {'date':'2026-10-05','source':{'file':SOURCE.name,'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()},
           'scope':'Exact certificate survival and single-certificate escape; replacement obstructs global progress.',
           'petersen_audit':{'prescribed_first_cycle':F,'feasible_flags_mod_y_plus_F':flags,
                             'nowhere_zero_flows_with_prescribed_first':fixed_flow_count,'completable_flows_with_prescribed_first':0,
                             'dual_dimension_histogram':sorted(dimensions.items()),'normalized_certificate_count':certificate_count,
                             'representative_flow_legal_moves':moves_count,'certificate_move_checks':len(records),
                             'surviving_certificate_move_pairs':sum(row[-1] for row in records),
                             'certificate_move_records_sha256':digest(records),'constructed_single_certificate_escapes':len(escapes),
                             'escape_records_sha256':digest(escapes),'fixed_component_charge_updates':normal_checks},
           'petersen_turnover':turnover,
           'flower_path':jrecords,'flower_move_audit':{'initial_legal_moves':jchecks,'fixed_component_charge_updates':jfixed}}
    (HERE/'cut_certificate_transport.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out['petersen_audit'],indent=2))
    print('J5 audit:',out['flower_move_audit'])
    print('J5 bad-component counts:',[[len(t['bad_components']) for t in rec['tests']] for rec in jrecords])


if __name__ == '__main__':
    main()
