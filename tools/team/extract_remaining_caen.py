import csv
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

FILE = Path("work/translate_parts_v2/04_expansions/01_caen_mg.csv")

def extract_remaining_caen():
    with open(FILE, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    for r in rows:
        sid = r['id']
        e = r['english']
        t = r['thai']
        
        # Look for bad patterns
        cond = (
            any(w in t for w in ['วิชาเอก', 'นั่งตัวแทน', 'ดินระเบิดสาธิต', 'บนดับเบิ้ล', 'จับจุดนั้น', 'เดญง', 'กงอยู่ในมือ', 'ถือสายไว้', 'ภาคที่ถูกจับกุม', 'ปิดบังโพสต์', 'พื้นปูนปกคลุม', 'ปกปิดลา', 'ลูกเสือ', 'ผู้บุกเบิกการทำลายล้าง', 'ผู้บุกเบิกผู้ก่อวินาศกรรม', 'ความเหนือกว่าของไฟ'])
            or any(w in e.lower() for w in ['sit-rep', 'sitrep', 'on the double', 'double quick', 'bren gunner']) and any(w in t for w in ['นั่ง', 'ดับเบิ้ล', 'สองเท่า', 'เบรน กันเนอร์'])
            or ('degnan' in e.lower() and 'สิบโท' not in t and 'เดกแนน' not in t)
            or ('bailey' in e.lower() and 'ร้อยโท' not in t and 'ผู้หมวด' not in t)
            or ('blackmore' in e.lower() and 'พันตรี' not in t)
            or ('cutting' in e.lower() and 'ร้อยเอก' not in t)
            or ('wallis' in e.lower() and 'ร้อยเอก' not in t)
            or ('wood' in e.lower() and 'captain' in e.lower() and 'ร้อยเอก' not in t)
        )
        if cond:
            print(f"{sid} | EN: {e} | TH: {t}")

if __name__ == '__main__':
    extract_remaining_caen()
