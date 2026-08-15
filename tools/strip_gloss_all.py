"""ลบวงเล็บ gloss อังกฤษ (มีตัวอักษร ASCII อย่างน้อย 1 ตัว) ออกจากทุกไฟล์ translate_parts_v2.

ไม่แตะวงเล็บไทย/ตัวเลขล้วน เช่น (2), (ของฝ่ายอักษะ)
"""

import csv
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GLOSS = re.compile(r"\s*\([^()]*[A-Za-z][^()]*\)")


def main() -> None:
    total = 0
    for p in sorted(Path("work/translate_parts_v2").rglob("*.csv")):
        rows = list(csv.DictReader(open(p, encoding="utf-8-sig", newline="")))
        changed = False
        for r in rows:
            t = r["thai"].strip()
            new = GLOSS.sub("", t).replace("  ", " ").strip()
            if new != t:
                r["thai"] = new
                changed = True
                total += 1
                print(f"{p.name}: {r['id']} {t[:45]!r} -> {new[:45]!r}")
        if changed:
            with open(p, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\r\n")
                w.writeheader()
                w.writerows(rows)
    print(f"stripped {total} rows")


if __name__ == "__main__":
    main()
