"""
dashboard.py — Streamlit: Document Intelligence Lab.

Menampilkan hasil ekstraksi PDF → data: ringkasan, topik, wilayah, kualitas
tabel, validasi akurasi. Setiap elemen disertai narasi Kenapa-Tujuan-Dampak
dan kotak Insight & Rekomendasi.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from config import COLORS as C, DB_FILE, MARTS, REPORTS  # noqa: E402
import explanations as X  # noqa: E402
import insights_content  # noqa: E402,F401
import insight as INS  # noqa: E402

st.set_page_config(page_title="Document Intelligence Lab", page_icon="📄",
                   layout="wide")


def _src() -> str:
    if DB_FILE.exists():
        return "db"
    if (MARTS / "mart_extraction_summary.parquet").exists():
        return "marts"
    return "none"


_S = _src()


def _ensure():
    if _S == "none":
        st.error("Data belum ada. Jalankan: `python src/run_pipeline.py`")
        st.stop()


_ensure()


@st.cache_data(show_spinner="Membaca hasil ekstraksi...")
def q(name: str) -> pd.DataFrame:
    if _S == "db":
        con = duckdb.connect(str(DB_FILE), read_only=True)
        df = con.execute(f"SELECT * FROM {name}").df()
        con.close()
        return df
    p = MARTS / f"{name}.parquet"
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()


def style(fig, h=420):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=54, b=10),
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#D5DBE1"),
                      title=dict(font=dict(size=16, color="#fff")),
                      legend=dict(bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(gridcolor="#2A3038", zeroline=False)
    fig.update_yaxes(gridcolor="#2A3038", zeroline=False)
    return fig


def kpi(col, label, value, sub, color):
    col.markdown(
        f"""<div style="background:#1A1F2B;border-left:4px solid {color};
        padding:14px 16px;border-radius:10px;height:118px;">
        <div style="color:#9AA7B4;font-size:.76rem;text-transform:uppercase;
        letter-spacing:.06em;">{label}</div>
        <div style="color:{color};font-size:1.55rem;font-weight:700;
        margin-top:6px;">{value}</div>
        <div style="color:#6B7885;font-size:.75rem;">{sub}</div></div>""",
        unsafe_allow_html=True)


summary = q("mart_extraction_summary")
topic = q("mart_indicators_by_topic")
region = q("mart_indicators_by_region")
try:
    val = json.loads((REPORTS / "validation.json").read_text())
except Exception:
    val = {}

total_ind = int(summary["indicators"].sum()) if len(summary) else 0
total_tbl = int(summary["tables_detected"].sum()) if len(summary) else 0
q_tbl = int(summary["tables_quality"].sum()) if len(summary) else 0

st.markdown(
    f"""<div style="background:linear-gradient(100deg,{C['primary']},{C['purple']});
    padding:22px 26px;border-radius:14px;margin-bottom:18px;">
    <div style="font-size:1.7rem;font-weight:800;color:white;">
    📄 Document Intelligence Lab</div>
    <div style="color:#D7E4DC;font-size:.9rem;margin-top:4px;">
    Ekstraksi data dari laporan PDF resmi (UN SDG 2024 + WPP 2022) →
    tabel terstruktur · pdfplumber + DuckDB · by <b>Sandi Ridwan</b></div></div>""",
    unsafe_allow_html=True)

X.render("kpi", st=st)
k1, k2, k3, k4 = st.columns(4)
kpi(k1, "Indikator terestrak", f"{total_ind:,}", "dari 2 laporan PDF",
    C["primary"])
kpi(k2, "Tabel terdeteksi", f"{total_tbl}", "di seluruh halaman", C["accent"])
kpi(k3, "Tabel berkualitas", f"{q_tbl}", "terstruktur bersih", C["red"])
kpi(k4, "Recall validasi", f"{val.get('gold_recall', 0):.0%}",
    "vs sampel gold", C["purple"])
INS.box("kpi", st=st)
st.write("")

t1, t2, t3, t4 = st.tabs(["📊 Topik", "🌍 Wilayah", "🔬 Kualitas & Validasi",
                          "📖 Metodologi"])

with t1:
    X.render("topic", st=st)
    tt = topic.head(15).copy()
    fig = px.bar(tt.iloc[::-1], x="n_indicators", y="topic", orientation="h",
                 color="n_indicators", color_continuous_scale="Greens",
                 text="n_indicators")
    style(fig, 480).update_layout(coloraxis_showscale=False,
                                  title="Indikator per Topik SDG",
                                  xaxis_title="jumlah indikator", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    INS.box("topic", st=st)

with t2:
    X.render("region", st=st)
    rr = region.sort_values("n_indicators", ascending=False).head(15)
    fig = px.bar(rr.iloc[::-1], x="n_indicators", y="region", orientation="h",
                 color="n_indicators", color_continuous_scale="Blues",
                 text="n_indicators")
    style(fig, 480).update_layout(coloraxis_showscale=False,
                                  title="Indikator per Wilayah",
                                  xaxis_title="jumlah", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(region, use_container_width=True, hide_index=True)
    INS.box("region", st=st)

with t3:
    X.render("quality", st=st)
    fig = px.bar(summary, x="source", y=["tables_detected", "tables_quality"],
                 barmode="group", title="Tabel Terdeteksi vs Berkualitas")
    style(fig, 360).update_layout(yaxis_title="jumlah", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(summary, use_container_width=True, hide_index=True)
    INS.box("quality", st=st)

    X.render("validation", st=st)
    if val:
        vk1, vk2, vk3 = st.columns(3)
        kpi(vk1, "Recall (gold)", f"{val.get('gold_recall', 0):.0%}",
            f"{len(val)} metrik uji", C["primary"])
        kpi(vk2, "Konsistensi topik",
            f"{val.get('topic_consistency', 0):.0%}", "label↔topik",
            C["accent"])
        kpi(vk3, "Noise rate", f"{val.get('noise_rate', 0):.0%}",
            "tanpa konteks", C["red"])
        st.json(val)
    else:
        st.info("Jalankan `python src/validate.py` untuk validasi.")
    INS.box("validation", st=st)

with t4:
    X.render("method", st=st)
    st.markdown("#### Arsitektur")
    st.code("""
 ingest.py ─► data/raw/*.pdf
      │
      ├─► parse.py ......... tabel → stg_table_cells
      └─► parse_extract.py . teks → stg_indicators
                    │
          load_db.py ─► DuckDB ─► transform.py ─► marts
                    │
          validate.py (recall/consistency/noise) ─► validation.json
                    │
        dashboard.py · make_charts.py · tests/
    """, language="text")
    st.markdown("#### Pendekatan")
    st.markdown(
        "- **pdfplumber** — ekstraksi tabel & kata berkoordinat.\n"
        "- **Line reconstruction** — gabung kata jadi baris via koordinat `top`.\n"
        "- **Pattern matching** — pasangkan label (topik/wilayah) + angka.\n"
        "- **Skoring kualitas** — tiap tabel dinilai (baris/kolom/rasio angka).\n"
        "- **Validasi** — recall vs gold, konsistensi topik, noise rate.\n\n"
        "⚠️ **Batas jujur:** tabel PDF kompleks sulit diekstrak (quality rate "
        "<1%); sebagian angka berasal dari teks naratif dan perlu verifikasi "
        "manual untuk keputusan penting.")

st.markdown(
    f"""<hr style="border-color:#2A3038;">
    <div style="color:#8B9AA6;font-size:.8rem;text-align:center;">
    📄 Document Intelligence Lab · sumber: UN SDG Report 2024 & WPP 2022 (publik)
    · pdfplumber + DuckDB · oleh <b>Sandi Ridwan</b><br>
    Analisis edukasional. Verifikasi manual dianjurkan untuk angka kritis.</div>""",
    unsafe_allow_html=True)
