# test_akademik.py - Unit Test Logika Evaluasi Akademik
import pytest

BOBOT_MUTU = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.0}


def hitung_ipk(daftar_matkul: list[dict]) -> float:
    """Helper kalkulasi IPK berbasis list mata kuliah."""
    if not daftar_matkul:
        return 0.0
    total_sks = sum(m["sks"] for m in daftar_matkul)
    if total_sks == 0:
        return 0.0
    total_mutu = sum(m["sks"] * BOBOT_MUTU.get(m["nilai"].upper(), 0.0) for m in daftar_matkul)
    return round(total_mutu / total_sks, 2)


def tentukan_predikat(ipk: float) -> str:
    """Helper penentuan predikat kelulusan."""
    if ipk >= 3.51:
        return "CumLaude 🏆"
    elif ipk >= 3.00:
        return "Sangat Memuaskan ⭐"
    elif ipk >= 2.75:
        return "Memuaskan 👍"
    return "Cukup ⚠️"


def test_koversi_bobot_mutu():
    assert BOBOT_MUTU["A"] == 4.0
    assert BOBOT_MUTU["B"] == 3.0
    assert BOBOT_MUTU["C"] == 2.0
    assert BOBOT_MUTU["D"] == 1.0
    assert BOBOT_MUTU["E"] == 0.0


def test_hitung_ipk_valid():
    sample_matkul = [
        {"mata_kuliah": "Algoritma 1", "sks": 3, "nilai": "B"},  # Mutu: 3 * 3 = 9
        {"mata_kuliah": "Aritmatika 1", "sks": 2, "nilai": "A"},  # Mutu: 2 * 4 = 8
    ]
    assert hitung_ipk(sample_matkul) == 3.40


def test_hitung_ipk_kosong():
    assert hitung_ipk([]) == 0.0


@pytest.mark.parametrize(
    "ipk_input, predikat_ekspektasi",
    [
        (3.85, "CumLaude 🏆"),
        (3.51, "CumLaude 🏆"),
        (3.50, "Sangat Memuaskan ⭐"),
        (3.00, "Sangat Memuaskan ⭐"),
        (2.80, "Memuaskan 👍"),
        (2.50, "Cukup ⚠️"),
    ],
)
def test_penentuan_predikat(ipk_input, predikat_ekspektasi):
    assert tentukan_predikat(ipk_input) == predikat_ekspektasi
