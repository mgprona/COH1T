import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FONTS = [
    (r"C:\Windows\Fonts\leelawad.ttf", "Leelawadee"),
    (r"C:\Windows\Fonts\LeelawUI.ttf", "Leelawadee UI"),
    (r"C:\Windows\Fonts\tahoma.ttf", "Tahoma"),
    (r"C:\Windows\Fonts\upcil.ttf", "AngsanaUPC"),
    (r"C:\Windows\Fonts\upcll.ttf", "Angsana New"),
    (r"C:\Windows\Fonts\upcdl.ttf", "DilleniaUPC"),
]

MARKS = {"ิ": "uni0E34", "่": "uni0E48", "ู": "uni0E39"}


def main() -> None:
    for path, label in FONTS:
        p = Path(path)
        if not p.exists():
            print(f"{label}: (ไม่มีไฟล์)")
            continue
        font = TTFont(p)
        gs = font.getGlyphSet()
        cmap = font.getBestCmap()
        verdict = "naive ✓"
        for name, uni in MARKS.items():
            gname = cmap.get(int(uni[3:], 16))
            if gname is None or gname not in gs:
                verdict = f"ไม่มี glyph {name}"
                break
            bp = BoundsPen(gs)
            gs[gname].draw(bp)
            b = bp.bounds
            if b[0] >= 0 and name in ("ิ", "่"):
                verdict = f"GPOS-pure ({name} xMin={b[0]})"
                break
        print(f"{label}: {verdict}")


if __name__ == "__main__":
    main()
