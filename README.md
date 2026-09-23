# 🎓 Academic Evaluation Dashboard (Client-Server Architecture)

Aplikasi evaluasi akademik komprehensif berbasis Python dengan arsitektur modern *Client-Server*. Dashboard ini mengekstraksi data transkrip nilai akademik dari dokumen PDF, menyimpannya ke basis data SQLite relasional, menyajikan visualisasi analitik tren IPK/IPS secara interaktif, serta menyediakan simulator target kelulusan prediktif (*What-If Calculator*).

---

## 🌟 Fitur Utama

- **Otomasi Ekstraksi PDF**: Ekstraksi teks dan tabel nilai otomatis dari transkrip akademik menggunakan `pdfplumber` dan *regular expression*.
- **RESTful Backend API**: Dibangun dengan **FastAPI** lengkap dengan skema validasi data **Pydantic**, CORS Middleware, *centralized logging*, dan *global exception handling*.
- **Frontend Interaktif**: Dashboard analitik berbasis **Streamlit** dengan visualisasi tren performa nilai antarsemester (`pandas`, visual grafik interaktif).
- **CRUD & Simulasi Nilai**: Kemampuan simulasi pembaruan nilai matakuliah secara *real-time* melalui HTTP REST Client.
- **Perencana Target IPK (What-If Calculator)**: Formula prediktif untuk menghitung minimal capaian IPS semester berikutnya guna meraih target IPK tertentu.
- **Pusat Unduhan**: Ekspor transkrip ke berkas CSV dan Excel (`openpyxl`) dengan pemisahan lembar kerja (*sheet*) otomatis per semester.
- **Database Seeder & Backup**: Endpoint bawaan untuk pengisian data uji coba (*demo mode*) serta pencadangan berkas basis data SQLite secara berkala.
- **Pengujian Otomatis & CI**: Unit testing dan API testing otomatis dengan `pytest` dan `httpx`, terintegrasi dalam pipeline **GitHub Actions**.
- **Container-Ready**: Konfigurasi `Dockerfile` terpisah untuk Frontend dan Backend serta orkestrasi `docker-compose.yml`.

---

## 🏗️ Arsitektur Proyek

```text
├── .github/workflows/    # CI Pipeline otomatis (GitHub Actions)
├── logs/                 # Pencatatan log sistem dan file cadangan database
├── module/               # Modul logika bisnis inti
│   ├── calculator.py     # Formula IPK, bobot mutu, dan target IPS prediktif
│   ├── database.py       # Operasi SQLite relasional, seeder, dan CRUD
│   ├── exporter.py       # Konversi dan styling ekspor Excel multi-sheet
│   ├── logger.py         # Konfigurasi sistem pencatatan log terpusat
│   ├── parser.py         # Regex dan ekstraksi teks berkas PDF
│   └── schemas.py        # Model validasi data request/response (Pydantic)
├── tests/                # Otomasi pengujian perangkat lunak
│   ├── test_akademik.py   # Pengujian unit kalkulator & logika bisnis
│   ├── test_api.py        # Pengujian endpoint REST API (TestClient)
│   └── test_calculator.py # Pengujian formula simulasi prediktif
├── app.py                # Antarmuka dashboard pengguna (Streamlit)
├── main.py               # Server backend REST API (FastAPI)
├── docker-compose.yml    # Orkestrasi kontainer layanan ganda
├── Dockerfile.api        # Spesifikasi image kontainer Backend
├── Dockerfile.web        # Spesifikasi image kontainer Frontend
└── requirements.txt      # Daftar pustaka dan dependensi proyek
```

---

## 🛠️ Tech Stack

- **Bahasa**: Python 3.12
- **Backend**: FastAPI, Uvicorn, Pydantic
- **Frontend**: Streamlit
- **Analisis & Pengolahan Data**: Pandas, pdfplumber, openpyxl
- **Basis Data**: SQLite3
- **Pengujian (Testing)**: Pytest, HTTPX
- **DevOps & Kontainer**: Docker, Docker Compose, GitHub Actions (CI)

---

## 🚀 Panduan Memulai

### 1. Kloning Repositori
```bash
git clone https://github.com/username/academic-evaluation-dashboard.git
cd academic-evaluation-dashboard
```

### 2. Konfigurasi Lingkungan Virtual
```bash
# Membuat virtual environment
python -m venv .venv

# Mengaktifkan virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Memasang dependensi
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi Secara Lokal

Jalankan kedua perintah berikut pada dua terminal terpisah:

**Terminal 1 — Backend API (FastAPI):**
```bash
uvicorn main:app --reload --port 8000
```
> Dokumentasi interaktif Swagger UI dapat diakses di: `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`

**Terminal 2 — Frontend Dashboard (Streamlit):**
```bash
streamlit run app.py
```
> Antarmuka Dashboard dapat diakses di: `http://localhost:8501`

---

## 🐳 Menjalankan Menggunakan Docker (Opsional)

Jika lingkungan Docker sudah siap, seluruh arsitektur dapat dijalankan secara bersamaan:

```bash
docker compose up --build
```
- **Frontend Dashboard**: `http://localhost:8501`
- **Backend API Docs**: `http://localhost:8000/docs`

---

## 🧪 Menjalankan Pengujian Otomatis

Jalankan suite pengujian unit dan pengujian endpoint API:
```bash
pytest -v
```

---

## 📝 Lisensi

Proyek ini dikembangkan untuk tujuan edukasi dan portofolio rekayasa perangkat lunak. Bebas digunakan dan dimodifikasi.