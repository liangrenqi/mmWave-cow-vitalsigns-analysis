"""事后查证（看过 `H10_判据3对齐_两方案比较结果.md` 之后写，不改任何判定）：
方案 A 的核心假定「每条 HR 通知的截止滞后 p 是全程常数」在真实 H10 上成立吗？

做法：取方案 B 在真实记录上 |差| ≤ 16 ms 的配对当作参照（B 在真实记录上 95–100% ≤ 16 ms），
对每条通知求它最后一个 RR 所隐含的滞后区间 [到达 − 下一峰, 到达 − 结束峰)。
若存在常数（或常数 + 线性漂移）p，所有区间应有公共交集。
输出：诊断输出/H10_判据3对齐_方案A假定事后查证.md
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from h10_rr_align import OUT, REAL, REAL_NAME, align_B, load_real  # noqa: E402


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    L = ["# 方案 A 假定的事后查证（看过比较结果后写，不改判定）\n",
         "参照配对取方案 B 在真实记录上 |差| ≤ 16 ms 的那些；每条通知的最后一个 RR 给出一个滞后区间"
         "[到达 − 下一个 R 峰, 到达 − 结束 R 峰)。常数 p 存在 ⇔ 所有区间有公共交集。\n",
         "| 记录 | 通知数 | 区间下界最大 | 区间上界最小 | 去线性趋势后区间中点 5–95 分位 | 去趋势后公共交集 |",
         "|---|---|---|---|---|---|"]
    for s in REAL:
        R = load_real(s)
        n, T = R["notes"], R["T"]
        rb = align_B(n["rr"], R["iv"])
        ok = np.abs(rb["dd"]) <= 16
        h, e = rb["h"][ok], rb["e"][ok]
        last = n["m"][h] == 0
        ni, el = n["ni"][h[last]], e[last]
        m = el + 2 < len(T)
        a = n["a"][ni[m]]
        up, lo = a - T[el[m] + 1], a - T[el[m] + 2]
        t = (a - a[0]) / 1000
        c = np.polyfit(t, (up + lo) / 2, 1)
        tr = np.polyval(c, t)
        mid = (up + lo) / 2 - tr
        exist = (lo - tr).max() < (up - tr).min()
        L.append(f"| {REAL_NAME[s]} | {len(a)} | {lo.max():.0f} ms | {up.min():.0f} ms | "
                 f"{np.percentile(mid,5):+.0f}…{np.percentile(mid,95):+.0f} ms | {'有' if exist else '**无**'} |")
    L.append("\n若四份都「无」：真实 H10 的通知截止滞后逐条浮动，不是常数，方案 A 的模型不成立；"
             "合成数据按常数 p（σ 15 ms）生成，因此对 A 偏乐观——这正是写定文件末节预先提示的风险。")
    (OUT / "H10_判据3对齐_方案A假定事后查证.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
