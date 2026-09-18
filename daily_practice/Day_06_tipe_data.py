# Hari 6: Tipe Data Primitif & Rich Panel
from rich.console import Console
from rich.panel import Panel

console = Console()

# 1. Deklarasi Variabel & Tipe Data
nama_aplikasi: str = "Sistem Monitoring Proyek"
versi_rilis: float = 1.0
total_tugas: int = 12
tugas_selesai: int = 9
status_aktif: bool = True

# 2. Operasi Aritmatika Sederhana
persentase_progres: float = (tugas_selesai / total_tugas) * 100

# 3. Format Output Teks (f-string)
ringkasan_info = (
    f"[bold cyan]Aplikasi:[/bold cyan] {nama_aplikasi}\n"
    f"[bold yellow]Versi:[/bold yellow] {versi_rilis}\n"
    f"[bold green]Status Aktif:[/bold green] {status_aktif}\n"
    f"[bold magenta]Progres Tugas:[/bold magenta] {tugas_selesai}/{total_tugas} ({persentase_progres:.1f}%)"
)

# 4. Tampilkan dalam Komponen Panel Visual
console.print(
    Panel(
        ringkasan_info,
        title="[bold white]Ringkasan Data Komponen[/bold white]",
        border_style="bright_blue",
    )
)
