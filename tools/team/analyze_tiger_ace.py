import csv
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def detailed_tiger_ace_analysis():
    p = Path("work/translate_parts_v2/04_expansions/03_tiger_ace.csv")
    with open(p, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Total rows in Tiger Ace: {len(rows)}")
    
    # Check for all specific patterns we need to polish
    fixes = []
    for r in rows:
        sid = r['id']
        e = r['english']
        t = r['thai']
        
        reasons = []
        
        # 1. Names / Ranks
        # Voss -> ร้อยเอกฟอสส์ (Hauptmann Voss) or ฟอสส์ (Voss)
        if 'voss' in e.lower() and ('โวส' in t or 'วอสส์' in t):
            reasons.append('Voss typo')
        # Schultz / Shultz -> ชูลทซ์ (Schultz)
        if ('schultz' in e.lower() or 'shultz' in e.lower()) and any(k in t for k in ['ชูลซ์', 'ชูลท์ซ', 'ชัลทซ์', 'ซูลทซ์']):
            reasons.append('Schultz typo')
        # Schroif -> ชรอยฟ์ (Schroif)
        if 'schroif' in e.lower() and ('ชรอยฟ' in t and not 'ชรอยฟ์' in t):
            reasons.append('Schroif typo')
        # Berndt -> แบร์นดท์
        if 'berndt' in e.lower() and not 'แบร์นดท์' in t:
            reasons.append('Berndt typo')
        # Sgt. Craft -> จ่าคราฟต์
        if 'craft' in e.lower() and ('งานฝีมือ' in t or 'คราฟ' in t or 'หัตถกรรม' in t or 'ประดิษฐ์' in t or 'จีที' in t or 'Craft' in t or 'คราฟท์' in t):
            reasons.append('Craft issue')
            
        # 2. Places / Proper names
        # Villers-Bocage -> วีแลร์-โบกาฌ (Villers-Bocage)
        if 'villers' in e.lower() and any(k in t for k in ['วิลเลอร์ส', 'วิลเลร์ส', 'วิลล่า', 'Villers']):
            reasons.append('Villers-Bocage translit')
        # Tiger 205 -> ไทเกอร์ 205
        if 'tiger' in e.lower() and 'เสือ' in t:
            reasons.append('Tiger as เสือ')
        # Desert Rats -> หนูทะเลทราย (Desert Rats)
        if 'desert rats' in e.lower() and 'Desert Rats' not in t:
            reasons.append('Desert Rats')
            
        # 3. Combat terms
        # Feuer frei! -> เปิดฉากยิงได้!
        if 'feuer frei' in e.lower():
            reasons.append('Feuer frei')
        # Fire / Direct Fire / Hold fire / Open fire / Taking fire
        if re.search(r'\b(direct fire)\b', e, re.I) and not 'การเล็งยิงโดยตรง' in t:
            reasons.append('Direct Fire')
        if 'open fire' in e.lower() and 'เปิดไฟ' in t:
            reasons.append('Open fire -> เปิดไฟ')
        if 'hold fire' in e.lower() and 'ไฟ' in t:
            reasons.append('Hold fire -> ไฟ')
        if 'check fire' in e.lower() and 'เช็คไฟ' in t:
            reasons.append('Check fire -> เช็คไฟ')
        if 'fire' in e.lower().split() and 'ไฟ' in t and not any(k in e.lower() for k in ['campfire', 'firefly', 'flame']):
            # check if it's fire weapon/shoot
            reasons.append('Fire -> ไฟ')
            
        # 4. Cover
        if re.search(r'\bcover\b', e, re.I) and any(k in t for k in ['ปกปิด', 'ปิดบัง']):
            reasons.append('Cover -> ปกปิด')
            
        # 5. Sector
        if re.search(r'\bsector\b', e, re.I) and 'ภาค' in t:
            reasons.append('Sector -> ภาค')
            
        # 6. Tommies / Jerry / Kraut
        if 'tommies' in e.lower() or 'tommy' in e.lower():
            if 'ทอมมี่' in t or 'ทหารอังกฤษ' in t:
                pass
                
        # 7. Untranslated / bad MT phrasing
        if 'The problem is' in t or 'No Key' in t:
            if '$' not in e:
                reasons.append('English leftover')

        if reasons:
            fixes.append((sid, reasons, e, t))

    print(f"Total potential issues in Tiger Ace: {len(fixes)}")
    for f in fixes[:40]:
        print(f"[{f[0]}] {f[1]} | EN: {f[2]} | TH: {f[3]}")

if __name__ == '__main__':
    detailed_tiger_ace_analysis()
