"""妊娠 bin → 慢时间复数矩阵。所有物理尺度集中在此，不散落到分析脚本里。

布局依据：memory `vitalsigns-bin-layout-verified`（已实测坐实）
    raw.reshape(-1, 32, 4, 256, 2)   frame, chirp, RX, sample, IQ
    z = I - 1j*Q                      ← 必须取共轭
"""
import os
import numpy as np

# ---- 波形参数（来自 cow_vitalsigns.cfg，见 NEW_SESSION_PROMPT 的参数表）----
S, RX, CH = 256, 4, 32                 # samples / rx / chirps per frame
FRAME_I16 = S * RX * 2 * CH            # 65536 个 int16 = 131072 B
FS = 20.0                              # 慢时间采样率 Hz = 1/50ms
C = 299_792_458.0
B_HZ = 3.0e9                           # 有效带宽 = 50us x 60MHz/us
F_CENTER = 61.86e9                     # 采样带中心频率
LAMBDA_MM = C / F_CENTER * 1000.0      # 4.8463 mm
MM_PER_RAD = LAMBDA_MM / (4 * np.pi)   # 0.38567 mm/rad
M_PER_BIN = C / (2 * B_HZ)             # 0.049965 m/bin
NBIN = S // 2                          # 只用正频 128 个


def frame_count(path):
    sz = os.path.getsize(path)
    assert sz % (FRAME_I16 * 2) == 0, f"{sz} 不是 131072 的整数倍"
    return sz // (FRAME_I16 * 2)


def build_slowtime(path, cache=None, block=200, verbose=True):
    """→ X[frame, rx, bin] 复数。每帧内 32 chirp 相干求和（= 取零多普勒）。

    每步的理由：
      减样本均值  去 ADC 直流与 TX-RX 泄漏的直流分量
      Hann 窗     压距离维旁瓣，防 0.1 m 的强泄漏泄进目标 bin
      32 chirp 求和  DFT 零频即求和；2.464 ms 内呼吸相位漂移 <0.15 rad 可忽略，
                     换来 sqrt(32)=7.5 dB SNR（推算，非实测）
    """
    if cache and os.path.exists(cache):
        if verbose:
            print(f"[cache] 复用 {cache}")
        return np.load(cache)

    nfr = frame_count(path)
    out = np.empty((nfr, RX, NBIN), np.complex64)
    win = np.hanning(S).astype(np.float32)
    mm = np.memmap(path, dtype="<i2", mode="r")

    for s in range(0, nfr, block):
        e = min(s + block, nfr)
        a = np.asarray(mm[s * FRAME_I16:e * FRAME_I16],
                       dtype=np.float32).reshape(-1, CH, RX, S, 2)
        z = np.empty(a.shape[:-1], np.complex64)
        z.real = a[..., 0]
        z.imag = -a[..., 1]                      # 取共轭
        z -= z.mean(axis=-1, keepdims=True)
        sp = np.fft.fft(z * win, axis=-1)[..., :NBIN]
        out[s:e] = sp.sum(axis=1)                # chirp 相干平均
        if verbose and (s // block) % 5 == 0:
            print(f"\r  距离FFT {e}/{nfr} 帧", end="", flush=True)

    del mm
    if verbose:
        print(f"\r  距离FFT {nfr}/{nfr} 帧  完成")
    if cache:
        np.save(cache, out)
        if verbose:
            print(f"[cache] 已存 {cache}")
    return out


def bin_to_m(k):
    return k * M_PER_BIN


def phase_mm(series):
    """复数慢时间序列 → 位移 mm（已去线性趋势）。"""
    ph = np.unwrap(np.angle(series))
    return (ph - ph.mean()) * MM_PER_RAD
