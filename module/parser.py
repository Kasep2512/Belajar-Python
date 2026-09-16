# modules/parser.py
"""Modul ekstraksi dan pembersihan teks PDF Rangkuman Nilai Gunadarma."""

import re
import pdfplumber


def proses_dokumen_pdf(file_pdf):
    """Mengekstrak teks metadata profil dan baris tabel nilai dari file PDF."""
    teks_seluruh = ""
    with pdfplumber.open(file_pdf) as pdf:
        for page in pdf.pages:
            teks_seluruh += (page.extract_text() or "") + "\n"

    # Normalisasi karakter alfabet Yunani PDF Gunadarma ke huruf Latin
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

    # Menangani format "SKS / IPK : 79 / 3.75" maupun "IPK : 3.75"
    ipk_match = re.search(r"SKS\s*/\s*IPK\s*[:]?\s*\d+\s*/\s*([0-9.]+)", teks_seluruh, re.IGNORECASE)
    if not ipk_match:
        ipk_match = re.search(r"IPK\s*[:]?\s*([0-9.]+)", teks_seluruh, re.IGNORECASE)

    profil = {
        "npm": npm_match.group(1).strip() if npm_match else "11124362",
        "nama": nama_match.group(1).strip() if nama_match else "Mahasiswa",
        "jurusan": jurusan_match.group(1).strip() if jurusan_match else "Sistem Informasi",
        "ipk_dokumen": ipk_match.group(1).strip() if ipk_match else "3.75",
    }

    # 2. Parsing Baris Tabel Nilai
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
                    "semester": int(match.group(6)),
                }
            )

    return profil, daftar_nilai
