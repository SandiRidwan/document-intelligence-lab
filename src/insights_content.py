
# ---------------------------------------------------------------------------
# KONTEN INSIGHT — Document Intelligence Lab
# Sudut pandang: analis data yang ditugaskan mengubah laporan PDF jadi dataset
# yang dapat dipakai — dan harus jujur soal keterbatasan ekstraksi.
# ---------------------------------------------------------------------------
from insight import register

register(
    "kpi",
    kesimpulan=(
        "Dari 2 laporan PDF (UN SDG 2024 & World Population 2022) berhasil "
        "diekstrak >1.300 indikator angka. Namun hanya sebagian kecil yang "
        "berasal dari tabel terstruktur — mayoritas dari paragraf naratif "
        "yang di-parse berbasis pola."),
    rekomendasi=[
        "Gunakan dataset ini untuk EXPLORASI tema, bukan angka final yang "
        "dikutip langsung ke laporan resmi.",
        "Untuk angka kritis, verifikasi manual terhadap PDF sumber.",
        "Bila volume besar, pertimbangkan OCR + model layout (mis. LayoutLM) "
        "sebagai langkah lanjutan.",
    ],
    risiko=(
        "Memakai hasil ekstraksi otomatis tanpa verifikasi untuk keputusan "
        "penting berisiko mengutip angka yang salah. Satu angka nyasar dalam "
        "laporan bisa merusak kredibilitas seluruh analisis."),
    tingkat="tinggi",
)

register(
    "topic",
    kesimpulan=(
        "Topik dominan: land (121), ocean (81), income (76), health (66), "
        "water (58). Sebagian besar indikator (615) tidak terdeteksi topiknya — "
        "menandakan angka tersebar di teks tanpa kata kunci tema."),
    rekomendasi=[
        "Fokuskan analisis pada topik dengan kata kunci jelas (land, ocean, "
        "health) — sana hasil ekstraksi paling dapat dipercaya.",
        "Untuk 615 'tanpa topik', lakukan klasifikasi topik tambahan atau "
        "tinjau manual sebelum dipakai.",
        "Gunakan distribusi topik untuk memetakan fokus laporan dengan cepat.",
    ],
    risiko=(
        "Mengabaikan 44% indikator tanpa topik berarti kehilangan sebagian "
        "besar data, atau sebaliknya — memakainya tanpa konteks dapat "
        "menyesatkan kesimpulan tematik."),
    tingkat="sedang",
)

register(
    "region",
    kesimpulan=(
        "Indikator tersebar merata antar-kawasan (Sub-Saharan Africa, Asia "
        "Selatan, Amerika Latin, dll), mencerminkan sifat laporan SDG yang "
        "membandingkan wilayah."),
    rekomendasi=[
        "Gunakan pemilahan wilayah untuk melacak ketimpangan antar-kawasan.",
        "Wilayah dengan sedikit indikator = area yang kurang disorot; bisa jadi "
        "celah data atau celah perhatian.",
        "Silangkan wilayah × topik untuk menemukan isu spesifik per kawasan.",
    ],
    risiko=(
        "Membaca data global tanpa memilah wilayah menyembunyikan krisis lokal. "
        "Rata-rata dunia yang 'membaik' bisa menutupi kemunduran di satu kawasan."),
    tingkat="sedang",
)

register(
    "quality",
    kesimpulan=(
        "Tingkat keberhasilan ekstraksi tabel sangat RENDAH (<1%): dari 246 "
        "tabel terdeteksi, hanya 1 yang benar-benar bersih & terstruktur. Ini "
        "fakta penting: PDF laporan resmi umumnya berlayout kompleks/dua-kolom."),
    rekomendasi=[
        "Jangan berasumsi `extract_tables()` cukup untuk laporan nyata — "
        "sering gagal; butuh pendekatan campuran (tabel + teks + OCR).",
        "Untuk proyek riil, anggarkan waktu untuk verifikasi manual.",
        "Pertimbangkan alat khusus (Camelot, Tabula, atau model ML layout) bila "
        "tabel banyak.",
    ],
    risiko=(
        "Percaya pada ekstraksi tabel otomatis saja akan menghasilkan dataset "
        "hampir kosong tanpa disadari. Tim yang tidak memeriksa 'quality rate' "
        "akan menyimpulkan 'tidak ada data', padahal datanya ada di teks."),
    tingkat="kritis",
)

register(
    "validation",
    kesimpulan=(
        "Validasi menunjukkan recall 67% vs sampel gold dan konsistensi topik "
        "99.9%, dengan noise rate rendah (setiap indikator punya topik/wilayah). "
        "Artinya pola ekstraksi dapat diandalkan untuk eksplorasi."),
    rekomendasi=[
        "Percayai indikator dengan topik/wilayah jelas; perlakukan 'tanpa topik' "
        "dengan hati-hati.",
        "Perluas gold sampel secara berkala untuk mengukur akurasi tiap iterasi.",
        "Simpan validation.json sebagai bukti audit untuk setiap rilis dataset.",
    ],
    risiko=(
        "Validasi pada sampel kecil (3 gold) bisa belum mewakili keseluruhan. "
        "Mengklaim 'akurat' tanpa sampel besar berisiko overclaim — perlu "
        "kejujuran soal ukuran sampel validasi."),
    tingkat="tinggi",
)


# --------------------------------------------------------------------------
# Chart ECharts (v2) — insight & rekomendasi.
# --------------------------------------------------------------------------

register(
    "echarts_sunburst",
    kesimpulan=(
        "Sunburst merangkum sebaran indikator antar-topik dalam satu pandangan: "
        "cincin luar = topik, luas = jumlah indikator. Distribusi timpang "
        "(beberapa topik mendominasi) itu wajar pada laporan SDG — tetapi "
        "menunjukkan di mana data paling padat vs paling tipis, sehingga "
        "kekosongan topik langsung terlihat."),
    rekomendasi=[
        "Gunakan sebaran ini untuk menilai cakupan: topik dengan irisan tipis "
        "berarti ekstraksi/pelaporan kurang lengkap.",
        "Saat membandingkan antar-laporan, bandingkan bentuk sunburst — "
        "pergeseran proporsi menandakan perubahan prioritas pelaporan.",
        "Jangan anggap topik tipis sebagai 'tidak penting'; bisa jadi datanya "
        "ada tapi belum terestrak.",
    ],
    risiko=(
        "Menganggap sunburst sebagai proporsi 'pentingnya' topik adalah keliru — "
        "ia mengukur JUMLAH INDIKATOR, bukan bobot kebijakan. Kesimpulan yang "
        "salah arah bisa menyesatkan prioritas."),
    tingkat="rendah",
)

register(
    "echarts_funnel",
    kesimpulan=(
        "Funnel menelusuri penyusutan dari tabel terdeteksi → berkualitas → "
        "indikator terestrak. Celah terbesar (biasanya 'tabel terdeteksi' → "
        "'berkualitas') mengungkap di mana upaya ekstraksi paling banyak hilang. "
        "Pada laporan PDF nyata, rasio tabel bersih bisa di bawah 1%."),
    rekomendasi=[
        "Fokuskan perbaikan parser pada tahap penyusutan terbesar, bukan merata "
        "di semua tahap.",
        "Untuk tabel kompleks (dua kolom/merge), pertimbangkan ekstraksi hibrida "
        "(tabel + pola teks) alih-alih hanya pdfplumber.",
        "Tambahkan validasi manual terjadwal pada indikator bernilai tinggi.",
    ],
    risiko=(
        "Mengklaim 'data berhasil diekstrak' tanpa memperhatikan funnel berisiko "
        "melaporkan angka dari tabel berkualitas rendah. Keputusan berbasis angka "
        "yang belum diverifikasi bisa salah secara serius."),
    tingkat="tinggi",
)
