# 新会话提示词（复制以下全部内容作为新对话的第一条消息）

---

继续毫米波雷达项目，新阶段：**用人体呼吸心跳数据验证 ADC 内容的正确性**。
硬件 IWR6843-ISK + MMWAVEICBOOST + DCA1000EVM + 树莓派 5。

## 先读这些（顺序别换）

1. **`C:\Users\34219\.claude\projects\F--Codes-CCS-LuaBinDataCapture\memory\MEMORY.md`
   及其索引的全部条目** —— 最权威的信息源。**注意这是旧项目目录下的 memory 路径，
   新项目要显式去那里读**，否则会丢掉全部上下文。
   里面含完整决策依据、已解决/未解决清单、TI 源码的几个已修缺陷，
   以及**多条对旧结论的更正**（哪些记错了、为什么）。
   与本阶段最相关的六条：
   - `vitalsigns-bin-layout-verified` —— bin 怎么解析，**已实测坐实，直接用**
   - `bin-tail-and-segment-straddle` —— **分片边界会劈开帧**，读取必须拼接
   - `hpf-corner-close-range-risk` —— HPF 拐点，决定了实验站位
   - `windows-python-interpreters` —— 必须用哪个 Python，别踩坏掉的那个
   - `capture-verdict-system` —— 七项判据体系（验链路完整性，**不验内容**）
   - `wireless-cfg-json-mapping` —— 波形参数与改时长的正确改法
2. **GitHub** https://github.com/liangrenqi/mmWave-cow-capture-Raspberrypi
   —— Pi 上全部代码与五份文档。"怎么用"看这里。Pi 工作副本 `~/mmwave-cow-capture`。
3. 旧项目目录 `F:\Codes\CCS\LuaBinDataCapture\`：第一阶段 Lua、波形设计文档、
   `refer/`（TI 官方文档转 txt，可 grep）。本机 TI SDK
   `D:\Ti\mmWaveSDK\mmwave_sdk_03_06_02_00-LTS\` —— **有些结论只有 SDK 源码/头文件
   里查得到，refer/ 没有**（如片上 L3 容量、HPF 拐点枚举）。
4. `F:\Codes\CCS\LuaBinDataCapture\vitalsigns_analysis\` —— 本阶段已有的东西：
   - **`radar_reader.py` —— bin 读取器，已写好并验证过，直接用，不要重写。**
     提供 `describe()` / `load_frames()` / `range_fft()` / `range_axis()`，
     内部已处理跨分片拼接与整帧对齐（这两件事都是静默陷阱，见下）。
   - `radar_inspector.py` —— 单条链路自检 L1-L7，含 RX 四通道功率对比
     （explain_one 只用 RX0，通道静默故障只有这里测得出）。
     `batch_run.py` 是它的批量版。
   - `vsp_core.py` / `explain_one.py` / `batch_explain.py` —— 09-14 之后的
     正式流程：ADC→慢时间、单条 8 步解释、批量汇总。
   - **已于 2026-09-14 删除**的探索脚本：`_test_reader.py`、`_verify_layout.py`、
     `_verify_axis.py`（布局与读取验证，结论已进 memory 并坐实）、
     `quicklook/refine/diag3/blind/score.py`（8 月单条摸索）、
     `batch_analysis.py`、`improved_peak_selection.py`、`diagnose_peak.py`
     及其批量与测试脚本（三套互不一致的 bin 评分公式，已由 explain_one
     第 4 步取代）、`analyze_bin_tracking.py`、`breathing_detailed_analysis.py`。
     连带删除 `testdata/`（chunk200.bin）与各采集目录下的
     `slowtime.npy` / `radar_inspector.png` / `peak_diagnosis.png` 等派生文件。
     原始 bin 与 pcap 全部保留，`cow_vitalsigns_Raw_0_slowtime.npy` 缓存保留。

## 本阶段要做什么

七项判据只能证明**数据链路完整**（序号连续、字节精确、bin≡pcap 逐字节），
**不能证明数据内容正确** —— 一段幅度极小的纯噪声能通过全部检查。
所以：我用妊娠配置采集自己的呼吸心跳（尽量保持不动），
由你做后处理提取呼吸率与心率。**能提取出生理上合理、且与我实测吻合的数值，
才算闭环证明了整条链路的内容正确性。**

需要你交付：
1. 完整的后处理与分析代码
2. **完整的算法说明与数据链路**（每一步做什么、为什么、尺度怎么来的）
3. 采集协议（站位距离、时长、憋气段安排）

## 已经核实的参数（不必重新推导，但可复核）

从 `config/cow_vitalsigns.cfg` 解出并交叉验证过：

```
profileCfg 0 60 20 6 57.00 0 0 60 0 256 5120 0 131072 30
frameCfg   0 0 32 54000 50 1 0
adcbufCfg -1 0 1 1 1      channelCfg 15 1 0      adcCfg 2 1
```

| 量 | 值 | 来源 |
|---|---|---|
| 起始频率 / 斜率 | 60 GHz / 60 MHz/us | cfg |
| ADC 起始 / ramp 结束 | 6 us / 57 us | cfg |
| 采样点 / 采样率 | 256 / 5120 ksps | cfg |
| 采样窗 | 50 us | 256/5.12 MHz |
| **实际采样频段** | 60.36 – 63.36 GHz | 60+0.06×6 到 60+0.06×56 |
| **有效带宽 B** | 3.0 GHz | 50 us × 60 MHz/us |
| 距离分辨率 / 每 bin | 0.049965 m | c/(2B) |
| 满量程 | 12.79 m | 256 bin × 0.05 |
| **采样带中心频率** | 61.86 GHz | 用它算 λ |
| **λ** | 4.8463 mm | c/61.86 GHz |
| **位移/相位** | 0.3857 mm/rad，2π ↔ 2.4232 mm | λ/(4π)，λ/2 |
| 每帧字节 | 131,072 B | 256×4×2×2×32 |
| 慢时间采样率 | **20 Hz** | 1/50 ms，Nyquist 10 Hz |
| 帧内 32 chirp 跨度 | 2.464 ms | 32 × 77 us |
| 帧间最大无模糊位移 | λ/4 = 1.212 mm | 对应 24.2 mm/s |

呼吸 0.1–0.6 Hz、心跳 0.8–2.0 Hz，都远在 10 Hz Nyquist 内。
呼吸位移 1–12 mm ⇒ 2.6–31 rad，**必然过 2π，必须 unwrap**；
心跳位移 0.1–0.5 mm ⇒ 0.26–1.3 rad。

## bin 解析方式（已实测坐实，别再猜）

**直接用 `radar_reader.py`，它已经把下面这些都处理了**：

```python
import radar_reader as rr
rr.describe(session_dir)                       # 先看布局与截断
z = rr.load_frames(session_dir, start=0, count=3600)   # (帧, 32, 4, 256) 复数
```

底层布局（若要自己验证）：

```python
cube = raw.reshape(-1, 32, 4, 256, 2)      # frame, chirp, RX, sample, IQ
z = cube[...,0] - 1j*cube[...,1]           # 注意是减号！
```

三条依据见 memory 的 `vitalsigns-bin-layout-verified`：
RX 非交织（用 meta 里 check_quality.py 的 RX 幅度做外部对照）、
I/Q 逐样本交织（错配会在 bin 127 出伪峰）、
**必须取共轭**（`I+jQ` 时目标能量全在负频，正负比 1:11.2）。

## 两个静默陷阱（`radar_reader.py` 已处理，但你要知道为什么）

**1. 分片边界不落在帧边界上。** 每片 1,073,741,760 B 是 UDP 载荷 1456 的
整数倍，但除以 131,072 得 8191.9995 —— **每个文件边界都劈开一帧，
错位量逐片递增 64 B**。按文件分别解析会从第一个边界起整体错位，
之后所有帧的相位都是垃圾且不报错。必须拼成连续流再切帧。
分片排序要按数字，字典序在 ≥10 片时把 `_Raw_10` 排到 `_Raw_2` 前面。

**2. 末尾总缺不足一帧的几百字节**（实测 128 或 384 B）。
不是丢包（L1/L2 精确为零），是 DCA1000 按 1456 B 推流、末帧凑不满，
那些字节从不存在。按 `floor(总字节/每帧字节)` 取整帧即可，丢最后 1 帧。
真需要完整帧可用 Pi 上的 `pcap_to_bin.py` 从 pcap 重建（已实测能拿回）。

详见 memory 的 `bin-tail-and-segment-straddle`。

## 环境：必须用对解释器（这台机器上有 4 个 Python，只有 1 个是坏的）

**分析在 Windows 做**（Pi 上 numpy 是坏的，三份冲突，见 memory）。
**用这个解释器**：

```
C:\Users\34219\AppData\Local\Programs\Python\Python39\python.exe
```

实测可用：numpy 1.26.1 / scipy 1.13.1 / matplotlib 3.9.4，
`butter`+`filtfilt`+`find_peaks`+`savefig` 全部跑通。
`F:\Tools\Anaconda3\envs\mmwave\python.exe`（3.8.20 / 1.24.4 / 1.10.1 / 3.7.5）
同样可用，是备选。

**坑**：git bash 里裸写 `python` 会解析到 **Anaconda base**
（`F:\Tools\Anaconda3\python.exe`），那个环境里 numpy 2.4.6 与 scipy 1.11.4
不兼容，import scipy/matplotlib 报 `_ARRAY_API not found` /
`numpy.core.multiarray failed to import`。
**别据此以为 scipy 不可用** —— 我上一轮就是这么误判的，用户当场纠正。
每次调用写全路径。
- Pi 免密直连 `ssh pi@192.168.1.131`（sudo 免密），
  数据在 `/mnt/pssd/Ti_radar_data`（exFAT，881 GB 可用）。

## HPF 拐点 —— 影响实验设计的关键发现

`rl_sensor.h:773-787`：HPF1 档位 175/235/350/700 kHz，
**HPF2 最低档就是 350 kHz**。我们配置是 HPF1=175 kHz、HPF2=350 kHz。
拍频 `f_beat = R × 400 kHz/m`，所以：

| 距离 | 拍频 | 结果 |
|---|---|---|
| 0.5 m | 200 kHz | **被衰减** |
| 1.2–1.5 m | 480–600 kHz | 安全 |

⇒ 主测站 **1.2–1.5 m**；**另做一段 0.5 m** 量衰减，
因为牛场妊娠工况正是 0.5 m（见 memory `farm-site-constraints`），
这条直接关系到那个前提还成不成立。衰减多少、相位是否仍可用，**未验证，要实测**。

## 工作方式要求（沿用，务必遵守）

- **改动前先说明目的，等我确认再动手**
- lua 里 `ar1.*` 粘贴区不要动
- 涉及参数计算和 TI 文档结论**先 grep `refer/` 或本机 SDK 核实**，不要凭记忆
- **未验证的结论明确标注**，不要把推算说成实测
- 改 Pi 上文件前先 diff 远端，确认没有我的改动会被覆盖
  （2026-08-02 发生过 scp 覆盖导致对着错误 cfg 下发，浪费一次采集）
- 验证期继续存 bin + pcap 双份
- 回复用中文，写入 memory 的内容也用中文

## 第一步

先给我采集协议（站位、时长、帧数怎么改、憋气段怎么安排），
以及你打算怎么组织分析代码。**我确认后再动手写。**
采集时长建议控制在 3 分钟左右（3600 帧，约 472 MB），别一上来就 45 分钟。
