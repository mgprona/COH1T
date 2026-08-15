import csv
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def analyze_caen_blocks():
    p = Path("work/translate_parts_v2/04_expansions/01_caen_mg.csv")
    with open(p, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # ID ranges
    id_prefixes = {}
    for r in rows:
        prefix = r['id'][:3]
        id_prefixes[prefix] = id_prefixes.get(prefix, 0) + 1
    print("ID prefixes:", sorted(id_prefixes.items()))

if __name__ == '__main__':
    analyze_caen_blocks()
