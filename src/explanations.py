"""
explanations.py — narasi Kenapa · Tujuan · Dampak untuk setiap elemen.
"""

from __future__ import annotations

EXPLAIN: dict[str, dict] = {
    "kpi": {
        "judul": "Ringkasan Ekstraksi",
        "kenapa": "Sebelum membaca data, kita harus tahu berapa yang berhasil "
                  "diekstrak dari PDF dan seberapa dapat dipercaya.",
        "tujuan": "Menjawab: berapa indikator terestrak, dan seberapa bersih?",
        "dampak": "Menentukan seberapa jauh data ini layak dipakai untuk "
                  "keputusan, dan di mana perlu verifikasi manual.",
        "baca": "Nilai dari hasil parsing PDF; kualitas diuji terpisah.",
    },
    "topic": {
        "judul": "Indikator per Topik SDG",
        "kenapa": "PDF laporan tidak terstruktur; mengelompokkan per topik "
                  "mengubah tumpukan angka jadi gambaran tema.",
        "tujuan": "Menjawab: tema apa yang paling banyak dibahas/diukur?",
        "dampak": "Menunjukkan fokus laporan & celah data antar-tema.",
        "baca": "Batang = jumlah indikator per topik; 'tanpa topik' = angka "
                "yang tak terkait kata kunci (perlu tinjauan).",
    },
    "region": {
        "judul": "Indikator per Wilayah",
        "kenapa": "Banyak data SDG dipilah per kawasan — ekstraksi wilayah "
                  "memungkinkan perbandingan geografis.",
        "tujuan": "Menjawab: kawasan mana paling banyak disorot?",
        "dampak": "Basis prioritas geografis & pelacakan ketimpangan.",
        "baca": "Wilayah dideteksi dari label teks (nama kawasan).",
    },
    "quality": {
        "judul": "Kualitas Ekstraksi Tabel",
        "kenapa": "Tidak semua tabel PDF bisa diekstrak. Menampilkan tingkat "
                  "keberhasilan jujur mencegah kepercayaan berlebihan.",
        "tujuan": "Menjawab: berapa persen tabel yang berhasil & bersih?",
        "dampak": "Menandai halaman yang perlu OCR/parsing manual.",
        "baca": "Quality rate rendah = PDF didominasi layout kompleks/scan.",
    },
    "validation": {
        "judul": "Validasi Akurasi",
        "kenapa": "Ekstraksi tanpa validasi = angka tanpa jaminan. Kita ukur "
                  "recall, konsistensi, & tingkat derau.",
        "tujuan": "Menjawab: seberapa akurat hasil ekstraksi?",
        "dampak": "Menentukan kelayakan data & batas yang harus disampaikan.",
        "baca": "Recall tinggi = pola ketemu; derau rendah = sedikit angka nyasar.",
    },
    "method": {
        "judul": "Metodologi",
        "kenapa": "Hasil harus dapat ditelusuri & direproduksi.",
        "tujuan": "Menjelaskan pendekatan ekstraksi & sumber.",
        "dampak": "Pemangku kepentingan dapat memverifikasi & menjalankan ulang.",
        "baca": "Lihat docs/ADR.md untuk keputusan lengkap.",
    },
}


def text(key: str) -> str:
    e = EXPLAIN.get(key)
    if not e:
        return ""
    p = [f"**{e['judul']}**", f"- **Kenapa:** {e['kenapa']}",
         f"- **Tujuan:** {e['tujuan']}", f"- **Dampak:** {e['dampak']}"]
    if e.get("baca"):
        p.append(f"- **Cara baca:** {e['baca']}")
    return "\n".join(p)


def render(key: str, expanded: bool = False, st=None) -> None:
    if st is None:
        import streamlit as st  # noqa
    e = EXPLAIN.get(key)
    if not e:
        return
    with st.expander(f"💡 {e['judul']} — Kenapa · Tujuan · Dampak",
                     expanded=expanded):
        st.markdown(
            f"**🔎 Kenapa** — {e['kenapa']}\n\n"
            f"**🎯 Tujuan** — {e['tujuan']}\n\n"
            f"**📈 Dampak** — {e['dampak']}")
        if e.get("baca"):
            st.caption(f"👁️ Cara baca: {e['baca']}")


def audit(verbose: bool = True) -> bool:
    ok = True
    for k, v in EXPLAIN.items():
        miss = [f for f in ("kenapa", "tujuan", "dampak") if not v.get(f)]
        if miss:
            ok = False
            if verbose:
                print(f"  MISSING {k}: {miss}")
    if verbose:
        print(f"Penjelasan: {len(EXPLAIN)} | "
              f"{'SEMUA LENGKAP' if ok else 'ADA YANG KURANG'}")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if audit() else 1)
