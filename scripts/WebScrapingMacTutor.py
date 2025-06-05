import csv
import json
import time
import os
import random
import requests
from bs4 import BeautifulSoup
from slugify import slugify
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------------------------------------------------------------
# CONFIGURAÇÕES
# -------------------------------------------------------------

CSV_PATH    = "public/matematicos.csv"
OUTPUT_DIR  = "biografias_json"
BASE_URL    = "https://mathshistory.st-andrews.ac.uk"
MAX_THREADS = 8         # número de threads simultâneas
DELAY_MIN   = 0.3       # delay mínimo após cada requisição (por thread)
DELAY_MAX   = 0.6       # delay máximo após cada requisição (por thread)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# Função de extração (igual ao que já temos)
# -------------------------------------------------------------

def extrair_dados_biografia(html, nome_curto, ano_nasc, ano_morte, url):
    soup = BeautifulSoup(html, 'lxml')

    # 1. Nome completo
    h1_tags = soup.find_all('h1')
    if len(h1_tags) > 1:
        nome_completo = h1_tags[1].get_text(strip=True)
    else:
        nome_completo = nome_curto

    # 2. Quick Info: datas/locais e summary
    data_nascimento = None
    local_nascimento = None
    data_morte = None
    local_morte = None
    summary = None

    quick_info = soup.find('h3', string='Quick Info')
    if quick_info:
        quick_div = quick_info.find_parent('div')
        for dt in quick_div.find_all('dt'):
            texto_dt = dt.get_text(strip=True)
            dd = dt.find_next_sibling('dd')
            if not dd:
                continue
            texto_dd = dd.get_text(separator='|', strip=True)

            if texto_dt == 'Born':
                partes = texto_dd.split('|', maxsplit=1)
                data_nascimento = partes[0].strip()
                if len(partes) > 1:
                    local_nascimento = partes[1].strip()

            elif texto_dt == 'Died':
                partes = texto_dd.split('|', maxsplit=1)
                data_morte = partes[0].strip()
                if len(partes) > 1:
                    local_morte = partes[1].strip()

            elif texto_dt == 'Summary':
                span_markup = dd.find('span', class_='markup')
                if span_markup:
                    summary = span_markup.get_text(separator=' ', strip=True)

    # 3. Biografia completa
    biografia = None
    bio_header = soup.find('h3', string='Biography')
    bio_div = None
    if bio_header:
        bio_div = bio_header.find_parent('div')
        bio_span = bio_div.find('span', class_='markup') if bio_div else None
        if bio_span:
            biografia = bio_span.get_text(separator='\n', strip=True)

    # 4. Matemáticos citados na biografia
    matematicos_citados = []
    if bio_div:
        for a in bio_div.find_all('a', href=True):
            texto = a.get_text(strip=True)
            href = a['href']
            if (href.startswith('../') or '/Biographies/' in href) and texto:
                if texto not in matematicos_citados:
                    matematicos_citados.append(texto)

    # 5. Imagens (miniatura + imagens dentro da biografia)
    imagens = []
    # 5.1) Miniatura de perfil
    thumb = soup.find('img', class_='biography-thumbnail')
    if thumb and thumb.get('src'):
        imagens.append(thumb['src'].strip())

    # 5.2) Todas as imagens dentro de bio_div
    if bio_div:
        for img in bio_div.find_all('img', src=True):
            src = img['src'].strip()
            if src not in imagens:
                imagens.append(src)

    return {
        "nome_completo": nome_completo,
        "nome_curto": nome_curto,
        "link": url,
        "data_nascimento": data_nascimento,
        "local_nascimento": local_nascimento,
        "data_morte": data_morte,
        "local_morte": local_morte,
        "summary": summary,
        "biografia": biografia,
        "matematicos_citados_na_biografia": matematicos_citados,
        "imagens": imagens
    }

# -------------------------------------------------------------
# Função que processa um matemático: download + parsing + salvar
# -------------------------------------------------------------

def processar_matematico(row, session):
    """
    row: dict vindo do CSV, com chaves 'Name', 'Link', 'Born', 'Die'
    session: requests.Session() compartilhada
    """
    nome = row['Name']
    link = row['Link']

    # Se for link relativo, prefixe
    if not link.startswith("http"):
        link = BASE_URL + link

    # Nome do arquivo de saída
    nome_arquivo = slugify(nome) + ".json"
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)

    # Se já existe, pular
    if os.path.exists(caminho):
        return (nome, "pulou")

    try:
        # Faz a requisição
        resp = session.get(link, timeout=15)
        resp.raise_for_status()

        dados = extrair_dados_biografia(
            html=resp.text,
            nome_curto=nome,
            ano_nasc=row.get('Born', None),
            ano_morte=row.get('Die', None),
            url=link
        )

        # Salvar JSON
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

        # Pequeno delay aleatório antes de finalizar a thread
        return (nome, "ok")

    except Exception as e:
        return (nome, f"erro: {e}")

# -------------------------------------------------------------
# Fluxo principal: carrega CSV, submete ao ThreadPoolExecutor
# -------------------------------------------------------------

def main():
    # 1) Ler todo o CSV
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile))

    # 2) Criar uma única Session (para reaproveitar conexões HTTP)
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})

    resultados = []

    # 3) Criar o pool de threads
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Mapeia cada row para uma future
        future_to_nome = {
            executor.submit(processar_matematico, row, session): row['Name']
            for row in reader
        }

        # 4) Conforme cada future é finalizada, atualiza o progresso e armazena o resultado
        for future in tqdm(as_completed(future_to_nome),
                           total=len(future_to_nome),
                           desc="Processando biografias",
                           unit="biografia"):
            nome = future_to_nome[future]
            try:
                status = future.result()
                resultados.append(status)  # (nome, "ok"/"pulou"/"erro: ...")
            except Exception as e:
                resultados.append((nome, f"erro inesperado: {e}"))

    # 5) Opcional: escrever em disco um log geral
    with open("log_resultados.txt", "w", encoding="utf-8") as logf:
        for nome, stat in resultados:
            logf.write(f"{nome}: {stat}\n")

if __name__ == "__main__":
    main()
