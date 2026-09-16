# test_akademik.py - Unit Test Terintegrasi dengan Modul
import pytest
from module.calculator import BOBOT_MUTU, hitung_ipk, tentukan_predikat


def test_konversi_bobot_mutu():
    assert BOBOT_MUTU["A"] == 4.0
    assert BOBOT_MUTU["B"] == 3.0
    assert BOBOT_MUTU["C"] == 2.0
    assert BOBOT_MUTU["D"] == 1.0
    assert BOBOT_MUTU["E"] == 0.0


def test_hitung_ipk_valid():
    sample_matkul = [
        {"mata_kuliah": "Algoritma 1", "sks": 3, "nilai": "B"},  # Mutu: 9
        {"mata_kuliah": "Matematika 1", "sks": 2, "nilai": "A"},  # Mutu: 8
    ]
    # Total SKS = 5, Total Mutu = 17 -> 17 / 5 = 3.40
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
