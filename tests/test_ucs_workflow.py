import sys
from csv import DictReader
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

    # read-side double-CR guard ต้องยิงจริง (universal newline translation ต้องไม่ทำลายหลักฐาน)
    bad = ROOT / "work" / "test_bad.ucs"
    with open(bad, "w", encoding="utf-16", newline="") as f:
        f.write("5256\tMAIN MENU\r\r\n")
    try:
        read_ucs(bad)
        raise AssertionError("double-CR guard did not fire")
    except AssertionError as e:
        assert "corruption detected" in str(e)

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

    # merge_parts: รวม part csvs + menu csv กลับเป็น csv เดียว
    from tools.ucs_workflow import merge_parts

    parts_dir = ROOT / "work" / "test_merge_parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    (parts_dir / "01_a.csv").write_text(
        "id,english,thai,context\r\n1,ONE,,c1\r\n2,TWO,,c2\r\n", encoding="utf-8-sig"
    )
    (parts_dir / "02_b.csv").write_text(
        "id,english,thai,context\r\n3,THREE,สาม,c3\r\n", encoding="utf-8-sig"
    )
    menu = ROOT / "work" / "test_merge_menu.csv"
    menu.write_text("id,english,thai,context\r\n1,,หนึ่ง,\r\n", encoding="utf-8-sig")
    merged = ROOT / "work" / "test_merged.csv"
    rows, translated = merge_parts(parts_dir, menu, merged)
    assert rows == 3, rows
    assert translated == 2, translated
    by_id = {r["id"]: r for r in DictReader(merged.read_text(encoding="utf-8-sig").splitlines())}
    assert by_id["1"]["thai"] == "หนึ่ง"
    assert by_id["2"]["thai"] == ""
    assert by_id["3"]["thai"] == "สาม"

    # ต่อท้าย main() เดิม
    from tools.pua_encode import PUA_START, save_map
    from tools.ucs_workflow import apply

    m = {"ล่": PUA_START, "ต่": PUA_START + 1}
    save_map(ROOT / "work" / "test_cmap.json", m)
    csv2 = ROOT / "work" / "test_translate.csv"
    csv2.write_text(
        "id,english,thai,context\r\n713512,CAMPAIGN,เล่นต่อ,\r\n713513,Continue,ต่อเก่ง,\r\n",
        encoding="utf-8-sig",
    )
    out2 = ROOT / "work" / "test_applied.ucs"
    warnings = apply(csv2, base, out2, ROOT / "work" / "test_cmap.json")
    entries = read_ucs(out2)
    assert entries[713512] == f"\u0e40{chr(PUA_START)}น{chr(PUA_START + 1)}อ"
    assert entries[713513] == "ต่อเก่ง"  # เก่ง มี cluster ใหม่ -> fallback ดิบ
    assert any("ก่" in w for w in warnings)
    assert entries[5256] == "MAIN MENU"  # ไม่ได้แปล -> คงต้นฉบับ

    # ทำความสะอาด test artifacts
    import shutil

    shutil.rmtree(cats_dir, ignore_errors=True)
    shutil.rmtree(parts_dir, ignore_errors=True)
    for p in [
        base,
        cur,
        csv,
        out,
        bad,
        big_base,
        big_cur,
        csv2,
        out2,
        menu,
        merged,
        ROOT / "work" / "test_cmap.json",
    ]:
        p.unlink(missing_ok=True)
    print("ok")


if __name__ == "__main__":
    main()
