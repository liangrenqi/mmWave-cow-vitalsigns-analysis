# 测试 2：h10_logger 单独重连（测前写定）

写于 2026-10-08，在测试 2 采集之前。

目的：不接雷达，单独验证新版 `h10_logger.py` 的断线重连这条路径在真实 BLE 上能不能走通。V2-R 是放进采集流程里测，这里先单独测，出了问题才能确定是 logger 本身的问题。

## 条件

- 使用 `~/mmwave-cow-capture/scripts/h10_logger.py`，md5 为 5b6f4e28。
- 佩戴 H10，电极湿润，静坐。手机蓝牙关闭。测试期间不要按遥控器。
- 运行 `--reconnect --remove-bond --duration 240`。
- 在约 60 s 和约 150 s 各执行一次 `bluetoothctl disconnect 24:AC:AC:11:CC:D4`，共 2 次，并人工记下执行时刻。

## 判据（全部满足 = 通过）

| # | 通过条件 |
|---|---|
| T2-1 | 日志中 `disconnected` 恰好 2 次，`connected` 恰好 3 次 |
| T2-2 | 3 次 `connected` 之前，最近一次 `bond_remove` 都是 `rc=0` |
| T2-3 | 每次 `disconnected` 之后，ECG 与 ACC 首个 PMD 帧都在 30 s 以内到达 |
| T2-4 | 不出现 `session_error`、`connect_fail`。`scan_fail` 与 `connect_attempt_failed` 允许出现，但要计数并报告 |
| T2-5 | 结尾为 `duration_reached`，接着 `disconnected_at_end`，再接 `end`；进程退出码为 0 |
| T2-6 | 每一次连接内部，ECG 与 ACC 的传感器时间戳都零缺口。两次连接之间的缺口是预期的，不计入 |
| T2-7 | 退出后 `pgrep -af h10_logger` 为空 |

## 不在本测试范围内

- 语音：logger 自己不播报，语音由 h10_session 负责，在 V2-R 测。
- 走出 BLE 范围造成的真实断线：在 V2-R 的 R2 测。
- systemd 服务环境：在 V3 测。
