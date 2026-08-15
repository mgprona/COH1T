"""สร้าง binary patch ระหว่าง Engine.sga ต้นฉบับ กับที่แพตช์แล้ว -> work/patch.json

patch.json = {vanilla_sha256, patched_sha256, blocks: [[offset, base64], ...]}
blocks = ช่วง byte ที่ต่างกัน (merge ช่องว่าง < 64B)
"""

import base64
import hashlib
import json
import sys
from pathlib import Path

VANILLA = Path("backup/Engine.sga")
PATCHED = Path("work/Engine_patched.sga")
OUT = Path("work/patch.json")
MERGE_GAP = 64


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def diff_ranges(a: bytes, b: bytes) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start = None
    for i in range(len(a)):
        if a[i] != b[i]:
            if start is None:
                start = i
        elif start is not None:
            ranges.append((start, i))
            start = None
    if start is not None:
        ranges.append((start, len(a)))
    merged: list[tuple[int, int]] = []
    for s, e in ranges:
        if merged and s - merged[-1][1] < MERGE_GAP:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    return merged


def main() -> None:
    a = VANILLA.read_bytes()
    b = PATCHED.read_bytes()
    assert len(a) == len(b), "sizes differ"
    blocks = [[off, base64.b64encode(b[off:end]).decode()] for off, end in diff_ranges(a, b)]
    total = sum(len(base64.b64decode(blk)) for _, blk in blocks)
    payload = {
        "vanilla_sha256": sha256(VANILLA),
        "patched_sha256": sha256(PATCHED),
        "blocks": blocks,
    }
    OUT.write_text(json.dumps(payload), encoding="utf-8")
    print(f"blocks: {len(blocks)}, patched bytes: {total:,}, json size: {OUT.stat().st_size:,}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
