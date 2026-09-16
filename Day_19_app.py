# Day 21 pada app.py - Academic Evaluation Dashboard (Modular Architecture)
import streamlit as st

from module.calculator import tentukan_predikat
from module.database import (
    ambil_data_nilai,
    ambil_profil,
    simpan_hasil_ekstraksi,
    update_nilai_matkul,
)
from module.exporter import konversi_ke_excel
from module.parser import proses_dokumen_pdf

st.set_page_config(
    page_title="Academic Evaluation Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


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
    st.caption("Academic Evaluation Dashboard • v2.0 (Modular)")


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
            st.info("📊 Format Excel (.xlsx) rapi dengan pemisahan sheet per semester.")
            st.download_button(
                label="⬇️ Unduh Berkas Excel",
                data=excel_data,
                file_name=f"Transkrip_{profil['npm']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )
        except Exception:
            st.warning("Modul `openpyxl` belum terpasang untuk ekspor Excel.")
