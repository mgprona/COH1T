import csv
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

FILE = Path("work/translate_parts_v2/04_expansions/03_tiger_ace.csv")

def audit_tiger_ace():
    with open(FILE, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print(f"Total rows in {FILE}: {len(rows)}")
    issues = []
    
    for r in rows:
        sid = r['id']
        e = r['english']
        t = r['thai']
        
        # Check specific problematic words
        problems = []
        if 'craft' in e.lower() and not ('คราฟต์' in t or 'จ่าคราฟต์' in t):
            problems.append(f"Craft: {t}")
        if any(w in t for w in ['งานฝีมือ', 'หัตถกรรม', 'ประดิษฐ์', 'จีที Craft', 'จีที งานฝีมือ', 'พล.ท. งานฝีมือ', 'จ่าหัตถกรรม']):
            problems.append(f"Bad Craft: {t}")
        if 'voss' in e.lower() and ('โวส' in t or 'วอสส์' in t):
            problems.append(f"Voss: {t}")
        if ('schultz' in e.lower() or 'shultz' in e.lower()) and not any(w in t for w in ['ชูลทซ์', 'ชูลต์ซ', 'ชูลทซ์']):
            problems.append(f"Schultz: {t}")
        if 'schroif' in e.lower() and not ('ชรอยฟ์' in t):
            problems.append(f"Schroif: {t}")
        if 'berndt' in e.lower() and not ('แบร์นดท์' in t):
            problems.append(f"Berndt: {t}")
        if 'villers' in e.lower() and ('วิลเลอร์ส' in t or 'วิลเลร์ส' in t or 'วิลล่า' in t or 'โบคาจ' in t):
            problems.append(f"Villers-Bocage: {t}")
        if 'tiger' in e.lower() and 'เสือ' in t and 'ไทเกอร์' not in t:
            if not 'เสือจนมุม' in t:
                problems.append(f"Tiger as เสือ: {t}")
        if re.search(r'\bdirect fire\b', e, re.I) and not ('การเล็งยิงโดยตรง' in t or 'เล็งยิงโดยตรง' in t):
            problems.append(f"Direct fire: {t}")
        if 'feuer frei' in e.lower() and not ('เปิดฉากยิง' in t or 'ยิงได้' in t):
            problems.append(f"Feuer frei: {t}")
        if re.search(r'\bcover\b', e, re.I) and any(w in t for w in ['ปกปิด', 'ปิดบัง']):
            problems.append(f"Cover: {t}")
        if re.search(r'\bsector\b', e, re.I) and 'ภาค' in t:
            problems.append(f"Sector: {t}")
        if re.search(r'\b(open fire|hold fire|taking fire|under fire|cease fire|check fire|fire!)\b', e, re.I) and 'ไฟ' in t:
            problems.append(f"Fire: {t}")
        if 'โหม็อด' in t:
            problems.append(f"Typo โหม็อด: {t}")
        if 'The problem is' in t:
            problems.append(f"Latin leak: {t}")
            
        if problems:
            issues.append((sid, problems, e, t))
            
    print(f"Total problematic rows found: {len(issues)}")
    for sid, probs, e, t in issues:
        print(f"ID {sid}: {probs}\n  EN: {e}\n  TH: {t}\n")

if __name__ == '__main__':
    audit_tiger_ace()
