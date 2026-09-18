# Day 9: Fungsi & Modularitas State
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

MODULE_REGISTRY: list[dict] = [
    {"hari": 1, "topik": "Instalasi Python 3.13", "kategori": "Setup", "selesai": True},
    {"hari": 2, "topik": "Setup VS Code & Ruff", "kategori": "Setup", "selesai": True},
    {"hari": 3, "topik": "Git Lokal & Identitas", "kategori": "Git", "selesai": True},
    {"hari": 4, "topik": "GitHub & .gitignore", "kategori": "Git", "selesai": True},
    {"hari": 5, "topik": "Virtual Environment", "kategori": "Setup", "selesai": True},
    {"hari": 6, "topik": "Tipe Data Primitif", "kategori": "Dasar", "selesai": True},
    {"hari": 7, "topik": "Koleksi List & Dict", "kategori": "Dasar", "selesai": True},
    {"hari": 8, "topik": "Alur Kontrol", "kategori": "Dasar", "selesai": True},
    {"hari": 9, "topik": "Fungsi", "kategori": "Dasar", "selesai": False},
]


def filter_modules(
    modules: list[dict],
    status: str = "SEMUA",
    keyword: str = "",
) -> list[dict]:
    query = keyword.strip().lower()
    return [
        m
        for m in modules
        if (
            status == "SEMUA"
            or (status == "SELESAI" and m["selesai"])
            or (status == "PENDING" and not m["selesai"])
        )
        and (query in m["topik"].lower())
    ]


def render_dashboard(data_terfilter: list[dict], filter_aktif: str) -> None:
    console.print(
        Panel(
            f"[bold cyan]Filter Aktif:[/bold cyan] {filter_aktif} | "
            f"[bold cyan]Total Ditemukan:[/bold cyan] {len(data_terfilter)}",
            title="[bold yellow]Panel State Controller[/bold yellow]",
            border_style="yellow",
        )
    )

    tabel = Table(title="[bold green]Tampilan State Dinamis[/bold green]")
    tabel.add_column("Hari", justify="center", style="yellow")
    tabel.add_column("Kategori", style="cyan")
    tabel.add_column("Topik Materi", style="white")
    tabel.add_column("Status", justify="center")

    for item in data_terfilter:
        label_status = (
            "[bold green]SELESAI[/bold green]"
            if item["selesai"]
            else "[bold red]BELUM[/bold red]"
        )
        tabel.add_row(
            f"H-{item['hari']}", item["kategori"], item["topik"], label_status
        )

    console.print(tabel)


if __name__ == "__main__":
    filter_pilihan = "SEMUA"
    hasil_filter = filter_modules(MODULE_REGISTRY, status=filter_pilihan)
    render_dashboard(hasil_filter, filter_aktif=filter_pilihan)
