"""H10 第一步判据 3 失败后的事后探查（**看过结果之后写的，不能用来改判定**）

判据 3 在 h10_20260928_153246 上不通过：h10_parse.py 的 R 峰检测只找到 28 个峰（RR 有 410 个）。
本脚本只回答「是 RR 与 ECG 真的不一致，还是 R 峰检测没找对」，结论只作为下一次采集前改写检测方法的依据。

    python h10_rr_posthoc.py 诊断输出/H10_20260928_153246
输入是 h10_parse.py 输出的 _ECG.csv / _HR.csv 前缀，输出 <前缀>_判据3事后探查.md
"""
import csv
import sys

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

FS = 130.0


def load(base):
    d = np.loadtxt(f"{base}_ECG.csv", delimiter=",", skiprows=1)
    rr = []
    for row in csv.DictReader(open(f"{base}_HR.csv", encoding="utf-8-sig")):
        rr += [float(s) for s in row["RR_ms"].split()]
    return d[:, 0], d[:, 1], np.array(rr)


def detect(v, sign):
    """5–25 Hz 带通后按给定极性找峰；阈值 = 中位 + 5×稳健标准差"""
    b, a = butter(2, [5 / (FS / 2), 25 / (FS / 2)], "band")
    x = sign * filtfilt(b, a, v)
    thr = np.median(x) + 5 * 1.4826 * np.median(np.abs(x - np.median(x)))
    pk, _ = find_peaks(x, height=thr, distance=int(0.33 * FS))
    return pk


def best_offset(rr, re, lo, hi):
    best = None
    for off in range(lo, hi):
        a = rr[max(off, 0):]
        b = re[max(-off, 0):]
        n = min(len(a), len(b))
        if n < 20:
            continue
        dd = a[:n] - b[:n]
        m = np.median(np.abs(dd))
        if best is None or m < best[0]:
            best = (m, off, n, dd)
    return best


def main(base):
    t, v, rr = load(base)
    L = [f"# 判据 3 事后探查：{base}", "",
         "**看过判定结果之后做的，只用来找原因，不改变 `_验收.md` 的判定。**", ""]
    L.append(f"ECG 时长 {(t[-1]-t[0])/1e3:.1f} s；HR 服务 RR {len(rr)} 个、合计 {rr.sum()/1e3:.1f} s、中位 {np.median(rr):.0f} ms")
    L.append(f"ECG 分位（0.1/1/50/99/99.9，mV）：{np.percentile(v, [0.1, 1, 50, 99, 99.9]).round(3).tolist()}")
    L.append("")
    L.append("## 极性")
    for s in (1, -1):
        pk = detect(v, s)
        L.append(f"- 极性 {s:+d}：检出 {len(pk)} 个峰")
    pk = detect(v, -1)
    re = np.diff(t[pk])
    tp = (t[pk][1:] - t[0]) / 1e3
    m, off, n, dd = best_offset(rr, re, -80, 81)
    L += ["", "## 反极性 + 带通，全程一个错位",
          f"ECG 峰 {len(pk)}；最佳错位 {off}、比对 {n} 拍：|差| 中位 {m:.1f} ms、"
          f"|差|≤16 ms 占 {np.mean(np.abs(dd) <= 16)*100:.1f}%", "",
          "## 分段各自找错位（每 40 个 ECG 间期）", "",
          "| ECG 间期序号 | 时段 s | 错位 | \\|差\\| 中位 ms | ≤16 ms |", "|---|---|---|---|---|"]
    for s in range(0, len(re), 40):
        seg = re[s:s + 40]
        best = None
        for o in range(0, 90):
            a = rr[s + o:s + o + len(seg)]
            if len(a) < len(seg):
                continue
            mm = np.median(np.abs(a - seg))
            if best is None or mm < best[0]:
                best = (mm, o, np.mean(np.abs(a - seg) <= 16))
        L.append(f"| {s}–{s+len(seg)} | {tp[s]:.0f}–{tp[min(s+39, len(tp)-1)]:.0f} | {best[1]} | {best[0]:.1f} | {best[2]*100:.0f}% |")
    out = f"{base}_判据3事后探查.md"
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\n→ {out}")


if __name__ == "__main__":
    main(sys.argv[1])
