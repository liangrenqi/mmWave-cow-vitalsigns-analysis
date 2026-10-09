"""手机导出（Polar Equine）里能不能看出「ECG/ACC 比记录开始晚多少」

    python h10_export_start_gap.py [--dir 心率带数据] [--out 诊断输出/H10手机导出_启动延迟估计.md]

导出文件各自的 MS 列都从约 0 起算、只有秒级的文件头时刻，所以**不能直接读出**启动延迟。
只能在假设下间接估计，两种估计都写明假设：
  估计 1（末端对齐）：GPS 是手机侧 1 Hz、从记录开始计时；若各路同时停止，
         ECG 起点 ≈ GPS 末时刻 − ECG 跨度
  估计 2（HR 对齐）：HR 的 MS = RR 累加（已核实完全相等）；若 HR 从记录开始即有、RR 累加即真实时间，
         ECG 起点在 HR 轴上 = 同一拍的常数偏移 + ECG 首样本 MS（偏移取自 H10导出核对.md：12289–12300 ms）
"""
import argparse
import glob
import os


def load(path):
    rows = []
    for l in open(path, encoding="utf-8"):
        l = l.strip()
        if not l or l.startswith("#") or not l[0] in "-0123456789":
            continue
        rows.append([float(x) for x in l.split(",")])
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="心率带数据")
    ap.add_argument("--out", default="诊断输出/H10手机导出_启动延迟估计.md")
    ap.add_argument("--hr-ecg-offset-ms", type=float, default=12290.0,
                    help="同一拍 HR 的 MS − ECG R 峰时刻，取自 H10导出核对.md")
    a = ap.parse_args()
    f = {k: glob.glob(os.path.join(a.dir, f"{k}_*.txt"))[0] for k in ("ECG", "ACC", "HR", "GPS")}
    ecg, acc, hr, gps = (load(f[k]) for k in ("ECG", "ACC", "HR", "GPS"))
    ecg_t = [r[-1] for r in ecg]
    acc_t = [r[-1] for r in acc]
    hr_t = [r[2] for r in hr]
    gps_t = [r[-1] for r in gps]
    span_ecg = (ecg_t[-1] - ecg_t[0]) / 1000
    est1 = gps_t[-1] / 1000 - span_ecg
    est2 = (a.hr_ecg_offset_ms + ecg_t[0]) / 1000
    L = ["# 手机导出：ECG/ACC 相对记录开始的起点（间接估计，均为推断）", "",
         f"文件：{', '.join(os.path.basename(v) for v in f.values())}", "",
         "| 路 | 首 MS | 末 MS | 跨度 s |", "|---|---|---|---|",
         f"| ECG | {ecg_t[0]:.0f} | {ecg_t[-1]:.0f} | {span_ecg:.2f} |",
         f"| ACC | {acc_t[0]:.0f} | {acc_t[-1]:.0f} | {(acc_t[-1] - acc_t[0]) / 1000:.2f} |",
         f"| HR（RR 累加） | {hr_t[0]:.0f} | {hr_t[-1]:.0f} | {(hr_t[-1] - hr_t[0]) / 1000:.2f} |",
         f"| GPS（手机 1 Hz） | {gps_t[0]:.0f} | {gps_t[-1]:.0f} | {(gps_t[-1] - gps_t[0]) / 1000:.2f} |", "",
         f"- 估计 1（末端对齐，假设各路同时停止、GPS 从记录开始）：ECG 起点 ≈ 记录开始后 **{est1:.1f} s**",
         f"- 估计 2（HR 对齐，假设 HR 从记录开始、RR 累加为真实时间）：ECG 起点 ≈ HR 轴 **{est2:.1f} s**",
         f"- HR 前 {sum(1 for r in hr if r[3] == 0)} 行皮肤接触 0；RR>1500 ms：{[int(r[1]) for r in hr if r[1] > 1500]}",
         "",
         "两种估计都 < 30 s，但**都不是 0**，且依赖未核实的假设：",
         "App 若在按「开始记录」之前就已连接并推流，真实的「启动命令 → 首帧」延迟被隐藏，导出里看不出来。",
         "要直接比较，只能抓手机蓝牙 HCI 日志（见 H10启动延迟_根因判据_测前写定.md 实验 D）。"]
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
