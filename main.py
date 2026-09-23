# main.py
import io
import time
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from module.calculator import BOBOT_MUTU, hitung_target_ips, tentukan_predikat
from module.schemas import (
    MataKuliahResponse,
    ProfilResponse,
    TargetIPKRequest,
    TargetIPKResponse,
    UpdateNilaiRequest,
)
import shutil
from module.database import (
    DB_PATH,
    ambil_data_nilai,
    ambil_profil,
    inisialisasi_database,
    jalankan_seeder,
    simpan_hasil_ekstraksi,
    update_nilai_matkul,
)
from module.logger import logger
from module.parser import proses_dokumen_pdf
from module.schemas import MataKuliahResponse, ProfilResponse, UpdateNilaiRequest
from pathlib import Path

# path absolut root proyek dibagian atas
BASE_DIR = Path(__file__).resolve().parent

inisialisasi_database()

app = FastAPI(
    title="Academic Evaluation API",
    description="Backend REST API untuk pengelolaan dan evaluasi transkrip akademik mahasiswa",
    version="2.1.0",
)

# Konfigurasi CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    waktu_mulai = time.time()
    response = await call_next(request)
    durasi = (time.time() - waktu_mulai) * 1000

    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Waktu: {durasi:.2f}ms")
    return response


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Terjadi kesalahan internal pada {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "pesan": "Terjadi kesalahan internal pada server backend.",
            "detail": str(exc),
        },
    )


# ENDPOINT REST API
@app.get("/", tags=["Sistem"])
def root():
    return {"pesan": "API Evaluasi Akademik Aktif!", "status": "online"}


@app.get("/mahasiswa/profil", response_model=ProfilResponse, tags=["Mahasiswa"])
def dapatkan_profil():
    """Mengambil data profil mahasiswa yang tersimpan di basis data."""
    profil = ambil_profil()
    if not profil:
        raise HTTPException(status_code=404, detail="Data profil mahasiswa belum ditemukan")
    return profil


@app.get(
    "/mahasiswa/{npm}/nilai",
    response_model=list[MataKuliahResponse],
    tags=["Akademik"],
)
def dapatkan_riwayat_nilai(npm: str):
    """Mengambil daftar riwayat nilai mahasiswa berdasarkan NPM."""
    df = ambil_data_nilai(npm)
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Belum ada riwayat nilai untuk mahasiswa dengan NPM {npm}",
        )
    return df.to_dict(orient="records")


@app.put("/nilai/{id_matkul}", tags=["Akademik"])
def perbarui_nilai(id_matkul: int, payload: UpdateNilaiRequest):
    """Memperbarui nilai huruf mata kuliah."""
    nilai_bersih = payload.nilai.upper()
    update_nilai_matkul(id_matkul, nilai_bersih)
    return {
        "status": "success",
        "pesan": f"Nilai berhasil diperbarui menjadi {nilai_bersih}",
        "bobot_baru": BOBOT_MUTU[nilai_bersih],
    }


@app.get("/kalkulator/predikat/{ipk}", tags=["Kalkulator"])
def cek_predikat(ipk: float):
    """Menentukan predikat yudisium berdasarkan capaian IPK."""
    if not (0.0 <= ipk <= 4.0):
        raise HTTPException(status_code=400, detail="Nilai IPK harus berada di rentang 0.0 - 4.0")
    return {"ipk": ipk, "predikat": tentukan_predikat(ipk)}


@app.post(
    "/kalkulator/target-ipk",
    response_model=TargetIPKResponse,
    tags=["Kalkulator"],
)
def simulasikan_target_ipk(payload: TargetIPKRequest):
    """Menghitung kebutuhan IPS semester berikutnya untuk mencapai target IPK."""
    try:
        hasil = hitung_target_ips(
            sks_lalu=payload.sks_lalu,
            ipk_lalu=payload.ipk_lalu,
            sks_rencana=payload.sks_rencana,
            target_ipk=payload.target_ipk,
        )
        return hasil
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/mahasiswa/unggah-pdf", tags=["Mahasiswa"])
async def unggah_transkrip_pdf(file: UploadFile = File(...)):
    """Menerima berkas PDF transkrip, mengekstrak data, dan menyimpannya ke database."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Format berkas tidak didukung. Harap unggah file PDF.",
        )

    konten = await file.read()
    aliran_berkas = io.BytesIO(konten)
    profil_ekstrak, nilai_ekstrak = proses_dokumen_pdf(aliran_berkas)

    if not nilai_ekstrak:
        raise HTTPException(
            status_code=422,
            detail="Gagal mendeteksi tabel nilai dari format dokumen PDF ini.",
        )

    simpan_hasil_ekstraksi(profil_ekstrak, nilai_ekstrak)

    return {
        "status": "success",
        "pesan": f"Berhasil memproses dan menyimpan {len(nilai_ekstrak)} mata kuliah.",
        "profil": profil_ekstrak,
    }


@app.post("/sistem/seed-data", tags=["Sistem"])
def seed_sample_data():
    """Mengisi baris data dengan data sampel pengujian (dummy)."""
    profil, jumlah_matkul = jalankan_seeder()
    logger.info("Data sampel pengujian berhasil dimasukkan ke baris data.")
    return {
        "status": "success",
        "pesan": f"Berhasil memuat data sampel untuk {profil['nama']} ({jumlah_matkul} mata kuliah).",
        "profil": profil,
    }


@app.post("/sistem/backup-db", tags=["Sistem"])
def backup_database():
    """Membuat salinan cadangan dari file database SQLite."""
    sumber = BASE_DIR / "akademik.db"
    # Pastikan folder logs tersedia
    folder_logs = DB_PATH.parent / "logs"
    folder_logs.mkdir(parents=True, exist_ok=True)

    tujuan = folder_logs / f"backup_akademik_{int(time.time())}.db"

    # Jika database belum terbentuk, jalankan inisialisasi tabel terlebih dahulu
    if not DB_PATH.exists():
        inisialisasi_database()

    try:
        shutil.copyfile(DB_PATH, tujuan)
        logger.info(f"Database berhasil dicadangkan ke {tujuan.name}")
        return {
            "status": "success",
            "pesan": f"Cadangan database berhasil dibuat: {tujuan.name}",
            "path_sumber": str(DB_PATH),
        }
    except Exception as e:
        logger.error(f"Gagal mencadangkan database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gagal mencadangkan database: {str(e)}")
