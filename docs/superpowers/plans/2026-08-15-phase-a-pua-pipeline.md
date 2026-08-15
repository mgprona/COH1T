# Phase A: PUA Font Pipeline + Translation Workflow — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** สร้าง pipeline ฟอนต์ PUA (precomposed Thai clusters) + workflow แยกไฟล์แปล (csv) ที่ทีมแปลและทีม mod ทำงานคู่ขนานกันได้

**Architecture:** แตกข้อความไทยเป็น cluster (ฐาน + combining marks) → สร้าง composite glyph ใส่ PUA ด้วย HarfBuzz+fontTools → เข้ารหัสข้อความใน .ucs เป็น PUA → แพตช์ฟอนต์ PUA เข้า Engine.sga แบบ in-place (วิธีพิสูจน์แล้วจาก Phase C)

**Tech Stack:** Python 3.14 (uv), fonttools 4.63, uharfbuzz (ติดตั้งใหม่), capstone/pefile (มีแล้ว, ไม่ใช้ในงานนี้)

## Global Constraints

- รันทุกอย่างผ่าน `uv run python ...` (venv `.venv`)
- ไฟล์ `.ucs`: UTF-16LE + CRLF + BOM เสมอ — เขียนด้วย `open(path, "w", encoding="utf-16", newline="")` และ join `"\r\n"` แล้ว assert ไม่มี `"\r\r"` (บทเรียนจากบั๊ก double-CR)
- Lint/typecheck ผ่านก่อนจบทุก task: `uv run ruff check tools tests` และ `uv run pyright tools tests`
- Tests = ไฟล์ plain python (`tests/test_*.py`) รันด้วย `uv run python tests/test_x.py` — ไม่มี pytest, assert + `main()` พอ
- คอมมิต: รันเฉพาะเมื่อผู้ใช้ยืนยันนโยบาย commit แล้วเท่านั้น (ข้ามขั้นตอน commit ได้ถ้าผู้ใช้ไม่สั่ง)
- ฟอนต์ฐาน: `C:\Windows\Fonts\LeelawUI.ttf` (regular), `C:\Windows\Fonts\LeelaUIb.ttf` (bold)
- สล็อตใน Engine.sga (ห้ามเปลี่ยน): `trebuc.ttf` @0x12092B73/134108, `trebucbd.ttf` @0x120B3853/123096, `impact.ttf` @0x120716E3/136076 — CRC32 อยู่ 4 ไบต์ก่อน data
- ห้ามแก้ไฟล์ในโฟลเดอร์เกมขณะ Steam/เกมเปิดอยู่
- เกมรันด้วย workdir = โฟลเดอร์เกม (ไม่งั้น RelicCOH.ini โหลดไม่เจอ)

---

### Task 1: Thai cluster tokenizer

**Files:**
- Create: `tools/thai_cluster.py`
- Test: `tests/test_thai_cluster.py`

**Interfaces:**
- Produces:
  - `is_thai(ch: str) -> bool` — True ถ้า U+0E00–U+0E7F
  - `tokenize_clusters(text: str) -> list[str]` — แยกข้อความเป็น cluster; cluster = ตัวอักษรฐาน (ที่ไม่ใช่ combining mark) + combining marks ที่ตามมา (U+0E31, U+0E34–0E3A, U+0E47–0E4E); สระที่เรนเดอร์ถูกตำแหน่งเองโดยไม่ต้อง shaping (สระหน้า เ แ โ ใ ไ และสระระยะ า ะ ำ) เป็นฐาน = cluster เดี่ยว

- [ ] **Step 1: เขียน test**

```python
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
```

- [ ] **Step 2: รัน test ให้ fail**

Run: `uv run python tests/test_thai_cluster.py`
Expected: `ModuleNotFoundError: No module named 'tools.thai_cluster'`

- [ ] **Step 3: เขียน implementation**

```python
MARK_RANGES = ((0x0E31, 0x0E31), (0x0E34, 0x0E3A), (0x0E47, 0x0E4E))


def is_thai(ch: str) -> bool:
    return 0x0E00 <= ord(ch) <= 0x0E7F


def _is_mark(ch: str) -> bool:
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in MARK_RANGES)


def tokenize_clusters(text: str) -> list[str]:
    clusters: list[str] = []
    for ch in text:
        if clusters and _is_mark(ch):
            clusters[-1] += ch
        else:
            clusters.append(ch)
    return clusters
```

- [ ] **Step 4: รัน test ให้ pass**

Run: `uv run python tests/test_thai_cluster.py`
Expected: `ok`

- [ ] **Step 5: lint + typecheck**

Run: `uv run ruff check tools tests; uv run pyright tools tests`
Expected: ผ่านทั้งหมด

- [ ] **Step 6: Commit (ถ้าผู้ใช้ยืนยันนโยบาย commit แล้ว)**

```bash
git add tools/thai_cluster.py tests/test_thai_cluster.py
git commit -m "feat: add thai cluster tokenizer"
```

---

### Task 2: PUA cluster map + encoder

**Files:**
- Create: `tools/pua_encode.py`
- Test: `tests/test_pua_encode.py`

**Interfaces:**
- Consumes: `tokenize_clusters(text) -> list[str]`, `is_thai(ch) -> bool` จาก `tools.thai_cluster`
- Produces:
  - `PUA_START = 0xE000`
  - `collect_clusters(texts: Iterable[str]) -> set[str]` — cluster ไทยความยาว >1 ทั้งหมดในชุดข้อความ
  - `load_map(path: Path) -> dict[str, int]` / `save_map(path: Path, m: dict[str, int]) -> None` — JSON: `{cluster: codepoint}`
  - `encode(text: str, m: dict[str, int]) -> tuple[str, set[str]]` — แปลงข้อความเป็น PUA; คืน (encoded, missing clusters ที่ไม่อยู่ใน map — cluster เหล่านั้นถูกปล่อยเป็นตัวดิบ)

- [ ] **Step 1: เขียน test**

```python
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.pua_encode import PUA_START, collect_clusters, encode, load_map, save_map


def main() -> None:
    clusters = collect_clusters(["เล่นต่อเกม", "ผู้เล่นหลายคน"])
    assert clusters == {"ล่", "ต่", "ผู้"}
    m = {c: PUA_START + i for i, c in enumerate(sorted(clusters))}
    tmp = Path("work/test_map.json")
    save_map(tmp, m)
    assert load_map(tmp) == m
    assert json.loads(tmp.read_text(encoding="utf-8")) == {c: PUA_START + i for i, c in enumerate(sorted(clusters))}
    out, missing = encode("เล่นต่อ", m)
    assert missing == set()
    assert out == f"\u0E40{chr(m['ล่'])}น{chr(m['ต่'])}อ"
    out2, missing2 = encode("เล่นต่อเก่ง", m)
    assert missing2 == {"ก่"}
    assert "เก่ง" in out2  # fallback เป็นตัวดิบ
    print("ok")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: รัน test ให้ fail**

Run: `uv run python tests/test_pua_encode.py`
Expected: `ModuleNotFoundError: No module named 'tools.pua_encode'`

- [ ] **Step 3: เขียน implementation**

```python
import json
from collections.abc import Iterable
from pathlib import Path

from tools.thai_cluster import is_thai, tokenize_clusters

PUA_START = 0xE000


def collect_clusters(texts: Iterable[str]) -> set[str]:
    found: set[str] = set()
    for text in texts:
        for c in tokenize_clusters(text):
            if len(c) > 1 and is_thai(c[0]):
                found.add(c)
    return found


def load_map(path: Path) -> dict[str, int]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_map(path: Path, m: dict[str, int]) -> None:
    path.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")


def encode(text: str, m: dict[str, int]) -> tuple[str, set[str]]:
    out: list[str] = []
    missing: set[str] = set()
    for c in tokenize_clusters(text):
        if len(c) > 1 and is_thai(c[0]):
            cp = m.get(c)
            if cp is None:
                missing.add(c)
                out.append(c)
            else:
                out.append(chr(cp))
        else:
            out.append(c)
    return "".join(out), missing
```

- [ ] **Step 4: รัน test ให้ pass**

Run: `uv run python tests/test_pua_encode.py`
Expected: `ok`

- [ ] **Step 5: lint + typecheck**

Run: `uv run ruff check tools tests; uv run pyright tools tests`
Expected: ผ่านทั้งหมด

- [ ] **Step 6: Commit (ถ้าผู้ใช้ยืนยันนโยบาย commit แล้ว)**

```bash
git add tools/pua_encode.py tests/test_pua_encode.py
git commit -m "feat: add pua cluster map and encoder"
```

---

### Task 3: ucs_workflow — extract (ส่งไฟล์ให้ทีมแปลได้เร็วสุด)

**Files:**
- Create: `tools/ucs_workflow.py` (ส่วน read_ucs/write_ucs/extract/CLI)
- Test: `tests/test_ucs_workflow.py`
- Produces (รันจริง): `work/translate.csv`

**Interfaces:**
- Produces:
  - `read_ucs(path: Path) -> dict[int, str]` — อ่าน .ucs (UTF-16LE+CRLF+BOM) → {id: text}; assert ไม่มี `\r\r`
  - `write_ucs(path: Path, entries: dict[int, str]) -> None` — เขียน UTF-16LE, join `"\r\n"`, `newline=""`, ลงท้าย `\r\n`
  - `extract(base_ucs: Path, current_ucs: Path, out_csv: Path) -> int` — เขียน csv (utf-8-sig, `lineterminator="\r\n"`) คอลัมน์ `id,english,thai,context`; english มาจาก base (backup ต้นฉบับ), thai มาจาก current เฉพาะบรรทัดที่ต่างจาก english (ที่แปลแล้ว); คืนจำนวนแถว
  - `FE_CONTEXTS: dict[int, str]` — บริบทของ ID เมนูหลัก (ดูโค้ดด้านล่าง)

- [ ] **Step 1: เขียน test**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.ucs_workflow import extract, read_ucs, write_ucs

ROOT = Path(__file__).parent.parent


def _make_ucs(path: Path, entries: dict[int, str]) -> None:
    lines = [f"{i}\t{t}" for i, t in sorted(entries.items())]
    with open(path, "w", encoding="utf-16", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")


def main() -> None:
    base = ROOT / "work" / "test_base.ucs"
    cur = ROOT / "work" / "test_cur.ucs"
    csv = ROOT / "work" / "test_out.csv"
    _make_ucs(base, {713512: "CAMPAIGN", 713513: "Continue", 5256: "MAIN MENU"})
    _make_ucs(cur, {713512: "แคมเปญ", 713513: "Continue", 5256: "MAIN MENU"})
    n = extract(base, cur, csv)
    assert n == 3
    content = csv.read_text(encoding="utf-8-sig").splitlines()
    assert content[0] == "id,english,thai,context"
    assert "713512,CAMPAIGN,แคมเปญ," in content[1:][0]
    assert any(line.startswith("713513,Continue,,") for line in content[1:])
    assert any(line.startswith("5256,MAIN MENU,,") for line in content[1:])
    entries = read_ucs(cur)
    assert entries[713512] == "แคมเปญ"
    out = ROOT / "work" / "test_rewrite.ucs"
    write_ucs(out, entries)
    assert read_ucs(out) == entries
    raw = out.read_bytes()
    assert raw[:2] == b"\xff\xfe"
    assert b"\r\r" not in raw and b"\r\x00\n\x00" in raw
    print("ok")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: รัน test ให้ fail**

Run: `uv run python tests/test_ucs_workflow.py`
Expected: `ModuleNotFoundError: No module named 'tools.ucs_workflow'`

- [ ] **Step 3: เขียน implementation**

```python
import csv
import sys
from pathlib import Path

FE_CONTEXTS = {
    713500: "ปุ่มต่อแคมเปญ",
    713501: "ชื่อแคมเปญนอร์มังดี",
    713502: "tooltip เริ่มแคมเปญนอร์มังดี",
    713503: "ปุ่มเมนูหลัก: บทเรียน",
    713504: "ฉลากเวอร์ชันเกม",
    713505: "tooltip เล่นแคมเปญผู้เล่นเดี่ยว",
    713506: "ชื่อแคมเปญบุกคาน",
    713507: "tooltip เริ่มบทเรียน",
    713508: "tooltip ออกจากเกม",
    713509: "ปุ่มเมนูหลัก: ศึกรวดเร็ว",
    713510: "ปุ่มเมนูหลัก: ออก",
    713511: "tooltip เริ่มแคมเปญบุกคาน",
    713512: "ปุ่มเมนูหลัก: แคมเปญ",
    713513: "tooltip ต่อแคมเปญนอร์มังดี",
    713514: "ชื่อแคมเปญมาร์เก็ตการ์เดน",
    713515: "ชื่อแคมเปญเสือเหล็ก",
    713516: "tooltip ศึกรวดเร็วกับ CPU",
    713517: "tooltip ต่อแคมเปญบุกคาน",
    713518: "tooltip เริ่มแคมเปญมาร์เก็ตการ์เดน",
    713519: "tooltip เล่นผู้เล่นหลายคน",
    713520: "ปุ่มเมนูหลัก: ผู้เล่นหลายคน",
    713521: "ปุ่มเมนูหลัก: ตัวเลือก",
    713522: "tooltip ตั้งค่าเกม",
    713523: "ปุ่มเลือกภารกิจ",
    713524: "ปุ่มต่อเกม",
    713525: "tooltip ล็อกปฏิบัติการ (ต้องมี Tales of Valor)",
    713526: "ปุ่มต่อเกม",
    713527: "ปุ่มต่อเกม",
    713528: "ปุ่มเมนูหลัก: เวิร์กชอป",
    713529: "ปุ่มเลือกภารกิจ",
    713530: "ปุ่มต่อเกม",
    713531: "ปุ่มเลือกภารกิจ",
    713532: "ปุ่มต่อเกม",
    713533: "ปุ่มเลือกภารกิจ",
    713535: "tooltip เข้า Steam Workshop",
    713540: "ปุ่มเลือกภารกิจ",
    713541: "tooltip เริ่มแคมเปญฟาแลสพ็อกเก็ต",
    713542: "tooltip ต่อแคมเปญฟาแลสพ็อกเก็ต",
    713543: "ปุ่มเลือกภารกิจ",
    713544: "ปุ่มเมนูหลัก: ปฏิบัติการ",
    713545: "ชื่อแคมเปญคอสเวย์",
    713547: "tooltip เริ่มแคมเปญคอสเวย์",
    713548: "ชื่อแคมเปญฟาแลสพ็อกเก็ต",
    713552: "tooltip ต่อแคมเปญมาร์เก็ตการ์เดน",
    713555: "tooltip เริ่มแคมเปญเสือเหล็ก",
    713556: "tooltip ต่อแคมเปญเสือเหล็ก",
    713557: "tooltip ต่อแคมเปญคอสเวย์",
    713558: "tooltip ปฏิบัติการผู้เล่นหลายคน",
    5256: "เมนูเก่า: เมนูหลัก",
    9250: "เมนูเก่า: แคมเปญ",
    9251: "เมนูเก่า: ศึกรวดเร็ว",
    9252: "เมนูเก่า: ผู้เล่นหลายคน",
}


def read_ucs(path: Path) -> dict[int, str]:
    text = path.read_text(encoding="utf-16")
    assert "\r\r" not in text, f"{path}: double-CR corruption detected"
    entries: dict[int, str] = {}
    for line in text.splitlines():
        if not line:
            continue
        sid, _, value = line.partition("\t")
        if sid.isdigit():
            entries[int(sid)] = value
    return entries


def write_ucs(path: Path, entries: dict[int, str]) -> None:
    lines = [f"{i}\t{t}" for i, t in sorted(entries.items())]
    with open(path, "w", encoding="utf-16", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")
    raw = path.read_bytes()
    assert b"\r\r" not in raw, f"{path}: double-CR corruption detected"


def extract(base_ucs: Path, current_ucs: Path, out_csv: Path) -> int:
    base = read_ucs(base_ucs)
    current = read_ucs(current_ucs)
    ids = sorted(FE_CONTEXTS)
    rows = 0
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(["id", "english", "thai", "context"])
        for sid in ids:
            english = base.get(sid, "")
            thai = current.get(sid, "")
            if thai == english:
                thai = ""
            w.writerow([sid, english, thai, FE_CONTEXTS[sid]])
            rows += 1
    return rows


def main() -> None:
    cmd = sys.argv[1]
    if cmd == "extract":
        n = extract(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
        print(f"extracted {n} rows -> {sys.argv[4]}")
    else:
        print("usage: ucs_workflow.py extract <base.ucs> <current.ucs> <out.csv>")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: รัน test ให้ pass**

Run: `uv run python tests/test_ucs_workflow.py`
Expected: `ok`

- [ ] **Step 5: รัน extract จริง**

Run: `uv run python tools/ucs_workflow.py extract backup/RelicCOH.English.ucs work/RelicCOH.English.ucs work/translate.csv`
Expected: `extracted 52 rows -> work/translate.csv`

- [ ] **Step 6: ตรวจ csv**

Run: `Get-Content work\translate.csv -TotalCount 8`
Expected: header `id,english,thai,context` + แถวที่แปลแล้วมีคอลัมน์ thai เป็นไทย (เช่น `713512,CAMPAIGN,แคมเปญ,ปุ่มเมนูหลัก: แคมเปญ`)

- [ ] **Step 7: lint + typecheck**

Run: `uv run ruff check tools tests; uv run pyright tools tests`
Expected: ผ่านทั้งหมด

- [ ] **Step 8: ส่งต่อผู้ใช้** — `work\translate.csv` พร้อมให้ทีมแปล (AI ตัวอื่น) ทำงานคู่ขนานได้ตั้งแต่นี้

- [ ] **Step 9: Commit (ถ้าผู้ใช้ยืนยันนโยบาย commit แล้ว)**

```bash
git add tools/ucs_workflow.py tests/test_ucs_workflow.py
git commit -m "feat: add ucs extract to translation csv"
```

---

### Task 4: PUA font builder (uharfbuzz + fontTools)

**Files:**
- Create: `tools/pua_font_builder.py`
- Test: `tests/test_pua_font_builder.py`
- Modify: `pyproject.toml` (เพิ่ม dependency `uharfbuzz`)

**Interfaces:**
- Consumes: `tokenize_clusters` จาก `tools.thai_cluster`, `save_map` จาก `tools.pua_encode`
- Produces:
  - `build_font(base_ttf: Path, clusters: set[str], out_ttf: Path, map_path: Path) -> dict[str, int]`
    — shape แต่ละ cluster ด้วย uharfbuzz → สร้าง composite glyph (`glyf` components + `hmtx` advance + `cmap` PUA) → save font + map; คืน cluster map
  - `main()` CLI: `pua_font_builder.py <clusters.json?>...` — ไม่มี arg: สแกนคอลัมน์ thai ของ `work/translate.csv` → build regular (`font/Leelawad-PUA.ttf`) + bold (`font/Leelawdb-PUA.ttf`) → เขียน `work/cluster_map.json`

- [ ] **Step 1: ติดตั้ง uharfbuzz**

Run: `uv add uharfbuzz`
Expected: ติดตั้งสำเร็จ ขึ้นใน pyproject dependencies

- [ ] **Step 2: เขียน test**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from fontTools.ttLib import TTFont
from tools.pua_encode import PUA_START, load_map
from tools.pua_font_builder import build_font

ROOT = Path(__file__).parent.parent
BASE = Path(r"C:\Windows\Fonts\LeelawUI.ttf")


def main() -> None:
    clusters = {"ล่", "ต่", "ผู้"}
    out = ROOT / "work" / "test_pua.ttf"
    map_path = ROOT / "work" / "test_map.json"
    m = build_font(BASE, clusters, out, map_path)
    assert m == load_map(map_path)
    assert sorted(m) == ["ผู้", "ต่", "ล่"]
    font = TTFont(out)
    cmap = font.getBestCmap()
    glyf = font["glyf"]
    for c, cp in m.items():
        gname = cmap[cp]
        g = glyf[gname]
        assert g.numberOfContours == -1, f"{c}: not composite"
        assert len(g.components) == len(c), f"{c}: {len(g.components)} comps != {len(c)} chars"
    assert 0x0E01 in cmap, "original Thai cmap must remain"
    print("ok")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: รัน test ให้ fail**

Run: `uv run python tests/test_pua_font_builder.py`
Expected: `ModuleNotFoundError: No module named 'tools.pua_font_builder'`

- [ ] **Step 4: เขียน implementation**

```python
import csv
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent

from tools.pua_encode import PUA_START, collect_clusters, load_map, save_map

REGULAR = Path(r"C:\Windows\Fonts\leelawad.ttf")
BOLD = Path(r"C:\Windows\Fonts\leelawdb.ttf")
OUT_DIR = Path("font")
CSV_PATH = Path("work/translate.csv")
MAP_PATH = Path("work/cluster_map.json")


def build_font(base_ttf: Path, clusters: set[str], out_ttf: Path, map_path: Path) -> dict[str, int]:
    clusters = set(sorted(clusters))
    m = {c: PUA_START + i for i, c in enumerate(sorted(clusters))}
    font = TTFont(base_ttf)
    order = font.getGlyphOrder()
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    face = hb.Face(base_ttf.read_bytes())
    hbfont = hb.Font(face)
    for cluster, cp in m.items():
        buf = hb.Buffer()
        buf.add_str(cluster)
        buf.guess_segment_properties()
        hb.shape(hbfont, buf)
        positions = buf.glyph_positions
        infos = buf.glyph_infos
        gname = f"pua{cp:X}"
        g = Glyph()
        g.numberOfContours = -1
        g.components = []
        for info, pos in zip(infos, positions):
            comp_name = order[info.codepoint]
            g.components.append(GlyphComponent(comp_name, round(pos.x_offset), round(pos.y_offset)))
        glyf[gname] = g
        hmtx[gname] = (round(sum(p.x_advance for p in positions)), 0)
        for table in font["cmap"].tables:
            if table.isUnicode():
                table.cmap[cp] = gname
    out_ttf.parent.mkdir(parents=True, exist_ok=True)
    font.save(out_ttf)
    save_map(map_path, m)
    return m


def main() -> None:
    texts: list[str] = []
    if CSV_PATH.exists():
        with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                thai = (row.get("thai") or "").strip()
                if thai:
                    texts.append(thai)
    clusters = collect_clusters(texts)
    m = build_font(REGULAR, clusters, OUT_DIR / "Leelawad-PUA.ttf", MAP_PATH)
    build_font(BOLD, clusters, OUT_DIR / "Leelawdb-PUA.ttf", MAP_PATH)
    print(f"built {len(clusters)} PUA glyphs into font/ (map -> {MAP_PATH})")
    print("map:", m)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: รัน test ให้ pass**

Run: `uv run python tests/test_pua_font_builder.py`
Expected: `ok`

- [ ] **Step 6: lint + typecheck**

Run: `uv run ruff check tools tests; uv run pyright tools tests`
Expected: ผ่านทั้งหมด (ถ้า pyright บ่นเรื่อง `Glyph` attrs ให้เพิ่ม type: ignore ในบรรทัดนั้นตามความจำเป็น)

- [ ] **Step 7: Commit (ถ้าผู้ใช้ยืนยันนโยบาย commit แล้ว)**

```bash
git add tools/pua_font_builder.py tests/test_pua_font_builder.py pyproject.toml uv.lock
git commit -m "feat: add pua font builder via harfbuzz"
```

---

### Task 5: ucs_workflow — apply (csv → PUA .ucs)

**Files:**
- Modify: `tools/ucs_workflow.py` (เพิ่ม `apply` + CLI branch)
- Test: `tests/test_ucs_workflow.py` (เพิ่ม test)

**Interfaces:**
- Consumes: `encode(text, m) -> tuple[str, set[str]]` จาก `tools.pua_encode`, `read_ucs`/`write_ucs` (Task 3)
- Produces:
  - `apply(csv_path: Path, base_ucs: Path, out_ucs: Path, map_path: Path) -> list[str]`
    — เริ่มจาก base (backup ต้นฉบับ) ทับด้วยคำแปลจาก csv → เข้ารหัส PUA → เขียน out; คืน warnings (cluster ใหม่ที่ไม่อยู่ใน map)
  - CLI: `ucs_workflow.py apply <translate.csv> <base.ucs> <out.ucs> <cluster_map.json>`

- [ ] **Step 1: เพิ่ม test**

```python
    # ต่อท้าย main() เดิม
    from tools.pua_encode import PUA_START, save_map
    from tools.ucs_workflow import apply

    m = {"ล่": PUA_START, "ต่": PUA_START + 1}
    save_map(ROOT / "work" / "test_cmap.json", m)
    csv2 = ROOT / "work" / "test_translate.csv"
    csv2.write_text(
        "id,english,thai,context\r\n713512,CAMPAIGN,เล่นต่อ,\r\n713513,Continue,ต่อเก่ง,\r\n",
        encoding="utf-8-sig",
    )
    out2 = ROOT / "work" / "test_applied.ucs"
    warnings = apply(csv2, base, out2, ROOT / "work" / "test_cmap.json")
    entries = read_ucs(out2)
    assert entries[713512] == f"\u0E40{chr(PUA_START)}น{chr(PUA_START + 1)}อ"
    assert entries[713513] == "ต่อเก่ง"  # เก่ง มี cluster ใหม่ -> fallback ดิบ
    assert any("ก่" in w for w in warnings)
    assert entries[5256] == "MAIN MENU"  # ไม่ได้แปล -> คงต้นฉบับ
```

- [ ] **Step 2: รัน test ให้ fail**

Run: `uv run python tests/test_ucs_workflow.py`
Expected: fail — `ImportError: cannot import name 'apply'`

- [ ] **Step 3: เขียน implementation**

```python
def apply(csv_path: Path, base_ucs: Path, out_ucs: Path, map_path: Path) -> list[str]:
    m = load_map(map_path)
    entries = read_ucs(base_ucs)
    warnings: list[str] = []
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            thai = (row.get("thai") or "").strip()
            if not thai:
                continue
            encoded, missing = encode(thai, m)
            if missing:
                warnings.append(f"id {row['id']}: new clusters {sorted(missing)} -> run pua_font_builder.py")
                entries[int(row["id"])] = thai
            else:
                entries[int(row["id"])] = encoded
    write_ucs(out_ucs, entries)
    return warnings
```

และใน `main()` เพิ่ม branch:

```python
    elif cmd == "apply":
        warnings = apply(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
        for w in warnings:
            print("WARN:", w)
        print(f"applied -> {sys.argv[4]}")
```

และ usage: `usage: ucs_workflow.py extract <base.ucs> <current.ucs> <out.csv> | apply <translate.csv> <base.ucs> <out.ucs> <cluster_map.json>`

เพิ่ม import ที่หัวไฟล์: `from tools.pua_encode import encode, load_map`

- [ ] **Step 4: รัน test ให้ pass**

Run: `uv run python tests/test_ucs_workflow.py`
Expected: `ok`

- [ ] **Step 5: lint + typecheck**

Run: `uv run ruff check tools tests; uv run pyright tools tests`
Expected: ผ่านทั้งหมด

- [ ] **Step 6: Commit (ถ้าผู้ใช้ยืนยันนโยบาย commit แล้ว)**

```bash
git add tools/ucs_workflow.py tests/test_ucs_workflow.py
git commit -m "feat: add ucs apply with pua encoding"
```

---

### Task 6: patch_sga รองรับฟอนต์ PUA

**Files:**
- Modify: `tools/patch_sga.py`
- Test: `tests/test_patch_sga.py`

**Interfaces:**
- Produces:
  - `FONT_SLOTS: dict[str, tuple[int, int, str]]` — เปลี่ยน replacement path เป็น `font/Leelawad-PUA.ttf` / `font/Leelawdb-PUA.ttf` (regular→trebuc+impact slots, bold→trebucbd slot)
  - `main()` — รับ arg เสริม: `patch_sga.py [src.sga] [dst.sga]` (default: backup\Engine.sga → work\Engine_patched.sga)

- [ ] **Step 1: เขียน test**

```python
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

    # สร้าง sga จำลอง: 16KB zero + 3 slot ttf + crc ก่อนแต่ละ slot
    data = bytearray(b"\x00" * 0x1000)
    fake = Path(r"C:\Windows\Fonts\leelawad.ttf").read_bytes()

    def place(slot_off: int, length: int) -> None:
        data[slot_off - 4 : slot_off] = zlib.crc32(fake).to_bytes(4, "little")
        data[slot_off : slot_off + length] = fake

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
    print("ok")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: รัน test ให้ fail**

Run: `uv run python tests/test_patch_sga.py`
Expected: fail — `AttributeError: module 'tools.patch_sga' has no attribute 'run'`

- [ ] **Step 3: แก้ implementation**

เปลี่ยน `tools/patch_sga.py` เป็น:

```python
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
```

- [ ] **Step 4: รัน test ให้ pass**

Run: `uv run python tests/test_patch_sga.py`
Expected: `ok`

- [ ] **Step 5: lint + typecheck**

Run: `uv run ruff check tools tests; uv run pyright tools tests`
Expected: ผ่านทั้งหมด

- [ ] **Step 6: Commit (ถ้าผู้ใช้ยืนยันนโยบาย commit แล้ว)**

```bash
git add tools/patch_sga.py tests/test_patch_sga.py
git commit -m "feat: generalize patch_sga for pua fonts"
```

---

### Task 7: Integration — deploy จริง + ทดสอบในเกม

**Files:**
- Produces: `work/cluster_map.json`, `font/Leelawad-PUA.ttf`, `font/Leelawdb-PUA.ttf`, `work/Engine_patched.sga`, `work/RelicCOH.English.ucs` (PUA)
- Modify (ในโฟลเดอร์เกม): `Engine\Archives\Engine.sga`, `CoH\Engine\Locale\English\RelicCOH.English.ucs`

- [ ] **Step 1: รัน font builder จริง**

Run: `uv run python tools/pua_font_builder.py`
Expected: `built N PUA glyphs into font/ (map -> work/cluster_map.json)` — N ≈ จำนวน cluster ใน 52 บรรทัด

- [ ] **Step 2: ตรวจฟอนต์ผลลัพธ์**

Run: `uv run python tests/test_pua_font_builder.py` แล้ว
`uv run python -c "from fontTools.ttLib import TTFont; f=TTFont('font/Leelawad-PUA.ttf'); print('glyphs:', len(f.getBestCmap()))"`
Expected: test ผ่าน, glyph นับ > 340 (Leelawadee เดิม 340 + PUA)

- [ ] **Step 3: apply แปล → .ucs PUA**

Run: `uv run python tools/ucs_workflow.py apply work/translate.csv backup/RelicCOH.English.ucs work/RelicCOH.English.ucs work/cluster_map.json`
Expected: `applied -> work/RelicCOH.English.ucs` + ไม่มี WARN (ถ้ามี WARN cluster ใหม่ → กลับไป Step 1 แล้วค่อยรันต่อ)

- [ ] **Step 4: ตรวจ .ucs เป็น PUA + format ถูก**

Run: `uv run python -c "e=open(r'work/RelicCOH.English.ucs',encoding='utf-16').read().splitlines(); print([l.encode('unicode_escape').decode() for l in e if l.startswith(('713512\t','713520\t'))])"`
Expected: ขึ้น `\ue...` (PUA codepoint) แทนอักษรไทยตรง ตามด้วย cluster ที่เป็นอักษรเดี่ยวเช่น `\u0e40` (สระหน้า) ผสมกัน

- [ ] **Step 5: ตรวจไฟล์ในเกมปิดอยู่**

Run: `Get-Process RelicCOH -ErrorAction SilentlyContinue`
Expected: ไม่มี output (เกมไม่เปิด)

- [ ] **Step 6: deploy เข้าเกม**

Run (PowerShell):

```powershell
$G = "C:\Program Files (x86)\Steam\steamapps\common\Company of Heroes Relaunch"
Copy-Item "work\Engine_patched.sga" "$G\Engine\Archives\Engine.sga" -Force
Copy-Item "work\RelicCOH.English.ucs" "$G\CoH\Engine\Locale\English\RelicCOH.English.ucs" -Force
```

Expected: ไม่มี error

- [ ] **Step 7: สร้าง Engine_patched.sga จาก patch_sga (ถ้ายังไม่ได้ทำใน Step 6)**

Run: `uv run python tools/patch_sga.py` (default: backup → work\Engine_patched.sga) แล้ว copy เหมือน Step 6

- [ ] **Step 8: รันเกม + จับภาพอัตโนมัติ**

Run: `powershell -ExecutionPolicy Bypass -File tools\capture_screen.ps1`
Expected: เกมเปิด เข้าเมนูหลัก (ตรวจ `warnings.log` ขึ้น `Beginning FE` + ไม่มี FATAL)

- [ ] **Step 9: ตรวจ log**

Run: `Get-Content "$env:USERPROFILE\Documents\My Games\Company of Heroes Relaunch\warnings.log" -TotalCount 8`
Expected: `WORKING-DIR C:\Program Files (x86)\Steam\steamapps\common\Company of Heroes Relaunch` + ไม่มี `Failed to load 'RelicCOH.ini'`

- [ ] **Step 10: ให้ผู้ใช้ดูผลในเกมจริง**

ผู้ใช้รันเกมตามปกติและรายงาน: สระ/วรรณยุกต์ตรงตำแหน่งไหม (เทียบกับก่อนหน้านี้ที่ลอย)

- [ ] **Step 11: สรุป + อัปเดต README**

ถ้าผู้ใช้ยืนยันว่าใช้ได้ → อัปเดต `README.md`: Phase C สำเร็จแล้ว (วิธี: แพตช์ slot ใน Engine.sga), Phase A pipeline ใช้การได้, วิธีใช้งานคำสั่ง `extract`/`apply`/`pua_font_builder`/`patch_sga`

- [ ] **Step 12: Commit (ถ้าผู้ใช้ยืนยันนโยบาย commit แล้ว)**

```bash
git add README.md work/cluster_map.json
git commit -m "docs: update readme with phase c results and phase a workflow"
```

---

## Self-Review Notes (ตรวจแล้ว)

- Spec coverage: cluster analysis → T1; precomposition (Harfbuzz+fontTools) → T4; encoding → T2/T5; font deploy → T6/T7; csv workflow (extract/apply + context) → T3/T5; คำเตือน cluster ใหม่ → T5; format safety (UTF-16LE/CRLF/BOM, assert \r\r) → T3/T5; ทำงานคู่ขนาน → T3 ส่ง csv ได้ก่อน T4
- Placeholder scan: ไม่มี TBD/TODO
- Type consistency: `tokenize_clusters`, `collect_clusters`, `encode(text, m) -> tuple[str, set[str]]`, `load_map`/`save_map(path, m)`, `build_font(base, clusters, out, map_path)`, `read_ucs`/`write_ucs(path, entries)`, `extract(base, current, out) -> int`, `apply(csv, base, out, map) -> list[str]`, `patch_sga.run(src, dst)` — ชื่อและ signature ตรงกันทุก task
