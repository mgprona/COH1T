"""ลบคำอังกฤษซ้ำซ้อนในวงเล็บ (Operation Market Garden) ออกจากทุกไฟล์ translate_parts_v2."""

import csv
import sys
from pathlib import Path

PATTERN = " (Operation Market Garden)"


def main() -> None:
    total = 0
    for p in sorted(Path("work/translate_parts_v2").rglob("*.csv")):
        with open(p, encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
        changed = False
        for r in rows:
            t = r["thai"]
            if PATTERN in t:
                r["thai"] = t.replace(PATTERN, "")
                changed = True
                total += 1
                print(f"{p.name}: {r['id']} -> {r['thai'][:60]}")
        if changed:
            with open(p, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\r\n")
                w.writeheader()
                w.writerows(rows)
    print(f"cleaned {total} rows")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    main()
