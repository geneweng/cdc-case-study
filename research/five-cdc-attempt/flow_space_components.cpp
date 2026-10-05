// Enumerate full-support subspaces, then join their coordinate fibers.
// Input: n m r k, edges, and a binary cycle basis. Compile with assertions.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <unordered_map>
#include <vector>

using Mask = uint64_t;
using Rows = std::array<unsigned, 3>;
struct DSU {
    std::vector<int> parent;
    int add() { int i = parent.size(); parent.push_back(i); return i; }
    int root(int v) { return parent[v] == v ? v : parent[v] = root(parent[v]); }
    void join(int a, int b) {
        a = root(a); b = root(b);
        if (a != b) parent[std::max(a,b)] = std::min(a,b);
    }
};

int n, m, r, dimension;
Mask full;
std::vector<std::pair<int,int>> edges;
std::vector<Mask> cycles;
std::vector<std::vector<Mask>> cuts;

// The smallest independent nonzero vectors give a unique subspace key.
Mask key(Rows rows, int rank) {
    std::vector<unsigned> points;
    for (int i = 1; i < (1 << rank); ++i) {
        unsigned x = 0;
        for (int j = 0; j < rank; ++j) if (i >> j & 1) x ^= rows[j];
        points.push_back(x);
    }
    std::sort(points.begin(), points.end());
    Mask result = points[0];
    if (rank >= 2) result |= Mask(points[1]) << 16;
    if (rank == 3) result |= Mask(points[3]) << 32;
    return result;
}
Rows unpack(Mask value) {
    return {unsigned(value & 65535), unsigned(value >> 16 & 65535), unsigned(value >> 32)};
}

bool successful(Rows rows) {
    if (dimension == 2) return true;
    Mask color[8] = {};
    for (unsigned c = 1; c < 8; ++c) {
        color[c] = full;
        for (int j = 0; j < 3; ++j)
            color[c] &= c >> j & 1 ? cycles[rows[j]] : ~cycles[rows[j]];
    }
    for (unsigned normal = 1; normal < 8; ++normal) {
        unsigned support = 0;
        for (int j = 0; j < 3; ++j) if (normal >> j & 1) support ^= rows[j];
        bool good = true;
        for (Mask cut : cuts[support]) {
            if (__builtin_parityll(cut & color[normal & -normal])) { good = false; break; }
        }
        if (good) return true;
    }
    return false;
}

struct Fiber { std::vector<int> states; };
struct State { Mask key; bool good; std::vector<int> fibers; };
std::vector<State> states;
std::vector<Fiber> fibers;
std::unordered_map<Mask,int> fiber_index;
DSU components;
uint64_t enumerated = 0, lower_full = 0;

void add_subspace(Rows rows, int rank) {
    Mask covered = 0;
    for (int j = 0; j < rank; ++j) covered |= cycles[rows[j]];
    if (rank != dimension) { lower_full += covered == full; return; }
    ++enumerated;
    if (covered != full) return;
    Mask state_key = key(rows, rank);
    rows = unpack(state_key);
    int at = components.add();
    states.push_back({state_key, successful(rows), {}});
    std::vector<Mask> keys;
    if (dimension == 2) {
        keys = {rows[0], rows[1], rows[0] ^ rows[1]};
    } else {
        unsigned points[8] = {};
        for (int i = 1; i < 8; ++i)
            for (int j = 0; j < 3; ++j) if (i >> j & 1) points[i] ^= rows[j];
        for (int i = 1; i < 8; ++i)
            for (int j = i+1; j < 8; ++j)
                if ((i ^ j) > j) keys.push_back(key({points[i], points[j], 0}, 2));
    }
    for (Mask fiber_key : keys) {
        auto found = fiber_index.find(fiber_key);
        int fi;
        if (found == fiber_index.end()) {
            fi = fibers.size(); fiber_index[fiber_key] = fi; fibers.push_back({{}});
        } else fi = found->second;
        auto &members = fibers[fi].states;
        if (!members.empty()) components.join(at, members[0]);
        members.push_back(at);
        states.back().fibers.push_back(fi);
    }
}

void enumerate(std::vector<int> pivots, int start, int rank) {
    if (int(pivots.size()) < rank) {
        for (int p = start; p < r; ++p) {
            pivots.push_back(p); enumerate(pivots, p+1, rank); pivots.pop_back();
        }
        return;
    }
    Rows rows{};
    std::vector<std::pair<int,int>> slots;
    for (int i = 0; i < rank; ++i) {
        rows[i] = 1u << pivots[i];
        for (int j = pivots[i]+1; j < r; ++j)
            if (std::find(pivots.begin(), pivots.end(), j) == pivots.end()) slots.push_back({i,j});
    }
    assert(slots.size() < 63);
    for (Mask assignment = 0; assignment < (Mask(1) << slots.size()); ++assignment) {
        if (assignment) {
            auto [row,col] = slots[__builtin_ctzll(assignment)]; rows[row] ^= 1u << col;
        }
        add_subspace(rows, rank);
    }
}

int main(int argc, char **argv) {
    assert(argc == 2);
    std::cin >> n >> m >> r >> dimension;
    assert(std::cin && n > 0 && m < 64 && r <= 15 && (dimension == 2 || dimension == 3));
    full = (Mask(1) << m)-1;
    for (int e = 0; e < m; ++e) { int u,v; std::cin >> u >> v; edges.push_back({u,v}); }
    cycles = {0};
    for (int i = 0; i < r; ++i) {
        Mask b; std::cin >> b;
        int count = cycles.size();
        for (int j = 0; j < count; ++j) cycles.push_back(cycles[j] ^ b);
    }
    cuts.resize(cycles.size());
    for (unsigned code = 0; code < cycles.size(); ++code) {
        DSU d;
        for (int v = 0; v < n; ++v) d.add();
        for (int e = 0; e < m; ++e) if (!(cycles[code] >> e & 1)) d.join(edges[e].first, edges[e].second);
        std::vector<Mask> boundary(n);
        for (int e = 0; e < m; ++e) {
            int u = d.root(edges[e].first), v = d.root(edges[e].second);
            if (u != v) { boundary[u] ^= Mask(1) << e; boundary[v] ^= Mask(1) << e; }
        }
        for (Mask b : boundary) if (b) cuts[code].push_back(b);
    }
    for (int rank = 1; rank <= dimension; ++rank) enumerate({}, 0, rank);
    assert(lower_full == 0);
    std::vector<int> distance(states.size(), -1);
    std::queue<int> queue;
    for (int i = 0; i < int(states.size()); ++i) if (states[i].good) { distance[i] = 0; queue.push(i); }
    std::vector<bool> expanded(fibers.size());
    while (!queue.empty()) {
        int at = queue.front(); queue.pop();
        for (int fi : states[at].fibers) if (!expanded[fi]) {
            expanded[fi] = true;
            for (int next : fibers[fi].states) if (distance[next] < 0) {
                distance[next] = distance[at]+1; queue.push(next);
            }
        }
    }
    std::map<int,std::array<uint64_t,3>> summaries;
    std::map<int,uint64_t> histogram, sizes;
    for (int i = 0; i < int(states.size()); ++i) {
        auto &c = summaries[components.root(i)];
        ++c[0]; c[1] += states[i].good;
        if (!c[2] || states[i].key < c[2]) c[2] = states[i].key;
        ++histogram[distance[i]];
    }
    for (auto &fiber : fibers) ++sizes[fiber.states.size()];
    std::vector<std::array<Mask,3>> records;
    for (int i = 0; i < int(states.size()); ++i)
        records.push_back({states[i].key, summaries[components.root(i)][2], Mask(distance[i]+1)});
    std::sort(records.begin(), records.end());
    std::ofstream output(argv[1], std::ios::binary);
    for (auto record : records) for (Mask x : record)
        for (int b = 0; b < 8; ++b) output.put(char(x >> (8*b) & 255));
    output.close();
    std::cout << "{\"subspaces_enumerated\":" << enumerated << ",\"full_support_spaces\":" << states.size()
              << ",\"fibers\":" << fibers.size() << ",\"components\":[";
    bool comma = false;
    for (auto [root,c] : summaries) {
        if (comma) std::cout << ','; comma = true;
        std::cout << '[' << c[0] << ',' << c[1] << ',' << c[2] << ']';
    }
    std::cout << "],\"fiber_distance_histogram\":["; comma = false;
    for (auto [d,count] : histogram) {
        if (comma) std::cout << ','; comma = true; std::cout << '[' << d << ',' << count << ']';
    }
    std::cout << "],\"fiber_size_histogram\":["; comma = false;
    for (auto [d,count] : sizes) {
        if (comma) std::cout << ','; comma = true; std::cout << '[' << d << ',' << count << ']';
    }
    std::cout << "]}\n";
}
