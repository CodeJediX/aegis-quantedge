"""Verify every listed submission file after ZIP extraction."""

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    text = (ROOT / "SUBMISSION_MANIFEST.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| (.+?) \| (\d+) \| ([a-f0-9]{64}) \|$", text, re.M)
    if not rows:
        raise ValueError("Empty checksum manifest")
    for name, size, digest in rows:
        p = (ROOT / name).resolve()
        if ROOT.resolve() not in p.parents:
            raise ValueError("Manifest path escapes project")
        if (
            not p.is_file()
            or p.stat().st_size != int(size)
            or hashlib.sha256(p.read_bytes()).hexdigest() != digest
        ):
            raise ValueError("File mismatch: " + name)
    print("Manifest verified:", len(rows), "files")


if __name__ == "__main__":
    main()
