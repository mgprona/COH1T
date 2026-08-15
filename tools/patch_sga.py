import sys
import zlib
from pathlib import Path

# Ground truth from Essence.Core.dll (official Relic reader):
# each entry: data immediately follows its u32 CRC32 field in the TOC.
FONT_SLOTS = {
    # path in archive -> (file offset, store length, replacement source file)
    r"font\trebuc.ttf": (0x12092B73, 134108, r"font\Leelawad-PUA.ttf"),
    r"font\trebucbd.ttf": (0x120B3853, 123096, r"font\Leelawdb-PUA.ttf"),
    r"font\impact.ttf": (0x120716E3, 136076, r"font\Leelawad-PUA.ttf"),
}


def run(src: str, dst: str) -> None:
    data = bytearray(Path(src).read_bytes())
    for path, (off, length, replacement) in FONT_SLOTS.items():
        ttf = Path(replacement).read_bytes()
        assert len(ttf) <= length, f"{path}: {len(ttf)} > slot {length}"
        padded = ttf + b"\x00" * (length - len(ttf))
        assert data[off : off + 4] == b"\x00\x01\x00\x00", f"{path}: slot doesn't look like a TTF"
        data[off : off + length] = padded
        crc = zlib.crc32(padded) & 0xFFFFFFFF
        data[off - 4 : off] = crc.to_bytes(4, "little")
        print(f"patched {path}: {len(ttf)} bytes + {length - len(ttf)} pad, crc={crc:08X}")
    Path(dst).write_bytes(data)
    print(f"wrote {dst} ({len(data)} bytes)")


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else r"backup\Engine.sga"
    dst = sys.argv[2] if len(sys.argv) > 2 else r"work\Engine_patched.sga"
    run(src, dst)


if __name__ == "__main__":
    main()
