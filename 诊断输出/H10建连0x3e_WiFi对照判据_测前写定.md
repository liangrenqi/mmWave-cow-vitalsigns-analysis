# H10 建连 0x3e：WiFi 开/关单变量对照（测前写定）

写于 2026-09-28，两次试跑之前。

## 现象

Pi 5 板载蓝牙（BCM4345C0，与 wlan0 同芯片）连 H10（24:AC:AC:11:CC:D4）：
LE Connection Complete 成功，约 0.3 s 后 Disconnect 0x3e。bleak 与 bluetoothctl 都一样。
wlan0 在 2.4 GHz 信道 1。

## 做法

两轮除 WiFi 外完全相同：同一 logger（md5 f9f167b6）、`--duration 20 --connect-timeout 40`、btmon 同时抓包、H10 佩戴不动、手机蓝牙关。

- 轮 1：WiFi 开（基线，SSH 直接跑）
- 轮 2：`nmcli radio wifi off` → 同样跑 → `nmcli radio wifi on`（systemd-run 托管，SSH 断开也会恢复）

## 计数口径（btmon）

每轮数：LE Connection Complete（成功）次数 N，其后 1 s 内以 0x3e 断开的次数 F。

## 判定

| 轮 1（WiFi 开） | 轮 2（WiFi 关） | 结论 |
|---|---|---|
| F/N ≥ 80% | 连上并收到 PMD 数据，且 F/N ≤ 20% | **坐实 WiFi 共存是主因** |
| F/N ≥ 80% | F/N ≥ 80% | **排除 WiFi**，转查 H10 侧 / 控制器 |
| 其他 | | 不判定，记录计数，加轮重复 |

单轮只能区分「显著」差异；若落入「其他」不硬下结论。
