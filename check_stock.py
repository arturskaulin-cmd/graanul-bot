import requests
from bs4 import BeautifulSoup
import os

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Frāzes kas norāda ka granulas NAV pieejamas
OUT_OF_STOCK_PHRASES = [
        "pagaidām jaunus pasūtījumus nevaram pieņemt",
        "pašlaik jaunus pasūtījumus nevaram pieņemt",
        "pasūtījumus nevaram pieņemt",
        "nav pieejamas",
        "nav noliktavā",
        "out of stock",
        "temporarily unavailable",
]

def check_stock():
        headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
                    resp = requests.get("https://www.graanul.lv", headers=headers, timeout=20)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, "html.parser")
                    text = soup.get_text().lower()
                    for phrase in OUT_OF_STOCK_PHRASES:
                                    if phrase.lower() in text:
                                                        print(f"Found out-of-stock phrase: '{phrase}'")
                                                        return False  # Nav pieejamas
        return True  # Pieejamas!
except requests.RequestException as e:
        print(f"Request error: {e}")
        return None  # Kļūda - nezinām statusu

def send_telegram(message):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        try:
                    r = requests.post(url, json=payload, timeout=10)
                    r.raise_for_status()
                    print("Telegram notification sent!")
except Exception as e:
        print(f"Telegram error: {e}")

def main():
        in_stock = check_stock()
        print(f"In stock: {in_stock}")
        if in_stock is True:
                    send_telegram(
                                    "\U0001fab5 <b>GRAANUL.LV — GRANULAS PIEEJAMAS!</b>\n\n"
                                    "Granulas ir atkal pārdošanā! Steidzies pasūtīt:\n"
                                    "\U0001f449 https://www.graanul.lv"
                    )
elif in_stock is False:
        print("Still out of stock.")
else:
        print("Could not determine stock status (request error).")

if __name__ == "__main__":
        main()
