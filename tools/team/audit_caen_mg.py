import csv
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

FILE = Path("work/translate_parts_v2/04_expansions/01_caen_mg.csv")

def extract_all_caen_issues():
    with open(FILE, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print(f"Total rows in Caen/MG: {len(rows)}")
    
    issues = []
    for r in rows:
        sid = r['id']
        e = r['english']
        t = r['thai']
        
        reasons = []
        
        # 1. Ranks / Names
        if 'craft' in e.lower():
            if not any(k in t for k in ['จ่าคราฟต์', 'คราฟต์']):
                reasons.append("Craft issue")
        if 'bailey' in e.lower():
            if 'ร้อยโทเบลีย์' not in t and 'เบลีย์' in t:
                reasons.append("Bailey rank")
        if 'degnan' in e.lower() and ('คปล' in t or 'ซีพีแอล' in t or 'สิบโทเดกแนน' not in t):
            reasons.append("Degnan Cpl")
        if 'dillingham' in e.lower() and ('ซีพีแอล' in t or 'คปล' in t or 'สิบโทดิลลิงแฮม' not in t and 'ดิลลิงแฮม' in t):
            reasons.append("Dillingham Cpl")
        if 'cutting' in e.lower() and ('กัปตัน' in t or 'ร้อยเอกคัตติ้ง' not in t):
            reasons.append("Cutting rank")
        if 'captain' in e.lower() and 'กัปตัน' in t:
            reasons.append("Captain rank")
        if re.search(r'\bmajor\b', e, re.I) and ('วิชาเอก' in t or 'ผู้พัน' in t):
            reasons.append("Major rank")
            
        # 2. Slang & Expressions
        if 'that\'s the gen' in e.lower() or 'thats the gen' in e.lower() or 'the gen' in e.lower():
            if any(k in t for k in ['เจน', 'พล.']):
                reasons.append("Gen issue")
        if 'double quick' in e.lower() or 'on the double' in e.lower():
            if 'สองเท่า' in t:
                reasons.append("Double quick")
        if 'firefly' in e.lower() and 'หิ่งห้อย' in t:
            reasons.append("Firefly as หิ่งห้อย")
        if 'walking barrage' in e.lower() and not ('ระดมยิงม่านกระสุนเคลื่อนที่' in t):
            reasons.append("Walking barrage")
        if 'creeping barrage' in e.lower() and not ('ระดมยิงม่านกระสุนคืบคลาน' in t):
            reasons.append("Creeping barrage")
        if 'demolition charge' in e.lower() or 'det charge' in e.lower():
            if 'ดินระเบิดทำลายล้าง' not in t and 'ดินระเบิด' not in t:
                reasons.append("Demolition charge")
        if 'bren gunner' in e.lower() and 'พลปืนเบรน' not in t:
            reasons.append("Bren gunner")
            
        # 3. Fire / Cover / Mortar / Sector / Bail / Pinned / Garrison / Arse
        if re.search(r'\b(open fire|hold fire|check fire|covering fire|fire superiority|fire artillery|taking fire|under fire)\b', e, re.I):
            if any(k in t for k in ['เปิดไฟ', 'เช็คไฟ', 'ปิดไฟ', 'ความเหนือกว่าของไฟ', 'ปืนใหญ่ไฟ', 'ถูกไฟไหม้', 'ลุกไหม้', 'โซนไฟ']):
                reasons.append("Fire issue")
        if re.search(r'\bcover\b', e, re.I) and any(k in t for k in ['ปกปิด', 'ปิดบัง']):
            reasons.append("Cover issue")
        if re.search(r'\btiger\b', e, re.I) and 'เสือ' in t and not any(k in t for k in ['ไทเกอร์', 'เสือจนมุม']):
            reasons.append("Tiger as เสือ")
        if 'mortar' in e.lower() and 'ปูน' in t and not any(k in t for k in ['ปูนปลาสเตอร์', 'ปูนขาว', 'ปูนซีเมนต์']):
            reasons.append("Mortar as ปูน")
        if re.search(r'\bsector\b', e, re.I) and ('ภาค' in t and not 'ภาคพื้น' in t and not 'ภาคสนาม' in t):
            reasons.append("Sector as ภาค")
        if 'arse' in e.lower() and 'ลา' in t:
            reasons.append("Arse as ลา")
        if 'bail out' in e.lower() and 'ประกันตัว' in t:
            reasons.append("Bail out as ประกันตัว")
        if 'pinned' in e.lower() and 'ปักหมุด' in t:
            reasons.append("Pinned as ปักหมุด")
        if 'garrison' in e.lower() and 'คุมขัง' in t:
            reasons.append("Garrison as คุมขัง")
            
        if reasons:
            issues.append((sid, reasons, e, t))
            
    print(f"Total issues found in Caen/MG: {len(issues)}")
    for sid, r, e, t in issues[:50]:
        print(f"[{sid}] {r}\n  EN: {e}\n  TH: {t}\n")

if __name__ == '__main__':
    extract_all_caen_issues()
