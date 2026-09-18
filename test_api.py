# Day 25 test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_endpoint_root():
    """Menguji apakah endpoint root / aktif dan mengembalikan status online."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "pesan" in data


def test_endpoint_predikat_sukses():
    """Menguji kalkulasi predikat via endpoint API."""
    response = client.get("/kalkulator/predikat/3.75")
    assert response.status_code == 200
    data = response.json()
    assert data["ipk"] == 3.75
    assert "CumLaude" in data["predikat"]


def test_endpoint_predikat_ipk_invalid():
    """Menguji validasi error saat IPK berada di luar rentang 0.0 - 4.0."""
    response = client.get("/kalkulator/predikat/4.5")
    assert response.status_code == 400
    assert response.json()["detail"] == "Nilai IPK harus berada di rentang 0.0 - 4.0"


def test_endpoint_update_nilai_validasi_pydantic_error():
    """Menguji apakah Pydantic menolak format nilai yang tidak sesuai (misal huruf 'Z')."""
    payload = {"nilai": "Z"}  # Seharusnya hanya A, B, C, D, E
    response = client.put("/nilai/1", json=payload)
    assert response.status_code == 422


def test_endpoint_profil_tidak_ada_atau_berhasil():
    """Menguji respons profil (harus mengembalikan 200 jika data ada, atau 404 jika kosong)."""
    response = client.get("/mahasiswa/profil")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "npm" in data
        assert "nama" in data
