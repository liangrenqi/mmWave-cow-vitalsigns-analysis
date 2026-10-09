# H10 建连 0x3e：WiFi 改 5 GHz 后复测（测前写定）

写于 2026-09-28，测量之前。前一次对照见 `H10建连0x3e_WiFi对照结果.md`（2.4 GHz 开：15/15 次 0x3e；WiFi 关：0/1）。

## 变化

用户把 Pi 默认 WiFi 改为 GSWIFI_5G_416。测前只读确认：wlan0 连在信道 149 / 5745 MHz，logger md5 仍为 f9f167b6（与前次相同）。

## 做法

与前次相同：同一 logger、`--duration 20 --connect-timeout 40`、btmon 同时抓包，WiFi **保持开启（5 GHz）**。
连跑 3 轮，每轮之间 `bluetoothctl disconnect` 确保 H10 空出。外层 `timeout -k 10 100` 防止 logger 退出卡死。

## 计数口径

每轮数 LE Connection Complete（成功）次数 N、其后 1 s 内以 0x3e 断开的次数 F；三轮合计。

## 判定

| 三轮合计 | 结论 |
|---|---|
| 3 轮都连上并收到 PMD 数据，且 F/N ≤ 20% | **5 GHz 可解决共存**，实验室可边采边 SSH |
| F/N ≥ 80% | **5 GHz 不够**，仍需采集时关 WiFi 或外置蓝牙 |
| 其他 | 不判定，记录计数，加轮 |

若扫描找不到 H10（未佩戴而休眠），该轮作废不计，不算失败。
本次只测建连，不作第一步验收（验收需戴好静坐 5 分钟，另跑）。
