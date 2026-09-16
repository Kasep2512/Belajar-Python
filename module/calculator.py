"""Modul kalkulasi akademik: konversi bobot mutu, kalkulasi IPK/IPS, dan predikat kelulusan."""

BOBOT_MUTU = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.0}


def ambil_bobot(nilai: str) -> float:
    """Mengembalikan bobot angka dari huruf mutu nilai."""
    return BOBOT_MUTU.get(nilai.strip().upper(), 0.0)


def hitung_ipk(daftar_matkul: list[dict]) -> float:
    """Menghitung IPK kumulatif dari daftar mata kuliah.

    Setiap item dict minimal memiliki key: 'sks' (int) dan 'nilai' (str).
    """
    if not daftar_matkul:
        return 0.0

    total_sks = sum(m["sks"] for m in daftar_matkul)
    if total_sks == 0:
        return 0.0

    total_mutu = sum(m["sks"] * ambil_bobot(m["nilai"]) for m in daftar_matkul)
    return round(total_mutu / total_sks, 2)


def tentukan_predikat(ipk: float) -> str:
    """Menentukan predikat kelulusan berdasarkan standar yudisium."""
    if ipk >= 3.51:
        return "CumLaude 🏆"
    elif ipk >= 3.00:
        return "Sangat Memuaskan ⭐"
    elif ipk >= 2.75:
        return "Memuaskan 👍"
    return "Cukup ⚠️"
