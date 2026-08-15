import csv
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

FILE = Path("work/translate_parts_v2/04_expansions/03_tiger_ace.csv")

MORE_TIGER_ACE_UPDATES = {
    "6022010": "ชูลทซ์! ชูลทซ์! มีคนเจ็บ! เอาชุดปฐมพยาบาลมารักษาเขาเร็ว!",
    "6030503": "นั่นเป็นครั้งสุดท้ายที่ฉันได้เห็นภายในของรถถังไทเกอร์ และเป็นครั้งสุดท้ายที่ฉันได้เห็นชูลทซ์",
    "6031090": "กองบัญชาการ นี่คือกองพลเลร์ (Lehr) เครื่องบินอังกฤษกำลังบินเข้ามา ขอกำลังเสริมด่วน!",
    "6031430": "ชูลทซ์ เก็บกระสุนเจาะเกราะ (AP) ไว้สำหรับรถถัง! ใช้ปืนกลจัดการพวกยานเกราะเบา",
    "6031470": "ชูลทซ์! อย่ายิงกระสุนเจาะเกราะ (AP) ทิ้งขว้าง เราอาจจำเป็นต้องใช้มัน!",
    "6031480": "ให้ตายสิ (Verdammt)! แกอยากโดนลดขั้นรึไง ชูลทซ์? กระสุนเจาะเกราะ (AP) มีไว้สำหรับรถถัง!",
    "6031713": "กลับลำรถถังเดี๋ยวนี้ ชรอยฟ์! เราต้องรอกำลังเสริมจากทหารเกรนาเดียร์ก่อนจะเข้าตีวีแลร์-โบกาฌ (Villers-Bocage)",
    "6031714": "เลิกเล่นบ้าๆ ซะที ชรอยฟ์! แกจะพาพวกเราตายกันหมด! เราต้องกวาดล้างเส้นทางบนถนน!",
    "6031718": "เปลี่ยนตำแหน่งรถถังเดี๋ยวนี้ ชรอยฟ์! ป้องกันปีกข้างของเราไว้!",
    "6031725": "ชรอยฟ์ เริ่มการซ่อมแซมสนามได้",
    "6031727": "เราต้องซ่อมรถถัง! ชรอยฟ์ จัดการเลย!",
    "6031735": "ยิงได้ดีมาก ชูลทซ์! ฐานปืนกลศัตรูถูกทำลายแล้ว",
    "6040600": "จ่าสิบเอกชูลทซ์ (Feldwebel Schultz) ยิงได้อย่างอิสระ",
    "6040660": "กลุ่มยานเกราะ (Panzergruppe) นี่คือร้อยเอกฟอสส์ (Hauptmann Voss) เราหยุดการบุกของข้าศึกได้แล้ว เป้าหมายทั้งหมดถูกกวาดล้างเรียบร้อย",
}

def apply():
    rows = []
    with open(FILE, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            sid = r['id']
            if sid in MORE_TIGER_ACE_UPDATES:
                r['thai'] = MORE_TIGER_ACE_UPDATES[sid]
            rows.append(r)
            
    with open(FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Applied additional updates to {FILE}")

if __name__ == '__main__':
    apply()
