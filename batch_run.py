#!/usr/bin/env python3
"""批量跑一个批次目录下的全部会话，汇总成一张表 + CSV。

解释器：C:\\Users\\34219\\AppData\\Local\\Programs\\Python\\Python39\\python.exe

用法：
  batch_run.py <batch_dir> [--plots] [--frames N]

只读：不修改 radar_inspector.py / vsp_core.py / blind.py 任何一行，
      analyze_data() 当模块调用，逐段独立。

为什么除了呼吸指标还要输出自检量：
  手腕采集（09-08）那次，程序对"没有呼吸的部位"报出了 17-24 bpm 的
  漂亮呼吸率，而 radar_inspector 自己的局域性判据（<50% 即不可信）
  同时在报警、只是没有拦截。所以这里把三个自检量与主指标并列打印，
  让"这个数可不可信"和"这个数是多少"一起进表。
"""
import sys
import os
import csv
import time
import traceback

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import radar_reader as rr
import radar_inspector as ri

# 心跳带（Hz）= 48..120 bpm。radar_inspector 只有呼吸带 0.1-0.6 Hz
HR_LO, HR_HI = 0.8, 2.0
# 局域性通过线：目标 bin +/-2 占 0-3 m 呼吸位移能量的比例
LOCALITY_TH = 50.0


def band_peak(x, fs, lo, hi):
    """→ (峰频 bpm, 显著度 dB)。显著度 = 带内峰值 / 带内中位。"""
    x = np.asarray(x, float)
    x = x - x.mean()
    n = len(x)
    if n < 16:
        return np.nan, np.nan
    nfft = 1 << (int(np.log2(n)) + 3)
    f = np.fft.rfftfreq(nfft, 1.0 / fs)
    P = np.abs(np.fft.rfft(x * np.hanning(n), nfft)) ** 2
    m = (f >= lo) & (f <= hi)
    if not m.any():
        return np.nan, np.nan
    idx = np.where(m)[0]
    j = idx[np.argmax(P[m])]
    if 0 < j < len(P) - 1:
        y0, y1, y2 = P[j - 1], P[j], P[j + 1]
        dj = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-30)
    else:
        dj = 0.0
    prom = 10 * np.log10(P[j] / (np.median(P[m]) + 1e-30))
    return (j + dj) * fs / nfft * 60.0, prom


def rx_checks(session_dir, tbin, fs):
    """4 个物理独立接收机的一致性 —— 假目标过不了这一关。

    radar_inspector 返回的 slowtime_complex 只有 RX0（:389，1-D），
    所以这里用 vsp_core.build_slowtime 自己取全 4 路。那一层的布局
    （维序 / IQ 交织 / z=I-jQ 取共轭）由 memory 实测坐实，可直接用。

    → (RX0-RX1 相位差 std rad, 4 路呼吸波形两两相关的最小值)
    """
    try:
        import vsp_core as vc
        binp = os.path.join(session_dir, "cow_vitalsigns_Raw_0.bin")
        X = vc.build_slowtime(binp, cache=os.path.join(session_dir, "slowtime.npy"),
                              verbose=False)
        if tbin >= X.shape[2]:
            return np.nan, np.nan
        a, b = X[:, 0, tbin], X[:, 1, tbin]
        pstd = float(np.std(np.angle(a * np.conj(b))))

        ds = []
        for r in range(X.shape[1]):
            d = vc.phase_mm(X[:, r, tbin])
            ds.append(ri.bandpass(d, fs, ri.BR_LO, ri.BR_HI))
        cc = [float(np.corrcoef(ds[i], ds[j])[0, 1])
              for i in range(len(ds)) for j in range(i + 1, len(ds))]
        return pstd, min(cc)
    except Exception:
        return np.nan, np.nan


def one(session_dir, wf, max_frames, make_plot):
    d = ri.analyze_data(session_dir, wf, max_frames=max_frames)
    fs = d["fs_hz"]
    dbp = d["disp_bp_mm"]
    br = d["breaths"]

    # 呼吸带：谱峰法（与逐周期平均互为交叉校验）
    br_bpm_spec, br_prom = band_peak(dbp, fs, ri.BR_LO, ri.BR_HI)
    # 心跳带：在未带通的位移上取，且用差分抑制呼吸基频泄漏（同 blind.py 做法）
    disp = d["displacement_mm"]
    hr_bpm, hr_prom = band_peak(np.diff(disp), fs, HR_LO, HR_HI)

    # locality 是 0..1 的比例（radar_inspector.py:431 用 :.1% 打印），转成百分数
    loc_pct = float(d["locality"]) * 100.0
    rxstd, rxcc = rx_checks(session_dir, d["target_bin"], fs)

    row = dict(
        session=os.path.basename(session_dir.rstrip("/\\")),
        nframes=d["nframes"],
        dur_s=round(d["nframes"] / fs, 1),
        target_bin=d["target_bin"],
        range_m=round(float(d["target_range_m"]), 3),
        disp_rms_mm=round(float(np.std(dbp)), 4),
        disp_p2p_mm=round(float(dbp.max() - dbp.min()), 3),
        br_bpm_peak=round(float(br["rate_bpm"]), 2) if np.isfinite(br["rate_bpm"]) else "",
        br_bpm_spec=round(float(br_bpm_spec), 2) if np.isfinite(br_bpm_spec) else "",
        br_prom_db=round(float(br_prom), 1) if np.isfinite(br_prom) else "",
        br_count=int(len(br["peaks"])),
        br_cv=round(float(br["cv"]), 3) if np.isfinite(br["cv"]) else "",
        hr_bpm=round(float(hr_bpm), 2) if np.isfinite(hr_bpm) else "",
        hr_prom_db=round(float(hr_prom), 1) if np.isfinite(hr_prom) else "",
        locality_pct=round(loc_pct, 2),
        rx01_phase_std=round(float(rxstd), 3) if np.isfinite(rxstd) else "",
        rx_corr_min=round(float(rxcc), 3) if np.isfinite(rxcc) else "",
        trust="OK" if loc_pct >= LOCALITY_TH else "LOW-LOCALITY",
    )

    if make_plot:
        ri.plot_results(d, os.path.join(session_dir, "radar_inspector.png"))
    return row


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    batch = sys.argv[1]
    make_plot = "--plots" in sys.argv
    max_frames = None
    for i, a in enumerate(sys.argv):
        if a == "--frames" and i + 1 < len(sys.argv):
            max_frames = int(sys.argv[i + 1])

    sessions = sorted(
        os.path.join(batch, x) for x in os.listdir(batch)
        if os.path.isdir(os.path.join(batch, x))
    )
    print(f"批次目录: {batch}")
    print(f"会话数  : {len(sessions)}")

    wf = rr.WAVEFORM_VITALSIGNS
    rows, fails = [], []
    t0 = time.time()
    for i, s in enumerate(sessions, 1):
        name = os.path.basename(s)
        print(f"\r[{i}/{len(sessions)}] {name} ...", end="", flush=True)
        try:
            # analyze_data 内部有大量 print，临时吞掉以保持进度行整洁
            buf, sys.stdout = sys.stdout, open(os.devnull, "w", encoding="utf-8")
            try:
                rows.append(one(s, wf, max_frames, make_plot))
            finally:
                sys.stdout.close()
                sys.stdout = buf
        except Exception as e:
            fails.append((name, repr(e)))
            print(f"\n  !! {name}: {e}")
            traceback.print_exc()
    print(f"\r完成 {len(rows)}/{len(sessions)} 段，用时 {time.time()-t0:.0f} s" + " " * 30)

    if not rows:
        print("没有成功的段。")
        return

    # ---- CSV ----
    out_csv = os.path.join(batch, "batch_summary.csv")
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- 控制台表 ----
    print("\n" + "=" * 150)
    print("批量汇总（时间顺序）")
    print("=" * 150)
    hdr = (f"{'#':>3} {'时刻':<15} {'bin':>4} {'距离m':>6} "
           f"{'RMS mm':>7} {'峰峰mm':>7} {'呼吸bpm':>8} {'谱峰bpm':>8} {'显著dB':>7} "
           f"{'次数':>4} {'CV':>6} {'心率bpm':>8} {'心显dB':>7} {'局域%':>7} "
           f"{'RXstd':>6} {'RXcc':>6} {'可信':>12}")
    print(hdr)
    print("-" * 160)
    for i, r in enumerate(rows, 1):
        tm = r["session"].replace("Cow_UNKNOWN_vitalsigns_", "")[:15]
        print(f"{i:>3} {tm:<15} {r['target_bin']:>4} {r['range_m']:>6.2f} "
              f"{r['disp_rms_mm']:>7.3f} {r['disp_p2p_mm']:>7.2f} "
              f"{str(r['br_bpm_peak']):>8} {str(r['br_bpm_spec']):>8} {str(r['br_prom_db']):>7} "
              f"{r['br_count']:>4} {str(r['br_cv']):>6} "
              f"{str(r['hr_bpm']):>8} {str(r['hr_prom_db']):>7} "
              f"{r['locality_pct']:>7.2f} {str(r['rx01_phase_std']):>6} "
              f"{str(r['rx_corr_min']):>6} {r['trust']:>12}")

    # ---- 统计概览 ----
    def col(k):
        return np.array([r[k] for r in rows if r[k] != ""], float)

    print("\n" + "=" * 150)
    print("分布概览（不做任何分组假设 —— 分组信息不在数据里）")
    print("=" * 150)
    for k, lab in [("range_m", "目标距离 m"), ("disp_rms_mm", "带通位移RMS mm"),
                   ("br_bpm_peak", "呼吸率(逐周期) bpm"), ("br_bpm_spec", "呼吸率(谱峰) bpm"),
                   ("br_prom_db", "呼吸谱显著度 dB"), ("br_cv", "呼吸CV"),
                   ("hr_bpm", "心率 bpm"), ("hr_prom_db", "心跳显著度 dB"),
                   ("locality_pct", "距离局域性 %"), ("rx01_phase_std", "RX01相位差std rad"),
                   ("rx_corr_min", "4RX波形相关最小值")]:
        v = col(k)
        if len(v):
            print(f"  {lab:<22} 中位 {np.median(v):8.2f}   "
                  f"均值 {v.mean():8.2f}   min {v.min():8.2f}   max {v.max():8.2f}")

    nlow = sum(1 for r in rows if r["trust"] != "OK")
    print(f"\n  局域性 <{LOCALITY_TH:.0f}% 的段: {nlow}/{len(rows)}"
          f"  （这些段的呼吸/心率数值不可直接采信）")
    tb = np.array([r["target_bin"] for r in rows])
    print(f"  目标 bin 取值分布: " + " ".join(
        f"{b}:{c}" for b, c in zip(*np.unique(tb, return_counts=True))))

    if fails:
        print(f"\n失败 {len(fails)} 段:")
        for n, e in fails:
            print(f"  {n}: {e}")

    print(f"\nCSV 已存: {out_csv}")


if __name__ == "__main__":
    main()