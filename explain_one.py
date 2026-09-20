#!/usr/bin/env python3
"""单条采集逐步解释工具：把一条 30 秒采集拆成 8 个可独立检查的步骤。

设计目的：让使用者能自己判断每一步对不对，而不是接受一个最终结论。
所以每一步都产出三样东西：
    - CSV：可以直接用 Excel 打开的中间数据
    - PNG：中文标注的图，图上自带判读提示
    - 判读说明：写进 阅读指南.md，说明正常长什么样、异常长什么样

用法（必须用 Python39 解释器）：
    python explain_one.py <采集目录>
    python explain_one.py <采集目录> --target-bin 16     手动指定目标 bin
    python explain_one.py <采集目录> --out-dir explain2  换输出目录名

输出：<采集目录>/explain/

不修改任何原始文件。.bin / .pcap / data_info.csv 只读。
"""
import argparse
import io
import os
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import scipy.signal as sp

import vsp_core
from pipeline import plotting

plotting.setup()
import matplotlib.pyplot as plt

C = plotting.COLORS

# ---- 分析参数。集中在这里，不散落到各步骤 ----
TARGET_RANGE_M = (0.6, 1.0)   # 目标距离先验。用户已确认本批实际约 0.8 m
BREATH_BAND = (0.1, 0.5)      # 呼吸带 Hz = 6-30 bpm
HEART_BAND = (0.8, 2.0)       # 心跳带 Hz = 48-120 bpm
LEAK_BINS = 5                 # 前 5 个 bin 是天线耦合泄漏，恒定排除

# 呼吸检测的绝对下限。没有这两条，安静时自适应阈值会把噪声数成呼吸。
# 数值依据：本批实测自然呼吸带内起伏约 0.6 mm，最安静的记录约 0.24 mm。
# 取 0.35 mm 作为分界，是这两组实测值之间的中点，属于经验阈值，
# 只在本批 0.8 m 人体数据上验证过，换距离或换物种（牛）必须重新标定。
# 注意它拦的是「起伏太小，数峰不可靠」，不是「受试者在憋气」——
# 后者用位移量分不出来，见 HOLD_PEAK_HINT_MM 处的说明。
MIN_BREATH_STD_MM = 0.35      # 带内起伏低于此值，判定为无有效呼吸
MIN_BREATH_PROM_MM = 0.10     # 单次起伏的绝对最小显著度

# 憋气记录的呼吸带主峰幅度参考线。注意：这是**提示线，不是判据**。
#
# 曾经想把它当判据用，依据是「憋气 0.17-0.24 mm，自然呼吸 0.63-2.27 mm，
# 中间是空的」。这个空档是假的 —— 它建立在把 lsw 两条算成自然呼吸的前提上。
# 受试者已确认那两条确实在憋气，于是憋气组的实测范围变成：
#     lrq  101453 / 102049   γ 0.971 / 0.961   0.172 / 0.243 mm
#     lsw  102905 / 103753   γ 0.799 / 0.720   1.066 / 2.284 mm
# 自然呼吸组 14 条（γ>0.6）是 0.63-2.27 mm，与憋气组**完全重叠**，没有空档。
#
# 所以「呼吸带有没有起伏」这件事，绝对幅度和显著度一样分不开憋气与呼吸。
# lsw 那两条 γ 有 0.72-0.80，相位可信，2.28 mm 约 12 bpm 的起伏是真实存在的
# 物理运动，不是伪影；来源未验证（可能是体位摆动、残余膈肌运动，
# 或憋气只覆盖 30 秒中的一部分）。**这是未验证的推测，不要当结论用。**
#
# 因此本项只标「存疑」，供人工看图，绝不判「不通过」——
# 否则真憋气记录会被自动剔除。
HOLD_PEAK_HINT_MM = 0.40
RTI_MAX_M = 3.0               # 热图只画到 3 m，远处是墙和杂物
NEIGHBOR = 2                  # 候选 bin 取目标 ±2

# ---- 相位相干度：判断位移到底能不能用的总闸 ----
# 定义 gamma = |E[conj(z_n) z_{n+1}]| / E[|z|^2]，即滞后一帧的复相干度。
# 为什么它比「相位跳变次数」可靠：
#   跳变次数数的是 |dphi| > pi/2 的帧数，但 np.unwrap 的输出按定义
#   |dphi| <= pi，所以那个计数只是「有多少帧接近混叠极限」，不是失败次数。
#   而且 pi/2 只对应 12.1 mm/s 径向速度，正常胸腔运动就会超，判据从物理上不成立。
#   相干度不做解缠，直接量「相邻帧复回波还剩多少确定关系」，没有模糊问题。
# 判据依据（chw 8 条实测，见下）：
#   工况 1 双静止  0.977 / 0.957      全程可用
#   工况 3 手持    0.745 / 0.704      断续可用，2 秒窗有 62%-72% 达标
#   工况 2 人动    0.057 / 0.075      与噪声本底同级
#   工况 4 双动    0.025 / 0.130      与噪声本底同级
#   599 帧的噪声本底 = 1/sqrt(599) = 0.041。工况 2/4 已无相位信息可言。
# 0.30 这条线取在「手持最差 0.704」与「人动最好 0.130」之间，中间是空的，
# 不是拟合出来的分界。只在本批 0.8 m 人体数据上成立，换距离或换牛必须重标。
MIN_COHERENCE = 0.30          # 低于此值：相位已随机，位移与呼吸率全部无效
GOOD_COHERENCE = 0.60         # 高于此值：相位可信；0.30-0.60 之间为断续可用
COH_WIN = 40                  # 分段相干度窗长 = 2 秒
COH_HOP = 20                  # 步进 1 秒
SEG_COHERENCE = 0.80          # 单个 2 秒窗算「相干」的判据

# ---- 目标移动量判据（按 chw 8 条实测重定）----
# 原判据「超过 1 个 bin(50 mm) 即算跨 bin」把 8 条全判成「是」，无区分度。
# 实测幅度重心峰峰值：静止胸腔 63/70/71/75 mm，人动 120/127/144/147 mm。
# 两组之间是空的，100 mm 落在空档中央。
# 注意 63 mm 不代表胸腔真动了 63 mm：重心本身有估计噪声（静止时约
# 27 mm/s 的抖动），所以这是「重心估计的峰峰值」，不是位移真值。
MOVE_LARGE_MM = 100.0

EXPECTED_FRAMES = 600
WORK_MODE_NAMES = {
    1: "双静止（雷达不动 + 人不动）",
    2: "人动（雷达不动 + 人移动胸腔）",
    3: "雷达动（手持雷达 + 人不动）",
    4: "双动（手持雷达 + 人移动）",
}


# ==================== 工具函数 ====================

def write_csv(path, header, rows):
    """写 CSV。utf-8-sig 让 Excel 双击打开不乱码。"""
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        f.write(",".join(str(h) for h in header) + "\n")
        for r in rows:
            f.write(",".join("" if v is None else str(v) for v in r) + "\n")


def read_meta(cap_dir):
    """读该采集自己的 data_info.csv。四列：受试者 工况 手环心率 自数呼吸次数。"""
    f = cap_dir / "data_info.csv"
    if not f.exists():
        return None
    txt = f.read_text(encoding="utf-8", errors="replace").strip()
    parts = txt.split()
    if len(parts) < 4:
        return None
    breath = int(parts[3])
    return {
        "subject": parts[0],
        "mode": int(parts[1]),
        "hr_band": int(parts[2]),
        "breath_count": breath,
        # 用户已明确：0 表示憋气，不是漏记
        "breath_hold": breath == 0,
    }


def bandpass(x, lo, hi, order=4):
    """零相位带通。离线分析用 sosfiltfilt：无相位延迟、无启动瞬态。

    不用 sosfilt 的原因：因果滤波会让波形整体后移，峰谷时刻不可信。
    """
    sos = sp.butter(order, [lo, hi], btype="band", fs=vsp_core.FS, output="sos")
    padlen = min(3 * (2 * order), len(x) - 1)
    return sp.sosfiltfilt(sos, x, padlen=padlen)


def displacement_mm(z):
    """复数慢时间序列 → 去线性趋势的位移（毫米）。

    先 unwrap 再去趋势：unwrap 需要连续相位，去趋势会破坏它，顺序不能反。
    """
    ph = np.unwrap(np.angle(z))
    t = np.arange(len(ph)) / vsp_core.FS
    ph = ph - np.polyval(np.polyfit(t, ph, 1), t)
    return ph * vsp_core.MM_PER_RAD


def coherence(z, lag=1):
    """滞后 lag 帧的复相干度 gamma，范围 0-1。

    不做 unwrap，因此不受 2pi 模糊影响：直接量相邻帧复回波还剩多少确定关系。
    gamma→1 相位连续可信；gamma→1/sqrt(N) 的本底则说明相邻帧已无关，
    此时任何位移、呼吸率都是噪声经带通整形后的产物。
    """
    z = np.asarray(z, dtype=np.complex128)
    p = np.mean(np.abs(z) ** 2)
    if p <= 0:
        return 0.0
    return float(abs(np.mean(np.conj(z[:-lag]) * z[lag:])) / p)


def coherence_segments(z, win=COH_WIN, hop=COH_HOP):
    """分段相干度。返回 (每窗 gamma 数组, 窗起始秒数组)。

    要分段而不是只看全程一个数：手持工况是间歇性抖动，
    全程 0.74 掩盖了「有 62% 的 2 秒窗其实是好的」这个事实。
    """
    gs, ts = [], []
    for s in range(0, len(z) - win + 1, hop):
        gs.append(coherence(z[s:s + win]))
        ts.append(s / vsp_core.FS)
    return np.array(gs), np.array(ts)


def longest_good_run(gs, thr=SEG_COHERENCE, hop=COH_HOP, win=COH_WIN):
    """最长连续相干时长（秒）。n 个连续窗覆盖 (n-1)*hop+win 帧。"""
    best = run = 0
    for g in gs:
        run = run + 1 if g >= thr else 0
        best = max(best, run)
    if best == 0:
        return 0.0
    return ((best - 1) * hop + win) / vsp_core.FS


def spectrum(x):
    """单边幅度谱。返回 (频率 Hz, 幅度)。"""
    mag = np.abs(np.fft.rfft(x))
    frq = np.fft.rfftfreq(len(x), 1.0 / vsp_core.FS)
    return frq, mag


def band_peak(frq, mag, lo, hi):
    """频带内主峰。返回 (峰频 Hz, 峰值, 谱峰显著度 dB)。

    显著度 = 20log10(峰值 / 带内中位数)。这不是 SNR：
    没有噪声模型，只是描述峰在带内有多突出。命名必须诚实。
    """
    m = (frq >= lo) & (frq <= hi)
    if not m.any():
        return np.nan, np.nan, np.nan
    fb, mb = frq[m], mag[m]
    i = int(np.argmax(mb))
    med = np.median(mb)
    prom = 20 * np.log10(mb[i] / med) if med > 0 else np.nan
    return float(fb[i]), float(mb[i]), float(prom)


# ==================== 步骤 1：帧完整性 ====================

def step1_integrity(bin_path, out, guide):
    size = os.path.getsize(bin_path)
    frame_bytes = vsp_core.FRAME_I16 * 2
    remainder = size % frame_bytes
    nfr = size // frame_bytes
    ok = (remainder == 0) and (nfr == EXPECTED_FRAMES)

    write_csv(out / "01_完整性.csv",
              ["项目", "实测值", "期望值", "是否正常"],
              [["文件字节数", size, f"{EXPECTED_FRAMES * frame_bytes}", size == EXPECTED_FRAMES * frame_bytes],
               ["每帧字节数", frame_bytes, frame_bytes, True],
               ["余数字节", remainder, 0, remainder == 0],
               ["帧数", nfr, EXPECTED_FRAMES, nfr == EXPECTED_FRAMES],
               ["时长秒", round(nfr / vsp_core.FS, 2), 30.0, abs(nfr / vsp_core.FS - 30) < 0.1]])

    guide.append(
        "## 第 1 步　帧完整性　`01_完整性.csv`\n\n"
        f"实测 {nfr} 帧，{size} 字节，余数 {remainder}。\n\n"
        "**怎么看**：余数必须是 0，帧数必须是 600。\n"
        "余数不为 0 说明文件被截断或分片拼接有误，"
        "此时后面所有步骤都不用看了，先查采集链路。\n"
        f"**本条结论**：{'通过，可以继续。' if ok else '不通过，后续结果不可信。'}\n")
    return ok, nfr


# ==================== 步骤 2：距离能量分布 ====================

def step2_range_profile(X, out, guide):
    """回答：人在哪个距离？哪些峰不是人？"""
    energy = np.abs(X).mean(axis=(0, 1))            # 时间+通道平均
    rng = np.arange(len(energy)) * vsp_core.M_PER_BIN
    e_db = 20 * np.log10(energy + 1e-9)

    write_csv(out / "02_距离能量.csv",
              ["bin", "距离_米", "能量_线性", "能量_dB"],
              [[b, round(rng[b], 4), f"{energy[b]:.4g}", round(e_db[b], 2)]
               for b in range(len(energy))])

    lo_m, hi_m = TARGET_RANGE_M
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(rng, e_db, color=C["signal"], lw=1.4)
    ax.axvspan(lo_m, hi_m, color=C["band"], alpha=0.15,
               label=f"目标预期区间 {lo_m}-{hi_m} m")
    ax.axvspan(0, LEAK_BINS * vsp_core.M_PER_BIN, color=C["clutter"], alpha=0.25,
               label="天线耦合泄漏区（非目标）")
    ax.set_xlim(0, RTI_MAX_M)
    ax.set_xlabel("距离 (米)")
    ax.set_ylabel("回波能量 (dB)")
    ax.set_title("第 2 步　距离能量分布：全程平均后，各距离上的回波强弱")
    ax.legend(loc="upper right", fontsize=9)
    plotting.note(ax,
                  "判读要点\n"
                  "· 灰区（<0.25 m）是收发天线直接耦合，永远有峰，不是人\n"
                  "· 绿区内应能看到人体的峰\n"
                  "· 2 m 附近常有更高的峰，那是墙壁或家具\n"
                  "· 只看能量最大值会选到墙，这就是早期选错 bin 的原因",
                  loc="lower left")
    fig.savefig(out / "02_距离能量.png")
    plt.close(fig)

    # 找出目标区内和全局的峰，用于说明
    b_lo = max(LEAK_BINS, int(lo_m / vsp_core.M_PER_BIN))
    b_hi = min(len(energy), int(hi_m / vsp_core.M_PER_BIN) + 1)
    peak_in = b_lo + int(np.argmax(energy[b_lo:b_hi]))
    peak_all = LEAK_BINS + int(np.argmax(energy[LEAK_BINS:]))

    guide.append(
        "## 第 2 步　距离能量分布　`02_距离能量.csv` / `.png`\n\n"
        f"目标区间内最强 bin = {peak_in}（{rng[peak_in]:.2f} m）；"
        f"排除泄漏后全局最强 bin = {peak_all}（{rng[peak_all]:.2f} m）。\n\n"
        "**怎么看**：横轴距离，纵轴回波强弱。\n"
        "灰色区是收发天线直接耦合造成的固定峰，不管有没有人都在，必须排除。\n"
        "绿色区是本批实验的实际人体距离（约 0.8 m，已确认）。\n"
        f"{'注意：全局最强峰不在目标区内，说明有比人更强的反射体（多半是墙），因此不能用能量最大值选目标。' if peak_all != peak_in else '本条中目标区内的峰同时也是全局最强峰。'}\n\n"
        "**这一步不能单独定 bin**：静止的墙可能比人更强，还要看第 3、4 步。\n")
    return energy, rng


# ==================== 步骤 3：距离-时间热图 ====================

def step3_range_time(X, out, guide):
    """回答：目标随时间移动了吗？跨 bin 了吗？"""
    nbin = min(X.shape[2], int(RTI_MAX_M / vsp_core.M_PER_BIN) + 1)
    amp = np.abs(X).mean(axis=1)[:, :nbin]                # (帧, bin)
    amp_db = 20 * np.log10(amp + 1e-9)
    # 逐帧归一化会掩盖整体变化，这里用全局归一化保留真实对比
    amp_db -= amp_db.max()

    t = np.arange(X.shape[0]) / vsp_core.FS
    lo_m, hi_m = TARGET_RANGE_M

    fig, ax = plt.subplots(figsize=(11, 4.6))
    im = ax.imshow(amp_db.T, aspect="auto", origin="lower", cmap="viridis",
                   extent=[0, t[-1], 0, nbin * vsp_core.M_PER_BIN],
                   vmin=-40, vmax=0, interpolation="nearest")
    ax.axhline(lo_m, color="white", ls="--", lw=1, alpha=0.8)
    ax.axhline(hi_m, color="white", ls="--", lw=1, alpha=0.8)
    ax.text(0.3, hi_m + 0.04, f"目标预期区间 {lo_m}-{hi_m} m",
            color="white", fontsize=9)
    ax.set_xlabel("时间 (秒)")
    ax.set_ylabel("距离 (米)")
    ax.set_title("第 3 步　距离-时间热图：亮带就是反射体，看它随时间有没有移动")
    fig.colorbar(im, ax=ax, label="相对回波强度 (dB)")
    plotting.note(ax,
                  "判读要点（这是判断目标有没有跨 bin 的唯一直观依据）\n"
                  "· 水平不动的亮带 = 静止物体（墙、家具），或雷达和人都没动\n"
                  "· 亮带上下缓慢起伏 = 人整体前后移动，可能跨 bin\n"
                  "· 亮带断裂、整幅忽明忽暗 = 手持雷达晃动\n"
                  "· 若目标亮带全程停在同一高度，用固定 bin 就够了",
                  loc="upper left")
    fig.savefig(out / "03_距离时间图.png")
    plt.close(fig)

    # 量化目标移动。仅在目标区内计算，避免被墙的强峰带跑。
    #
    # 用幅度重心而不是逐帧 argmax：
    #   argmax 只能取整数 bin，目标停在两个 bin 边界时会来回跳，
    #   看起来"跨了 3 个 bin"，其实只动了十几毫米。这是离散化假象。
    #   重心是加权平均，能给出亚 bin 位置，反映真实移动。
    b_lo = max(LEAK_BINS, int(lo_m / vsp_core.M_PER_BIN))
    b_hi = min(X.shape[2], int(hi_m / vsp_core.M_PER_BIN) + 1)
    w = amp[:, b_lo:b_hi]
    idx = np.arange(b_lo, b_hi)
    centroid = (w * idx).sum(axis=1) / np.maximum(w.sum(axis=1), 1e-30)
    per_frame = b_lo + np.argmax(w, axis=1)

    move_mm = float(centroid.max() - centroid.min()) * vsp_core.M_PER_BIN * 1000
    spread_arg = int(per_frame.max() - per_frame.min())

    write_csv(out / "03_目标位置随时间.csv",
              ["帧号", "时间_秒", "幅度重心_bin", "重心距离_米", "逐帧最强bin"],
              [[i, round(i / vsp_core.FS, 3), round(float(centroid[i]), 3),
                round(float(centroid[i]) * vsp_core.M_PER_BIN, 4), int(per_frame[i])]
               for i in range(len(centroid))])

    # 重心曲线单独画一张，比热图更容易看出有没有漂移
    fig2, ax2 = plt.subplots(figsize=(11, 3.4))
    ax2.plot(t, centroid * vsp_core.M_PER_BIN, color=C["signal"], lw=1.3,
             label="幅度重心（亚 bin，推荐看这条）")
    ax2.plot(t, per_frame * vsp_core.M_PER_BIN, color=C["raw"], lw=0.8,
             alpha=0.75, label="逐帧最强 bin（阶梯状是离散化假象）")
    ax2.set_xlabel("时间 (秒)")
    ax2.set_ylabel("距离 (米)")
    ax2.set_title(f"第 3 步补充　目标距离随时间：全程移动约 {move_mm:.0f} mm")
    ax2.legend(loc="upper right", fontsize=9)
    plotting.note(ax2,
                  f"1 个 bin = {vsp_core.M_PER_BIN * 1000:.1f} mm\n"
                  "灰线跳动不代表人真的动了那么多：\n"
                  "目标停在两 bin 之间时，取整会来回跳\n"
                  "蓝线是加权重心，才是真实位置",
                  loc="lower left")
    fig2.savefig(out / "03_目标位置随时间.png")
    plt.close(fig2)

    crossed = move_mm > vsp_core.M_PER_BIN * 1000
    guide.append(
        "## 第 3 步　距离-时间热图　`03_距离时间图.png` / `03_目标位置随时间.png` / `.csv`\n\n"
        f"幅度重心全程移动约 **{move_mm:.0f} mm**"
        f"（1 个 bin = {vsp_core.M_PER_BIN * 1000:.1f} mm）。\n"
        f"逐帧最强 bin 的跨度是 {spread_arg} 个 bin，但这个数偏大，见下面说明。\n\n"
        "**怎么看热图**：横轴时间，纵轴距离，亮 = 反射强。人体是白色虚线之间的亮带。\n"
        "亮带高度不变说明距离没变；上下起伏说明人整体前后移动了。\n\n"
        "**为什么要看重心那张图**：逐帧取最强 bin 只能落在整数上，\n"
        "目标正好停在两个 bin 中间时会不停来回跳，看着像移动了好几个 bin，\n"
        "其实只动了十几毫米。加权重心能给出亚 bin 位置，是更可信的依据。\n\n"
        f"**本条结论**：{'移动量小于 1 个 bin，可以用固定 bin。' if not crossed else '移动量超过 1 个 bin，需要注意跨 bin 造成的相位基准变化。'}\n")
    return per_frame, centroid, move_mm


# ==================== 步骤 4：候选 bin 波形对比 ====================

def step4_candidates(X, energy, out, guide, forced_bin=None):
    """回答：哪个 bin 才是人？让使用者自己看波形挑。"""
    lo_m, hi_m = TARGET_RANGE_M
    b_lo = max(LEAK_BINS, int(lo_m / vsp_core.M_PER_BIN))
    b_hi = min(X.shape[2], int(hi_m / vsp_core.M_PER_BIN) + 1)

    # 自动初选：回波能量 + 呼吸周期性 的加权。
    #
    # 为什么不能只用呼吸带起伏（第一版的错误）：
    #   起伏大不等于呼吸强。信噪比差的 bin 被噪声抬高，起伏反而更大。
    #   实测 bin 19 起伏 0.685 mm 但能量只有 102 dB，是人体回波的拖尾，
    #   而真正的人体在 bin 15-16（能量 114-118 dB），被错过了。
    # 为什么不能只用能量：静止的墙可能比人更强，但墙不呼吸。
    # 所以两者都要：能量说明"有东西"，谱峰显著度说明"这东西在周期性起伏"。
    detail = {}
    for b in range(b_lo, b_hi):
        d = displacement_mm(X[:, 0, b])
        br = bandpass(d, *BREATH_BAND)
        frq, mag = spectrum(br)
        _, _, prom = band_peak(frq, mag, *BREATH_BAND)
        detail[b] = {
            "e_db": 20 * np.log10(energy[b] + 1e-9),
            "prom": prom if np.isfinite(prom) else 0.0,
            "std": float(br.std()),
        }

    e_vals = np.array([detail[b]["e_db"] for b in detail])
    p_vals = np.array([max(detail[b]["prom"], 0.0) for b in detail])
    e_rng = max(e_vals.max() - e_vals.min(), 1e-9)
    p_max = max(p_vals.max(), 1e-9)
    for b in detail:
        detail[b]["score"] = (0.6 * (detail[b]["e_db"] - e_vals.min()) / e_rng
                              + 0.4 * max(detail[b]["prom"], 0.0) / p_max)
    auto_bin = max(detail, key=lambda b: detail[b]["score"])
    center = forced_bin if forced_bin is not None else auto_bin

    cands = [b for b in range(center - NEIGHBOR, center + NEIGHBOR + 1)
             if 0 <= b < X.shape[2]]

    rows = []
    fig, axes = plt.subplots(len(cands), 1, figsize=(11, 1.75 * len(cands)),
                             sharex=True)
    t = np.arange(X.shape[0]) / vsp_core.FS
    for ax, b in zip(np.atleast_1d(axes), cands):
        d = displacement_mm(X[:, 0, b])
        br = bandpass(d, *BREATH_BAND)
        frq, mag = spectrum(br)
        f_pk, _, prom = band_peak(frq, mag, *BREATH_BAND)
        is_sel = (b == center)
        ax.plot(t, br, color=C["breath"] if is_sel else C["raw"],
                lw=1.5 if is_sel else 0.9)
        ax.set_ylabel(f"bin {b}\n{b * vsp_core.M_PER_BIN:.2f} m", fontsize=9)
        tag = "　← 选定" if is_sel else ""
        ax.set_title(f"呼吸带位移　峰频 {f_pk * 60:.1f} bpm　显著度 {prom:.1f} dB"
                     f"　带内起伏 {br.std():.3f} mm{tag}",
                     fontsize=9.5, loc="left")
        if is_sel:
            for s in ax.spines.values():
                s.set_edgecolor(C["target"])
                s.set_linewidth(1.8)
        rows.append([b, round(b * vsp_core.M_PER_BIN, 4),
                     round(20 * np.log10(energy[b] + 1e-9), 2),
                     round(br.std(), 4), round(f_pk * 60, 2), round(prom, 2),
                     "是" if is_sel else ""])

    np.atleast_1d(axes)[-1].set_xlabel("时间 (秒)")
    fig.suptitle("第 4 步　候选 bin 波形对比：真目标的呼吸应光滑近周期，杂波是杂乱噪声",
                 fontsize=12, y=0.995)
    fig.tight_layout()
    fig.savefig(out / "04_候选bin波形.png")
    plt.close(fig)

    write_csv(out / "04_候选bin.csv",
              ["bin", "距离_米", "回波能量_dB", "呼吸带起伏_mm",
               "呼吸峰频_bpm", "谱峰显著度_dB", "选定"], rows)

    guide.append(
        "## 第 4 步　候选 bin 波形对比　`04_候选bin波形.png` / `04_候选bin.csv`\n\n"
        f"自动初选 bin {auto_bin}（{auto_bin * vsp_core.M_PER_BIN:.2f} m），"
        f"依据是目标区内呼吸带起伏最大。"
        f"{f'本次按命令行指定改用 bin {forced_bin}。' if forced_bin is not None else ''}\n\n"
        "**怎么看**：五张并排的波形是目标附近相邻 bin。\n"
        "真正的人体 bin：曲线光滑、接近周期性、能数出呼吸次数。\n"
        "杂波 bin：忽高忽低、没有稳定周期，或者幅度极小。\n\n"
        "**这一步是给你做主的**：如果你觉得选错了，用\n"
        "`python explain_one.py <目录> --target-bin <你选的编号>`\n"
        "重跑，第 4 步以后的所有输出都会跟着变。\n\n"
        "**为什么不用能量最大**：墙的能量往往比人大，但墙没有呼吸。\n"
        "所以这里用呼吸带起伏排序，而不是回波能量。\n")
    return center, auto_bin


# ==================== 步骤 5：选定 bin 位移 ====================

def step5_displacement(X, target_bin, out, guide, meta):
    z = X[:, 0, target_bin]
    ph_raw = np.unwrap(np.angle(z))
    t = np.arange(len(z)) / vsp_core.FS
    disp_raw = (ph_raw - ph_raw.mean()) * vsp_core.MM_PER_RAD
    disp_dt = displacement_mm(z)
    br = bandpass(disp_dt, *BREATH_BAND)

    # 相位相干度：位移能不能用的总闸，必须在数峰之前判。
    # 实测教训：工况 2/4 的 gamma 只有 0.025-0.130（噪声本底 0.041），
    # 相位已经随机，但带通滤波仍会把它整形成光滑的类正弦波，
    # 图上第 ③ 行看起来比真呼吸还漂亮 —— 这是最危险的失效模式，
    # 因为最好看的那条曲线恰好是完全不可信的那条。
    coh = coherence(z)
    coh_seg, coh_t = coherence_segments(z)
    good_ratio = float((coh_seg >= SEG_COHERENCE).mean()) if len(coh_seg) else 0.0
    best_run_s = longest_good_run(coh_seg)
    phase_ok = coh >= MIN_COHERENCE

    write_csv(out / "05_位移.csv",
              ["帧号", "时间_秒", "原始位移_mm", "去趋势位移_mm", "呼吸带位移_mm"],
              [[i, round(t[i], 3), round(disp_raw[i], 4),
                round(disp_dt[i], 4), round(br[i], 4)]
               for i in range(len(t))])
    write_csv(out / "05_相位相干度.csv",
              ["窗起始_秒", "窗长_秒", "相干度", "是否相干"],
              [[round(coh_t[i], 2), COH_WIN / vsp_core.FS, round(coh_seg[i], 4),
                "是" if coh_seg[i] >= SEG_COHERENCE else "否"]
               for i in range(len(coh_seg))])

    # 呼吸峰谷检测。
    #
    # 这里踩过一个坑：第一版阈值只写 max(0.2*br.std(), 1e-6)，
    # 完全跟着信号自身幅度缩放。憋气时 std 只有 0.24 mm，阈值就降到
    # 0.047 mm，比自然呼吸的 0.12 mm 还松一半，于是残余噪声的每个
    # 小起伏都被数成一次呼吸 —— 憋气反而"检出"10 次，比真呼吸还多。
    # 自适应阈值在信号消失时会反向失效：越该严的时候越松。
    #
    # 修法：加一条绝对下限。呼吸位移是毫米量级，低于 MIN_BREATH_MM
    # 的起伏在物理上不可能是呼吸，只能是噪声。
    # 同时先判断整段有没有呼吸，没有就直接报 0，不进入峰检测。
    #
    # 幅度下限拦不住相位随机的情况：工况 2/4 带内起伏有 2.0 mm，
    # 远超 0.35 mm 的下限，却全是伪影。所以相干度是独立的第二道闸。
    #
    # 两者必须分开，不能揉进一个变量（这里第二次踩坑）：
    #   amp_has_breath 是「呼吸带幅度够不够大」，纯物理量，与相干度无关。
    #   phase_ok       是「相位还能不能用」。
    # 曾把相干度 and 进 has_breath，结果憋气那组检查（检查「应判为无呼吸」）
    # 变成了「相位越好越判失败」—— 相干度 0.961 的最佳憋气记录反被判不可用。
    # 判据的语义必须和它检查的物理量对应。
    prom = max(0.2 * br.std(), MIN_BREATH_PROM_MM)
    amp_has_breath = br.std() >= MIN_BREATH_STD_MM
    has_breath = amp_has_breath and phase_ok
    if has_breath:
        peaks, _ = sp.find_peaks(br, distance=int(vsp_core.FS * 1.5),
                                 prominence=prom)
    else:
        peaks = np.array([], dtype=int)

    fig, axes = plt.subplots(4, 1, figsize=(11, 9.5), sharex=True,
                             gridspec_kw={"height_ratios": [1, 1, 1, 0.6]})
    axes[0].plot(t, disp_raw, color=C["raw"], lw=0.9)
    axes[0].set_ylabel("位移 (mm)")
    axes[0].set_title(f"① 原始位移（含慢漂移）　bin {target_bin} = "
                      f"{target_bin * vsp_core.M_PER_BIN:.2f} m", loc="left")
    plotting.note(axes[0], "斜坡或大幅漂移是正常的：\n人轻微移动、雷达手持晃动都会造成", loc="upper left")

    axes[1].plot(t, disp_dt, color=C["signal"], lw=0.9)
    axes[1].set_ylabel("位移 (mm)")
    axes[1].set_title("② 去掉线性趋势后", loc="left")

    axes[2].plot(t, br, color=C["breath"] if phase_ok else C["clutter"], lw=1.4)
    axes[2].plot(t[peaks], br[peaks], "v", color=C["peak"], ms=7,
                 label=f"检出起伏 {len(peaks)} 次")
    axes[2].set_ylabel("位移 (mm)")
    axes[2].set_title(f"③ 呼吸带滤波后 {BREATH_BAND[0]}-{BREATH_BAND[1]} Hz"
                      f"（{BREATH_BAND[0]*60:.0f}-{BREATH_BAND[1]*60:.0f} bpm）"
                      + ("" if phase_ok else "　【相位已随机，此曲线为伪影】"),
                      loc="left")
    axes[2].legend(loc="upper right", fontsize=9)

    amp_line = (f"带内起伏 {br.std():.3f} mm　判据 ≥{MIN_BREATH_STD_MM} mm　"
                f"→ {'有呼吸' if amp_has_breath else '无有效呼吸'}")
    if not phase_ok:
        hint = ("⚠ 相位相干度 %.3f < %.2f：相邻帧回波已无关联\n"
                "这条绿线是带通滤波把随机相位整形出来的，不是呼吸。\n"
                "看起来光滑周期，恰恰因为滤波器只让 0.1-0.5 Hz 通过。\n"
                "本条不可用，检出次数强制为 0。"
                % (coh, MIN_COHERENCE))
    elif meta and meta["breath_hold"]:
        hint = ("本条是憋气记录（自报 0 次）\n" + amp_line + "\n"
                "判读：理想应接近平坦，但不平坦≠标签错\n"
                "已有确认憋气却仍有约 12 bpm 起伏的实例\n"
                "幅度低于判据时直接报 0 次，不再数峰")
    elif meta:
        hint = (f"本条受试者自报呼吸 {meta['breath_count']} 次，"
                f"算法检出 {len(peaks)} 次\n" + amp_line + "\n"
                "判读：两者相差 2 次以内算相符\n"
                "自报值不是严格真值，只能粗核")
    else:
        hint = "判读：数一数三角标记的个数，应与自报呼吸次数接近\n" + amp_line
    plotting.note(axes[2], hint, loc="lower left")

    # ④ 相干度时间轴：告诉用户哪几秒的相位是可信的
    axes[3].plot(coh_t + COH_WIN / vsp_core.FS / 2, coh_seg,
                 color=C["signal"], lw=1.2, marker="o", ms=2.5)
    axes[3].axhline(SEG_COHERENCE, color=C["breath"], ls="--", lw=1,
                    label=f"相干判据 {SEG_COHERENCE}")
    axes[3].axhline(MIN_COHERENCE, color=C["heart"], ls="--", lw=1,
                    label=f"可用下限 {MIN_COHERENCE}")
    axes[3].fill_between(coh_t + COH_WIN / vsp_core.FS / 2, 0, 1,
                         where=coh_seg >= SEG_COHERENCE,
                         color=C["band"], alpha=0.15, step="mid")
    axes[3].set_ylim(0, 1.02)
    axes[3].set_ylabel("相干度")
    axes[3].set_xlabel("时间 (秒)")
    axes[3].set_title(f"④ 相位相干度（2 秒窗）　全程 {coh:.3f}　"
                      f"达标窗占 {good_ratio*100:.0f}%　最长连续 {best_run_s:.0f} 秒",
                      loc="left")
    axes[3].legend(loc="lower right", fontsize=8, ncol=2)

    fig.suptitle("第 5 步　选定 bin 的位移：从原始相位到呼吸波形", fontsize=12, y=0.997)
    fig.tight_layout()
    fig.savefig(out / "05_位移.png")
    plt.close(fig)

    counted = f"，受试者自报 {meta['breath_count']} 次" if meta else ""
    guide.append(
        "## 第 5 步　选定 bin 位移　`05_位移.csv` / `.png` / `05_相位相干度.csv`\n\n"
        f"四条曲线：原始 → 去趋势 → 呼吸带 → 相干度。检出起伏 {len(peaks)} 次{counted}。\n"
        f"带内起伏 {br.std():.3f} mm（判据 ≥{MIN_BREATH_STD_MM} mm），"
        f"幅度判定**{'有呼吸' if amp_has_breath else '无有效呼吸'}**；"
        f"相位相干度 {coh:.3f}（判据 ≥{MIN_COHERENCE}），"
        f"**{'相位可用' if phase_ok else '相位不可用'}**。\n\n"
        "这两项是独立的：幅度说的是呼吸带有多大起伏，相干度说的是相位还能不能信。\n"
        "两者都过才数峰。\n\n"
        "**为什么要三条位移曲线**：原始位移里 0.5 mm 的呼吸会被几毫米的慢漂移埋掉，\n"
        "所以必须去趋势加带通才看得见。这不是修饰数据，是把想看的频段取出来。\n\n"
        "**先看第 ④ 条，再看第 ③ 条**（顺序很重要）：\n"
        "相干度衡量相邻帧的复回波还剩多少确定关系。它低于下限时，\n"
        "第 ③ 条无论多光滑都是假的 —— 带通滤波会把随机相位整形成类正弦波，\n"
        "**图上越好看的绿线越可能是伪影**。实测工况 2/4 的相干度只有 0.03-0.13\n"
        "（599 帧的噪声本底是 0.041），第 ③ 条却比真呼吸还规整。\n\n"
        "**相干度为什么比「相位跳变次数」可靠**：\n"
        "跳变次数数的是 |dφ|>π/2 的帧数，但 unwrap 的输出按定义 |dφ|≤π，\n"
        "所以那个计数只是「有多少帧接近混叠极限」，不是失败次数；\n"
        "且 π/2 只对应 12 mm/s 径向速度，正常胸腔运动就会超。\n"
        "相干度不做解缠，没有 2π 模糊问题。\n\n"
        "**为什么要先判幅度再数峰**（这里修过一个 bug）：\n"
        "峰检测阈值如果只按信号自身幅度缩放，憋气时幅度小、阈值也跟着变小，\n"
        "残余噪声就会被数成呼吸 —— 实测憋气曾被数出 10 次，比真呼吸还多。\n"
        f"所以加了绝对下限 {MIN_BREATH_STD_MM} mm。\n"
        "注意幅度下限拦不住相位随机的情况：工况 2/4 带内起伏有 2.0 mm，\n"
        "远超下限却全是伪影，所以相干度是独立的第二道闸。\n"
        + ("\n**本条是憋气记录**：③ 理想应接近平坦、检出 0 次，"
           "但不平坦不等于标签错。\n"
           "实测有确认在憋气、γ=0.72-0.80（相位可信）、③ 却有约 12 bpm "
           "规律起伏的记录（lsw 102905/103753，主峰 1.07/2.28 mm）。\n"
           "憋气段仍可能存在体位摆动等其他周期运动，雷达只看位移，\n"
           "分不清位移由什么产生。所以憋气三项只作提示，不判不可用。\n"
           if meta and meta["breath_hold"] else "")
        + ("\n**本条相位不可用**：相干度 %.3f 低于下限 %.2f，"
           "位移、呼吸率、心跳一律不成立，检出次数已强制为 0。\n"
           % (coh, MIN_COHERENCE) if not phase_ok else "")
        + f"\n**分段结果**：2 秒窗中有 {good_ratio*100:.0f}% 达到 {SEG_COHERENCE}，"
        f"最长连续相干 {best_run_s:.0f} 秒。\n"
        "手持工况是间歇性抖动，全程均值会掩盖「其实有一半窗是好的」；\n"
        "人动工况是持续破坏，一秒都不达标。两者性质不同，处理方式也不同。\n"
        "\n**滤波说明**：用的是零相位滤波（sosfiltfilt），"
        "峰谷时刻没有被平移；因果滤波会整体后移，不适合看时刻。\n")
    return (disp_dt, br, peaks, amp_has_breath, coh, good_ratio, best_run_s)


# ==================== 步骤 6：呼吸频谱 ====================

def step6_breath_spectrum(br, out, guide, meta):
    frq, mag = spectrum(br)
    f_pk, pk, prom = band_peak(frq, mag, *BREATH_BAND)
    df = vsp_core.FS / len(br)          # 频率分辨率

    # 主峰的等效正弦幅度（mm），绝对量。
    # 它比显著度有用，因为显著度 = 峰/带内中位数，是无量纲比值，
    # 对幅度缩放不敏感，无法回答「起伏有多大」。等效幅度能。
    #
    # 但它也**不能**用来判断「是否在憋气」：实测憋气组 0.17-2.28 mm
    # 与自然呼吸组 0.63-2.27 mm 完全重叠（详见 HOLD_PEAK_HINT_MM 处的说明）。
    # 它只能回答「这条数据的呼吸带起伏有多大」，不能回答「受试者在做什么」。
    pk_mm = float(pk * 2 / len(br)) if np.isfinite(pk) else np.nan

    m = frq <= 1.0
    write_csv(out / "06_呼吸频谱.csv",
              ["频率_Hz", "对应_bpm", "幅度"],
              [[round(frq[i], 5), round(frq[i] * 60, 2), f"{mag[i]:.5g}"]
               for i in np.where(m)[0]])

    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(frq[m] * 60, mag[m], color=C["breath"], lw=1.4)
    ax.axvspan(BREATH_BAND[0] * 60, BREATH_BAND[1] * 60,
               color=C["band"], alpha=0.13, label="呼吸带 6-30 bpm")
    if np.isfinite(f_pk):
        ax.axvline(f_pk * 60, color=C["peak"], ls="--", lw=1.4,
                   label=f"主峰 {f_pk * 60:.1f} bpm")
    if meta and not meta["breath_hold"]:
        ax.axvline(meta["breath_count"] * 2, color=C["signal"], ls=":", lw=1.6,
                   label=f"自报参考 {meta['breath_count'] * 2:.0f} bpm（弱真值）")
    ax.set_xlabel("呼吸率 (次/分)")
    ax.set_ylabel("幅度")
    ax.set_title("第 6 步　呼吸频谱：主峰位置就是呼吸率")
    ax.set_xlim(0, 60)
    ax.legend(loc="upper right", fontsize=9)
    plotting.note(ax,
                  f"精度上限：30 秒数据的频率分辨率是 {df:.4f} Hz = {df * 60:.1f} bpm\n"
                  f"所以呼吸率只能给到 {df * 60:.0f} bpm 的整数倍\n"
                  "结果总是 8、10、12 这类数就是这个原因，不是巧合\n"
                  "判读：应有单一明显主峰；多峰或平坦说明信号差",
                  loc="center left")
    fig.savefig(out / "06_呼吸频谱.png")
    plt.close(fig)

    err = None
    if meta and not meta["breath_hold"]:
        # 自报次数是 30 秒内总次数（已向用户确认），换算成 bpm 要 ×2
        err = f_pk * 60 - meta["breath_count"] * 2

    guide.append(
        "## 第 6 步　呼吸频谱　`06_呼吸频谱.csv` / `.png`\n\n"
        f"主峰 {f_pk * 60:.1f} bpm，等效幅度 {pk_mm:.3f} mm，"
        f"谱峰显著度 {prom:.1f} dB。"
        + (f"受试者自报 {meta['breath_count']} 次/30 秒 = {meta['breath_count'] * 2:.0f} bpm，"
           f"偏差 {err:+.1f} bpm。\n\n"
           "**自报值是弱真值**：由受试者自己报告，不是看秒表计数，\n"
           "加上频率分辨率本身 2 bpm，两者相差 4 bpm 以内都算相符。\n\n"
           if err is not None else "\n\n") +
        f"**精度上限**：30 秒 20 Hz 的频率分辨率是 {df:.4f} Hz，也就是 {df * 60:.1f} bpm。\n"
        f"这意味着呼吸率只能落在 {df * 60:.0f} bpm 的整数倍上。想更细必须采更长时间。\n\n"
        "**怎么看**：绿区内应有一个明显主峰，且与蓝色虚线（自数真值）接近。\n"
        "出现多个高度接近的峰，说明呼吸不规律或者混进了别的运动。\n"
        + "\n**显著度和等效幅度的分工**：\n"
        "显著度是「峰 / 带内中位数」的比值，无量纲，不随幅度缩放变化，\n"
        "它回答「峰突不突出」。等效幅度是绝对量，回答「起伏有多大」。\n"
        "**两者都无法回答「受试者是否在憋气」**：实测憋气记录的主峰幅度\n"
        "跨 0.17-2.28 mm，自然呼吸跨 0.63-2.27 mm，两组完全重叠。\n"
        "原因是憋气时仍可能有其他周期性运动（体位摆动等），\n"
        "雷达看到的是位移，分不清位移由什么产生。\n"
        + ("\n**本条是憋气记录**：此处不做真值比较。\n"
           "注意不要反推「有主峰就说明没憋气」—— 已有确认在憋气但\n"
           "呼吸带主峰达 2.28 mm 的实例（lsw 103753，γ=0.720 相位可信）。\n"
           if meta and meta["breath_hold"] else ""))
    return f_pk, prom, err, pk_mm


# ==================== 步骤 7：心跳频带 ====================

def step7_heart(disp, out, guide, meta):
    ht = bandpass(disp, *HEART_BAND)
    frq, mag = spectrum(ht)
    f_pk, _, prom = band_peak(frq, mag, *HEART_BAND)
    df = vsp_core.FS / len(ht)

    m = (frq >= 0.5) & (frq <= 3.0)
    write_csv(out / "07_心跳频带.csv",
              ["频率_Hz", "对应_bpm", "幅度"],
              [[round(frq[i], 5), round(frq[i] * 60, 2), f"{mag[i]:.5g}"]
               for i in np.where(m)[0]])

    t = np.arange(len(ht)) / vsp_core.FS
    fig, axes = plt.subplots(2, 1, figsize=(11, 6.4))
    axes[0].plot(t, ht, color=C["heart"], lw=1.0)
    axes[0].set_xlabel("时间 (秒)")
    axes[0].set_ylabel("位移 (mm)")
    axes[0].set_title(f"① 心跳带位移 {HEART_BAND[0]}-{HEART_BAND[1]} Hz"
                      f"（{HEART_BAND[0]*60:.0f}-{HEART_BAND[1]*60:.0f} bpm）"
                      f"　起伏 {ht.std():.4f} mm", loc="left")

    axes[1].plot(frq[m] * 60, mag[m], color=C["heart"], lw=1.4)
    axes[1].axvspan(HEART_BAND[0] * 60, HEART_BAND[1] * 60,
                    color=C["heart"], alpha=0.10, label="心跳带 48-120 bpm")
    if np.isfinite(f_pk):
        axes[1].axvline(f_pk * 60, color=C["peak"], ls="--", lw=1.4,
                        label=f"主峰 {f_pk * 60:.1f} bpm")
    if meta:
        axes[1].axvline(meta["hr_band"], color=C["signal"], ls=":", lw=1.6,
                        label=f"手环平均 {meta['hr_band']} bpm")
    axes[1].set_xlabel("心率 (次/分)")
    axes[1].set_ylabel("幅度")
    axes[1].set_title("② 心跳频带频谱", loc="left")
    axes[1].legend(loc="upper right", fontsize=9)
    plotting.note(axes[1],
                  "判读要点（这一步最容易过度解读）\n"
                  "· 有峰不等于测对了：带内总会有个最大值\n"
                  "· 手环是一段时间的平均值，不是逐拍真值，只能粗核\n"
                  "· 呼吸的谐波会落进这个带造成假峰\n"
                  "· 憋气段没有呼吸干扰，最可能看到真心跳",
                  loc="center left")

    fig.suptitle("第 7 步　心跳频带：只能说明带内有没有突出峰", fontsize=12, y=0.997)
    fig.tight_layout()
    fig.savefig(out / "07_心跳频带.png")
    plt.close(fig)

    guide.append(
        "## 第 7 步　心跳频带　`07_心跳频带.csv` / `.png`\n\n"
        f"带内主峰 {f_pk * 60:.1f} bpm，谱峰显著度 {prom:.1f} dB，"
        f"带内起伏 {ht.std():.4f} mm。"
        + (f"手环平均心率 {meta['hr_band']} bpm，"
           f"差 {f_pk * 60 - meta['hr_band']:+.1f} bpm。\n\n" if meta else "\n\n") +
        "**这里的显著度不是 SNR**：它只是「峰值 / 带内中位数」，\n"
        "没有噪声模型，只描述峰有多突出。之前叫 SNR 是不准确的。\n\n"
        "**为什么不能只看有没有峰**：任何频带内都必然存在最大值。\n"
        f"再加上频率分辨率 {df * 60:.1f} bpm，"
        "以及呼吸谐波可能落进 48-120 bpm，假峰很常见。\n\n"
        "**手环只能粗核**：手环给的是平均心率，不是逐拍时刻。\n"
        "要验证心跳时刻和 BCG 波形，必须有指夹血氧、胸带或 ECG 这类逐拍参考。\n"
        "在拿到之前，所有 BCG 相关结论都只能标为未验证。\n"
        + ("**本条是憋气记录**：没有呼吸干扰，是观察心跳的最好条件。\n"
           if meta and meta["breath_hold"] else
           "**本条有自然呼吸**：呼吸谐波可能污染此带，结果要更保守看待。\n"))
    return f_pk, prom, ht


# ==================== 步骤 8：质量红旗 ====================

def step8_flags(X, target_bin, move_mm, br, peaks, has_breath, prom_breath,
                err_bpm, out, guide, meta, nfr, coh, good_ratio, best_run_s,
                pk_mm):
    flags = []

    flags.append(["帧数完整", "通过" if nfr == EXPECTED_FRAMES else "不通过",
                  f"{nfr} 帧", "必须 600 帧"])

    # 相位相干度：这是总闸，排在其他项前面。
    # 它不通过时，位移/呼吸率/心跳全部无意义，后面的项只是参考。
    if coh >= GOOD_COHERENCE:
        coh_res = "通过"
    elif coh >= MIN_COHERENCE:
        coh_res = "存疑"
    else:
        coh_res = "不通过"
    flags.append(["相位相干度（总闸）", coh_res, f"{coh:.3f}",
                  f"≥{GOOD_COHERENCE} 可信；{MIN_COHERENCE}-{GOOD_COHERENCE} 断续可用；"
                  f"<{MIN_COHERENCE} 相位随机，位移无效"])
    flags.append(["相干时间占比", "通过" if good_ratio >= 0.5 else "存疑",
                  f"{good_ratio*100:.0f}%　最长连续 {best_run_s:.0f} 秒",
                  f"2 秒窗中相干度≥{SEG_COHERENCE} 的比例；"
                  f"低于 50% 说明只能分段分析"])

    flags.append(["目标移动量（幅度重心）",
                  "否" if move_mm <= MOVE_LARGE_MM else "是",
                  f"{move_mm:.0f} mm",
                  f"超过 {MOVE_LARGE_MM:.0f} mm 算大幅移动"
                  f"（实测静止 63-75 mm、人动 120-147 mm）"])

    amp = float(np.abs(X[:, 0, target_bin]).mean())
    amp_all = float(np.abs(X[:, 0, LEAK_BINS:]).mean())
    ratio_db = 20 * np.log10(amp / (amp_all + 1e-9))
    flags.append(["目标相对平均回波", "通过" if ratio_db > 0 else "存疑",
                  f"{ratio_db:+.1f} dB", "低于平均说明选中的可能不是主目标"])

    if coh < MIN_COHERENCE:
        # 相位随机时，呼吸率与真值的比对没有意义：偶尔对上是碰巧。
        # 实测 093824（工况 4）检出 9 次 / 自报 9 次完全吻合，
        # 但那条的相干度只有 0.023，比噪声本底还低。若照常判「通过」，
        # 就会把纯伪影当成最好的一条数据。
        flags.append(["呼吸/心跳指标", "不通过", "未计算",
                      "相位相干度未过总闸，下游指标一律不成立"])
    elif meta and meta["breath_hold"]:
        # 憋气三项一律只给「通过 / 存疑」，不给「不通过」。
        #
        # 为什么降级：原本这三项是当算法自检用的 —— 憋气应平坦，
        # 若显示呼吸就说明算法在骗人。这个逻辑已被实测推翻：
        # lsw 102905 / 103753 经受试者确认确实在憋气，但 γ 有 0.799 / 0.720
        # （相位可信），呼吸带主峰 1.066 / 2.284 mm，图上是规律的约 12 bpm 起伏。
        # 相位可信 + 起伏真实 → 这不是伪影，是憋气时仍存在的其他运动。
        # 也就是说「憋气 → 呼吸带应平坦」这个前提本身不成立，
        # 拿它判「不通过」会把真实数据自动剔除。
        #
        # 幅度这项传的是 amp_has_breath（纯幅度判定），不是含相干度的
        # has_breath。憋气检查的物理量是「呼吸带有没有起伏」，
        # 与相位质量无关；把相干度 and 进来会让「相位越好越容易判失败」，
        # 语义就反了。判据必须只依赖它真正检查的那个量。
        quiet = np.isfinite(pk_mm) and pk_mm < HOLD_PEAK_HINT_MM
        flags.append(["憋气记录-主峰幅度", "通过" if quiet else "存疑",
                      f"{pk_mm:.3f} mm（显著度 {prom_breath:.1f} dB，仅参考）",
                      f"仅提示：低于 {HOLD_PEAK_HINT_MM} mm 说明呼吸带确实安静"
                      f"（lrq 实测 0.17/0.24 mm）；高于此值需人工看图，"
                      f"但不代表标签错 —— lsw 两条 1.07/2.28 mm 经确认确实在憋气"])
        flags.append(["憋气记录-幅度判定", "通过" if not has_breath else "存疑",
                      f"带内起伏 {br.std():.3f} mm",
                      f"仅提示：低于 {MIN_BREATH_STD_MM} mm 为安静；"
                      f"超出说明憋气段仍有其他运动，来源未验证"])
        flags.append(["憋气记录-检出次数", "通过" if len(peaks) == 0 else "存疑",
                      f"检出 {len(peaks)} 次",
                      "仅提示：憋气理想应为 0 次；非 0 需人工看图确认是"
                      "噪声被数成呼吸，还是憋气段真有周期性体动"])
    elif err_bpm is not None:
        # 判据放宽到 ±4 bpm 的理由（不是为了让结果好看）：
        #   1. 真值由受试者自己报告，不是看秒表数的，本身有误差；
        #   2. 30 秒数据的频率分辨率就是 2 bpm，算法侧固有量化误差 ±1 个单元。
        #   两项叠加，±2 bpm 的判据过严，会把正常数据判成不可用。
        ok = abs(err_bpm) <= 4.0
        flags.append(["呼吸率对自报真值", "通过" if ok else "存疑",
                      f"偏差 {err_bpm:+.1f} bpm",
                      "放宽到 ±4 bpm：自报真值较弱 + 频率分辨率 2 bpm"])
        n_gap = abs(len(peaks) - meta["breath_count"])
        flags.append(["检出次数对自报", "通过" if n_gap <= 2 else "存疑",
                      f"检出 {len(peaks)} 次 / 自报 {meta['breath_count']} 次",
                      "放宽到 ±2 次，同上"])

    bad = sum(1 for f in flags if f[1] == "不通过")
    doubt = sum(1 for f in flags if f[1] == "存疑")
    verdict = "不可用" if bad else ("存疑" if doubt else "可用")

    write_csv(out / "08_质量红旗.csv",
              ["检查项", "结果", "实测", "判据"],
              flags + [["总体结论", verdict, f"不通过 {bad} 项 / 存疑 {doubt} 项", ""]])

    guide.append(
        "## 第 8 步　质量红旗　`08_质量红旗.csv`\n\n"
        f"**总体结论：{verdict}**（不通过 {bad} 项，存疑 {doubt} 项）\n\n"
        + "\n".join(f"- {f[0]}：{f[1]}（{f[2]}）" for f in flags) + "\n\n"
        "**怎么用**：这张表决定这条数据能不能进后续统计。\n"
        "「不可用」的数据必须剔除，不能靠后期算法补救。\n"
        "「存疑」需要人工看图确认。\n\n"
        "**先看相位相干度这一项**：它是总闸。不过闸时，\n"
        "呼吸率哪怕和自报值完全吻合也是碰巧 —— 实测有一条工况 4 的数据\n"
        "检出 9 次 / 自报 9 次完全一致，但相干度只有 0.023（噪声本底 0.041），\n"
        "整条曲线都是带通滤波把随机相位整形出来的。\n"
        "所以这一项不过，下游指标一律不再参与判定。\n\n"
        "**已移除的项**：原来的「相位跳变次数」判据（非 0 即存疑）已删。\n"
        "原因是 unwrap 的输出按定义 |dφ|≤π，那个计数并不是失败次数；\n"
        "且 π/2 只对应 12 mm/s 径向速度，正常呼吸就会超，判据本身不成立。\n"
        "改用相干度，它不做解缠，没有模糊问题。\n")
    return verdict, flags


# ==================== 主流程 ====================

def explain(cap_dir, out_name="explain", forced_bin=None):
    cap_dir = Path(cap_dir)
    bins = sorted(cap_dir.glob("*_Raw_0.bin"))
    if not bins:
        raise FileNotFoundError(f"{cap_dir} 下没有 *_Raw_0.bin")
    bin_path = str(bins[0])

    out = cap_dir / out_name
    out.mkdir(exist_ok=True)
    meta = read_meta(cap_dir)
    guide = []

    print(f"采集目录：{cap_dir.name}")
    if meta:
        print(f"受试者 {meta['subject']}　工况 {meta['mode']} "
              f"{WORK_MODE_NAMES.get(meta['mode'], '')}")
        print(f"手环心率 {meta['hr_band']} bpm　自数呼吸 {meta['breath_count']} 次"
              f"{'（憋气）' if meta['breath_hold'] else ''}")

    print("[1/8] 帧完整性")
    ok, nfr = step1_integrity(bin_path, out, guide)
    if not ok:
        (out / "阅读指南.md").write_text("\n".join(guide), encoding="utf-8")
        print("  完整性不通过，停止。")
        return

    print("      构建慢时间矩阵（首次较慢，之后走缓存）")
    X = vsp_core.build_slowtime(bin_path,
                                cache=bin_path.replace(".bin", "_slowtime.npy"),
                                verbose=False)

    print("[2/8] 距离能量分布")
    energy, _ = step2_range_profile(X, out, guide)
    print("[3/8] 距离-时间热图")
    per_frame, centroid, move_mm = step3_range_time(X, out, guide)
    print("[4/8] 候选 bin 波形对比")
    target_bin, auto_bin = step4_candidates(X, energy, out, guide, forced_bin)
    print(f"      选定 bin {target_bin}（{target_bin * vsp_core.M_PER_BIN:.2f} m）"
          f"{'　自动' if forced_bin is None else '　手动指定'}")
    print("[5/8] 位移提取")
    (disp, br, peaks, has_breath,
     coh, good_ratio, best_run_s) = step5_displacement(X, target_bin, out, guide, meta)
    print(f"      相位相干度 {coh:.3f}"
          f"（2 秒窗达标 {good_ratio*100:.0f}%，最长连续 {best_run_s:.0f} 秒）"
          f"{'' if coh >= MIN_COHERENCE else '　← 低于下限，位移不可用'}")
    print("[6/8] 呼吸频谱")
    f_br, prom_br, err, pk_mm = step6_breath_spectrum(br, out, guide, meta)
    print("[7/8] 心跳频带")
    f_ht, prom_ht, _ = step7_heart(disp, out, guide, meta)
    print("[8/8] 质量红旗")
    verdict, flags = step8_flags(X, target_bin, move_mm, br, peaks, has_breath,
                                 prom_br, err, out, guide, meta, nfr,
                                 coh, good_ratio, best_run_s, pk_mm)

    head = [f"# 采集解读：{cap_dir.name}\n"]
    if meta:
        head.append(
            f"- 受试者：{meta['subject']}\n"
            f"- 工况：{meta['mode']}　{WORK_MODE_NAMES.get(meta['mode'], '')}\n"
            f"- 手环心率：{meta['hr_band']} bpm（平均值，不是逐拍真值）\n"
            f"- 自数呼吸：{meta['breath_count']} 次"
            f"{'　→ 本条是憋气记录' if meta['breath_hold'] else ''}\n")
    head.append(
        f"- 选定目标：bin {target_bin} = {target_bin * vsp_core.M_PER_BIN:.2f} m"
        f"（自动初选 {auto_bin}）\n"
        f"- **总体结论：{verdict}**\n\n"
        "本目录每一步都有 CSV 和 PNG。CSV 可直接用 Excel 打开。\n"
        "按顺序看，前一步不通过就不要看后面的。\n\n---\n")

    (out / "阅读指南.md").write_text("\n".join(head + guide), encoding="utf-8")
    print(f"完成。输出目录：{out}")
    print(f"先看：{out / '阅读指南.md'}")
    return verdict


def main():
    ap = argparse.ArgumentParser(description="单条采集逐步解释")
    ap.add_argument("capture_dir", help="采集目录")
    ap.add_argument("--target-bin", type=int, default=None,
                    help="手动指定目标 bin，覆盖自动选择")
    ap.add_argument("--out-dir", default="explain", help="输出子目录名")
    a = ap.parse_args()
    explain(a.capture_dir, a.out_dir, a.target_bin)


if __name__ == "__main__":
    main()
