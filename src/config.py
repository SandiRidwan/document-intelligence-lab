"""
config.py — satu sumber kebenaran: path, sumber, konstanta.

Project: Document Intelligence Lab
Fokus: mengekstrak DATA dari PDF laporan resmi → tabel terstruktur → analisis.

Sumber: UN Sustainable Development Goals Report 2024 (PDF publik, tanpa key).
Jujur soal batas: tabel PDF kompleks; akurasi divalidasi & dilaporkan.
"""

from __future__ import annotations

from pathlib import Path

# ---- Path -----------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
STAGING = DATA / "staging"
MARTS = DATA / "marts"
DB = ROOT / "db"
SQL = ROOT / "sql"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"

for _p in (RAW, STAGING, MARTS, DB, REPORTS, FIGURES):
    _p.mkdir(parents=True, exist_ok=True)

DB_FILE = DB / "documents.duckdb"

# ---- Sumber PDF (publik, tanpa API key) ------------------------------------
SOURCES = {
    "un_sdg_2024": {
        "url": ("https://unstats.un.org/sdgs/report/2024/"
                "The-Sustainable-Development-Goals-Report-2024.pdf"),
        "nama": "UN Sustainable Development Goals Report 2024",
        "tahun": 2024,
        "halaman_min": 5,      # lewati halaman sampul/daftar isi
    },
    "un_wpp_2022": {
        "url": ("https://www.un.org/development/desa/pd/sites/"
                "www.un.org.development.desa.pd/files/"
                "wpp2022_summary_of_results.pdf"),
        "nama": "UN World Population Prospects 2022 — Summary",
        "tahun": 2022,
        "halaman_min": 10,
    },
}

# ---- Ekstraksi -------------------------------------------------------------
# Tabel dianggap "berkualitas" bila memenuhi ambang minimum.
MIN_ROWS = 3           # minimal baris (selain header)
MIN_COLS = 2           # minimal kolom
MIN_NUMERIC_RATIO = 0.3  # minimal 30% sel berupa angka (tabel data, bukan teks)

# ---- Palet warna -----------------------------------------------------------
COLORS = {
    "primary": "#1F5C3D", "accent": "#E4A11B", "dark": "#1B2A33",
    "grey": "#8B9AA6", "red": "#C0392B", "blue": "#2E6F95",
    "purple": "#6A4C93", "teal": "#2A9D8F",
}
