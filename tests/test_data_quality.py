"""
test_data_quality.py — uji kualitas data & validitas ekstraksi (CI-friendly).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import duckdb

from config import DB_FILE

FAILS: list[str] = []
PASSES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        PASSES.append(name)
        print(f"  PASS  {name}")
    else:
        FAILS.append(f"{name} — {detail}")
        print(f"  FAIL  {name}  {detail}")


def main() -> int:
    con = duckdb.connect(str(DB_FILE), read_only=True)
    print("[dq] uji kualitas data & validitas ekstraksi\n")

    # data ada
    n = con.execute("SELECT count(*) FROM stg_indicators").fetchone()[0]
    check("indikator terestrak > 0", n > 0, f"{n}")

    # nilai tidak semua null
    nn = con.execute("SELECT count(*) FROM stg_indicators WHERE value IS NOT NULL").fetchone()[0]
    check("nilai terisi", nn == n, f"{nn}/{n} non-null")

    # setiap indikator punya konteks (topik ATAU wilayah) — bukan angka nyasar
    orphan = con.execute("""SELECT count(*) FROM stg_indicators
        WHERE topic IS NULL AND region IS NULL""").fetchone()[0]
    check("indikator punya konteks (topik/wilayah)", orphan == 0,
          f"{orphan} tanpa konteks")

    # tahun (1900-2100) tidak masuk sebagai data
    years = con.execute("""SELECT count(*) FROM stg_indicators
        WHERE value BETWEEN 1900 AND 2100 AND unit = 'count'""").fetchone()[0]
    check("tahun tidak salah jadi data", years == 0, f"{years} mencurigakan")

    # unit valid
    bad_unit = con.execute("""SELECT count(*) FROM stg_indicators
        WHERE unit NOT IN ('%','usd','count')""").fetchone()[0]
    check("unit terklasifikasi", bad_unit == 0, f"{bad_unit} unit aneh")

    # marts terbentuk
    for t in ["mart_extraction_summary", "mart_indicators_by_topic",
              "mart_indicators_by_region"]:
        c = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        check(f"{t} terisi", c > 0, f"{c}")

    # ringkasan mencakup semua sumber
    n_src = con.execute("SELECT count(DISTINCT source) FROM stg_indicators").fetchone()[0]
    check("cakupan sumber >= 2", n_src >= 2, f"{n_src}")

    # konsistensi topik (dari validate.py) tersimpan
    vpath = Path(__file__).resolve().parent.parent / "reports" / "validation.json"
    if vpath.exists():
        import json
        v = json.loads(vpath.read_text())
        check("konsistensi topik tinggi (>=0.9)",
              v.get("topic_consistency", 0) >= 0.9,
              f"{v.get('topic_consistency')}")
        check("noise rate rendah (<=0.1)",
              v.get("noise_rate", 1) <= 0.1, f"{v.get('noise_rate')}")

    con.close()
    print(f"\n[dq] {len(PASSES)} lulus, {len(FAILS)} gagal")
    if FAILS:
        print("\nGAGAL:")
        for f in FAILS:
            print("  -", f)
        return 1
    print("[dq] SEMUA UJI LULUS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
