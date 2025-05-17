
import csv, json, pathlib, random, re, time
from urllib.parse import urljoin
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE       = "https://mathshistory.st-andrews.ac.uk"
INDEX_URL  = f"{BASE}/Biographies/chronological/"
OUT_DIR    = pathlib.Path("data")
OUT_DIR.mkdir(exist_ok=True)

USER_AGENTS = [
    
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
})

def scrape_biographies_raw_soup() -> BeautifulSoup:
    """Fetch the chronological index and return a parsed soup object."""
    resp = SESSION.get(INDEX_URL, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")
def extract_bio_urls(soup: BeautifulSoup) -> list[str]:
    """
    Devolve todos os URLs absolutos das biografias,
    sem duplicatas e na ordem em que aparecem.
    """
    urls, seen = [], set()

    for a in soup.select("li a[href]"):        # qualquer link dentro de <li>
        href = a["href"]
        if href.startswith("#") or href.startswith("http"):
            continue
        # os links das biografias começam com "../" ou, muito raramente, "./"
        if not href.startswith(("../", "./")):
            continue

        full = urljoin(INDEX_URL, href)        # INDEX_URL = …/Biographies/chronological/
        if full not in seen:
            urls.append(full)
            seen.add(full)

    return urls
def save_urls(urls: list[str],
              folder: str = "data",
              filename: str = "bios_urls.txt") -> pathlib.Path:
    """
    Cria a pasta <folder>/ se não existir, depois grava cada string de
    `urls` em <folder>/<filename>, uma por linha.
    Devolve o caminho completo para eventuais conferências.
    """
    out_dir = pathlib.Path(folder)
    out_dir.mkdir(parents=True, exist_ok=True)      

    out_path = out_dir / filename

    out_path.write_text("\n".join(urls), encoding="utf-8")
    return out_path



if __name__ == '__main__':
    soup = scrape_biographies_raw_soup()
    bio_urls = extract_bio_urls(soup)

    txt_path = save_urls(bio_urls)      
    print(f"{len(bio_urls)} links gravados em {txt_path}")
