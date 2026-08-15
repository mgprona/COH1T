import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.ucs_sections import SECTIONS, section_of


def _load_ucs() -> dict[int, str]:
    with open(r"backup\RelicCOH.English.ucs", encoding="utf-16") as fh:
        lines = fh.read().splitlines()
    entries: dict[int, str] = {}
    for l in lines:
        if not l:
            continue
        sid, _, v = l.partition("\t")
        if sid.isdigit():
            entries[int(sid)] = v
    return entries


def main() -> None:
    entries = _load_ucs()
    # 1) ทุก id ต้องจำแนกได้ และ map ไป section เดียว (คำนวณซ้ำได้ deterministic)
    counts: dict[str, int] = {}
    for sid, english in entries.items():
        sec = section_of(sid, english)
        assert section_of(sid, english).key == sec.key
        counts[sec.category + "/" + sec.key] = counts.get(sec.category + "/" + sec.key, 0) + 1
    assert sum(counts.values()) == len(entries), f"covered {sum(counts.values())} != {len(entries)}"
    # 2) sections ที่ kind=None ต้องมี range ไม่ซ้อนกัน
    plain = [(s.key, s.ranges) for s in SECTIONS if s.kind is None]
    for i, (k1, r1) in enumerate(plain):
        for k2, r2 in plain[i + 1 :]:
            for lo1, hi1 in r1:
                for lo2, hi2 in r2:
                    assert not (lo1 < hi2 and lo2 < hi1), f"overlap: {k1}{r1} vs {k2}{r2}"
    # 3) filenames unique + category/key unique
    keys = [(s.category, s.key) for s in SECTIONS]
    assert len(keys) == len(set(keys)), "duplicate category/key"
    files = [s.file for s in SECTIONS]
    assert len(files) == len(set(files)), "duplicate file names"
    print(f"ok — {len(entries)} ids, {len(SECTIONS)} sections")
    for k, n in sorted(counts.items()):
        print(f"  {k}: {n}")


if __name__ == "__main__":
    main()
