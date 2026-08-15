import csv
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

FILES = [
    "work/translate_parts_v2/04_expansions/01_caen_mg.csv",
    "work/translate_parts_v2/04_expansions/02_market_garden.csv",
    "work/translate_parts_v2/04_expansions/03_tiger_ace.csv",
    "work/translate_parts_v2/04_expansions/04_operations.csv",
    "work/translate_parts_v2/04_expansions/05_tov_briefing.csv",
    "work/translate_parts_v2/05_speech/01_numbers.csv",
]

def final_check():
    total_checked = 0
    all_issues = []
    
    # Check forbidden words or MT bugs
    bad_patterns = [
        (r'พล\.ท\. งานฝีมือ|จีที Craft|ร้อยโท ประดิษฐ์|พล\.ท\. หัตถกรรม|จ่าหัตถกรรม|จีที งานฝีมือ', 'Bad Craft rank/name'),
        (r'นาวาโท|ร\.ท\.\s*เบลีย์', 'Bad Bailey rank'),
        (r'คปล\.|ซีพีแอล\s*เดกแนน|ซีพีแอล\s*ดิลลิงแฮม', 'Bad Cpl transliteration'),
        (r'กัปตันคัตติ้ง', 'Bad Captain Cutting rank'),
        (r'วิชาเอก', 'Major translated as subject/major'),
        (r'สองเท่านะหนุ่มๆ|บนดับเบิ้ล', 'Bad double quick'),
        (r'เช็คไฟ', 'Bad check fire'),
        (r'ปิดไฟ', 'Bad covering fire as turn off light'),
        (r'ความเหนือกว่าของไฟ', 'Bad fire superiority'),
        (r'หิ่งห้อย', 'Sherman Firefly translated as firefly insect'),
        (r'ปกปิดลา|บันทึกลา', 'Arse translated as donkey'),
        (r'นั่งตัวแทน', 'Sit-Rep translated as sit agent'),
        (r'โหม็อด', 'Typo โหม็อด'),
        (r'โวส\b|วอสส์\b(?! \(Hauptmann Voss\))', 'Voss check'),
        (r'ชูลท์ซ|ชูลซ์(?! \(Feldwebel Schultz\))', 'Schultz check'),
    ]
    
    for fpath in FILES:
        p = Path(fpath)
        with open(p, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for r in reader:
                total_checked += 1
                sid = r['id']
                e = r['english']
                t = r['thai']
                
                for pat, desc in bad_patterns:
                    if re.search(pat, t):
                        # Filter out false positives if any
                        all_issues.append((str(p), sid, desc, e, t))
                        
    print(f"Total rows scanned: {total_checked}")
    print(f"Total issues detected: {len(all_issues)}")
    for iss in all_issues:
        print(f"[{iss[0]} : {iss[1]}] {iss[2]}\n  EN: {iss[3]}\n  TH: {iss[4]}\n")

if __name__ == '__main__':
    final_check()
