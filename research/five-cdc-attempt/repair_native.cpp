// Exhaustive circuit-repair check modulo GL(3,2). No general theorem asserted.
// Compile without -DNDEBUG: assertions validate the graph/cycle input.
// Input: n m r, then m endpoint pairs, then r decimal cycle-support masks.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
#include <numeric>
#include <set>
#include <utility>
#include <vector>

using Mask = uint64_t;
using Rows = std::array<unsigned, 3>;
using Supports = std::array<Mask, 3>;

struct DSU {
    std::vector<int> p;
    explicit DSU(int n): p(n) { std::iota(p.begin(), p.end(), 0); }
    int root(int u) { return p[u] == u ? u : p[u] = root(p[u]); }
    void join(int u, int v) { p[root(u)] = root(v); }
};

struct Search {
    int n, m, r;
    Mask full;
    std::vector<std::pair<int,int>> edges;
    std::vector<Mask> supports;
    std::vector<std::vector<Mask>> cuts;
    std::vector<unsigned> circuits;
    uint64_t enumerated[4] = {}, nz[4] = {}, bad = 0, neighbor_checks = 0;
    Rows trap{};
    bool found = false;

    void read() {
        std::cin >> n >> m >> r;
        assert(std::cin && n > 0 && m > 0 && m < 64 && r > 0 && r <= 16);
        assert(2*m == 3*n && r == m-n+1);
        full = (Mask(1) << m) - 1;
        std::vector<int> degree(n);
        DSU connected(n);
        for (int e=0; e<m; ++e) {
            int u, v; std::cin >> u >> v;
            assert(u >= 0 && v >= 0 && u < n && v < n && u != v);
            edges.emplace_back(u,v); ++degree[u]; ++degree[v]; connected.join(u,v);
        }
        for (int v=0; v<n; ++v) { assert(degree[v] == 3); assert(connected.root(v) == connected.root(0)); }
        supports.push_back(0);
        for (int j=0; j<r; ++j) {
            Mask b; std::cin >> b; assert(std::cin && b && !(b & ~full));
            std::vector<int> parity(n);
            for (int e=0; e<m; ++e) if ((b>>e)&1) {
                parity[edges[e].first] ^= 1; parity[edges[e].second] ^= 1;
            }
            for (int p: parity) assert(p == 0);
            size_t count = supports.size();
            for (size_t s=0; s<count; ++s) supports.push_back(supports[s]^b);
        }
        assert(std::set<Mask>(supports.begin(), supports.end()).size() == supports.size());
        cuts.resize(supports.size());
        for (unsigned code=0; code<supports.size(); ++code) {
            Mask mask = supports[code];
            DSU h(n), selected(n);
            int first = -1;
            for (int e=0; e<m; ++e) {
                auto [u,v] = edges[e];
                if ((mask>>e)&1) { selected.join(u,v); first = u; }
                else h.join(u,v);
            }
            std::vector<Mask> boundary(n);
            bool circuit = first >= 0;
            for (int e=0; e<m; ++e) {
                auto [u,v] = edges[e];
                int a=h.root(u), b=h.root(v);
                if (a != b) { boundary[a] ^= Mask(1)<<e; boundary[b] ^= Mask(1)<<e; }
                if (((mask>>e)&1) && selected.root(u) != selected.root(first)) circuit = false;
            }
            for (Mask b: boundary) if (b) cuts[code].push_back(b);
            if (circuit) circuits.push_back(code);
        }
    }

    std::array<int,7> defects(const Rows& rows, const Supports& s) const {
        std::array<int,7> d{};
        std::array<Mask,5> color{};
        color[1]=s[0]&~s[1]&~s[2];
        color[2]=~s[0]&s[1]&~s[2];
        color[4]=~s[0]&~s[1]&s[2];
        for (unsigned l=1; l<8; ++l) {
            unsigned code=0;
            for (unsigned j=0; j<3; ++j) if ((l>>j)&1) code ^= rows[j];
            Mask mark = color[l & -l];
            for (Mask cut: cuts[code]) d[l-1] += __builtin_parityll(cut & mark);
        }
        return d;
    }

    std::pair<int,int> potential(const Rows& rows, const Supports& s) const {
        auto d=defects(rows,s);
        return {*std::min_element(d.begin(),d.end()),std::accumulate(d.begin(),d.end(),0)};
    }

    bool check(const Rows& rows, const Supports& s, int rank) {
        ++enumerated[rank];
        if ((s[0]|s[1]|s[2]) != full) return true;
        ++nz[rank];
        auto value=potential(rows,s);
        if (!value.first) return true;
        assert(rank == 3); ++bad;
        std::array<Mask,8> colors{};
        for (unsigned a=1; a<8; ++a) {
            colors[a]=full;
            for (unsigned j=0; j<3; ++j) colors[a] &= ((a>>j)&1) ? s[j] : ~s[j];
        }
        for (unsigned q: circuits) for (unsigned a=1; a<8; ++a) {
            Mask mask=supports[q];
            if (mask & colors[a]) continue;
            Rows next=rows; Supports next_s=s;
            for (unsigned j=0; j<3; ++j) if ((a>>j)&1) { next[j]^=q; next_s[j]^=mask; }
            ++neighbor_checks;
            if (potential(next,next_s) < value) return true;
        }
        trap=rows; found=true; return false;
    }

    bool pivot_block(const std::vector<int>& pivots) {
        int k=int(pivots.size());
        Rows rows{}; Supports s{};
        std::vector<std::pair<int,int>> slots;
        for (int i=0; i<k; ++i) {
            rows[i]=1u<<pivots[i]; s[i]=supports[rows[i]];
            for (int j=pivots[i]+1; j<r; ++j)
                if (std::find(pivots.begin(),pivots.end(),j)==pivots.end()) slots.emplace_back(i,j);
        }
        assert(slots.size()<63);
        uint64_t total=uint64_t(1)<<slots.size();
        for (uint64_t step=0; step<total; ++step) {
            // Gray order visits every assignment once, changing a single slot.
            if (step) {
                auto [row,col]=slots[__builtin_ctzll(step)];
                rows[row]^=1u<<col; s[row]^=supports[1u<<col];
            }
            if (!check(rows,s,k)) return false;
        }
        return true;
    }

    void run() {
        for (int p=0; p<r; ++p) for (int q=p+1; q<r; ++q)
            if (!pivot_block({p,q})) return;
        for (int p=0; p<r; ++p) for (int q=p+1; q<r; ++q) for (int t=q+1; t<r; ++t)
            if (!pivot_block({p,q,t})) return;
    }

    void write() const {
        std::cout << "{\"vertices\":" << n << ",\"cycle_dimension\":" << r
                  << ",\"circuit_count\":" << circuits.size()
                  << ",\"subspaces_enumerated_by_rank\":{\"2\":" << enumerated[2] << ",\"3\":" << enumerated[3]
                  << "},\"nz_orbits_by_rank\":{\"2\":" << nz[2] << ",\"3\":" << nz[3]
                  << "},\"bad_orbits_checked\":" << bad << ",\"neighbors_examined\":" << neighbor_checks
                  << ",\"exhausted_all_flow_orbits\":" << (found?"false":"true") << ",\"counterexample\":";
        if (!found) std::cout << "null";
        else {
            Supports s={supports[trap[0]],supports[trap[1]],supports[trap[2]]};
            auto d=defects(trap,s);
            std::cout << "{\"rows\":[" << trap[0] << ',' << trap[1] << ',' << trap[2] << "],\"flow\":[";
            for (int e=0; e<m; ++e) {
                if (e) std::cout << ',';
                std::cout << (((s[0]>>e)&1)+2*((s[1]>>e)&1)+4*((s[2]>>e)&1));
            }
            std::cout << "],\"defects\":[";
            for (int i=0; i<7; ++i) { if (i) std::cout << ','; std::cout << d[i]; }
            std::cout << "]}";
        }
        std::cout << "}\n";
    }
};

#ifndef CDC_REPAIR_LIBRARY
int main() { Search search; search.read(); search.run(); search.write(); }
#endif
