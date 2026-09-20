#!/usr/bin/env python3
"""对全部采集跑 explain_one，并汇总成一张总表。

为什么单独一个脚本而不是改 explain_one：
  explain_one 的职责是「让人看懂一条」，输出是给人读的图和说明。
  批量的职责是「看清 40 条的分布」，输出是给人筛的表。
  两件事混在一个脚本里，任何一边的改动都会牵动另一边。

输出（都在 batch_explain_results/）：
  汇总总表.csv          一行一条采集，含所有关键指标与结论
  按工况统计.csv        四种工况的可用率与相干度分布
  工况对比.png          相干度、移动量、呼吸偏差的分工况箱线图
"""
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import argparse
import traceback
from pathlib import Path

import numpy as np

from pipeline import plotting
plotting.setup()
import matplotlib.pyplot as plt

import vsp_core
import explain_one as E

C = plotting.COLORS
ROOT = Path(__file__).parent / "data" / "Batch_1_Experiments_Marked"
OUT = Path(__file__).parent / "batch_explain_results"


def read_flags(cap):
    """读回该采集的 08_质量红旗.csv，返回 {检查项: (结果, 实测)}。

    从文件读而不是让 explain() 返回：这样即使某条是上一轮跑的，
    也能汇总进来，不必强制全部重跑。
    """
    p = cap / "explain" / "08_质量红旗.csv"
    if not p.exists():
        return {}
    d = {}
    for line in p.read_text(encoding="utf-8-sig").splitlines()[1:]:
        f = line.split(",")
        if len(f) >= 3:
            d[f[0]] = (f[1], f[2])
    return d


def selected_bin(cap):
    p = cap / "explain" / "04_候选bin.csv"
    if not p.exists():
        return None
    for line in p.read_text(encoding="utf-8-sig").splitlines()[1:]:
        f = line.split(",")
        if len(f) >= 7 and f[6].strip() == "是":
            return int(f[0])
    return None


def num(s):
    """从「+15.1 dB」「120 mm」「0.977」这类实测字段里抠出数字。"""
    if s is None:
        return np.nan
    t = ""
    for ch in s:
        if ch.isdigit() or ch in "+-.":
            t += ch
        elif t:
            break
    try:
        return float(t)
    except ValueError:
        return np.nan


def main():
    ap = argparse.ArgumentParser(description="批量跑 explain_one 并汇总")
    ap.add_argument("--skip-existing", action="store_true",
                    help="已有 explain/08_质量红旗.csv 的跳过，只做汇总")
    a = ap.parse_args()

    OUT.mkdir(exist_ok=True)
    caps = sorted(d for d in ROOT.iterdir() if d.is_dir())
    print(f"共 {len(caps)} 个采集目录\n")

    rows, failed = [], []
    for i, cap in enumerate(caps, 1):
        meta = E.read_meta(cap)
        tag = f"[{i}/{len(caps)}] {cap.name[-17:]}"
        if meta is None:
            print(f"{tag}  无 data_info.csv，跳过")
            continue

        done = (cap / "explain" / "08_质量红旗.csv").exists()
        if not (a.skip_existing and done):
            try:
                E.explain(cap)
            except Exception:
                print(f"{tag}  失败")
                traceback.print_exc()
                failed.append(cap.name)
                continue

        fl = read_flags(cap)
        b = selected_bin(cap)
        coh = num(fl.get("相位相干度（总闸）", (None, None))[1])
        ratio = num(fl.get("相干时间占比", (None, None))[1])
        move = num(fl.get("目标移动量（幅度重心）", (None, None))[1])
        ampdb = num(fl.get("目标相对平均回波", (None, None))[1])
        verdict = fl.get("总体结论", ("", ""))[0]

        # 呼吸相关：憋气与自然呼吸的字段名不同，分别取
        err = num(fl.get("呼吸率对自报真值", (None, None))[1])
        det = num(fl.get("检出次数对自报", (None, None))[1])
        # 字段名从「憋气自检-*」改成「憋气记录-*」，因为这三项已从判据
        # 降级为提示：受试者确认 lsw 两条确实在憋气，但呼吸带主峰有
        # 1.07/2.28 mm，说明「憋气→应平坦」这个前提不成立，不能拿来判失败。
        #
        # 必须先看字段在不在，不能直接 all(...== "通过")：
        # 相干度不过闸的记录走的是另一个分支，压根没生成憋气三项，
        # fl.get() 全部落空 → all() 得 False → 汇报成「有起伏」，
        # 而真相是「没算」。实测那 5 条 γ<0.3 的憋气记录全中此坑。
        HOLD_KEYS = ("憋气记录-主峰幅度", "憋气记录-幅度判定", "憋气记录-检出次数")
        hold_pk = num(fl.get(HOLD_KEYS[0], (None, None))[1])
        if not meta["breath_hold"] or not all(k in fl for k in HOLD_KEYS):
            hold_quiet = None            # 非憋气记录，或相干度没过闸没算
        else:
            hold_quiet = all(fl[k][0] == "通过" for k in HOLD_KEYS)

        rows.append(dict(
            采集=cap.name[-17:], 受试者=meta["subject"], 工况=meta["mode"],
            工况名=E.WORK_MODE_NAMES.get(meta["mode"], "").split("（")[0],
            憋气="是" if meta["breath_hold"] else "",
            手环心率=meta["hr_band"], 自报呼吸=meta["breath_count"],
            选定bin=b, 距离m=round(b * vsp_core.M_PER_BIN, 3) if b else None,
            相干度=coh, 相干占比=ratio, 移动量mm=move, 目标dB=ampdb,
            呼吸偏差bpm=err, 检出次数=det,
            憋气主峰mm=hold_pk if meta["breath_hold"] else None,
            # 三态：安静 / 有起伏 / 未算（相干度没过闸）。空值表示非憋气记录。
            憋气呼吸带=("" if hold_quiet is None and not meta["breath_hold"]
                        else "未算" if hold_quiet is None
                        else "安静" if hold_quiet else "有起伏"),
            结论=verdict))
        print(f"{tag}  工况{meta['mode']} bin{b}　"
              f"相干{coh:.3f}　{verdict}")

    if not rows:
        print("没有可汇总的数据")
        return

    # ---- 汇总总表 ----
    cols = list(rows[0].keys())
    E.write_csv(OUT / "汇总总表.csv", cols,
                [[r[c] for c in cols] for r in rows])
    print(f"\n汇总总表：{OUT / '汇总总表.csv'}")

    # 工况名取到括号前：WORK_MODE_NAMES 是「双静止（雷达不动 + 人不动）」，
    # 直接切前 4 字会切出「双静止（」这种带半个括号的标签。
    short = {m: E.WORK_MODE_NAMES[m].split("（")[0] for m in (1, 2, 3, 4)}

    # ---- 按工况统计 ----
    stat = []
    for m in (1, 2, 3, 4):
        g = [r for r in rows if r["工况"] == m]
        if not g:
            continue
        coh = np.array([r["相干度"] for r in g], float)
        mv = np.array([r["移动量mm"] for r in g], float)
        usable = sum(1 for r in g if r["结论"] != "不可用")
        stat.append([
            m, short[m], len(g),
            f"{usable}/{len(g)}",
            f"{np.nanmean(coh):.3f} ± {np.nanstd(coh):.3f}",
            f"{np.nanmin(coh):.3f} ~ {np.nanmax(coh):.3f}",
            int((coh >= E.MIN_COHERENCE).sum()),
            f"{np.nanmean(mv):.0f} ± {np.nanstd(mv):.0f}",
        ])
    E.write_csv(OUT / "按工况统计.csv",
                ["工况", "工况名", "采集数", "非不可用", "相干度均值",
                 "相干度范围", f"相干度≥{E.MIN_COHERENCE}条数", "移动量mm"],
                stat)
    print(f"按工况统计：{OUT / '按工况统计.csv'}")
    print()
    hdr = ["工况", "工况名", "数", "非不可用", "相干度均值",
           "相干度范围", f"≥{E.MIN_COHERENCE}", "移动量mm"]
    w = [4, 6, 4, 10, 17, 17, 6, 12]
    print("".join(f"{h:<{x}}" for h, x in zip(hdr, w)))
    for s in stat:
        print("".join(f"{str(v):<{x}}" for v, x in zip(s, w)))

    # ---- 分工况箱线图 ----
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6))
    names = [short[m] for m in (1, 2, 3, 4)
             if any(r["工况"] == m for r in rows)]
    modes = [m for m in (1, 2, 3, 4) if any(r["工况"] == m for r in rows)]

    def by_mode(key):
        return [[r[key] for r in rows if r["工况"] == m and
                 r[key] is not None and not np.isnan(float(r[key]))]
                for m in modes]

    for ax, key, title, ylab in [
            (axes[0], "相干度", "相位相干度（总闸）", "相干度"),
            (axes[1], "移动量mm", "目标移动量（幅度重心）", "移动量 (mm)"),
            (axes[2], "呼吸偏差bpm", "呼吸率对自报参考的偏差", "偏差 (bpm)")]:
        data = by_mode(key)
        keep = [(d, n) for d, n in zip(data, names) if d]
        if not keep:
            ax.set_visible(False)
            continue
        bp = ax.boxplot([d for d, _ in keep], labels=[n for _, n in keep],
                        patch_artist=True, medianprops=dict(color=C["heart"]))
        for p in bp["boxes"]:
            p.set_facecolor("#dce7f3")
        # 散点叠在箱线上：每组只有 8-10 条，箱线图本身信息太少
        for j, (d, _) in enumerate(keep, 1):
            ax.plot(np.full(len(d), j) + np.random.uniform(-.08, .08, len(d)),
                    d, "o", ms=4, color=C["signal"], alpha=.6)
        ax.set_title(title)
        ax.set_ylabel(ylab)

    axes[0].axhline(E.MIN_COHERENCE, color=C["heart"], ls="--", lw=1)
    axes[0].axhline(E.GOOD_COHERENCE, color=C["breath"], ls="--", lw=1)
    plotting.note(axes[0], f"红线 {E.MIN_COHERENCE} 可用下限\n"
                           f"绿线 {E.GOOD_COHERENCE} 可信线", loc="center left")
    axes[1].axhline(E.MOVE_LARGE_MM, color=C["heart"], ls="--", lw=1)
    axes[2].axhline(0, color="#666", lw=.8)
    for y in (-4, 4):
        axes[2].axhline(y, color=C["heart"], ls="--", lw=1)

    fig.suptitle("四工况对比：相位质量、目标移动、呼吸率偏差", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "工况对比.png")
    plt.close(fig)
    print(f"\n工况对比图：{OUT / '工况对比.png'}")

    if failed:
        print(f"\n失败 {len(failed)} 条：{failed}")


if __name__ == "__main__":
    main()
