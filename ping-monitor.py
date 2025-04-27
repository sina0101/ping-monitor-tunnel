import subprocess
import threading
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import box
#اینجا آیپی هارو وارد کن
IPS = ["10.0.0.1" , "10.0.0.2" , ........]

ip_stats = {
    ip: {
        "loss": 0,
        "last_ping": "-",
        "pings": []
    } for ip in IPS
}

console = Console()

def ping_ip(ip):
    while True:
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output = result.stdout
            now = time.time()

            if "0 received" in output or result.returncode != 0:
                ip_stats[ip]["loss"] = 100
                ip_stats[ip]["last_ping"] = "-"
                ip_stats[ip]["pings"].append((now, None))
            else:
                loss_line = [line for line in output.splitlines() if "packet loss" in line][0]
                loss = int(loss_line.split('%')[0].split(' ')[-1])

                rtt_line = [line for line in output.splitlines() if "rtt" in line or "round-trip" in line][0]
                min_, avg_, max_, _ = rtt_line.split('=')[1].split('/')

                last_ping = [float(line.split('time=')[1].split(' ')[0]) for line in output.splitlines() if "bytes from" in line]
                last_ping_value = last_ping[-1] if last_ping else None

                ip_stats[ip]["loss"] = loss
                ip_stats[ip]["last_ping"] = f"{last_ping_value:.1f}" if last_ping_value else "-"
                ip_stats[ip]["pings"].append((now, last_ping_value))

            one_hour_ago = now - 3600
            ip_stats[ip]["pings"] = [p for p in ip_stats[ip]["pings"] if p[0] >= one_hour_ago]

        except Exception as e:
            console.print(f"[red]Error pinging {ip}: {e}[/red]")

        time.sleep(1)

def create_table():
    table = Table(title="🌐 Ping Monitor (Last 1 Hour)", box=box.ROUNDED, expand=True)

    table.add_column("IP Address", justify="center", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Packet Loss", justify="center")
    table.add_column("Min 1h (ms)", justify="center")
    table.add_column("Max 1h (ms)", justify="center")
    table.add_column("Last Ping (ms)", justify="center")
    table.add_column("Last Pings (History)", justify="center")

    for ip, stats in ip_stats.items():
        loss = stats["loss"]
        last_ping = stats["last_ping"]
        pings = stats["pings"]

        recent_pings = [ping for timestamp, ping in pings if ping is not None]

        if recent_pings:
            min_recent = f"{min(recent_pings):.1f}"
            max_recent = f"{max(recent_pings):.1f}"
        else:
            min_recent = "-"
            max_recent = "-"

        if loss == 100:
            status = "[bold red]🔴 DOWN[/bold red]"
        elif loss > 20 or (last_ping != "-" and float(last_ping) > 150):
            status = "[bold yellow]🟡 Slow[/bold yellow]"
        else:
            status = "[bold green]🟢 OK[/bold green]"

        graph = ""
        for _, ping in pings[-20:]:
            if ping is None:
                graph += " "
            elif ping < 50:
                graph += "▂"
            elif ping < 100:
                graph += "▄"
            elif ping < 200:
                graph += "▆"
            else:
                graph += "█"

        table.add_row(
            ip,
            status,
            f"{loss}%",
            min_recent,
            max_recent,
            last_ping,
            graph
        )

    table.caption = (
        "\n[bold]Legend:[/bold] "
        "[green]🟢 OK[/green]: Connection is healthy. "
        "[yellow]🟡 Slow[/yellow]: High latency or packet loss detected. "
        "[red]🔴 DOWN[/red]: Host is unreachable.\n"
        "[bold]Graph symbols:[/bold] "
        "▂ (<50ms), ▄ (50-100ms), ▆ (100-200ms), █ (>200ms).\n"
        "[bold]Info:[/bold] "
        "Min and Max values are calculated based on the last 1 hour of recorded pings.\n"
    )

    return table

if __name__ == "__main__":
    for ip in IPS:
        threading.Thread(target=ping_ip, args=(ip,), daemon=True).start()

    with Live(create_table(), refresh_per_second=1, screen=True) as live:
        while True:
            live.update(create_table())
            time.sleep(1)
