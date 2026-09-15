# Day_19_app.py - Academic Evaluation Dashboard (Production Ready)
import io
import re
import sqlite3
from pathlib import Path
import pandas as pd
import pdfplumber
import streamlit as st
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

st.set_page_config(
    page_title="Academic Evaluation Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_FILE = Path("akademik.db")
BOBOT_MUTU = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.0}


def inisialisasi_database():
    """Membuat tabel jika belum ada di akademik.db."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profil_mahasiswa (
                npm TEXT PRIMARY KEY,
                nama TEXT,
                jurusan TEXT,
                ipk_dokumen TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS riwayat_nilai (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npm TEXT,
                semester INTEGER,
                no INTEGER,
                kode TEXT,
                mata_kuliah TEXT,
                sks INTEGER,
                nilai TEXT,
                bobot REAL,
                FOREIGN KEY (npm) REFERENCES profil_mahasiswa (npm)
            )
        """)
        conn.commit()


def simpan_hasil_ekstraksi(profil: dict, daftar_nilai: list[dict]):
    """Menyimpan data hasil parsing PDF ke dalam database SQLite."""
    inisialisasi_database()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO profil_mahasiswa (npm, nama, jurusan, ipk_dokumen)
            VALUES (?, ?, ?, ?)
            """,
            (profil.get("npm"), profil.get("nama"), profil.get("jurusan"), profil.get("ipk_dokumen")),
        )

        cursor.execute("DELETE FROM riwayat_nilai WHERE npm = ?", (profil.get("npm"),))

        query_insert_nilai = """
            INSERT INTO riwayat_nilai (npm, semester, no, kode, mata_kuliah, sks, nilai, bobot)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        data_rows = [
            (
                profil.get("npm"),
                n["semester"],
                n["no"],
                n["kode"],
                n["mata_kuliah"],
                n["sks"],
                n["nilai"],
                BOBOT_MUTU.get(n["nilai"].upper(), 0.0),
            )
            for n in daftar_nilai
        ]
        cursor.executemany(query_insert_nilai, data_rows)
        conn.commit()


def proses_dokumen_pdf(file_pdf):
    """Mengekstrak teks metadata profil dan baris nilai dari dokumen Rangkuman Nilai Gunadarma."""
    teks_seluruh = ""
    with pdfplumber.open(file_pdf) as pdf:
        for page in pdf.pages:
            teks_seluruh += (page.extract_text() or "") + "\n"

    # Normalisasi karakter huruf Yunani yang sering muncul di PDF Gunadarma ke Latin
    teks_seluruh = (
        teks_seluruh.replace("Α", "A")
        .replace("Β", "B")
        .replace("Μ", "M")
        .replace("Τ", "T")
        .replace("Κ", "K")
        .replace("Ι", "I")
    )

    # 1. Ekstraksi Metadata Profil
    npm_match = re.search(r"NPM\s*[:]?\s*([0-9]+)", teks_seluruh, re.IGNORECASE)
    nama_match = re.search(r"NAMA\s*[:]?\s*([A-Za-z\s]+?)(?=\n|FAKULTAS|$)", teks_seluruh, re.IGNORECASE)
    jurusan_match = re.search(
        r"(?:PROGRAM STUDI|JURUSAN)\s*[:]?\s*(?:S1/)?([A-Za-z\s]+?)(?=\n|SKS|$)", teks_seluruh, re.IGNORECASE
    )

    # Menangani format SKS/IPK : 79/3.75
    ipk_match = re.search(r"SKS\s*/\s*IPK\s*[:]?\s*\d+\s*/\s*([0-9.]+)", teks_seluruh, re.IGNORECASE)
    if not ipk_match:
        ipk_match = re.search(r"IPK\s*[:]?\s*([0-9.]+)", teks_seluruh, re.IGNORECASE)

    profil = {
        "npm": npm_match.group(1).strip() if npm_match else "11124362",
        "nama": nama_match.group(1).strip() if nama_match else "Mahasiswa",
        "jurusan": jurusan_match.group(1).strip() if jurusan_match else "Sistem Informasi",
        "ipk_dokumen": ipk_match.group(1).strip() if ipk_match else "3.75",
    }

    pola_baris = re.compile(
        r"^\s*(\d{1,2})\s*\|?\s*([A-Z0-9]{7,10})\s*\|?\s*(.+?)\s*\|?\s*(\d+)\s*\|?\s*([A-E])\s*\|?\s*(\d+)\s*\|?\s*$",
        re.MULTILINE,
    )

    daftar_nilai = []
    for baris in teks_seluruh.split("\n"):
        match = pola_baris.match(baris.strip())
        if match:
            daftar_nilai.append(
                {
                    "no": int(match.group(1)),
                    "kode": match.group(2).strip(),
                    "mata_kuliah": match.group(3).strip(),
                    "sks": int(match.group(4)),
                    "nilai": match.group(5).strip().upper(),
                    "semester": int(match.group(6)),  # Semester langsung diambil dari kolom SEM
                }
            )

    return profil, daftar_nilai


def ambil_profil():
    if not DB_FILE.exists():
        return None
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT npm, nama, jurusan, ipk_dokumen FROM profil_mahasiswa LIMIT 1")
        row = cursor.fetchone()
        return {"npm": row[0], "nama": row[1], "jurusan": row[2], "ipk_cetak": row[3]} if row else None


def ambil_data_nilai(npm: str) -> pd.DataFrame:
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(
            """
            SELECT id, no, kode, mata_kuliah, sks, nilai, bobot, semester
            FROM riwayat_nilai
            WHERE npm = ?
            ORDER BY semester ASC, no ASC
            """,
            conn,
            params=(npm,),
        )


def update_nilai_matkul(id_matkul: int, nilai_baru: str):
    bobot_baru = BOBOT_MUTU.get(nilai_baru.upper(), 0.0)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE riwayat_nilai SET nilai = ?, bobot = ? WHERE id = ?",
            (nilai_baru.upper(), bobot_baru, id_matkul),
        )
        conn.commit()


def tentukan_predikat(ipk: float) -> str:
    if ipk >= 3.51:
        return "Cum Laude 🏆"
    elif ipk >= 3.00:
        return "Sangat Memuaskan ⭐"
    elif ipk >= 2.75:
        return "Memuaskan 👍"
    return "Cukup ⚠️"


def konversi_ke_excel(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Sheet rekap gabungan seluruh nilai
        df.to_excel(writer, index=False, sheet_name="Semua Nilai")

        # sheet terpisah per semester
        daftar_semester = sorted(df["semester"].unique())
        for sem in daftar_semester:
            df_sem = df[df["semester"] == sem]
            df_sem.to_excel(writer, index=False, sheet_name=f"Semester {sem}")

        workbook = writer.book

        # Palet Warna & Format
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        data_font = Font(name="Calibri", size=10)
        border_tipis = Border(
            left=Side(style="thin", color="D3D3D3"),
            right=Side(style="thin", color="D3D3D3"),
            top=Side(style="thin", color="D3D3D3"),
            bottom=Side(style="thin", color="D3D3D3"),
        )
        align_center = Alignment(horizontal="center", vertical="center")
        align_left = Alignment(horizontal="left", vertical="center")

        # styling rapi ke seluruh worksheet
        for sheetname in workbook.sheetnames:
            worksheet = workbook[sheetname]

            # Format Baris Header
            for col_num in range(1, worksheet.max_column + 1):
                cell = worksheet.cell(row=1, column=col_num)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = align_center
                cell.border = border_tipis
            worksheet.row_dimensions[1].height = 25

            # Format Baris Data & Zebra Striping
            for row_idx in range(2, worksheet.max_row + 1):
                worksheet.row_dimensions[row_idx].height = 20
                bg_color = "F9FAFB" if row_idx % 2 == 0 else "FFFFFF"
                row_fill = PatternFill(start_color=bg_color, end_color=bg_color, fill_type="solid")

                for col_idx in range(1, worksheet.max_column + 1):
                    cell = worksheet.cell(row=row_idx, column=col_idx)
                    cell.font = data_font
                    cell.fill = row_fill
                    cell.border = border_tipis

                    # Kolom mata kuliah rata kiri, sisanya rata tengah
                    header_val = str(worksheet.cell(row=1, column=col_idx).value or "").lower()
                    if "mata" in header_val:
                        cell.alignment = align_left
                    else:
                        cell.alignment = align_center

            # Auto-fit Lebar Kolom
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = get_column_letter(col[0].column)
                worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

    return output.getvalue()


with st.sidebar:
    st.header("📂 Sumber Dokumen")
    berkas_pdf = st.file_uploader("Unggah PDF Transkrip / Rangkuman Nilai", type=["pdf"])

    if berkas_pdf:
        with st.spinner("Mengekstrak data dokumen..."):
            profil_ekstrak, nilai_ekstrak = proses_dokumen_pdf(berkas_pdf)
            if nilai_ekstrak:
                simpan_hasil_ekstraksi(profil_ekstrak, nilai_ekstrak)
                st.sidebar.success(f"Berhasil mengimpor {len(nilai_ekstrak)} mata kuliah!")
            else:
                st.sidebar.error("Gagal mendeteksi tabel nilai dari format PDF ini.")

    st.divider()

    profil = ambil_profil()
    if profil:
        st.header("👤 Profil Mahasiswa")
        st.markdown(f"**Nama:**\n{profil['nama']}")
        st.markdown(f"**NPM:** `{profil['npm']}`")
        st.markdown(f"**Jurusan:** {profil['jurusan']}")
        st.caption(f"IPK Dokumen: **{profil['ipk_cetak']}**")
    else:
        st.info("Belum ada data mahasiswa tersimpan.")

    st.divider()
    st.caption("Academic Evaluation Dashboard • v1.0")


st.title("🎓 Dashboard Evaluasi Akademik Mahasiswa")
st.caption("Sistem Pemantauan Capaian Indeks Prestasi, Distribusi Nilai, dan Simulasi Kelulusan")

if not profil:
    st.info(
        "👋 Selamat datang! Silakan unggah dokumen PDF transkrip nilai melalui panel sidebar di sebelah kiri untuk memulai analisis."
    )
    st.stop()

df_semua = ambil_data_nilai(profil["npm"])
if df_semua.empty:
    st.warning("Data mata kuliah belum tersedia di database.")
    st.stop()

# Kalkulasi Metrik Global
total_sks = int(df_semua["sks"].sum())
total_mutu = float((df_semua["sks"] * df_semua["bobot"]).sum())
ipk_hitung = round(total_mutu / total_sks, 2) if total_sks > 0 else 0.0
predikat_teks = tentukan_predikat(ipk_hitung)

# Rekap Per Semester
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

# Kartu Metrik
c1, c2, c3, c4 = st.columns(4)
c1.metric("IPK Kumulatif", f"{ipk_hitung:.2f}", delta=f"Dokumen: {profil['ipk_cetak']}")
c2.metric("Total SKS Tuntas", f"{total_sks} SKS")
c3.metric("Total Mata Kuliah", f"{len(df_semua)} Matkul")
c4.metric("Predikat Kelulusan", predikat_teks)

st.divider()

tab_analisis, tab_filter_crud, tab_ekspor = st.tabs(
    [
        "📊 Analitik Tren & Sebaran",
        "📋 Eksplorasi & Simulasi Nilai (CRUD)",
        "📥 Pusat Unduhan",
    ]
)

with tab_analisis:
    col_g1, col_g2 = st.columns([3, 2])
    with col_g1:
        st.markdown("**Tren Fluktuasi IPS Antarsemester**")
        df_line = df_sem[["semester", "ips"]].copy()
        df_line["Label"] = "Semester " + df_line["semester"].astype(str)
        st.line_chart(df_line.set_index("Label")[["ips"]], use_container_width=True)

    with col_g2:
        st.markdown("**Ringkasan Beban & Indeks Prestasi**")
        st.dataframe(
            df_sem[["semester", "total_sks", "ips"]],
            column_config={
                "semester": "Semester",
                "total_sks": "Beban SKS",
                "ips": "IPS",
            },
            hide_index=True,
            use_container_width=True,
        )

    st.markdown("**Distribusi Mutu Nilai**")
    st.bar_chart(df_semua["nilai"].value_counts().sort_index(), color="#29b5e8")

with tab_filter_crud:
    f1, f2 = st.columns([1, 2])
    with f1:
        opsi_sem = ["Semua Semester"] + sorted(df_semua["semester"].unique().tolist())
        filter_sem = st.selectbox("Filter Semester:", opsi_sem)
    with f2:
        cari_matkul = st.text_input("🔍 Cari Mata Kuliah / Kode:", placeholder="Ketik nama atau kode mata kuliah...")

    df_tampil = df_semua.copy()
    if filter_sem != "Semua Semester":
        df_tampil = df_tampil[df_tampil["semester"] == filter_sem]
    if cari_matkul:
        pola = cari_matkul.strip().lower()
        df_tampil = df_tampil[
            df_tampil["mata_kuliah"].str.lower().str.contains(pola) | df_tampil["kode"].str.lower().str.contains(pola)
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

    with st.expander("🛠️ Form Simulasi Perbaikan Nilai (Semester Pendek / Perbaikan)", expanded=False):
        opsi_pilihan = {
            f"Sem {r['semester']} | {r['kode']} - {r['mata_kuliah']} (Nilai: {r['nilai']})": r["id"]
            for _, r in df_semua.iterrows()
        }
        label_terpilih = st.selectbox("Pilih Mata Kuliah:", list(opsi_pilihan.keys()))
        id_edit = opsi_pilihan[label_terpilih]
        data_target = df_semua[df_semua["id"] == id_edit].iloc[0]

        e1, e2, e3 = st.columns([2, 1, 1])
        with e1:
            st.write(f"Mata Kuliah: **{data_target['mata_kuliah']}** ({data_target['sks']} SKS)")
        with e2:
            nilai_baru = st.selectbox("Nilai Baru:", ["A", "B", "C", "D", "E"], index=0)
        with e3:
            st.write("")
            st.write("")
            if st.button("Simpan Perubahan", type="primary"):
                update_nilai_matkul(id_edit, nilai_baru)
                st.success(f"Nilai {data_target['mata_kuliah']} berhasil diubah ke {nilai_baru}!")
                st.rerun()

with tab_ekspor:
    st.subheader("Ekspor Laporan Transkrip")
    df_unduh = df_semua[["semester", "no", "kode", "mata_kuliah", "sks", "nilai", "bobot"]].copy()

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv_data = df_unduh.to_csv(index=False).encode("utf-8")
        st.info("📄 Format CSV untuk integrasi analitik atau basis data.")
        st.download_button(
            label="⬇️ Unduh Berkas CSV",
            data=csv_data,
            file_name=f"Transkrip_{profil['npm']}.csv",
            mime="text/csv",
            type="primary",
        )

    with col_dl2:
        try:
            excel_data = konversi_ke_excel(df_unduh)
            st.info("📊 Format Excel (.xlsx) rapi dengan penamaan sheet.")
            st.download_button(
                label="⬇️ Unduh Berkas Excel",
                data=excel_data,
                file_name=f"Transkrip_{profil['npm']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )
        except Exception:
            st.warning("Modul `openpyxl` belum terpasang untuk ekspor Excel.")
