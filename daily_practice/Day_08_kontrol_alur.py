# Hari 8: Alur Kontrol & List Comprehension (Filtering Data UI)
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

daftar_modul: list[dict] = [
    {"hari": 1, "topik": "Instalasi Python 3.13", "kategori": "Setup", "selesai": True},
    {"hari": 2, "topik": "Setup VS Code & Ruff", "kategori": "Setup", "selesai": True},
    {"hari": 3, "topik": "Git Lokal & Identitas", "kategori": "Git", "selesai": True},
    {"hari": 4, "topik": "GitHub & .gitignore", "kategori": "Git", "selesai": True},
    {"hari": 5, "topik": "Virtual Environment", "kategori": "Setup", "selesai": True},
    {"hari": 6, "topik": "Tipe Data Primitif", "kategori": "Dasar", "selesai": True},
    {"hari": 7, "topik": "Koleksi List & Dict", "kategori": "Dasar", "selesai": True},
    {"hari": 8, "topik": "Alur Kontrol", "kategori": "Dasar", "selesai": False},
    {"hari": 9, "topik": "Fungsi", "kategori": "Dasar", "selesai": False},
]

filter_status: str = "PENDING"
kata_kunci: str = ""

modul_terfilter = [
    modul
    for modul in daftar_modul
    if (
        (filter_status == "SEMUA")
        or (filter_status == "SELESAI" and modul["selesai"])
        or (filter_status == "PENDING" and not modul["selesai"])
    )
    and (kata_kunci.lower() in modul["topik"].lower())
]

console.print(
    Panel(
        f"[bold cyan]Filter Aktif:[/bold cyan] {filter_status} | "
        f"[bold cyan]Pencarian:[/bold cyan] '{kata_kunci if kata_kunci else 'Semua'}'\n"
        f"[dim]Total Ditemukan: {len(modul_terfilter)} item[/dim]",
        title="[bold yellow]Panel Kontrol UI[/bold yellow]",
        border_style="yellow",
    )
)

tabel = Table(title="[bold green]Hasil Filter Komponen[/bold green]")
tabel.add_column("Hari", justify="center", style="yellow")
tabel.add_column("Kategori", style="cyan")
tabel.add_column("Topik", style="white")
tabel.add_column("Status", justify="center")

for item in modul_terfilter:
    status_label = (
        "[bold green]SELESAI[/bold green]"
        if item["selesai"]
        else "[bold red]BELUM[/bold red]"
    )
    tabel.add_row(f"H-{item['hari']}", item["kategori"], item["topik"], status_label)

console.print(tabel)
