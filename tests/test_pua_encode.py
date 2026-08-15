import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.pua_encode import PUA_START, collect_clusters, encode, load_map, save_map


def main() -> None:
    clusters = collect_clusters(["เล่นต่อเกม", "ผู้เล่นหลายคน"])
    assert clusters == {"ล่", "ต่", "ผู้"}
    m = {c: PUA_START + i for i, c in enumerate(sorted(clusters))}
    tmp = Path("work/test_map.json")
    save_map(tmp, m)
    assert load_map(tmp) == m
    assert json.loads(tmp.read_text(encoding="utf-8")) == {
        c: PUA_START + i for i, c in enumerate(sorted(clusters))
    }
    out, missing = encode("เล่นต่อ", m)
    assert missing == set()
    assert out == f"\u0e40{chr(m['ล่'])}น{chr(m['ต่'])}อ"
    out2, missing2 = encode("เล่นต่อเก่ง", m)
    assert missing2 == {"ก่"}
    assert "เก่ง" in out2  # fallback เป็นตัวดิบ
    tmp.unlink(missing_ok=True)
    print("ok")


if __name__ == "__main__":
    main()
