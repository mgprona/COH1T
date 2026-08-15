import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from fontTools.ttLib import TTFont

from tools.pua_encode import load_map
from tools.pua_font_builder import build_font

ROOT = Path(__file__).parent.parent
BASE = Path(r"C:\Windows\Fonts\leelawad.ttf")


def main() -> None:
    clusters = {"ลื", "ผู้"}
    out = ROOT / "work" / "test_pua.ttf"
    map_path = ROOT / "work" / "test_map.json"
    m = build_font(BASE, clusters, out, map_path)
    assert m == load_map(map_path)
    font = TTFont(out)
    cmap = font.getBestCmap() or {}
    glyf = font["glyf"]
    hmtx = font["hmtx"]

    ลื = glyf[cmap[m["ลื"]]]
    assert len(ลื.components) == 2
    c0, c1 = ลื.components
    assert (c0.glyphName, c0.x, c0.y) == ("uni0E25", 0, 0)
    assert (c1.glyphName, c1.x, c1.y) == ("uni0E37", 1104, 0)
    assert hmtx[cmap[m["ลื"]]][0] == 1104

    ผู้ = glyf[cmap[m["ผู้"]]]
    assert len(ผู้.components) == 3
    b, v1, v2 = ผู้.components
    assert (b.glyphName, b.x, b.y) == ("uni0E1C", 0, 0)
    assert (v1.glyphName, v1.x, v1.y) == ("uni0E39", 1225, 0)
    assert (v2.glyphName, v2.x, v2.y) == ("uni0E49", 1225, 0)
    assert hmtx[cmap[m["ผู้"]]][0] == 1225
    assert 0x0E01 in cmap, "original Thai cmap must remain"
    out.unlink(missing_ok=True)
    map_path.unlink(missing_ok=True)
    print("ok")


if __name__ == "__main__":
    main()
