// Independent exhaustive check: enumerate actual closed pair words, eliminate
// candidate charges directly, and find matchings crossing every dangerous cut.
// No constructor code is included. C++17 standard library only.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;
using Word = array<int, 10>;
const vector<int> auxiliary = {6, 10, 12, 18, 20, 24}, distinguished = {3, 5, 9, 17};
struct Case { int marked, odd; };

bool no_charge(const Word& word, const Case& profile) {
    uint32_t available = 0;
    for (int h = 0; h < 32; ++h)
        if (!__builtin_parity(unsigned(h)) && (h & 1) == (profile.odd & 1))
            available |= uint32_t(1) << h;
    int at = 0;
    for (int i = 0; i < 10; ++i) {
        if (profile.marked >> i & 1) available &= ~(uint32_t(1) << (30 ^ at));
        at ^= word[i];
    }
    if (at) abort();
    return available == 0;
}

// All subsets admitting a nonescaping perfect matching, built by adding an
// edge to a smaller matched subset. This differs from the constructor's DFS.
bool forcing(Word word, int swap, const Case& profile) {
    vector<int> active;
    for (int i = 0; i < 10; ++i)
        if (__builtin_popcount(unsigned(word[i] & swap)) == 1) active.push_back(i);
    int n = active.size();
    vector<pair<int, int>> allowed;
    for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) {
        word[active[i]] ^= swap; word[active[j]] ^= swap;
        if (no_charge(word, profile)) allowed.emplace_back(i, j);
        word[active[i]] ^= swap; word[active[j]] ^= swap;
    }
    vector<char> reached(1 << n);
    reached[0] = 1;
    for (int mask = 0; mask < (1 << n); ++mask) if (reached[mask])
        for (auto [i, j] : allowed) if (!(mask >> i & 1) && !(mask >> j & 1))
            reached[mask | (1 << i) | (1 << j)] = 1;
    return !reached.back();
}

bool crossing_matching(int unmatched, const vector<int>& dangerous) {
    if (dangerous.empty()) return true; // Any pairing completes the remainder.
    if (!unmatched) return false;
    int i = __builtin_ctz(unsigned(unmatched));
    int rest = unmatched ^ (1 << i);
    for (int j = i + 1; j < 10; ++j) if (rest >> j & 1) {
        vector<int> remaining;
        for (int cut : dangerous) if (!(((cut >> i) ^ (cut >> j)) & 1)) remaining.push_back(cut);
        if (crossing_matching(rest ^ (1 << j), remaining)) return true;
    }
    return false;
}

struct Audit {
    Case profile;
    long long total = 0, bad_count = 0;
    array<long long, 7> histogram{};
    unordered_map<uint64_t, vector<int>> bad_orbits;
    vector<int> alphabets[10];

    explicit Audit(Case p) : profile(p) {
        for (int i = 0; i < 10; ++i)
            alphabets[i] = (((p.odd >> i) ^ (p.odd >> ((i + 1) % 10))) & 1) ? distinguished : auxiliary;
    }

    void accept(const Word& word) {
        ++total;
        if (!no_charge(word, profile)) return;
        ++bad_count;
        uint64_t key = 0;
        int assignment = 0;
        for (int i = 0; i < 10; ++i) {
            int r = word[i];
            if (__builtin_popcount(unsigned(r & 6)) == 1) {
                if ((r ^ 6) < r) { assignment |= 1 << i; r ^= 6; }
            }
            key |= uint64_t(r) << (5 * i);
        }
        bad_orbits[key].push_back(assignment);
        int count = 0;
        for (int swap : auxiliary) count += forcing(word, swap, profile);
        ++histogram[count];
        if (!count) { cerr << "Escape failed independently\n"; exit(2); }
    }

    void visit(int i, int sum, Word& word) {
        if (i == 9) {
            if (find(alphabets[9].begin(), alphabets[9].end(), sum) != alphabets[9].end()) {
                word[9] = sum;
                accept(word);
            }
            return;
        }
        for (int r : alphabets[i]) { word[i] = r; visit(i + 1, sum ^ r, word); }
    }

    long long protection() const {
        long long good = 0;
        for (const auto& entry : bad_orbits) {
            uint64_t encoded = entry.first;
            vector<int> bad = entry.second;
            sort(bad.begin(), bad.end());
            if (adjacent_find(bad.begin(), bad.end()) != bad.end()) abort();
            Word key{};
            int active = 0, sum = 0;
            for (int i = 0; i < 10; ++i) {
                key[i] = (encoded >> (5 * i)) & 31;
                sum ^= key[i];
                if (__builtin_popcount(unsigned(key[i] & 6)) == 1) active |= 1 << i;
            }
            for (int bits = 0; bits < 1024; ++bits) {
                if (bits & ~active) continue;
                if (sum ^ (__builtin_parity(unsigned(bits)) ? 6 : 0)) continue;
                if (binary_search(bad.begin(), bad.end(), bits)) continue;
                vector<int> dangerous;
                for (int b : bad) dangerous.push_back(bits ^ b);
                if (!crossing_matching(active, dangerous)) {
                    cerr << "Protection failed independently\n"; exit(3);
                }
                ++good;
            }
        }
        return good;
    }
};

int main() {
    vector<Case> profiles;
    for (int missing = 0; missing <= 2; ++missing) {
        if (!missing) profiles.push_back({1023, 0});
        else if (missing == 1) for (int odd : {0, 1}) profiles.push_back({1022, odd});
        else for (int d = 1; d <= 5; ++d)
            for (int odd : {0, 1, 1 + (1 << d)}) profiles.push_back({1022 - (1 << d), odd});
    }
    for (auto p : profiles) {
        Audit audit(p);
        Word word{};
        audit.visit(0, 0, word);
        long long good = audit.protection();
        cout << p.marked << ' ' << p.odd << ' ' << audit.total << ' ' << audit.bad_count
             << ' ' << audit.bad_orbits.size() << ' ' << good;
        for (auto n : audit.histogram) cout << ' ' << n;
        cout << endl;
    }
}
