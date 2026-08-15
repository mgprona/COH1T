import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.thai_cluster import is_thai, tokenize_clusters


def main() -> None:
    assert is_thai("ก") and is_thai("่") and not is_thai("A") and not is_thai(" ")
    assert tokenize_clusters("เมนูหลัก") == ["เ", "ม", "นู", "ห", "ลั", "ก"]
    assert tokenize_clusters("เล่นต่อ") == ["เ", "ล่", "น", "ต่", "อ"]
    assert tokenize_clusters("ผู้เล่นหลายคน") == ["ผู้", "เ", "ล่", "น", "ห", "ล", "า", "ย", "ค", "น"]
    assert tokenize_clusters("เก่ง") == ["เ", "ก่", "ง"]
    assert tokenize_clusters("ศึกรวดเร็ว") == ["ศึ", "ก", "ร", "ว", "ด", "เ", "ร็", "ว"]
    assert tokenize_clusters("Hello ไทย") == ["H", "e", "l", "l", "o", " ", "ไ", "ท", "ย"]
    print("ok")


if __name__ == "__main__":
    main()
