"""
ingest.py — unduh PDF sumber → data/raw. Idempoten (lewati bila sudah ada).

Menghitung hash untuk audit. TIDAK melakukan parsing (itu tugas parse.py).
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import RAW, SOURCES, STAGING

H = {"User-Agent": "document-intelligence-lab/1.0 (portfolio)"}


def _download(url: str, dest: Path) -> int:
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, timeout=180) as r:
        data = r.read()
    dest.write_bytes(data)
    return len(data)


def main() -> None:
    t0 = time.time()
    print("[ingest] mulai")
    meta = {"run_at": datetime.now(timezone.utc).isoformat(), "files": {}}

    for key, spec in SOURCES.items():
        dest = RAW / f"{key}.pdf"
        if dest.exists() and dest.stat().st_size > 10000:
            size = dest.stat().st_size
            print(f"[ingest] {key}: sudah ada ({size//1024} KB) — dilewati")
        else:
            print(f"[ingest] {key}: mengunduh...")
            try:
                size = _download(spec["url"], dest)
                print(f"  → {size//1024} KB")
            except Exception as e:  # noqa: BLE001
                print(f"  ! gagal: {str(e)[:100]}")
                continue
        b = dest.read_bytes()
        meta["files"][key] = {
            "url": spec["url"], "nama": spec["nama"],
            "bytes": len(b), "md5": hashlib.md5(b).hexdigest(),
            "is_pdf": b[:5] == b"%PDF-",
        }

    meta["duration_sec"] = round(time.time() - t0, 2)
    (STAGING / "_ingest_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[ingest] selesai ({meta['duration_sec']}s, {len(meta['files'])} file)")


if __name__ == "__main__":
    main()
