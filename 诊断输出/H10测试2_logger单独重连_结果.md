# 测试 2 结果：h10_logger 单独重连（2026-10-08 20:29–20:37）

判据见 `H10测试2_logger单独重连_测前写定.md`，本报告只执行判据，不改判据。

- 日志：`logs/test2_20261008_202940.log`，原件在 Pi 的 `~/Ti_radar/data/h10/`。
- 人工断开：20:33:59 和 20:36:18。日志记到的 `disconnected` 分别在 20:34:01.7 和 20:36:21.2。
- **测后查到的环境：Pi 的 wlan0 连在 GSWIFI_416，2412 MHz，信道 1，即 2.4 GHz**，不是 09-28 改成的 5 GHz。测前没有核这一项。

## 逐条

| # | 结果 | 依据 |
|---|---|---|
| T2-1 | 通过 | `disconnected` 2 次，`connected` 3 次 |
| T2-2 | **不通过** | 3 次 `connected` 之前最近一次删绑定依次为 rc=0、**rc=1（Device not available）**、rc=0 |
| T2-3 | **不通过** | 断开到首个 PMD：第 1 次约 117 s，第 2 次约 54 s。两次都超过 30 s |
| T2-4 | **不通过** | `connect_fail TimeoutError` 8 次，`session_error` 0 次。另计 `scan_fail` 1 次、`connect_attempt_failed` 373 次 |
| T2-5 | 通过 | 顺序为 `duration_reached` → `disconnected_at_end` → `end`，rc=0 |
| T2-6 | 通过 | 3 次连接内部 ECG 与 ACC 均零缺口（ECG 61.8 / 21.9 / 9.0 s，ACC 62.1 / 22.5 / 9.8 s） |
| T2-7 | 通过 | `pgrep -af h10_logger` 为空 |

**结论：测试 2 不通过（T2-2、T2-3、T2-4）。**

## 分解

- 连上之后各环节都正常。每次 `connected` 后，ECG 首帧在 3.2–3.6 s 到达，ACC 首帧在 2.8–3.2 s 到达。删绑定之后不再出现 30 s 延迟，3 次连接都是如此。
- 慢在建连这一步。首次从启动到连上用了 195 s。每轮扫描都能扫到设备，但 bleak 的建连随后连续失败几十次，直到 30 s 超时。
- 这与 09-28 实测到的现象一致：WiFi 在 2.4 GHz 时建连 15/15 次出现 0x3e，改到 5 GHz 后 3/3 次成功。**本次没有抓 btmon，失败原因是否就是 0x3e 未核实**，目前只是推断。
- T2-2 中的 rc=1 是 bluetoothctl 报「Device not available」，即 BlueZ 里没有这个设备的记录、也就没有绑定可删。上一轮建连失败后设备对象已被清掉。随后那次连接的 PMD 首帧 3.2 s 就到了，没有 30 s 延迟。按写定的判据，这一项仍记为不通过。

## 附带发现（不影响判定）

- `--duration` 只在连接期间检查，断线重连的时间也算在里面，所以本次实际在 267 s 才停下。随采集运行时用的是 SIGINT 加 timeout，不用 `--duration`，没有影响。
- 删绑定的输出里带有 ANSI 颜色码，只影响日志可读性。
