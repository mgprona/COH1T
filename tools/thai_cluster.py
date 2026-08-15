MARK_RANGES = ((0x0E31, 0x0E31), (0x0E34, 0x0E3A), (0x0E47, 0x0E4E))


def is_thai(ch: str) -> bool:
    return 0x0E00 <= ord(ch) <= 0x0E7F


def _is_mark(ch: str) -> bool:
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in MARK_RANGES)


def tokenize_clusters(text: str) -> list[str]:
    clusters: list[str] = []
    for ch in text:
        if clusters and _is_mark(ch):
            clusters[-1] += ch
        else:
            clusters.append(ch)
    return clusters
