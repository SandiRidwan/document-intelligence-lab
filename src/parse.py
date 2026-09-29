"""
parse.py — PARSER: ekstrak tabel dari PDF → data/staging.

Inti project: bukan sekadar extract_tables(), tapi menilai KUALITAS tiap tabel
dan MENANDAI yang gagal/meragukan — jujur soal batas ekstraksi PDF.

Untuk setiap tabel yang terdeteksi, hitung:
  · n_rows, n_cols
  · numeric_ratio  (proporsi sel berupa angka)
  · is_quality     (lolos ambang MIN_ROWS/COLS/NUMERIC_RATIO)
  · has_header     (baris pertama bukan angka semua)

Output:
  data/staging/tables_raw.parquet     — semua tabel (satu baris per sel)
  data/staging/parse_report.json      — ringkasan kualitas per halaman
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import pdfplumber

from config import (MIN_COLS, MIN_NUMERIC_RATIO, MIN_ROWS, RAW, SOURCES,
                    STAGING)

NUM_RE = re.compile(r"^[\s]*[-+]?[\d.,]+%?[\s]*$")


def _is_numeric(cell) -> bool:
    if cell is None:
        return False
    s = str(cell).strip().replace(" ", "")
    if not s:
        return False
    return bool(NUM_RE.match(s))


def _to_float(cell):
    if cell is None:
        return None
    s = str(cell).strip().replace(" ", "").replace("%", "")
    # buang pemisah ribuan gaya berbeda (1,234.5 / 1.234,5 / 1 234)
    if "," in s and "." in s:
        s = s.replace(",", "") if s.rfind(".") > s.rfind(",") else \
            s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _analyze_table(rows: list[list]) -> dict:
    """Nilai kualitas tabel mentah."""
    clean = [r for r in rows if any(c is not None and str(c).strip()
                                    for c in r)]
    if not clean:
        return {"is_quality": False, "n_rows": 0, "n_cols": 0,
                "numeric_ratio": 0.0, "has_header": False}
    n_cols = max(len(r) for r in clean)
    cells = [c for r in clean for c in r]
    n_num = sum(1 for c in cells if _is_numeric(c))
    ratio = n_num / len(cells) if cells else 0.0
    # header: baris pertama sebagian besar non-angka
    first = clean[0]
    first_num = sum(1 for c in first if _is_numeric(c))
    has_header = first_num <= max(1, len(first) // 3)
    n_body = len(clean) - (1 if has_header else 0)
    is_q = (n_body >= MIN_ROWS and n_cols >= MIN_COLS
            and ratio >= MIN_NUMERIC_RATIO)
    return {"is_quality": is_q, "n_rows": len(clean), "n_cols": n_cols,
            "numeric_ratio": round(ratio, 3), "has_header": has_header}


def parse_pdf(key: str) -> tuple[list[dict], list[dict]]:
    """Ekstrak semua tabel dari satu PDF. Kembalikan (rows, page_report)."""
    path = RAW / f"{key}.pdf"
    if not path.exists():
        print(f"  ! {key}: PDF tidak ada, dilewati")
        return [], []
    spec = SOURCES[key]
    page_min = spec.get("halaman_min", 0)
    rows_out, report = [], []
    with pdfplumber.open(path) as pdf:
        n = len(pdf.pages)
        for pi in range(page_min, n):
            page = pdf.pages[pi]
            try:
                tables = page.extract_tables()
            except Exception:  # noqa: BLE001
                tables = []
            n_q = 0
            for ti, tbl in enumerate(tables):
                info = _analyze_table(tbl)
                report.append({"source": key, "page": pi, "table_idx": ti,
                               **info})
                if not info["is_quality"]:
                    continue
                n_q += 1
                header = None
                start = 0
                if info["has_header"]:
                    header = [str(c) if c is not None else f"col_{j}"
                              for j, c in enumerate(tbl[0])]
                    start = 1
                for ri in range(start, len(tbl)):
                    for ci, cell in enumerate(tbl[ri]):
                        col = header[ci] if header and ci < len(header) \
                            else f"col_{ci}"
                        rows_out.append({
                            "source": key, "page": pi, "table_idx": ti,
                            "row_idx": ri, "col_idx": ci, "col_name": col,
                            "cell_raw": (None if cell is None
                                         else str(cell).strip()),
                            "cell_num": _to_float(cell),
                            "is_numeric": _is_numeric(cell),
                        })
            report.append({"source": key, "page": pi, "table_idx": -1,
                           "page_total_tables": len(tables),
                           "page_quality_tables": n_q})
    return rows_out, report


def main() -> None:
    t0 = time.time()
    print("[parse] mulai ekstraksi tabel PDF")
    all_rows, all_report = [], []
    for key in SOURCES:
        print(f"[parse] {key}...")
        rows, rep = parse_pdf(key)
        all_rows += rows
        all_report += rep
        n_pages_with_table = len({r["page"] for r in rep
                                  if r.get("page_total_tables", 0) > 0})
        n_q = len({(r["page"], r["table_idx"]) for r in rep
                   if r.get("is_quality")})
        print(f"  → {n_pages_with_table} halaman bertabel, "
              f"{n_q} tabel berkualitas")

    df = pd.DataFrame(all_rows)
    df.to_parquet(STAGING / "tables_raw.parquet", index=False)
    rep_df = pd.DataFrame(all_report)
    rep_df.to_parquet(STAGING / "parse_report.parquet", index=False)
    (STAGING / "parse_report.json").write_text(
        json.dumps({"rows": len(df),
                    "quality_tables": int(rep_df.get("is_quality", pd.Series(
                        dtype=bool)).sum()) if len(rep_df) else 0,
                    "duration_sec": round(time.time() - t0, 1)},
                   indent=2), encoding="utf-8")
    print(f"[parse] selesai: {len(df)} sel (dari tabel berkualitas), "
          f"{time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
