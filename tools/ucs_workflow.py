import csv
import sys
from pathlib import Path

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
    text = path.read_text(encoding="utf-16")
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
    assert b"\r\r" not in raw, f"{path}: double-CR corruption detected"


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


def main() -> None:
    cmd = sys.argv[1]
    if cmd == "extract":
        n = extract(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
        print(f"extracted {n} rows -> {sys.argv[4]}")
    else:
        print("usage: ucs_workflow.py extract <base.ucs> <current.ucs> <out.csv>")
        sys.exit(1)


if __name__ == "__main__":
    main()
