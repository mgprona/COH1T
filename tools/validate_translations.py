"""ตรวจคุณภาพงานแปล (placeholder ครบไหม, ละตินปน, coverage ราย section).

Usage: python -m tools.validate_translations <parts_dir> [out_report.md]
"""

import csv
import re
import sys
from pathlib import Path

PLACEHOLDER = re.compile(
    r"%\d+\$?[a-zA-Z%]+%?|%\d+[sdif]|\$[A-Za-z_]+|\[[a-z]:[^\]]*\]|\[b\]|\[/b\]"
)
LATIN = re.compile(r"[A-Za-z]{2,}")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    parts = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("work/validation_report.md")

    ph_broken: list[tuple[str, str, str, str]] = []
    latin: dict[str, int] = {}
    coverage: dict[str, tuple[int, int]] = {}
    for p in sorted(parts.rglob("*.csv")):
        total = translated = 0
        with open(p, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                total += 1
                e = row["english"]
                t = (row.get("thai") or "").strip()
                if t:
                    translated += 1
                if not t:
                    continue
                if re.findall(PLACEHOLDER, e) != re.findall(PLACEHOLDER, t):
                    ph_broken.append((str(p), row["id"], e[:60], t[:60]))
                if LATIN.search(t):
                    latin[str(p)] = latin.get(str(p), 0) + 1
        coverage[str(p)] = (translated, total)

    lines = [
        "# รายงานตรวจคุณภาพงานแปล",
        "",
        f"สแกน: {parts} — {len(coverage)} ไฟล์",
        "",
        "## Coverage รายไฟล์ (แปลแล้ว/ทั้งหมด)",
        "",
        "| ไฟล์ | แปลแล้ว | ทั้งหมด | % |",
        "|---|---|---|---|",
    ]
    for p, (tr, tot) in sorted(coverage.items()):
        lines.append(f"| {p} | {tr} | {tot} | {100 * tr // max(1, tot)}% |")
    lines += [
        "",
        f"## Placeholder ผิด/หาย ({len(ph_broken)} แถว) — ต้องแก้ก่อนเข้าสู่เกม",
        "",
        "| ไฟล์ | id | english | thai |",
        "|---|---|---|---|",
    ]
    for p, sid, e, t in ph_broken:
        lines.append(f"| {p} | {sid} | {e} | {t} |")
    lines += [
        "",
        f"## ไทยปนละติน (อาจตั้งใจ เช่น ชื่อเฉพาะ) — {sum(latin.values())} แถว",
        "",
    ]
    for p, n in sorted(latin.items(), key=lambda kv: -kv[1]):
        lines.append(f"- {p}: {n}")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"report -> {out}")
    print(f"placeholder broken: {len(ph_broken)}, latin-leak: {sum(latin.values())}")


if __name__ == "__main__":
    main()
