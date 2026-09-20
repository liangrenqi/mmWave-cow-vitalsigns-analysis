"""统一绘图设置：中文字体、配色、样式。

为什么需要这个模块：此前的图全是英文，或者中文变成方框乱码，
导致图只有写代码的人看得懂。本机已确认存在 msyh.ttc / simhei.ttf，
所以中文完全可用，不需要退回英文。

用法：
    from pipeline import plotting
    plotting.setup()      # 在任何 plt 调用之前调用一次
"""
import matplotlib
matplotlib.use("Agg")            # 无界面后端，脚本里不弹窗
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 本机实测存在的中文字体，按优先级排列
_CJK_CANDIDATES = [
    "Microsoft YaHei",   # msyh.ttc  微软雅黑，正文最清晰
    "SimHei",            # simhei.ttf 黑体，兜底
    "DengXian",          # Deng.ttf  等线
    "SimSun",            # simsun.ttc 宋体
]

# 统一配色。语义固定，跨图一致，看图不用重新记图例。
COLORS = {
    "raw":      "#8894a8",   # 原始信号，灰蓝，退到背景
    "signal":   "#1f6fb4",   # 主信号，蓝
    "breath":   "#2e8b57",   # 呼吸，绿
    "heart":    "#c1440e",   # 心跳，橙红
    "target":   "#c1440e",   # 目标标记，橙红
    "clutter":  "#8894a8",   # 杂波/干扰，灰
    "band":     "#2e8b57",   # 目标区间底色，绿
    "peak":     "#c1440e",   # 峰
    "trough":   "#1f6fb4",   # 谷
    "warn":     "#b8860b",   # 警告，暗金
}


def available_cjk_font():
    """返回本机实际可用的第一个中文字体名；都没有则返回 None。"""
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in _CJK_CANDIDATES:
        if name in installed:
            return name
    return None


def setup():
    """设置全局样式。返回实际使用的中文字体名（None 表示没找到）。"""
    font = available_cjk_font()
    if font:
        plt.rcParams["font.sans-serif"] = [font] + _CJK_CANDIDATES
    plt.rcParams["axes.unicode_minus"] = False   # 负号不用 U+2212，否则显示成方框

    plt.rcParams["figure.dpi"] = 110
    plt.rcParams["savefig.dpi"] = 150
    plt.rcParams["savefig.bbox"] = "tight"
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.titlesize"] = 12
    plt.rcParams["axes.labelsize"] = 10
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.alpha"] = 0.3
    plt.rcParams["grid.linestyle"] = "--"
    plt.rcParams["legend.framealpha"] = 0.9
    plt.rcParams["axes.axisbelow"] = True        # 网格压在数据下面
    return font


def note(ax, text, loc="upper right"):
    """在图上角贴一段中文判读提示。让图自带说明，不依赖外部文档。"""
    xy = {"upper right": (0.98, 0.97), "upper left": (0.02, 0.97),
          "lower right": (0.98, 0.03), "lower left": (0.02, 0.03),
          "center right": (0.98, 0.5), "center left": (0.02, 0.5)}[loc]
    ha = "right" if "right" in loc else "left"
    va = "top" if "upper" in loc else ("bottom" if "lower" in loc else "center")
    ax.text(xy[0], xy[1], text, transform=ax.transAxes,
            ha=ha, va=va, fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#fffbe6",
                      edgecolor="#d4c68a", alpha=0.92))
