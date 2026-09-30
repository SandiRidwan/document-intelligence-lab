
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
        {
            "aksi": "Perlakukan dataset sebagai bahan eksplorasi tema, bukan angka final",
            "langkah": [
                "Tandai 1.392 indikator terestrak (UN SDG 2024 8.4 MB + World "
                "Population 2022 10.9 MB) sebagai status 'eksplorasi' di katalog data.",
                "Tempel atribut sumber (nama file, halaman, metode: pdfplumber "
                "tabel vs parsing teks naratif) pada setiap baris indikator.",
                "Larang kutipan angka langsung ke laporan resmi dari dataset ini "
                "sebelum melewati tahap verifikasi (lihat aksi verifikasi manual).",
            ],
            "metrik": "100% baris indikator punya atribut sumber + status 'eksplorasi'",
            "pemilik": "Analis data (pemilik dataset)",
        },
        {
            "aksi": "Verifikasi manual untuk indikator bernilai tinggi sebelum dikutip",
            "langkah": [
                "Susun daftar kandidat angka kritis (mis. target SDG %), urutkan "
                "berdasarkan dampak keputusan.",
                "Cocokkan tiap angka kritis ke halaman asli PDF sumber dan tandai "
                "cocok / tidak cocok.",
                "Naikkan status indikator ke 'terverifikasi' hanya bila lolos "
                "pencocokan; sisanya tetap 'eksplorasi'.",
            ],
            "metrik": "Minimal 30 indikator kritis terverifikasi; target akurasi 100% pada sampel itu",
            "pemilik": "Analis data + reviewer domain SDG",
        },
        {
            "aksi": "Naikkan cakupan ekstraksi dengan OCR + model layout untuk volume besar",
            "langkah": [
                "Ukur baseline: recall 67% & 1.392 indikator dari 2 laporan saat ini.",
                "Jalankan OCR (Tesseract) + model layout (mis. LayoutLM) pada "
                "1 laporan pilot yang tabelnya kompleks.",
                "Bandingkan jumlah indikator dan recall hasil pilot vs baseline "
                "sebelum memutuskan rollout.",
            ],
            "metrik": "Kenaikan recall dari 67% baseline, tanpa menaikkan noise rate di atas 0%",
            "pemilik": "Data engineer / ML engineer",
        },
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
        {
            "aksi": "Prioritaskan analisis pada topik berkata kunci jelas (land, ocean, health)",
            "langkah": [
                "Urutkan topik per jumlah indikator: land (121), ocean (81), "
                "income (76), health (66), water (58).",
                "Bangun analisis mendalam lebih dulu pada land & ocean yang "
                "datanya paling padat.",
                "Batasi klaim tematik pada topik ini karena hasil ekstraksinya "
                "paling dapat dipercaya.",
            ],
            "metrik": "Cakupan analisis mendalam pada topik 50+ indikator (land, ocean, income, health, water)",
            "pemilik": "Analis data (pemilik dataset)",
        },
        {
            "aksi": "Tangani 615 indikator 'tanpa topik' sebelum dipakai",
            "langkah": [
                "Isolasi 615 indikator yang tidak punya kata kunci tema (~44% dari total).",
                "Jalankan klasifikasi topik tambahan (kata kunci diperluas / model "
                "teks) lalu hitung berapa yang berhasil diberi topik.",
                "Tinjau manual sisa yang masih 'tanpa topik' sebelum masuk ke analisis tematik.",
            ],
            "metrik": "Turunkan 'tanpa topik' dari 615 indikator; capai label topik untuk ≥80% sisanya",
            "pemilik": "Data scientist (NLP) + analis data",
        },
        {
            "aksi": "Pakai distribusi topik sebagai peta fokus laporan",
            "langkah": [
                "Render distribusi topik (konsistensi topik 99.9%) sebagai rujukan cepat.",
                "Bandingkan proporsi antar-file (UN SDG vs World Population) untuk "
                "melihat pergeseran fokus.",
                "Jadikan topik tipis sebagai daftar periksa: 'data memang sedikit' "
                "atau 'belum terestrak'.",
            ],
            "metrik": "Peta distribusi topik tersedia & diperbarui setiap rilis dataset",
            "pemilik": "Analis data",
        },
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
        {
            "aksi": "Lacak ketimpangan antar-kawasan lewat pemilahan wilayah",
            "langkah": [
                "Kelompokkan 1.392 indikator berdasarkan wilayah yang terdeteksi.",
                "Hitung sebaran indikator per kawasan (Sub-Saharan Africa, Asia "
                "Selatan, Amerika Latin, dll).",
                "Tandai kawasan dengan indikator paling sedikit sebagai area "
                "kurang disorot untuk ditelusuri.",
            ],
            "metrik": "Setiap kawasan punya jumlah indikator & rasio antar-kawasan terdokumentasi",
            "pemilik": "Analis data + reviewer domain SDG",
        },
        {
            "aksi": "Selidiki wilayah berindikator tipis (celah data vs celah perhatian)",
            "langkah": [
                "Identifikasi kawasan dengan jumlah indikator di bawah rata-rata.",
                "Cek langsung ke PDF sumber apakah datanya memang tidak ada atau "
                "gagal terestrak (recall 67%).",
                "Catat kesimpulan per kawasan: 'celah data' atau 'celah perhatian'.",
            ],
            "metrik": "100% wilayah tipis punya status 'celah data' atau 'celah perhatian'",
            "pemilik": "Analis data",
        },
        {
            "aksi": "Silangkan wilayah × topik untuk menemukan isu spesifik",
            "langkah": [
                "Buat matriks wilayah × topik (land, ocean, income, health, water).",
                "Sorot sel dengan indikator padat sebagai isu prioritas per kawasan.",
                "Terjemahkan sel padat menjadi hipotesis krisis lokal untuk diverifikasi.",
            ],
            "metrik": "Matriks wilayah × topik lengkap & tiap sel padat punya hipotesis isu",
            "pemilik": "Analis data + tim kebijakan",
        },
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
        {
            "aksi": "Ganti asumsi 'extract_tables() cukup' dengan pendekatan campuran",
            "langkah": [
                "Catat fakta: dari 246 tabel terdeteksi, hanya 1 yang bersih (<1%).",
                "Terapkan pipeline campuran: tabel (pdfplumber) + parsing teks "
                "naratif + OCR untuk halaman gambar.",
                "Uji pada kedua laporan (8.4 MB & 10.9 MB) dan bandingkan hasil "
                "dengan baseline tabel-only.",
            ],
            "metrik": "Jumlah tabel bersih naik dari 1 dari 246; recall tidak turun di bawah 67%",
            "pemilik": "Data engineer",
        },
        {
            "aksi": "Anggarkan waktu verifikasi manual untuk proyek riil",
            "langkah": [
                "Estimasi rasio tabel bersih (<1%) untuk menghitung beban verifikasi.",
                "Alokasikan slot verifikasi manual per batch dokumen (per 2 laporan).",
                "Catat jam aktual verifikasi vs estimasi tiap iterasi.",
            ],
            "metrik": "Estimasi jam verifikasi vs aktual tercatat, selisih <20%",
            "pemilik": "Project lead + analis data",
        },
        {
            "aksi": "Adopsi alat khusus tabel (Camelot, Tabula, atau model ML layout)",
            "langkah": [
                "Pilih 1 laporan pilot dengan tabel dua-kolom/merge.",
                "Jalankan Camelot, Tabula, dan model layout pada tabel yang sama.",
                "Pilih alat terbaik berdasarkan jumlah tabel bersih & waktu proses, "
                "lalu integrasikan ke pipeline (DuckDB).",
            ],
            "metrik": "Peningkatan tabel bersih terukur pada pilot; pilihan alat "
                      "terdokumentasi dengan bukti",
            "pemilik": "ML engineer / data engineer",
        },
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
        {
            "aksi": "Percayai indikator bertopik/wilayah jelas, hati-hati pada 'tanpa topik'",
            "langkah": [
                "Pisahkan 1.392 indikator menjadi 'bertopik jelas' dan 'tanpa topik'.",
                "Pakai langsung indikator bertopik/wilayah (konsistensi topik "
                "99.9%, noise rate 0%) untuk eksplorasi.",
                "Beri flag peringatan pada 'tanpa topik' agar tidak dipakai sebagai "
                "dasar keputusan.",
            ],
            "metrik": "100% indikator diberi flag kualitas; 'tanpa topik' tidak masuk keputusan",
            "pemilik": "Analis data",
        },
        {
            "aksi": "Perluas gold sampel secara berkala untuk mengukur akurasi",
            "langkah": [
                "Perbesar sampel gold dari 3 dokumen/sampel ke lebih banyak secara bertahap.",
                "Ukur ulang recall (baseline 67%) & konsistensi topik (99.9%) tiap iterasi.",
                "Catat tren metrik validasi antar-rilis untuk melihat perbaikan.",
            ],
            "metrik": "Ukuran gold sampel naik; recall & konsistensi topik tercatat per iterasi",
            "pemilik": "QA / reviewer validasi",
        },
        {
            "aksi": "Simpan validation.json sebagai bukti audit tiap rilis dataset",
            "langkah": [
                "Jalankan 16 uji otomatis sebelum setiap rilis dataset.",
                "Ekspor hasil validasi (recall, konsistensi topik, noise rate) ke validation.json.",
                "Arsipkan validation.json bersama versi dataset agar dapat diaudit.",
            ],
            "metrik": "100% rilis dataset punya validation.json dengan 16 uji lulus",
            "pemilik": "Data engineer (CI/release)",
        },
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
        {
            "aksi": "Nilai cakupan dari sebaran sunburst (irisan tipis = kurang lengkap)",
            "langkah": [
                "Baca luas irisan per topik (land 121, ocean 81, income 76, health 66, water 58).",
                "Tandai topik beririsan tipis sebagai kandidat ekstraksi/pelaporan kurang lengkap.",
                "Kirim daftar topik tipis untuk ditelusuri apakah datanya gagal terestrak.",
            ],
            "metrik": "Daftar topik tipis teridentifikasi & jumlahnya turun tiap iterasi",
            "pemilik": "Analis data",
        },
        {
            "aksi": "Bandingkan bentuk sunburst antar-laporan untuk melihat pergeseran prioritas",
            "langkah": [
                "Render sunburst UN SDG 2024 dan World Population 2022 berdampingan.",
                "Bandingkan proporsi tiap topik antar kedua laporan.",
                "Catat pergeseran proporsi sebagai indikator perubahan prioritas pelaporan.",
            ],
            "metrik": "Perbandingan proporsi topik antar-2 laporan terdokumentasi",
            "pemilik": "Analis data + tim kebijakan",
        },
        {
            "aksi": "Jangan samakan topik tipis dengan 'tidak penting'",
            "langkah": [
                "Beri anotasi pada topik tipis: 'data kurang' vs 'memang sedikit'.",
                "Cek langsung ke PDF sumber untuk topik tipis prioritas.",
                "Perbarui tampilan sunburst bila hasil cek mengubah jumlah indikator.",
            ],
            "metrik": "Tiap topik tipis punya anotasi status sebelum dipakai interpretasi",
            "pemilik": "Analis data + reviewer domain SDG",
        },
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
        {
            "aksi": "Fokuskan perbaikan parser pada tahap penyusutan terbesar",
            "langkah": [
                "Baca funnel: tabel terdeteksi (246) → berkualitas (1) → indikator terestrak (1.392).",
                "Identifikasi celah terbesar, yaitu 'tabel terdeteksi' → 'berkualitas' (<1%).",
                "Alokasikan upaya perbaikan parser ke tahap terbesar itu, bukan merata.",
            ],
            "metrik": "Rasio tabel berkualitas naik dari <1% (1 dari 246) pada laporan uji",
            "pemilik": "Data engineer",
        },
        {
            "aksi": "Pakai ekstraksi hibrida untuk tabel kompleks (dua kolom/merge)",
            "langkah": [
                "Kumpulkan contoh tabel dua-kolom/merge yang gagal terdeteksi bersih.",
                "Terapkan ekstraksi hibrida (tabel + pola teks + DuckDB untuk olah) alih-alih pdfplumber saja.",
                "Ukur tambahan indikator/tabel bersih dari pendekatan hibrida.",
            ],
            "metrik": "Peningkatan tabel bersih pada sampel tabel kompleks; noise rate tetap 0%",
            "pemilik": "Data engineer / ML engineer",
        },
        {
            "aksi": "Tambahkan validasi manual terjadwal pada indikator bernilai tinggi",
            "langkah": [
                "Pilih indikator bernilai tinggi (angka keputusan) dari 1.392 terestrak.",
                "Jadwalkan verifikasi manual berkala (per rilis) dengan checklist.",
                "Jalankan 16 uji otomatis + verifikasi manual sebelum indikator dipakai.",
            ],
            "metrik": "100% indikator bernilai tinggi terverifikasi manual tiap rilis",
            "pemilik": "QA / reviewer validasi",
        },
    ],
    risiko=(
        "Mengklaim 'data berhasil diekstrak' tanpa memperhatikan funnel berisiko "
        "melaporkan angka dari tabel berkualitas rendah. Keputusan berbasis angka "
        "yang belum diverifikasi bisa salah secara serius."),
    tingkat="tinggi",
)
