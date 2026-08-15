# COH1T — ม็อดแปลไทย Company of Heroes 1 (Legacy/Relaunch)

## เป้าหมาย

ม็อดแปลไทย CoH1 ใช้เองก่อน (ขอบเขตเริ่ม: UI / เมนู / หน่วยรบ แปลมือล้วน)
เส้นทาง: **Phase C** (ทดสอบฟอนต์ไทยธรรมดา) → ถ้าสระลอยค่อยไป **Phase A** (ฟอนต์ PUA)

## ข้อมูลเกมที่สำรวจแล้ว (ข้อเท็จจริงจากเครื่องนี้)

เกม: `C:\Program Files (x86)\Steam\steamapps\common\Company of Heroes Relaunch` (appid 228200)

| เรื่อง | ข้อเท็จจริง |
|---|---|
| ไฟล์ข้อความ | `CoH\Engine\Locale\English\RelicCOH.English.ucs` — ไฟล์หลวม 2.1 MB, เข้ารหัส UTF-16LE (ขึ้นต้น FF FE), รูปแบบ `id<TAB>text` ต่อบรรทัด แก้ด้วย VS Code/Notepad++ ได้เลย |
| ฟอนต์ | อยู่ใน `Engine\Archives\Engine.sga` (350 MB) โฟลเดอร์ `font\`: `arialuni.ttf` (23 MB, **มี glyph ไทยอยู่แล้ว**), `trebuc.ttf`, `trebucbd.ttf`, `impact.ttf` + ไฟล์ `.fnt` (config ช่วงรหัสอักขระแต่ละฟอนต์/ขนาด เช่น `trebuchet ms regular 12.fnt`) |
| ไฟล์หลอก | `EngineEnglish.sga`, `WW2\Archives\WW2Locale-English.sga` มีขนาด 0 ไบต์ (placeholder) — ข้อความไม่ได้อยู่ตรงนั้น |
| ภาษา | `Locale.ini` ตั้ง `lang = english` — ระบบเลือกภาษาแบบเก่าไม่ใช้; แก้ .ucs โดยตรงแทน |
| เครื่องมือแพ็ก | `Archive.exe` อยู่ในโฟลเดอร์เกม (ใช้ได้เลย ไม่ต้องหาโหลด) |

### คำสั่ง Archive.exe (ตรวจสอบแล้ว)

```powershell
$A = "C:\Program Files (x86)\Steam\steamapps\common\Company of Heroes Relaunch\Archive.exe"

# ดูรายการไฟล์ใน .sga
& $A -a "<file.sga>" -l

# แกะทั้ง archive ลงโฟลเดอร์
& $A -a "<file.sga>" -e "<โฟลเดอร์ปลายทาง>"

# สร้าง .sga ใหม่ (listfile = รายชื่อไฟล์ บรรทัดละไฟล์)
& $A -a "<out.sga>" -c "<listfile.txt>" -r "<โฟลเดอร์รากของไฟล์>"
```

## โครงสร้างโฟลเดอร์

```
COH1T\
├── README.md     ← ไฟล์นี้
├── backup\       ← สำรองต้นฉบับ (RelicCOH.English.ucs, Engine.sga) ก่อนแก้ทุกครั้ง
├── work\         ← ไฟล์แกะจาก .sga, ไฟล์ .ucs ที่กำลังแก้, ผลลัพธ์
├── font\         ← ฟอนต์ไทย + งานปรับฟอนต์ (PUA)
└── tools\        ← สคริปต์ช่วย (แปลง ucs↔csv, เข้ารหัส PUA, ฯลฯ)
```

## Phase C — ทดสอบฟอนต์ไทยธรรมดา (ทำก่อนเสมอ)

เหตุผล: `arialuni.ttf` ในเกมมี glyph ไทยครบ (U+0E00–0E7F) จึงมีโอกาสที่แค่
เปิดช่วงรหัสใน `.fnt` แล้วเกมจะวาดไทยได้ — ใช้เวลา ~30 นาที ถ้าได้ก็จบ ไม่ต้องทำ PUA
(ความเสี่ยงหลัก: Essence Engine 1.0 ไม่มี text shaping → สระ/วรรณยุกต์ลอย)

ขั้นตอน:

1. **สำรอง** — คัดลอก `RelicCOH.English.ucs` และ `Engine.sga` ไว้ใน `backup\`
2. **แกะฟอนต์** — `Archive.exe -a Engine.sga -e work\engine_extracted`
3. **อ่าน .fnt** — เปิด `work\engine_extracted\font\trebuchet ms regular 12.fnt` (และพี่น้อง) ดูว่า format กำหนดช่วงรหัสยังไง (น่าจะเป็นตาราง `unicode_range` / list ของช่วง) จดไว้ในนี้
4. **เพิ่มช่วงไทย** — เพิ่ม `U+0E00–U+0E7F` ลงใน .fnt ที่ใช้กับ arialuni.ttf (หรือทุก .fnt ที่ UI ใช้) — ถ้า .fnt ผูกกับฟอนต์เฉพาะ ให้ใช้ arialuni.ttf เป็นตัวหลัก
5. **ทดสอบข้อความ** — แก้ `RelicCOH.English.ucs` เปลี่ยนข้อความเมนูหลักสัก 1-2 บรรทัดเป็นไทย (บันทึก UTF-16LE พร้อม BOM)
6. **รันเกม** — `RelicCOH.exe` ดูเมนูหลักว่าไทยแสดงผลยังไง
   - ตัวอักษรขึ้น แต่สระลอย/วรรณยุกต์ลอย → ยืนยันว่า engine ไม่ทำ shaping → ไป Phase A
   - ขึ้นสวยไม่ลอย → โชคดีมาก ข้าม Phase A ได้เลย
7. **คืนสภาพ** — เอาไฟล์ใน `backup\` ทับกลับ

จุดที่ยังไม่รู้ (ต้องทดลอง): เกมอ่านฟอนต์จาก loose folder (โฟลเดอร์ไหน) หรือต้องแพ็กกลับ .sga —
จะทดลองวาง `font\` เป็นไฟล์หลวมในโฟลเดอร์เกมก่อน ถ้าไม่โหลดค่อยแพ็ก .sga ใหม่

## Phase A — ฟอนต์ PUA (แผนสำรอง ถ้า C ล้มเหลว)

วิธีมาตรฐานวงการม็อด Relic engine (แบบที่ม็อดไทย CoH2 ใช้):

1. เลือกฟอนต์ไทยฟรี (Sarabun / Noto Sans Thai — OFL license)
2. ใช้ FontForge สร้าง glyph แบบ **precomposed**: พยัญชนะ+สระ+วรรณยุกต์ที่ใช้จริง
   รวมเป็น glyph เดียว ใส่รหัส PUA (U+E000+)
3. แก้ `.fnt` เพิ่มช่วง PUA
4. เขียนสคริปต์ Python (ใน `tools\`) แปลงข้อความไทย → รหัส PUA
   (ฟังก์ชันเดียวกับ TPUA แต่เขียนเอง ~50 บรรทัด คุมการจับคู่ได้เอง)
5. เอา .ucs ที่เข้ารหัส PUA แล้วกลับไปวางทับ

เคล็ดลับ: สร้าง glyph เฉพาะคู่ที่ปรากฏในข้อความที่แปลจริง (scope UI/หน่วยรบ → ไม่กี่ร้อยคู่ ไม่ต้องครบทุกคู่ของภาษาไทย)

## หมายเหตุ

- แก้ไฟล์ในโฟลเดอร์เกมโดยตรงไม่ได้ถ้า Steam เปิดอยู่ — ปิดเกมก่อนแก้/ทับไฟล์
- เก็บ .ucs ที่แปลแล้วไว้ใน `work\` เสมอ อย่าทำงานบนไฟล์ในโฟลเดอร์เกมโดยตรง
- CoH1 Relaunch รวมของ Opposing Fronts/Tales of Valor มาหมดแล้ว — ไฟล์ข้อความไฟล์เดียวจบ
