"""
parse_extract.py — ekstraksi angka-indikator dari laporan PDF naratif.

Melengkapi parse.py (yang fokus tabel). Di sini kita ekstrak pasangan
LABEL WILAYAH/INDIKATOR + ANGKA dari tata letak laporan, karena laporan
resmi sering menyajikan data di dalam paragraf dua-kolom, bukan tabel.

Pendekatan (deterministik, dapat diaudit):
  · Ambil kata per halaman via pdfplumber (dengan koordinat).
  · Deteksi BARIS (word top sama) lalu gabung kata jadi teks baris.
  · Cari pola: <label teks> ... <angka>%? pada baris yang sama.
  · Simpan (source, page, label, value, unit).

Output: data/staging/indicators.parquet
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

from config import RAW, SOURCES, STAGING

# Label wilayah/kawasan yang sering muncul di laporan SDG (Bahasa Inggris).
REGION_HINTS = [
    "Sub-Saharan Africa", "Northern Africa", "Western Asia",
    "Central and Southern Asia", "Latin America", "Caribbean",
    "Europe", "Northern America", "Eastern and South-Eastern Asia",
    "Australia", "New Zealand", "Oceania", "Least developed",
    "Landlocked", "Small Island", "World",
]
# Indikator/kata kunci konteks SDG.
TOPIC_HINTS = [
    "poverty", "hunger", "food", "health", "education", "gender",
    "water", "energy", "work", "industry", "inequality", "cities",
    "consumption", "climate", "ocean", "land", "peace", "partnership",
    "agriculture", "income", "mortality", "internet", "sanitation",
]

# Angka (dengan opsional %), memisahkan ribuan/desimal.
NUM = r"[-+]?\d[\d.,]*\s*(?:billion|million|trillion|per cent|%)?"


def _lines_from_words(words: list[dict], y_tol: float = 3.0) -> list[dict]:
    """Gabung kata menjadi baris berdasarkan koordinat 'top'."""
    lines = []
    for w in sorted(words, key=lambda x: (round(x["top"]), x["x0"])):
        placed = False
        for ln in lines:
            if abs(ln["top"] - w["top"]) <= y_tol:
                ln["words"].append(w)
                placed = True
                break
        if not placed:
            lines.append({"top": w["top"], "words": [w]})
    out = []
    for ln in lines:
        ws = sorted(ln["words"], key=lambda x: x["x0"])
        out.append({"top": ln["top"], "text": " ".join(w["text"] for w in ws)})
    return out


def extract_indicators(key: str) -> list[dict]:
    path = RAW / f"{key}.pdf"
    if not path.exists():
        return []
    spec = SOURCES[key]
    page_min = spec.get("halaman_min", 0)
    rows = []
    with pdfplumber.open(path) as pdf:
        for pi in range(page_min, len(pdf.pages)):
            words = pdf.pages[pi].extract_words()
            for ln in _lines_from_words(words):
                text = ln["text"]
                low = text.lower()
                region = next((r for r in REGION_HINTS if r.lower() in low),
                              None)
                topic = next((t for t in TOPIC_HINTS if t in low), None)
                nums = re.findall(NUM, text)
                if not nums:
                    continue
                # ambil angka bermakna (bukan tahun 4-digit & bukan nomor kecil)
                for raw in nums:
                    val = _parse_val(raw)
                    if val is None:
                        continue
                    if 1900 <= val <= 2100:          # tahun, bukan data
                        continue
                    if region or topic:
                        rows.append({
                            "source": key, "page": pi,
                            "region": region, "topic": topic,
                            "label": text[:160],
                            "value_raw": raw.strip(),
                            "value": val,
                            "unit": ("%" if "%" in raw or "per cent" in raw
                                     else "usd" if ("billion" in raw
                                                    or "million" in raw
                                                    or "trillion" in raw)
                                     else "count"),
                        })
    return rows


def _parse_val(raw: str):
    s = raw.strip().lower()
    mult = 1.0
    if "trillion" in s:
        mult = 1e12
    elif "billion" in s:
        mult = 1e9
    elif "million" in s:
        mult = 1e6
    s2 = re.sub(r"(billion|million|trillion|per cent|%)", "", s).strip()
    s2 = s2.replace(" ", "")
    if "," in s2 and "." in s2:
        s2 = s2.replace(",", "") if s2.rfind(".") > s2.rfind(",") \
            else s2.replace(".", "").replace(",", ".")
    elif "," in s2:
        s2 = s2.replace(",", ".")
    try:
        return float(s2) * mult
    except ValueError:
        return None


def main() -> None:
    t0 = time.time()
    print("[extract] ekstraksi indikator dari teks laporan")
    all_rows = []
    for key in SOURCES:
        print(f"[extract] {key}...")
        rows = extract_indicators(key)
        all_rows += rows
        print(f"  → {len(rows)} pasangan label-angka")
    df = pd.DataFrame(all_rows)
    df.to_parquet(STAGING / "indicators.parquet", index=False)
    meta = {"rows": len(df),
            "by_source": df["source"].value_counts().to_dict() if len(df) else {},
            "by_topic": df["topic"].value_counts().head(10).to_dict() if len(df)
            else {},
            "duration_sec": round(time.time() - t0, 1)}
    (STAGING / "_extract_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[extract] selesai: {len(df)} baris, {time.time()-t0:.1f}s")
    if len(df):
        print("[extract] topik teratas:")
        for t, n in df["topic"].value_counts().head(8).items():
            print(f"   {t}: {n}")


if __name__ == "__main__":
    main()
