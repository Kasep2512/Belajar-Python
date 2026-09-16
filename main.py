# Day 22 main.py fastAPI
from fastapi import FastAPI
from module.calculator import BOBOT_MUTU, tentukan_predikat

app = FastAPI(
    title="Academic Evaluation API",
    description="Backend REST API untuk perhitungan evaluasi akademi",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"pesan": "API Evaluasi Akademik Aktif!", "status": "online"}


@app.get("/bobot")
def cek_semua_bobot():
    return {"daftar_bobot": BOBOT_MUTU}


@app.get("/predikat/{ipk}")
def cek_predikat(ipk: float):
    predikat = tentukan_predikat(ipk)
    return {"ipk": ipk, "predikat": predikat}
