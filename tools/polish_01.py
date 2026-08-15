"""เกลา 01_ui: ลบวงเล็บ gloss อังกฤษท้ายประโยค + normalize double-space + แก้ FSAA."""

import csv
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("work/translate_parts_v2/01_ui")
LATIN_PAREN = re.compile(r"\s*\([A-Za-z0-9 &'\-\.:/]+\)\s*$")
FIXES = {"FSAA": "FSAA"}


def main() -> None:
    total = 0
    for p in sorted(ROOT.rglob("*.csv")):
        rows = list(csv.DictReader(open(p, encoding="utf-8-sig", newline="")))
        changed = False
        for r in rows:
            t = r["thai"].strip()
            new = t
            new = LATIN_PAREN.sub("", new)
            new = new.replace("  ", " ")
            if r["english"].strip() in FIXES and t != FIXES[r["english"].strip()]:
                new = FIXES[r["english"].strip()]
            if new != t:
                r["thai"] = new
                changed = True
                total += 1
                print(f"{p.name}: {r['id']} {t[:50]!r} -> {new[:50]!r}")
        if changed:
            with open(p, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\r\n")
                w.writeheader()
                w.writerows(rows)
    print(f"polished {total} rows")


if __name__ == "__main__":
    main()
