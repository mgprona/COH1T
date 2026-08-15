import csv
import sys
from pathlib import Path

FILE = Path("work/translate_parts_v2/03_normandy/m16_chambois.csv")

UPDATES = {
    "369001": "ช็องบัวส์ (Chambois), 14:25 น. วันที่ 19 สิงหาคม",
    "369025": "ตรวจพบขบวนยานยนต์ฝ่ายอักษะ!",
    "369030": "เชื่อมต่อเซกเตอร์อาณาเขตทางใต้เข้ากับแนวหน้าของกองทัพแคนาดาทางทิศเหนือ ยึดจุดยุทธศาสตร์ที่กำหนดเพื่อปิดวงล้อมฟาเลส์ (Falaise Pocket) ให้ทันเวลา!",
    "369031": "ทำลายขบวนยานยนต์ฝ่ายอักษะ",
    "369033": "ทำลายขบวนยานยนต์ฝ่ายอักษะที่กำลังถอยร่นทั้งหมดก่อนที่พวกมันจะหนีผ่านช็องบัวส์ (Chambois) ไปได้ การควบคุมสะพานจะช่วยจำกัดเส้นทางหลบหนีของขบวนรถ",
    "369035": "เชื่อมต่ออาณาเขตเข้ากับกองกำลังสัมพันธมิตร",
    "369050": "ยึดสะพานได้แล้ว",
    "369920": "เป้าหมายสำเร็จ: เชื่อมต่ออาณาเขตของคุณกับฝ่ายสัมพันธมิตรก่อนหมดเวลา!",
    "369950": "สร้างความสูญเสียให้ข้าศึก 300 นาย",
    "369951": "สร้างความสูญเสียให้แก่กองทัพที่ 7 ของเยอรมันให้ได้มากที่สุด",
}

def apply_updates():
    rows = []
    with open(FILE, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            sid = r['id']
            if sid in UPDATES:
                r['thai'] = UPDATES[sid]
            rows.append(r)
            
    with open(FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Applied {len(UPDATES)} updates to {FILE}")

if __name__ == '__main__':
    apply_updates()
