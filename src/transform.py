"""
transform.py — jalankan SQL marts & ekspor.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb

from config import DB_FILE, MARTS, SQL

MARTS_TABLES = [
    "mart_extraction_summary",
    "mart_indicators_by_topic",
    "mart_indicators_by_region",
]


def main() -> None:
    con = duckdb.connect(str(DB_FILE))
    print("[transform] menjalankan sql/transform.sql")
    con.execute((SQL / "transform.sql").read_text(encoding="utf-8"))
    for t in MARTS_TABLES:
        n = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        print(f"   {t:30} {n:5} baris")
        con.execute(f"""COPY {t}
            TO '{(MARTS / (t + '.parquet')).as_posix()}' (FORMAT PARQUET)""")

    print("\n[transform] ringkasan ekstraksi:")
    for r in con.execute("""SELECT source, tables_detected, tables_quality,
        indicators, quality_rate FROM mart_extraction_summary""").fetchall():
        print(f"   {r[0]:14} tabel={r[1]} berkualitas={r[2]} "
              f"indikator={r[3]} rate={r[4]}")

    print("\n[transform] topik teratas:")
    for r in con.execute("""SELECT topic, n_indicators, n_pct
        FROM mart_indicators_by_topic LIMIT 8""").fetchall():
        print(f"   {r[0]:16} {r[1]:4} indikator ({r[2]} %)")
    con.close()


if __name__ == "__main__":
    main()
