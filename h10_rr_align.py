"""判据 3 的两个对齐方案与比较，按 `H10_判据3对齐算法_两方案与选择规则_测前写定.md` 执行（方案、检验、选择规则都在该文件写定）。

    A：按 Pi 到达时刻对齐——通知在 a 到达，其最后一个 RR 结束于「Pi 时钟上 ≤ a − p 的最后一个 R 峰」，p 全程一个常数
    B：逐窗对齐——全程搜起始错位，之后每 10 个 HR RR 一窗、在上一窗错位 ±3 内找最佳

用法：python h10_rr_align.py
输出：诊断输出/H10_判据3对齐_两方案比较结果.md、_合成明细.csv
align_A / align_B 供 h10_rpeak 在选定后调用。
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "诊断输出"
LOGS = HERE / "H10原始日志"
REAL = ["h10_20260928_153246", "h10_20260929_095556", "h10_20260929_100239", "h10_20260929_100955"]
REAL_NAME = {"h10_20260928_153246": "09-28", "h10_20260929_095556": "V1 r1",
             "h10_20260929_100239": "V1 r2", "h10_20260929_100955": "V1 r3"}
P_GRID = np.arange(-1000.0, 2500.0 + 1, 2.0)      # 方案 A 的 p 搜索网格，ms
MIN_PAIRS = 20
WIN, WIN_REACH, WIN_MIN = 10, 3, 5                 # 方案 B：窗长、每窗错位可变范围、窗内最少配对
P0S = (150.0, 400.0, 700.0)
SEEDS = 20


# ---------------- 判据 3（两方案共用） ----------------
def crit3(dd):
    if len(dd) < MIN_PAIRS:
        return False, float("nan"), float("nan")
    a = np.abs(dd)
    med, frac = float(np.median(a)), float(np.mean(a <= 16))
    return bool(med <= 8 and frac >= 0.90), med, frac


def make_notes(arrive_ms, rr_lists):
    """通知列表 → 扁平数组：rr（ms）、ni（所属通知）、m（在该通知里倒数第几个，最后一个为 0）。"""
    rr, ni, m = [], [], []
    for i, lst in enumerate(rr_lists):
        k = len(lst)
        for q, x in enumerate(lst):
            rr.append(x); ni.append(i); m.append(k - 1 - q)
    return dict(a=np.asarray(arrive_ms, float), rr=np.asarray(rr, float),
                ni=np.asarray(ni, int), m=np.asarray(m, int))


# ---------------- 方案 A ----------------
def align_A(T, iv, cov, notes):
    """T：R 峰 Pi 时钟时刻（ms，升序）；iv：相邻峰间期（ms，len(T)-1）；cov：ECG 覆盖的 Pi 时段（ms）。
    返回 dict(p, h, e, dd)：h 为 HR RR 扁平下标，e 为配到的 ECG 间期下标。"""
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
            best = (med, p, np.flatnonzero(v), e[v])
    if best is None:
        return None
    _, p, h, e = best
    return dict(p=float(p), h=h, e=e, dd=rr[h] - iv[e])


# ---------------- 方案 B ----------------
def global_off(rr_hr, iv):
    """原算法（错位 off ≥ 0 表示 rr_hr[i+off] ↔ iv[i]），搜索范围放到全程。"""
    best = None
    for off in range(-(len(iv) - MIN_PAIRS), len(rr_hr) - MIN_PAIRS + 1):
        a, b = rr_hr[max(off, 0):], iv[max(-off, 0):]
        n = min(len(a), len(b))
        if n < MIN_PAIRS:
            continue
        med = np.median(np.abs(a[:n] - b[:n]))
        if best is None or med < best[0]:
            best = (med, off)
    return None if best is None else best[1]


def align_B(rr_hr, iv):
    o0 = global_off(rr_hr, iv)
    if o0 is None:
        return None
    prev, H, E, offs = o0, [], [], []
    for w0 in range(0, len(rr_hr), WIN):
        h = np.arange(w0, min(w0 + WIN, len(rr_hr)))
        cand = []
        for o in range(prev - WIN_REACH, prev + WIN_REACH + 1):
            e = h - o
            v = (e >= 0) & (e < len(iv))
            if v.sum() < WIN_MIN:
                continue
            cand.append((float(np.median(np.abs(rr_hr[h[v]] - iv[e[v]]))), abs(o - prev), o))
        if not cand:
            continue                                   # 跳过该窗，错位沿用上一窗
        prev = min(cand)[2]
        e = h - prev
        v = (e >= 0) & (e < len(iv))
        H += h[v].tolist(); E += e[v].tolist(); offs.append(prev)
    H, E = np.asarray(H, int), np.asarray(E, int)
    return dict(o0=o0, offs=offs, h=H, e=E, dd=rr_hr[H] - iv[E])


# ---------------- 合成数据 ----------------
def pick_positions(rng, b, n, lo_ms, gap=15, tail=10):
    cand = np.flatnonzero((b > lo_ms))
    cand = cand[(cand >= 2) & (cand < len(b) - tail)]
    for _ in range(10000):
        pos = np.sort(rng.choice(cand, n, replace=False))
        if np.all(np.diff(pos) >= gap):
            return pos
    raise RuntimeError("错误位置排不下")


def rr_round(x):
    return np.round(x * 1.024) / 1.024                 # 1/1024 s 取整


def synth_notes(hb, hid, rng, p0, t_end):
    """由 HR 侧心跳生成通知。返回 notes 与每个 HR RR 的真值键（起、止心跳 id）。"""
    a0 = hb[0] - rng.uniform(0, 1000)
    a = [a0]
    while a[-1] < t_end + 2000:
        a.append(a[-1] + rng.uniform(920, 1080))
    a = np.asarray(a)
    cut = a - (p0 + rng.normal(0, 15, len(a)))
    vals = rr_round(np.diff(hb) + rng.normal(0, 1, len(hb) - 1))
    keys = list(zip(hid[:-1], hid[1:]))
    which = np.searchsorted(cut, hb[1:], side="left")  # hb[k] 属于 cut[i-1] < hb[k] ≤ cut[i] 的通知 i
    lists = [[] for _ in a]
    klists = [[] for _ in a]
    for k, i in enumerate(which):
        if i < len(a):
            lists[i].append(vals[k]); klists[i].append(keys[k])
    notes = make_notes(a, lists)
    flat_keys = [kk for kl in klists for kk in kl]
    return notes, flat_keys


def real_key(k0, k1):
    return (k0, k1) if (k0 >= 0 and k1 == k0 + 1) else None


def synth_run(beats_ms, rng, p0, late30, errors=True):
    b = np.asarray(beats_ms, float)
    b = b - b[0] + 2000.0
    N = len(b)
    ids = np.arange(N)
    start = b[0] + (30000.0 if late30 else 0.0)
    et, eid = b + rng.uniform(-3.85, 3.85, N), ids.copy()
    hb, hid = b.copy(), ids.copy()
    if errors:
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
    notes, hkeys = synth_notes(hb, hid, rng, p0, b[-1])
    truth = {h: ekey[real_key(*k)] for h, k in enumerate(hkeys) if real_key(*k) and real_key(*k) in ekey}
    return et, iv, cov, notes, truth


def correct_rate(res, truth):
    if res is None:
        return 0.0
    got = dict(zip(res["h"].tolist(), res["e"].tolist()))
    return float(np.mean([got.get(h) == e for h, e in truth.items()])) if truth else float("nan")


def lowvar_beats(rng, dur_ms=300000.0):
    rr = rng.normal(800, 8, int(dur_ms / 800) + 5)
    return np.concatenate([[0.0], np.cumsum(rr)])


# ---------------- 真实记录 ----------------
def load_real(stem):
    return load_path(LOGS / f"{stem}.log")


def load_path(path):
    """任意路径的 H10 日志 → 对齐所需的 T / iv / cov / notes（V2 起日志在段目录里，不在 H10原始日志/）"""
    from h10_parse import ECG, frames_to_series, lower_envelope_fit, parse_hr, parse_pmd, read_log
    from h10_rpeak import detect
    _, recs = read_log(path)
    arr, lists, frames = [], [], []
    for rt, _, s, d in recs:
        if s == "HR":
            arr.append(rt / 1e6); lists.append(parse_hr(d)[2])
        elif s == "PMD" and (d[0] & 0x3F) == ECG:
            _, ts, _, smp = parse_pmd(d, {})
            if smp is not None and len(smp):
                frames.append((rt, ts, smp))
    ecg = frames_to_series(frames, 130)
    det = detect(ecg["v"][:, 0] / 1000.0)
    ppm, icpt, _ = lower_envelope_fit(ecg["ts"], ecg["arrive"])
    slope = ppm * 1e3                                   # ns / s
    to_pi = lambda t: (t + icpt + slope * (t - ecg["ts"][0]) / 1e9) / 1e6
    ts_pk = ecg["t"][det["peaks"]].astype(float)
    T = to_pi(ts_pk)
    iv = np.diff(ts_pk) / 1e6
    cov = (to_pi(float(ecg["t"][0])), to_pi(float(ecg["t"][-1])))
    notes = make_notes(arr, lists)
    return dict(T=T, iv=iv, cov=cov, notes=notes, beats_ms=ts_pk / 1e6, ppm=ppm)


# ---------------- 主流程 ----------------
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(HERE))
    real = {s: load_real(s) for s in REAL}
    L = ["# 判据 3 对齐：方案 A（到达时刻）与方案 B（逐窗）比较结果\n",
         "方案、检验、选择规则见 `H10_判据3对齐算法_两方案与选择规则_测前写定.md`，本报告只执行不改。"
         "实现 `h10_rr_align.py`。\n"]

    # 第 1 组：合成
    sources = [(REAL_NAME[s], "real", s) for s in REAL] + [("低变异", "low", None)]
    rows = []
    for si, (name, kind, s) in enumerate(sources):
        for pi, p0 in enumerate(P0S):
            for late in (False, True):
                for seed in range(SEEDS):
                    rng = np.random.default_rng([si, pi, int(late), seed])
                    beats = real[s]["beats_ms"] if kind == "real" else lowvar_beats(rng)
                    et, iv, cov, notes, truth = synth_run(beats, rng, p0, late)
                    ra = align_A(et, iv, cov, notes)
                    rb = align_B(notes["rr"], iv)
                    rows.append(dict(src=name, p0=p0, late=late, seed=seed, n_truth=len(truth),
                                     A_ok=correct_rate(ra, truth), B_ok=correct_rate(rb, truth),
                                     A_c3=crit3(ra["dd"])[0] if ra else False,
                                     B_c3=crit3(rb["dd"])[0] if rb else False,
                                     A_p=ra["p"] if ra else float("nan")))
        print(f"合成 {name} 完成", flush=True)
    with open(OUT / "H10_判据3对齐_合成明细.csv", "w", encoding="utf-8-sig") as f:
        f.write("心跳来源,p0_ms,缺前30s,种子,有真值的RR数,A配对正确率,B配对正确率,A判据3通过,B判据3通过,A所得p_ms\n")
        for r in rows:
            f.write(f"{r['src']},{r['p0']:.0f},{int(r['late'])},{r['seed']},{r['n_truth']},{r['A_ok']:.4f},"
                    f"{r['B_ok']:.4f},{int(r['A_c3'])},{int(r['B_c3'])},{r['A_p']:.0f}\n")

    L.append("## 第 1 组 合成数据（600 次；每次都加 3 多检 + 3 漏检 + HR 并拍 1 + HR 劈拍 1）\n")
    L.append("| 心跳来源 | 情形 | A 配对正确率 均值 / 最低 | B 配对正确率 均值 / 最低 | A 判据 3 通过 | B 判据 3 通过 |")
    L.append("|---|---|---|---|---|---|")
    worst = {"A": [], "B": []}
    for name, _, _ in sources:
        for late in (False, True, None):
            sub = [r for r in rows if r["src"] == name and (late is None or r["late"] == late)]
            A = np.array([r["A_ok"] for r in sub]); B = np.array([r["B_ok"] for r in sub])
            tag = {False: "ECG 全程", True: "ECG 缺前 30 s", None: "**合计**"}[late]
            L.append(f"| {name} | {tag} | {A.mean()*100:.2f}% / {A.min()*100:.1f}% | {B.mean()*100:.2f}% / "
                     f"{B.min()*100:.1f}% | {np.mean([r['A_c3'] for r in sub])*100:.0f}% | "
                     f"{np.mean([r['B_c3'] for r in sub])*100:.0f}% |")
            if late is None:
                worst["A"].append(A.mean()); worst["B"].append(B.mean())
    wA, wB = min(worst["A"]), min(worst["B"])
    L.append(f"\n最差来源的平均配对正确率：A {wA*100:.2f}%、B {wB*100:.2f}%")
    pa = np.array([r["A_p"] - r["p0"] for r in rows])
    L.append(f"（附：A 找到的 p 与合成 p0 之差，中位 {np.nanmedian(pa):+.0f} ms、5–95 分位 "
             f"{np.nanpercentile(pa,5):+.0f}…{np.nanpercentile(pa,95):+.0f} ms）\n")
    print("第 1 组完成", flush=True)

    # 第 2 组：错配
    L.append("## 第 2 组 错配数据（判据 3 应当不通过）\n")
    fpA, fpB, nA, nB, detail = 0, 0, 0, 0, []
    for x in REAL:
        for y in REAL:
            if x == y:
                continue
            X, Y = real[x], real[y]
            rb = align_B(X["notes"]["rr"], Y["iv"])
            okb, medb, _ = crit3(rb["dd"]) if rb else (False, float("nan"), 0)
            fpB += okb; nB += 1
            meds = []
            for s in range(0, 61, 10):
                n2 = dict(X["notes"]); n2["a"] = X["notes"]["a"] - X["notes"]["a"][0] + Y["cov"][0] + s * 1000
                ra = align_A(Y["T"], Y["iv"], Y["cov"], n2)
                oka, meda, _ = crit3(ra["dd"]) if ra else (False, float("nan"), 0)
                fpA += oka; nA += 1; meds.append(meda)
            detail.append(f"| HR {REAL_NAME[x]} × ECG {REAL_NAME[y]} | {min(meds):.1f}–{max(meds):.1f} ms | {medb:.1f} ms |")
    L.append(f"真实交叉：A 假通过 **{fpA}/{nA}**、B 假通过 **{fpB}/{nB}**\n")
    L.append("| 组合 | A 的 \\|差\\| 中位（7 个平移） | B 的 \\|差\\| 中位 |\n|---|---|---|")
    L += detail
    lfA = lfB = 0
    lmA, lmB = [], []
    for k in range(50):
        rng = np.random.default_rng([99, k])
        b1, b2 = lowvar_beats(rng) + 2000, lowvar_beats(rng) + 2000
        notes, _ = synth_notes(b1, np.arange(len(b1)), rng, P0S[k % 3], b1[-1])
        et = b2 + rng.uniform(-3.85, 3.85, len(b2))
        iv = np.diff(et)
        ra = align_A(et, iv, (b2[0] - 400, b2[-1] + 400), notes)
        rb = align_B(notes["rr"], iv)
        a3, b3 = crit3(ra["dd"]) if ra else (False, np.nan, 0), crit3(rb["dd"]) if rb else (False, np.nan, 0)
        lfA += a3[0]; lfB += b3[0]; lmA.append(a3[1]); lmB.append(b3[1])
    L.append(f"\n低变异交叉（50 次）：A 假通过 **{lfA}/50**（\\|差\\| 中位最低 {np.nanmin(lmA):.1f} ms），"
             f"B 假通过 **{lfB}/50**（最低 {np.nanmin(lmB):.1f} ms）\n")
    print("第 2 组完成", flush=True)

    # 第 3 组：真实记录
    L.append("## 第 3 组 4 份真实记录（已看过，只作一票否决，不参与排名）\n")
    L.append("| 记录 | A：p / 配对数 / \\|差\\| 中位 / ≤16 ms / 判据 3 | B：错位 / 配对数 / \\|差\\| 中位 / ≤16 ms / 判据 3 | 两方案配对相同 |")
    L.append("|---|---|---|---|")
    vetoA = vetoB = 0
    for s in REAL:
        R = real[s]
        ra = align_A(R["T"], R["iv"], R["cov"], R["notes"])
        rb = align_B(R["notes"]["rr"], R["iv"])
        ca, cb = crit3(ra["dd"]), crit3(rb["dd"])
        vetoA += ca[1] > 8; vetoB += cb[1] > 8
        ga = dict(zip(ra["h"].tolist(), ra["e"].tolist()))
        gb = dict(zip(rb["h"].tolist(), rb["e"].tolist()))
        common = set(ga) | set(gb)
        same = np.mean([ga.get(h) == gb.get(h) for h in common])
        ob = sorted(set(rb["offs"]))
        L.append(f"| {REAL_NAME[s]} | {ra['p']:.0f} ms / {len(ra['h'])} / {ca[1]:.1f} ms / {ca[2]*100:.1f}% / "
                 f"{'过' if ca[0] else '不过'} | 起始 {rb['o0']}、窗内出现 {ob} / {len(rb['h'])} / {cb[1]:.1f} ms / "
                 f"{cb[2]*100:.1f}% / {'过' if cb[0] else '不过'} | {same*100:.1f}% |")
    L.append(f"\n\\|差\\| 中位 > 8 ms 的记录数：A {vetoA}、B {vetoB}（≥ 2 即一票否决）\n")

    # 选择规则
    L.append("## 按写定规则选择\n")
    elim = {}
    for k, fp, lf, vt in (("A", fpA, lfA, vetoA), ("B", fpB, lfB, vetoB)):
        why = []
        if fp > 0: why.append(f"真实交叉假通过 {fp} 次")
        if lf / 50 > 0.05: why.append(f"低变异交叉假通过率 {lf/50*100:.0f}%")
        if vt >= 2: why.append(f"真实记录 {vt} 份 \\|差\\| 中位 > 8 ms")
        elim[k] = why
        L.append(f"- 方案 {k}：{'淘汰（' + '；'.join(why) + '）' if why else '未淘汰'}")
    alive = [k for k in "AB" if not elim[k]]
    if not alive:
        pick = None
        L.append("\n**两个都被淘汰 → 不选，报告用户重新设计。**")
    elif len(alive) == 1:
        pick = alive[0]
        L.append(f"\n**选定方案 {pick}**（另一方案被淘汰）")
    else:
        d = (wA - wB) * 100
        pick = "A" if d > -1 else "B"
        rule = ("A 高出 ≥ 1 个百分点" if d >= 1 else "B 高出 ≥ 1 个百分点" if d <= -1
                else "差距 < 1 个百分点，按写定偏好取 A")
        L.append(f"\n最差来源平均配对正确率 A {wA*100:.2f}% vs B {wB*100:.2f}%（差 {d:+.2f} 个百分点）→ {rule} → "
                 f"**选定方案 {pick}**")
    (OUT / "H10_判据3对齐_两方案比较结果.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
