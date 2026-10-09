"""V2 第 2 段判据 3 失败（D1 极性 P/N=1.05）的原因诊断。只读日志、只画图，不改 h10_rpeak 的算法与判定。

用法：python h10_v2_seg2_diag.py
输出：诊断输出/H10_V2第2段极性诊断_*.png 与终端数字

做法：三段并排比较。
  ① 逐 2 s 窗的 P（最大值）与 N（−最小值）随时间变化：是整段都分不清，还是某段时间变了
  ② 漏检位置：ECG 检出间期 > 1.5 × HR 服务 RR 中位的地方
  ③ 每段挑几个 4 s 片段看波形本身（R 波朝向、T 波高度、噪声）
  ④ ACC 逐窗标准差：有没有动
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "诊断输出"
sys.path.insert(0, str(HERE))
D = HERE / "logs" / "V2_20261009"
SEGS = [("段1 08:22", D / "Cow_UNKNOWN_vitalsigns_20261009_082228_to_082728" / "h10_20261009_082222.log"),
        ("段2 08:29", D / "Cow_UNKNOWN_vitalsigns_20261009_082920_to_083420" / "h10_20261009_082913.log"),
        ("段3 08:36", D / "Cow_UNKNOWN_vitalsigns_20261009_083658_to_084158" / "h10_20261009_083651.log")]


def load(path):
    from h10_parse import ACC, ECG, frames_to_series, parse_hr, parse_pmd, read_log
    from h10_rpeak import FS_NK, WIN_S, detect
    _, recs = read_log(str(path))
    rr_hr, fe, fa = [], [], []
    for rt, _, s, d in recs:
        if s == "HR":
            rr_hr += parse_hr(d)[2]
        elif s == "PMD":
            mt, ts, _, smp = parse_pmd(d, {})
            if smp is not None and len(smp):
                (fe if mt == ECG else fa if mt == ACC else []).append((rt, ts, smp))
    ecg = frames_to_series(fe, 130)
    acc = frames_to_series(fa, 200) if fa else None
    v = ecg["v"][:, 0] / 1000.0
    det = detect(v)
    clean = det["clean"]
    n = int(round(WIN_S * FS_NK))
    k = len(clean) // n
    seg = clean[:k * n].reshape(k, n)
    win = dict(t=(np.arange(k) + 0.5) * WIN_S, P=seg.max(axis=1), N=-seg.min(axis=1))
    t = (ecg["t"] - ecg["t"][0]) / 1e9
    return dict(t=t, v=v, det=det, win=win, rr_hr=np.asarray(rr_hr, float), acc=acc, fs=ecg["fs"])


def acc_std(acc, t0_ns, wins=10.0):
    ta = (acc["t"] - t0_ns) / 1e9
    mag = np.linalg.norm(acc["v"], axis=1)
    edges = np.arange(0, ta[-1] + wins, wins)
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (ta >= a) & (ta < b)
        out.append((a + wins / 2, float(np.std(mag[m])) if m.sum() > 10 else np.nan))
    return np.array(out)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    from pipeline import plotting
    import matplotlib.pyplot as plt
    plotting.setup()
    data = []
    for name, p in SEGS:
        r = load(p)
        from h10_parse import frames_to_series  # noqa
        data.append((name, r))
        w, det = r["win"], r["det"]
        pk = det["peaks"]
        ipi = np.diff(r["t"][pk]) * 1000
        rrm = np.median(r["rr_hr"])
        miss = ipi > 1.5 * rrm
        extra = ipi < 0.6 * rrm
        ratio_w = w["P"] / w["N"]
        print(f"== {name}  fs {r['fs']:.3f}  ECG {r['t'][-1]:.0f} s")
        print(f"  整段 P {det['P']:.3f} / N {det['N']:.3f} mV  比值 {det['ratio']:.2f}  取{'正' if det['sign']>0 else '负'}向")
        q = np.percentile(ratio_w, [5, 25, 50, 75, 95])
        print(f"  逐窗 P/N 分位 5/25/50/75/95：{np.round(q, 2)}；P>N 的窗占 {np.mean(ratio_w > 1)*100:.0f}%")
        for a in range(0, int(w['t'][-1]) + 1, 60):
            m = (w["t"] >= a) & (w["t"] < a + 60)
            if m.any():
                print(f"    {a:3d}–{a+60:3d} s：P 中位 {np.median(w['P'][m]):.3f}  N 中位 {np.median(w['N'][m]):.3f}"
                      f"  比值 {np.median(w['P'][m])/np.median(w['N'][m]):.2f}")
        print(f"  HR RR 中位 {rrm:.0f} ms（{60000/rrm:.0f} bpm）；检出峰 {len(pk)}；"
              f"漏检嫌疑间期（>1.5×）{miss.sum()} 处、多检嫌疑（<0.6×）{extra.sum()} 处")
        if miss.any():
            tm = r["t"][pk][:-1][miss]
            print(f"    漏检位置（s）前 15 个：{np.round(tm[:15], 0)}")
        r["miss_t"] = r["t"][pk][:-1][miss]
        r["extra_t"] = r["t"][pk][:-1][extra]
        if r["acc"] is not None:
            r["accstd"] = acc_std(r["acc"], r["acc"]["t"][0])
            s = r["accstd"][:, 1]
            print(f"  ACC |a| 逐 10 s 标准差：中位 {np.nanmedian(s):.1f}、最大 {np.nanmax(s):.1f}（mg 原始单位）")

    # 图 1：三段逐窗 P、N、ACC 并排
    fig, ax = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    for i, (name, r) in enumerate(data):
        w = r["win"]
        ax[i].plot(w["t"], w["P"], lw=0.8, label="P：窗内最大值（正向）")
        ax[i].plot(w["t"], w["N"], lw=0.8, label="N：窗内 −最小值（负向）")
        for tm in r["miss_t"]:
            ax[i].axvline(tm, color="r", alpha=0.25, lw=0.8)
        ax[i].set_ylabel("mV（清洗后）")
        ax[i].set_title(f"{name}：整段 P/N={r['det']['ratio']:.2f}，红线 = 漏检嫌疑位置", loc="left")
        if "accstd" in r:
            a2 = ax[i].twinx()
            a2.plot(r["accstd"][:, 0], r["accstd"][:, 1], "k.--", lw=0.6, alpha=0.5, label="ACC |a| 10 s 标准差")
            a2.set_ylabel("ACC 标准差（原始单位）")
            a2.legend(loc="upper right", fontsize=8)
        ax[i].legend(loc="upper left", fontsize=8)
    ax[-1].set_xlabel("ECG 传感器时刻 s（自首样本起）")
    fig.tight_layout()
    f1 = OUT / "H10_V2第2段极性诊断_逐窗PN.png"
    fig.savefig(f1, dpi=110)

    # 图 2：每段 4 个 4 s 片段（60/120/180/240 s 处），原始 ECG + 清洗后 + 检出峰
    fig, ax = plt.subplots(3, 4, figsize=(18, 9), sharey=True)
    for i, (name, r) in enumerate(data):
        det = r["det"]
        for j, a in enumerate((60, 120, 180, 240)):
            m = (r["t"] >= a) & (r["t"] < a + 4)
            ax[i, j].plot(r["t"][m], r["v"][m] - np.median(r["v"][m]), lw=0.7, color="0.6", label="原始（去中位）")
            ax[i, j].plot(r["t"][m], det["clean"][m], lw=0.9, label="清洗后")
            pm = det["peaks"][(r["t"][det["peaks"]] >= a) & (r["t"][det["peaks"]] < a + 4)]
            ax[i, j].plot(r["t"][pm], det["clean"][pm], "rv", label="检出峰")
            ax[i, j].axhline(0, color="k", lw=0.4)
            ax[i, j].set_title(f"{name}  {a}–{a+4} s", fontsize=9, loc="left")
            if j == 0:
                ax[i, j].set_ylabel("mV")
    ax[0, 0].legend(fontsize=7)
    fig.tight_layout()
    f2 = OUT / "H10_V2第2段极性诊断_波形片段.png"
    fig.savefig(f2, dpi=110)

    # 图 3：叠加平均（以 HR 不可用时用检出峰；这里用检出峰对齐，看每段一拍的平均形状）
    fig, ax = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
    for i, (name, r) in enumerate(data):
        c, pk = r["det"]["clean"], r["det"]["peaks"]
        pre, post = 40, 80
        segs = np.array([c[p - pre:p + post] for p in pk if p - pre >= 0 and p + post <= len(c)])
        tt = (np.arange(-pre, post)) / 130 * 1000
        for s in segs[::10]:
            ax[i].plot(tt, s, color="0.8", lw=0.4)
        ax[i].plot(tt, segs.mean(axis=0), lw=1.6, label=f"平均（{len(segs)} 拍）")
        ax[i].axvline(0, color="r", lw=0.6)
        ax[i].set_title(f"{name}：以检出峰对齐的一拍（取{'正' if r['det']['sign']>0 else '负'}向）", fontsize=9, loc="left")
        ax[i].set_xlabel("相对检出峰 ms")
        ax[i].legend(fontsize=8)
    ax[0].set_ylabel("mV（清洗后，未乘极性）")
    fig.tight_layout()
    f3 = OUT / "H10_V2第2段极性诊断_叠加平均.png"
    fig.savefig(f3, dpi=110)
    print(f"\n→ {f1}\n→ {f2}\n→ {f3}")


if __name__ == "__main__":
    main()
