import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

FILE = Path("work/translate_parts_v2/04_expansions/01_caen_mg.csv")

FIXES_7 = {
    "1311380": "ดูเหมือนฉันจะต้องเลี้ยงเบียร์ร้อยเอกคัตติ้งสักไพนต์สองไพนต์แล้วสิ",
    "1311390": "สิบโทเดกแนน ส่งข้อความตามสายบังคับบัญชาไปถึงร้อยเอกคัตติ้ง บอกเขาว่าพื้นที่ปลอดภัยแล้ว",
    "1330505": "ชูลทซ์ แกกำลังทำอะไรอยู่ตรงนั้น? กลับมานี่เดี๋ยวนี้!",
    "1390910": "เคลื่อนย้ายรถถังไฟร์ฟลาย (Sherman Fireflies) ให้อยู่นอกระยะยิงของรถถังหนักแพนเซอร์ และตรึงระยะไว้อย่างนั้น!",
    "1420680": "เรารู้หรือยังว่าเกิดอะไรขึ้น? ฉันได้ยินว่าพวกมันต้องการตัวพลตรีฟอสส์ (Generalmajor Voss)!",
    "1422390": "พลตรีฟอสส์ (Generalmajor Voss) กำลังเดินทางมาจากอาร์เนมครับ ร้อยเอกแบร์เกอร์ (Hauptmann Berger)",
    "1481286": "เราต้องรักษาแรงกดดันต่อกองกำลังข้าศึกในโอสเตร์เบก (Oosterbeek) ต่อไปเพื่อชัยชนะ คำสั่งของท่านคืออะไรครับ พลตรีฟอสส์ (Generalmajor Voss)?",
}

def apply():
    rows = []
    with open(FILE, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            sid = r['id']
            if sid in FIXES_7:
                r['thai'] = FIXES_7[sid]
            rows.append(r)
            
    with open(FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Applied 7 fixes to {FILE}")

if __name__ == '__main__':
    apply()
