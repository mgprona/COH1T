from pathlib import Path

for name in ["install.ps1", "uninstall.ps1"]:
    p = Path("release") / name
    t = p.read_text(encoding="utf-8")
    p.write_bytes(b"\xef\xbb\xbf" + t.encode("utf-8"))
    print(name, "-> utf-8 bom")
