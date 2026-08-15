import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

FILE = Path("work/translate_parts_v2/05_speech/01_numbers.csv")

NUMBERS_UPDATES = {
    "802001": "คุณแน่ใจหรือไม่ว่าต้องการเลือกกองร้อยนี้สำหรับผู้บังคับการของคุณ?",
    "802253": "วัตถุประสงค์เหรียญตรา",
    "802254": "คุณพ่ายแพ้",
    "802255": "คุณได้รับชัยชนะ",
    "802353": "สัญญาณที่เพื่อนร่วมทีมของคุณมองเห็นได้",
    "806805": "เลือกกองร้อยนี้สำหรับผู้บังคับการของคุณ?",
    "806829": "กำลังทางอากาศ",
    "806861": "การระดมยิงปืนใหญ่",
    "6901358": "พลบรรจุกระสุน ชึทเซอ ลิทซ์เคอ (Schütze Litzke)",
    "6901359": "พลวิทยุ ชึทเซอ แบร์นดท์ (Schütze Berndt)",
    "6901360": "พลปืน จ่าสิบเอกชูลทซ์ (Feldwebel Schultz)",
    "6901361": "พลขับ พลทหารอาวุโสชรอยฟ์ (Oberschütze Schroif)",
}

def apply():
    rows = []
    with open(FILE, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            sid = r['id']
            if sid in NUMBERS_UPDATES:
                r['thai'] = NUMBERS_UPDATES[sid]
            rows.append(r)
            
    with open(FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Applied updates to {FILE}")

if __name__ == '__main__':
    apply()
