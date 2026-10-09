"""H10 ECG 的 R 峰检测，按 `H10_R峰检测_测前写定.md` 执行（方法与阈值在该文件里写定，这里不改）。

用法：
    python h10_rpeak.py --selftest                  # 合成 ECG：正/负极性各一遍，只证实现自洽
    python h10_rpeak.py <h10_xxx.log>... --explore  # 只跑通、记录，不出判定（V1 与 09-28 的日志必须加）
    python h10_rpeak.py <h10_xxx.log>...            # V2 起的采集：出 D1/D2/判据 3/判据 5 判定
                                                    # （判据 3 对齐用合并方案 AB，见 h10_rr_align_ab.py）
    输出：诊断输出/H10_<时间>_R峰.md 与 _R峰.csv

neurokit2 固定 0.2.12。0.2.12 的 data/read_xdf.py 用了 `float | None` 注解，Python 3.9 一 import 就报 TypeError；
本项目不用 xdf，所以在 3.9 下先塞一个空的 read_xdf 模块再 import（不改 site-packages）。
"""
import sys
import types
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "诊断输出"
NK_VERSION = "0.2.12"
FS_NK = 130                      # 交给 neurokit2 的采样率（实测 130.02 Hz，取整；峰时刻仍用传感器时间戳）
WIN_S = 2.0                      # 极性判定窗长
D1_RATIO = 1.5
D2_TOL = 0.03


def import_nk():
    if sys.version_info < (3, 10) and "neurokit2.data.read_xdf" not in sys.modules:
        stub = types.ModuleType("neurokit2.data.read_xdf")
        stub.read_xdf = None
        sys.modules["neurokit2.data.read_xdf"] = stub
    import neurokit2 as nk
    if nk.__version__ != NK_VERSION:
        raise SystemExit(f"neurokit2 版本 {nk.__version__} ≠ 写定的 {NK_VERSION}，停止")
    return nk


def polarity(clean, fs):
    """2 s 不重叠窗，每窗最大值 P、−最小值 N，各取中位；P ≥ N 取正向。返回 (符号, 比值, P, N)。"""
    n = int(round(WIN_S * fs))
    k = len(clean) // n
    seg = clean[:k * n].reshape(k, n)
    p = float(np.median(seg.max(axis=1)))
    q = float(np.median(-seg.min(axis=1)))
    sign = 1 if p >= q else -1
    lo, hi = min(p, q), max(p, q)
    ratio = hi / lo if lo > 0 else float("inf")
    return sign, ratio, p, q


def detect(v_mv, nk=None):
    """v_mv：ECG（mV）。返回 dict：sign、ratio、P、N、clean、peaks（样本下标）、amp（mV，正数）。"""
    nk = nk or import_nk()
    clean = np.asarray(nk.ecg_clean(v_mv, sampling_rate=FS_NK, method="neurokit"), dtype=float)
    sign, ratio, p, q = polarity(clean, FS_NK)
    _, info = nk.ecg_peaks(sign * clean, sampling_rate=FS_NK, method="neurokit", correct_artifacts=False)
    pk = np.asarray(info["ECG_R_Peaks"], dtype=int)
    return dict(sign=sign, ratio=ratio, P=p, N=q, clean=clean, peaks=pk, amp=sign * clean[pk])


def rr_align(rr_hr, rr_ecg):
    """与 h10_parse 判据 3 原算法相同：错位 −20…20 拍，取 |差| 中位最小者，比对拍数 < 20 的错位不考虑。"""
    best = None
    for off in range(-20, 21):
        a = rr_hr[max(off, 0):]
        b = rr_ecg[max(-off, 0):]
        n = min(len(a), len(b))
        if n < 20:
            continue
        dd = a[:n] - b[:n]
        med = np.median(np.abs(dd))
        if best is None or med < best[0]:
            best = (med, off, n, dd)
    return best


def judge(t_ns, det, rr_hr, ab=None):
    """按写定判据给出各项结果。t_ns：每个 ECG 样本的传感器时刻。返回 (结果 dict, 报告行列表)。
    ab：h10_rr_align.load_path 的结果；给了就用合并方案 AB 判判据 3，否则用原「全程单一错位」（探查模式保持旧算法）。"""
    L, res = [], {}
    pk = det["peaks"]
    res["D1"] = det["ratio"] >= D1_RATIO
    L.append(f"极性：P（每窗最大值中位）{det['P']:.3f} mV、N（每窗 −最小值中位）{det['N']:.3f} mV → "
             f"取{'正' if det['sign'] > 0 else '负'}向，比值 {det['ratio']:.2f}（≥ {D1_RATIO}）→ "
             f"**D1 {'通过' if res['D1'] else '不通过'}**")

    dur = (t_ns[-1] - t_ns[0]) / 1e9
    rr_med = float(np.median(rr_hr)) if len(rr_hr) else float("nan")
    expect = dur * 1000 / rr_med
    rel = (len(pk) - 1 - expect) / expect
    res["D2"] = abs(rel) <= D2_TOL
    L.append(f"完整性：ECG 时长 {dur:.1f} s、HR 服务 RR 中位 {rr_med:.1f} ms → 预期约 {expect:.1f} 个间期；"
             f"检出峰 {len(pk)} 个（{len(pk)-1} 个间期），相差 {rel*100:+.2f}%（±{D2_TOL*100:.0f}%）→ "
             f"**D2 {'通过' if res['D2'] else '不通过'}**")

    rr_ecg = np.diff(t_ns[pk]) / 1e6
    if ab is not None:
        # 2026-10-08 起：对齐改用合并方案 AB（`H10_判据3对齐_合并方案AB_测前写定.md`，检验全部满足后采用）。
        # 阈值不变；多一个「无法判定」——平移 ±20/40/60 s 也能过，说明这份数据分不开对错
        from h10_rr_align_ab import verdict
        v = verdict(ab["T"], ab["iv"], ab["cov"], ab["notes"])
        r = v["res"]
        if r is None or not len(r["dd"]):
            res["3"] = False
            L.append("判据 3（合并方案 AB）：粗定位找不到 ≥ 20 个配对 → **不通过**")
        else:
            dd = r["dd"]
            res["3"] = {"通过": True, "不通过": False}.get(v["out"])      # 无法判定 → None
            L.append(f"判据 3（合并方案 AB）：粗定位滞后 {r['p']:.0f} ms、配对 {len(dd)} 拍，|差| 中位 {v['c3'][1]:.1f} ms、"
                     f"均值 {np.abs(dd).mean():.1f} ms、最大 {np.abs(dd).max():.1f} ms、|差|≤16 ms 占 {v['c3'][2]*100:.1f}%；"
                     f"平移自检也通过的 {v['shift_pass'] or '无'} → **{v['out']}**")
    elif (best := rr_align(np.asarray(rr_hr), rr_ecg)):
        med, off, n, dd = best
        frac = float(np.mean(np.abs(dd) <= 16))
        res["3"] = bool(med <= 8 and frac >= 0.90)
        L.append(f"判据 3：最佳错位 {off} 拍、比对 {n} 拍，|差| 中位 {med:.1f} ms、均值 {np.abs(dd).mean():.1f} ms、"
                 f"最大 {np.abs(dd).max():.1f} ms、|差|≤16 ms 占 {frac*100:.1f}% → "
                 f"**{'通过' if res['3'] else '不通过'}**")
    else:
        res["3"] = False
        L.append("判据 3：可比对拍数不足 20 → **不通过**")

    amp = float(np.median(det["amp"])) if len(pk) else 0.0
    res["5"] = 0.3 <= amp <= 5
    L.append(f"判据 5：峰幅度中位 {amp:.3f} mV（5–95 分位 {np.percentile(det['amp'],5):.3f}–"
             f"{np.percentile(det['amp'],95):.3f}，量在「极性×清洗后」信号上）→ **{'通过' if res['5'] else '不通过'}**")

    if not (res["D1"] and res["D2"]):
        L.append("→ D1 或 D2 未过：按写定规则，判据 3、5 **不判定**（上面两行只作记录）")
        res["3"] = res["5"] = None
    return res, L, rr_ecg


def run_log(path, explore):
    from h10_parse import ECG, frames_to_series, parse_hr, parse_pmd, read_log
    head, recs = read_log(path)
    stamp = Path(path).stem.replace("h10_", "")
    rr_hr, frames = [], []
    for rt, _, s, d in recs:
        if s == "HR":
            rr_hr += parse_hr(d)[2]
        elif s == "PMD" and (d[0] & 0x3F) == ECG:
            _, ts, _, smp = parse_pmd(d, {})
            if smp is not None and len(smp):
                frames.append((rt, ts, smp))
    L = [f"# H10 R 峰检测：{Path(path).name}\n",
         "方法与判据见 `H10_R峰检测_测前写定.md`，本报告只执行不改。\n"]
    if explore:
        L.append("**探查模式：本日志在判据写定前已采集/已被看过，按规则只记录、不出判定。**\n")
    if not frames:
        L.append("无 ECG 帧")
        return L, stamp
    ecg = frames_to_series(frames, 130)
    v = ecg["v"][:, 0] / 1000.0
    det = detect(v)
    ab = None
    if not explore:                     # 判定模式：判据 3 用合并方案 AB（要到达时刻，换到 Pi 时钟）
        from h10_rr_align import load_path
        ab = load_path(path)
    res, JL, rr_ecg = judge(ecg["t"], det, rr_hr, ab)
    L.append(f"- ECG {len(v)} 样本、实测 {ecg['fs']:.3f} Hz；HR 服务 RR {len(rr_hr)} 个\n")
    L += [f"- {x}" for x in JL]
    if not explore:
        verdict = {k: ("通过" if v_ else "不通过" if v_ is False else "不判定") for k, v_ in res.items()}
        L.append(f"\n## 判定：{'、'.join(f'{k} {x}' for k, x in verdict.items())}")
    pk = det["peaks"]
    with open(OUT / f"H10_{stamp}_R峰.csv", "w", encoding="utf-8-sig") as f:
        f.write("峰序号,样本下标,传感器时刻ms,幅度mV,与前峰间期ms\n")
        tms = ecg["t"][pk] / 1e6
        for i, (k, tt, a) in enumerate(zip(pk, tms, det["amp"])):
            f.write(f"{i},{k},{tt:.3f},{a:.4f},{'' if i == 0 else f'{tt - tms[i-1]:.1f}'}\n")
    return L, stamp


def selftest():
    """合成 ECG（neurokit2 自带模拟器）：正向与取反各跑一遍。
    只证明：极性规则能识别方向、两种极性检出的峰位置一致、峰数与模拟心率相符——**不证明对真实 H10 数据有效**。"""
    nk = import_nk()
    fs, dur, hr = FS_NK, 120, 70
    ecg = nk.ecg_simulate(duration=dur, sampling_rate=fs, heart_rate=hr, noise=0.05, random_state=1)
    a = detect(ecg, nk)
    b = detect(-ecg, nk)
    expect = dur * hr / 60
    assert a["sign"] == 1 and b["sign"] == -1, (a["sign"], b["sign"])
    assert a["ratio"] >= D1_RATIO and b["ratio"] >= D1_RATIO, (a["ratio"], b["ratio"])
    assert abs(len(a["peaks"]) - expect) <= 2, (len(a["peaks"]), expect)
    assert len(a["peaks"]) == len(b["peaks"]) and np.all(np.abs(a["peaks"] - b["peaks"]) <= 1)
    assert np.allclose(a["amp"], b["amp"], atol=1e-9)
    print(f"selftest 通过：合成 {dur} s / {hr} bpm，正向与取反都判对极性（比值 {a['ratio']:.2f} / {b['ratio']:.2f}），"
          f"峰各 {len(a['peaks'])} 个（预期约 {expect:.0f}），位置差 ≤ 1 样本、幅度一致")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(HERE))
    if "--selftest" in sys.argv:
        selftest(); sys.exit()
    explore = "--explore" in sys.argv
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        L, stamp = run_log(p, explore)
        (OUT / f"H10_{stamp}_R峰.md").write_text("\n".join(L), encoding="utf-8")
        print("\n".join(L)); print()
