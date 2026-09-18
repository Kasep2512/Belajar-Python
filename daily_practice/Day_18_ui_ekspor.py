# Day 18: Restrukturisasi UI/UX, Fitur Ekspor Data & Simulasi CRUD
import io
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Portal Akademik Mahasiswa",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_FILE = Path("akademik.db")
BOBOT_MUTU = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.0}


def ambil_profil() -> dict | None:
    if not DB_FILE.exists():
        return None
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT npm, nama, jurusan, ipk_dokumen FROM profil_mahasiswa LIMIT 1")
        row = cursor.fetchone()
        if not row:
            return None
        return {"npm": row[0], "nama": row[1], "jurusan": row[2], "ipk_cetak": row[3]}


def ambil_data_nilai(npm: str) -> pd.DataFrame:
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
    """Operasi UPDATE nilai ke SQLite."""
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


def tentukan_predikat(ipk: float) -> tuple[str, str]:
    if ipk >= 3.51:
        return "Dengan Pujian (Cum Laude) 🏆", "normal"
    elif ipk >= 3.00:
        return "Sangat Memuaskan ⭐", "normal"
    elif ipk >= 2.75:
        return "Memuaskan 👍", "off"
    else:
        return "Cukup ⚠️", "inverse"


def konversi_ke_excel(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Riwayat_Nilai")
    return output.getvalue()


profil = ambil_profil()

if not profil:
    st.error("⚠️ Database `akademik.db` belum ditemukan atau masih kosong.")
    st.info("Silakan jalankan script `Day_16_engine_sqlite.py` terlebih dahulu untuk memproses berkas PDF.")
    st.stop()

df_semua = ambil_data_nilai(profil["npm"])

# Perhitungan Metrik Global
total_sks = int(df_semua["sks"].sum())
total_mutu = float((df_semua["sks"] * df_semua["bobot"]).sum())
ipk_hitung = round(total_mutu / total_sks, 2) if total_sks > 0 else 0.0
predikat_teks, predikat_warna = tentukan_predikat(ipk_hitung)

# Rekap per Semester
df_sem = (
    df_semua.groupby("semester")
    .agg(
        total_sks=("sks", "sum"),
        total_mutu=("sks", lambda x: (x * df_semua.loc[x.index, "bobot"]).sum()),
        jumlah_matkul=("no", "count"),
    )
    .reset_index()
)
df_sem["ips"] = (df_sem["total_mutu"] / df_sem["total_sks"]).round(2)

with st.sidebar:
    st.header("👤 Profil Mahasiswa")
    st.markdown(f"**Nama:**\n{profil['nama']}")
    st.markdown(f"**NPM:** `{profil['npm']}`")
    st.markdown(f"**Jurusan:** {profil['jurusan']}")
    st.divider()

    st.subheader("📌 Status Predikat")
    st.success(predikat_teks)

    st.divider()
    st.caption("Dev Habit Portfolio • Hari ke-18")


st.title("🎓 Dashboard Evaluasi Akademik Mahasiswa")
st.caption("Sistem Pemantauan Capaian Indeks Prestasi, Sebaran Nilai, dan Ekspor Laporan")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("IPK Kumulatif", f"{ipk_hitung:.2f}", delta=f"Cetak: {profil['ipk_cetak']}")
col_m2.metric("Total SKS Tuntas", f"{total_sks} SKS")
col_m3.metric("Total Mata Kuliah", f"{len(df_semua)} Matkul")
col_m4.metric("Semester Aktif/Terekam", f"{df_sem['semester'].max()} Semester")

st.divider()

tab_dashboard, tab_tabel, tab_ekspor = st.tabs(
    [
        "📊 Analitik & Grafik",
        "📋 Eksplorasi & Simulasi Edit Nilai",
        "📥 Pusat Unduhan (Ekspor)",
    ]
)

with tab_dashboard:
    st.subheader("Tren Fluktuasi Indeks Prestasi Semester (IPS)")

    col_chart1, col_chart2 = st.columns([3, 2])

    with col_chart1:
        df_chart_ips = df_sem[["semester", "ips"]].copy()
        df_chart_ips["Label"] = "Semester " + df_chart_ips["semester"].astype(str)
        df_chart_ips = df_chart_ips.set_index("Label")[["ips"]]
        st.line_chart(df_chart_ips, use_container_width=True)

    with col_chart2:
        st.write("**Ringkasan Angka Tiap Semester**")
        st.dataframe(
            df_sem[["semester", "total_sks", "ips"]],
            column_config={
                "semester": "Semester",
                "total_sks": "Beban SKS",
                "ips": "Indeks Prestasi (IPS)",
            },
            hide_index=True,
            use_container_width=True,
        )

    st.subheader("Sebaran Mutu Nilai Mata Kuliah")
    sebaran_nilai = df_semua["nilai"].value_counts().sort_index()
    st.bar_chart(sebaran_nilai, color="#29b5e8")

with tab_tabel:
    st.subheader("Daftar Riwayat Mata Kuliah")

    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        opsi_semester = ["Semua Semester"] + sorted(df_semua["semester"].unique().tolist())
        pilih_sem = st.selectbox("Pilih Semester:", opsi_semester)
    with col_f2:
        kata_kunci = st.text_input("🔍 Cari Mata Kuliah / Kode Matkul:", placeholder="Ketik nama atau kode...")

    # Filter Data Tampilan
    df_tampil = df_semua.copy()
    if pilih_sem != "Semua Semester":
        df_tampil = df_tampil[df_tampil["semester"] == pilih_sem]
    if kata_kunci:
        pola_cari = kata_kunci.strip().lower()
        df_tampil = df_tampil[
            df_tampil["mata_kuliah"].str.lower().str.contains(pola_cari)
            | df_tampil["kode"].str.lower().str.contains(pola_cari)
        ]

    st.caption(f"Menampilkan **{len(df_tampil)}** dari total **{len(df_semua)}** mata kuliah.")

    st.dataframe(
        df_tampil[["semester", "no", "kode", "mata_kuliah", "sks", "nilai", "bobot"]],
        column_config={
            "semester": "Sem",
            "no": "No",
            "kode": "Kode",
            "mata_kuliah": "Nama Mata Kuliah",
            "sks": "SKS",
            "nilai": "Nilai",
            "bobot": "Bobot",
        },
        hide_index=True,
        use_container_width=True,
    )

    st.write("")
    # FITUR CRUD EDIT NILAI (KEMBALI DIINTEGRASIKAN)
    with st.expander("🛠️ Form Simulasi Perbaikan Nilai (Edit Nilai / Semester Pendek)", expanded=False):
        opsi_matkul = {
            f"Sem {row['semester']} | {row['kode']} - {row['mata_kuliah']} (Nilai Sekarang: {row['nilai']})": row["id"]
            for _, row in df_semua.iterrows()
        }

        pilihan_label = st.selectbox("Pilih Mata Kuliah yang Ingin Diperbaiki:", list(opsi_matkul.keys()))
        id_terpilih = opsi_matkul[pilihan_label]
        baris_pilihan = df_semua[df_semua["id"] == id_terpilih].iloc[0]

        col_e1, col_e2, col_e3 = st.columns([2, 1, 1])
        with col_e1:
            st.write(f"Mata Kuliah: **{baris_pilihan['mata_kuliah']}** ({baris_pilihan['sks']} SKS)")
        with col_e2:
            nilai_baru = st.selectbox("Nilai Baru:", ["A", "B", "C", "D", "E"], index=0)
        with col_e3:
            st.write("")
            st.write("")
            if st.button("Simpan Perubahan", type="primary"):
                update_nilai_matkul(id_terpilih, nilai_baru)
                st.success(f"Nilai {baris_pilihan['mata_kuliah']} berhasil diubah ke {nilai_baru}!")
                st.rerun()

with tab_ekspor:
    st.subheader("Ekspor Data Riwayat Akademik")
    st.write("Unduh data rekapitulasi nilai untuk keperluan arsip digital atau lampiran beasiswa/magang.")

    df_ekspor = df_semua[["semester", "no", "kode", "mata_kuliah", "sks", "nilai", "bobot"]].copy()

    csv_bytes = df_ekspor.to_csv(index=False).encode("utf-8")

    try:
        excel_bytes = konversi_ke_excel(df_ekspor)
        bisa_excel = True
    except Exception:
        bisa_excel = False

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        st.info("📄 **Format CSV (Comma Separated Values)**\nCocok untuk olah data via pandas, R, atau database.")
        st.download_button(
            label="⬇️ Unduh Data Nilai (.csv)",
            data=csv_bytes,
            file_name=f"Rekap_Nilai_{profil['npm']}.csv",
            mime="text/csv",
            type="primary",
        )

    with col_btn2:
        st.info("📊 **Format Excel (.xlsx)**\nCocok untuk spreadsheet Microsoft Excel lengkap dengan sheet nama.")
        if bisa_excel:
            st.download_button(
                label="⬇️ Unduh Data Nilai (.xlsx)",
                data=excel_bytes,
                file_name=f"Rekap_Nilai_{profil['npm']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )
        else:
            st.warning(
                "Pustaka `openpyxl` belum terpasang. Jalankan `pip install openpyxl` di terminal untuk mengaktifkan ekspor Excel."
            )
