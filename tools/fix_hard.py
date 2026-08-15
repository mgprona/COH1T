"""แก้เฉพาะจุด: Hard (ระดับความยาก) -> ยาก"""

import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = Path("work/translate_parts_v2/01_ui/01_system.csv")


def main() -> None:
    rows = list(csv.DictReader(open(P, encoding="utf-8-sig", newline="")))
    for r in rows:
        if r["id"] in ("1702", "12508") and r["english"].strip() in ("Hard", "HARD"):
            r["thai"] = "ยาก"
            print(r["id"], repr(r["thai"]))
    with open(P, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)
    print("fixed")


if __name__ == "__main__":
    main()
