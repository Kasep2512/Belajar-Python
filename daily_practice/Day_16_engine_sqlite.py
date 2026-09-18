# Day 16: Engine Perhitungan IP/IPK & Persistensi SQLite (Auto-Reload on Refresh)
import re
import sqlite3
from pathlib import Path
import pandas as pd
import pdfplumber
import streamlit as st

st.set_page_config(page_title="Analisis Nilai & Kalkulator IPK", page_icon="🎓", layout="wide")

DB_FILE = Path("akademik.db")
BOBOT_MUTU = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.0}


def inisialisasi_database():
    """Membuat tabel profil dan riwayat nilai jika belum ada."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS profil_mahasiswa (
                npm TEXT PRIMARY KEY,
                nama TEXT,
                jurusan TEXT,
                ipk_dokumen TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS riwayat_nilai (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npm TEXT,
                no INTEGER,
                kode TEXT,
                mata_kuliah TEXT,
                sks INTEGER,
                nilai TEXT,
                bobot REAL,
                semester INTEGER,
                FOREIGN KEY (npm) REFERENCES profil_mahasiswa (npm)
            )
            """
        )
        conn.commit()


def ambil_semua_mahasiswa() -> list[tuple[str, str]]:
    """Mengambil daftar seluruh mahasiswa yang tersimpan di database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT npm, nama FROM profil_mahasiswa ORDER BY rowid DESC")
        return cursor.fetchall()


def simpan_ke_database(profil: dict, df_nilai: pd.DataFrame):
    """Menyimpan profil dan 37 baris mata kuliah ke SQLite."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO profil_mahasiswa (npm, nama, jurusan, ipk_dokumen)
            VALUES (?, ?, ?, ?)
            """,
            (profil["npm"], profil["nama"], profil["jurusan"], profil["ipk_cetak"]),
        )
        cursor.execute("DELETE FROM riwayat_nilai WHERE npm = ?", (profil["npm"],))

        for _, baris in df_nilai.iterrows():
            bobot = BOBOT_MUTU.get(baris["nilai"].upper(), 0.0)
            cursor.execute(
                """
                INSERT INTO riwayat_nilai (npm, no, kode, mata_kuliah, sks, nilai, bobot, semester)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profil["npm"],
                    int(baris["no"]),
                    baris["kode"],
                    baris["mata_kuliah"],
                    int(baris["sks"]),
                    baris["nilai"],
                    bobot,
                    int(baris["semester"]),
                ),
            )
        conn.commit()


def ambil_data_mahasiswa(npm: str) -> tuple[dict | None, pd.DataFrame]:
    """Mengambil profil dan tabel nilai berdasarkan NPM dari database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT npm, nama, jurusan, ipk_dokumen FROM profil_mahasiswa WHERE npm = ?", (npm,))
        row = cursor.fetchone()
        if not row:
            return None, pd.DataFrame()

        profil = {"npm": row[0], "nama": row[1], "jurusan": row[2], "ipk_cetak": row[3]}
        df_nilai = pd.read_sql_query(
            "SELECT no, kode, mata_kuliah, sks, nilai, bobot, semester FROM riwayat_nilai WHERE npm = ? ORDER BY no ASC",
            conn,
            params=(npm,),
        )
        return profil, df_nilai


def ekstrak_data_pdf(file_pdf) -> tuple[dict, pd.DataFrame]:
    profil = {"npm": "-", "nama": "-", "jurusan": "-", "ipk_cetak": "-"}
    baris_matkul = []

    with pdfplumber.open(file_pdf) as pdf:
        semua_teks = ""
        for halaman in pdf.pages:
            teks = halaman.extract_text()
            if teks:
                semua_teks += "\n" + teks

            tabel = halaman.extract_table()
            if tabel:
                for row in tabel:
                    clean_row = [str(c).strip() if c is not None else "" for c in row]
                    if len(clean_row) >= 6 and clean_row[0].isdigit():
                        baris_matkul.append(
                            {
                                "no": int(clean_row[0]),
                                "kode": clean_row[1],
                                "mata_kuliah": clean_row[2].replace("\n", " "),
                                "sks": int(clean_row[3]),
                                "nilai": clean_row[4],
                                "semester": int(clean_row[5]),
                            }
                        )

    if not baris_matkul:
        pola = re.compile(r"^\s*(\d+)\s+([A-Z0-9]+)\s+(.+?)\s+(\d+)\s+([A-E])\s+(\d+)\s*$", re.MULTILINE)
        for c in pola.finditer(semua_teks):
            baris_matkul.append(
                {
                    "no": int(c.group(1)),
                    "kode": c.group(2),
                    "mata_kuliah": c.group(3).strip(),
                    "sks": int(c.group(4)),
                    "nilai": c.group(5),
                    "semester": int(c.group(6)),
                }
            )

    npm_m = re.search(r"NPM\s*:\s*(\d+)", semua_teks)
    nama_m = re.search(r"NAMA\s*:\s*([^\n\r]+)", semua_teks)
    prodi_m = re.search(r"PROGRAM STUDI\s*:\s*([^\n\r]+)", semua_teks)
    ipk_m = re.search(r"SKS/IPK\s*:\s*([^\n\r]+)", semua_teks)

    if npm_m:
        profil["npm"] = npm_m.group(1).strip()
    if nama_m:
        profil["nama"] = nama_m.group(1).strip()
    if prodi_m:
        profil["jurusan"] = prodi_m.group(1).strip()
    if ipk_m:
        profil["ipk_cetak"] = ipk_m.group(1).strip()

    df_nilai = pd.DataFrame(baris_matkul)
    if not df_nilai.empty:
        df_nilai["bobot"] = df_nilai["nilai"].map(lambda x: BOBOT_MUTU.get(str(x).upper(), 0.0))

    return profil, df_nilai


def hitung_statistik_akademik(df_nilai: pd.DataFrame) -> dict:
    if df_nilai.empty:
        return {"total_sks": 0, "ipk": 0.0, "ips_per_semester": pd.DataFrame()}

    df = df_nilai.copy()
    df["sks_x_bobot"] = df["sks"] * df["bobot"]

    total_sks = int(df["sks"].sum())
    total_mutu = float(df["sks_x_bobot"].sum())
    ipk = (total_mutu / total_sks) if total_sks > 0 else 0.0

    grup = (
        df.groupby("semester")
        .agg(
            total_sks=("sks", "sum"),
            total_mutu=("sks_x_bobot", "sum"),
            jumlah_matkul=("no", "count"),
        )
        .reset_index()
    )
    grup["ips"] = (grup["total_mutu"] / grup["total_sks"]).round(2)

    return {"total_sks": total_sks, "ipk": round(ipk, 2), "ips_per_semester": grup}


inisialisasi_database()
daftar_tersimpan = ambil_semua_mahasiswa()

st.title("🎓 Portal Evaluasi & Engine Nilai Mahasiswa")
st.caption("Kalkulasi otomatis IP Semester, IPK kumulatif, dan persistensi database SQLite")

file_unggah = st.file_uploader("Unggah file PDF Rangkuman Nilai:", type=["pdf"])

if file_unggah is not None:
    with st.spinner("Mengekstrak dan memproses nilai..."):
        profil, df_nilai = ekstrak_data_pdf(file_unggah)
        if not df_nilai.empty and profil["npm"] != "-":
            simpan_ke_database(profil, df_nilai)
            st.session_state["npm_aktif"] = profil["npm"]
            st.success("Data berhasil diekstrak dan disimpan ke SQLite!")
            st.rerun()

if "npm_aktif" not in st.session_state and daftar_tersimpan:
    st.session_state["npm_aktif"] = daftar_tersimpan[0][0]

if "npm_aktif" in st.session_state:
    profil_aktif, df_aktif = ambil_data_mahasiswa(st.session_state["npm_aktif"])

    if profil_aktif and not df_aktif.empty:
        hasil_hitung = hitung_statistik_akademik(df_aktif)

        st.info(
            f"📂 Menampilkan data tersimpan dari database lokal (`akademik.db`) untuk NPM **{profil_aktif['npm']}**."
        )

        st.subheader("Ringkasan Akademik")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("NPM Mahasiswa", profil_aktif["npm"])
        k2.metric("Nama", profil_aktif["nama"])
        k3.metric("Total SKS Tuntas", f"{hasil_hitung['total_sks']} SKS")
        k4.metric("IPK Dihitung (Otomatis)", f"{hasil_hitung['ipk']:.2f}", delta=f"Cetak: {profil_aktif['ipk_cetak']}")

        st.divider()

        st.subheader("📊 Rincian Indeks Prestasi per Semester (IPS)")
        df_ips = hasil_hitung["ips_per_semester"]

        cols_sem = st.columns(len(df_ips))
        for idx, row in df_ips.iterrows():
            with cols_sem[idx]:
                st.metric(
                    label=f"Semester {int(row['semester'])}",
                    value=f"IPS: {row['ips']:.2f}",
                    help=f"{row['total_sks']} SKS • {row['jumlah_matkul']} Mata Kuliah",
                )

        st.dataframe(
            df_ips[["semester", "jumlah_matkul", "total_sks", "ips"]],
            column_config={
                "semester": "Semester",
                "jumlah_matkul": "Jumlah Matkul",
                "total_sks": "Beban SKS",
                "ips": "Indeks Prestasi Semester (IPS)",
            },
            hide_index=True,
            use_container_width=True,
        )

        st.divider()

        st.subheader(f"Tabel Riwayat Nilai ({len(df_aktif)} Mata Kuliah)")
        st.dataframe(
            df_aktif[["no", "kode", "mata_kuliah", "sks", "nilai", "bobot", "semester"]],
            column_config={
                "no": "No",
                "kode": "Kode",
                "mata_kuliah": "Mata Kuliah",
                "sks": "SKS",
                "nilai": "Huruf Mutu",
                "bobot": "Bobot Angka",
                "semester": "Semester",
            },
            hide_index=True,
            use_container_width=True,
        )
