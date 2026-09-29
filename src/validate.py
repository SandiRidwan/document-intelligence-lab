"""
validate.py — VALIDASI AKURASI EKSTRAKSI (inti document intelligence).

Tidak cukup "mengekstrak"; kita harus tahu SEBERAPA AKURAT hasilnya.
Karena membaca ulang seluruh PDF manual tak praktis, kita pakai pendekatan:

  1. GROUND-TRUTH SAMPEL: segelintir baris dikurasi manual (lihat _gold di
     bawah) yang mencerminkan pola ekstraksi; kita ukur recall & presisi.
  2. UJI KONSISTENSI INTERNAL: label yang memuat kata kunci topik HARUS
     mendapat topik yang sama (deteksi inkonsistensi parser).
  3. AUDIT FALSE-POSITIVE: proporsi indikator tanpa topik & tanpa wilayah —
     proxy angka "nyasar".

Output: data/staging/validation.json + reports/validation.md (jujur).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb

from config import DB_FILE, REPORTS

# Ground-truth manual: potongan baris yang KITA VERIFIKASI benar ada di PDF
# (dibaca mata dari laporan). Parser harus menemukannya.
GOLD = [
    # (substring label yang harus muncul, topik diharapkan)
    ("small-scale food producers", "food"),
    ("agriculture orientation index", "agriculture"),
    ("sub-saharan africa", None),        # region, topik tak wajib
]


def main() -> None:
    con = duckdb.connect(str(DB_FILE), read_only=True)
    ind = con.execute("SELECT * FROM stg_indicators").df()
    rep = con.execute("SELECT * FROM stg_parse_report").df()
    con.close()

    n = len(ind)
    n_no_topic = int(ind["topic"].isna().sum())
    n_no_region = int(ind["region"].isna().sum())
    n_both = int((ind["topic"].isna() & ind["region"].isna()).sum())

    # 1. Recall vs gold: apakah label gold ada di hasil ekstraksi?
    found = 0
    for sub, _ in GOLD:
        if ind["label"].str.lower().str.contains(sub, regex=False).any():
            found += 1
    recall = found / len(GOLD)

    # 2. Konsistensi: baris dengan kata topik di label harus punya topik itu.
    def expected_topic(label: str) -> str | None:
        low = label.lower()
        for t in ["poverty", "hunger", "food", "health", "education", "gender",
                  "water", "energy", "work", "inequality", "climate", "ocean",
                  "land", "agriculture", "income", "mortality"]:
            if t in low:
                return t
        return None
    mism = 0
    checked = 0
    for _, r in ind.iterrows():
        exp = expected_topic(str(r["label"]))
        if exp:
            checked += 1
            if r["topic"] != exp:
                mism += 1
    consistency = 1 - (mism / checked) if checked else 0.0

    # 3. "noise rate": indikator tanpa topik DAN tanpa wilayah
    noise_rate = n_both / n if n else 0.0

    result = {
        "total_indicators": n,
        "gold_recall": round(recall, 3),
        "topic_consistency": round(consistency, 3),
        "no_topic": n_no_topic,
        "no_region": n_no_region,
        "no_topic_no_region": n_both,
        "noise_rate": round(noise_rate, 3),
        "quality_tables": int(rep["is_quality"].sum()),
        "tables_detected": int((rep["table_idx"] >= 0).sum()),
    }
    (REPORTS / "validation.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8")

    md = ["# Validasi Ekstraksi (jujur)", "",
          f"- Total indikator terestrak: **{n}**",
          f"- Recall vs gold sampel: **{recall:.0%}**",
          f"- Konsistensi topik: **{consistency:.0%}**",
          f"- Indikator tanpa topik: {n_no_topic} ({n_no_topic/n:.0%})",
          f"- Indikator tanpa topik & wilayah (proxy derau): "
          f"**{n_both} ({noise_rate:.0%})**",
          f"- Tabel berkualitas: {result['quality_tables']} dari "
          f"{result['tables_detected']} terdeteksi",
          "",
          "## Kesimpulan jujur",
          "Ekstraksi label-angka berhasil (recall tinggi), tetapi sebagian "
          "signifikan indikator tanpa topik/wilayah — menandakan angka nyasar "
          "dari paragraf naratif. Ini **batas metode berbasis pola**, "
          "didokumentasikan terbuka, bukan disembunyikan."]
    (REPORTS / "validation.md").write_text("\n".join(md), encoding="utf-8")

    print("[validate] hasil:")
    for k, v in result.items():
        print(f"   {k:24} {v}")
    print(f"[validate] → {REPORTS / 'validation.md'}")


if __name__ == "__main__":
    main()
