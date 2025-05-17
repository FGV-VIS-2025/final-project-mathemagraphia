
from pathlib import Path
from urllib.parse import urljoin
import json, re, requests, os
from bs4 import BeautifulSoup



BASE_URL   = "https://mathshistory.st-andrews.ac.uk/"
ARQ_URLS   = Path("data") / "bios_urls.txt"   
DIR_SAIDA  = Path("data")                    
DIR_SAIDA.mkdir(parents=True, exist_ok=True)




def limpa_html(html: str) -> str:
    html  = re.sub(r"<br\s*/?>", "\n", html)
    texto = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+\n", "\n", texto).strip()

def href_abs(a):          
    return urljoin(BASE_URL, a["href"])




def scrape_bio(url: str) -> dict:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    
    info = {}
    quick = soup.find("h3", string=re.compile(r"quick info", re.I))
    if quick:
        for dt in quick.find_all_next("dt"):
            dd = dt.find_next_sibling("dd")
            if not dd:
                break
            chave        = dt.text.strip(":").lower()
            info[chave]  = limpa_html(dd.decode_contents())
            if dt.find_next("hr"):
                break

    
    data = {
        "source" : url,
        "name"   : soup.h1.text.strip() if soup.h1 else None,
        "born"   : info.get("born"),
        "died"   : info.get("died"),
        "summary": info.get("summary"),
    }

    
    bio_h3 = soup.find("h3", string=re.compile(r"Biography", re.I))
    if bio_h3:
        paras = []
        for sib in bio_h3.find_next_siblings():
            if sib.name == "h3":
                break
            if sib.name in {"span", "p", "div"}:
                txt = limpa_html(sib.decode_contents())
                if txt:
                    paras.append(txt)
        if paras:
            data["biography"] = "\n\n".join(paras)

    
    upd = soup.find(string=re.compile(r"Last Update", re.I))
    if upd:
        data["last_updated"] = upd.split("Last Update")[-1].strip()

    
    add = soup.find("h3", string=re.compile(r"Additional Resources", re.I))
    if add and (ol := add.find_next("ol")):
        links = [{"text": a.get_text(strip=True), "url": href_abs(a)}
                 for a in ol.select("a[href]")]
        if links:
            data["additional_resources"] = links

    
    ref = soup.find("h3", string=re.compile(r"References", re.I))
    if ref and (ol := ref.find_next("ol")):
        refs = [limpa_html(li.decode_contents()) for li in ol.find_all("li", limit=5)]
        if refs:
            data["references_excerpt"] = refs

    return data




with ARQ_URLS.open(encoding="utf-8") as f:
    urls = [u.strip() for u in f if u.strip()]

for i, url in enumerate(urls, start=1):
    try:
        registro = scrape_bio(url)

        
        nome   = registro.get("name") or f"bio_{i}"
        slug   = re.sub(r"\W+", "_", nome.lower()).strip("_")
        arq    = DIR_SAIDA / f"{str.lower(url.split("/")[-2])}.json"

        
        with arq.open("w", encoding="utf-8") as fh:
            json.dump(registro, fh, ensure_ascii=False, indent=2)

        print(f"OK: Saved → {arq}")
    except Exception as e:
        print(f"NOK ERROR: {url}: {e}")
