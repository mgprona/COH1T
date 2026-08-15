import csv
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

FILE = Path("work/translate_parts_v2/04_expansions/01_caen_mg.csv")

def collect_caen_updates():
    with open(FILE, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print(f"Total rows in {FILE}: {len(rows)}")
    
    # We will build a detailed dictionary
    return rows

if __name__ == '__main__':
    collect_caen_updates()
