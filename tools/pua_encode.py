import json
from collections.abc import Iterable
from pathlib import Path

from tools.thai_cluster import is_thai, tokenize_clusters

PUA_START = 0xE000


def collect_clusters(texts: Iterable[str]) -> set[str]:
    found: set[str] = set()
    for text in texts:
        for c in tokenize_clusters(text):
            if len(c) > 1 and is_thai(c[0]):
                found.add(c)
    return found


def load_map(path: Path) -> dict[str, int]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_map(path: Path, m: dict[str, int]) -> None:
    path.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")


def encode(text: str, m: dict[str, int]) -> tuple[str, set[str]]:
    out: list[str] = []
    missing: set[str] = set()
    for c in tokenize_clusters(text):
        if len(c) > 1 and is_thai(c[0]):
            cp = m.get(c)
            if cp is None:
                missing.add(c)
                out.append(c)
            else:
                out.append(chr(cp))
        else:
            out.append(c)
    return "".join(out), missing
