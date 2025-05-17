
import csv, json, pathlib, random, re, time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE       = "https://mathshistory.st-andrews.ac.uk"
INDEX_URL  = f"{BASE}/Biographies/chronological/"
OUT_DIR    = pathlib.Path("data")
OUT_DIR.mkdir(exist_ok=True)

USER_AGENTS = [
    # alguns UA modernos para embaralhar
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]
