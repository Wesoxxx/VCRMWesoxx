\
import os, re, time, random
from typing import List, Dict
from bs4 import BeautifulSoup
from supabase import create_client
from playwright.sync_api import sync_playwright

PROFILE_URL = os.environ.get("PROFILE_URL","").strip()
MAX_PAGES = int(os.environ.get("MAX_PAGES","3"))
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def pause(a=0.6, b=1.2):
    time.sleep(random.uniform(a, b))

def scrape_public_profile(profile_url: str, max_pages: int = 3) -> List[Dict]:
    items = []
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(profile_url, wait_until="domcontentloaded")
        pause()

        # try to open closet tab
        try:
            page.click('a[href*="closet"]', timeout=2000)
            pause()
        except Exception:
            pass

        for _ in range(max_pages):
            page.mouse.wheel(0, 3000)
            pause(0.8, 1.8)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "lxml")
    seen = set()
    results = []
    for a in soup.select('a[href*="/items/"]'):
        href = a.get("href","")
        if not href or not re.search(r"/items/\d+", href):
            continue
        card = a
        for _ in range(4):
            if card and card.find("img"):
                break
            if card:
                card = card.parent
        title = a.get_text(" ", strip=True) or "Article Vinted"
        txt = (card or a).get_text(" ", strip=True) if card else a.get_text(" ", strip=True)
        m_price = re.search(r"(\d+[.,]?\d*)\s*€", txt)
        price = float(m_price.group(1).replace(",", ".")) if m_price else None
        size = None
        m_size = re.search(r"\b(Taille\s*)?([A-Z0-9./-]{1,6})\b", txt)
        if m_size:
            size = m_size.group(2)
        img = None
        if card:
            imgtag = card.find("img")
            if imgtag and imgtag.get("src"):
                img = imgtag["src"]

        url = "https://www.vinted.fr" + href if href.startswith("/") else href
        if url in seen:
            continue
        seen.add(url)

        results.append({
            "title": title,
            "brand": None,
            "size": size,
            "price_eur": price,
            "image_url": img,
            "item_url": url,
            "status": "en_stock",
            "cost_eur": None,
            "margin_eur": None,
            "sku": None,
            "notes": None
        })
    return results

def upsert_supabase(rows: List[Dict]):
    client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    batch = 500
    for i in range(0, len(rows), batch):
        chunk = rows[i:i+batch]
        client.table("items").upsert(chunk, on_conflict="item_url").execute()
        print("Upserted", len(chunk), "rows.")

def main():
    if not PROFILE_URL:
        raise SystemExit("Missing PROFILE_URL env var (Vinted public profile URL).")
    rows = scrape_public_profile(PROFILE_URL, MAX_PAGES)
    if not rows:
        print("No items found.")
    else:
        upsert_supabase(rows)
        print(f"Done. Found {len(rows)} items.")

if __name__ == "__main__":
    main()
