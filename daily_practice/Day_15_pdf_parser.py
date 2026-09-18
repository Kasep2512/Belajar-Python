# Day 15: Upload & Ekstraksi Data Rangkuman Nilai PDF
import re
import pandas as pd
import pdfplumber
import streamlit as st

st.set_page_config(page_title="Analisis Nilai Mahasiswa", page_icon="🎓", layout="wide")


def ekstrak_data_pdf(file_pdf) -> tuple[dict, pd.DataFrame]:
    """Mengekstrak profil mahasiswa dan daftar baris nilai dari dokumen PDF."""
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
        pola_baris = re.compile(r"^\s*(\d+)\s+([A-Z0-9]+)\s+(.+?)\s+(\d+)\s+([A-E])\s+(\d+)\s*$", re.MULTILINE)
        for cocok in pola_baris.finditer(semua_teks):
            baris_matkul.append(
                {
                    "no": int(cocok.group(1)),
                    "kode": cocok.group(2),
                    "mata_kuliah": cocok.group(3).strip(),
                    "sks": int(cocok.group(4)),
                    "nilai": cocok.group(5),
                    "semester": int(cocok.group(6)),
                }
            )

    npm_match = re.search(r"NPM\s*:\s*(\d+)", semua_teks)
    nama_match = re.search(r"NAMA\s*:\s*([^\n\r]+)", semua_teks)
    prodi_match = re.search(r"PROGRAM STUDI\s*:\s*([^\n\r]+)", semua_teks)
    ipk_match = re.search(r"SKS/IPK\s*:\s*([^\n\r]+)", semua_teks)

    if npm_match:
        profil["npm"] = npm_match.group(1).strip()
    if nama_match:
        profil["nama"] = nama_match.group(1).strip()
    if prodi_match:
        profil["jurusan"] = prodi_match.group(1).strip()
    if ipk_match:
        profil["ipk_cetak"] = ipk_match.group(1).strip()

    df_nilai = pd.DataFrame(baris_matkul)
    return profil, df_nilai


st.title("🎓 Portal Evaluasi & Analisis Nilai Mahasiswa")
st.caption("Unggah dokumen PDF Rangkuman Nilai untuk mengevaluasi riwayat akademik")

file_unggah = st.file_uploader("Pilih file PDF Rangkuman Nilai:", type=["pdf"])

if file_unggah is not None:
    with st.spinner("Mengekstrak data dari dokumen..."):
        profil_mhs, df_hasil = ekstrak_data_pdf(file_unggah)

    if not df_hasil.empty:
        st.subheader("Data Akademik Mahasiswa")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("NPM", profil_mhs["npm"])
        k2.metric("Nama", profil_mhs["nama"])
        k3.metric("Program Studi", profil_mhs["jurusan"])
        k4.metric("SKS / IPK Tertera", profil_mhs["ipk_cetak"])

        st.divider()

        st.subheader(f"Tabel Riwayat Nilai ({len(df_hasil)} Mata Kuliah Terdeteksi)")
        st.dataframe(
            df_hasil,
            column_config={
                "no": "No",
                "kode": "Kode Matkul",
                "mata_kuliah": "Nama Mata Kuliah",
                "sks": "SKS",
                "nilai": "Huruf Mutu",
                "semester": "Semester",
            },
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.error("Struktur tabel nilai tidak terdeteksi di dokumen. Pastikan file sesuai format rangkuman nilai.")
