import zlib
from pathlib import Path

# Ground truth from Essence.Core.dll (official Relic reader):
# each entry: data immediately follows its u32 CRC32 field in the TOC.
FONT_SLOTS = {
    # path in archive -> (file offset, store length, replacement source file)
    r"font\trebuc.ttf": (0x12092B73, 134108, r"C:\Windows\Fonts\leelawad.ttf"),
    r"font\trebucbd.ttf": (0x120B3853, 123096, r"C:\Windows\Fonts\leelawdb.ttf"),
    r"font\impact.ttf": (0x120716E3, 136076, r"C:\Windows\Fonts\leelawad.ttf"),
}

SRC = Path(r"backup\Engine.sga")
DST = Path(r"work\Engine_patched.sga")


def main() -> None:
    data = bytearray(SRC.read_bytes())
    for path, (off, length, replacement) in FONT_SLOTS.items():
        ttf = Path(replacement).read_bytes()
        assert len(ttf) <= length, f"{path}: {len(ttf)} > slot {length}"
        padded = ttf + b"\x00" * (length - len(ttf))
        assert data[off : off + 4] == b"\x00\x01\x00\x00", f"{path}: slot doesn't look like a TTF"
        data[off : off + length] = padded
        crc = zlib.crc32(padded) & 0xFFFFFFFF
        data[off - 4 : off] = crc.to_bytes(4, "little")
        print(f"patched {path}: {len(ttf)} bytes + {length - len(ttf)} pad, crc={crc:08X}")
    DST.write_bytes(data)
    print(f"wrote {DST} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
