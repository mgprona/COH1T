import csv
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def scan_file(path_str):
    p = Path(path_str)
    print(f"=== Scanning {p.name} ({p}) ===")
    with open(p, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"Total rows: {len(rows)}")
    
    issues = []
    for r in rows:
        sid = r['id']
        e = r['english']
        t = r['thai']
        
        # 1. Ranks / Names
        if 'craft' in e.lower() and not any(k in t for k in ['คราฟต์', 'คราฟท์', 'คราฟ']):
            issues.append((sid, "Craft missing/misnamed", e, t))
        if any(k in t for k in ['งานฝีมือ', 'หัตถกรรม', 'ประดิษฐ์', 'จีที Craft', 'จีที งานฝีมือ', 'พล.ท. งานฝีมือ', 'พล.ท. หัตถกรรม', 'จ่าหัตถกรรม', 'ร้อยโท ประดิษฐ์']):
            issues.append((sid, "Craft bad translation", e, t))
        if 'bailey' in e.lower() and any(k in t for k in ['นาวาโท', 'ร.ท.', 'เบลีย์']):
            if 'นาวาโท' in t or 'ร.ท.' in t or 'เบลีย์' not in t:
                issues.append((sid, "Bailey rank", e, t))
        if 'degnan' in e.lower() and 'คปล' in t:
            issues.append((sid, "Degnan Cpl", e, t))
        if 'dillingham' in e.lower() and ('ซีพีแอล' in t or 'คปล' in t):
            issues.append((sid, "Dillingham Cpl", e, t))
        if 'voss' in e.lower() and ('โวส' in t or 'วอสส์' in t):
            issues.append((sid, "Voss spelling", e, t))
        if 'schroif' in e.lower() and ('ชรอยฟ์' not in t and 'ชรอยฟ' not in t):
            issues.append((sid, "Schroif spelling", e, t))
        if 'schultz' in e.lower() or 'shultz' in e.lower():
            if 'ชูลทซ์' not in t and 'ชูลท์ซ' not in t and 'ชูลซ์' not in t:
                issues.append((sid, "Schultz spelling", e, t))
                
        # 2. Fire vs ไฟ
        if re.search(r'\b(fire|firing|fired)\b', e, re.I):
            # check if translated as ไฟ inappropriately
            t_no_flame = re.sub(r'เครื่องพ่นไฟ|กระสุนเพลิง|ลูกไฟ|กองไฟ|เพลิง|ไฟร์ฟลาย', '', t)
            if 'ไฟ' in t_no_flame:
                # check if english meant shoot/shell/fire weapon
                if any(k in e.lower() for k in ['open fire', 'hold fire', 'taking fire', 'under fire', 'return fire', 'direct fire', 'mortar fire', 'rapid fire', 'cease fire', 'fire!']):
                    issues.append((sid, "Fire as ไฟ", e, t))
                elif re.search(r'\bfire\b', e, re.I) and not any(k in e.lower() for k in ['firefly', 'campfire', 'bonfire', 'wildfire']):
                    issues.append((sid, "Fire as ไฟ (general)", e, t))

        # 3. Cover vs ปกปิด/ปิดบัง
        if re.search(r'\bcover\b', e, re.I) and any(k in t for k in ['ปกปิด', 'ปิดบัง']):
            issues.append((sid, "Cover as ปกปิด/ปิดบัง", e, t))
            
        # 4. Tiger / Panther
        if re.search(r'\btiger\b', e, re.I) and 'เสือ' in t and not 'ไทเกอร์' in t:
            if not 'เสือจนมุม' in t and not 'เขี้ยวเล็บ' in t:
                issues.append((sid, "Tiger as เสือ", e, t))
        if re.search(r'\bpanther\b', e, re.I) and 'เสือดำ' in t and not 'แพนเธอร์' in t:
            issues.append((sid, "Panther as เสือดำ", e, t))
            
        # 5. Mortar vs ปูน
        if 'mortar' in e.lower() and 'ปูน' in t and not any(k in t for k in ['ปูนปลาสเตอร์', 'ปูนขาว', 'ปูนซีเมนต์']):
            issues.append((sid, "Mortar as ปูน", e, t))
            
        # 6. Sector vs ภาค
        if 'sector' in e.lower() and ('ภาค' in t and 'ภาคสนาม' not in t and 'ภาคพื้น' not in t):
            # check if used as sector / เซกเตอร์ / พื้นที่
            issues.append((sid, "Sector as ภาค", e, t))
            
        # 7. English slang / expressions
        if 'double' in e.lower() and 'สองเท่า' in t:
            issues.append((sid, "Double as สองเท่า", e, t))
        if any(k in e.lower() for k in ['gents', 'lads', 'mates']) and any(k in t for k in ['หนุ่มๆ', 'เด็กๆ', 'เพื่อนๆ']):
            # check context
            pass
        if 'gen' in e.lower().split() and any(k in t for k in ['เจน', 'พล.']):
            issues.append((sid, "Gen as เจน/พล", e, t))
            
        # 8. Placeholders / formatting
        # check unescaped or broken english sentences left
        if re.search(r'[A-Za-z]{4,}\s+[A-Za-z]{4,}\s+[A-Za-z]{4,}', t):
            # large english chunks left in thai
            issues.append((sid, "Untranslated Latin phrase", e, t))

    print(f"Found {len(issues)} candidate issues.")
    for iss in issues[:35]:
        print(f"  [{iss[1]}] {iss[0]} | EN: {iss[2]} | TH: {iss[3]}")
    return issues

if __name__ == '__main__':
    for f in [
        "work/translate_parts_v2/04_expansions/03_tiger_ace.csv",
        "work/translate_parts_v2/04_expansions/01_caen_mg.csv"
    ]:
        scan_file(f)
