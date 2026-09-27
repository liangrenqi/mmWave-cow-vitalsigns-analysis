"""实验 0：静态角反射器分析。判据见 `实验0判据_分析前写定.md`（commit 842b87e），本脚本只执行不改判据。

输出全部写到 诊断输出/实验0_*。
用法：python exp0_reflector.py
"""
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import vsp_core
import explain_one as eo          # 复用 displacement_mm / bandpass，与批次 2 同一定义
from pipeline import plotting
import matplotlib.pyplot as plt

B3 = HERE / "data" / "Batch_3_Experiments_Marked"
B2 = HERE / "data" / "Batch_2_Experiments_Marked"
OUT = HERE / "诊断输出"
NOISE_BINS = slice(80, 128)
HEART = (0.8, 2.0)


def load(cap):
    bins = sorted(cap.glob("*_Raw_0.bin"))
    b = str(bins[0])
    return vsp_core.build_slowtime(b, cache=b.replace(".bin", "_slowtime.npy"), verbose=False)


def info(cap):
    p = (cap / "data_info.csv").read_text(encoding="utf-8").split()
    return {"plate": int(p[4]), "dist": float(p[6]) if len(p) > 6 else np.nan,
            "note": p[7] if len(p) > 7 else ""}


def rms_amp(X, k, rx=0):
    """判据定义：五 bin 功率和开方。"""
    ks = range(max(k - 2, 0), k + 3)
    return float(np.sqrt(sum(np.mean(np.abs(X[:, rx, j]) ** 2) for j in ks)))


def noise_floor(X, rx=0):
    return float(np.abs(X[:, rx, NOISE_BINS]).mean())


def sigma_h(z):
    return float(eo.bandpass(eo.displacement_mm(z), *HEART).std())


def peak_subbin(prof, k):
    """三点抛物线插值的亚 bin 峰位（对 dB 幅度）。"""
    a, b, c = 20 * np.log10(prof[k - 1:k + 2])
    return k + 0.5 * (a - c) / (a - 2 * b + c)


def analyse(cap, d_nominal):
    X = load(cap)
    prof = np.sqrt(np.mean(np.abs(X[:, 0, :]) ** 2, axis=0))
    k0 = int(round(d_nominal / vsp_core.M_PER_BIN))
    lo, hi = max(eo.LEAK_BINS, k0 - 4), k0 + 4
    k = lo + int(np.argmax(prof[lo:hi + 1]))
    z = X[:, 0, k]
    A, N = rms_amp(X, k), noise_floor(X)
    # 辅助诊断：复数起伏的径向（相位）与幅度分量。静止目标 → 以均值为参考
    zm = z.mean()
    dz = (z - zm) * np.exp(-1j * np.angle(zm))
    return {
        "X": X, "prof": prof, "k": k,
        "目标bin": k, "亚bin峰位": round(peak_subbin(prof, k), 3),
        "测得距离m": round(peak_subbin(prof, k) * vsp_core.M_PER_BIN, 4),
        "目标幅度A": round(A, 1), "噪声底N": round(N, 1),
        "SNR_dB": round(20 * np.log10(A / N), 2),
        "心跳带位移噪声mm": round(sigma_h(z), 5),
        "心跳带_4RX": [round(sigma_h(X[:, r, k]), 5) for r in range(4)],
        "全带位移std_mm": round(float(eo.displacement_mm(z).std()), 5),
        "相干度": round(eo.coherence(z), 5),
        "径向起伏": float(np.std(dz.imag)), "幅度起伏": float(np.std(dz.real)),
    }


def write_csv(path, rows, cols):
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(str(r.get(c, "")) for c in cols) + "\n")


def main():
    plotting.setup()
    C = plotting.COLORS
    caps = sorted(p for p in B3.iterdir() if p.is_dir())
    rows = []
    for cap in caps:
        m = info(cap)
        r = analyse(cap, m["dist"])
        r.update({"采集": cap.name.split("_")[-3], "卷尺距离m": m["dist"], "板": m["plate"],
                  "备注": m["note"]})
        # 分组
        if "度" in m["note"]:
            r["组"] = "0d"
        elif cap.name.split("_")[-3] >= "151000":
            r["组"] = "0c"
        else:
            r["组"] = "0b" if m["plate"] else "0a"
        rows.append(r)
        print(r["组"], r["采集"], r["卷尺距离m"], r["目标bin"], r["SNR_dB"], r["心跳带位移噪声mm"])

    # ---------- 人体（批次 2）同定义重算 ----------
    human = []
    for cap in sorted(p for p in B2.iterdir() if p.is_dir()):
        X = load(cap)
        prof = np.sqrt(np.mean(np.abs(X[:, 0, :]) ** 2, axis=0))
        lo = max(eo.LEAK_BINS, int(0.6 / vsp_core.M_PER_BIN))
        hi = int(1.0 / vsp_core.M_PER_BIN)
        k = lo + int(np.argmax(prof[lo:hi + 1]))
        A, N = rms_amp(X, k), noise_floor(X)
        p = (cap / "data_info.csv").read_text(encoding="utf-8").split()
        human.append({"采集": cap.name.split("_")[-3], "受试者": p[0], "板": int(p[4]),
                      "目标bin": k, "目标幅度A": round(A, 1), "噪声底N": round(N, 1),
                      "SNR_dB": round(20 * np.log10(A / N), 2),
                      "心跳带位移mm": round(sigma_h(X[:, 0, k]), 5)})

    # ---------- 判据 1 ----------
    g = {k: [r for r in rows if r["组"] == k] for k in ("0a", "0b", "0c", "0d")}
    s0a = np.array([r["心跳带位移噪声mm"] for r in g["0a"]])
    snr0a = np.array([r["SNR_dB"] for r in g["0a"]])
    xs = np.array([r["SNR_dB"] for r in g["0c"]]) / 20      # log10(SNR)
    ys = np.log10([r["心跳带位移噪声mm"] for r in g["0c"]])
    slope, icpt = np.polyfit(xs, ys, 1)
    if -1.3 <= slope <= -0.7:
        mode = "热噪声主导，缩放成立"
    elif -0.3 <= slope <= 0.3:
        mode = "本底与SNR无关，反射器值为人体噪声下限"
    else:
        mode = "缩放关系不清，不外推"
    s_ref, snr_ref = float(np.median(s0a)), float(np.median(snr0a))
    for h in human:
        h["反射器外推噪声mm"] = (round(s_ref * 10 ** ((snr_ref - h["SNR_dB"]) / 20), 5)
                           if mode.startswith("热") else "")
        if mode.startswith("热"):
            h["信号超出噪声dB"] = round(20 * np.log10(h["心跳带位移mm"] / h["反射器外推噪声mm"]), 2)

    # ---------- 判据 3 ----------
    A0a = np.array([20 * np.log10(r["目标幅度A"]) for r in g["0a"]])
    A0b = np.array([20 * np.log10(r["目标幅度A"]) for r in g["0b"]])

    # ---------- 判据 4 ----------
    A12 = np.mean([r["目标幅度A"] for r in g["0c"] if r["卷尺距离m"] == 1.2])
    for r in g["0c"]:
        exp_db = 20 * np.log10(A12) + 40 * np.log10(1.2 / r["卷尺距离m"])
        r["期望幅度dB"] = round(exp_db, 2)
        r["实测幅度dB"] = round(20 * np.log10(r["目标幅度A"]), 2)
        r["亏损dB"] = round(exp_db - r["实测幅度dB"], 2)

    # ---------- 判据 5 ----------
    ang = {}
    for r in g["0d"]:
        zc = r["X"][:, :, r["k"]].mean(axis=0)            # 4 RX 复数均值
        ang[r["备注"]] = zc
    ref = [v for k_, v in ang.items() if "0度" in k_][0]
    cal = np.exp(-1j * np.angle(ref))                     # 0° 条作通道相位校准
    for r in g["0d"]:
        zc = ang[r["备注"]] * cal
        dphi = np.angle(zc[1:] * np.conj(zc[:-1]))
        r["相邻RX相位差rad"] = " / ".join(f"{v:+.3f}" for v in dphi)
        r["未校准相邻差rad"] = " / ".join(
            f"{v:+.3f}" for v in np.angle(ang[r["备注"]][1:] * np.conj(ang[r["备注"]][:-1])))
        r["_dphi"] = dphi
        r["等效角度deg"] = round(float(np.degrees(np.arcsin(np.clip(dphi.mean() / np.pi, -1, 1)))), 2)
        r["4RX幅度dB"] = " / ".join(f"{20*np.log10(abs(v)):.1f}" for v in ang[r["备注"]])

    # ---------- 辅助：径向/幅度起伏比 ----------
    for r in rows:
        r["径向_幅度起伏比"] = round(r["径向起伏"] / r["幅度起伏"], 3)
        r["心跳带_4RX"] = " / ".join(f"{v:.4f}" for v in r["心跳带_4RX"])

    cols = ["组", "采集", "卷尺距离m", "板", "备注", "目标bin", "亚bin峰位", "测得距离m",
            "目标幅度A", "噪声底N", "SNR_dB", "心跳带位移噪声mm", "心跳带_4RX", "全带位移std_mm",
            "相干度", "径向_幅度起伏比", "期望幅度dB", "实测幅度dB", "亏损dB",
            "未校准相邻差rad", "相邻RX相位差rad", "等效角度deg", "4RX幅度dB"]
    write_csv(OUT / "实验0_逐条指标.csv", rows, cols)
    write_csv(OUT / "实验0_人体对照_批次2重算.csv", human,
              ["采集", "受试者", "板", "目标bin", "目标幅度A", "噪声底N", "SNR_dB",
               "心跳带位移mm", "反射器外推噪声mm", "信号超出噪声dB"])

    # ---------- 距离拟合（补充） ----------
    dm = np.array([r["卷尺距离m"] for r in g["0a"] + g["0c"]])
    dd = np.array([r["测得距离m"] for r in g["0a"] + g["0c"]])
    a_fit, b_fit = np.polyfit(dm, dd, 1)

    # ---------- 判定汇总 ----------
    L = []
    L.append("# 实验 0 判定汇总（判据见 实验0判据_分析前写定.md @842b87e）\n")
    L.append("## 判据 1 根因\n")
    L.append(f"0a 心跳带位移噪声：{', '.join(f'{v:.4f}' for v in s0a)} mm；中位 {s_ref:.4f}，跨度 {s0a.min():.4f}–{s0a.max():.4f}")
    L.append(f"0a SNR：{', '.join(f'{v:.1f}' for v in snr0a)} dB；中位 {snr_ref:.1f}")
    L.append(f"0c 斜率 log10σ_h 对 log10SNR = {slope:.3f} → {mode}")
    hs = np.array([h["SNR_dB"] for h in human])
    hh = np.array([h["心跳带位移mm"] for h in human])
    L.append(f"人体 SNR {hs.min():.1f}–{hs.max():.1f} dB（中位 {np.median(hs):.1f}）；人体心跳带位移 {hh.min():.4f}–{hh.max():.4f} mm")
    if mode.startswith("热"):
        ex = np.array([h["反射器外推噪声mm"] for h in human])
        L.append(f"人体等效噪声（外推）{ex.min():.4f}–{ex.max():.4f} mm，中位 {np.median(ex):.4f}")
        med = np.median(ex)
        v = "SNR 不够" if med >= 0.13 else ("呼吸干扰" if med <= 0.03 else "两者兼有")
        L.append(f"**判定：{v}**（阈值 ≥0.13 SNR / ≤0.03 呼吸干扰，按中位数）")
        L.append(f"逐条：≥0.13 有 {(ex>=0.13).sum()} 条，≤0.03 有 {(ex<=0.03).sum()} 条，中间 {((ex>0.03)&(ex<0.13)).sum()} 条")
    elif mode.startswith("本底"):
        v = "SNR 不够" if s_ref >= 0.13 else ("反射器本底 ≤0.03，但只是下限，不能判呼吸干扰" if s_ref <= 0.03 else "下限落在中间区")
        L.append(f"**判定（仅下限方向）：{v}**")
    else:
        L.append("**判据 1 不判定**")
    L.append("\n## 判据 2 距离偏置\n")
    L.append(f"0a 目标 bin：{[r['目标bin'] for r in g['0a']]}（原判据：≠16 即偏置）")
    L.append(f"补充拟合：测得 = {a_fit:.4f} × 卷尺 + {b_fit:+.4f} m")
    L.append("\n## 判据 3 板损耗\n")
    L.append(f"0a 幅度 {A0a.mean():.2f} dB（跨度 {np.ptp(A0a):.2f}），0b {A0b.mean():.2f} dB（跨度 {np.ptp(A0b):.2f}）")
    L.append(f"组间差 {A0b.mean()-A0a.mean():+.2f} dB；判据 >3 dB 且 > 组内跨度")
    L.append("\n## 判据 4 HPF\n")
    for d in (0.4, 0.5, 0.65, 0.8, 1.2):
        rr = [r for r in g["0c"] if r["卷尺距离m"] == d]
        L.append(f"{d} m：亏损 {[r['亏损dB'] for r in rr]} dB，σ_h {[r['心跳带位移噪声mm'] for r in rr]} mm，bin {[r['目标bin'] for r in rr]}")
    L.append("\n## 判据 5 RX 与角度\n")
    for r in g["0d"]:
        d = r["_dphi"]
        L.append(f"{r['备注']}：校准后相邻差 {r['相邻RX相位差rad']} rad，互差 {np.ptp(d):.3f}，均值 {d.mean():+.3f}，等效 {r['等效角度deg']}°；4RX 幅度 {r['4RX幅度dB']}")
    # ---------- 事后补充：非预注册，不作判定，只供理解 ----------
    L.append("\n---\n\n# 事后补充（非预注册，不作判定）\n")
    L.append(f"0c 斜率标准误：{slope:.2f} ± {np.sqrt(np.polyfit(xs, ys, 1, cov=True)[1][0, 0]):.2f}；"
             f"0c 十条 SNR 只跨 {np.ptp(xs) * 20:.1f} dB，拟合条件差")
    need = 20 * np.log10(0.13 / s_ref) / (snr_ref - hs.min())
    L.append(f"要让最差人体（SNR {hs.min():.1f} dB）处噪声达到 0.13 mm，"
             f"需 SNR 每降 1 dB 噪声升 {need:.2f} dB（热噪声理论为 1.00）")
    for gname in ("0b", "0d"):
        for r in g[gname]:
            if r["SNR_dB"] < snr_ref - 3:
                L.append(f"{gname} {r['采集']}：SNR {r['SNR_dB']} dB（比 0a 低 {snr_ref - r['SNR_dB']:.1f}），"
                         f"σ_h {r['心跳带位移噪声mm']} mm")
    for sl in (-1.0, -2.0, slope):
        ex = s_ref * 10 ** (-sl * (snr_ref - hs) / 20)
        L.append(f"假设斜率 {sl:.2f}：人体等效噪声 {ex.min():.4f}–{ex.max():.4f} mm")
    # 预注册定义的 σ_h 含 sosfiltfilt 首尾瞬态。反射器本底极小，瞬态占主导；人体不受影响
    def s_mid(z):
        return float(eo.bandpass(eo.displacement_mm(z), *HEART)[40:-40].std())
    L.append("\n预注册 σ_h 含滤波首尾瞬态；去掉首尾各 2 秒（40 帧）后重算：")
    for r in rows:
        r["心跳带位移噪声_去边mm"] = round(s_mid(r["X"][:, 0, r["k"]]), 5)
    ym = np.log10([r["心跳带位移噪声_去边mm"] for r in g["0c"]])
    sl_m, _ = np.polyfit(xs, ym, 1)
    for gname in ("0a", "0b", "0c"):
        v = np.array([r["心跳带位移噪声_去边mm"] for r in g[gname]])
        L.append(f"{gname}：{v.min():.5f}–{v.max():.5f} mm，中位 {np.median(v):.5f}")
    L.append(f"0c 去边斜率 = {sl_m:.2f}（预注册定义下为 {slope:.2f}）")
    m_a = np.median([r["心跳带位移噪声_去边mm"] for r in g["0a"]])
    m_b = np.median([r["心跳带位移噪声_去边mm"] for r in g["0b"]])
    d_snr = snr_ref - np.median([r["SNR_dB"] for r in g["0b"]])
    L.append(f"0b 对 0a（同几何，只差板）：SNR 降 {d_snr:.1f} dB，去边噪声变 "
             f"{20 * np.log10(m_b / m_a):+.1f} dB → 等效斜率 {-20 * np.log10(m_b / m_a) / d_snr:.2f}")
    hm = np.array([s_mid(load(c)[:, 0, h["目标bin"]]) for c, h in
                   zip(sorted(p for p in B2.iterdir() if p.is_dir()), human)])
    L.append(f"人体去边：{hm.min():.4f}–{hm.max():.4f} mm（预注册定义 {hh.min():.4f}–{hh.max():.4f}，几乎不变）")
    L.append(f"人体心跳带内容 / 反射器本底（去边中位）= {20 * np.log10(hm.min() / m_a):.1f} – "
             f"{20 * np.log10(hm.max() / m_a):.1f} dB")
    write_csv(OUT / "实验0_逐条指标.csv", rows, cols + ["心跳带位移噪声_去边mm"])
    L.append("\nHPF 亏损的距离偏置敏感性（真实距离 = 卷尺 + 偏置 b 后重算 R⁻²）：")
    for d in (0.4, 0.5, 0.65, 0.8):
        corr = 40 * np.log10(1.2 / d) - 40 * np.log10((1.2 + b_fit) / (d + b_fit))
        rr = [r for r in g["0c"] if r["卷尺距离m"] == d]
        L.append(f"{d} m：亏损 {[round(r['亏损dB'] - corr, 2) for r in rr]} dB（拍频约 "
                 f"{rr[0]['目标bin'] * vsp_core.M_PER_BIN * 400:.0f} kHz）")
    (OUT / "实验0_判定汇总.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))

    # ---------- 图 ----------
    fig, ax = plt.subplots(2, 3, figsize=(18, 10))
    # (1) 距离像
    a = ax[0, 0]
    for r in g["0c"][:5]:
        a.plot(np.arange(vsp_core.NBIN) * vsp_core.M_PER_BIN, 20 * np.log10(r["prof"]), label=f"{r['卷尺距离m']} m")
    a.set_xlim(0, 2); a.set_xlabel("距离 m"); a.set_ylabel("RX0 幅度 dB"); a.legend()
    a.set_title("① 0c 第一轮距离像：峰应落在卷尺距离处", loc="left")
    # (2) 反射器 vs 人体 心跳带
    a = ax[0, 1]
    a.scatter([r["SNR_dB"] for r in rows], [r["心跳带位移噪声mm"] for r in rows], c=C["signal"], label="反射器（噪声）")
    a.scatter(hs, hh, c=C["heart"], marker="^", label="人体批次2（心跳带位移）")
    xx = np.linspace(min(hs.min(), xs.min() * 20) - 3, xs.max() * 20 + 3, 50)
    a.plot(xx, 10 ** (icpt + slope * xx / 20), "--", c=C["signal"], label=f"0c 拟合 斜率 {slope:.2f}")
    a.axhline(0.13, c=C["warn"], ls=":"); a.axhline(0.03, c=C["warn"], ls=":")
    a.set_yscale("log"); a.set_xlabel("目标 SNR dB"); a.set_ylabel("心跳带 0.8–2 Hz 位移 std mm")
    a.legend(fontsize=8); a.set_title("② 判据 1：噪声本底 vs 人体心跳信号", loc="left")
    # (3) HPF
    a = ax[0, 2]
    dd_ = np.array([r["卷尺距离m"] for r in g["0c"]])
    a.scatter(dd_, [r["实测幅度dB"] for r in g["0c"]], c=C["signal"], label="实测")
    xr = np.linspace(0.35, 1.25, 50)
    a.plot(xr, 20 * np.log10(A12) + 40 * np.log10(1.2 / xr), "--", c=C["raw"], label="R^-2 期望（锚 1.2 m）")
    a.set_xlabel("卷尺距离 m"); a.set_ylabel("目标幅度 dB"); a.legend()
    a.set_title("③ 判据 4：HPF 近距离衰减", loc="left")
    # (4) 0a 位移时间序列
    a = ax[1, 0]
    t = np.arange(600) / vsp_core.FS
    for r in g["0a"]:
        a.plot(t, eo.bandpass(eo.displacement_mm(r["X"][:, 0, r["k"]]), *HEART), lw=0.7, label=r["采集"])
    a.set_xlabel("时间 s"); a.set_ylabel("mm"); a.legend(fontsize=7)
    a.set_title("④ 0a 反射器心跳带位移（纯噪声）", loc="left")
    # (5) 板
    a = ax[1, 1]
    a.scatter(np.zeros(5), A0a, c=C["signal"]); a.scatter(np.ones(5), A0b, c=C["heart"])
    a.set_xticks([0, 1]); a.set_xticklabels(["0a 无板", "0b 有板"]); a.set_ylabel("目标幅度 dB")
    a.set_title(f"⑤ 判据 3：板损耗 {A0b.mean()-A0a.mean():+.2f} dB", loc="left")
    # (6) 角度
    a = ax[1, 2]
    for r in g["0d"]:
        a.plot(range(4), np.concatenate([[0], np.cumsum(r["_dphi"])]), "o-", label=r["备注"][-12:])
    a.set_xlabel("RX 序号"); a.set_ylabel("校准后相位 rad"); a.legend(fontsize=7)
    a.set_title("⑥ 判据 5：相位应随 RX 线性变化", loc="left")
    fig.tight_layout()
    fig.savefig(OUT / "实验0_总览.png", dpi=120)


if __name__ == "__main__":
    main()
