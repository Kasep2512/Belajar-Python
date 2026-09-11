# Hari 7: Struktur Koleksi List dan Dictionary
from rich.console import Console
from rich.table import Table

console = Console()

proyek_info: dict = {
    "nama": "Dashboard Belajar Python",
    "kategori": "Web Frontend (Reactive)",
    "status": "Sedang Berjalan",
}

daftar_modul: list[dict] = [
    {"hari": 1, "topik": "Instalasi Python 3,13", "selesai": True},
    {"hari": 2, "topik": "Setup VC Code & Ruff", "selesai": True},
    {"hari": 3, "topik": "Git Lokal & Indentitas", "selesai": True},
    {"hari": 4, "topik": "GitHub & .gitignore", "selesai": True},
    {"hari": 5, "topik": "Virtual Environment (venv)", "selesai": True},
    {"hari": 6, "topik": "Tipe Data Primitif & Rich Panel", "selesai": True},
    {"hari": 7, "topik": "Struktur Koleksi (List & Dict)", "selesai": False},
]

daftar_modul.append(
    {"hari": 8, "topik": "Alur Kontrol (If/Else & Loop)", "selesai": False}
)

tabel = Table(title=f"[bold cyan]{proyek_info['nama']}[/bold cyan]")

tabel.add_column("Hari", justify="center", style="yellow")
tabel.add_column("Topik Materi", style="white")
tabel.add_column("Status", justify="center")

for modul in daftar_modul:
    if modul["selesai"]:
        status_teks = "[bold green]SELESAI[/bold green]"
    else:
        status_teks = "[bold blue]DALAM PROGRES[/bold blue]"
    tabel.add_row(f"H-{modul['hari']}", modul["topik"], status_teks)

console.print(tabel)
