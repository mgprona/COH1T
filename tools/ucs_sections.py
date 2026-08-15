"""Schema มาตรฐานการจัดหมวดข้อความ COH1T.

ทุก string ID ใน RelicCOH.English.ucs ต้องตกใน SECTION เดียวพอดี
(บล็อก ID ที่ไม่ใช่ kind-filtered ต้องไม่ซ้อนกัน; kind-filtered sections ใช้ range เดียวกัน
แต่กรองด้วย classify_kind) — มี test กำกับใน tests/test_ucs_sections.py

แก้ schema ได้เรื่อยๆ (เพิ่มบล็อก/ย้ายช่วง) โดยรัน test + extract ใหม่
"""

from __future__ import annotations

import re
from dataclasses import dataclass

STAT_PREFIX = "Good vs."
_NAME_MAX_LEN = 45


@dataclass(frozen=True)
class Section:
    category: str
    key: str
    file: str
    ranges: tuple[tuple[int, int], ...]
    kind: str | None
    context: str


def _r(*pairs: tuple[int, int]) -> tuple[tuple[int, int], ...]:
    return pairs


UI_RANGE = _r((0, 32261), (40500, 42750), (53250, 90000))
UNITS_RANGE = _r((90000, 200000), (2000000, 2300000))

SECTIONS: tuple[Section, ...] = (
    # ---- 01 UI ----
    Section("01_ui", "01_system", "01_system.csv", UI_RANGE, None, "UI: ระบบ/ปุ่มทั่วไป/ตั้งค่า"),
    Section(
        "01_ui",
        "02_game_ui",
        "02_game_ui.csv",
        _r((32261, 40500)),
        None,
        "UI: หน้าจอเกม/save-load/แคมเปญ",
    ),
    Section(
        "01_ui", "03_setup", "03_setup.csv", _r((42750, 53250)), None, "UI: เลือกโหมด/ตั้งเกม/อีเวนต์คิว"
    ),
    Section(
        "01_ui",
        "04_main_menu",
        "04_main_menu.csv",
        _r((713495, 713561)),
        None,
        "UI: เมนูหลัก Relaunch",
    ),
    Section(
        "01_ui",
        "05_lobby",
        "05_lobby.csv",
        _r((500000, 713495), (713561, 800000)),
        None,
        "UI: ล็อบบี้/ออนไลน์/แรงก์/ผลแมตช์",
    ),
    Section(
        "01_ui",
        "06_workshop",
        "06_workshop.csv",
        _r((12000000, 20000000)),
        None,
        "UI: Steam Workshop",
    ),
    # ---- 02 หน่วยรบ (kind-based) ----
    Section(
        "02_units", "01_names", "01_names.csv", UNITS_RANGE, "name", "ยูนิต: ชื่อหน่วย/อาวุธ/อาคาร/สกิล"
    ),
    Section(
        "02_units",
        "02_descriptions",
        "02_descriptions.csv",
        UNITS_RANGE,
        "desc",
        "ยูนิต: คำอธิบาย/tooltip",
    ),
    Section(
        "02_units", "03_stats", "03_stats.csv", UNITS_RANGE, "stat", "ยูนิต: สถิติอาวุธ (Good vs. ...)"
    ),
    Section(
        "02_units", "04_misc", "04_misc.csv", UNITS_RANGE, "other", "ยูนิต: เบ็ดเตล็ด (ตัวเลข/เทสต์)"
    ),
    # ---- 03 แคมเปญนอร์มังดี (แยกตามภารกิจ) ----
    Section(
        "03_normandy", "m01_dday", "m01_dday.csv", _r((200000, 219001)), None, "บทพูด/ภารกิจ M01 ดีเดย์"
    ),
    Section(
        "03_normandy",
        "m02_paradrop",
        "m02_paradrop.csv",
        _r((219001, 230000)),
        None,
        "บทพูด/ภารกิจ M02 โดดร่ม",
    ),
    Section(
        "03_normandy",
        "m03_carentan",
        "m03_carentan.csv",
        _r((230000, 240000)),
        None,
        "บทพูด/ภารกิจ M03 คารองต็อง",
    ),
    Section(
        "03_normandy",
        "m04_carentan_counter",
        "m04_carentan_counter.csv",
        _r((240000, 250000)),
        None,
        "บทพูด/ภารกิจ M04 คารองต็องโต้กลับ",
    ),
    Section(
        "03_normandy",
        "m05_redball",
        "m05_redball.csv",
        _r((250000, 260000)),
        None,
        "บทพูด/ภารกิจ M05 เรดบอลเอ็กซ์เพรส",
    ),
    Section(
        "03_normandy",
        "m06_cherbourg",
        "m06_cherbourg.csv",
        _r((260000, 270000)),
        None,
        "บทพูด/ภารกิจ M06 แชร์บูร์ก",
    ),
    Section(
        "03_normandy", "m07_v2", "m07_v2.csv", _r((270000, 280000)), None, "บทพูด/ภารกิจ M07 จรวด V2"
    ),
    Section(
        "03_normandy",
        "m08_artillery",
        "m08_artillery.csv",
        _r((280000, 289001)),
        None,
        "บทพูด/ภารกิจ M08 ปืนใหญ่ประชัน",
    ),
    Section(
        "03_normandy",
        "m09_hill192",
        "m09_hill192.csv",
        _r((289001, 300000)),
        None,
        "บทพูด/ภารกิจ M09 เนิน 192",
    ),
    Section(
        "03_normandy",
        "m10_stlo",
        "m10_stlo.csv",
        _r((300000, 310000)),
        None,
        "บทพูด/ภารกิจ M10 สต.โลโต้กลับ",
    ),
    Section(
        "03_normandy",
        "m12_division",
        "m12_division.csv",
        _r((310000, 320000)),
        None,
        "บทพูด/ภารกิจ M12 มรณกรรมของกองพล",
    ),
    Section(
        "03_normandy",
        "m13_mortain",
        "m13_mortain.csv",
        _r((320000, 330000)),
        None,
        "บทพูด/ภารกิจ M13 มอร์แตง",
    ),
    Section(
        "03_normandy",
        "m14_mortain_counter",
        "m14_mortain_counter.csv",
        _r((330000, 360000)),
        None,
        "บทพูด/ภารกิจ M14 มอร์แตงโต้กลับ",
    ),
    Section(
        "03_normandy",
        "m15_tiger",
        "m15_tiger.csv",
        _r((360000, 369000)),
        None,
        "บทพูด/ภารกิจ M15 เสือจนมุม",
    ),
    Section(
        "03_normandy",
        "m16_chambois",
        "m16_chambois.csv",
        _r((369000, 400000)),
        None,
        "บทพูด/ภารกิจ M16 ช็องบัว",
    ),
    Section("03_normandy", "tutorial", "tutorial.csv", _r((400000, 500000)), None, "บทเรียน/เทรนนิ่ง"),
    # ---- 04 แคมเปญเสริม ----
    Section(
        "04_expansions",
        "01_caen_mg",
        "01_caen_mg.csv",
        _r((1300000, 1500000)),
        None,
        "แคมเปญก็อง+มาร์เก็ตการ์เดน (บทพูดภารกิจ)",
    ),
    Section(
        "04_expansions",
        "02_market_garden",
        "02_market_garden.csv",
        _r((7000000, 7500000)),
        None,
        "แคมเปญมาร์เก็ตการ์เดน (บทพูดภารกิจ)",
    ),
    Section(
        "04_expansions",
        "03_tiger_ace",
        "03_tiger_ace.csv",
        _r((6000000, 6100000), (9300000, 9600000)),
        None,
        "แคมเปญไทเกอร์เอซ (บทพูดเยอรมัน)",
    ),
    Section(
        "04_expansions",
        "04_operations",
        "04_operations.csv",
        _r((10000000, 10100000)),
        None,
        "โหมดปฏิบัติการ (Falaise/Causeway)",
    ),
    Section(
        "04_expansions",
        "05_tov_briefing",
        "05_tov_briefing.csv",
        _r((11000000, 12000000)),
        None,
        "บรีฟภารกิจ Tales of Valor",
    ),
    # ---- 05 เสียงพากย์ ----
    Section(
        "05_speech",
        "01_numbers",
        "01_numbers.csv",
        _r((800000, 900000), (6900000, 7000000)),
        None,
        "เสียงพากย์: ตัวเลขเสียง",
    ),
    Section(
        "05_speech",
        "02_radio",
        "02_radio.csv",
        _r((90000, 200000)),
        None,
        "เสียงพากย์: ข้อความวิทยุ/รับคำสั่ง",
    ),
)

# range เดียวใช้สองที่ (UNITS_RANGE ถูก 02_units kind ใช้ และ 05_speech/02_radio ใช้ไม่ได้)
# — ต้องไม่ซ้อน: ลบ 02_radio ออกเพราะ (90000,200000) ชนกับ UNITS_RANGE
SECTIONS = tuple(s for s in SECTIONS if s.key != "02_radio")

_NAME_RE = re.compile(r"^[A-Z0-9].*$")


def classify_kind(english: str) -> str:
    s = english.strip()
    if not s:
        return "other"
    if s.startswith(STAT_PREFIX):
        return "stat"
    if len(s) <= _NAME_MAX_LEN and _NAME_RE.match(s) and not re.search(r"\s[a-z]", s):
        return "name"
    if len(s) <= _NAME_MAX_LEN:
        return "name"
    return "desc"


def _in_ranges(sid: int, ranges: tuple[tuple[int, int], ...]) -> bool:
    return any(lo <= sid < hi for lo, hi in ranges)


def section_of(sid: int, english: str) -> Section:
    for sec in SECTIONS:
        if _in_ranges(sid, sec.ranges) and (sec.kind is None or classify_kind(english) == sec.kind):
            return sec
    raise ValueError(f"id {sid} not covered by SECTIONS (english={english[:40]!r})")
