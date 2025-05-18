import csv
import json
import time
import os
import requests
from bs4 import BeautifulSoup
from slugify import slugify
from tqdm import tqdm

# Pasta de saída
OUTPUT_DIR = "biografias_json"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extrair_dados_biografia(html, nome_curto, ano_nasc, ano_morte, url):
    soup = BeautifulSoup(html, 'lxml') # Usar o parser 'lxml' ( Mais eficiente)

    # 1. Nome completo
    h1_tags = soup.find_all('h1') 
    nome_completo = h1_tags[1].text.strip() if len(h1_tags) > 1 else nome_curto # Vi que os nomes estão em geral no segundo <h1> da página

    # 2. Locais
    lugar_nascimento = None
    lugar_morte = None
    quick_info = soup.find('h3', string='Quick Info') # Existe sempre um bloco Quick Info que  dá informações de Born e Died
    if quick_info:
        quick_section = quick_info.find_parent('div')
        dts = quick_section.find_all('dt')
        for dt in dts:
            if 'Born' in dt.text:
                dd = dt.find_next_sibling('dd')
                if dd:
                    link = dd.find('a')
                    lugar_nascimento = link.text.strip() if link else None
            if 'Died' in dt.text:
                dd = dt.find_next_sibling('dd')
                if dd:
                    partes = dd.get_text(separator='|', strip=True).split('|')
                    if len(partes) > 1:
                        lugar_morte = partes[1].strip()


    # 3. Biografia
    biografia = None
    bio_header = soup.find('h3', string='Biography') # As biogradias se encontram em uma <div> que contém o <h3>Biography<h3>
    if bio_header:
        bio_div = bio_header.find_parent('div') # Aqui pego o pai do <h3>
        bio_span = bio_div.find('span', class_='markup') # Busco o texto de biografia que está no elemento span
        if bio_span:
            biografia = bio_span.get_text(separator='\n', strip=True)

    return {
        "nome_completo": nome_completo,
        "nome_curto": nome_curto,
        "ano_nascimento": ano_nasc,
        "ano_morte": ano_morte,
        "link": url,
        "lugar_nascimento": lugar_nascimento,
        "lugar_morte": lugar_morte,
        "biografia": biografia
    }

# Leitura do CSV
csv_path = "public/matematicos.csv"
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = list(csv.DictReader(csvfile))

    for row in tqdm(reader, desc="Processando biografias", unit="biografia"):
        nome = row['Name']
        link = row['Link']

        try:
            response = requests.get(link)
            response.raise_for_status()

            dados = extrair_dados_biografia(
                html=response.text,
                nome_curto=nome,
                ano_nasc=row['Born'],
                ano_morte=row['Die'],
                url=link
            )

            nome_arquivo = slugify(nome) + ".json"
            caminho = os.path.join(OUTPUT_DIR, nome_arquivo)

            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"\n⚠️ Erro ao processar {nome}: {e}")

        import random
        time.sleep(random.uniform(0.6, 0.8)) 

