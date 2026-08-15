import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.ucs_workflow import extract, read_ucs, write_ucs

ROOT = Path(__file__).parent.parent


def _make_ucs(path: Path, entries: dict[int, str]) -> None:
    lines = [f"{i}\t{t}" for i, t in sorted(entries.items())]
    with open(path, "w", encoding="utf-16", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")


def main() -> None:
    base = ROOT / "work" / "test_base.ucs"
    cur = ROOT / "work" / "test_cur.ucs"
    csv = ROOT / "work" / "test_out.csv"
    _make_ucs(base, {713512: "CAMPAIGN", 713513: "Continue", 5256: "MAIN MENU"})
    _make_ucs(cur, {713512: "แคมเปญ", 713513: "Continue", 5256: "MAIN MENU"})
    n = extract(base, cur, csv)
    assert n == 52, n
    content = csv.read_text(encoding="utf-8-sig").splitlines()
    assert content[0] == "id,english,thai,context"
    assert "713512,CAMPAIGN,แคมเปญ,ปุ่มเมนูหลัก: แคมเปญ" in content
    assert "713513,Continue,,tooltip ต่อแคมเปญนอร์มังดี" in content
    assert "5256,MAIN MENU,,เมนูเก่า: เมนูหลัก" in content
    entries = read_ucs(cur)
    assert entries[713512] == "แคมเปญ"
    out = ROOT / "work" / "test_rewrite.ucs"
    write_ucs(out, entries)
    assert read_ucs(out) == entries
    raw = out.read_bytes()
    assert raw[:2] == b"\xff\xfe"
    assert b"\r\r" not in raw and b"\r\x00\n\x00" in raw

    # extract_categories: ทุก id ตกหลุมไหนสักหมวด และไม่มีซ้ำ
    from tools.ucs_workflow import CATEGORY_RANGES, extract_categories

    big_base = ROOT / "work" / "test_big_base.ucs"
    big_cur = ROOT / "work" / "test_big_cur.ucs"
    all_ids: dict[int, str] = {}
    for cat, ranges in CATEGORY_RANGES.items():
        for lo, hi in ranges:
            all_ids[lo] = f"cat {cat} lo"
            all_ids[hi - 1] = f"cat {cat} hi"
    _make_ucs(big_base, all_ids)
    _make_ucs(big_cur, all_ids)
    cats_dir = ROOT / "work" / "test_cats"
    counts = extract_categories(big_base, big_cur, csv, cats_dir)
    assert sum(counts.values()) == len(all_ids)
    seen: set[int] = set()
    for cat in CATEGORY_RANGES:
        p = cats_dir / f"{cat}.csv"
        content = p.read_text(encoding="utf-8-sig").splitlines()
        assert content[0] == "id,english,thai,context"
        for line in content[1:]:
            sid = int(line.split(",")[0])
            assert sid not in seen, f"duplicate id {sid}"
            seen.add(sid)
    assert seen == set(all_ids)
    print("ok")


if __name__ == "__main__":
    main()
