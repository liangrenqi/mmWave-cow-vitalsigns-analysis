"""V2 判定：雷达与 H10 并行互不干扰，按 `诊断输出/H10方案验证_V2判据_测前写定.md` 执行（判据在该文件写定，这里不改）。

用法：
    python h10_v2_check.py <段目录1> [<段目录2> …]
    python h10_v2_check.py --redo <段目录…>   # 重做 V2：V2-1 按重做版写定文件，输出 H10方案验证_V2重做结果.md
    段目录 = Pi 上 fileBasePath 下的 Cow_*（或 BAD_Cow_*）整个拷回来；
    V2-2 要看同级的 _h10_staging/ 与 H10_ORPHAN/，所以连同父目录一起拷（或至少拷这两个目录）。
输出：诊断输出/H10方案验证_V2结果.md
V2-8（无残留进程）、V2-9（语音）是人工项，报告里留空位手填。
判据 3 不进 V2：另跑 `h10_rpeak.py <日志>`（判定模式，合并方案 AB）单列。
"""
import contextlib
import io
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "诊断输出"
sys.path.insert(0, str(HERE))
# --redo：按 `H10方案验证_V2重做_判据_测前写定.md` 判（只改了 V2-1），输出另存，不覆盖首轮结果
REDO = "--redo" in sys.argv


def read_meta(p):
    kv = {}
    for ln in p.read_text(encoding="utf-8").splitlines():
        if "=" in ln and not ln.startswith("#") and not ln.startswith(" "):
            k, _, v = ln.partition("=")
            kv[k.strip()] = v.split("   #")[0].strip()
    return kv


def events(log):
    out = []
    for ln in log.read_text(encoding="utf-8").splitlines():
        parts = ln.split()
        if len(parts) >= 3 and parts[2] == "EV" and not ln.startswith("#"):
            try:
                out.append((int(parts[0]), bytes.fromhex(parts[3]).decode(errors="replace") if len(parts) > 3 else ""))
            except ValueError:
                pass
    return out


def step1_results(L):
    """从 h10_parse.analyse 的报告行取判据 1–6 的通过与否（按「## 判据 k」小节里第一个 → **通过/不通过**）"""
    res, cur = {}, None
    for ln in L:
        m = re.match(r"\n?## 判据 (\d)", ln)
        if m:
            cur = int(m.group(1)); continue
        if cur and cur not in res:
            if "**通过**" in ln:
                res[cur] = True
            elif "**不通过**" in ln:
                res[cur] = False
    return res


def check(seg):
    seg = Path(seg)
    R, notes = {}, []
    meta_p = seg / "capture_meta.txt"
    meta = read_meta(meta_p) if meta_p.is_file() else {}

    # V2-1
    try:
        fails, unk = int(meta.get("checks_failed", -1)), int(meta.get("checks_unknown", -1))
    except ValueError:
        fails = unk = -1
    unk_items = sorted(k[len("check."):] for k, v in meta.items()
                       if k.startswith("check.") and not k.endswith(".detail") and v == "UNKNOWN")
    if REDO:
        # 重做版（`H10方案验证_V2重做_判据_测前写定.md`）：未判定项只允许 csv，且 csv 须是「为空」那种未判定
        csv_ok = unk_items in ([], ["csv"]) and (not unk_items or "为空" in meta.get("check.csv.detail", ""))
        R["V2-1"] = (meta.get("verdict") == "GOOD" and fails == 0 and len(unk_items) == unk and csv_ok)
    else:
        R["V2-1"] = meta.get("verdict") == "GOOD" and fails == 0 and unk == 0
    notes.append(f"V2-1 verdict={meta.get('verdict')} checks_failed={fails} checks_unknown={unk} 未判定项 {unk_items}")

    # V2-2
    logs = sorted(seg.glob("h10_*.log"))
    outs = sorted(seg.glob("h10_*.log.stdout.txt"))
    stage = seg.parent / "_h10_staging"
    stage_left = [p.name for p in stage.glob("h10_*")] if stage.is_dir() else None
    orphan_new = []
    t0 = datetime.strptime(meta["start"], "%Y-%m-%d %H:%M:%S") if "start" in meta else None
    t1 = datetime.strptime(meta["end"], "%Y-%m-%d %H:%M:%S") if "end" in meta else None
    orphan = seg.parent / "H10_ORPHAN"
    if orphan.is_dir() and t0 and t1:
        for p in orphan.glob("h10_*.log"):
            m = re.match(r"h10_(\d{8}_\d{6})", p.name)
            if m:
                ts = datetime.strptime(m.group(1), "%Y%m%d_%H%M%S")
                if t0 - timedelta(seconds=120) <= ts <= t1:
                    orphan_new.append(p.name)
    ok_one = len(logs) == 1 and len(outs) == 1 and outs[0].name == logs[0].name + ".stdout.txt"
    R["V2-2"] = ok_one and stage_left == [] and not orphan_new
    notes.append(f"V2-2 段内日志 {[p.name for p in logs]}、stdout {[p.name for p in outs]}；"
                 f"_h10_staging 残留 {stage_left if stage_left is not None else '（目录未拷回，无法核）'}；"
                 f"本段时间内 H10_ORPHAN 新文件 {orphan_new or '无'}")
    if stage_left is None:
        R["V2-2"] = None
    if len(logs) != 1:
        for k in ("V2-3", "V2-4", "V2-5"):
            R[k] = False
        notes.append("段内 H10 日志不是恰好 1 个 → V2-3/4/5 记不通过")
        log = None
    else:
        log = logs[0]

    if log is not None:
        ev = events(log)
        names = [e for _, e in ev]
        # V2-3：每个 connected 之前（自上一个 connected 起）最近一次 bond_remove 的 rc 为 0
        ok_bond, last_bond, seen = True, None, []
        for _, e in ev:
            if e.startswith("bond_remove"):
                last_bond = e
            elif e == "connected":
                seen.append(last_bond)
                ok_bond &= bool(last_bond) and last_bond.startswith("bond_remove rc=0")
                last_bond = None
        from h10_start_latency import one
        lat = one(str(log))
        try:
            ecg_s, acc_s = float(lat["ECG"]), float(lat["ACC"])
            ok_fast = ecg_s < 5 and acc_s < 5
        except (KeyError, ValueError):
            ecg_s = acc_s = None; ok_fast = False
        R["V2-3"] = ok_bond and ok_fast and bool(seen)
        notes.append(f"V2-3 每次建连前的删绑定 {seen}；首帧 ECG {lat.get('ECG')} s、ACC {lat.get('ACC')} s（< 5 s）")

        # V2-4
        n_conn = names.count("connected")
        bad = {k: names.count(k) for k in ("disconnected", "connect_attempt_failed", "scan_fail")}
        bad["session_error"] = sum(e.startswith("session_error") for e in names)
        n_end = names.count("disconnected_at_end")
        R["V2-4"] = n_conn == 1 and not any(bad.values()) and n_end == 1
        notes.append(f"V2-4 connected {n_conn} 次；{bad}；disconnected_at_end {n_end} 次")

        # V2-5：第一步判据 1、2、4、6
        from h10_parse import analyse
        with contextlib.redirect_stdout(io.StringIO()):
            L, _, _ = analyse(str(log))
        s1 = step1_results(L)
        R["V2-5"] = all(s1.get(k) is True for k in (1, 2, 4, 6))
        notes.append(f"V2-5 第一步判据 1/2/4/6：{ {k: s1.get(k) for k in (1, 2, 4, 6)} }"
                     f"（判据 3、5 不进 V2，此处仅记录：3={s1.get(3)} 5={s1.get(5)}）")
        notes.append("    " + next((x for x in L if x.startswith("ECG：") and "帧" in x), ""))

    # V2-6
    def num(k):
        try:
            return float(meta[k])
        except (KeyError, ValueError):
            return None
    lead, tail = num("h10_pmd_lead_sec"), num("h10_pmd_tail_sec")
    R["V2-6"] = lead is not None and tail is not None and lead >= 0 and tail >= 0
    notes.append(f"V2-6 h10_pmd_lead_sec={lead} h10_pmd_tail_sec={tail}（都须 ≥ 0）")

    # V2-7
    ex, rc = meta.get("h10_exit", ""), meta.get("h10_rc", "")
    if ex == "正常退出" and rc == "0":
        R["V2-7"] = True
    elif "exit_forced" in ex:
        R["V2-7"] = "有保留"
    else:
        R["V2-7"] = False
    notes.append(f"V2-7 h10_exit={ex} h10_rc={rc} h10_status={meta.get('h10_status')}")
    return R, notes, (str(log) if log else None)


def word(v):
    return {True: "通过", False: "**不通过**", None: "不判定", "有保留": "有保留通过"}.get(v, str(v))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    segs = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not segs:
        print(__doc__); sys.exit(1)
    keys = [f"V2-{i}" for i in range(1, 8)]
    title, crit = (("# H10 并入验证 V2 重做结果\n", "`H10方案验证_V2重做_判据_测前写定.md`") if REDO
                   else ("# H10 并入验证 V2 结果\n", "`H10方案验证_V2判据_测前写定.md`"))
    L = [title, f"判据见 {crit}，本报告只执行不改。\n",
         "| 段 | " + " | ".join(keys) + " | V2-8 无残留（人工） | V2-9 语音（人工） |",
         "|---|" + "---|" * (len(keys) + 2)]
    detail, logs, allres = [], [], []
    for s in segs:
        R, notes, log = check(s)
        allres.append(R)
        logs.append(log)
        L.append(f"| {Path(s).name} | " + " | ".join(word(R.get(k)) for k in keys) + " | 　 | 　 |")
        detail += [f"\n### {Path(s).name}\n"] + [f"- {n}" for n in notes]
    L += ["\n## 明细"] + detail
    hard = [k for R in allres for k in keys if R.get(k) is False]
    L.append("\n## 结论（脚本部分；V2-8、V2-9 人工补填后才是最终结论）\n")
    if len(segs) != 3:
        L.append(f"- 写定为 3 段，本次给了 {len(segs)} 段")
    L.append("- 脚本项全部通过" if not hard else f"- 脚本项不通过：{sorted(set(hard))}，按写定文件「结论」表处理")
    L.append("\n## 单列：判据 3（合并方案 AB，不影响 V2 结论）\n")
    L.append("对每段跑：" + "；".join(f"`python h10_rpeak.py {p}`" for p in logs if p))
    out = OUT / ("H10方案验证_V2重做结果.md" if REDO else "H10方案验证_V2结果.md")
    out.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L)); print(f"\n→ {out}")


if __name__ == "__main__":
    main()
