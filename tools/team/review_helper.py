import csv
import sys
from pathlib import Path

def dump_csv(filepath, start=0, count=100):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(filepath, encoding='utf-8-sig') as f:
        reader = list(csv.DictReader(f))
    print(f"Total rows in {filepath}: {len(reader)}")
    for i, r in enumerate(reader[start:start+count], start=start):
        print(f"[{i}] {r['id']}: EN: {r['english']}")
        print(f"    TH: {r['thai']}")
        print("-" * 60)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        dump_csv(sys.argv[1], start, count)
