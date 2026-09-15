# 🎓 Academic Evaluation Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/SQLite-Integrated-lightgrey.svg)](https://sqlite.org/)
[![Tests](https://img.shields.io/badge/pytest-Passing-brightgreen.svg)](https://docs.pytest.org/)

Aplikasi web analitik akademik berbasis Python dan Streamlit yang mengotomatisasi ekstraksi dokumen rangkuman nilai (PDF) ke basis data lokal SQLite, memvisualisasikan tren fluktuasi indeks prestasi, menyediakan fitur simulasi perbaikan nilai (CRUD), serta ekspor data ke format Excel dan CSV.

---

## 🚀 Live Demo
Aplikasi sudah dipublikasikan secara online dan bisa diakses langsung:  
👉 **[Buka Academic Evaluation Dashboard](https://share.streamlit.io)** *(Ganti tautan ini dengan URL Streamlit Cloud kamu)*

---

## ✨ Fitur Utama
* **Ekstraksi PDF Cerdas**: Parsing otomatis dokumen Rangkuman Nilai Gunadarma menggunakan `pdfplumber` dan Regex toleran Unicode.
* **Penyimpanan SQLite Terstruktur**: Data profil dan riwayat nilai otomatis tersimpan ke basis data relasional lokal (`akademik.db`).
* **Visualisasi Tren Interaktif**: Grafik garis fluktuasi IPS per semester dan diagram batang sebaran huruf mutu.
* **Simulasi Perbaikan Nilai (CRUD)**: Fasilitas pengubahan nilai mata kuliah secara instan untuk memperkirakan kenaikan IPK kumulatif.
* **Pusat Unduhan Multi-Format**: Ekspor riwayat nilai langsung ke format `.xlsx` (Excel) dan `.csv`.

---

## 🛠️ Tech Stack
* **Bahasa**: Python 3.10+
* **Framework Web**: Streamlit
* **Olah Data**: Pandas, OpenPyXL
* **Ekstraksi Dokumen**: pdfplumber, Regular Expression (`re`)
* **Basis Data**: SQLite3
* **Pengujian Otomatis**: pytest

---

## 💻 Panduan Menjalankan di Lokal

1. **Clone Repositori**
   ```bash
   git clone [https://github.com/Kasep2512/Belajar-Python.git](https://github.com/Kasep2512/Belajar-Python.git)
   cd Belajar-Python