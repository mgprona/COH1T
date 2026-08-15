import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent.parent


def main() -> None:
    import tools.patch_sga as ps

    # monkeypatch: ใช้ฟอนต์ระบบแทน *-PUA.ttf (ยังไม่ถูก build ใน task นี้)
    for key in ps.FONT_SLOTS:
        off, length, _ = ps.FONT_SLOTS[key]
        ps.FONT_SLOTS[key] = (off, length, r"C:\Windows\Fonts\leelawad.ttf")

    # สร้าง sga จำลอง: zero-filled จนครอบ slot สุดท้าย + 3 slot ttf + crc ก่อนแต่ละ slot
    max_end = max(off + length for off, length, _ in ps.FONT_SLOTS.values())
    data = bytearray(b"\x00" * max_end)
    fake = Path(r"C:\Windows\Fonts\leelawad.ttf").read_bytes()

    def place(slot_off: int, length: int) -> None:
        data[slot_off - 4 : slot_off] = zlib.crc32(fake).to_bytes(4, "little")
        data[slot_off : slot_off + length] = fake + b"\x00" * (length - len(fake))

    place(ps.FONT_SLOTS[r"font\trebuc.ttf"][0], ps.FONT_SLOTS[r"font\trebuc.ttf"][1])
    place(ps.FONT_SLOTS[r"font\trebucbd.ttf"][0], ps.FONT_SLOTS[r"font\trebucbd.ttf"][1])
    place(ps.FONT_SLOTS[r"font\impact.ttf"][0], ps.FONT_SLOTS[r"font\impact.ttf"][1])
    src = ROOT / "work" / "test_src.sga"
    dst = ROOT / "work" / "test_dst.sga"
    src.write_bytes(data)
    ps.run(str(src), str(dst))
    out = dst.read_bytes()
    for path, (off, length, _repl) in ps.FONT_SLOTS.items():
        slot = out[off : off + length]
        assert slot[:4] == b"\x00\x01\x00\x00", f"{path}: slot not patched"
        assert zlib.crc32(slot) & 0xFFFFFFFF == int.from_bytes(out[off - 4 : off], "little")
    src.unlink(missing_ok=True)
    dst.unlink(missing_ok=True)
    print("ok")


if __name__ == "__main__":
    main()
