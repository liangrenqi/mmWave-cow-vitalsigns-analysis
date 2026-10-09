"""离线解析 Pi 上 h10_logger.py 录的原始日志，并按 `H10第一步判据_采集前写定.md` 验收。

用法：
    python h10_parse.py <h10_xxx.log>        # 输出到 诊断输出/H10_<时间>_*
    python h10_parse.py --selftest           # 只测 delta 解码的位打包

协议依据：`polarofficial polar-ble-sdk master technical_documentation/online_measurement.pdf`
（下称「文档」）与蓝牙 SIG 心率服务规范。文档未写明、按社区实现推断的地方在代码里标「推断」。
"""
import math
import struct
import sys
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
OUT = HERE / "诊断输出"
EPOCH_2000_NS = 946684800 * 10**9            # 文档 4.1：时间戳自 2000-01-01 UTC 起的纳秒
ECG, ACC = 0, 2
SETTING_SIZE = {0: 2, 1: 2, 2: 2, 4: 1, 5: 4}


# ---------------- 读日志 ----------------
def read_log(path):
    head, recs = {}, []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            k, _, v = line[2:].partition("=")
            head[k] = v
        elif line.strip():
            rt, mono, src, hx = (line.split() + [""])[:4]
            recs.append((int(rt), int(mono), src, bytes.fromhex(hx)))
    return head, recs


def parse_settings(resp):
    out, i = {}, 5
    while i + 2 <= len(resp):
        t, cnt = resp[i], resp[i + 1]
        size = SETTING_SIZE.get(t)
        if size is None or i + 2 + cnt * size > len(resp):
            break
        out[t] = [struct.unpack("<f", resp[i + 2 + j * 4:i + 6 + j * 4])[0] if t == 5
                  else int.from_bytes(resp[i + 2 + j * size:i + 2 + (j + 1) * size], "little")
                  for j in range(cnt)]
        i += 2 + cnt * size
    return out


# ---------------- 标准心率 0x2A37 ----------------
def parse_hr(d):
    """蓝牙 SIG 心率测量：flags bit0 心率 16 位；bit1-2 皮肤接触；bit3 能量；bit4 RR（1/1024 s）。"""
    f, i = d[0], 1
    if f & 1:
        hr = int.from_bytes(d[1:3], "little"); i = 3
    else:
        hr = d[1]; i = 2
    contact = (f >> 1) & 3            # 3 = 支持且接触，2 = 支持未接触，0/1 = 不支持
    if f & 8:
        i += 2
    rr = [int.from_bytes(d[j:j + 2], "little") / 1024 * 1000 for j in range(i, len(d) - 1, 2)] if f & 16 else []
    return hr, contact, rr


# ---------------- PMD ----------------
def signed(v, bits):
    return v - (1 << bits) if v & (1 << (bits - 1)) else v


def decode_delta(payload, channels, res_bits):
    """文档 4.3.2–4.3.3。参考样本占 channels×ceil(res/8) 字节（小端有符号），
    之后若干块：[delta 位宽 1B][样本数 1B][位流]。位流按字节内低位在前展开（推断：
    文档未写位序，按 Polar SDK 用的 BitSet.valueOf 语义），每个 delta 有符号。"""
    nb = math.ceil(res_bits / 8)
    ref = [signed(int.from_bytes(payload[c * nb:(c + 1) * nb], "little"), nb * 8) for c in range(channels)]
    out, prev, i = [ref], ref, channels * nb
    while i + 2 <= len(payload):
        width, count = payload[i], payload[i + 1]
        i += 2
        nbytes = math.ceil(width * count * channels / 8)
        bits = int.from_bytes(payload[i:i + nbytes], "little")
        i += nbytes
        pos = 0
        for _ in range(count):
            cur = []
            for c in range(channels):
                v = signed((bits >> pos) & ((1 << width) - 1), width) if width else 0
                pos += width
                cur.append(prev[c] + v)
            out.append(cur)
            prev = cur
    return out


def parse_pmd(d, settings):
    """文档表 6：[0] 测量类型 &0x3F、[1:9] 时间戳 uint64 ns、[9] 帧类型（bit7 = 压缩）、[10:] 数据。"""
    mtype, ts, ftype = d[0] & 0x3F, int.from_bytes(d[1:9], "little"), d[9]
    comp, ft, p = bool(ftype & 0x80), ftype & 0x7F, d[10:]
    if mtype == ECG:
        if comp:
            raise ValueError("ECG 压缩帧：文档未给 H10 例子，需单独实现")
        samples = [[signed(int.from_bytes(p[j:j + 3], "little"), 24)] for j in range(0, len(p) - 2, 3)]
    elif mtype == ACC:
        if comp:
            samples = decode_delta(p, 3, settings.get(1, [16])[0])
        else:
            w = {0: 1, 1: 2, 2: 3}[ft]
            samples = [[signed(int.from_bytes(p[j + c * w:j + (c + 1) * w], "little"), w * 8) for c in range(3)]
                       for j in range(0, len(p) - 3 * w + 1, 3 * w)]
    else:
        return mtype, ts, ftype, None
    return mtype, ts, ftype, np.array(samples, dtype=float)


# ---------------- 验收 ----------------
def frames_to_series(frames, fs_nominal):
    """frames: [(到达realtime_ns, 传感器ts_ns, 样本数组)]。
    推断：时间戳是帧内**最后一个**样本的时刻（社区实现做法，文档未写）。
    用相邻帧时间戳差 / 样本数估真实采样率，再给每个样本分配传感器时刻。"""
    ts = np.array([f[1] for f in frames], dtype=np.int64)
    n = np.array([len(f[2]) for f in frames])
    dts = np.diff(ts)
    # 真实采样间隔：用全程 (最后帧ts − 首帧ts) / 其间样本数
    period = (ts[-1] - ts[0]) / n[1:].sum()
    # 缺口：相邻帧 ts 差 − 本帧样本数×间隔，超 2 个采样间隔即计丢帧
    gap = dts - n[1:] * period
    t_samp = np.concatenate([f[1] - (len(f[2]) - 1 - np.arange(len(f[2]))) * period for f in frames])
    vals = np.concatenate([f[2] for f in frames])
    arrive = np.array([f[0] for f in frames], dtype=np.int64)
    return dict(ts=ts, n=n, period=period, fs=1e9 / period, gap=gap, t=t_samp, v=vals, arrive=arrive,
                fs_nominal=fs_nominal)


def lower_envelope_fit(ts, arrive):
    """到达时刻 = 传感器时刻×(1+漂移) + 偏移 + 延迟(≥0)。取每 10 秒窗内最小的(到达−传感器)做直线，
    得偏移与漂移；延迟 = 到达 − 拟合线。"""
    d = (arrive - ts).astype(float)
    t = (ts - ts[0]) / 1e9
    win = np.floor(t / 10).astype(int)
    xs, ys = [], []
    for w in np.unique(win):
        m = win == w
        k = np.argmin(d[m])
        xs.append(t[m][k]); ys.append(d[m][k])
    if len(xs) >= 2:
        slope, icpt = np.polyfit(xs, ys, 1)
    else:
        slope, icpt = 0.0, float(np.min(d))
    lat = d - (icpt + slope * t)
    return slope / 1e9 * 1e6, icpt, lat          # 漂移 ppm、偏移 ns、延迟 ns


def analyse(path):
    head, recs = read_log(path)
    stamp = Path(path).stem.replace("h10_", "")
    L = [f"# H10 第一步验收：{Path(path).name}\n", "判据见 `H10第一步判据_采集前写定.md`，本报告只执行不改判据。\n"]
    for k in ("start_local", "device", "bleak", "mtu", "ECG_settings", "ACC_settings", "counts"):
        L.append(f"- {k}：{head.get(k, '（无）')}")

    # 设置：取每类测量「读设置」回应里的换算系数等
    settings, last_tx = {}, None
    for rt, mono, src, d in recs:
        if src == "CP_TX":
            last_tx = d
        elif src == "CP_RX" and last_tx is not None and last_tx[0] == 1 and len(d) > 5:
            settings[last_tx[1]] = parse_settings(d)
    L.append(f"- 读到的设置回应：{settings}")

    ev = [(rt, d.decode()) for rt, _, s, d in recs if s == "EV"]
    L.append(f"- 事件：{[e for _, e in ev]}")
    rt_all = np.array([r[0] for r in recs if r[2] in ("HR", "PMD")], dtype=np.int64)
    mo_all = np.array([r[1] for r in recs if r[2] in ("HR", "PMD")], dtype=np.int64)
    dur = (rt_all[-1] - rt_all[0]) / 1e9
    step = (rt_all - mo_all) - (rt_all[0] - mo_all[0])
    L.append(f"- 时长 {dur:.1f} s；REALTIME−MONOTONIC 变化范围 {step.min()/1e6:+.3f} ~ {step.max()/1e6:+.3f} ms")

    # HR
    hr_rows = []
    for rt, _, s, d in recs:
        if s == "HR":
            hr, contact, rr = parse_hr(d)
            hr_rows.append((rt, hr, contact, rr))
    rr_all = [x for r in hr_rows for x in r[3]]

    # PMD
    frames = {ECG: [], ACC: []}
    ftypes = {ECG: set(), ACC: set()}
    for rt, _, s, d in recs:
        if s == "PMD":
            mtype, ts, ftype, smp = parse_pmd(d, settings.get(d[0] & 0x3F, {}))
            if smp is not None and len(smp):
                frames[mtype].append((rt, ts, smp))
                ftypes[mtype].add(ftype)

    res = {}
    L.append("\n## 判据 1 三路都启动\n")
    ok1 = len(hr_rows) > 0 and len(frames[ECG]) > 0 and len(frames[ACC]) > 0
    L.append(f"HR 通知 {len(hr_rows)}、ECG 帧 {len(frames[ECG])}、ACC 帧 {len(frames[ACC])}；"
             f"帧类型 ECG {sorted(ftypes[ECG])} ACC {sorted(hex(x) for x in ftypes[ACC])} → **{'通过' if ok1 else '不通过'}**")
    res[1] = ok1
    if not ok1:
        return L, stamp, None

    ecg = frames_to_series(frames[ECG], 130)
    acc = frames_to_series(frames[ACC], None)
    fac_acc = settings.get(ACC, {}).get(5, [1.0])[0]
    fac_ecg = settings.get(ECG, {}).get(5, [1.0])[0]
    L.append(f"\n换算系数（设置类型 5）：ECG {fac_ecg}、ACC {fac_acc}（缺省 1.0）")

    L.append("\n## 判据 2 无丢帧（传感器时间戳连续）\n")
    ok2 = True
    for name, s in (("ECG", ecg), ("ACC", acc)):
        bad = np.abs(s["gap"]) > 2 * s["period"]
        ok2 &= not bad.any()
        L.append(f"{name}：{len(s['n'])} 帧、{s['n'].sum()} 样本，每帧样本数 {sorted(set(s['n'].tolist()))}，"
                 f"实测采样率 {s['fs']:.3f} Hz；|缺口|>2 个采样间隔 {bad.sum()} 处，"
                 f"最大 {np.abs(s['gap']).max()/1e6:.2f} ms")
    L.append(f"→ **{'通过' if ok2 else '不通过'}**")
    res[2] = ok2

    L.append("\n## 判据 3 RR 与 ECG R 峰逐拍一致\n")
    v = ecg["v"][:, 0] * fac_ecg / 1000.0            # µV → mV
    fs = ecg["fs"]
    pk, _ = find_peaks(v, height=np.percentile(v, 99) * 0.5, distance=int(0.33 * fs))
    rr_ecg = np.diff(ecg["t"][pk]) / 1e6               # ms
    rr_hr = np.array(rr_all)
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
    if best:
        med, off, n, dd = best
        frac = np.mean(np.abs(dd) <= 16)
        ok3 = med <= 8 and frac >= 0.90
        L.append(f"HR 的 RR {len(rr_hr)} 个、ECG R 峰 {len(pk)} 个；最佳错位 {off} 拍、比对 {n} 拍："
                 f"|差| 中位 {med:.1f} ms、均值 {np.abs(dd).mean():.1f} ms、|差|≤16 ms 占 {frac*100:.1f}% → "
                 f"**{'通过' if ok3 else '不通过'}**")
    else:
        ok3 = False
        L.append("可比对的拍数不足 20 → **不通过**")
    res[3] = ok3

    L.append("\n## 判据 4 ACC 静止时模长约 1 g\n")
    a3 = acc["v"] * fac_acc
    mag = np.linalg.norm(a3, axis=1)
    ok4 = 950 <= np.median(mag) <= 1050
    L.append(f"模长中位 {np.median(mag):.1f} mg（5–95 分位 {np.percentile(mag,5):.0f}–{np.percentile(mag,95):.0f}）"
             f"，三轴中位 {np.median(a3,axis=0).round(0).tolist()} → **{'通过' if ok4 else '不通过'}**")
    res[4] = ok4

    L.append("\n## 判据 5 ECG 幅度合理\n")
    ramp = np.median(v[pk]) if len(pk) else 0
    ok5 = 0.3 <= ramp <= 5
    L.append(f"R 峰幅度中位 {ramp:.3f} mV（以 {fac_ecg} 换算、µV 转 mV）→ **{'通过' if ok5 else '不通过'}**")
    res[5] = ok5

    L.append("\n## 判据 6 采集中未被调钟\n")
    ok6 = np.abs(step).max() < 1e6
    L.append(f"REALTIME−MONOTONIC 最大变化 {np.abs(step).max()/1e6:.3f} ms（<1 ms 通过）→ **{'通过' if ok6 else '不通过'}**")
    res[6] = ok6

    L.append("\n## 记录项（不判定，第 3 步对时用）\n")
    for name, s in (("ECG", ecg), ("ACC", acc)):
        ppm, icpt, lat = lower_envelope_fit(s["ts"], s["arrive"])
        L.append(f"{name}：传感器时间戳按 2000 纪元解读 = {(s['ts'][0]+EPOCH_2000_NS)/1e9:.0f} s Unix"
                 f"（与 Pi 时钟差 {(s['arrive'][0]-s['ts'][0]-EPOCH_2000_NS)/1e9:+.1f} s，大则说明 H10 时钟未设）；"
                 f"相对 Pi 漂移 {ppm:+.1f} ppm；到达延迟（相对下包络）中位 {np.median(lat)/1e6:.1f} ms、"
                 f"95 分位 {np.percentile(lat,95)/1e6:.1f} ms、最大 {lat.max()/1e6:.1f} ms")
        dd = np.diff(s["ts"]) / 1e6
        L.append(f"{name}：相邻帧时间戳差 {dd.min():.1f}–{dd.max():.1f} ms（每帧样本数恒定时分不出时间戳是首样本还是末样本）")
    L.append(f"心率 {min(r[1] for r in hr_rows)}–{max(r[1] for r in hr_rows)} bpm；"
             f"皮肤接触值 {sorted(set(r[2] for r in hr_rows))}（3 = 接触良好）")

    L.append(f"\n## 总判：{'**第一步通过**' if all(res.values()) else '**未通过**：' + '、'.join(f'判据{k}' for k, v_ in res.items() if not v_)}")

    # 落文件：逐样本 csv
    base = OUT / f"H10_{stamp}"
    np.savetxt(f"{base}_ECG.csv", np.c_[ecg["t"] / 1e6, v], delimiter=",", fmt=["%.3f", "%.4f"],
               header="传感器时刻ms,ECG_mV", comments="", encoding="utf-8")
    np.savetxt(f"{base}_ACC.csv", np.c_[acc["t"] / 1e6, a3], delimiter=",", fmt=["%.3f", "%.1f", "%.1f", "%.1f"],
               header="传感器时刻ms,X_mg,Y_mg,Z_mg", comments="", encoding="utf-8")
    with open(f"{base}_HR.csv", "w", encoding="utf-8-sig") as f:
        f.write("Pi到达realtime_ns,心率bpm,皮肤接触,RR_ms\n")
        for rt, hr, c, rr in hr_rows:
            f.write(f"{rt},{hr},{c},{' '.join(f'{x:.1f}' for x in rr)}\n")
    return L, stamp, (ecg, acc, v, pk, rr_hr, rr_ecg)


def plot(stamp, data):
    from pipeline import plotting
    import matplotlib.pyplot as plt
    plotting.setup()
    ecg, acc, v, pk, rr_hr, rr_ecg = data
    fig, ax = plt.subplots(3, 1, figsize=(14, 10))
    t = (ecg["t"] - ecg["t"][0]) / 1e9
    m = t < 10
    ax[0].plot(t[m], v[m], lw=0.7); ax[0].plot(t[pk][t[pk] < 10], v[pk][t[pk] < 10], "rv")
    ax[0].set_xlabel("传感器时刻 s"); ax[0].set_ylabel("mV"); ax[0].set_title("① ECG 前 10 秒与检出的 R 峰", loc="left")
    ax[1].plot(rr_hr, ".-", label="HR 服务 RR"); ax[1].plot(rr_ecg, ".-", alpha=0.7, label="ECG R 峰间期")
    ax[1].set_xlabel("拍序号"); ax[1].set_ylabel("ms"); ax[1].legend()
    ax[1].set_title("② 两路逐拍间期（未对齐错位，仅看形状）", loc="left")
    ta = (acc["t"] - acc["t"][0]) / 1e9
    ax[2].plot(ta, acc["v"], lw=0.6); ax[2].set_xlabel("传感器时刻 s"); ax[2].set_ylabel("mg（未乘换算系数）")
    ax[2].set_title("③ ACC 三轴", loc="left")
    fig.tight_layout(); fig.savefig(OUT / f"H10_{stamp}_总览.png", dpi=110)


def selftest():
    """位打包往返：按本文件假定的格式编码再解码。只证明解码器自洽，**不证明假定格式与 Polar 一致**
    ——那要靠真实数据的判据 4（静止 1 g、曲线平滑）来证。"""
    rng = np.random.default_rng(0)
    ref = [100, -200, 1000]
    width, count = 7, 20
    deltas = rng.integers(-60, 60, size=(count, 3))
    payload = b"".join(int(r & 0xFFFF).to_bytes(2, "little") for r in ref)
    bits, pos = 0, 0
    for row in deltas:
        for dv in row:
            bits |= (int(dv) & ((1 << width) - 1)) << pos
            pos += width
    payload += bytes([width, count]) + bits.to_bytes(math.ceil(pos / 8), "little")
    got = np.array(decode_delta(payload, 3, 16))
    want = np.vstack([ref, ref + np.cumsum(deltas, axis=0)])
    assert np.array_equal(got, want), (got[:3], want[:3])
    hr, c, rr = parse_hr(bytes([0x16, 72, 0x00, 0x04, 0x00, 0x02]))
    assert (hr, c) == (72, 3) and rr == [1000.0, 500.0], (hr, c, rr)
    print("selftest 通过：delta 位打包往返一致；心率 8 位 + 两个 RR（1/1024 s）解析正确")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest(); sys.exit()
    sys.path.insert(0, str(HERE))
    L, stamp, data = analyse(sys.argv[1])
    (OUT / f"H10_{stamp}_验收.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    if data:
        plot(stamp, data)
