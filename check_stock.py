import requests
from bs4 import BeautifulSoup
import os
import hashlib

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
HASH_FILE = "/tmp/last_page_hash.txt"

def get_page_hash():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        resp = requests.get("https://www.graanul.lv", headers=headers, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        page_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        return page_hash, text
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None, None

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
    current_hash, page_text = get_page_hash()
    if current_hash is None:
        print("Could not fetch page.")
        return

    # Load previous hash
    try:
        with open(HASH_FILE, "r") as f:
            last_hash = f.read().strip()
    except FileNotFoundError:
        last_hash = None

    print(f"Last hash: {last_hash}")
    print(f"Current hash: {current_hash}")

    if last_hash is None:
        # First run - save hash and send current status
        with open(HASH_FILE, "w") as f:
            f.write(current_hash)
        print("First run - hash saved.")
        # Also check if in stock right now
        out_of_stock_keywords = ["pagaidam", "nevaram pienemt", "pasutijumus nevaram"]
        text_lower = page_text.lower()
        is_out_of_stock = any(kw in text_lower for kw in out_of_stock_keywords)
        if not is_out_of_stock:
            send_telegram(
                "\U0001fab5 <b>GRAANUL.LV - GRANULAS PIEEJAMAS!</b>\n\n"
                "Granulas ir pieejamas!\n"
                "\U0001f449 https://www.graanul.lv"
            )
        else:
            print("Out of stock on first run.")
        return

    if current_hash != last_hash:
        print("PAGE CHANGED!")
        # Save new hash
        with open(HASH_FILE, "w") as f:
            f.write(current_hash)
        # Check if now in stock
        out_of_stock_keywords = ["pagaidam", "nevaram pienemt", "pasutijumus nevaram"]
        text_lower = page_text.lower()
        is_out_of_stock = any(kw in text_lower for kw in out_of_stock_keywords)
        if not is_out_of_stock:
            send_telegram(
                "\U0001fab5 <b>GRAANUL.LV - GRANULAS PIEEJAMAS!</b>\n\n"
                "Lapa ir mainijusies un granulas izskata pieejamas!\n"
                "\U0001f449 https://www.graanul.lv"
            )
        else:
            send_telegram(
                "\U00002139 <b>GRAANUL.LV - LAPA MAINIJUSIES</b>\n\n"
                "Lapa ir mainijusies, bet granulas vel nav pieejamas.\n"
                "Seko lidzi: https://www.graanul.lv"
            )
    else:
        print("No change detected.")

if __name__ == "__main__":
    main()
