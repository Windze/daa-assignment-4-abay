"""Implement algorithm bodies. See docs/guide/CONTRACTS.md; inputs and outputs are dictionaries."""
from collections import deque


def lcs(request):
    """Compare two versions of a sequence while preserving the order of shared characters. Implement lcs according to docs/guide/CONTRACTS.md."""
    a = request["a"]
    b = request["b"]
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return {"length": 0, "sequence": ""}

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    result = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            result.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    result.reverse()
    seq = "".join(result)
    return {"length": len(seq), "sequence": seq}


def merge(request):
    """Plan the cheapest sequence of adjacent block merges when the original order must be preserved. Implement merge according to docs/guide/CONTRACTS.md."""
    sizes = request["sizes"]
    n = len(sizes)
    if n <= 1:
        return {"cost": 0, "plan": []}

    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + sizes[i]

    INF = float("inf")
    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]

    for length in range(2, n + 1):
        for l in range(n - length + 1):
            r = l + length - 1
            dp[l][r] = INF
            cost_lr = prefix[r + 1] - prefix[l]
            for k in range(l, r):
                val = dp[l][k] + dp[k + 1][r] + cost_lr
                if val < dp[l][r]:
                    dp[l][r] = val
                    split[l][r] = k

    plan = []

    def build_plan(l, r):
        if l == r:
            return
        k = split[l][r]
        build_plan(l, k)
        build_plan(k + 1, r)
        plan.append([l, k, r])

    build_plan(0, n - 1)
    return {"cost": dp[0][n - 1], "plan": plan}


def tree(request):
    """Choose a maximum-value set when neighbouring vertices are incompatible and conflicts form a tree. Implement tree according to docs/guide/CONTRACTS.md."""
    n = request["n"]
    weights = request["weights"]
    edges = request["edges"]

    if n == 0:
        return {"weight": 0, "selected": []}

    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    dp_take = [0] * n
    dp_skip = [0] * n
    parent = [-1] * n
    order = []

    visited = [False] * n
    stack = [0]
    visited[0] = True
    while stack:
        v = stack.pop()
        order.append(v)
        for u in adj[v]:
            if not visited[u]:
                visited[u] = True
                parent[u] = v
                stack.append(u)

    for v in reversed(order):
        dp_take[v] = max(0, weights[v])
        dp_skip[v] = 0
        for u in adj[v]:
            if u == parent[v]:
                continue
            dp_take[v] += dp_skip[u]
            dp_skip[v] += max(dp_take[u], dp_skip[u])

    total = max(dp_take[0], dp_skip[0])

    selected = []
    choose = [False] * n
    root_take = dp_take[0] >= dp_skip[0]
    choose[0] = root_take

    for v in order:
        taking_v = choose[v]
        for u in adj[v]:
            if u == parent[v]:
                continue
            if taking_v:
                choose[u] = False
            else:
                choose[u] = dp_take[u] >= dp_skip[u]

    for v in range(n):
        if choose[v] and weights[v] > 0:
            selected.append(v)

    return {"weight": total, "selected": selected}


def naive(request):
    """Establish a simple exact-search baseline against which the other two searches can be checked. Implement naive according to docs/guide/CONTRACTS.md."""
    text = request["text"]
    pattern = request["pattern"]
    n = len(text)
    m = len(pattern)
    positions = []

    if m == 0:
        for i in range(n + 1):
            positions.append(i)
        return {"positions": positions}

    if m > n:
        return {"positions": []}

    for i in range(n - m + 1):
        match = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            positions.append(i)

    return {"positions": positions}


def kmp(request):
    """Reuse information about matched prefixes to avoid restarting the search after every mismatch. Implement kmp according to docs/guide/CONTRACTS.md."""
    text = request["text"]
    pattern = request["pattern"]
    n = len(text)
    m = len(pattern)
    positions = []

    if m == 0:
        return {"positions": list(range(n + 1))}

    if m > n:
        return {"positions": []}

    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and pattern[i] != pattern[k]:
            k = pi[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        pi[i] = k

    q = 0
    for i in range(n):
        while q > 0 and text[i] != pattern[q]:
            q = pi[q - 1]
        if text[i] == pattern[q]:
            q += 1
        if q == m:
            positions.append(i - m + 1)
            q = pi[q - 1]

    return {"positions": positions}


def rk(request):
    """Reject windows with unequal fingerprints and verify every equal-hash candidate. Implement rk according to docs/guide/CONTRACTS.md."""
    text = request["text"]
    pattern = request["pattern"]
    n = len(text)
    m = len(pattern)
    BASE = 31
    MOD = 101
    positions = []

    if m == 0:
        return {"positions": list(range(n + 1))}

    if m > n:
        return {"positions": []}

    ph = 0
    for c in pattern:
        ph = (ph * BASE + ord(c)) % MOD

    high = 1
    for _ in range(m - 1):
        high = (high * BASE) % MOD

    wh = 0
    for i in range(m):
        wh = (wh * BASE + ord(text[i])) % MOD

    for i in range(n - m + 1):
        if wh == ph:
            match = True
            for j in range(m):
                if text[i + j] != pattern[j]:
                    match = False
                    break
            if match:
                positions.append(i)
        if i < n - m:
            wh = (wh - ord(text[i]) * high % MOD + MOD) % MOD
            wh = (wh * BASE + ord(text[i + m])) % MOD

    return {"positions": positions}


def suffix(request):
    """Order the text suffixes and use adjacent common prefixes to find repeated substrings. Implement suffix according to docs/guide/CONTRACTS.md."""
    text = request["text"]
    n = len(text)

    if n == 0:
        return {"sa": [], "lcp": [], "repeated": ""}

    sa = sorted(range(n), key=lambda i: text[i:])

    rank = [0] * n
    for i, s in enumerate(sa):
        rank[s] = i

    k = 1
    while k < n:
        def sort_key(i, _k=k, _rank=rank):
            r1 = _rank[i]
            r2 = _rank[i + _k] if i + _k < n else -1
            return (r1, r2)
        sa = sorted(range(n), key=sort_key)
        new_rank = [0] * n
        new_rank[sa[0]] = 0
        for i in range(1, n):
            prev, cur = sa[i - 1], sa[i]
            pr1, pr2 = rank[prev], rank[prev + k] if prev + k < n else -1
            cr1, cr2 = rank[cur], rank[cur + k] if cur + k < n else -1
            new_rank[cur] = new_rank[prev] if (pr1 == cr1 and pr2 == cr2) else new_rank[prev] + 1
        rank = new_rank
        if rank[sa[-1]] == n - 1:
            break
        k *= 2

    lcp = [0] * n
    inv = [0] * n
    for i in range(n):
        inv[sa[i]] = i

    h = 0
    for i in range(n):
        if inv[i] > 0:
            j = sa[inv[i] - 1]
            while i + h < n and j + h < n and text[i + h] == text[j + h]:
                h += 1
            lcp[inv[i]] = h
            if h > 0:
                h -= 1

    max_lcp = max(lcp)
    repeated = ""
    if max_lcp > 0:
        idx = lcp.index(max_lcp)
        repeated = text[sa[idx]:sa[idx] + max_lcp]

    return {"sa": sa, "lcp": lcp, "repeated": repeated}


def aho(request):
    """Build one dictionary automaton and count its patterns in several independent texts. Implement aho according to docs/guide/CONTRACTS.md."""
    patterns = request["patterns"]
    texts = request["texts"]
    p = len(patterns)
    q = len(texts)

    if q == 0:
        return {"counts": []}

    if p == 0:
        return {"counts": [[] for _ in texts]}

    ALPHA = 95
    BASE_CHAR = 32

    goto = [[-1] * ALPHA]
    fail = [0]
    output = [[]]

    for pid, pat in enumerate(patterns):
        cur = 0
        for ch in pat:
            c = ord(ch) - BASE_CHAR
            if goto[cur][c] == -1:
                goto[cur][c] = len(goto)
                goto.append([-1] * ALPHA)
                fail.append(0)
                output.append([])
            cur = goto[cur][c]
        output[cur].append(pid)

    S = len(goto)
    trans = [[-1] * ALPHA for _ in range(S)]

    bfsq = deque()
    for c in range(ALPHA):
        if goto[0][c] == -1:
            trans[0][c] = 0
        else:
            s = goto[0][c]
            trans[0][c] = s
            fail[s] = 0
            bfsq.append(s)

    while bfsq:
        u = bfsq.popleft()
        for c in range(ALPHA):
            v = goto[u][c]
            if v == -1:
                trans[u][c] = trans[fail[u]][c]
            else:
                trans[u][c] = v
                fail[v] = trans[fail[u]][c]
                bfsq.append(v)

    suffix_link = [0] * S
    for s in range(1, S):
        f = fail[s]
        if output[f]:
            suffix_link[s] = f
        else:
            suffix_link[s] = suffix_link[f]

    counts_result = []
    for text in texts:
        row = [0] * p
        cur = 0
        for ch in text:
            c = ord(ch) - BASE_CHAR
            if 0 <= c < ALPHA:
                cur = trans[cur][c]
            else:
                cur = 0
            tmp = cur
            while tmp != 0:
                for pid in output[tmp]:
                    row[pid] += 1
                tmp = suffix_link[tmp]
            if output[0]:
                for pid in output[0]:
                    row[pid] += 1

        counts_result.append(row)

    return {"counts": counts_result}
