# Day 23 FastAPI, pydantic & endpoint CRUD
from fastapi import FastAPI, HTTPException
from module.calculator import BOBOT_MUTU, tentukan_predikat
from module.database import (
    ambil_data_nilai,
    ambil_profil,
    inisialisasi_database,
    update_nilai_matkul,
)
from module.schemas import MataKuliahResponse, ProfilResponse, UpdateNilaiRequest

app = FastAPI(
    title="Academic Evaluation API",
    description="Backend REST API untuk pengelolaan dan evaluasi transkrip akademik mahasiswa",
    version="2.0.0",
)


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
    """Memperbarui nilai huruf mata kuliah (simulasi perbaikan nilai/SP)."""
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
