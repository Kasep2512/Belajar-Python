# Day 13: Penyimpanan Data Permanen Menggunakan File JSON
import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Modul Tracker Persistent", page_icon="💾", layout="centered")

FILE_DATA = Path("modul_data.json")

DATA_AWAL = [
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
    {"hari": 12, "topik": "Session State & Form", "kategori": "Web UI", "selesai": True},
    {"hari": 13, "topik": "File I/O & JSON Storage", "kategori": "File I/O", "selesai": False},
]


def muat_data() -> list[dict]:
    if not FILE_DATA.exists():
        simpan_data(DATA_AWAL)
        return DATA_AWAL
    with open(FILE_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def simpan_data(data: list[dict]) -> None:
    with open(FILE_DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if "daftar_modul" not in st.session_state:
    st.session_state.daftar_modul = muat_data()

st.title("💾 Tracker Modul Berbasis JSON")
st.caption("Data otomatis tersimpan ke file lokal dan tidak akan hilang saat server mati")

with st.expander("➕ Tambah Modul Baru"):
    with st.form("form_modul", clear_on_submit=True):
        topik = st.text_input("Topik Materi:")
        kategori = st.selectbox("Kategori:", ["Dasar", "Setup", "Git", "OOP", "Web UI", "File I/O", "Database"])
        selesai = st.checkbox("Langsung selesai?")
        simpan = st.form_submit_button("Simpan Permanen")

        if simpan:
            if topik.strip():
                nomor_baru = max([m["hari"] for m in st.session_state.daftar_modul], default=0) + 1
                item_baru = {"hari": nomor_baru, "topik": topik.strip(), "kategori": kategori, "selesai": selesai}
                st.session_state.daftar_modul.append(item_baru)
                simpan_data(st.session_state.daftar_modul)
                st.success(f"Modul H-{nomor_baru} tersimpan ke JSON!")
                st.rerun()
            else:
                st.error("Topik tidak boleh kosong.")

col_filter, col_cari = st.columns([1, 2])
with col_filter:
    filter_status = st.selectbox("Status:", ["SEMUA", "SELESAI", "PENDING"])
with col_cari:
    kata_kunci = st.text_input("Cari:", placeholder="Ketik topik atau kategori...")

query = kata_kunci.strip().lower()
hasil = [
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
total = len(st.session_state.daftar_modul)
tuntas = sum(1 for m in st.session_state.daftar_modul if m["selesai"])
m1, m2 = st.columns(2)
m1.metric("Progres Selesai", f"{tuntas}/{total}")
m2.metric("Hasil Tampil", f"{len(hasil)} modul")

st.subheader("Daftar Materi")
if not hasil:
    st.warning("Data tidak ditemukan.")
else:
    for item in hasil:
        c_cek, c_teks, c_hapus = st.columns([0.6, 4, 0.6])

        with c_cek:
            centang = st.checkbox("", value=item["selesai"], key=f"c_{item['hari']}", label_visibility="collapsed")
            if centang != item["selesai"]:
                item["selesai"] = centang
                simpan_data(st.session_state.daftar_modul)
                st.rerun()

        with c_teks:
            label = "✅ Selesai" if item["selesai"] else "⏳ Pending"
            st.markdown(f"**H-{item['hari']} | {item['topik']}**  \nKategori: `{item['kategori']}` — *{label}*")

        with c_hapus:
            if st.button("🗑️", key=f"d_{item['hari']}"):
                st.session_state.daftar_modul = [m for m in st.session_state.daftar_modul if m["hari"] != item["hari"]]
                simpan_data(st.session_state.daftar_modul)
                st.rerun()

        st.write("---")
