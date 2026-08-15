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
    print("ok")


if __name__ == "__main__":
    main()
