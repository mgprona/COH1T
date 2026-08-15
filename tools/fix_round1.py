import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

FIXES: dict[str, dict[str, str]] = {
    # file -> {english-substring: new thai}
    "work/translate_parts_v2/01_ui/05_lobby.csv": {
        "Relic Online Login": "เข้าสู่ระบบ Relic Online",
    },
    "work/translate_parts_v2/04_expansions/03_tiger_ace.csv": {
        "Crush all the civilian vehicles": "ทำลายยานพาหนะพลเรือนให้หมด แล้วฉันจะให้มาร์คสิบอัน!",
        "May God have mercy": "ขอพระเจ้าเมตตาผู้ที่หนีไปด้วย",
    },
    "work/translate_parts_v2/03_normandy/m05_redball.csv": {
        "Squads from Dog Company": "หมู่รบจากกองร้อยด็อกกำลังถูกยิงตรึงกำลัง จงกำจัดทหารฝ่ายอักษะทั้งหมดในพื้นที่",
    },
}


def main() -> None:
    total_fixed = 0
    for path, subs in FIXES.items():
        p = Path(path)
        with open(p, encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
        fieldnames = list(rows[0].keys()) if rows else []
        fixed = 0
        for r in rows:
            for sub, new_thai in subs.items():
                if sub.lower() in r["english"].lower() and r["thai"].strip() != new_thai:
                    r["thai"] = new_thai
                    fixed += 1
                    print(f"{p.name}: {r['id']} {r['english'][:40]!r} -> {new_thai!r}")
        if fixed:
            with open(p, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\r\n")
                w.writeheader()
                w.writerows(rows)
        total_fixed += fixed
    print(f"fixed {total_fixed} rows")


if __name__ == "__main__":
    main()
