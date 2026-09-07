# Day 12: Session State & Form Input Dinamis
import streamlit as st

st.set_page_config(page_title="Modul Tracker Dinamis", page_icon="📝", layout="centered")

if "daftar_modul" not in st.session_state:
    st.session_state.daftar_modul = [
        {"hari": 1, "topik": "Instalasi Python 3.13", "kategori": "Setup", "selesai": True},
        {"hari": 2, "topik": "Setup VS Code & Ruff", "kategori": "Setup", "selesai": True},
        {"hari": 3, "topik": "Git Lokal & Identitas", "kategori": "Git", "selesai": True},
        {"hari": 4, "topik": "GitHub & .gitignore", "kategori": "Git", "selesai": True},
        {"hari": 5, "topik": "Virtual Environment", "kategori": "Setup", "selesai": True},
        {"hari": 6, "topik": "Tipe Data Primitif", "kategori": "Dasar", "selesai": True},
        {"hari": 7, "topik": "Koleksi List & Dict", "kategori": "Dasar", "selesai": True},
        {"hari": 8, "topik": "Alur Kontrol & Filtering", "kategori": "Dasar", "selesai": True},
        {"hari": 9, "topik": "Fungsi Modular State", "kategori": "Dasar", "selesai": True},
        {"hari": 10, "topik": "Pemodelan State Class", "kategori": "OOP", "selesai": True},
        {"hari": 11, "topik": "Aplikasi Web Pertama", "kategori": "Web UI", "selesai": True},
        {"hari": 12, "topik": "Session State & Input Form", "kategori": "Web UI", "selesai": False},
    ]

st.title("📝 Tracker Modul Interaktif")
st.caption("Kelola dan tambahkan materi belajar secara dinamis")

with st.expander("➕ Tambah Modul Baru"):
    with st.form("form_tambah_modul", clear_on_submit=True):
        topik_baru = st.text_input("Topik Materi:")
        kategori_baru = st.selectbox("Kategori:", ["Dasar", "Setup", "Git", "OOP", "Web UI", "Database"])
        status_baru = st.checkbox("Tandai langsung selesai?")
        tombol_simpan = st.form_submit_button("Simpan Modul")

        if tombol_simpan:
            if topik_baru.strip() != "":
                nomor_hari_berikutnya = len(st.session_state.daftar_modul) + 1
                modul_baru = {
                    "hari": nomor_hari_berikutnya,
                    "topik": topik_baru.strip(),
                    "kategori": kategori_baru,
                    "selesai": status_baru,
                }
                st.session_state.daftar_modul.append(modul_baru)
                st.success(f"Modul Hari ke-{nomor_hari_berikutnya} berhasil ditambahkan!")
                st.rerun()
            else:
                st.error("Nama topik materi nggak boleh kosong.")

col1, col2 = st.columns([1, 2])
with col1:
    filter_status = st.selectbox("Filter Status:", ["SEMUA", "SELESAI", "PENDING"])
with col2:
    kata_kunci = st.text_input("Cari Materi:", placeholder="Ketik topik atau kategori...")

query = kata_kunci.strip().lower()
data_terfilter = [
    item
    for item in st.session_state.daftar_modul
    if (
        filter_status == "SEMUA"
        or (filter_status == "SELESAI" and item["selesai"])
        or (filter_status == "PENDING" and not item["selesai"])
    )
    and (query in item["topik"].lower() or query in item["kategori"].lower())
]

st.divider()
total_modul = len(st.session_state.daftar_modul)
total_selesai = sum(1 for item in st.session_state.daftar_modul if item["selesai"])

col_metrik1, col_metrik2 = st.columns(2)
col_metrik1.metric("Progres Selesai", f"{total_selesai}/{total_modul}")
col_metrik2.metric("Hasil Tampil", f"{len(data_terfilter)} modul")

st.subheader("Daftar Materi")
if not data_terfilter:
    st.warning("Nggak ada modul yang cocok dengan filter.")
else:
    for item in data_terfilter:
        label = "✅ Selesai" if item["selesai"] else "⏳ Belum Selesai"
        st.markdown(f"**H-{item['hari']} | {item['topik']}**  \nKategori: `{item['kategori']}` — *Status:* **{label}**")
        st.write("---")
