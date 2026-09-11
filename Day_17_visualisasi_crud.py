# Day 17: Visualisasi Grafik & Operasi CRUD SQLite
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Grafik & Simulasi Nilai", page_icon="📈", layout="wide")

DB_FILE = Path("akademik.db")
BOBOT_MUTU = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.0}


def ambil_profil_pertama() -> dict | None:
    """Mengambil profil mahasiswa yang tersimpan di database."""
    if not DB_FILE.exists():
        return None
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT npm, nama, jurusan, ipk_dokumen FROM profil_mahasiswa LIMIT 1")
        row = cursor.fetchone()
        if not row:
            return None
        return {"npm": row[0], "nama": row[1], "jurusan": row[2], "ipk_cetak": row[3]}


def ambil_semua_nilai(npm: str) -> pd.DataFrame:
    """Membaca daftar riwayat nilai dari tabel riwayat_nilai."""
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query(
            """
            SELECT id, no, kode, mata_kuliah, sks, nilai, bobot, semester
            FROM riwayat_nilai
            WHERE npm = ?
            ORDER BY semester ASC, no ASC
            """,
            conn,
            params=(npm,),
        )
        return df


def update_nilai_matkul(id_matkul: int, nilai_baru: str) -> None:
    """Operasi UPDATE: memperbarui huruf mutu dan bobot nilai di database."""
    bobot_baru = BOBOT_MUTU.get(nilai_baru.upper(), 0.0)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE riwayat_nilai
            SET nilai = ?, bobot = ?
            WHERE id = ?
            """,
            (nilai_baru.upper(), bobot_baru, id_matkul),
        )
        conn.commit()


def hapus_matkul(id_matkul: int) -> None:
    """Operasi DELETE: menghapus baris mata kuliah tertentu."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM riwayat_nilai WHERE id = ?", (id_matkul,))
        conn.commit()


def hitung_ringkasan(df_nilai: pd.DataFrame) -> dict:
    if df_nilai.empty:
        return {"total_sks": 0, "ipk": 0.0, "rekap_sem": pd.DataFrame()}

    df = df_nilai.copy()
    df["sks_x_bobot"] = df["sks"] * df["bobot"]

    total_sks = int(df["sks"].sum())
    total_mutu = float(df["sks_x_bobot"].sum())
    ipk = (total_mutu / total_sks) if total_sks > 0 else 0.0

    # Rekapitulasi per Semester
    rekap_sem = (
        df.groupby("semester")
        .agg(
            total_sks=("sks", "sum"),
            total_mutu=("sks_x_bobot", "sum"),
            jumlah_matkul=("id", "count"),
        )
        .reset_index()
    )

    rekap_sem["ips"] = (rekap_sem["total_mutu"] / rekap_sem["total_sks"]).round(2)
    return {"total_sks": total_sks, "ipk": round(ipk, 2), "rekap_sem": rekap_sem}


st.title("📈 Analitik Nilai & Simulasi Perbaikan (CRUD)")
st.caption("Eksplorasi tren fluktuasi indeks prestasi dan simulasi perbaikan nilai secara langsung.")

profil = ambil_profil_pertama()

if not profil:
    st.warning(
        "Database `akademik.db` belum berisi data. Jalankan `Day_16_engine_sqlite.py` terlebih dahulu dan unggah file PDF."
    )
    st.stop()

# Membaca data terbaru dari database
df_nilai = ambil_semua_nilai(profil["npm"])
statistik = hitung_ringkasan(df_nilai)
df_sem = statistik["rekap_sem"]

# Tampilan Ringkasan Profil & Metrik Utama
st.subheader("Profil Akademik")
k1, k2, k3, k4 = st.columns(4)
k1.metric("NPM", profil["npm"])
k2.metric("Nama", profil["nama"])
k3.metric("Total SKS", f"{statistik['total_sks']} SKS")
k4.metric("IPK Kumulatif", f"{statistik['ipk']:.2f}")

st.divider()

st.subheader("📊 Analisis Visual Tren & Sebaran Nilai")
col_grafik1, col_grafik2 = st.columns(2)

with col_grafik1:
    st.markdown("**Tren Fluktuasi IPS (Semester 1 – 4)**")
    if not df_sem.empty:
        # Menyiapkan data grafik garis dengan index nama semester
        df_chart_ips = df_sem[["semester", "ips"]].copy()
        df_chart_ips["Label"] = "Sem " + df_chart_ips["semester"].astype(str)
        df_chart_ips = df_chart_ips.set_index("Label")[["ips"]]
        st.line_chart(df_chart_ips)
    else:
        st.info("Belum ada data semester.")

with col_grafik2:
    st.markdown("**Distribusi Perolehan Huruf Mutu**")
    if not df_nilai.empty:
        sebaran_nilai = df_nilai["nilai"].value_counts()
        st.bar_chart(sebaran_nilai, color="#ff4b4b")
    else:
        st.info("Belum ada data nilai.")

st.divider()


st.subheader("🛠️ Simulasi Perbaikan Nilai (Operasi CRUD)")

with st.expander("📝 Form Edit Nilai Mata Kuliah (Simulasi SP / Ujian Perbaikan)"):
    # Buat label
    opsi_matkul = {
        f"Sem {row['semester']} | {row['kode']} - {row['mata_kuliah']} (Nilai Sekarang: {row['nilai']})": row["id"]
        for _, row in df_nilai.iterrows()
    }

    pilihan_label = st.selectbox("Pilih Mata Kuliah yang Ingin Diperbaiki:", list(opsi_matkul.keys()))
    id_terpilih = opsi_matkul[pilihan_label]

    baris_pilihan = df_nilai[df_nilai["id"] == id_terpilih].iloc[0]

    col_edit1, col_edit2, col_tombol = st.columns([2, 1, 1])
    with col_edit1:
        st.write(f"Mata Kuliah: **{baris_pilihan['mata_kuliah']}** ({baris_pilihan['sks']} SKS)")
    with col_edit2:
        nilai_baru = st.selectbox("Ubah Nilai Menjadi:", ["A", "B", "C", "D", "E"], index=0)
    with col_tombol:
        st.write("")
        st.write("")
        if st.button("Simpan Perubahan", type="primary"):
            update_nilai_matkul(id_terpilih, nilai_baru)
            st.success(f"Nilai {baris_pilihan['mata_kuliah']} berhasil diubah ke {nilai_baru}!")
            st.rerun()

st.divider()

# Menampilkan Tabel Lengkap
st.subheader(f"📋 Riwayat Nilai Keseluruhan ({len(df_nilai)} Mata Kuliah)")
st.dataframe(
    df_nilai[["no", "kode", "mata_kuliah", "sks", "nilai", "bobot", "semester"]],
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
