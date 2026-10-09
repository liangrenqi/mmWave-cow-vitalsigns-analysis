"""H10 PMD 启动延迟：从「启动命令被接受」到「首个数据帧到达」各多久

只读 h10_logger.py 的原始日志，按 REALTIME 列计算，一条日志一行：
    python h10_start_latency.py <日志1> [<日志2> …] --out 诊断输出/xxx.md

延迟 = 首个该类 PMD 帧的到达时刻 − 该类启动回应（f0 02 <类型> 00）的到达时刻。
只能说明「Pi 这边什么时候收到」；要证明空中确实没包，还得看 btmon（见 PMD启动延迟定位.md 查证 2）。
"""
import argparse
import os

ECG, ACC = 0x00, 0x02
NAME = {ECG: "ECG", ACC: "ACC"}


def one(path):
    rows = [l.split() for l in open(path, encoding="utf-8") if not l.startswith("#") and l.strip()]
    t_conn = next((int(r[0]) for r in rows if r[2] == "EV" and bytes.fromhex(r[3]) == b"connected"), None)
    out = {"文件": os.path.basename(path)}
    # 实验 C 要看「连接 → 首个 ACC 帧」（计时起点是连接还是启动命令）
    t_acc = next((int(r[0]) for r in rows if r[2] == "PMD" and r[3][:2] == f"{ACC:02x}"), None)
    out["连接→首个ACC s"] = f"{(t_acc - t_conn) / 1e9:.2f}" if t_acc and t_conn else "—"
    for m in (ECG, ACC):
        # 启动回应：f0 02 <类型> <状态>，状态 0 = 成功
        t_start = next((int(r[0]) for r in rows if r[2] == "CP_RX"
                        and r[3][:6] == f"f002{m:02x}" and r[3][6:8] == "00"), None)
        t_first = next((int(r[0]) for r in rows if r[2] == "PMD" and r[3][:2] == f"{m:02x}"), None)
        if t_start is None:
            out[NAME[m]] = "未启动"
        elif t_first is None:
            out[NAME[m]] = "启动后无数据"
        else:
            out[NAME[m]] = f"{(t_first - t_start) / 1e9:.2f}"
        if m == ACC and t_start is not None and t_first is not None:
            out["期间HR通知"] = sum(1 for r in rows if r[2] == "HR" and t_start < int(r[0]) < t_first)
    # 实验 E：同一连接内停止再重启（logger --restart-after），只看 restart_begin 之后的记录
    t_rb = next((int(r[0]) for r in rows if r[2] == "EV" and bytes.fromhex(r[3]) == b"restart_begin"), None)
    if t_rb is not None:
        after = [r for r in rows if int(r[0]) > t_rb]
        # 停止回应 f0 03 <类型> <状态>；取 ACC 的（logger 先停 ECG 再停 ACC）
        stop_rx = next((r for r in after if r[2] == "CP_RX" and r[3][:6] == f"f003{ACC:02x}"), None)
        out["停止回应状态"] = stop_rx[3][6:8] if stop_rx else "无"
        t_rs = next((int(r[0]) for r in after if r[2] == "CP_RX"
                     and r[3][:6] == f"f002{ACC:02x}" and r[3][6:8] == "00"), None)
        t_rf = next((int(r[0]) for r in after if r[2] == "PMD" and r[3][:2] == f"{ACC:02x}"
                     and t_rs and int(r[0]) > t_rs), None)
        out["重启ACC s"] = (f"{(t_rf - t_rs) / 1e9:.2f}" if t_rf else "重启后无数据") if t_rs else "未重启"
        # 有效性：停止回应 2 s 后到重启回应之前不应再有 PMD 帧（否则重启后的「首帧」可能是残留）
        if stop_rx and t_rs:
            t_sr = int(stop_rx[0])
            out["停止后残留PMD"] = sum(1 for r in after if r[2] == "PMD" and t_sr + 2e9 < int(r[0]) < t_rs)
        out["中途断开"] = "是" if any(r[2] == "EV" and bytes.fromhex(r[3]) == b"disconnected"
                                    and int(r[0]) < (t_rf or 0) for r in rows) else "否"
    hr = [bytes.fromhex(r[3]) for r in rows if r[2] == "HR"]
    # 标志字节 bit1-2 = 皮肤接触（3 = 支持且接触良好）
    out["首条HR接触"] = (hr[0][0] >> 1) & 3 if hr else "无HR"
    out["连接→首条HR s"] = (f"{(next(int(r[0]) for r in rows if r[2] == 'HR') - t_conn) / 1e9:.2f}"
                          if hr and t_conn else "—")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = [one(p) for p in a.logs]
    cols = ["文件", "ECG", "ACC", "连接→首个ACC s", "期间HR通知", "首条HR接触", "连接→首条HR s"]
    if any("重启ACC s" in r for r in res):
        cols += ["停止回应状态", "停止后残留PMD", "重启ACC s", "中途断开"]
    L = ["# H10 PMD 启动延迟（单位 s，启动回应 → 首个数据帧）", "",
         "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    L += ["| " + " | ".join(str(r.get(c, "—")) for c in cols) + " |" for r in res]
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\n→ {a.out}")
