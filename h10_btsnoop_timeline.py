"""btmon 抓包（btsnoop，Linux monitor 格式 2001）→ 逐包时间线，找 H10 PMD 启动那 30 s 里空中发生了什么

    python h10_btsnoop_timeline.py <x.btsnoop> [--out 诊断输出/xxx.md] [--all]

默认省略：HR 通知（句柄 0x0010）、PMD 数据通知（0x0032 分片起始包只计数）、Number of Completed Packets 事件、
ACL 续传分片。其余逐条列出：HCI 命令/事件、SMP（CID 6）、L2CAP 信令（CID 5）、所有 ATT 请求/响应/错误。
方向：TX = Pi→H10，RX = H10→Pi。时间以第一个 LE Connection Complete 为 0。
只读抓包文件，不改原始数据。
"""
import argparse
import struct

OPC = {0: "NEW_INDEX", 1: "DEL_INDEX", 2: "CMD", 3: "EVT", 4: "ACL_TX", 5: "ACL_RX",
       8: "OPEN_INDEX", 9: "CLOSE_INDEX", 10: "INDEX_INFO", 12: "NOTE", 13: "LOG"}
ATT = {0x01: "Error Rsp", 0x02: "Exchange MTU Req", 0x03: "Exchange MTU Rsp", 0x04: "Find Info Req",
       0x05: "Find Info Rsp", 0x06: "Find By Type Value Req", 0x07: "Find By Type Value Rsp",
       0x08: "Read By Type Req", 0x09: "Read By Type Rsp", 0x0a: "Read Req", 0x0b: "Read Rsp",
       0x0c: "Read Blob Req", 0x0d: "Read Blob Rsp", 0x10: "Read By Group Type Req",
       0x11: "Read By Group Type Rsp", 0x12: "Write Req", 0x13: "Write Rsp", 0x52: "Write Cmd",
       0x1b: "Notify", 0x1d: "Indicate", 0x1e: "Confirm"}
ATT_REQ = {0x02, 0x04, 0x06, 0x08, 0x0a, 0x0c, 0x10, 0x12}
SMP = {0x01: "Pairing Req", 0x02: "Pairing Rsp", 0x03: "Pairing Confirm", 0x04: "Pairing Random",
       0x05: "Pairing Failed", 0x06: "Encryption Info", 0x07: "Central Ident", 0x08: "Identity Info",
       0x09: "Identity Addr Info", 0x0a: "Signing Info", 0x0b: "Security Req",
       0x0c: "Pairing Public Key", 0x0d: "DHKey Check"}
EVT = {0x05: "Disconnection Complete", 0x08: "Encryption Change", 0x0e: "Command Complete",
       0x0f: "Command Status", 0x30: "Encryption Key Refresh Complete", 0x3e: "LE Meta"}
LE_SUB = {0x01: "LE Connection Complete", 0x03: "LE Conn Update Complete", 0x04: "LE Read Remote Features",
          0x05: "LE LTK Request", 0x06: "LE Remote Conn Param Req", 0x07: "LE Data Length Change",
          0x0a: "LE Enhanced Conn Complete", 0x0c: "LE PHY Update Complete"}
CMD = {0x0406: "Disconnect", 0x2019: "LE Start Encryption", 0x201a: "LE LTK Reply",
       0x201b: "LE LTK Neg Reply", 0x200d: "LE Create Connection", 0x2043: "LE Ext Create Connection",
       0x2013: "LE Conn Update", 0x2016: "LE Read Remote Features", 0x2022: "LE Set Data Length",
       0x2032: "LE Set PHY", 0x200e: "LE Create Conn Cancel", 0x0c05: "", 0x2042: "LE Set Ext Scan Enable",
       0x200c: "LE Set Scan Enable"}
HR_H, PMD_H = 0x0010, 0x0032


def records(path):
    d = open(path, "rb").read()
    assert d[:8] == b"btsnoop\0", "不是 btsnoop"
    ver, dlt = struct.unpack(">II", d[8:16])
    assert dlt == 2001, f"datalink={dlt}，只支持 Linux monitor 格式 2001"
    p = 16
    while p + 24 <= len(d):
        olen, ilen, flags, drops, ts = struct.unpack(">IIIIq", d[p:p + 24])
        p += 24
        yield ts, flags & 0xffff, flags >> 16, d[p:p + ilen]
        p += ilen


def describe(op, pkt):
    """返回 (类别, 文字)；类别用于默认过滤"""
    if op == 2:
        opc = struct.unpack("<H", pkt[:2])[0]
        return "cmd", f"CMD 0x{opc:04x} {CMD.get(opc, '')} {pkt[3:].hex()}"
    if op == 3:
        code = pkt[0]
        if code == 0x13:
            return "ncp", "Num Completed Packets"
        if code == 0x3e:
            sub = pkt[2]
            return "evt", f"EVT {LE_SUB.get(sub, f'LE sub 0x{sub:02x}')} {pkt[3:].hex()}"
        if code in (0x0e, 0x0f):
            if code == 0x0e:
                opc = struct.unpack("<H", pkt[3:5])[0]
                return "evt", f"EVT Command Complete 0x{opc:04x} {CMD.get(opc, '')} 状态 {pkt[5:6].hex()}"
            opc = struct.unpack("<H", pkt[4:6])[0]
            return "evt", f"EVT Command Status 0x{opc:04x} {CMD.get(opc, '')} 状态 {pkt[2]:02x}"
        return "evt", f"EVT {EVT.get(code, f'0x{code:02x}')} {pkt[2:].hex()}"
    if op in (4, 5):
        d = "TX Pi→H10" if op == 4 else "RX H10→Pi"
        hf = struct.unpack("<H", pkt[:2])[0]
        pb = (hf >> 12) & 3
        if pb == 1:
            return "cont", f"{d} ACL 续传分片"
        l2len, cid = struct.unpack("<HH", pkt[4:8])
        pl = pkt[8:]
        if cid == 4 and pl:
            o = pl[0]
            name = ATT.get(o, f"ATT 0x{o:02x}")
            if o in (0x1b, 0x1d) and len(pl) >= 3:
                h = struct.unpack("<H", pl[1:3])[0]
                if h == HR_H:
                    return "hr", f"{d} HR 通知"
                if h == PMD_H:
                    return "pmd", f"{d} PMD 数据 类型 {pl[3:4].hex()} L2CAP 长 {l2len}"
                return "att", f"{d} ATT {name} 句柄 0x{h:04x} {pl[3:].hex()}"
            if o == 0x01:
                return "att", f"{d} ATT Error Rsp 对 {ATT.get(pl[1], hex(pl[1]))} 句柄 0x{struct.unpack('<H', pl[2:4])[0]:04x} 错误 0x{pl[4]:02x}"
            tag = "【请求】" if o in ATT_REQ else ""
            return "att", f"{d} ATT {name}{tag} {pl[1:].hex()}"
        if cid == 6:
            return "smp", f"{d} SMP {SMP.get(pl[0], hex(pl[0]))} {pl[1:].hex()}"
        if cid == 5:
            return "sig", f"{d} L2CAP 信令 code 0x{pl[0]:02x} {pl[1:].hex()}"
        return "l2", f"{d} L2CAP CID 0x{cid:04x} 长 {l2len}"
    if op == 12:
        return "note", "NOTE " + pkt.rstrip(b"\0").decode(errors="replace")
    return "other", f"{OPC.get(op, op)}"


def timeline(path, show_all=False):
    rows, t0 = [], None
    pending = {}  # 尚未收到响应的 ATT 请求：方向 → (时刻, 文字)
    for ts, op, idx, pkt in records(path):
        try:
            kind, text = describe(op, pkt)
        except Exception as e:  # 截断包等
            kind, text = "bad", f"解析失败 {e}"
        if t0 is None and "Connection Complete" in text:
            t0 = ts
        rows.append((ts, kind, text))
    t0 = t0 or rows[0][0]
    out, n_hr, n_pmd, first_pmd = [], 0, 0, None
    for ts, kind, text in rows:
        t = (ts - t0) / 1e6
        if kind == "hr":
            n_hr += 1
        if kind == "pmd":
            n_pmd += 1
            if first_pmd is None:
                first_pmd = t
                out.append((t, f"**首个 PMD 数据包** {text}（此前 HR 通知 {n_hr} 个）"))
                continue
        if show_all or kind in ("cmd", "evt", "smp", "sig", "att", "l2", "note", "bad"):
            # 扫描阶段的广播报告与扫描开关与本问题无关
            if not show_all and (t < 0 or "Scan" in text or "LE sub 0x02" in text or "LE sub 0x0d" in text):
                continue
            out.append((t, text))
    return out, n_hr, n_pmd, first_pmd


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("snoops", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    L = ["# btsnoop 时间线（省略 HR/PMD 数据通知与续传分片；t=0 为首个 Connection Complete）", ""]
    for s in a.snoops:
        out, n_hr, n_pmd, fp = timeline(s, a.all)
        L += [f"## {s}", "", f"HR 通知 {n_hr}、PMD 数据包 {n_pmd}、首个 PMD 在 t={fp}", "", "```"]
        L += [f"{t:9.3f}  {x}" for t, x in out]
        L += ["```", ""]
    txt = "\n".join(L)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(txt)
    print(txt)
