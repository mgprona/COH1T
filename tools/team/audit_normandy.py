import csv
import glob
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

NORMANDY_DIR = "work/translate_parts_v2/03_normandy"

# Checks and bad patterns
BAD_PATTERNS = [
    # Fire errors
    (r"ไฟไหม้|ลุกเป็นไฟ|เปิดไฟ|ปิดไฟ|รีเทิร์นไฟ|ความเหนือกว่าของไฟ|เช็คไฟ|สายไฟ|รังไฟ|ดึงดูดไฟ|ไฟตรง|ไฟโดยตรง|ตกอยู่ใต้ไฟ|ใต้กองไฟ|ปืนไฟ", "Fire MT error (ยิง/กระสุน/เพลิง)"),
    # Cover errors
    (r"ปกปิด|คลุมไว้|ฝาครอบ|การปกปิด", "Cover MT error (ที่กำบัง)"),
    # Pinned errors
    (r"ปักหมุด", "Pinned MT error (ถูกยิงตรึงกำลัง)"),
    # Garrison errors
    (r"คุมขัง", "Garrison MT error (เข้าประจำการในอาคาร)"),
    # Dig in errors
    (r"ขุดเข้าไป|เจาะลึก", "Dig in MT error (ขุดสนามเพลาะ)"),
    # Fall back errors
    (r"ตกกลับ", "Fall back MT error (ถอยร่น/ถอนตัว)"),
    # Pillbox errors
    (r"กล่องยา|ยาเม็ด", "Pillbox MT error (บังเกอร์ป้อมปืน)"),
    # Bail out errors
    (r"ประกันตัว", "Bail out MT error (สละรถ)"),
    # At all costs errors
    (r"ค่าใช้จ่ายทั้งหมด|ระงับค่าใช้จ่าย", "At all costs MT error (ไม่ว่าจะแลกด้วยอะไรก็ตาม)"),
    # Vehicle errors
    (r"รถถังเสือ|เสือลูกเรือ|เร่งความเร็วเสือ|มีเสือเพียง|โทรหาเสือ|ทำลายเสือ|เสือทำลาย|กลุ่มการต่อสู้เสือดำ|เลือกเสือดำ", "Tiger/Panther MT error (ไทเกอร์/แพนเธอร์)"),
    (r"นักบวช", "Priest SPG MT error (พรีสต์)"),
    (r"ปูน(?!ปลาสเตอร์)|ปูนเกรียม|แท่นปูน|ประกอบด้วยปูน|กระสุนปูน|วางปูน|การสนับสนุนปูน", "Mortar MT error (ครก/ปืนครก)"),
    # Church errors
    (r"คริสตจักร", "Church MT error (โบสถ์)"),
    # Kraut/Jerry errors
    (r"กะหล่ำ|ทีมเจอร์รี่|เคราท์|เคราต์|Bloody Krauts", "Kraut/Jerry MT error (ไอ้เยอรมัน/พวกเยอรมัน)"),
    # Other MT idioms/mistranslations
    (r"ปาก 38", "Pak 38 MT error"),
    (r"แผ่นไม้มุงหลังคา|มุงหลังคา", "Shingle MT error (แนวหินกรวด)"),
    (r"กิเลส", "Defilade MT error (แนวลาดกำบัง/มุมอับกระสุน)"),
    (r"เป่าสายไฟ", "Blow the wire MT error (ระเบิดลวดหนาม)"),
    (r"กระเป๋าตังค์|กระเป๋าเงิน", "Satchel charge MT error (ระเบิดแรงสูง)"),
    (r"สีข้าง", "Flank MT error (ปีก/ปีกข้าง)"),
    (r"พระคริสต์บนจักรยาน|นรกใช่", "Idiom MT error"),
    (r"ลานจัดหา", "Supply yard MT error (ลานเสบียง)"),
    (r"เอเบิ้ล", "Able naming inconsistency (ควรเป็น เอเบิล)"),
    (r"ในอาคารในอาคาร|ที่กำบังที่กำบัง", "Repeated words"),
    (r"หม็อด", "Typo (หมด)"),
    (r"สิบห้าร้อย|ห้าสิบหกพัน", "Number translation unnatural"),
    (r"ได้รับการปกปิด|ได้รับการมุงหลังคา", "Passive MT defect"),
]

def audit_file(filepath):
    issues = []
    with open(filepath, encoding='utf-8-sig') as f:
        reader = list(csv.DictReader(f))
    
    for row in reader:
        sid = row['id']
        e = row['english']
        t = row.get('thai', '')
        
        # Check bad patterns
        for pattern, desc in BAD_PATTERNS:
            if re.search(pattern, t):
                issues.append((sid, desc, e, t))
                
    return len(reader), issues

def main():
    files = sorted(glob.glob(f"{NORMANDY_DIR}/*.csv"))
    total_issues = 0
    for f in files:
        count, issues = audit_file(f)
        total_issues += len(issues)
        print(f"\n{'='*70}")
        print(f"File: {f} ({count} rows, {len(issues)} flagged issues)")
        print(f"{'='*70}")
        for sid, desc, e, t in issues:
            print(f"[{sid}] {desc}")
            print(f"  EN: {e}")
            print(f"  TH: {t}")
    print(f"\n\nTotal flagged issues across Normandy: {total_issues}")

if __name__ == "__main__":
    main()
