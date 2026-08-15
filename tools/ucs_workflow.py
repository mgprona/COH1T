import csv
import sys
from pathlib import Path

from tools.pua_encode import encode, load_map
from tools.ucs_sections import Section, section_of

FE_CONTEXTS = {
    713500: "ปุ่มต่อแคมเปญ",
    713501: "ชื่อแคมเปญนอร์มังดี",
    713502: "tooltip เริ่มแคมเปญนอร์มังดี",
    713503: "ปุ่มเมนูหลัก: บทเรียน",
    713504: "ฉลากเวอร์ชันเกม",
    713505: "tooltip เล่นแคมเปญผู้เล่นเดี่ยว",
    713506: "ชื่อแคมเปญบุกคาน",
    713507: "tooltip เริ่มบทเรียน",
    713508: "tooltip ออกจากเกม",
    713509: "ปุ่มเมนูหลัก: ศึกรวดเร็ว",
    713510: "ปุ่มเมนูหลัก: ออก",
    713511: "tooltip เริ่มแคมเปญบุกคาน",
    713512: "ปุ่มเมนูหลัก: แคมเปญ",
    713513: "tooltip ต่อแคมเปญนอร์มังดี",
    713514: "ชื่อแคมเปญมาร์เก็ตการ์เดน",
    713515: "ชื่อแคมเปญเสือเหล็ก",
    713516: "tooltip ศึกรวดเร็วกับ CPU",
    713517: "tooltip ต่อแคมเปญบุกคาน",
    713518: "tooltip เริ่มแคมเปญมาร์เก็ตการ์เดน",
    713519: "tooltip เล่นผู้เล่นหลายคน",
    713520: "ปุ่มเมนูหลัก: ผู้เล่นหลายคน",
    713521: "ปุ่มเมนูหลัก: ตัวเลือก",
    713522: "tooltip ตั้งค่าเกม",
    713523: "ปุ่มเลือกภารกิจ",
    713524: "ปุ่มต่อเกม",
    713525: "tooltip ล็อกปฏิบัติการ (ต้องมี Tales of Valor)",
    713526: "ปุ่มต่อเกม",
    713527: "ปุ่มต่อเกม",
    713528: "ปุ่มเมนูหลัก: เวิร์กชอป",
    713529: "ปุ่มเลือกภารกิจ",
    713530: "ปุ่มต่อเกม",
    713531: "ปุ่มเลือกภารกิจ",
    713532: "ปุ่มต่อเกม",
    713533: "ปุ่มเลือกภารกิจ",
    713535: "tooltip เข้า Steam Workshop",
    713540: "ปุ่มเลือกภารกิจ",
    713541: "tooltip เริ่มแคมเปญฟาแลสพ็อกเก็ต",
    713542: "tooltip ต่อแคมเปญฟาแลสพ็อกเก็ต",
    713543: "ปุ่มเลือกภารกิจ",
    713544: "ปุ่มเมนูหลัก: ปฏิบัติการ",
    713545: "ชื่อแคมเปญคอสเวย์",
    713547: "tooltip เริ่มแคมเปญคอสเวย์",
    713548: "ชื่อแคมเปญฟาแลสพ็อกเก็ต",
    713552: "tooltip ต่อแคมเปญมาร์เก็ตการ์เดน",
    713555: "tooltip เริ่มแคมเปญเสือเหล็ก",
    713556: "tooltip ต่อแคมเปญเสือเหล็ก",
    713557: "tooltip ต่อแคมเปญคอสเวย์",
    713558: "tooltip ปฏิบัติการผู้เล่นหลายคน",
    5256: "เมนูเก่า: เมนูหลัก",
    9250: "เมนูเก่า: แคมเปญ",
    9251: "เมนูเก่า: ศึกรวดเร็ว",
    9252: "เมนูเก่า: ผู้เล่นหลายคน",
}


def read_ucs(path: Path) -> dict[int, str]:
    text = path.read_bytes().decode("utf-16")
    assert "\r\r" not in text, f"{path}: double-CR corruption detected"
    entries: dict[int, str] = {}
    for line in text.splitlines():
        if not line:
            continue
        sid, _, value = line.partition("\t")
        if sid.isdigit():
            entries[int(sid)] = value
    return entries


def write_ucs(path: Path, entries: dict[int, str]) -> None:
    lines = [f"{i}\t{t}" for i, t in sorted(entries.items())]
    with open(path, "w", encoding="utf-16", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")
    raw = path.read_bytes()
    assert b"\r\x00\r\x00" not in raw, f"{path}: double-CR corruption detected"


def extract(base_ucs: Path, current_ucs: Path, out_csv: Path) -> int:
    base = read_ucs(base_ucs)
    current = read_ucs(current_ucs)
    ids = sorted(FE_CONTEXTS)
    rows = 0
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(["id", "english", "thai", "context"])
        for sid in ids:
            english = base.get(sid, "")
            thai = current.get(sid, "")
            if thai == english:
                thai = ""
            w.writerow([sid, english, thai, FE_CONTEXTS[sid]])
            rows += 1
    return rows


def extract_all(base_ucs: Path, current_ucs: Path, menu_csv: Path, out_csv: Path) -> int:
    base = read_ucs(base_ucs)
    current = read_ucs(current_ucs)
    menu_translations: dict[int, str] = {}
    if menu_csv.exists():
        with open(menu_csv, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                thai = (row.get("thai") or "").strip()
                if thai:
                    menu_translations[int(row["id"])] = thai
    rows = 0
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(["id", "english", "thai", "context"])
        for sid in sorted(base):
            english = base[sid]
            thai = menu_translations.get(sid)
            if thai is None:
                cur = current.get(sid, "")
                thai = "" if cur == english else cur
            w.writerow([sid, english, thai, FE_CONTEXTS.get(sid, "")])
            rows += 1
    return rows


CATEGORY_RANGES = {
    "01_ui_menu": [(0, 100000), (500000, 800000), (12000000, 20000000)],
    "02_units_abilities": [(100000, 200000), (2000000, 2300000)],
    "03_campaign_normandy": [(200000, 500000)],
    "04_campaign_expansions": [
        (1300000, 1500000),
        (9000000, 9600000),
        (10000000, 10100000),
        (11000000, 12000000),
    ],
    "05_speech_radio": [(800000, 900000), (6000000, 7500000)],
}

CATEGORY_CONTEXTS = {
    "01_ui_menu": "UI/เมนู/ตั้งค่า/ระบบ",
    "02_units_abilities": "ยูนิต/อาวุธ/สกิล/อัปเกรด/สิ่งปลูกสร้าง",
    "03_campaign_normandy": "แคมเปญนอร์มังดี: บทพูด/บรีฟภารกิจ/เป้าหมาย",
    "04_campaign_expansions": "แคมเปญเสริม: ก็อง/มาร์เก็ตการ์เดน/ToV",
    "05_speech_radio": "เสียงพากย์/วิทยุสื่อสาร/เสียงตอบรับ",
}


def _category_of(sid: int) -> str:
    for cat, ranges in CATEGORY_RANGES.items():
        for lo, hi in ranges:
            if lo <= sid < hi:
                return cat
    raise ValueError(f"id {sid} not covered by CATEGORY_RANGES")


def extract_categories(
    base_ucs: Path, current_ucs: Path, menu_csv: Path, out_dir: Path
) -> dict[str, int]:
    base = read_ucs(base_ucs)
    current = read_ucs(current_ucs)
    menu_translations: dict[int, str] = {}
    if menu_csv.exists():
        with open(menu_csv, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                thai = (row.get("thai") or "").strip()
                if thai:
                    menu_translations[int(row["id"])] = thai
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_by_cat: dict[str, list[tuple[int, str, str]]] = {c: [] for c in CATEGORY_RANGES}
    for sid in sorted(base):
        english = base[sid]
        thai = menu_translations.get(sid)
        if thai is None:
            cur = current.get(sid, "")
            thai = "" if cur == english else cur
        rows_by_cat[_category_of(sid)].append((sid, english, thai))
    counts: dict[str, int] = {}
    for cat, rows in rows_by_cat.items():
        path = out_dir / f"{cat}.csv"
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, lineterminator="\r\n")
            w.writerow(["id", "english", "thai", "context"])
            for sid, english, thai in rows:
                context = FE_CONTEXTS.get(sid) or CATEGORY_CONTEXTS[cat]
                w.writerow([sid, english, thai, context])
        counts[cat] = len(rows)
    return counts


def merge_parts(parts_dir: Path, menu_csv: Path, out_csv: Path) -> tuple[int, int]:
    rows: dict[str, dict[str, str]] = {}
    for src in [*sorted(parts_dir.rglob("*.csv")), menu_csv]:
        if not src.exists():
            continue
        with open(src, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                sid = row["id"]
                merged = rows.setdefault(sid, {"id": sid, "english": "", "thai": "", "context": ""})
                for col in ("english", "thai", "context"):
                    v = (row.get(col) or "").strip()
                    if v:
                        merged[col] = v
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(["id", "english", "thai", "context"])
        for sid in sorted(rows, key=int):
            r = rows[sid]
            w.writerow([r["id"], r["english"], r["thai"], r["context"]])
    translated = sum(1 for r in rows.values() if r["thai"])
    return len(rows), translated


def _row_ids(row: dict[str, str]) -> list[int]:
    raw = row.get("all_ids") or row.get("id") or ""
    ids: list[int] = []
    for token in raw.replace("|", " ").replace(";", " ").split():
        if token.isdigit():
            ids.append(int(token))
    return ids


def collect_translations(src: Path) -> tuple[dict[int, str], list[str]]:
    """อ่านคำแปลจาก csv เดียวหรือโฟลเดอร์ csvs (กระจาย all_ids) -> ({id: thai}, warnings)"""
    trans: dict[int, str] = {}
    warnings: list[str] = []
    paths = sorted(src.rglob("*.csv")) if src.is_dir() else [src]
    for p in paths:
        with open(p, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                thai = (row.get("thai") or "").strip()
                if not thai:
                    continue
                for sid in _row_ids(row):
                    if sid in trans and trans[sid] != thai:
                        warnings.append(f"id {sid}: มีคำแปลซ้ำขัดกันในไฟล์ ({p.name}) -> ใช้ค่าหลัง")
                    trans[sid] = thai
    return trans, warnings


def apply(csv_path: Path, base_ucs: Path, out_ucs: Path, map_path: Path) -> list[str]:
    m = load_map(map_path)
    entries = read_ucs(base_ucs)
    warnings: list[str] = []
    trans, dup_warnings = collect_translations(csv_path)
    warnings.extend(dup_warnings)
    for sid in sorted(trans):
        thai = trans[sid]
        if sid not in entries:
            warnings.append(f"id {sid}: ไม่มีใน ucs ต้นฉบับ -> ข้าม")
            continue
        encoded, missing = encode(thai, m)
        if missing:
            warnings.append(f"id {sid}: new clusters {sorted(missing)} -> run pua_font_builder.py")
            entries[sid] = thai
        else:
            entries[sid] = encoded
    write_ucs(out_ucs, entries)
    return warnings


def extract_unique(base_ucs: Path, parts_dir: Path, out_dir: Path) -> dict[str, int]:
    """โครงสร้างใหม่: dedupe แบบ (english,thai) + all_ids + ไฟล์ต่อ section (ตาม ucs_sections)"""
    base = read_ucs(base_ucs)
    trans, dup_warnings = collect_translations(parts_dir)
    for w in dup_warnings:
        print("WARN:", w)
    groups: dict[tuple[str, str], list[int]] = {}
    for sid in sorted(base):
        e = base[sid]
        t = trans.get(sid, "")
        groups.setdefault((e, t), []).append(sid)
    rows_by_sec: dict[Section, list[tuple[str, str, list[int]]]] = {}
    for (e, t), ids in groups.items():
        sec = section_of(ids[0], e)
        rows_by_sec.setdefault(sec, []).append((e, t, ids))
    counts: dict[str, int] = {}
    for sec, rows in rows_by_sec.items():
        d = out_dir / sec.category
        d.mkdir(parents=True, exist_ok=True)
        with open(d / sec.file, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, lineterminator="\r\n")
            w.writerow(["id", "english", "thai", "context", "all_ids"])
            for e, t, ids in sorted(rows, key=lambda r: r[2][0]):
                context = sec.context
                if ids[0] in FE_CONTEXTS:
                    context = f"{sec.context} | {FE_CONTEXTS[ids[0]]}"
                w.writerow([ids[0], e, t, context, "|".join(map(str, ids))])
        counts[f"{sec.category}/{sec.file}"] = len(rows)
    return counts


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    cmd = sys.argv[1]
    if cmd == "extract":
        n = extract(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
        print(f"extracted {n} rows -> {sys.argv[4]}")
    elif cmd == "extract_all":
        n = extract_all(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
        print(f"extracted {n} rows -> {sys.argv[5]}")
    elif cmd == "extract_categories":
        counts = extract_categories(
            Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5])
        )
        for cat, n in counts.items():
            print(f"{cat}: {n}")
    elif cmd == "extract_unique":
        counts = extract_unique(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
        for sec, n in sorted(counts.items()):
            print(f"{sec}: {n} rows")
        print(f"รวม {sum(counts.values())} rows")
    elif cmd == "merge_parts":
        rows, translated = merge_parts(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
        print(f"merged {rows} rows ({translated} translated) -> {sys.argv[4]}")
    elif cmd == "apply":
        warnings = apply(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
        for w in warnings:
            print("WARN:", w)
        print(f"applied -> {sys.argv[4]}")
    else:
        print(
            "usage: ucs_workflow.py extract <base.ucs> <current.ucs> <out.csv> | "
            "extract_all <base.ucs> <current.ucs> <menu.csv> <out.csv> | "
            "extract_categories <base.ucs> <current.ucs> <menu.csv> <out_dir> | "
            "extract_unique <base.ucs> <parts_dir> <out_dir> | "
            "merge_parts <parts_dir> <menu.csv> <out.csv> | "
            "apply <translate.csv|parts_dir> <base.ucs> <out.ucs> <cluster_map.json>"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
