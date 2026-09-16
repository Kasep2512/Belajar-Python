"""Modul operasi basis data SQLite untuk profil dan riwayat nilai mahasiswa."""

from pathlib import Path
import sqlite3
import pandas as pd
from module.calculator import BOBOT_MUTU

DB_FILE = Path("akademik.db")


def inisialisasi_database():
    """Membuat tabel profil_mahasiswa dan riwayat_nilai jika belum ada."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profil_mahasiswa (
                npm TEXT PRIMARY KEY,
                nama TEXT,
                jurusan TEXT,
                ipk_dokumen TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS riwayat_nilai (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npm TEXT,
                semester INTEGER,
                no INTEGER,
                kode TEXT,
                mata_kuliah TEXT,
                sks INTEGER,
                nilai TEXT,
                bobot REAL,
                FOREIGN KEY (npm) REFERENCES profil_mahasiswa (npm)
            )
        """)
        conn.commit()


def simpan_hasil_ekstraksi(profil: dict, daftar_nilai: list[dict]):
    """Menyimpan data hasil parsing PDF ke dalam database SQLite."""
    inisialisasi_database()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO profil_mahasiswa (npm, nama, jurusan, ipk_dokumen)
            VALUES (?, ?, ?, ?)
            """,
            (profil.get("npm"), profil.get("nama"), profil.get("jurusan"), profil.get("ipk_dokumen")),
        )

        cursor.execute("DELETE FROM riwayat_nilai WHERE npm = ?", (profil.get("npm"),))

        query_insert_nilai = """
            INSERT INTO riwayat_nilai (npm, semester, no, kode, mata_kuliah, sks, nilai, bobot)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        data_rows = [
            (
                profil.get("npm"),
                n["semester"],
                n["no"],
                n["kode"],
                n["mata_kuliah"],
                n["sks"],
                n["nilai"],
                BOBOT_MUTU.get(n["nilai"].upper(), 0.0),
            )
            for n in daftar_nilai
        ]
        cursor.executemany(query_insert_nilai, data_rows)
        conn.commit()


def ambil_profil():
    """Mengambil data profil mahasiswa terdaftar."""
    if not DB_FILE.exists():
        return None
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT npm, nama, jurusan, ipk_dokumen FROM profil_mahasiswa LIMIT 1")
        row = cursor.fetchone()
        return {"npm": row[0], "nama": row[1], "jurusan": row[2], "ipk_cetak": row[3]} if row else None


def ambil_data_nilai(npm: str) -> pd.DataFrame:
    """Mengambil seluruh riwayat nilai mahasiswa dalam bentuk DataFrame pandas."""
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(
            """
            SELECT id, no, kode, mata_kuliah, sks, nilai, bobot, semester
            FROM riwayat_nilai
            WHERE npm = ?
            ORDER BY semester ASC, no ASC
            """,
            conn,
            params=(npm,),
        )


def update_nilai_matkul(id_matkul: int, nilai_baru: str):
    """Memperbarui nilai dan bobot mata kuliah tertentu untuk simulasi perbaikan nilai."""
    bobot_baru = BOBOT_MUTU.get(nilai_baru.upper(), 0.0)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE riwayat_nilai SET nilai = ?, bobot = ? WHERE id = ?",
            (nilai_baru.upper(), bobot_baru, id_matkul),
        )
        conn.commit()
