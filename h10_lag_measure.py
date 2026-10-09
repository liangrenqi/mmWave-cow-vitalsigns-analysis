"""实测 H10 HR 通知的「截止滞后」—— 给合并方案 AB 的合成数据用（设计阶段的测量，不判定任何东西）

模型：通知 i 在 Pi 时刻 a_i 到达，装入「Pi 时钟上 ≤ 截止点 c_i 的心跳」，c_i = a_i − d_i，
d_i = d0 + s·t_i + j_i（j_i 为逐条浮动）。
c_i 看不见，只知道它落在 [本条最后一拍的结束峰, 下一个峰) 之间 —— 所以 j_i 只知道一个区间（区间删失）。
直接拿区间中点当 j_i 会把「一拍宽的量化」也算成浮动，约多出 ±RR/2，故用区间删失极大似然估 d0、s、σ_j。

参照配对：方案 B 在真实记录上 |差| ≤ 16 ms 的配对（与 h10_rr_align_posthoc.py 同）。
输出：诊断输出/H10_通知滞后实测.md、H10_通知滞后实测.csv（每条通知的区间，供合成数据重采样）
"""
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from h10_rr_align import OUT, REAL, REAL_NAME, align_B, load_real  # noqa: E402


def intervals(R):
    """每条通知的滞后区间 (lo, hi]：d ∈ (a − T_next, a − T_end]。返回 t(s)、lo、hi、到达间隔"""
    n, T = R["notes"], R["T"]
    rb = align_B(n["rr"], R["iv"])
    ok = np.abs(rb["dd"]) <= 16
    h, e = rb["h"][ok], rb["e"][ok]
    last = n["m"][h] == 0
    ni, el = n["ni"][h[last]], e[last]
    m = el + 2 < len(T)
    ni, el = ni[m], el[m]
    a = n["a"][ni]
    hi = a - T[el + 1]          # 结束峰（iv[e] 介于 T[e] 与 T[e+1]）
    lo = a - T[el + 2]          # 下一个峰
    t = (a - n["a"][0]) / 1000.0
    return t, lo, hi, np.diff(n["a"])


def fit(t, lo, hi):
    """区间删失正态：max Σ log[Φ((hi−μ)/σ) − Φ((lo−μ)/σ)]，μ = d0 + s·t"""
    def nll(x):
        d0, s, ls = x
        mu, sg = d0 + s * t, np.exp(ls)
        p = norm.cdf((hi - mu) / sg) - norm.cdf((lo - mu) / sg)
        return -np.sum(np.log(np.maximum(p, 1e-300)))
    c = np.polyfit(t, (lo + hi) / 2, 1)
    best = None
    for ls0 in np.log([20, 60, 150, 300]):
        r = minimize(nll, [c[1], c[0], ls0], method="Nelder-Mead",
                     options=dict(xatol=0.1, fatol=1e-4, maxiter=4000))
        if best is None or r.fun < best.fun:
            best = r
    d0, s, ls = best.x
    return d0, s, float(np.exp(ls)), best.fun


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    L = ["# H10 HR 通知截止滞后实测（设计阶段测量，供合并方案 AB 的合成数据）\n",
         "模型与方法见 `h10_lag_measure.py` 文件头。σ_j 是**去掉一拍量化之后**的逐条浮动；",
         "「区间外」= 拟合直线落在该通知区间外超过 3σ_j 的条数（离群）。\n",
         "| 记录 | 通知数 | d0（t=0） | 漂移 s | σ_j | 区间中点去趋势 5–95 分位 | 离群 >3σ | 到达间隔 5–95 分位 |",
         "|---|---|---|---|---|---|---|---|"]
    rows = []
    for s in REAL:
        R = load_real(s)
        t, lo, hi, da = intervals(R)
        d0, sl, sg, _ = fit(t, lo, hi)
        mu = d0 + sl * t
        out = np.sum((lo - mu > 3 * sg) | (mu - hi > 3 * sg))
        mid = (lo + hi) / 2 - mu
        L.append(f"| {REAL_NAME[s]} | {len(t)} | {d0:.0f} ms | {sl * 60:+.1f} ms/min | {sg:.0f} ms | "
                 f"{np.percentile(mid, 5):+.0f}…{np.percentile(mid, 95):+.0f} ms | {out} | "
                 f"{np.percentile(da, 5):.0f}–{np.percentile(da, 95):.0f} ms |")
        for k in range(len(t)):
            rows.append((REAL_NAME[s], t[k], lo[k] - mu[k], hi[k] - mu[k]))
        print(REAL_NAME[s], "完成", flush=True)
    with open(OUT / "H10_通知滞后实测.csv", "w", encoding="utf-8-sig") as f:
        f.write("记录,t_s,区间下界_去趋势_ms,区间上界_去趋势_ms\n")
        for r in rows:
            f.write(f"{r[0]},{r[1]:.3f},{r[2]:.1f},{r[3]:.1f}\n")
    L.append("\n注：d0 依赖 R 峰换到 Pi 时钟所用的下包络偏移，绝对值只在同一换算下有意义；"
             "合成数据只用 σ_j、漂移量级与到达间隔分布。")
    (OUT / "H10_通知滞后实测.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
