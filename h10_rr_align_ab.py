"""判据 3 对齐：合并方案 AB，按 `H10_判据3对齐_合并方案AB_测前写定.md` 执行（算法、检验、通过规则都在该文件写定）。

    粗定位：方案 A 的常数滞后搜索给初值 → 每条通知 ±600 ms 时间窗限定「末拍结束峰」候选
    精配  ：逐通知 Viterbi，节点代价 = RR 数值差（每拍封顶 50 ms），转移代价 = 拍序不连续罚 60
    细化  ：用配得好的通知估局部滞后（±30 s 中位），重划时间窗，共两轮
    区分力：到达时刻整体平移 ±20/40/60 s 也能过判据 3 → 「无法判定」，不冒充「通过」

用法：python h10_rr_align_ab.py
输出：诊断输出/H10_判据3对齐_合并方案AB_结果.md、_合成明细.csv
verdict() 供 h10_rpeak / V2 起的判据 3 调用。
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from h10_rr_align import (LOGS, OUT, REAL, REAL_NAME, crit3, load_real, lowvar_beats,  # noqa: E402,F401
                          make_notes, pick_positions, real_key, rr_round)

P_GRID = np.arange(-1000.0, 3000.0 + 1, 10.0)     # 粗定位常数滞后，ms
MIN_PAIRS = 20
W = 600.0                                          # 时间窗半宽，ms
CAP = 50.0                                         # 每拍 RR 差封顶，ms
DIST_W = 4.0                                       # 偏离窗中心的代价：每 600 ms 记 4
JUMP = 60.0                                        # 拍序不连续的转移代价
REFINE_HALF = 30000.0                              # 局部滞后中位的半窗，ms
GOOD = 16.0
SHIFTS = (-60, -40, -20, 20, 40, 60)               # 区分力自检的平移，s

# 合成用滞后参数（d0 ms, 漂移 ms/min, σ_j ms, 相邻自相关 ρ），取自 诊断输出/H10_通知滞后实测.md
LAGS = [(1789.0, -9.8, 207.0, 0.00), (2002.0, 39.3, 179.0, 0.58),
        (2083.0, -1.0, 93.0, 0.53), (1892.0, 38.2, 419.0, 0.70)]
SEEDS = 60


# ---------------- 算法 ----------------
def _note_spans(notes):
    n = len(notes["a"])
    idx = np.arange(n)
    return np.searchsorted(notes["ni"], idx, "left"), np.searchsorted(notes["ni"], idx, "right")


def coarse(T, iv, cov, notes):
    """第 1 步：常数滞后 p（方案 A 的配对方式）"""
    a, rr, ni, m = notes["a"], notes["rr"], notes["ni"], notes["m"]
    best = None
    for p in P_GRID:
        cut = a - p
        ok_n = (cut >= cov[0]) & (cut <= cov[1])
        j = np.searchsorted(T, cut, side="right") - 1
        e = j[ni] - m - 1
        v = ok_n[ni] & (e >= 0)
        if v.sum() < MIN_PAIRS:
            continue
        med = np.median(np.abs(rr[v] - iv[e[v]]))
        if best is None or med < best[0]:
            best = (med, p)
    return None if best is None else best[1]


def viterbi(T, iv, cov, notes, dhat, spans):
    """第 2–3 步。返回路径 [(通知 i, 末拍结束峰 k)]，按通知顺序"""
    a, rr = notes["a"], notes["rr"]
    st, en = spans
    nT = len(T)
    c = a - dhat
    path, seg = [], []                 # seg: [(i, ks, node, back)]

    def flush():
        if not seg:
            return
        j = int(np.argmin(seg[-1][2]))
        out = []
        for i, ks, _, back in reversed(seg):
            out.append((i, int(ks[j])))
            j = back[j] if back is not None else 0
        path.extend(reversed(out))
        seg.clear()

    for i in range(len(a)):
        K = en[i] - st[i]
        if K == 0:
            continue                   # 空通知不占拍，不断链
        ci = c[i]
        if not (cov[0] <= ci <= cov[1]):
            flush()
            continue
        lo = np.searchsorted(T, ci - W, "right") - 1
        hi = np.searchsorted(T, ci + W, "right") - 1
        ks = np.arange(max(lo, K), min(hi, nT - 1) + 1)
        if len(ks) == 0:
            flush()
            continue
        r = rr[st[i]:en[i]]
        node = np.empty(len(ks))
        for q, k in enumerate(ks):
            e = k - K + np.arange(K)
            cost = np.minimum(np.abs(r - iv[e]), CAP).sum()
            t0, t1 = T[k], (T[k + 1] if k + 1 < nT else np.inf)
            dist = t0 - ci if ci < t0 else (ci - t1 if ci >= t1 else 0.0)
            node[q] = cost + DIST_W * dist / W
        if not seg:
            seg.append((i, ks, node, None))
            continue
        _, pks, pacc, _ = seg[-1]
        acc, back = np.empty(len(ks)), np.empty(len(ks), int)
        for q, k in enumerate(ks):
            tr = pacc + np.where(pks == k - K, 0.0, JUMP)
            b = int(np.argmin(tr))
            acc[q], back[q] = node[q] + tr[b], b
        seg.append((i, ks, acc, back))
    flush()
    return path


def _pairs(path, notes, spans, iv):
    st, en = spans
    H, E = [], []
    for i, k in path:
        K = en[i] - st[i]
        H += list(range(st[i], en[i]))
        E += list(range(k - K, k))
    H, E = np.asarray(H, int), np.asarray(E, int)
    return H, E, notes["rr"][H] - iv[E]


def refine(T, iv, notes, spans, path, dhat):
    """第 4 步：配得好的通知的隐含滞后，±30 s 中位"""
    a, rr = notes["a"], notes["rr"]
    st, en = spans
    ta, lag = [], []
    for i, k in path:
        K = en[i] - st[i]
        if k + 1 >= len(T):
            continue
        if np.all(np.abs(rr[st[i]:en[i]] - iv[k - K:k]) <= GOOD):
            ta.append(a[i]); lag.append(a[i] - (T[k] + T[k + 1]) / 2)
    if not ta:
        return dhat
    ta, lag = np.asarray(ta), np.asarray(lag)
    out = dhat.copy()
    lo = np.searchsorted(ta, a - REFINE_HALF, "left")
    hi = np.searchsorted(ta, a + REFINE_HALF, "right")
    for i in range(len(a)):
        if hi[i] > lo[i]:
            out[i] = np.median(lag[lo[i]:hi[i]])
    return out


def align_AB(T, iv, cov, notes):
    p = coarse(T, iv, cov, notes)
    if p is None:
        return None
    spans = _note_spans(notes)
    dhat = np.full(len(notes["a"]), p)
    for _ in range(2):
        path = viterbi(T, iv, cov, notes, dhat, spans)
        dhat = refine(T, iv, notes, spans, path, dhat)
    path = viterbi(T, iv, cov, notes, dhat, spans)
    h, e, dd = _pairs(path, notes, spans, iv)
    return dict(p=float(p), h=h, e=e, dd=dd, dhat=dhat)


def verdict(T, iv, cov, notes):
    """第 5–6 步。返回 dict(out=通过/不通过/无法判定, res, c3, shift_pass=[通过的平移 s])"""
    res = align_AB(T, iv, cov, notes)
    c3 = crit3(res["dd"]) if res is not None else (False, float("nan"), float("nan"))
    if not c3[0]:
        return dict(out="不通过", res=res, c3=c3, shift_pass=[])
    hits = []
    for s in SHIFTS:
        n2 = dict(notes); n2["a"] = notes["a"] + s * 1000.0
        r2 = align_AB(T, iv, cov, n2)
        if r2 is not None and crit3(r2["dd"])[0]:
            hits.append(s)
    return dict(out="无法判定" if hits else "通过", res=res, c3=c3, shift_pass=hits)


# ---------------- 合成数据（浮动滞后） ----------------
def float_notes(hb, hid, rng, lag, t_end):
    d0, slope, sg, rho = lag
    a0 = hb[0] - rng.uniform(0, 1000)
    a = [a0]
    while a[-1] < t_end + d0 + 3000:
        a.append(a[-1] + rng.uniform(920, 1080))
    a = np.asarray(a)
    j = np.empty(len(a))
    j[0] = rng.normal(0, sg)
    z = rng.normal(0, 1, len(a))
    for i in range(1, len(a)):
        j[i] = rho * j[i - 1] + np.sqrt(1 - rho ** 2) * sg * z[i]
    cut = np.maximum.accumulate(a - (d0 + slope / 60000.0 * (a - a0) + j))
    vals = rr_round(np.diff(hb) + rng.normal(0, 1, len(hb) - 1))
    keys = list(zip(hid[:-1], hid[1:]))
    which = np.searchsorted(cut, hb[1:], side="left")
    lists, klists = [[] for _ in a], [[] for _ in a]
    for k, i in enumerate(which):
        if i < len(a):
            lists[i].append(vals[k]); klists[i].append(keys[k])
    return make_notes(a, lists), [kk for kl in klists for kk in kl]


def synth_run(beats_ms, rng, lag, late30):
    """与 h10_rr_align.synth_run 相同的心跳与错误注入，只把通知滞后换成浮动的"""
    b = np.asarray(beats_ms, float)
    b = b - b[0] + 2000.0
    N = len(b)
    ids = np.arange(N)
    start = b[0] + (30000.0 if late30 else 0.0)
    et, eid = b + rng.uniform(-3.85, 3.85, N), ids.copy()
    pos = pick_positions(rng, b, 8, start + 2000)
    extra, miss, merge, split = pos[:3], pos[3:6], pos[6], pos[7]
    keep = np.ones(N, bool); keep[miss] = False
    xt = b[extra - 1] + rng.uniform(0.4, 0.6, 3) * (b[extra] - b[extra - 1])
    et = np.concatenate([et[keep], xt]); eid = np.concatenate([eid[keep], -np.ones(3, int)])
    o = np.argsort(et); et, eid = et[o], eid[o]
    hk = np.ones(N, bool); hk[merge] = False
    ft = b[split - 1] + rng.uniform(0.4, 0.6) * (b[split] - b[split - 1])
    hb = np.concatenate([b[hk], [ft]]); hid = np.concatenate([ids[hk], [-1]])
    o = np.argsort(hb); hb, hid = hb[o], hid[o]
    m = et >= start
    et, eid = et[m], eid[m]
    cov = (start if late30 else b[0] - 400.0, b[-1] + 400.0)
    iv = np.diff(et)
    ekey = {real_key(eid[e], eid[e + 1]): e for e in range(len(iv)) if real_key(eid[e], eid[e + 1])}
    notes, hkeys = float_notes(hb, hid, rng, lag, b[-1])
    truth = {h: ekey[real_key(*k)] for h, k in enumerate(hkeys) if real_key(*k) and real_key(*k) in ekey}
    return et, iv, cov, notes, truth


def correct_rate(res, truth):
    if res is None:
        return 0.0
    got = dict(zip(res["h"].tolist(), res["e"].tolist()))
    return float(np.mean([got.get(h) == e for h, e in truth.items()])) if truth else float("nan")


# ---------------- 主流程 ----------------
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    real = {s: load_real(s) for s in REAL}
    L = ["# 判据 3 对齐：合并方案 AB 检验结果\n",
         "算法、检验、通过规则见 `H10_判据3对齐_合并方案AB_测前写定.md`，本报告只执行不改。实现 `h10_rr_align_ab.py`。\n"]

    # 第 1 组
    sources = [(REAL_NAME[s], s) for s in REAL] + [("低变异", None)]
    rows = []
    for si, (name, s) in enumerate(sources):
        for late in (False, True):
            for seed in range(SEEDS):
                rng = np.random.default_rng([7, si, int(late), seed])
                lag = LAGS[seed % 4]
                beats = real[s]["beats_ms"] if s else lowvar_beats(rng)
                et, iv, cov, notes, truth = synth_run(beats, rng, lag, late)
                v = verdict(et, iv, cov, notes)
                rows.append(dict(src=name, late=late, seed=seed, lag=seed % 4, n_truth=len(truth),
                                 ok=correct_rate(v["res"], truth), out=v["out"], med=v["c3"][1],
                                 shifts=v["shift_pass"]))
        print(f"合成 {name} 完成", flush=True)
    with open(OUT / "H10_判据3对齐_合并方案AB_合成明细.csv", "w", encoding="utf-8-sig") as f:
        f.write("心跳来源,缺前30s,种子,滞后参数组,有真值的RR数,配对正确率,|差|中位_ms,输出,也通过的平移s\n")
        for r in rows:
            f.write(f"{r['src']},{int(r['late'])},{r['seed']},{r['lag']},{r['n_truth']},{r['ok']:.4f},"
                    f"{r['med']:.2f},{r['out']},{' '.join(map(str, r['shifts']))}\n")

    L.append("## 第 1 组 合成数据（600 次；浮动滞后；每次都加 3 多检 + 3 漏检 + 并拍 1 + 劈拍 1）\n")
    L.append("| 心跳来源 | 情形 | 配对正确率 均值 / 最低 | 通过 / 不通过 / 无法判定 |")
    L.append("|---|---|---|---|")
    rule1, rule2 = [], []
    for name, s in sources:
        for late in (False, True, None):
            sub = [r for r in rows if r["src"] == name and (late is None or r["late"] == late)]
            ok = np.array([r["ok"] for r in sub])
            cnt = {k: sum(r["out"] == k for r in sub) for k in ("通过", "不通过", "无法判定")}
            tag = {False: "ECG 全程", True: "ECG 缺前 30 s", None: "**合计**"}[late]
            L.append(f"| {name} | {tag} | {ok.mean()*100:.2f}% / {ok.min()*100:.1f}% | "
                     f"{cnt['通过']} / {cnt['不通过']} / {cnt['无法判定']} |")
            if late is None:
                n = len(sub)
                if s:
                    good = ok.mean() >= 0.95 and ok.min() >= 0.85 and cnt["通过"] / n >= 0.95
                    rule1.append((name, good, ok.mean(), ok.min(), cnt["通过"] / n))
                else:
                    good = ok.mean() >= 0.95 and cnt["不通过"] / n <= 0.05
                    rule2.append((name, good, ok.mean(), cnt["不通过"] / n, cnt["无法判定"] / n))
    L.append("\n按滞后参数组拆开（全部来源合计，配对正确率均值）：" + "；".join(
        f"组 {g}（σ {LAGS[g][2]:.0f} ms）{np.mean([r['ok'] for r in rows if r['lag'] == g])*100:.2f}%"
        for g in range(4)))
    print("第 1 组完成", flush=True)

    # 第 2 组
    L.append("\n## 第 2 组 错配数据（不得输出「通过」）\n")
    fp, nA, detail = 0, 0, []
    for x in REAL:
        for y in REAL:
            if x == y:
                continue
            X, Y = real[x], real[y]
            outs, meds = [], []
            for s in range(0, 61, 10):
                n2 = dict(X["notes"]); n2["a"] = X["notes"]["a"] - X["notes"]["a"][0] + Y["cov"][0] + s * 1000
                v = verdict(Y["T"], Y["iv"], Y["cov"], n2)
                outs.append(v["out"]); meds.append(v["c3"][1])
                fp += v["out"] == "通过"; nA += 1
            detail.append(f"| HR {REAL_NAME[x]} × ECG {REAL_NAME[y]} | {np.nanmin(meds):.1f}–{np.nanmax(meds):.1f} ms | "
                          f"{'、'.join(sorted(set(outs)))} |")
    L.append(f"真实交叉：输出「通过」**{fp}/{nA}**\n")
    L.append("| 组合 | \\|差\\| 中位（7 个平移） | 输出 |\n|---|---|---|")
    L += detail
    lf, lmed, lout = 0, [], []
    for k in range(50):
        rng = np.random.default_rng([99, k])
        b1, b2 = lowvar_beats(rng) + 2000, lowvar_beats(rng) + 2000
        notes, _ = float_notes(b1, np.arange(len(b1)), rng, LAGS[k % 4], b1[-1])
        et = b2 + rng.uniform(-3.85, 3.85, len(b2))
        v = verdict(et, np.diff(et), (b2[0] - 400, b2[-1] + 400), notes)
        lf += v["out"] == "通过"; lmed.append(v["c3"][1]); lout.append(v["out"])
    L.append(f"\n低变异交叉（50 次）：输出「通过」**{lf}/50**、不通过 {lout.count('不通过')}、"
             f"无法判定 {lout.count('无法判定')}（\\|差\\| 中位最低 {np.nanmin(lmed):.1f} ms）\n")
    print("第 2 组完成", flush=True)

    # 第 3 组
    L.append("## 第 3 组 4 份真实记录（否决门：全部须输出「通过」）\n")
    L.append("| 记录 | 粗定位 p | 配对数 | \\|差\\| 中位 | ≤16 ms | 输出 | 也通过的平移 |")
    L.append("|---|---|---|---|---|---|---|")
    real_out = []
    for s in REAL:
        R = real[s]
        v = verdict(R["T"], R["iv"], R["cov"], R["notes"])
        r = v["res"]
        real_out.append(v["out"])
        L.append(f"| {REAL_NAME[s]} | {r['p']:.0f} ms | {len(r['h'])} | {v['c3'][1]:.1f} ms | {v['c3'][2]*100:.1f}% | "
                 f"{v['out']} | {v['shift_pass'] or '无'} |")

    # 规则
    L.append("\n## 按写定规则判定\n")
    ok_all = True
    for name, g, mean, mn, pr in rule1:
        L.append(f"- 规则 1 {name}：均值 {mean*100:.2f}%（≥95%）、最低 {mn*100:.1f}%（≥85%）、"
                 f"通过率 {pr*100:.1f}%（≥95%）→ {'满足' if g else '**不满足**'}")
        ok_all &= g
    for name, g, mean, nr, ur in rule2:
        L.append(f"- 规则 2 {name}：均值 {mean*100:.2f}%（≥95%）、不通过率 {nr*100:.1f}%（≤5%）、"
                 f"无法判定 {ur*100:.1f}%（单列）→ {'满足' if g else '**不满足**'}")
        ok_all &= g
    g3, g4, g5 = fp == 0, lf <= 2, all(o == "通过" for o in real_out)
    L.append(f"- 规则 3 真实交叉「通过」{fp} 次（须 0）→ {'满足' if g3 else '**不满足**'}")
    L.append(f"- 规则 4 低变异交叉「通过」{lf}/50（须 ≤2）→ {'满足' if g4 else '**不满足**'}")
    L.append(f"- 规则 5 真实记录输出 {real_out}（须全部「通过」）→ {'满足' if g5 else '**不满足**'}")
    ok_all &= g3 and g4 and g5
    L.append("\n**" + ("全部满足 → 从 V2 起采用合并方案 AB。" if ok_all
                       else "有规则不满足 → 不采用，停下报告用户，不调参重跑。") + "**")
    (OUT / "H10_判据3对齐_合并方案AB_结果.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
