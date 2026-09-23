import pytest
from module.calculator import hitung_target_ips, tentukan_predikat


# Pengujian Logika Predikat
def test_tentukan_predikat_pujian():
    """Menguji predikat dengan Pujian (CumLaude)."""
    assert "CumLaude" in tentukan_predikat(3.75)
    assert "CumLaude" in tentukan_predikat(3.90)


def test_tentukan_predikat_sangat_memuaskan():
    """Menguji predikat Sangat Memuaskan."""
    assert "Sangat Memuaskan" in tentukan_predikat(3.25)
    assert "Sangat Memuaskan" in tentukan_predikat(3.49)


def test_tentukan_predikat_memuaskan():
    """Menguji predikat Memuaskan."""
    assert "Memuaskan" in tentukan_predikat(2.76)
    assert "Memuaskan" in tentukan_predikat(3.00)


# Pengujian simulasi target IPK
def test_hitung_ips_valid():
    """Target realistis: 60 SKS dengan IPK 3.50, ambil 20 SKS, target IPK 3.60.

    Mutu lalu = 60 * 3.50 = 210.0
    Mutu total target = 80 * 3.60 288.0
    Mutu butuh = 78.0 -> IPS butuh = 78.0 / 20 = 3.90
    """
    hasil = hitung_target_ips(sks_lalu=60, ipk_lalu=3.50, sks_rencana=20, target_ipk=3.60)
    assert hasil["tercapai"] is True
    assert hasil["ips_dibutuhkan"] == 3.90
    assert hasil["sks_total_nanti"] == 80


def test_hitung_ips_mustahil():
    """Target mustahil: butuh IPS di atas 4.00."""
    hasil = hitung_target_ips(sks_lalu=60, ipk_lalu=2.00, sks_rencana=10, target_ipk=3.80)
    assert hasil["tercapai"] is False
    assert hasil["ips_dibutuhkan"] > 4.00


def test_hitung_target_ips_error_input():
    """Memastikan sistem melempar ValueError saat menerima input tidak valid."""
    # SKS rencana 0 atau negatif
    with pytest.raises(ValueError):
        hitung_target_ips(sks_lalu=60, ipk_lalu=3.50, sks_rencana=0, target_ipk=3.70)

    # Target IPK di luar batas (misal > 4.0)
    with pytest.raises(ValueError):
        hitung_target_ips(sks_lalu=60, ipk_lalu=3.50, sks_rencana=20, target_ipk=4.50)
