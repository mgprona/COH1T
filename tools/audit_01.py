"""ตรวจละเอียดหมวด 01_ui: สแกนหลายมิติแล้วออกบัตรงาน (ไม่แก้ให้เองทั้งหมด)."""

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("work/translate_parts_v2/01_ui")

# แบรนด์/คำเฉพาะที่ละตินได้โดยชอบธรรม
OK_LATIN = {
    "steam",
    "cpu",
    "ram",
    "fps",
    "lan",
    "ip",
    "gpu",
    "co-op",
    "co op",
    "ok",
    "company of heroes",
    "relic online",
    "reliccoh",
    "tales of valor",
    "opposing fronts",
    "directx",
    "windows",
    "internet",
    "cd",
    "dvd",
    "usb",
    "hdd",
    "ssd",
    "firewall",
    "mac",
    "nvidia",
    "ati",
    "amd",
    "intel",
    "wlan",
}


def latin_words(t: str) -> list[str]:
    return [w.lower() for w in re.findall(r"[A-Za-z]{2,}", t)]


def main() -> None:
    rows = []
    for p in sorted(ROOT.rglob("*.csv")):
        with open(p, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                rows.append((p.name, r))

    issues: dict[str, list] = defaultdict(list)
    short_en: Counter = Counter()
    translated = [(f, r) for f, r in rows if (r["thai"] or "").strip()]

    # 1. ละตินปนที่ไม่อยู่ใน whitelist
    for f, r in translated:
        bad = [w for w in latin_words(r["thai"]) if w not in OK_LATIN]
        if bad:
            issues["latin"].append((f, r["id"], r["english"][:45], r["thai"][:60], bad))

    # 2. เครื่องหมาย/เว้นวรรคเพี้ยน
    for f, r in translated:
        t = r["thai"]
        if re.search(r"[!！]{2,}|[?？]{2,}|[.]{3,}|[ก-๙]\s{2,}|\s{2,}[ก-๙]", t):
            issues["punct"].append((f, r["id"], r["english"][:45], t[:60]))

    # 3. ยาวผิดปกติ (>2.2x ของอังกฤษ — เสี่ยงล้นกรอบ)
    for f, r in translated:
        e, t = r["english"], r["thai"]
        if len(e) > 10 and len(t) > len(e) * 2.2:
            issues["long"].append((f, r["id"], e[:45], t[:60]))

    # 4. คำสั้นๆ ที่แปลไม่สม่ำเสมอ (เทอม UI กลาง)
    for f, r in translated:
        e = r["english"].strip()
        if len(e) <= 30 and e.isupper() and not any(c in e for c in "%$[]"):
            short_en[(f, e, r["thai"])] += 1

    # 5. ขึ้นต้น/ลงท้ายเว้นวรรค หรือ tab ปน
    for f, r in translated:
        t = r["thai"]
        if t != t.strip() or "\t" in t:
            issues["ws"].append((f, r["id"], t[:60]))

    print(f"## แถวแปลทั้งหมด: {len(translated)}")
    print(f"## latin ปน (นอก whitelist): {len(issues['latin'])}")
    for v in issues["latin"][:20]:
        print("  ", v)
    print(f"## เครื่องหมาย/เว้นวรรคเพี้ยน: {len(issues['punct'])}")
    for v in issues["punct"][:15]:
        print("  ", v)
    print(f"## ยาว >2.2x: {len(issues['long'])}")
    for v in issues["long"][:10]:
        print("  ", v)
    print("## คำสั้นซ้ำหลายแบบ (ดูความไม่สม่ำเสมอ):")
    for (f, e, t), n in sorted(short_en.items(), key=lambda kv: -kv[1])[:25]:
        print(f"  x{n:2d} [{f}] {e!r} -> {t!r}")
    print(f"## whitespace เพี้ยน: {len(issues['ws'])}")
    for v in issues["ws"][:10]:
        print("  ", v)


if __name__ == "__main__":
    main()
