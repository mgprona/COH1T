import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from fontTools.ttLib import TTFont

from tools.pua_encode import load_map
from tools.pua_font_builder import build_font

ROOT = Path(__file__).parent.parent
BASE = Path(r"C:\Windows\Fonts\leelawad.ttf")


def main() -> None:
    clusters = {"ล่", "ต่", "ผู้"}
    out = ROOT / "work" / "test_pua.ttf"
    map_path = ROOT / "work" / "test_map.json"
    m = build_font(BASE, clusters, out, map_path)
    assert m == load_map(map_path)
    assert sorted(m) == ["\u0e15\u0e48", "\u0e1c\u0e39\u0e49", "\u0e25\u0e48"]
    font = TTFont(out)
    cmap = font.getBestCmap() or {}
    glyf = font["glyf"]
    for c, cp in m.items():
        gname = cmap[cp]
        g = glyf[gname]
        assert g.numberOfContours == -1, f"{c}: not composite"
        assert len(g.components) == len(c), f"{c}: {len(g.components)} comps != {len(c)} chars"
    assert 0x0E01 in cmap, "original Thai cmap must remain"
    print("ok")


if __name__ == "__main__":
    main()
