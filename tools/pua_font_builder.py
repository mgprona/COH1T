import csv
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent

from tools.pua_encode import PUA_START, collect_clusters, save_map

REGULAR = Path(r"work\BaiJamjuree-Regular.ttf")
BOLD = Path(r"work\BaiJamjuree-Bold.ttf")
OUT_DIR = Path("font")
CSV_PATH = Path("work/translate.csv")
MAP_PATH = Path("work/cluster_map.json")


def _comp(name: str, dx: int, dy: int) -> GlyphComponent:
    comp = GlyphComponent()
    comp.glyphName = name
    comp.flags = 0
    comp.x = dx
    comp.y = dy
    return comp


def build_font(base_ttf: Path, clusters: set[str], out_ttf: Path, map_path: Path) -> dict[str, int]:
    m = {c: PUA_START + i for i, c in enumerate(sorted(clusters))}
    font = TTFont(base_ttf)
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    cmap = font.getBestCmap() or {}
    for cluster, cp in m.items():
        base_name = cmap[ord(cluster[0])]
        cons_advance = hmtx[base_name][0]
        g = Glyph()
        g.numberOfContours = -1
        g.components = [_comp(base_name, 0, 0)]
        for mark in cluster[1:]:
            mark_name = cmap[ord(mark)]
            g.components.append(_comp(mark_name, cons_advance, 0))
        gname = f"pua{cp:X}"
        glyf[gname] = g
        hmtx[gname] = (cons_advance, 0)
        for table in font["cmap"].tables:
            if table.isUnicode():
                table.cmap[cp] = gname
    out_ttf.parent.mkdir(parents=True, exist_ok=True)
    font.save(out_ttf)
    save_map(map_path, m)
    return m


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass
    texts: list[str] = []
    if CSV_PATH.exists():
        with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                thai = (row.get("thai") or "").strip()
                if thai:
                    texts.append(thai)
    clusters = collect_clusters(texts)
    m = build_font(REGULAR, clusters, OUT_DIR / "BaiJamjuree-PUA.ttf", MAP_PATH)
    build_font(BOLD, clusters, OUT_DIR / "BaiJamjuree-Bold-PUA.ttf", MAP_PATH)
    print(f"built {len(clusters)} PUA glyphs into font/ (map -> {MAP_PATH})")
    print("map:", m)


if __name__ == "__main__":
    main()
