"""把 Pi 上 h10_logger.py 录的原始日志转成与手机 Polar Equine 导出**同格式**的 HR / ECG / ACC 三个 txt。

用法：
    python h10_export.py <h10_xxx.log> [<h10_yyy.log> …] [--out 目录]
    默认输出到 心率带数据/Pi导出_<日志时间>/（不和手机导出混在同一目录，免得 glob 取错文件）

格式照抄 心率带数据/ 里的手机导出（2026-09-28 那份）：文件头 # 行、空行、列名行、逗号+空格分隔。
解码复用 h10_parse.py（与验收同一套，不另写）。原始日志只读。

与手机导出的对应关系（「推断」= 手机导出只看得到结果，看不到它怎么算的）：
- HR：每个 RR 一行，心率与皮肤接触取该 RR 所在的那条通知；不带 RR 的通知不出行（推断：手机约每拍一行）。
  RR = 1/1024 s 计数换成 ms 后四舍五入到整数（手机 55 个 RR 全能由计数四舍五入得到，向下取整只有 47%）。
  MS = RR 逐项累加（手机导出已核实完全相等），**不是真实时钟**，与手机同样有「一个伪 RR 推偏后面全部」的缺陷。
  SC = 皮肤接触位（0x2A37 flags bit1-2 == 3 记 1，否则 0）
- ECG：µV 整数 ÷ 1000 → mV，写成最短小数（手机同样最多 3 位小数、从不写整数）。换算系数按 1.0（推断，
  H10 设置回应里没有类型 5；同时对照未做）
- ACC：mg 整数照写；文件头采样率/量程取 logger 实际发给 H10 的设置（手机那份是 100 Hz，Pi 默认 200 Hz）
- ECG、ACC 的 MS：H10 传感器时间戳，以两路里**更早的首样本**为 0，四舍五入到整数 ms → 两路同一时间轴
  （手机那份也是同一时间轴：ECG 从 505、ACC 从 10 起）。每样本时刻按「帧时间戳 = 帧末样本」推断，与 h10_parse 相同
- 文件头 Collection Timestamp 取日志 start_local，写成手机的「2026.9.28 上午8.52.03」样式（下午按 12 小时制，推断）；
  Version 行 Pi 日志没有（logger 未读设备信息服务），如实写「未读取」

手机格式装不下、只在原始日志里的：Pi 到达时刻（与雷达 pcap 对时要用它）、H10 绝对时间戳、逐帧连续性。
这些仍以日志 + h10_parse.py 为准，本脚本的 txt 只用于沿用手机格式的分析。
"""
import argparse
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from h10_parse import ACC, ECG, frames_to_series, parse_hr, parse_pmd, parse_settings, read_log  # noqa: E402


def collection_stamp(start_local):
    """'2026-09-29 09:55:56 +0800' → '2026.9.29 上午9.55.56'（手机样式：月日时不补零，分秒补零）"""
    t = datetime.strptime(start_local[:19], "%Y-%m-%d %H:%M:%S")
    ampm = "上午" if t.hour < 12 else "下午"
    h12 = t.hour if t.hour <= 12 else t.hour - 12
    return f"{t.year}.{t.month}.{t.day} {ampm}{h12}.{t.minute:02d}.{t.second:02d}"


def round_half_up(x):
    return int(math.floor(x + 0.5))


def fmt_mv(uv):
    """整数 µV → mV 最短小数：-310 → '-0.31'，0 → '0.0'，1000 → '1.0'"""
    return repr(int(uv) / 1000)


def decode(path):
    head, recs = read_log(path)
    settings, last_tx = {}, None
    for rt, mono, src, d in recs:
        if src == "CP_TX":
            last_tx = d
        elif src == "CP_RX" and last_tx is not None and last_tx[0] == 1 and len(d) > 5:
            settings[last_tx[1]] = parse_settings(d)

    hr_rows = []                       # (心率, SC, RR 整数 ms)
    for rt, _, s, d in recs:
        if s == "HR":
            hr, contact, rr = parse_hr(d)
            sc = 1 if contact == 3 else 0
            hr_rows += [(hr, sc, round_half_up(x)) for x in rr]

    frames, ftypes = {ECG: [], ACC: []}, {ECG: set(), ACC: set()}
    for rt, _, s, d in recs:
        if s == "PMD":
            mtype, ts, ftype, smp = parse_pmd(d, settings.get(d[0] & 0x3F, {}))
            if smp is not None and len(smp):
                frames[mtype].append((rt, ts, smp))
                ftypes[mtype].add(ftype)
    return head, hr_rows, frames, ftypes


def write_txt(path, header, cols, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(header) + "\n\n" + cols + "\n")
        for r in rows:
            f.write(", ".join(r) + "\n")


def export(path, out_root):
    head, hr_rows, frames, ftypes = decode(path)
    stamp = collection_stamp(head["start_local"])
    dev = head.get("device", "")
    dev_id = next((w for w in dev.split() if len(w) == 8 and all(c in "0123456789ABCDEF" for c in w)), "未知")
    common = [f"# Collection Timestamp: {stamp}",
              f"# Device Info: ID {dev_id}, Version 未读取（Pi 日志不含）",
              f"# Application Version: h10_export.py ← {Path(path).name}"]
    out = Path(out_root) if out_root else HERE / "心率带数据" / f"Pi导出_{Path(path).stem.replace('h10_', '')}"
    out.mkdir(parents=True, exist_ok=True)
    fname = stamp.replace(" ", "_")
    notes = []

    # HR
    ms = np.cumsum([r[2] for r in hr_rows]).tolist()
    write_txt(out / f"HR_{fname}.txt",
              ["# File: Heart Rate data", *common, "# Columns:",
               "# 1. Heart Rate (beats per minute) (HR)",
               "# 2. RR interval (time between two beats) in milliseconds (RR)",
               "# 3. Measurement sample timestamps in milliseconds (MS)",
               "# 4. Skin Contact Status (0 = false, 1 = true) (SC)"],
              "HR, RR, MS, SC",
              [(str(h), str(rr), str(m), str(sc)) for (h, sc, rr), m in zip(hr_rows, ms)])
    notes.append(f"HR：{len(hr_rows)} 行（每个 RR 一行）")

    if not frames[ECG] or not frames[ACC]:
        notes.append(f"ECG 帧 {len(frames[ECG])}、ACC 帧 {len(frames[ACC])}：有一路为空，不写 ECG/ACC")
        return out, notes
    for m, name in ((ECG, "ECG"), (ACC, "ACC")):
        if any(ft & 0x80 for ft in ftypes[m]):
            notes.append(f"**警告**：{name} 有压缩帧（delta 解码未经验证），数值需另行核对")

    ecg = frames_to_series(frames[ECG], 130)
    acc = frames_to_series(frames[ACC], None)
    t0 = min(ecg["t"][0], acc["t"][0])
    ecg_ms = [round_half_up(x) for x in (ecg["t"] - t0) / 1e6]
    acc_ms = [round_half_up(x) for x in (acc["t"] - t0) / 1e6]

    write_txt(out / f"ECG_{fname}.txt",
              ["# File: Electrocardiogram data", *common, "# Columns:",
               "# 1. Raw ECG voltage in millivolts (ECG)",
               "# 3. Measurement sample timestamps in milliseconds (MS)"],
              "ECG, MS",
              [(fmt_mv(v), str(t)) for v, t in zip(ecg["v"][:, 0], ecg_ms)])

    acc_set = dict(kv.split(":") for kv in head.get("ACC_settings", "").split())
    write_txt(out / f"ACC_{fname}.txt",
              ["# File: Accelerometer data", *common, "# Sensor Details: ",
               f"# - Sampling Frequency (Hz): {acc_set.get('0', '?')}",
               f"# - Accelerometer Range: +-{acc_set.get('2', '?')}g",
               "# Columns:",
               "# 1. Acceleration X-axis (milli-g) (ACCX)",
               "# 2. Acceleration Y-axis (milli-g) (ACCY)",
               "# 3. Acceleration Z-axis (milli-g) (ACCZ)",
               "# 4. Measurement sample timestamps in milliseconds (MS)"],
              "ACCX, ACCY, ACCZ, MS",
              [(str(int(x)), str(int(y)), str(int(z)), str(t)) for (x, y, z), t in zip(acc["v"], acc_ms)])
    notes.append(f"ECG：{len(ecg_ms)} 行，实测 {ecg['fs']:.2f} Hz，MS {ecg_ms[0]}–{ecg_ms[-1]}")
    notes.append(f"ACC：{len(acc_ms)} 行，实测 {acc['fs']:.2f} Hz（标称 {acc_set.get('0', '?')}），MS {acc_ms[0]}–{acc_ms[-1]}")
    return out, notes


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--out", default=None, help="输出目录；多个日志时忽略，各自用默认目录")
    a = ap.parse_args()
    for p in a.logs:
        out, notes = export(p, a.out if len(a.logs) == 1 else None)
        print(f"{Path(p).name} → {out}")
        for n in notes:
            print("  " + n)
