import os
import time
import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
API_KEY = os.getenv("ETHERSCAN_API_KEY")

def check_eth_balance(address: str) -> float:
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "1":
                return int(result["result"]) / 1e18
            elif "rate limit" in result.get("result", "").lower():
                logger.warning("Rate limit kena, tunggu 5 detik...")
                time.sleep(5)
        else:
            logger.error(f"HTTP error: {response.status_code}")
    except Exception as e:
        logger.error(f"Error saat cek saldo: {e}")
    return 0.0
