# Phase A — ระบบฟอนต์ PUA + Workflow การแปล (Design Spec)

วันที่: 2026-08-15
สถานะ: อนุมัติแล้ว (รอรีวิว spec)

## บริบท

Phase C สำเร็จแล้ว: เกมวาดอักษรไทยได้ผ่านฟอนต์ Leelawadee ที่แพตช์ใน `Engine.sga` แบบ in-place
(สล็อต `trebuc.ttf`/`trebucbd.ttf`/`impact.ttf` ไม่ต้องแก้ .fnt หรือ TOC)
แต่ Essence Engine 1.0 ไม่ทำ text shaping → สระบน/ล่างและวรรณยุกต์วางผิดตำแหน่ง
(สังเกต: คำที่ใช้สระฐาน/สระหน้าเท่านั้นดูปกติ เช่น "เมนู")

Phase A แก้ปัญหานี้ด้วยฟอนต์ PUA แบบ precomposed cluster ตามวิธีมาตรฐานวงการม็อด Relic

## ขอบเขต (รอบแรก)

- ข้อความเมนูหลัก (ID 713495–713560) + ที่แปลแล้ว (5256, 9250–9252)
- ฟอนต์ฐาน: Leelawadee UI (LeelawUI.ttf regular / LeelaUIb.ttf bold) — พิสูจน์แล้วว่า engine วาดได้
- ยังไม่ทำ: ข้อความในแมตช์, หน่วยรบ, chat — รอบถัดไป

## หลักการทำงาน

1. **Cluster analysis**: แตกข้อความไทยเป็น cluster = ตัวอักษรฐาน (พยัญชนะ/สระ) + combining marks ที่ตามมา
   (สระบน/ล่าง + วรรณยุกต์) สระหน้า เ แ โ ใ ไ เป็น glyph เดี่ยวอยู่แล้ว
   (engine เรียงซ้าย→ขวา เรนเดอร์ถูกตำแหน่งโดยธรรมชาติ)
2. **Precomposition**: แต่ละ cluster ที่ปรากฏจริง → 1 composite glyph ในช่วง PUA (U+E000 ขึ้นไป)
   ตำแหน่งของ mark ได้จาก HarfBuzz (uharfbuzz) shape ตาม GPOS ของ Leelawadee
3. **Encoding**: ข้อความไทยใน .ucs ถูกแปลงเป็นลำดับรหัส PUA ก่อนนำเข้าเกม
4. **Font deploy**: ฟอนต์ PUA แทนที่สล็อต ttf เดิมใน Engine.sga แบบ in-place (วิธีที่พิสูจน์แล้วใน Phase C)

## Components

### 1. `tools/pua_font_builder.py` — สร้างฟอนต์ PUA

- Input: `LeelawUI.ttf` / `LeelaUIb.ttf` (จาก C:\Windows\Fonts) + cluster list จากข้อความแปลแล้ว
- ใช้ `uharfbuzz` shape แต่ละ cluster (font size ปกติ) → ได้ glyph positions + advance
- ใช้ fontTools สร้าง composite glyph (base + marks ที่ offset ถูกต้อง) ใส่ cmap PUA
- Output: `font\LeelawUI-PUA.ttf`, `font\LeelaUIb-PUA.ttf`
- การ์ด cluster → PUA: อ่าน/เขียนจากไฟล์แมปที่แชร์กับ encoder (ดูข้อ 2)
- Self-check: เปิดฟอนต์ผลลัพธ์ด้วย fontTools ตรวจว่ามี glyph PUA ครบตามแมป
  และ bounding box ของ glyph cluster มี mark อยู่เหนือ/ใต้ base ตามที่คาด

### 2. `tools/ucs_workflow.py` — extract/apply ไฟล์แปล (ตัวเดียว 2 subcommand)

- `extract`:
  - อ่าน `.ucs` (UTF-16LE + CRLF + BOM)
  - เขียน `work\translate.csv` คอลัมน์: `id, english, thai, context`
  - `context` เติมจากความรู้ UI (ปุ่มเมนูหลัก / tooltip / ชื่อแคมเปญ / อื่นๆ) — ช่วย AI แปลรักษาบริบทเกม
- `apply`:
  - อ่าน `work\translate.csv`
  - ตรวจความสมบูรณ์: id มีอยู่, คอลัมน์ไม่เพี้ยน, ไฟล์ยัง UTF-16LE/CRLF/BOM
  - เข้ารหัสคอลัมน์ `thai` เป็น PUA ด้วย cluster map เดียวกับ font builder
    - cluster ที่ไม่อยู่ในแมป → เขียนตัวดิบ + เตือน "มี cluster ใหม่ N ชุด รัน pua_font_builder.py"
  - เขียน `.ucs` ใหม่ (คง format เดิม) → ทับ `work\` + โฟลเดอร์เกม

### 3. `tools/patch_sga.py` (ต่อยอดของเดิม)

- เพิ่มสล็อต PUA font เข้าแทน ttf เดิม 3 สล็อต (regular/bold/impact) ใน Engine.sga
- In-place + zero-pad + อัปเดต CRC32 (วิธีพิสูจน์แล้ว)
- ไม่แตะ TOC / .fnt / signature

## ข้อกำหนดร่วม

- Cluster map (cluster → PUA codepoint) เป็นไฟล์เดียวใน `work\` (เช่น `work\cluster_map.json`)
  font builder เขียน, encoder อ่าน — ทั้งสองส่วนต้องใช้แมปเดียวกันเสมอ
- ไฟล์ `.ucs` ต้องคง encoding UTF-16LE + CRLF + BOM ตลอด pipeline (เกม fatal ถ้าเพี้ยน — บทเรียนจากบั๊ก \r\r\n)
- มี assert/self-check กันการ corrupt (double-CR, PUA map ครบ, font เปิดได้)

## การไหลของงาน (คู่ขนาน)

```
ทีมแปล: work\translate.csv (แก้คอลัมน์ thai) ──┐
                                              ├─→ ucs_workflow apply → .ucs PUA → เกม
ทีม mod: Leelawadee ─→ pua_font_builder ─→ *-PUA.ttf ─→ patch_sga ─→ Engine.sga ─┘
```

ทีมแปลแปลไปเรื่อยๆ โดยไม่ต้องรอฟอนต์ ถ้ามี cluster ใหม่ → tool เตือน → ทีม mod รัน font builder ใหม่

## ความเสี่ยง/ข้อควรระวัง

- Composite offset ปัดเป็นจำนวนเต็ม font units → ค่าคลาดเคลื่อนเล็กน้อยระดับ subpixel ยอมรับได้
- ขนาดฟอนต์ PUA ต้องไม่เกินสล็อตเดิม (134,108 / 123,096 / 136,076 ไบต์) — composite เล็กมาก คาดว่าผ่านสบาย
- ห้ามแก้ไฟล์ในโฟลเดอร์เกมขณะ Steam/เกมเปิดอยู่
