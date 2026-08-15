import csv
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

FILE = Path("work/translate_parts_v2/04_expansions/03_tiger_ace.csv")

def print_all_candidates():
    with open(FILE, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    for r in rows:
        sid = r['id']
        e = r['english']
        t = r['thai']
        
        # We print all lines where improvements are needed
        cond = (
            any(w in e.lower() for w in ['craft', 'voss', 'schultz', 'shultz', 'schroif', 'berndt', 'litzke', 'villers', 'bocage', 'direct fire', 'feuer', 'tommies', 'tommy', 'jabo', 'tigergruppe', 'point 213', 'desert rats', 'panzer lehr'])
            or any(w in t for w in ['งานฝีมือ', 'หัตถกรรม', 'ประดิษฐ์', 'จีที', 'โวส', 'วอสส์', 'ชูลท์ซ', 'ชูลซ์', 'ชรอยฟ', 'เบิร์นดท์', 'วิลเลอร์ส', 'วิลเลร์ส', 'วิลล่า', 'โบคาจ', 'โหม็อด', 'ปกปิด', 'ปิดบัง', 'ปูน'])
            or ('เสือ' in t and 'ไทเกอร์' not in t and 'เสือจนมุม' not in t and 'เขี้ยวเล็บ' not in t)
            or (re.search(r'\bsector\b', e, re.I) and 'ภาค' in t)
            or (re.search(r'\b(fire|firing)\b', e, re.I) and 'ไฟ' in t and not any(k in e.lower() for k in ['campfire', 'firefly', 'flame', 'incendiary']))
        )
        if cond:
            print(f"SID: {sid}\n  EN: {e}\n  TH: {t}\n")

if __name__ == '__main__':
    print_all_candidates()
