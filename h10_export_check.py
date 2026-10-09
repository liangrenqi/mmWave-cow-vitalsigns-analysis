"""核对 Polar Equine 导出的 H10 数据：采样率、缺口、时间基是否一致、RR 与 ECG 是否吻合。

只读 心率带数据/*.txt，结果写到 诊断输出/H10导出核对.md。
用法：python h10_export_check.py
"""
import sys
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
SRC = HERE / "心率带数据"
OUT = HERE / "诊断输出"


def load(prefix):
    f = sorted(SRC.glob(f"{prefix}_*.txt"))[0]
    lines = f.read_text(encoding="utf-8").splitlines()
    head = [l for l in lines if l.startswith("#")]
    i = next(j for j, l in enumerate(lines) if l and not l.startswith("#"))
    cols = [c.strip() for c in lines[i].split(",")]
    data = np.array([[float(v) for v in l.split(",")] for l in lines[i + 1:] if l.strip()])
    return f.name, head, cols, data


def rate_report(name, t):
    dt = np.diff(t)
    return (f"{name}：{len(t)} 点，{t[0]:.0f}–{t[-1]:.0f} ms（{(t[-1]-t[0])/1000:.2f} s），"
            f"平均间隔 {dt.mean():.3f} ms → {1000/dt.mean():.2f} Hz；间隔范围 {dt.min():.0f}–{dt.max():.0f} ms；"
            f"间隔 >2 倍均值的缺口 {(dt > 2*dt.mean()).sum()} 处")


def main():
    L = ["# H10 导出核对（Polar Equine）\n"]
    ecg_n, ecg_h, _, ecg = load("ECG")
    acc_n, acc_h, _, acc = load("ACC")
    hr_n, hr_h, _, hr = load("HR")
    gps_n, _, _, gps = load("GPS")
    L.append("文件头：" + " | ".join(h.lstrip("# ") for h in ecg_h[1:4]))
    L.append("\n## 采样率与缺口\n")
    L.append(rate_report("ECG", ecg[:, 1]))
    L.append(rate_report("ACC", acc[:, 3]))
    L.append(rate_report("GPS", gps[:, 2]))

    # HR 的 MS 列是否就是 RR 累加
    rr, ms, sc = hr[:, 1], hr[:, 2], hr[:, 3]
    L.append("\n## HR 文件的 MS 列\n")
    L.append(f"MS 是否等于 RR 累加：{np.array_equal(np.cumsum(rr), ms)}"
             f"（最大差 {np.abs(np.cumsum(rr) - ms).max():.0f} ms）")
    L.append(f"{len(rr)} 行，皮肤接触 SC=0 的 {(sc == 0).sum()} 行；RR>1500 ms 的异常值 {(rr > 1500).tolist().count(True)} 个："
             f"{rr[rr > 1500].astype(int).tolist()}")

    # ECG R 峰 → 逐拍 RR，与 HR 文件的 RR 比对
    t, v = ecg[:, 1], ecg[:, 0]
    fs = 1000 / np.diff(t).mean()
    pk, _ = find_peaks(v, height=np.percentile(v, 99) * 0.5, distance=int(0.33 * fs))
    tr = t[pk]
    rr_ecg = np.diff(tr)
    L.append("\n## ECG R 峰与 HR 文件 RR 对照\n")
    L.append(f"ECG R 峰 {len(pk)} 个（阈值=99 分位的一半、最小间隔 0.33 s），ECG RR {rr_ecg.min():.0f}–{rr_ecg.max():.0f} ms")
    good = rr[(sc == 1) & (rr < 1500)]
    # 用序列互相关找对齐偏移（ECG 起点晚，逐拍错位）
    best = None
    for off in range(0, len(good) - 10):
        n = min(len(good) - off, len(rr_ecg))
        if n < 10:
            break
        d = good[off:off + n] - rr_ecg[:n]
        s = np.abs(d).mean()
        if best is None or s < best[0]:
            best = (s, off, n, d)
    if best:
        s, off, n, d = best
        L.append(f"最佳对齐：HR 有效 RR 第 {off} 拍对 ECG 第 0 拍，{n} 拍比对，"
                 f"差值均值 {d.mean():+.1f} ms、|差| 均值 {s:.1f} ms、最大 {np.abs(d).max():.0f} ms")
        # 同一拍在两个 MS 时间轴上的位置
        ms_good = ms[(sc == 1) & (rr < 1500)]
        k = min(n, 10)
        # good[off+j] 是 tr[j]→tr[j+1] 这一拍，其 MS 是该拍结束时刻，对应 tr[j+1]
        dd = ms_good[off:off + n] - tr[1:1 + n]
        L.append(f"同一拍的时刻差（HR 的 MS − ECG R 峰时刻）：前 {k} 拍 {dd[:k].astype(int).tolist()} ms；"
                 f"全 {n} 拍 {dd.min():.0f}–{dd.max():.0f} ms")
    L.append("\n## GPS\n")
    L.append(f"速度 {gps[:,0].min():.2f}–{gps[:,0].max():.2f} km/h，精度 {gps[:,1].min():.1f}–{gps[:,1].max():.1f} m（手机 GPS，H10 无 GPS）")
    (OUT / "H10导出核对.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
