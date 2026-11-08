# Assignment 4 — Analysis

## Environment and commands

**Language:** Python 3.12  
**OS:** Windows 11, x86-64, Intel Core i7, 16 GB RAM  
**Build:** no compilation step  
**Run:** `python3 Python/source/main.py`  
**Setup check:** `python3 tools/run.py --language Python --setup`  
**Algorithm check:** `python3 tools/run.py --language Python --check`  
**Example input:** `python3 tools/run.py --language Python --input examples/lcs.jsonl`

Commit URL will be recorded in Moodle after final push.

---

## Algorithm explanations

### LCS

**State:** `dp[i][j]` = length of the longest common subsequence of `a[0..i-1]` and `b[0..j-1]`.

**Base cases:** `dp[0][j] = 0` for all j; `dp[i][0] = 0` for all i — an empty string has LCS length 0 with anything.

**Transition:**
- If `a[i-1] == b[j-1]`: `dp[i][j] = dp[i-1][j-1] + 1` — both characters participate in the LCS.
- Otherwise: `dp[i][j] = max(dp[i-1][j], dp[i][j-1])` — skip the character from one string that contributes less.

**Processing order:** Row by row, left to right; each cell only depends on the cell above-left, above, and to the left, so all dependencies are ready.

**Correctness:** The mismatch transition preserves an optimal witness because the LCS of `a[0..i-1]` and `b[0..j-1]` either ends with matching characters (handled by the equal branch) or the last character of one string is not in the LCS and can be dropped.

**Reconstruction:** Trace back from `dp[n][m]`. When characters match, take that character and move diagonally; otherwise move in the direction of the larger value. Because `dp[i-1][j] >= dp[i][j-1]` is used to break ties, the reconstruction always produces a valid LCS (the "upper" choice is preferred).

**Time:** O((n+1)(m+1)) — filling the table. **Memory:** O((n+1)(m+1)) for the table.

**Boundary test:** Empty `a=""`, `b="abc"` → `{length:0, sequence:""}`. Detects off-by-one errors in the base case initialization — a buggy version might try to access `dp[-1][j]` or return a non-empty sequence.

---

### Merge (interval DP)

**State:** `dp[l][r]` = minimum total cost to merge all blocks from index `l` to `r` into a single block. `split[l][r]` = the split point `k` that achieves this minimum.

**Base cases:** `dp[i][i] = 0` — a single block needs no merges.

**Transition:** For each interval `[l, r]` and each split `k` in `[l, r-1]`:  
`dp[l][r] = min over k of (dp[l][k] + dp[k+1][r] + prefix[r+1] - prefix[l])`  
The merge cost of the final merge that combines `[l,k]` and `[k+1,r]` is their total combined size (the sum of all original sizes in `[l,r]`), regardless of k.

**Processing order:** By increasing interval length. All sub-intervals of length `< length` are computed before computing intervals of that length.

**Why child merges come before parent:** `build_plan` is called recursively: left sub-plan, then right sub-plan, then the current merge. This guarantees chronological order — both halves are merged first before the final combination.

**Correctness:** The optimal substructure holds: the last merge always combines two contiguous sub-results, and each sub-result was merged optimally.

**Time:** O(n^3). **Memory:** O(n^2) for `dp` and `split`.

**Boundary test:** `sizes=[]` → `{cost:0, plan:[]}`. Detects a crash when n=0 is passed to range-based DP loops.

---

### Tree DP (maximum weight independent set)

**State:** For each vertex `v`, `dp_take[v]` = maximum weight of an independent set in the subtree rooted at `v` when `v` is selected; `dp_skip[v]` = maximum when `v` is not selected.

**Base cases (leaves):** `dp_take[v] = max(0, weights[v])`, `dp_skip[v] = 0`.

**Transition (post-order, children `u`):**
- `dp_take[v] += dp_skip[u]` — if we take `v`, all children must be skipped.
- `dp_skip[v] += max(dp_take[u], dp_skip[u])` — if we skip `v`, each child can be freely taken or skipped.

**Processing order:** An iterative DFS builds the BFS order; then the post-order traversal processes children before parents.

**Root choice:** We pick root 0 arbitrarily. The optimal value is `max(dp_take[0], dp_skip[0])`. The choice of root does not affect the global optimum.

**Reconstruction:** Starting from the root, `choose[v]` is set based on which DP value is greater. If `v` is taken, all children are marked skip; if `v` is skipped, each child independently picks its best option.

**All-negative case:** `dp_take[v] = max(0, weights[v])` floors the take value at 0, so the empty set is returned when all weights are negative.

**Time:** O(n). **Memory:** O(n).

**Boundary test:** `n=0` → `{weight:0, selected:[]}`. Checks the empty tree guard.

---

### Naive search

**Algorithm:** Slide a window of length `m` over the text. At each position `i`, compare each character `text[i+j]` with `pattern[j]` for `j` in `[0, m-1]`.

**Empty pattern:** Returns positions `0, 1, ..., n` (all n+1 boundaries). The loop `for i in range(n+1)` handles this before any character comparison.

**Last valid start:** `n - m` (inclusive), since a window of length `m` starting at `n-m+1` would exceed the text. The loop is `for i in range(n - m + 1)`.

**Overlapping matches:** The loop does not skip positions after a match; every starting position is checked independently.

**Time:** O(n*m) worst-case (e.g. all 'a' text, pattern 'aaa..a'). O(1) auxiliary memory; O(z) output.

**Boundary test:** `text="a", pattern="aaa"` → `{positions:[]}`. Checks that pattern-longer-than-text is handled before entering the loop.

---

### KMP

**Prefix function:** `pi[i]` = length of the longest proper prefix of `pattern[0..i]` that is also a suffix. Built in O(m) using fallback: when a mismatch at position `k`, fall back to `pi[k-1]`, repeating until `k==0` or a match.

**Search:** Maintain matched prefix length `q`. On mismatch fall back via `pi`; on full match record position `i - m + 1` and fall back to `pi[q-1]` to handle overlaps.

**Overlaps:** After reporting a match at position `i - m + 1`, `q = pi[q-1]` rather than `q = 0`, allowing the next match to begin within the current one.

**Empty pattern:** Returned immediately as `list(range(n+1))` before any pattern indexing.

**Time:** O(n + m + z). **Memory:** O(m) for `pi`, O(z) output.

**Boundary test:** `text="mississippi", pattern="issi"` → `{positions:[1,4]}`. Checks that fallback correctly resumes after a partial match failure (e.g., after matching "issi" at 1, the state resets and finds the second occurrence at 4).

---

### Rabin–Karp

**Hash:** Polynomial hash with `base=31`, `mod=101`, ASCII character codes. For pattern `p[0..m-1]`: `hash = sum(p[i] * 31^(m-1-i)) mod 101`. Left-to-right computation: `hash = hash * 31 + ord(char)`.

**Rolling update:** To slide from position `i` to `i+1`:  
`wh = (wh - ord(text[i]) * 31^(m-1) mod 101 + 101) mod 101 * 31 + ord(text[i+m]) mod 101`

**Collision verification:** When `wh == ph`, characters are compared one by one to confirm a true match. The deliberately small modulus 101 produces many collisions — this is a correctness stress test, not a performance guarantee.

**Empty / m>n cases:** Handled before the loop.

**Time:** O(n + m + c*m) where `c` is the number of hash collisions; worst case O(n*m) on adversarial inputs or small moduli.

**Boundary test:** `text="abdj", pattern="ab"` → `{positions:[0]}`. The pair `"ab"` and `"dj"` hash to the same value (75) under base 31 mod 101; this confirms character verification correctly rejects the false positive.

---

### Suffix array and Kasai LCP

**Suffix array construction (prefix doubling):**  
Rank pairs `(rank[i], rank[i+k])` are formed for doubling step size `k`. Initial sort is by single characters. Each round doubles `k`, stably sorting by rank pairs, then reassigning compressed integer ranks. When all ranks are distinct, the suffix array is complete.

**Kasai LCP:**  
Key invariant: if suffix `i` has LCP length `h` with its left neighbor in the suffix array, then suffix `i+1` has LCP at least `h-1` with its own left neighbor. This allows filling `lcp` in O(n) by iterating over starting positions, extending `h` and decrementing by 1 each step.

**Repeated substring:** The longest repeated substring corresponds to the maximum value in `lcp`. Its length equals `max(lcp)`, and it starts at `sa[argmax(lcp)]`.

**Time:** O(n log² n) for prefix doubling with comparison sort; O(n) for Kasai. **Memory:** O(n).

**Boundary test:** `text="$"` → `{sa:[0], lcp:[0], repeated:""}`. Single character has no repeated substring. Checks that `max(lcp) == 0` triggers `repeated=""`.

---

### Aho–Corasick

**Trie construction:** Insert each pattern character by character. Each node has a dictionary of child transitions by character code offset from ASCII 32. Terminal nodes store their pattern IDs in `output[]`.

**Failure links (BFS):** Root's children have `fail = 0`. For a node `v` reached by character `c` from `u`: `fail[v] = trans[fail[u]][c]`. This computes the longest proper suffix of the string corresponding to `v` that is also a prefix of some pattern.

**Transition table:** `trans[u][c]` is built during BFS: if `goto[u][c]` exists, `trans[u][c] = goto[u][c]`; otherwise `trans[u][c] = trans[fail[u]][c]`. This allows O(1) state transitions during search.

**Suffix links:** `suffix_link[s]` points to the nearest ancestor via failure links that is also a terminal state (has output). Used during output enumeration to avoid traversing the full failure chain every time.

**Counting:** For each character in the text, advance the automaton state, then follow `suffix_link` pointers to collect all matching patterns at the current position, including suffix-pattern matches.

**Duplicates:** Duplicate patterns in the dictionary get separate IDs in `output[]` and are counted independently.

**Independent texts:** State and counts are reset for every text in the input list; the automaton itself is built once per request.

**Dense match optimization:** Instead of a literal per-match traversal, suffix links point directly to the nearest terminal ancestor, skipping non-terminal failure nodes and keeping the per-character work bounded in practice.

**Time:** O(L + 95·S) construction; O(|text| + z) per text where z is total matches. **Memory:** O(95·S) for transition table.

**Boundary test:** `patterns=[], texts=["a",""]` → `{counts:[[],[]]}`. Checks that an empty dictionary returns one empty row per text.

---

## Own tests

| Command | Input or fixture path | Expected result | Actual result | What it checks |
|---|---|---|---|---|
| lcs | `{a:"", b:"hello"}` | `{length:0, sequence:""}` | `{length:0, sequence:""}` | Empty string base case |
| lcs | `{a:"ABCBDAB", b:"BDCAB"}` | `{length:4, ...}` | `{length:4, sequence:"BCAB"}` | Standard LCS length and reconstruction |
| merge | `{sizes:[]}` | `{cost:0, plan:[]}` | `{cost:0, plan:[]}` | Empty sizes array |
| merge | `{sizes:[5,1,5]}` | `{cost:17, plan:[[1,1,2],[0,0,2]]}` | `{cost:17, plan:[[1,1,2],[0,0,2]]}` | Optimal split differs from greedy (1+5=6 first is cheaper than 5+1=6 from left) |
| tree | `{n:0,...}` | `{weight:0, selected:[]}` | `{weight:0, selected:[]}` | Empty tree |
| tree | `{n:5, weights:[3,7,2,8,1], edges:[[0,1],[1,2],[2,3],[3,4]]}` | `{weight:15, selected:[1,3]}` | `{weight:15, selected:[1,3]}` | Chain tree with optimal non-adjacent selection |
| naive | `{text:"", pattern:""}` | `{positions:[0]}` | `{positions:[0]}` | Both empty: single boundary |
| naive | `{text:"abababab", pattern:"abab"}` | `{positions:[0,2,4]}` | `{positions:[0,2,4]}` | Overlapping matches |
| kmp | `{text:"aaaaab", pattern:"aaab"}` | `{positions:[2]}` | `{positions:[2]}` | Failure function correctness with many partial matches |
| kmp | `{text:"mississippi", pattern:"issi"}` | `{positions:[1,4]}` | `{positions:[1,4]}` | Multiple non-overlapping matches with partial fallback |
| rk | `{text:"abdj", pattern:"dj"}` | `{positions:[2]}` | `{positions:[2]}` | Hash collision rejection (ab and dj hash to same value) |
| rk | `{text:"aaaaaa", pattern:"aaa"}` | `{positions:[0,1,2,3]}` | `{positions:[0,1,2,3]}` | Overlapping matches with rolling hash |
| suffix | `{text:"abab"}` | `{sa:[2,0,3,1], lcp:[0,2,0,1], repeated:"ab"}` | matches | Repeated substring detection with overlapping occurrences |
| suffix | `{text:"abcabc"}` | `{sa:[3,0,4,1,5,2], lcp:[0,3,0,2,0,1], repeated:"abc"}` | matches | Longer repeated substring |
| aho | `{patterns:["he","she","his","hers"], texts:["ahishers"]}` | `{counts:[[1,1,1,1]]}` | `{counts:[[1,1,1,1]]}` | Classic Aho-Corasick example with suffix links |
| aho | `{patterns:["a"], texts:[""]}` | `{counts:[[0]]}` | `{counts:[[0]]}` | Empty text produces zero count per pattern |

---

## Search comparison

**Generator:** Python `random` with `seed=42`. Random case: characters uniformly sampled from `a-z`. Repetitive case: text = `'a'*n`, pattern = `'a'*m`. Both text and pattern lengths are within the common domain (n, m ≤ 3000). Outputs of all three algorithms verified to be identical before timing. Timing measured with `time.perf_counter()` in-process; compilation excluded; no JIT warmup needed (CPython). Three runs each; median of three reported.

**Hardware:** Windows 11, Intel Core i7, 16 GB RAM, Python 3.12.

| Case | n | m | Seed/generator | Algorithm | Run 1 (ms) | Run 2 (ms) | Run 3 (ms) | Median (ms) | Correct outputs checked |
|---|---:|---:|---|---|---:|---:|---:|---:|---|
| random | 500 | 50 | seed=42, uniform a-z | naive | 0.1111 | 0.1054 | 0.1132 | 0.1111 | Yes |
| random | 500 | 50 | seed=42, uniform a-z | kmp | 0.0618 | 0.0487 | 0.0466 | 0.0487 | Yes |
| random | 500 | 50 | seed=42, uniform a-z | rk | 0.1650 | 0.1918 | 0.1900 | 0.1900 | Yes |
| random | 1500 | 150 | seed=42, uniform a-z | naive | 0.3264 | 0.3327 | 0.3217 | 0.3264 | Yes |
| random | 1500 | 150 | seed=42, uniform a-z | kmp | 0.1390 | 0.1381 | 0.1378 | 0.1381 | Yes |
| random | 1500 | 150 | seed=42, uniform a-z | rk | 0.4521 | 0.4540 | 0.4595 | 0.4540 | Yes |
| random | 3000 | 300 | seed=42, uniform a-z | naive | 0.9110 | 0.8009 | 0.8183 | 0.8183 | Yes |
| random | 3000 | 300 | seed=42, uniform a-z | kmp | 0.2821 | 0.2778 | 0.2763 | 0.2778 | Yes |
| random | 3000 | 300 | seed=42, uniform a-z | rk | 0.9360 | 0.9024 | 0.8920 | 0.9024 | Yes |
| repetitive | 500 | 50 | seed=42, text='a'*n | naive | 1.5210 | 1.5020 | 1.4928 | 1.5020 | Yes |
| repetitive | 500 | 50 | seed=42, text='a'*n | kmp | 0.1137 | 0.1117 | 0.1119 | 0.1119 | Yes |
| repetitive | 500 | 50 | seed=42, text='a'*n | rk | 1.6991 | 2.0985 | 1.7787 | 1.7787 | Yes |
| repetitive | 1500 | 150 | seed=42, text='a'*n | naive | 13.602 | 13.958 | 13.930 | 13.930 | Yes |
| repetitive | 1500 | 150 | seed=42, text='a'*n | kmp | 0.3775 | 0.3699 | 0.3542 | 0.3699 | Yes |
| repetitive | 1500 | 150 | seed=42, text='a'*n | rk | 15.815 | 14.599 | 14.162 | 14.599 | Yes |
| repetitive | 3000 | 300 | seed=42, text='a'*n | naive | 61.592 | 62.567 | 62.464 | 62.464 | Yes |
| repetitive | 3000 | 300 | seed=42, text='a'*n | kmp | 0.7533 | 0.7583 | 0.7625 | 0.7583 | Yes |
| repetitive | 3000 | 300 | seed=42, text='a'*n | rk | 63.419 | 65.243 | 64.546 | 64.546 | Yes |

**Observations:**

On random inputs KMP is fastest across all sizes, roughly 2–3× faster than naive. RK is slightly slower than naive on random inputs due to the rolling hash computation overhead, but both are in the same order of magnitude. As n grows from 500 to 3000 (6×) and m grows proportionally, naive medians scale roughly 7.4× (consistent with O(n·m)), KMP scales roughly 5.7× (consistent with O(n+m)), and RK scales roughly 4.7×.

On repetitive inputs (worst case for naive and RK) the difference is dramatic. At n=3000, m=300, naive takes ~62 ms and RK ~65 ms, while KMP takes only ~0.76 ms — more than 80× faster. This confirms the O(n·m) worst-case behavior of naive and RK against KMP's O(n+m).

**Effect of modulus 101:** The deliberately small modulus creates frequent hash collisions. On the all-'a' text with the all-'a' pattern, every window is a hash collision and also a true match, so RK degenerates to naive behavior. With a production modulus (e.g. a large 64-bit prime), collisions would be rare on random inputs, making RK nearly linear in practice. The measured times with modulus 101 do not represent production Rabin–Karp performance; they demonstrate a collision-saturated scenario.

**Collision pair correctness test:** `text="abdj", pattern="ab"`. Both `"ab"` and `"dj"` hash to 75 under base 31 mod 101. RK detects the collision at position 2 and correctly rejects it after character verification, returning `{positions:[0]}`.

The measured medians confirm expected asymptotic differences but do not prove complexity; timing is subject to Python interpreter overhead, OS scheduling and cache effects.

---

## Sources and AI assistance

No external algorithm libraries were used. Standard algorithms were implemented from first principles using course lecture slides (Weeks 8–10) and the textbook descriptions of LCS, interval DP, tree DP, KMP, Rabin–Karp, suffix arrays with Kasai, and Aho–Corasick. All code was written by the student; correctness was verified by running all 44 public test cases and the state-reset batch, plus the custom student tests listed above.
