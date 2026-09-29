"""
make_charts.py — chart PNG statis untuk README.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import COLORS as C, DB_FILE, FIGURES, REPORTS

plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight",
                     "axes.grid": True, "grid.alpha": 0.25,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "font.size": 10})


def q(sql):
    con = duckdb.connect(str(DB_FILE), read_only=True)
    df = con.execute(sql).df()
    con.close()
    return df


def chart_topics():
    t = q("""SELECT topic, n_indicators FROM mart_indicators_by_topic
             WHERE topic <> '(tak ada topik)' ORDER BY n_indicators DESC
             LIMIT 12""")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(t["topic"][::-1], t["n_indicators"][::-1], color=C["primary"])
    for i, v in enumerate(t["n_indicators"][::-1]):
        ax.text(v + 0.5, i, int(v), va="center", fontsize=8)
    ax.set_title("Indikator per Topik SDG", fontweight="bold")
    ax.set_xlabel("jumlah indikator")
    fig.savefig(FIGURES / "01_topics.png")
    plt.close(fig)
    print("  ✓ 01_topics.png")


def chart_quality():
    t = q("SELECT source, tables_detected, tables_quality FROM mart_extraction_summary")
    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(t))
    w = 0.38
    ax.bar([i - w/2 for i in x], t["tables_detected"], w, label="terdeteksi",
           color=C["grey"])
    ax.bar([i + w/2 for i in x], t["tables_quality"], w, label="berkualitas",
           color=C["red"])
    ax.set_xticks(list(x))
    ax.set_xticklabels(t["source"], fontsize=8)
    ax.set_title("Tabel Terdeteksi vs Berkualitas (rate sangat rendah)",
                 fontweight="bold")
    ax.legend()
    fig.savefig(FIGURES / "02_quality.png")
    plt.close(fig)
    print("  ✓ 02_quality.png")


def chart_region():
    t = q("""SELECT region, sum(n_indicators) n FROM mart_indicators_by_region
             WHERE region <> '(global/none)' GROUP BY region
             ORDER BY n DESC LIMIT 12""")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(t["region"][::-1], t["n"][::-1], color=C["blue"])
    for i, v in enumerate(t["n"][::-1]):
        ax.text(v + 0.3, i, int(v), va="center", fontsize=8)
    ax.set_title("Indikator per Wilayah", fontweight="bold")
    ax.set_xlabel("jumlah indikator")
    fig.savefig(FIGURES / "03_regions.png")
    plt.close(fig)
    print("  ✓ 03_regions.png")


def chart_validation():
    vp = REPORTS / "validation.json"
    if not vp.exists():
        print("  (validasi belum ada)")
        return
    v = json.loads(vp.read_text())
    labels = ["Recall", "Konsistensi\nTopik", "1 − Noise"]
    vals = [v.get("gold_recall", 0), v.get("topic_consistency", 0),
            1 - v.get("noise_rate", 0)]
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, vals, color=[C["primary"], C["accent"], C["teal"]])
    for b, val in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, val + 0.02, f"{val:.0%}",
                ha="center", fontsize=10)
    ax.set_ylim(0, 1.15)
    ax.set_title("Metrik Validasi Ekstraksi", fontweight="bold")
    fig.savefig(FIGURES / "04_validation.png")
    plt.close(fig)
    print("  ✓ 04_validation.png")


def main() -> None:
    if not DB_FILE.exists():
        raise SystemExit("DB belum ada — jalankan pipeline dulu")
    print("[charts] menghasilkan PNG untuk README:")
    chart_topics()
    chart_quality()
    chart_region()
    chart_validation()
    print(f"[charts] selesai → {FIGURES}")


if __name__ == "__main__":
    main()
