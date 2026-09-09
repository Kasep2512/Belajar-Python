# Day 14: Visualisasi Data & Analitik Progres Belajar
import json
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard Progres & Analitik", page_icon="📊", layout="wide")

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
    {"hari": 13, "topik": "File I/O & JSON Storage", "kategori": "File I/O", "selesai": True},
    {"hari": 14, "topik": "Visualisasi Data & Grafik", "kategori": "Web UI", "selesai": False},
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


# Inisialisasi session state dari JSON
if "daftar_modul" not in st.session_state:
    st.session_state.daftar_modul = muat_data()

st.title("📊 Dashboard Analitik & Progres Belajar")
st.caption("Visualisasi status materi berbasis data riil dari modul_data.json")

# ==========================================
# 1. BAGIAN METRIK & PROGRESS BAR
# ==========================================
total_modul = len(st.session_state.daftar_modul)
total_selesai = sum(1 for item in st.session_state.daftar_modul if item["selesai"])
total_pending = total_modul - total_selesai
rasio_selesai = (total_selesai / total_modul) if total_modul > 0 else 0.0

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Total Modul", f"{total_modul} Topik")
col_m2.metric("Tuntas Diambil", f"{total_selesai} Topik")
col_m3.metric("Belum Selesai", f"{total_pending} Topik")

st.markdown("**Persentase Kelulusan Modul:**")
st.progress(rasio_selesai, text=f"{rasio_selesai * 100:.1f}% materi berhasil dituntaskan")

st.divider()

# ==========================================
# 2. BAGIAN VISUALISASI GRAFIK (CHARTS)
# ==========================================
st.subheader("📈 Distribusi Materi per Kategori")

df = pd.DataFrame(st.session_state.daftar_modul)

if not df.empty:
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("**Total Materi per Kategori**")
        hitung_kategori = df["kategori"].value_counts()
        st.bar_chart(hitung_kategori, color="#29b5e8")

    with col_chart2:
        st.markdown("**Status Materi (Selesai vs Pending) per Kategori**")
        rekap_status = df.groupby(["kategori", "selesai"]).size().unstack(fill_value=0)

        # Ubah nama kolom boolean agar mudah dibaca di grafik
        kolom_ganti = {}
        if True in rekap_status.columns:
            kolom_ganti[True] = "Selesai"
        if False in rekap_status.columns:
            kolom_ganti[False] = "Pending"
        rekap_status.rename(columns=kolom_ganti, inplace=True)

        st.bar_chart(rekap_status)

st.divider()

# ==========================================
# 3. KONTROL INTERAKTIF & DAFTAR MODUL
# ==========================================
col_kiri, col_kanan = st.columns([1, 1])

# Form Tambah Data Baru
with col_kiri:
    with st.expander("➕ Tambah Modul Baru"):
        with st.form("form_tambah", clear_on_submit=True):
            topik = st.text_input("Nama Topik:")
            kategori = st.selectbox(
                "Kategori:",
                [
                    "Dasar",
                    "Setup",
                    "Git",
                    "OOP",
                    "Web UI",
                    "File I/O",
                    "Database",
                ],
            )
            selesai = st.checkbox("Langsung Selesai?")
            tombol = st.form_submit_button("Simpan Modul")

            if tombol:
                if topik.strip():
                    nomor_baru = (
                        max(
                            [m["hari"] for m in st.session_state.daftar_modul],
                            default=0,
                        )
                        + 1
                    )
                    modul_baru = {
                        "hari": nomor_baru,
                        "topik": topik.strip(),
                        "kategori": kategori,
                        "selesai": selesai,
                    }
                    st.session_state.daftar_modul.append(modul_baru)
                    simpan_data(st.session_state.daftar_modul)
                    st.rerun()
                else:
                    st.error("Topik tidak boleh kosong.")

# Filter Pencarian
with col_kanan:
    with st.expander("🔍 Filter & Cari Data"):
        filter_status = st.selectbox("Status:", ["SEMUA", "SELESAI", "PENDING"])
        kata_kunci = st.text_input("Cari:", placeholder="Ketik topik atau kategori...")

# Terapkan Filter
query = kata_kunci.strip().lower()
hasil_filter = [
    item
    for item in st.session_state.daftar_modul
    if (
        filter_status == "SEMUA"
        or (filter_status == "SELESAI" and item["selesai"])
        or (filter_status == "PENDING" and not item["selesai"])
    )
    and (query in item["topik"].lower() or query in item["kategori"].lower())
]

# Tampilkan Daftar Modul
st.subheader("Daftar Modul")
if not hasil_filter:
    st.warning("Tidak ada modul yang cocok dengan kriteria pencarian.")
else:
    for item in hasil_filter:
        c_centang, c_info, c_hapus = st.columns([0.5, 4.5, 0.5])

        with c_centang:
            cek = st.checkbox(
                "",
                value=item["selesai"],
                key=f"chk_{item['hari']}",
                label_visibility="collapsed",
            )
            if cek != item["selesai"]:
                item["selesai"] = cek
                simpan_data(st.session_state.daftar_modul)
                st.rerun()

        with c_info:
            status_text = "✅ Selesai" if item["selesai"] else "⏳ Pending"
            st.markdown(f"**H-{item['hari']} | {item['topik']}** (`{item['kategori']}`) — {status_text}")

        with c_hapus:
            if st.button("🗑️", key=f"btn_{item['hari']}"):
                st.session_state.daftar_modul = [m for m in st.session_state.daftar_modul if m["hari"] != item["hari"]]
                simpan_data(st.session_state.daftar_modul)
                st.rerun()
