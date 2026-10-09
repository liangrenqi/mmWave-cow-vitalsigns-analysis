# mmWave-cow-vitalsigns-analysis

IWR6843 毫米波雷达生命体征的离线分析：raw ADC → 慢时间相位 → 呼吸 / 心跳，
以及 Polar H10 心电带作为心跳真值的解析、R 峰检测与对齐验证。

采集端（Pi 5 + DCA1000 + H10）在另一个仓库：
[mmWave-cow-capture-Raspberrypi](https://github.com/liangrenqi/mmWave-cow-capture-Raspberrypi)。
本仓库只读采集产物，不改原始数据。

最终目标是奶牛早期妊娠（30–60 天）判别。目前全部数据是**人体与角反射器**，
作用是打磨方法、量化测量能力，**不产生任何妊娠结论**。

## 工作方式：判据测前写定

每一轮实验都先写判据、再采集或分析，判据文件写定后不改。
不通过就改代码或改下一轮的写定文件，不回头放宽。
所以仓库里成对出现 `*_测前写定.md` 与 `*_结果.md`，前者是后者的凭证。
事后探查脚本（`*_posthoc.py`、`*_diag.py`）只用来解释原因，不改判定。

## 已有结论

| 项 | 状态 | 依据 |
|---|---|---|
| bin 布局 | 已坐实：`(帧, 32 chirp, 4 RX, 256 样本, IQ)`，**必须取共轭 z = I − jQ** | `vsp_core.py` |
| 分片劈帧 | 已坐实：CLI 按 1456 B 推流，分片边界不落在帧边界，读取必须拼接 | `radar_reader.py` |
| ADC 内容正确性 | 已闭环：5 min 盲测六次憋气全中，起点误差均值 0.58 s | 2026-08 |
| 数据能否用的总闸 | 滞后一帧复相干度 γ；人动工况 γ 与噪声本底同级，整条不可用 | `explain_one.py` |
| 30 s 心率提取 | **负结果**：10 个算法、6 个闸判据都失败，严格计仅 4/12 | 批次 2 |
| 雷达噪声本底 | 比人体心跳带内容低约 60 dB，排除"雷达 SNR 不够" | `诊断输出/实验0_判定汇总.md` |
| 距离偏置 | 测得 = 0.9948 × 卷尺 + 0.144 m，系统偏置，只影响绝对距离 | 实验 0 |
| H10 并入采集 | V1 → V2 → V2-R → V3 全过（2026-10-09）；判据 3（RR 与 ECG R 峰对齐）三段全过 | `诊断输出/H10方案验证_*` |

下一步是实验 1（憋气 + H10 真值），用来区分心跳带里的东西是呼吸谐波还是其它体动。
设计见 [下一轮实验设计.md](下一轮实验设计.md)。

## 脚本

**雷达：ADC 到慢时间**

| 文件 | 用途 |
|---|---|
| `vsp_core.py` | 妊娠 bin → 慢时间复数矩阵，所有物理尺度集中在此（唯一的 ADC 解析实现） |
| `radar_reader.py` | bin 读取器：跨分片拼接 + 整帧对齐 + 立方体解析 |
| `radar_inspector.py` | 单条链路自检 L1–L7，含 RX 四通道功率对比 |
| `batch_run.py` | `radar_inspector` 的批量版 |
| `explain_one.py` | 单条采集拆成 8 步，每步出 CSV + 中文图 + 判读说明 |
| `explain_one_new.py` | `explain_one.py` 的试验改版（RTI 只画到 1.5 m、绝对 dB、加一维距离剖面） |
| `batch_explain.py` | 对全部采集跑 explain_one，汇总成总表与分工况统计 |
| `exp0_reflector.py` | 实验 0 角反射器分析，按 `实验0判据_分析前写定.md` 执行 |
| `pipeline/plotting.py` | 统一绘图设置（中文字体、配色） |

**心率带 H10**

| 文件 | 用途 |
|---|---|
| `h10_parse.py` | 解析 Pi 上 `h10_logger.py` 的原始日志（HR / ECG / ACC），按第一步判据验收 |
| `h10_export.py` | 原始日志转成与手机 Polar Equine 导出同格式的 txt |
| `h10_rpeak.py` | ECG R 峰检测（neurokit2 + 极性门 D1/D2），出判据 3 / 5 判定 |
| `h10_rr_align_ab.py` | 判据 3 对齐：合并方案 AB（粗定位 + 逐通知 Viterbi + 区分力检验） |
| `h10_lag_measure.py` | 实测 HR 通知的截止滞后，给合成数据用 |
| `h10_v2_check.py` | V2 / V2 重做 / V3 判定：雷达与 H10 并行互不干扰 |
| `h10_start_latency.py` | PMD 启动延迟（启动回应 → 首个数据帧） |
| `h10_btsnoop_timeline.py` | btmon 抓包 → 逐包时间线，定位 30 s 启动延迟 |
| `h10_rr_align.py` | 判据 3 的 A / B 两方案比较（已被合并方案 AB 取代，保留作凭证） |
| `h10_rr_posthoc.py`、`h10_rr_align_posthoc.py`、`h10_v2_seg2_diag.py` | 事后探查，不改判定 |
| `h10_export_check.py`、`h10_export_start_gap.py` | 手机导出数据的核对 |

## 目录

```
*.py                    分析脚本（见上表）
pipeline/               公共模块
*_测前写定.md            顶层的判据文件
下一轮实验设计.md         实验 0–5 的设计、判据与批次进度
NEW_SESSION_PROMPT.md   参数表与 bin 解析方式的速查
诊断输出/                每轮的判据、结果 md，以及结果引用的 csv / png
data/                   每条采集的 data_info.csv（人工标注）与 capture_meta.txt（七项判据与波形参数）
```

## 数据不在仓库里

- 雷达原始 `.bin` / `.pcap` 约 21 GB，不入库。重跑雷达脚本需要把采集目录放回 `data/` 下原位置。
- H10 原始日志、手机导出、`logs/` 下的现场拷贝也不入库。H10 脚本的输入路径见各文件头的用法说明。
- 派生的 `.npy` / `.npz`、`batch_explain_results/` 可由原始数据重算，不入库。

`data_info.csv` 是一行、空白分隔的位置字段：

```
受试者  工况  心率bpm  呼吸次数  板  脉搏次数  [距离m]  [备注]
```

未记录的项填 −1，不要留空。**呼吸次数填 0 表示憋气**，所以"未记录"必须填 −1。
工况 1 双静止 / 2 人动 / 3 雷达手持 / 4 双动 / 9 角反射器（受试者位写 `REFL`）。

| 批次 | 条数 | 内容 |
|---|---|---|
| 1 | 40 | 人体，工况 1–4 |
| 2 | 12 | 人体，亚克力板对照，含人工脉搏真值（呼吸列全 −1） |
| 3 | 23 | 角反射器（实验 0） |

## 环境

Windows 上用 Python 3.9：

```
Python      3.9.2
numpy       1.26.1
scipy       1.13.1
matplotlib  3.9.4
neurokit2   0.2.12   # 只有 h10_rpeak.py 用；版本固定，换版本须重跑判据
```

中文图依赖本机的 Microsoft YaHei / SimHei 字体。

```bash
python explain_one.py data/Batch_1_Experiments_Marked/<采集目录>
python explain_one.py <采集目录> --target-bin 16        # 手动指定目标 bin
python h10_rpeak.py --selftest
python h10_rpeak.py <h10_xxx.log>                      # 判定模式
python h10_v2_check.py --redo <段目录…>                 # 会覆盖 诊断输出/H10方案验证_V2重做结果.md
```

## 波形参数（生命体征）

| 量 | 值 |
|---|---|
| 有效带宽 / 距离分辨率 | 3.0 GHz / 0.04997 m 每 bin |
| 采样带中心 / λ | 61.86 GHz / 4.8463 mm |
| 位移 / 相位 | 0.3857 mm/rad |
| 帧周期 / 慢时间采样率 | 50 ms / 20 Hz |
| 每帧 | 1 TX × 4 RX × 32 chirp × 256 样本 = 131,072 B |

推导与 cfg 原文见 [NEW_SESSION_PROMPT.md](NEW_SESSION_PROMPT.md)。
