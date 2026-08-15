"""ปั้น work/staged ตามงวด: รวมโฟลเดอร์หมวดที่เลือก + แถวที่แตะ ID เมนูหลักเสมอ.

Usage: python -m tools.stage_round <category_folder> [<category_folder> ...]
"""

import csv
import shutil
import sys
from pathlib import Path

ROOT = Path("work/translate_parts_v2")
STAGED = Path("work/staged")
FE_IDS = range(713495, 713561)


def main() -> None:
    cats = sys.argv[1:]
    if STAGED.exists():
        shutil.rmtree(STAGED)
    STAGED.mkdir(parents=True)
    for cat in cats:
        shutil.copytree(ROOT / cat, STAGED / cat)
    fe_rows: dict[str, list[dict]] = {}
    for p in sorted(ROOT.rglob("*.csv")):
        with open(p, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                ids = [int(t) for t in (r.get("all_ids") or "").split("|") if t.isdigit()]
                if any(sid in FE_IDS for sid in ids):
                    fe_rows.setdefault(p.name, []).append(r)
    for name, rows in fe_rows.items():
        out = STAGED / "_fe_extra" / name
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\r\n")
            w.writeheader()
            w.writerows(rows)
        print(f"FE rows -> staged/_fe_extra/{name}: {len(rows)}")
    print(f"staged: {cats} + FE extras")


if __name__ == "__main__":
    main()
