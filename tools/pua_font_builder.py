import csv
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent

from tools.pua_encode import PUA_START, collect_clusters, save_map

REGULAR = Path(r"C:\Windows\Fonts\leelawad.ttf")
BOLD = Path(r"C:\Windows\Fonts\leelawdb.ttf")
OUT_DIR = Path("font")
CSV_PATH = Path("work/translate.csv")
MAP_PATH = Path("work/cluster_map.json")


def build_font(base_ttf: Path, clusters: set[str], out_ttf: Path, map_path: Path) -> dict[str, int]:
    m = {c: PUA_START + i for i, c in enumerate(sorted(clusters))}
    font = TTFont(base_ttf)
    order = font.getGlyphOrder()
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    face = hb.Face(base_ttf.read_bytes())  # type: ignore[attr-defined]
    hbfont = hb.Font(face)  # type: ignore[attr-defined]
    for cluster, cp in m.items():
        buf = hb.Buffer()  # type: ignore[attr-defined]
        buf.add_str(cluster)
        buf.guess_segment_properties()
        hb.shape(hbfont, buf)  # type: ignore[attr-defined]
        positions = buf.glyph_positions
        infos = buf.glyph_infos
        gname = f"pua{cp:X}"
        g = Glyph()
        g.numberOfContours = -1
        g.components = []
        for info, pos in zip(infos, positions):
            comp_name = order[info.codepoint]
            comp = GlyphComponent()
            comp.glyphName = comp_name
            comp.flags = 0
            comp.x = round(pos.x_offset)
            comp.y = round(pos.y_offset)
            g.components.append(comp)
        glyf[gname] = g
        hmtx[gname] = (round(sum(p.x_advance for p in positions)), 0)
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
    m = build_font(REGULAR, clusters, OUT_DIR / "Leelawad-PUA.ttf", MAP_PATH)
    build_font(BOLD, clusters, OUT_DIR / "Leelawdb-PUA.ttf", MAP_PATH)
    print(f"built {len(clusters)} PUA glyphs into font/ (map -> {MAP_PATH})")
    print("map:", m)


if __name__ == "__main__":
    main()
