import os
import json
import secrets
import time
from datetime import datetime
from eth_account import Account
from rich.console import Console
from rich.live import Live
from rich.progress import Progress
from rich.table import Table
from dotenv import load_dotenv
from loguru import logger
from utils import check_eth_balance

# Load konfigurasi dari .env
load_dotenv()
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", 1000))
LOG_DIR = "logs"
FOUND_FILE = os.path.join(LOG_DIR, "found_wallets.json")

# Setup folder log
os.makedirs(LOG_DIR, exist_ok=True)
logger.add(os.path.join(LOG_DIR, "scanner.log"), rotation="1 MB")
console = Console()

# Jika file JSON belum ada, buat file kosong
if not os.path.exists(FOUND_FILE):
    with open(FOUND_FILE, "w") as f:
        f.write("")

# Membuat tampilan dashboard
def create_dashboard(attempts, found, last_address, last_balance):
    table = Table(title="Ethereum Wallet Scanner", show_lines=True)
    table.add_column("🔁 Attempts", justify="center")
    table.add_column("🎯 Found", justify="center")
    table.add_column("📫 Last Address", overflow="fold")
    table.add_column("💰 Balance (ETH)", justify="right")
    table.add_row(str(attempts), str(found), last_address, f"{last_balance:.8f}")
    return table

# Fungsi utama
def main():
    attempts = 0
    found_count = 0
    last_address = "-"
    last_balance = 0.0

    progress = Progress(
        "[progress.percentage]{task.percentage:>3.0f}%",
        "•",
        "[cyan]{task.completed}/{task.total} wallets scanned",
        transient=True,
    )
    task = progress.add_task("Scanning wallets...", total=MAX_ATTEMPTS)

    def render():
        layout = Table.grid()
        layout.add_row(create_dashboard(attempts, found_count, last_address, last_balance))
        layout.add_row(progress.get_renderable())
        return layout

    console.print("[bold green]🚀 Memulai pemindaian dompet Ethereum...[/bold green]")

    with Live(render(), refresh_per_second=2, console=console) as live:
        while attempts < MAX_ATTEMPTS:
            priv_key = "0x" + secrets.token_hex(32)
            acct = Account.from_key(priv_key)
            address = acct.address
            balance = check_eth_balance(address)

            attempts += 1
            last_address = address
            last_balance = balance

            progress.update(task, advance=1)
            live.update(render())

            if balance > 0:
                found_count += 1
                logger.success(f"[FOUND] {address} | {balance:.8f} ETH")

                wallet_data = {
                    "timestamp": datetime.now().isoformat(),
                    "address": address,
                    "private_key": priv_key,
                    "balance_eth": balance
                }

                # Simpan dalam format JSONL (1 baris = 1 data JSON)
                with open(FOUND_FILE, "a") as f:
                    f.write(json.dumps(wallet_data) + "\n")

            time.sleep(1.2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]❌ Dihentikan oleh pengguna.[/red]")
