from pathlib import Path
import os, json, re, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ---------------------------------------------------------------------------
# Configurações gerais
# ---------------------------------------------------------------------------
BASE_URL = "https://mathshistory.st-andrews.ac.uk/"
ARQ_URLS = Path("data") / "bios_urls.txt"     # lista de URLs (uma por linha)
DIR_SAIDA = Path("dados")                     # JSONs gerados aqui
DIR_SAIDA.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Funções utilitárias
# ---------------------------------------------------------------------------
def clean(html: str) -> str:
    """Remove tags, <br>, múltiplos espaços e linhas vazias."""
    html = re.sub(r"<br\s*/?>", "\n", html)
    texto = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+\n", "\n", texto).strip()

def abs_href(a_tag) -> str:
    """Converte href relativo em absoluto."""
    return urljoin(BASE_URL, a_tag["href"])

# ---------------------------------------------------------------------------
# Scraper de uma biografia
# ---------------------------------------------------------------------------
def scrape_bio(url: str) -> dict:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # ---------- quick info --------------------------------------------------
    info = {}
    quick = soup.find("h3", string=re.compile(r"quick info", re.I))
    if quick:
        for dt in quick.find_all_next("dt"):
            dd = dt.find_next_sibling("dd")
            if not dd:
                break
            chave = dt.text.strip(":").lower()
            info[chave] = clean(dd.decode_contents())
            if dt.find_next("hr"):
                break

    # ---------- dados básicos ----------------------------------------------
    dados = {
        "source": url,
        "name": soup.h1.text.strip() if soup.h1 else None,
        "born": info.get("born"),
        "died": info.get("died"),
        "summary": info.get("summary"),
    }

    # ---------- biografia (parágrafos) -------------------------------------
    bio_h3 = soup.find("h3", string=re.compile(r"Biography", re.I))
    if bio_h3:
        paras = []
        for sib in bio_h3.find_next_siblings():
            if sib.name == "h3":                # acabou a seção
                break
            if sib.name in {"span", "p", "div"}:
                txt = clean(sib.decode_contents())
                if txt:
                    paras.append(txt)
        if paras:
            dados["biography"] = "\n\n".join(paras)

    # ---------- última atualização -----------------------------------------
    last_upd = soup.find(string=re.compile(r"Last Update", re.I))
    if last_upd:
        dados["last_updated"] = last_upd.split("Last Update")[-1].strip()

    # ---------- links “Additional Resources” -------------------------------
    add_h3 = soup.find("h3", string=re.compile(r"Additional Resources", re.I))
    if add_h3:
        links = []
        ol = add_h3.find_next("ol")
        if ol:
            for a in ol.select("a[href]"):
                links.append({"text": a.get_text(strip=True),
                              "url": abs_href(a)})
        if links:
            dados["additional_resources"] = links

    # ---------- referências (apenas as 5 primeiras) ------------------------
    ref_h3 = soup.find("h3", string=re.compile(r"References", re.I))
    if ref_h3:
        refs = []
        ol = ref_h3.find_next("ol")
        if ol:
            for li in ol.find_all("li", limit=5):
                refs.append(clean(li.decode_contents()))
        if refs:
            dados["references_excerpt"] = refs

    return dados

# ---------------------------------------------------------------------------
# Loop principal: lê lista de URLs, processa cada uma e salva JSON
# ---------------------------------------------------------------------------
with ARQ_URLS.open(encoding="utf-8") as f:
    urls = [u.strip() for u in f if u.strip()]

for url in urls:
    try:
        registro = scrape_bio(url)
        # cria nome de arquivo limpo a partir do nome da pessoa
        nome_arquivo = re.sub(r"\W+", "_", registro["name"].lower()) + ".json"
        arq_out = DIR_SAIDA / nome_arquivo
        with arq_out.open("w", encoding="utf-8") as fp:
            json.dump(registro, fp, ensure_ascii=False, indent=2)
        print(f"✅  Salvo: {arq_out}")
    except Exception as e:
        print(f"❌  Erro em {url}: {e}")
