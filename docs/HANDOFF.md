# COH1T — คู่มือส่งต่องาน (Handoff)

เอกสารนี้สำหรับ **AI/ทีมที่มารับช่วงต่อ** — อ่านให้จบก่อนทำอะไร ครอบคลุมทุกสิ่งที่ต้องรู้เพื่อสานต่อโปรเจกต์นี้ได้ทันที

## สถานะปัจจุบัน (16 ส.ค. 2026)

- **เกมแสดงภาษาไทยได้สมบูรณ์ทั้งเกม** — 22,629 ID แปลครบ 14,673 แถว (dedupe แล้ว), ฟอนต์ Bai Jamjuree + PUA 475 clusters
- Phase C (ฟอนต์ใช้ได้) + Phase A (PUA pipeline) เสร็จและเทสต์จริงในเกมแล้ว
- โครงสร้างงานแปล v2 (31 ไฟล์ แยก section) อยู่ใน `work/translate_parts_v2/` — **source of truth ของงานแปล**

## สิ่งที่ต้องมีบนเครื่องใหม่

1. **Python 3.12+** + `uv` → `uv sync` (ติดตั้ง fonttools, ruff, pyright)
2. **เกม Company of Heroes Relaunch** ติดตั้งแล้ว (Steam appid 228200)
3. ไฟล์ต้นฉบับจากเกม ก๊อปมาวางที่:
   - `<เกม>\CoH\Engine\Locale\English\RelicCOH.English.ucs` → `backup\RelicCOH.English.ucs`
   - `<เกม>\Engine\Archives\Engine.sga` → `backup\Engine.sga`

## Pipeline หลัก (เรียงตามลำดับใช้จริง)

```powershell
# 1. ฟอนต์ PUA (จากงานแปลปัจจุบัน)
uv run python -m tools.pua_font_builder
#    -> font/BaiJamjuree-PUA.ttf, font/BaiJamjuree-Bold-PUA.ttf, work/cluster_map.json

# 2. ใส่คำแปลลง .ucs (เข้ารหัส PUA + fallback ไทยดิบถ้ามี cluster ใหม่ + เตือน)
uv run python -m tools.ucs_workflow apply work/translate_parts_v2 backup/RelicCOH.English.ucs work/RelicCOH.English.ucs work/cluster_map.json

# 3. แพตช์ฟอนต์เข้า Engine.sga (in-place, อัปเดต CRC)
uv run python -m tools.patch_sga
#    -> work/Engine_patched.sga

# 4. Deploy ลงเกม (ปิดเกมก่อน!)
#    ก๊อป work/Engine_patched.sga -> <เกม>\Engine\Archives\Engine.sga
#    ก๊อป work/RelicCOH.English.ucs -> <เกม>\CoH\Engine\Locale\English\RelicCOH.English.ucs
```

**Stage เป็นงวดๆ** (ถ้าอยากทยอยลงเกมทีละหมวด): `uv run python -m tools.stage_round 01_ui 02_units ...` → แล้วใช้โฟลเดอร์ `work/staged` แทน `translate_parts_v2` ในขั้น 2 (แถวที่แตะ ID เมนูหลัก 713495-713561 จะถูกดึงมาด้วยเสมอ)

## งานแปลอยู่ไหน

- `work/translate_parts_v2/` — 31 csv แยกหมวด/section คอลัมน์ `id,english,thai,context,all_ids`
  - **กติกาทีมแปล**: `docs/translator-guide.md` (id/all_ids ห้ามแตะ, placeholder ต้องครบ, แยกแถวได้โดยแก้ all_ids)
  - **ศัพท์กลาง**: `docs/glossary.md`
- `tools/team/` — สคริปต์ตรวจ/เกลาของทีมแปล (ยกเว้นจาก lint — เกณฑ์คุณภาพของเจ้าของเอง)

## QA / ตรวจก่อน deploy

```powershell
Get-ChildItem tests\test_*.py | ForEach-Object { uv run python $_.FullName }   # 5 test files
uv run ruff check tools tests; uv run pyright tools tests
uv run python -m tools.validate_translations work/translate_parts_v2 work/validation_report.md
```

## ข้อเท็จจริงสำคัญ (อ่านก่อนแก้ — มาจากการทดลองจริง)

1. **ไฟล์ .ucs: UTF-16LE + CRLF + BOM เสมอ** — double-CR (`\r\r`) ทำให้เกม FATAL ตอนเปิด; มี assert กันใน read/write_ucs แล้ว ห้ามถอด
2. **เกมอ่านฟอนต์จากใน .sga เท่านั้น** — วางไฟล์หลวมไม่เวิร์ก; patch ในตำแหน่งเดิม (in-place) เท่านั้น
3. **สล็อตฟอนต์ 3 ช่อง** (trebuc/trebucbd/impact) — offsets/sizes คงที่ใน `tools/patch_sga.py` ห้ามเลื่อน
4. **ฟอนต์ Bai Jamjuree ต้องเป็น naive-positioning** (mark contour ฝังตำแหน่ง) — ห้ามใช้ HarfBuzz/GPOS offsets วาง mark (บทเรียนจากประวัติ commit); ฟอนต์ใหม่ต้องเช็กด้วย `tools/diag_font_style.py` ก่อน
5. **ห้ามปรับสเกลฟอนต์ (upem)** — ลองแล้ว (commit 2d5e647) ดูแย่กว่าเดิม revert แล้ว (f05476f)
6. **"Belgrade" ในแช็ต = ชื่อช่องจากเซิร์ฟเวอร์** — ไม่อยู่ใน ucs แปลไม่ได้ ไม่ใช่บั๊ก
7. รันเกมจากโฟลเดอร์เกมเท่านั้น (RelicCOH.ini โหลดไม่เจอถ้า workdir ผิด)

## Known issues (ยังไม่แก้ — งานคิวถัดไป)

- **ฟอนต์ชั้น 3 (impact slot) บางคำ "ซ้อน"** — ผู้ใช้รายงาน 16 ส.ค. ยังไม่ได้สืบสาเหตุ; สงสัย advance ของ composite ในปุ่ม/หัวเรื่อง — จดคำ+หน้าจอที่เจอตอนสืบ
- ขนาดฟอนต์รวม 102KB ยังพอดีสล็อต 134KB แต่ถ้า cluster เกิน ~700 ตัวจะล้น → แผนสำรอง: ลงช่อง arialuni.ttf (23MB) + patch .fnt ชี้ไป (ยังไม่ได้ทำ)

## โครงสร้าง repo ย่อ

```
tools/           pipeline (ucs_workflow, pua_font_builder, patch_sga, thai_cluster, pua_encode, ucs_sections, stage_round, validate_translations, diag_*)
tools/team/      สคริปต์ทีมแปล (excluded จาก lint)
tests/           5 ไฟล์ test แบบ plain python
docs/            specs, plans, translator-guide, glossary, release-plan, HANDOFF.md
work/translate_parts_v2/   งานแปล (tracked ใน git)
backup/, font/, work/อื่นๆ  generated — ไม่ track
```
