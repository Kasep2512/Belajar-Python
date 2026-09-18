# Day 10: Pemodelan State dengan Class
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class ModulState:
    def __init__(self) -> None:
        self.daftar_modul: list[dict] = [
            {"hari": 1, "topik": "Instalasi Python 3.13", "kategori": "Setup", "selesai": True},
            {"hari": 2, "topik": "Setup VS Code & Ruff", "kategori": "Setup", "selesai": True},
            {"hari": 3, "topik": "Git Lokal & Identitas", "kategori": "Git", "selesai": True},
            {"hari": 4, "topik": "GitHub & .gitignore", "kategori": "Git", "selesai": True},
            {"hari": 5, "topik": "Virtual Environment", "kategori": "Setup", "selesai": True},
            {"hari": 6, "topik": "Tipe Data Primitif", "kategori": "Dasar", "selesai": True},
            {"hari": 7, "topik": "Koleksi List & Dict", "kategori": "Dasar", "selesai": True},
            {"hari": 8, "topik": "Alur Kontrol & Filtering", "kategori": "Dasar", "selesai": True},
            {"hari": 9, "topik": "Fungsi Modular State", "kategori": "Dasar", "selesai": True},
            {"hari": 10, "topik": "Pemodelan State Class", "kategori": "OOP", "selesai": False},
        ]
        self.filter_aktif: str = "SEMUA"

    def ubah_filter(self, filter_baru: str) -> None:
        self.filter_aktif = filter_baru

    def tandai_selesai(self, nomor_hari: int) -> None:
        for item in self.daftar_modul:
            if item["hari"] == nomor_hari:
                item["selesai"] = True
                break

    def ambil_data_terfilter(self) -> list[dict]:
        return [
            item
            for item in self.daftar_modul
            if (
                self.filter_aktif == "SEMUA"
                or (self.filter_aktif == "SELESAI" and item["selesai"])
                or (self.filter_aktif == "PENDING" and not item["selesai"])
            )
        ]


def render_tampilan(state: ModulState) -> None:
    data = state.ambil_data_terfilter()

    console.print(
        Panel(
            f"[bold cyan]Filter Aktif:[/bold cyan] {state.filter_aktif} | "
            f"[bold cyan]Total Ditemukan:[/bold cyan] {len(data)}",
            title="[bold yellow]State Controller UI[/bold yellow]",
            border_style="yellow",
        )
    )

    tabel = Table(title="[bold green]Dashboard Belajar Python[/bold green]")
    tabel.add_column("Hari", justify="center", style="yellow")
    tabel.add_column("Kategori", style="cyan")
    tabel.add_column("Topik Materi", style="white")
    tabel.add_column("Status", justify="center")

    for item in data:
        status = "[bold green]SELESAI[/bold green]" if item["selesai"] else "[bold red]BELUM[/bold red]"
        tabel.add_row(f"H-{item['hari']}", item["kategori"], item["topik"], status)

    console.print(tabel)


if __name__ == "__main__":
    app_state = ModulState()

    app_state.tandai_selesai(10)
    app_state.ubah_filter("SELESAI")

    render_tampilan(app_state)
