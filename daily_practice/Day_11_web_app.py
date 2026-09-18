# Day 11: Aplikasi Web (Streamlit UI)
import streamlit as st

st.set_page_config(page_title="Roadmap Belajar Python", page_icon="💻", layout="centered")


class ModulState:
    def __init__(self) -> None:
        self.daftar_modul: list[dict] = [
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
            {"hari": 11, "topik": "Aplikasi Web Pertama", "kategori": "Web UI", "selesai": False},
        ]

    def ambil_data(self, filter_status: str, kata_kunci: str) -> list[dict]:
        query = kata_kunci.strip().lower()
        return [
            item
            for item in self.daftar_modul
            if (
                filter_status == "SEMUA"
                or (filter_status == "SELESAI" and item["selesai"])
                or (filter_status == "PENDING" and not item["selesai"])
            )
            and (query in item["topik"].lower() or query in item["kategori"].lower())
        ]


state = ModulState()

st.title("💻 Dashboard Belajar Python")
st.caption("Aplikasi web reaktif menggunakan Python & Streamlit")

col1, col2 = st.columns([1, 2])
with col1:
    pilihan_filter = st.selectbox("Filter Status:", ["SEMUA", "SELESAI", "PENDING"])
with col2:
    cari_topik = st.text_input("Cari Materi / Kategori:", placeholder="ketik kata kunci...")

hasil_data = state.ambil_data(pilihan_filter, cari_topik)

st.divider()
total_selesai = sum(1 for m in state.daftar_modul if m["selesai"])
kolom_stat1, kolom_stat2 = st.columns(2)
kolom_stat1.metric("Modul Tuntas", f"{total_selesai}/{len(state.daftar_modul)}")
kolom_stat2.metric("Data Tampil", f"{len(hasil_data)} item")

st.subheader("Daftar Modul")
if not hasil_data:
    st.warning("Tidak ada materi yang sesuai dengan filter.")
else:
    for item in hasil_data:
        status_badge = "✅ Selesai" if item["selesai"] else "⏳ Pending"
        st.markdown(
            f"**H-{item['hari']} | {item['topik']}**  \nKategori: '{item['kategori']}' - *Status:* **{status_badge}**"
        )
        st.write("---")
