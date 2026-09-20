#!/usr/bin/env python3
"""雷达数据探查器：从 pcap/bin 提取最基本的雷达信息

解释器：C:\\Users\\34219\\AppData\\Local\\Programs\\Python\\Python39\\python.exe

用法：
  radar_inspector.py <session_dir> [选项]

选项：
  --behavior       使用行为波形参数（默认妊娠）
  --frames N       只处理前 N 帧（默认全部，大文件时建议限制）
  --target-bin N   手动指定目标 bin（用于验证或修正自动选择）
  --no-plot        不生成图像，仅输出文本报告

输出：
  - 控制台文本报告（L1-L7 所有基本信息）
  - radar_inspector.png（八宫格可视化）
  - radar_inspector_data.npz（中间结果，供进一步分析）

改进（v2）：
  - 目标检测限制在 0.3-2.5m（排除近场杂波）
  - 基于呼吸带能量选择目标（比纯幅度更可靠）
  - 显示候选目标的呼吸信号质量评分
  - 支持手动指定目标 bin

改进（v3，可视化直观化）：
  - 带通位移波形 + 逐次呼吸峰谷标注（呼吸次数、周期、规律性 CV）
  - STFT 时频图：呼吸率随时间，憋气/体动表现为亮带断裂
  - 相位 RTI：各距离 bin 的带通位移热图，替代看不出东西的幅度 RTI
  - IQ 复平面轨迹：真目标是圆弧，噪声是散点团
  为什么原来的位移图不直观：phase_to_displacement_mm 会把线性趋势加回去
  （unwrap 需要），于是 0.5 mm 的呼吸被几毫米慢漂移埋掉。带通解决这点。

示例：
  # 自动选择目标
  radar_inspector.py ./data/session_xxx

  # 手动指定 bin 13 为目标
  radar_inspector.py ./data/session_xxx --target-bin 13
"""
import sys
import os
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks, stft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import radar_reader as rr


# ============ 常量定义 ============
C = 299792458.0  # 光速 m/s
SAMPLE_RATE_HZ = 5120e3  # ADC 采样率
SLOPE_HZ_PER_S = 60e6 / 1e-6  # chirp 斜率 60 MHz/us
FC_GHZ = 60.25  # 中心频率（近似，用于波长计算）
LAMBDA_M = C / (FC_GHZ * 1e9)  # 波长（米）

# 呼吸带（Hz）= 6..36 bpm，与 quicklook.py 保持一致
BR_LO, BR_HI = 0.1, 0.6
# 相位 RTI 的距离显示上限（米）
RTI_MAX_M = 3.0


def print_section(title):
    """打印分节标题"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def radar_params(wf):
    """计算雷达参数：分辨率、最大距离等"""
    # 距离参数
    t_sample = wf["samples"] / SAMPLE_RATE_HZ  # 采样窗时长（秒）
    bandwidth_hz = t_sample * SLOPE_HZ_PER_S    # 有效带宽
    range_res = C / (2 * bandwidth_hz)          # 距离分辨率
    max_range = range_res * wf["samples"] / 2   # 最大不模糊距离

    # 速度参数（基于帧周期）
    frame_time_s = wf["period_ms"] / 1000.0
    max_velocity = LAMBDA_M / (4 * frame_time_s)  # 最大不模糊速度

    # 角度参数（假设线性阵列，间距 lambda/2）
    angle_res_deg = np.rad2deg(LAMBDA_M / (wf["rx"] * LAMBDA_M / 2)) if wf["rx"] > 1 else np.nan

    return {
        "range_res_m": range_res,
        "max_range_m": max_range,
        "max_velocity_mps": max_velocity,
        "angle_res_deg": angle_res_deg,
        "bandwidth_mhz": bandwidth_hz / 1e6,
        "frame_time_s": frame_time_s,
    }


def estimate_noise_floor(range_profile_db):
    """估计噪声基底：取最低 20% 的中位数"""
    sorted_vals = np.sort(range_profile_db.flatten())
    return np.median(sorted_vals[:int(len(sorted_vals) * 0.2)])


def detect_targets(range_profile_db, range_axis_m, noise_floor_db, threshold_db=15,
                   search_min_m=0.3, search_max_m=2.5):
    """目标检测：在有效区域内，超过噪底 threshold_db 的峰值

    search_min_m: 最小搜索距离（排除近场杂波）
    search_max_m: 最大搜索距离
    """
    peaks = []
    search_start = np.argmin(np.abs(range_axis_m - search_min_m))
    search_end = np.argmin(np.abs(range_axis_m - search_max_m))

    for i in range(search_start, search_end):
        if i == 0 or i >= len(range_profile_db) - 1:
            continue
        if range_profile_db[i] > noise_floor_db + threshold_db:
            # 检查是否是局部最大值
            if range_profile_db[i] > range_profile_db[i-1] and \
               range_profile_db[i] > range_profile_db[i+1]:
                peaks.append(i)
    return peaks


def phase_unwrap_robust(phase_rad):
    """鲁棒相位展开：先去趋势，再 unwrap，再恢复"""
    # 移除线性趋势（避免大幅度运动导致的 unwrap 失败）
    n = len(phase_rad)
    x = np.arange(n)
    p = np.polyfit(x, phase_rad, 1)
    detrended = phase_rad - np.polyval(p, x)
    unwrapped = np.unwrap(detrended)
    return unwrapped + np.polyval(p, x)


def phase_to_displacement_mm(phase_rad):
    """相位转位移（毫米）：Δr = λ × Δφ / (4π)"""
    phase_unwrapped = phase_unwrap_robust(phase_rad)
    # 去掉均值，只关心变化量
    phase_unwrapped -= phase_unwrapped.mean()
    return phase_unwrapped * (LAMBDA_M * 1000) / (4 * np.pi)


def bandpass(x, fs_hz, lo=BR_LO, hi=BR_HI, order=4):
    """呼吸带带通。先去线性趋势再滤，避免趋势在 filtfilt 边界造成振铃。

    这一步是"位移图看不出呼吸"的解药：phase_to_displacement_mm 会把线性
    趋势加回去（unwrap 的需要），于是 0.5 mm 的呼吸被几毫米的慢漂移埋掉。
    """
    x = np.asarray(x, dtype=float)
    n = len(x)
    x = x - np.polyval(np.polyfit(np.arange(n), x, 1), np.arange(n))
    nyq = fs_hz / 2.0
    b, a = butter(order, [lo / nyq, hi / nyq], btype="band")
    return filtfilt(b, a, x)


def detect_breaths(disp_bp_mm, fs_hz, lo=BR_LO, hi=BR_HI):
    """在带通位移上做峰检测，把波形变成可数的呼吸事件。

    distance 取最高呼吸频率对应周期的 0.7 倍（同 quicklook.py 的取法），
    既不会把一次呼吸拆成两个峰，也不至于漏掉快呼吸。
    """
    min_dist = max(1, int(fs_hz / hi * 0.7))
    peaks, _ = find_peaks(disp_bp_mm, distance=min_dist)
    troughs, _ = find_peaks(-disp_bp_mm, distance=min_dist)

    if len(peaks) > 1:
        intervals_s = np.diff(peaks) / fs_hz
        rate_bpm = 60.0 / intervals_s.mean()
        # 变异系数：越小越规律。憋气/乱动会把它抬起来
        cv = intervals_s.std() / intervals_s.mean() if intervals_s.mean() > 0 else np.nan
    else:
        intervals_s = np.array([])
        rate_bpm, cv = np.nan, np.nan

    return dict(peaks=peaks, troughs=troughs, intervals_s=intervals_s,
                rate_bpm=rate_bpm, cv=cv)


def breathing_stft(disp_bp_mm, fs_hz, win_s=20.0):
    """呼吸带 STFT。返回 (时间轴 s, 频率轴 bpm, 幅度 dB)

    win_s=20 s → 频率分辨率 0.05 Hz = 3 bpm，够分辨 16 vs 20 bpm；
    段数在 60 s 采集上约 11 段（50% 重叠），时间上还能看出变化。
    """
    nper = min(int(win_s * fs_hz), len(disp_bp_mm))
    if nper < 8:
        return None
    f, t, Z = stft(disp_bp_mm, fs=fs_hz, nperseg=nper, noverlap=nper // 2)
    mag_db = 20 * np.log10(np.abs(Z) + 1e-12)
    return t, f * 60.0, mag_db


def phase_rti(range_fft, fs_hz, nbin, rx=0):
    """各距离 bin 的带通相位位移，shape (nbin, 帧)

    幅度 RTI 看不出呼吸 —— 胸壁运动几乎不改变回波强度，只改变相位。
    换成相位后，真目标是局限在几个 bin 上的横向条纹；若整个距离轴同步
    起伏，那是整板振动/时钟抖动的共模，不是目标。
    """
    out = np.zeros((nbin, range_fft.shape[0]))
    for k in range(nbin):
        st = range_fft[:, :, rx, k].mean(axis=1)
        out[k] = bandpass(phase_to_displacement_mm(np.angle(st)), fs_hz)
    return out


def analyze_data(session_dir, wf, max_frames=None, manual_target_bin=None):
    """主分析流程：从 bin 提取所有基本信息

    manual_target_bin: 手动指定目标 bin（用于验证或修正）
    """

    print_section("L1: 数据完整性")
    info = rr.describe(session_dir, wf)
    total_frames = info["frames"]

    if max_frames is not None and max_frames < total_frames:
        print(f"\n⚠ 限制处理前 {max_frames} 帧（共 {total_frames} 帧）")
        nframes = max_frames
    else:
        nframes = total_frames

    print_section("L2: 雷达配置参数")
    params = radar_params(wf)
    print(f"波形参数:")
    print(f"  采样点数/chirp : {wf['samples']}")
    print(f"  RX 通道数       : {wf['rx']}")
    print(f"  Chirps/帧       : {wf['chirps']}")
    print(f"  TX 数           : {wf['tx']}")
    print(f"  帧周期          : {wf['period_ms']} ms")
    print(f"\n性能参数:")
    print(f"  带宽            : {params['bandwidth_mhz']:.2f} MHz")
    print(f"  距离分辨率      : {params['range_res_m']*100:.2f} cm")
    print(f"  最大探测距离    : {params['max_range_m']:.2f} m")
    print(f"  最大不模糊速度  : {params['max_velocity_mps']:.3f} m/s")
    if wf['rx'] > 1:
        print(f"  角度分辨率      : {params['angle_res_deg']:.1f}°")
    print(f"  波长            : {LAMBDA_M*1000:.3f} mm")

    print_section("L3: 读取数据并执行距离 FFT")
    print(f"正在读取 {nframes} 帧...")
    cube = rr.load_frames(session_dir, wf, start=0, count=nframes)
    print(f"数据立方体 shape: {cube.shape}  (帧, chirp, RX, 采样点)")
    print(f"数据类型: {cube.dtype}  内存占用: {cube.nbytes / 1024**2:.1f} MB")

    # 距离 FFT
    print("执行距离 FFT（已去直流 + Hanning 窗）...")
    range_fft = rr.range_fft(cube, window=True, remove_dc=True)
    print(f"频谱立方体 shape: {range_fft.shape}")

    # 计算距离轴
    range_axis_m = rr.range_axis(wf)

    # 距离剖面：对所有帧、所有 chirp、所有 RX 取平均
    range_profile = np.abs(range_fft).mean(axis=(0, 1, 2))  # 平均到 (samples,)
    range_profile_db = 20 * np.log10(range_profile + 1e-9)

    print_section("L4: 距离维分析")
    noise_floor = estimate_noise_floor(range_profile_db)
    targets = detect_targets(range_profile_db, range_axis_m, noise_floor, threshold_db=15,
                           search_min_m=0.3, search_max_m=2.5)

    print(f"噪声基底（估计）: {noise_floor:.1f} dB")
    print(f"搜索区间: 0.3 - 2.5 m（排除近场杂波）")
    print(f"检测到 {len(targets)} 个目标（>噪底 15 dB）:")
    for i, tgt_bin in enumerate(targets[:10]):  # 最多显示 10 个
        tgt_range_m = range_axis_m[tgt_bin]
        tgt_power_db = range_profile_db[tgt_bin]
        snr_db = tgt_power_db - noise_floor
        print(f"  #{i+1}: bin {tgt_bin:3d} -> {tgt_range_m:.3f} m  "
              f"功率 {tgt_power_db:.1f} dB  SNR {snr_db:.1f} dB")
    if len(targets) > 10:
        print(f"  ... 还有 {len(targets)-10} 个目标未显示")
    if len(targets) == 0:
        print("  ⚠ 未检测到明显目标（可能距离太近或功率太弱）")

    print_section("L5: 慢时间维分析（相位变化）")

    # 目标选择策略
    if manual_target_bin is not None:
        target_bin = manual_target_bin
        print(f"使用手动指定的目标: bin {target_bin} -> {range_axis_m[target_bin]:.3f} m")
    elif len(targets) > 0:
        # 多因素评分选择目标（更鲁棒）
        print("\n评估候选目标质量（多因素评分）...")
        candidates = []
        fs_hz = 1.0 / params['frame_time_s']

        for tgt_bin in targets[:8]:  # 评估前 8 个目标
            slowtime = range_fft[:, :, 0, tgt_bin].mean(axis=1)
            phase = np.angle(slowtime)
            displacement = phase_to_displacement_mm(phase)
            disp_rms = np.std(displacement)

            # 呼吸带能量 (0.1-0.6 Hz)
            displacement_centered = displacement - displacement.mean()
            windowed = displacement_centered * np.hanning(len(displacement_centered))
            spectrum = np.fft.rfft(windowed)
            freqs = np.fft.rfftfreq(len(displacement_centered), 1/fs_hz)
            br_mask = (freqs >= 0.1) & (freqs <= 0.6)
            br_energy = np.sum(np.abs(spectrum[br_mask])**2)
            total_energy = np.sum(np.abs(spectrum)**2)
            br_ratio = br_energy / (total_energy + 1e-30)

            # 主频率
            br_peak_idx = np.argmax(np.abs(spectrum[br_mask]))
            br_freq_hz = freqs[br_mask][br_peak_idx] if len(freqs[br_mask]) > 0 else 0

            # 多因素评分
            score = 0
            rng = range_axis_m[tgt_bin]
            snr_db = range_profile_db[tgt_bin] - noise_floor

            # 因素1: 距离权重（0.3-1.5m 人体典型距离）
            if 0.3 <= rng <= 1.5:
                dist_score = 40 * (1.0 - abs(rng - 0.65) / 1.2)  # 0.65m 为中心
            else:
                dist_score = 5

            # 因素2: 位移幅度（>0.1mm 认为有效）
            amp_score = min(25, disp_rms / 0.1 * 25)

            # 因素3: 呼吸带绝对能量（避免低能量 bin 虚高）
            energy_score = min(20, np.log10(br_energy + 1e-30) + 60)

            # 因素4: 呼吸频率合理性（6-36 bpm）
            br_bpm = br_freq_hz * 60
            if 10 <= br_bpm <= 25:
                freq_score = 15
            elif 6 <= br_bpm <= 36:
                freq_score = 10
            else:
                freq_score = 0

            score = dist_score + amp_score + energy_score + freq_score

            candidates.append({
                'bin': tgt_bin,
                'range_m': rng,
                'snr_db': snr_db,
                'disp_rms': disp_rms,
                'br_ratio': br_ratio,
                'br_energy': br_energy,
                'br_bpm': br_bpm,
                'score': score,
                'dist_score': dist_score,
                'amp_score': amp_score,
                'energy_score': energy_score,
                'freq_score': freq_score,
            })

        # 按得分排序
        candidates.sort(key=lambda x: x['score'], reverse=True)

        # 显示评估结果（前5个）
        print("\n候选目标综合评分 (距离/幅度/能量/频率):")
        print(f"{'Bin':<6} {'Range(m)':<10} {'RMS(mm)':<10} {'BR(bpm)':<10} {'Score':<8} {'详情'}")
        print("-" * 75)
        for c in candidates[:5]:
            detail = f"D:{c['dist_score']:.0f} A:{c['amp_score']:.0f} E:{c['energy_score']:.0f} F:{c['freq_score']:.0f}"
            print(f"{c['bin']:<6} {c['range_m']:<10.3f} {c['disp_rms']:<10.4f} "
                  f"{c['br_bpm']:<10.1f} {c['score']:<8.1f} {detail}")

        # 选择得分最高的
        best = candidates[0]
        target_bin = best['bin']
        print(f"\n>>> 自动选择: bin {target_bin} ({best['range_m']:.3f} m) "
              f"得分 {best['score']:.1f}/100")
    else:
        # 没有明显目标，选搜索区间内最强的
        search_start = np.argmin(np.abs(range_axis_m - 0.3))
        search_end = np.argmin(np.abs(range_axis_m - 2.5))
        target_bin = search_start + np.argmax(range_profile[search_start:search_end])
        print(f"⚠ 无明显目标，选择搜索区间内最强 bin: {target_bin} -> {range_axis_m[target_bin]:.3f} m")

    target_range_m = range_axis_m[target_bin]
    print(f"选定目标: bin {target_bin} -> {target_range_m:.2f} m")

    # 提取慢时间序列：选第一个 RX，所有 chirp 平均
    slowtime_complex = range_fft[:, :, 0, target_bin].mean(axis=1)  # (帧,)
    phase_rad = np.angle(slowtime_complex)
    displacement_mm = phase_to_displacement_mm(phase_rad)

    time_axis_s = np.arange(nframes) * params['frame_time_s']

    fs_hz = 1.0 / params['frame_time_s']
    disp_bp_mm = bandpass(displacement_mm, fs_hz)

    print(f"相位统计:")
    print(f"  均值（原始）: {np.mean(phase_rad):.3f} rad")
    print(f"  标准差      : {np.std(phase_rad):.3f} rad")
    print(f"位移统计（含慢漂移）:")
    print(f"  RMS         : {np.std(displacement_mm):.3f} mm")
    print(f"  峰峰值      : {np.ptp(displacement_mm):.2f} mm")
    print(f"位移统计（{BR_LO}-{BR_HI} Hz 带通后，这才是呼吸本身）:")
    print(f"  RMS         : {np.std(disp_bp_mm):.3f} mm")
    print(f"  峰峰值      : {np.ptp(disp_bp_mm):.2f} mm")
    print(f"  最大速率    : {np.max(np.abs(np.diff(disp_bp_mm))) * fs_hz:.2f} mm/s")

    br = detect_breaths(disp_bp_mm, fs_hz)
    print(f"\n呼吸事件（带通波形峰检测）:")
    print(f"  检出呼吸次数: {len(br['peaks'])} 次 / {nframes * params['frame_time_s']:.0f} s")
    if len(br['intervals_s']):
        print(f"  平均周期    : {br['intervals_s'].mean():.2f} s "
              f"(最短 {br['intervals_s'].min():.2f} / 最长 {br['intervals_s'].max():.2f})")
        print(f"  呼吸率      : {br['rate_bpm']:.1f} bpm（逐周期平均）")
        print(f"  规律性 CV   : {br['cv']:.3f}"
              f"  （<0.2 平稳；>0.4 有憋气或体动）")
    else:
        print(f"  ⚠ 峰数不足，无法给出周期统计")

    stft_out = breathing_stft(disp_bp_mm, fs_hz)

    nbin_rti = min(int(RTI_MAX_M / params['range_res_m']) + 1, wf['samples'] // 2)
    print(f"\n构造相位 RTI（0-{RTI_MAX_M:.0f} m，{nbin_rti} 个 bin）...")
    prti = phase_rti(range_fft, fs_hz, nbin_rti)

    # 局域性：真目标的呼吸能量应集中在目标 bin 附近，而非全距离共模
    bin_rms = prti.std(axis=1)
    lo_k, hi_k = max(0, target_bin - 2), min(nbin_rti, target_bin + 3)
    locality = bin_rms[lo_k:hi_k].sum() / (bin_rms.sum() + 1e-30)
    print(f"  目标 bin ±2 占 0-{RTI_MAX_M:.0f} m 呼吸位移能量 {locality:.1%}"
          f"  （>50% 说明是局域目标，不是整板振动）")

    print_section("L6: 多通道分析（RX 通道对比）")
    rx_powers = []
    for rx_idx in range(wf['rx']):
        rx_profile = np.abs(range_fft[:, :, rx_idx, :]).mean(axis=(0, 1))
        rx_powers.append(rx_profile[target_bin])
    rx_powers = np.array(rx_powers)
    rx_powers_db = 20 * np.log10(rx_powers / rx_powers.max() + 1e-9)

    print(f"目标 bin {target_bin} 在各 RX 的相对功率:")
    for rx_idx, pwr_db in enumerate(rx_powers_db):
        print(f"  RX{rx_idx}: {pwr_db:+.1f} dB")

    # 通道间相位差（用于角度估计）
    if wf['rx'] > 1:
        phase_diff_01 = np.angle(slowtime_complex) - \
                        np.angle(range_fft[:, :, 1, target_bin].mean(axis=1))
        phase_diff_mean = np.mean(phase_diff_01)
        phase_diff_std = np.std(phase_diff_01)
        print(f"\nRX0-RX1 相位差:")
        print(f"  均值: {phase_diff_mean:.3f} rad ({np.rad2deg(phase_diff_mean):.1f}°)")
        print(f"  标准差: {phase_diff_std:.3f} rad (稳定性指标)")

    print_section("L7: 时空特征（Range-Time 热图）")
    # 构造 Range-Time Intensity (RTI) 图
    # 取第一个 RX，所有 chirp 平均
    rti = np.abs(range_fft[:, :, 0, :]).mean(axis=1)  # (帧, bin)
    rti_db = 20 * np.log10(rti.T + 1e-9)  # 转置为 (bin, 帧) 便于绘图

    print(f"RTI 矩阵 shape: {rti_db.shape}  (距离 bin × 时间帧)")
    print(f"动态范围: {rti_db.min():.1f} ~ {rti_db.max():.1f} dB")

    # 距离维的时间方差（哪些 bin 有运动）
    range_var = np.var(rti, axis=0)  # 对时间轴求方差
    dynamic_bins = np.where(range_var > np.median(range_var) * 2)[0]
    print(f"检测到 {len(dynamic_bins)} 个'动态' bin（方差 > 中位数×2）")

    return {
        "wf": wf,
        "params": params,
        "range_axis_m": range_axis_m,
        "range_profile_db": range_profile_db,
        "noise_floor_db": noise_floor,
        "targets": targets,
        "target_bin": target_bin,
        "target_range_m": target_range_m,
        "time_axis_s": time_axis_s,
        "phase_rad": phase_rad,
        "displacement_mm": displacement_mm,
        "disp_bp_mm": disp_bp_mm,
        "slowtime_complex": slowtime_complex,
        "breaths": br,
        "stft": stft_out,
        "phase_rti": prti,
        "nbin_rti": nbin_rti,
        "locality": locality,
        "fs_hz": fs_hz,
        "rx_powers_db": rx_powers_db,
        "rti_db": rti_db,
        "nframes": nframes,
    }


def plot_results(data, output_path):
    """生成八宫格可视化"""
    fig, axes = plt.subplots(4, 2, figsize=(16, 17))
    fig.suptitle(
        f"Radar Data Inspector  |  target bin {data['target_bin']} "
        f"@ {data['target_range_m']:.2f} m  |  "
        f"{len(data['breaths']['peaks'])} breaths, {data['breaths']['rate_bpm']:.1f} bpm",
        fontsize=15, fontweight="bold")

    # (0,0) 距离剖面
    ax = axes[0, 0]
    ax.plot(data['range_axis_m'], data['range_profile_db'], lw=1)
    ax.axhline(data['noise_floor_db'], color='r', ls='--', label='Noise floor')
    ax.axhline(data['noise_floor_db'] + 15, color='orange', ls=':', label='Detection threshold')
    for tgt_bin in data['targets'][:5]:
        ax.axvline(data['range_axis_m'][tgt_bin], color='g', alpha=0.3, lw=1)
    ax.axvline(data['target_range_m'], color='red', lw=2, label=f"Selected target ({data['target_range_m']:.2f} m)")
    ax.set_xlabel("Range (m)")
    ax.set_ylabel("Power (dB)")
    ax.set_title("Range Profile (averaged over all frames/chirps/RX)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_xlim(0, min(5, data['range_axis_m'][-1]))

    # (0,1) RX 通道功率对比
    ax = axes[0, 1]
    rx_indices = np.arange(len(data['rx_powers_db']))
    ax.bar(rx_indices, data['rx_powers_db'], color='steelblue', edgecolor='black')
    ax.set_xlabel("RX Channel")
    ax.set_ylabel("Relative Power (dB)")
    ax.set_title(f"RX Power at Target bin {data['target_bin']} ({data['target_range_m']:.2f} m)")
    ax.set_xticks(rx_indices)
    ax.set_xticklabels([f"RX{i}" for i in rx_indices])
    ax.grid(axis='y', alpha=0.3)
    ax.axhline(0, color='black', lw=0.8)

    # (1,0) 漂移 vs 带通：说明为什么原来的位移图看不出呼吸
    ax = axes[1, 0]
    t = data['time_axis_s']
    ax.plot(t, data['displacement_mm'], lw=0.7, color='gray',
            label=f"raw (drift included), RMS={np.std(data['displacement_mm']):.2f} mm")
    ax.plot(t, data['disp_bp_mm'], lw=1.1, color='C0',
            label=f"bandpass {BR_LO}-{BR_HI} Hz, RMS={np.std(data['disp_bp_mm']):.2f} mm")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Displacement (mm)")
    ax.set_title("Why the raw phase plot looks flat: drift dominates")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # (1,1) 呼吸波形 + 逐次呼吸标注
    ax = axes[1, 1]
    d = data['disp_bp_mm']
    br = data['breaths']
    ax.plot(t, d, lw=1.2, color='C0')
    ax.plot(t[br['peaks']], d[br['peaks']], 'v', color='C3', ms=6,
            label=f"inhale peak ({len(br['peaks'])})")
    ax.plot(t[br['troughs']], d[br['troughs']], '^', color='C2', ms=5,
            label=f"exhale trough ({len(br['troughs'])})")
    ax.axhline(0, color='black', lw=0.6, alpha=0.5)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Displacement (mm)")
    cv_txt = f"CV={br['cv']:.2f}" if np.isfinite(br['cv']) else "CV=n/a"
    ax.set_title(f"Breathing waveform  |  {br['rate_bpm']:.1f} bpm, {cv_txt}")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # (2,0) STFT 时频图：呼吸率随时间
    ax = axes[2, 0]
    if data['stft'] is not None:
        st_t, st_bpm, st_db = data['stft']
        m = st_bpm <= 60
        im = ax.pcolormesh(st_t, st_bpm[m], st_db[m], cmap='magma', shading='auto')
        ax.axhline(br['rate_bpm'], color='cyan', ls='--', lw=1.2,
                   label=f"peak-count rate {br['rate_bpm']:.1f} bpm")
        ax.set_ylabel("Rate (bpm)")
        ax.set_title("STFT: breathing rate over time (bright band = steady breathing)")
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("dB", rotation=270, labelpad=12)
        ax.legend(fontsize=8, loc='upper right')
    else:
        ax.text(0.5, 0.5, "capture too short for STFT", ha='center', va='center')
    ax.set_xlabel("Time (s)")

    # (2,1) 位移频谱（检测周期性运动）
    ax = axes[2, 1]
    fs_hz = data['fs_hz']
    dc = data['disp_bp_mm'] - data['disp_bp_mm'].mean()
    spectrum = np.fft.rfft(dc * np.hanning(len(dc)))
    freqs_hz = np.fft.rfftfreq(len(dc), 1.0 / fs_hz)
    power_db = 20 * np.log10(np.abs(spectrum) + 1e-9)

    ax.plot(freqs_hz * 60, power_db, lw=0.8)
    ax.axvspan(BR_LO * 60, BR_HI * 60, color='C0', alpha=0.15,
               label=f"Breathing band ({BR_LO*60:.0f}-{BR_HI*60:.0f} bpm)")
    ax.axvspan(48, 120, color='C3', alpha=0.15, label='Heart band (48-120 bpm)')
    ax.set_xlabel("Frequency (bpm)")
    ax.set_ylabel("Power (dB)")
    ax.set_title("Displacement spectrum (bandpassed)")
    ax.set_xlim(0, 150)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

    # (3,0) 相位 RTI：哪些距离在动
    ax = axes[3, 0]
    prti = data['phase_rti']
    vmax = np.percentile(np.abs(prti), 99.5)
    extent = [0, t[-1], 0, data['range_axis_m'][data['nbin_rti'] - 1]]
    im = ax.imshow(prti, aspect='auto', origin='lower', extent=extent,
                   cmap='RdBu_r', vmin=-vmax, vmax=vmax, interpolation='nearest')
    ax.axhline(data['target_range_m'], color='k', ls='--', lw=1.2,
               label=f"target {data['target_range_m']:.2f} m")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Range (m)")
    ax.set_title(f"Phase RTI: bandpassed motion per range bin "
                 f"(locality {data['locality']:.0%})")
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Displacement (mm)", rotation=270, labelpad=14)
    ax.legend(fontsize=8, loc='upper right')

    # (3,1) IQ 复平面轨迹
    ax = axes[3, 1]
    z = data['slowtime_complex']
    ax.plot(z.real, z.imag, lw=0.5, color='C0', alpha=0.6)
    sc = ax.scatter(z.real, z.imag, c=t, cmap='viridis', s=4, zorder=3)
    ax.plot(0, 0, '+', color='k', ms=10)
    ax.set_aspect('equal', adjustable='datalim')
    ax.set_xlabel("I")
    ax.set_ylabel("Q")
    ax.set_title("IQ trajectory (arc = real target motion; blob = noise)")
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Time (s)", rotation=270, labelpad=14)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    print(f"\n✓ 图像已保存: {output_path}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    session_dir = sys.argv[1]
    use_behavior = "--behavior" in sys.argv
    no_plot = "--no-plot" in sys.argv

    # 解析 --frames 参数
    max_frames = None
    manual_target_bin = None
    for i, arg in enumerate(sys.argv):
        if arg == "--frames" and i + 1 < len(sys.argv):
            max_frames = int(sys.argv[i + 1])
        elif arg == "--target-bin" and i + 1 < len(sys.argv):
            manual_target_bin = int(sys.argv[i + 1])

    wf = rr.WAVEFORM_BEHAVIOR if use_behavior else rr.WAVEFORM_VITALSIGNS

    print(f"\n{'#' * 70}")
    print(f"#  Radar Data Inspector")
    print(f"#  会话目录: {session_dir}")
    print(f"#  波形: {'行为' if use_behavior else '妊娠'}")
    if manual_target_bin is not None:
        print(f"#  手动目标 bin: {manual_target_bin}")
    print(f"{'#' * 70}")

    # 主分析
    data = analyze_data(session_dir, wf, max_frames=max_frames,
                       manual_target_bin=manual_target_bin)

    # 保存中间数据
    npz_path = os.path.join(session_dir, "radar_inspector_data.npz")
    np.savez_compressed(
        npz_path,
        range_axis_m=data['range_axis_m'],
        range_profile_db=data['range_profile_db'],
        time_axis_s=data['time_axis_s'],
        displacement_mm=data['displacement_mm'],
        disp_bp_mm=data['disp_bp_mm'],
        slowtime_complex=data['slowtime_complex'],
        phase_rad=data['phase_rad'],
        rti_db=data['rti_db'],
        phase_rti=data['phase_rti'],
        breath_peaks=data['breaths']['peaks'],
        breath_intervals_s=data['breaths']['intervals_s'],
        target_bin=data['target_bin'],
        target_range_m=data['target_range_m'],
        fs_hz=data['fs_hz'],
    )
    print(f"\n✓ 数据已保存: {npz_path}")

    # 可视化
    if not no_plot:
        png_path = os.path.join(session_dir, "radar_inspector.png")
        plot_results(data, png_path)

    print("\n" + "=" * 70)
    print("  分析完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()

