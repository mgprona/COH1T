# COH1T — ม็อดแปลไทย Company of Heroes 1 (Relaunch)

สถานะ: **Phase C สำเร็จ ✓ / Phase A สำเร็จ ✓** — เกมแสดงภาษาไทยสวยงาม สระ/วรรณยุกต์ถูกตำแหน่ง
(เมนูหลัก 52 บรรทัดแรกผ่านการตรวจบนเกมจริง 2026-08-15)

## สิ่งที่ค้นพบระหว่างทาง (สำคัญสำหรับคนทำต่อ)

| เรื่อง | ข้อเท็จจริง |
|---|---|
| ข้อความเกม | `CoH\Engine\Locale\English\RelicCOH.English.ucs` — UTF-16LE + BOM + CRLF (ห้าม double-CR เกม fatal!), รูปแบบ `id<TAB>text` |
| เมนูหลัก Relaunch | ใช้ string ID บล็อก **713495–713560** (ไม่ใช่ 9250 ของ CoH1 รุ่นเก่า) |
| ฟอนต์ | .fnt แค่ชี้ `file = "xxx.ttf"` ไม่มีตาราง range; **เกมอ่าน ttf จากใน .sga เท่านั้น** (วางหลวมไม่เวิร์ก); arialuni/segoeui ใช้ไม่ได้ (กล่องหมด) แต่ **Leelawadee ใช้ได้** |
| วิธีแพตช์ฟอนต์ | แทนที่เนื้อหา ttf สล็อตเดิมใน `Engine.sga` แบบ **in-place + zero-pad + อัปเดต CRC32** (ไม่ต้องแก้ TOC/.fnt/signature) — `tools/patch_sga.py` |
| การวาง mark ไทย | Leelawadee ฝังตำแหน่งสระ/วรรณยุกต์ไว้ใน contour ของ glyph เอง → PUA composite ต้องวาง mark ที่ `x = advance ของพยัญชนะ, y = 0` (วิธี naive แบบ ThaiPUA) ห้ามใช้ HarfBuzz anchor offsets |
| การรันเกม | ต้องรันจาก workdir = โฟลเดอร์เกม (ไม่งั้น RelicCOH.ini โหลดไม่เจอ); `-dev` อ่านไฟล์หลวมได้เฉพาะ .fnt ไม่ใช่ .ttf |

## Pipeline ปัจจุบัน (tools/)

```
[ทีมแปล] work/translate_parts/*.csv (แก้คอลัมน์ thai)
[ทีม mod]
  1. uv run python -m tools.pua_font_builder     # สร้าง font/Leelawad-PUA.ttf + Leelawdb-PUA.ttf + work/cluster_map.json
  2. uv run python -m tools.ucs_workflow apply work/translate.csv backup/RelicCOH.English.ucs work/RelicCOH.English.ucs work/cluster_map.json
  3. uv run python -m tools.patch_sga            # backup/Engine.sga -> work/Engine_patched.sga
  4. deploy: copy งาน 2 ไฟล์เข้าโฟลเดอร์เกม (ปิดเกมก่อน)
```

- ไฟล์ให้ทีมแปล: `work/translate_parts/` — 5 หมวด (`01_ui_menu` / `02_units_abilities` / `03_campaign_normandy` / `04_campaign_expansions` / `05_speech_radio`) คอลัมน์ `id,english,thai,context`; **id คือ key ตายตัว อย่าแตะ**
- ถ้า apply เตือน "new clusters" → รัน pua_font_builder ใหม่ก่อน (cluster ใหม่จากคำแปลใหม่)
- เทสต์: `uv run python tests/test_thai_cluster.py tests/test_pua_encode.py tests/test_pua_font_builder.py tests/test_ucs_workflow.py tests/test_patch_sga.py` / `uv run ruff check tools tests` / `uv run pyright tools tests`

## วิธีแพตช์ Engine.sga (ถ้าต้องทำใหม่จากศูนย์)

1. สำรอง: `RelicCOH.English.ucs` + `Engine.sga` → `backup\`
2. `uv run python -m tools.pua_font_builder` (ต้องการ `work/translate.csv` ที่มีคอลัมน์ thai)
3. `uv run python -m tools.patch_sga` → `work\Engine_patched.sga`
4. แทนที่ `Engine\Archives\Engine.sga` ในโฟลเดอร์เกม

## หมายเหตุ

- แก้ไฟล์ในโฟลเดอร์เกมไม่ได้ถ้าเกม/Steam เปิดอยู่
- เก็บงานใน `work\` เสมอ; `backup\` มีไฟล์ต้นฉบับ
- อ้างอิงเพิ่มเติม: `work/thaipua_ref` (ThaiPUA tool — แนวคิด composition + snap settings), `docs/superpowers/` (spec + plan + SDD ledger)
