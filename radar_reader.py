#!/usr/bin/env python3
"""妊娠/行为 raw-ADC bin 读取器：分片拼接 + 整帧对齐 + 立方体解析

解释器：C:\\Users\\34219\\AppData\\Local\\Programs\\Python\\Python39\\python.exe
（git bash 裸写 python 会落到 Anaconda base，那里 numpy 2.4.6 把 scipy 打坏了）

为什么需要这个模块 —— 两个静默陷阱，各自都会毁掉数据且不报错：

**陷阱 1：分片边界不落在帧边界上。**
CLI_Record 按 maxRecFileSize_MB=1024 切分，实际每片 1,073,741,760 B
（= 1024 MiB − 64，是 UDP 载荷 1456 的整数倍：737,460 × 1456）。
但妊娠每帧 131,072 B，1,073,741,760 / 131,072 = 8191.9995 **不整除**。
根因是 DCA1000 按 1456 B 连续推流、完全不管帧边界（131072/1456 = 90.022）。

于是每个文件边界都把一帧劈成两半，且错位量逐片递增 64 B：

    _Raw_0 末 → 第 8191 帧只写了 131,008 B，剩 64 B 在 _Raw_1 开头
    _Raw_1 末 → 第 16383 帧缺 128 B，在 _Raw_2 开头
    _Raw_2 末 → 第 24575 帧缺 192 B，在 _Raw_3 开头

**按文件分别解析会从第一个边界起整体错位，之后所有帧的相位都是垃圾，
而且不报错。** 7 个分片的采集会中招 6 次。所以必须拼成一条连续流再切帧。

**陷阱 2：末尾总有几百字节不足一帧。**
实测 128 B（3000 帧行为、18000 帧妊娠）、384 B（54000 帧妊娠）。
不是丢包 —— L1/L2 判据精确为零，说明字节全部到达主机。
真相是 DCA1000 发完最后一个 1456 B 包时，末帧只凑到 130,688 B
（54000 帧那次），还差 384 B，而雷达已经停了，**那些字节从不存在**。
所以按 floor(总字节 / 每帧字节) 取整帧即可，天然丢掉尾巴。
代价是丢最后 1 帧：54000 帧里的 1 帧 = 0.0019%。

L3 逐字节判据通过是这两条的安全保证：它证明截断只在尾部、中间无空洞。
若中间少 128 B，后续数据会整体错位、L3 会大面积失败而不是通过。

bin 的解析布局（2026-08-06 实测坐实，见 memory vitalsigns-bin-layout-verified）：

    cube = raw.reshape(nframes, 32, 4, 256, 2)   # frame, chirp, RX, sample, IQ
    z = cube[...,0] - 1j*cube[...,1]             # 注意是减号

三条依据：RX 非交织（用 capture_meta.txt 里 check_quality.py 的 RX 幅度
做外部对照）、I/Q 逐样本交织（错配会在 bin S/2 出伪峰）、
**必须取共轭**（z=I+jQ 时目标能量全落负频，正负比 1:11.2）。
"""

import glob
import os
import re

import numpy as np

# 妊娠波形（cow_vitalsigns.cfg）。行为波形用 WAVEFORM_BEHAVIOR。
WAVEFORM_VITALSIGNS = dict(samples=256, rx=4, chirps=32, tx=1, period_ms=50)
WAVEFORM_BEHAVIOR = dict(samples=128, rx=4, chirps=120, tx=3, period_ms=100)


def frame_bytes(wf):
    """每帧字节 = samples × RX × 2(I/Q) × 2B × chirps × TX"""
    return wf["samples"] * wf["rx"] * 2 * 2 * wf["chirps"] * wf["tx"]


def find_bins(session_dir):
    """按 _Raw_<N>.bin 的数字排序，不能用字典序

    字典序在 N >= 10 时会把 _Raw_10 排到 _Raw_2 前面 —— 拼接顺序一错，
    整段数据从那里起全是垃圾，且不报错。当前最多 7 片还没触发，
    但 45 分钟以上的采集就会到两位数。
    """
    paths = glob.glob(os.path.join(session_dir, "*_Raw_*.bin"))
    if not paths:
        raise FileNotFoundError(f"{session_dir} 下没有 _Raw_*.bin")

    def idx(p):
        m = re.search(r"_Raw_(\d+)\.bin$", os.path.basename(p))
        if not m:
            raise ValueError(f"文件名不符合 _Raw_<N>.bin: {p}")
        return int(m.group(1))

    out = sorted(paths, key=idx)
    got = [idx(p) for p in out]
    if got != list(range(len(got))):
        raise ValueError(f"分片编号不连续: {got} —— 缺文件会导致静默错位")
    return out


def describe(session_dir, wf=None):
    """不读数据，只报布局与截断情况。写代码/排查时先看这个。"""
    wf = wf or WAVEFORM_VITALSIGNS
    fb = frame_bytes(wf)
    paths = find_bins(session_dir)
    sizes = [os.path.getsize(p) for p in paths]
    total = sum(sizes)
    nfr, tail = divmod(total, fb)

    print(f"分片数   : {len(paths)}")
    for p, s in zip(paths, sizes):
        print(f"  {os.path.basename(p):32s} {s:>15,} B")
    print(f"合计     : {total:,} B")
    print(f"每帧     : {fb:,} B")
    print(f"完整帧   : {nfr:,}")
    if tail:
        print(f"尾部残帧 : {tail:,} B（缺 {fb - tail:,} B，已丢弃，"
              f"占全段 {100.0 / (nfr + 1):.4f}%）")

    cum = 0
    straddle = 0
    for i, s in enumerate(sizes[:-1]):
        cum += s
        r = cum % fb
        if r:
            straddle += 1
            if straddle <= 3:
                print(f"  边界 {os.path.basename(paths[i])} 末: 第 {cum // fb} 帧"
                      f"被切开，剩 {fb - r:,} B 在下一片开头")
    if straddle:
        print(f"跨界帧   : {straddle} 处 —— 必须拼接读取（本模块已处理）")
    return dict(paths=paths, sizes=sizes, total=total, frames=nfr, tail=tail)


def load_frames(session_dir, wf=None, start=0, count=None):
    """读取 [start, start+count) 帧，返回复数立方体

    返回 shape (nframes, chirps, rx, samples) 的 complex128，
    已按 z = I − jQ 取共轭。

    跨分片透明处理：内部把所有 _Raw_N.bin 当一条连续字节流，
    按全局字节偏移定位，所以跨界帧能被正确拼回来。
    只读需要的部分，不把 7 GB 全载进内存。
    """
    wf = wf or WAVEFORM_VITALSIGNS
    fb = frame_bytes(wf)
    paths = find_bins(session_dir)
    sizes = [os.path.getsize(p) for p in paths]
    total_frames = sum(sizes) // fb

    if start < 0 or start >= total_frames:
        raise ValueError(f"start={start} 超出范围，共 {total_frames} 帧")
    if count is None:
        count = total_frames - start
    count = min(count, total_frames - start)

    raw = _read_span(paths, sizes, start * fb, count * fb)
    a = np.frombuffer(raw, dtype="<i2").reshape(
        count, wf["chirps"], wf["rx"], wf["samples"], 2).astype(np.float64)
    return a[..., 0] - 1j * a[..., 1]


def _read_span(paths, sizes, offset, length):
    """按全局字节偏移跨分片读取 —— 这里就是陷阱 1 的解法

    做法与 Pi 上 verify_pcap_bin.py 的 bin_read() 同构（那份已被
    L3 判据在 7 GB 数据上验证过），区别是这里支持任意起始偏移。
    """
    out = bytearray()
    remain = length
    pos = 0
    for p, sz in zip(paths, sizes):
        if remain <= 0:
            break
        if offset >= pos + sz:
            pos += sz
            continue
        local = max(0, offset - pos)
        take = min(sz - local, remain)
        with open(p, "rb") as f:
            f.seek(local)
            piece = f.read(take)
        if len(piece) != take:
            raise IOError(f"{p} 读取不足：要 {take} 得 {len(piece)}")
        out += piece
        remain -= take
        offset += take
        pos += sz
    if remain:
        raise IOError(f"读取不足，还差 {remain} B")
    return bytes(out)


def range_fft(z, window=True, remove_dc=True):
    """距离维 FFT，返回 shape (..., samples) 的复数谱

    remove_dc：去掉每个 chirp 自己的均值。这一步同时压掉 ADC 直流偏置
    和 TX-RX 直接泄漏的一部分，否则 bin 0 会盖住近距离目标。
    """
    if remove_dc:
        z = z - z.mean(axis=-1, keepdims=True)
    if window:
        z = z * np.hanning(z.shape[-1])
    return np.fft.fft(z, axis=-1)


def range_axis(wf=None):
    """距离轴（米）。只有前 samples/2 个 bin 有效（取共轭后目标在正频）。

    每 bin = c / (2B)，B = 有效带宽 = 采样窗 × 斜率。
    妊娠：采样窗 50 us（256/5120 ksps）× 60 MHz/us = 3.0 GHz → 0.049965 m
    """
    wf = wf or WAVEFORM_VITALSIGNS
    c = 299792458.0
    sample_rate_hz = 5120e3
    slope_hz_per_s = 60e6 / 1e-6
    b_hz = wf["samples"] / sample_rate_hz * slope_hz_per_s
    return np.arange(wf["samples"]) * c / (2 * b_hz)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        sys.exit("用法: radar_reader.py <session_dir> [--behavior]")
    w = WAVEFORM_BEHAVIOR if "--behavior" in sys.argv else WAVEFORM_VITALSIGNS
    describe(sys.argv[1], w)
