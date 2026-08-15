"""Survey the .ucs: print the first string of each 2k-id window with its id.

Read-only diagnostic to establish section block boundaries for tools/ucs_sections.py.
"""

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

WINDOW = 2000


def main() -> None:
    with open(r"backup\RelicCOH.English.ucs", encoding="utf-16") as fh:
        lines = fh.read().splitlines()
    entries: dict[int, str] = {}
    for l in lines:
        if not l:
            continue
        sid, _, v = l.partition("\t")
        if sid.isdigit():
            entries[int(sid)] = v
    ids = sorted(entries)
    lo = (ids[0] // WINDOW) * WINDOW
    hi = ((ids[-1] // WINDOW) + 1) * WINDOW
    prev_first = None
    for w in range(lo, hi, WINDOW):
        inwin = [i for i in ids if w <= i < w + WINDOW]
        if not inwin:
            continue
        first = inwin[0]
        text = entries[first][:60]
        marker = " <NEW>" if prev_first is None or first - prev_first > WINDOW else ""
        prev_first = first
        print(f"{first:>9}  {text}{marker}")


if __name__ == "__main__":
    main()
