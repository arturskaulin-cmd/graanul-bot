import requests
from bs4 import BeautifulSoup
import os

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

OUT_OF_STOCK_TEXT = "TESTS_NEEKSISTEJOSS_TEKSTS_XYZ999"

def check_stock():
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get("https://www.graanul.lv", headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text()
    return OUT_OF_STOCK_TEXT not in text  # True = IN STOCK

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, json=payload, timeout=10)

def main():
    in_stock = check_stock()
    print(f"In stock: {in_stock}")
    if in_stock:
        send_telegram(
            "U0001fab5 <b>GRAANUL.LV — GRANULAS PIEEJAMAS!</b>\n\n"
            "Granulas ir atkal pārdošanā! Steidzies pasūtīt:\n"
            "U0001f449 https://www.graanul.lv"
        )
        print("Telegram notification sent!")
    else:
        print("Still out of stock.")

if __name__ == "__main__":
    main()
