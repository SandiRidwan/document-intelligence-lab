"""
load_db.py — muat staging (Parquet) ke DuckDB. Idempoten.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb

from config import DB_FILE, SQL, STAGING


def main() -> None:
    con = duckdb.connect(str(DB_FILE))
    print(f"[load] database → {DB_FILE}")
    con.execute((SQL / "schema.sql").read_text(encoding="utf-8"))

    cells = STAGING / "tables_raw.parquet"
    report = STAGING / "parse_report.parquet"
    ind = STAGING / "indicators.parquet"

    n_cells = n_rep = n_ind = 0
    if cells.exists():
        con.execute("DELETE FROM stg_table_cells")
        con.execute(f"""INSERT INTO stg_table_cells
            SELECT source, page, table_idx, row_idx, col_idx, col_name,
                   cell_raw, cell_num, is_numeric
            FROM read_parquet('{cells.as_posix()}')""")
        n_cells = con.execute("SELECT count(*) FROM stg_table_cells").fetchone()[0]
    if report.exists():
        con.execute("DELETE FROM stg_parse_report")
        con.execute(f"""INSERT INTO stg_parse_report
            SELECT source, page, table_idx, is_quality, n_rows, n_cols,
                   numeric_ratio, has_header, page_total_tables,
                   page_quality_tables
            FROM read_parquet('{report.as_posix()}')""")
        n_rep = con.execute("SELECT count(*) FROM stg_parse_report").fetchone()[0]
    if ind.exists():
        con.execute("DELETE FROM stg_indicators")
        con.execute(f"""INSERT INTO stg_indicators
            SELECT source, page, region, topic, label, value_raw, value, unit
            FROM read_parquet('{ind.as_posix()}')""")
        n_ind = con.execute("SELECT count(*) FROM stg_indicators").fetchone()[0]

    print(f"[load] stg_table_cells  : {n_cells} sel")
    print(f"[load] stg_parse_report : {n_rep} baris")
    print(f"[load] stg_indicators   : {n_ind} baris")

    rows = con.execute("""SELECT source, count(*) FROM stg_indicators
        GROUP BY source ORDER BY source""").fetchall()
    if rows:
        print("[load] indikator per sumber:")
        for r in rows:
            print(f"   {r[0]:14} {r[1]} baris")
    con.close()


if __name__ == "__main__":
    main()
