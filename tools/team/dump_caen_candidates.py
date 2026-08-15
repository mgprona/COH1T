import csv
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

FILE = Path("work/translate_parts_v2/04_expansions/01_caen_mg.csv")

def extract_all():
    with open(FILE, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    for r in rows:
        sid = r['id']
        e = r['english']
        t = r['thai']
        
        # Check if row needs polish
        cond = (
            any(w in e.lower() for w in ['craft', 'bailey', 'degnan', 'dillingham', 'cutting', 'blackmore', 'wallis', 'wood', 'firefly', 'walking barrage', 'creeping barrage', 'det charge', 'demolition charge', 'bren gunner', 'the gen'])
            or any(w in t for w in ['งานฝีมือ', 'หัตถกรรม', 'ประดิษฐ์', 'จีที', 'นาวาโท', 'ร.ท.', 'คปล', 'ซีพีแอล', 'กัปตัน', 'วิชาเอก', 'หิ่งห้อย', 'ปิดไฟ', 'เช็คไฟ', 'ความเหนือกว่าของไฟ', 'ปืนใหญ่ไฟ', 'ปกปิด', 'ปิดบัง', 'ปูน', 'ภาคปลอดภัย', 'บันทึกลา', 'ปกปิดลา'])
            or ('เสือ' in t and not any(w in t for w in ['ไทเกอร์', 'เสือจนมุม']))
            or (re.search(r'\bsector\b', e, re.I) and ('ภาค' in t and 'ภาคสนาม' not in t and 'ภาคพื้น' not in t))
            or (re.search(r'\b(double quick|on the double)\b', e, re.I) and 'สองเท่า' in t)
            or (re.search(r'\bmajor\b', e, re.I) and 'ผู้พัน' in t)
        )
        if cond:
            print(f"{sid} | EN: {e} | TH: {t}")

if __name__ == '__main__':
    extract_all()
