import os
import json
from slugify import slugify

# Pasta de entrada e saída
INPUT_DIR = "biografias_json"
OUTPUT_DIR = "biografias_com_areas"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mapeamento de palavras-chave para áreas matemáticas
MAPEAMENTO = {
    "álgebra": "Álgebra",
    "geometria": "Geometria",
    "diferencial": "Geometria",
    "cálculo": "Cálculo",
    "limite": "Cálculo",
    "derivada": "Cálculo",
    "integração": "Cálculo",
    "estatística": "Estatística",
    "probabilidade": "Estatística",
    "análise": "Análise",
    "funções": "Análise",
    "teoria dos números": "Teoria dos Números",
    "números primos": "Teoria dos Números",
    "topologia": "Topologia",
    "conjuntos abertos": "Topologia",
    "lógica": "Lógica",
    "prova": "Lógica",
    "combinatória": "Combinatória",
    "contagem": "Combinatória",
    "matemática aplicada": "Matemática Aplicada",
    "física": "Matemática Aplicada",
    "modelagem": "Matemática Aplicada",
}

def identificar_areas(biografia, mapeamento):
    if not biografia:
        return []
    biografia = biografia.lower()
    areas = set()
    for palavra, area in mapeamento.items():
        if palavra in biografia:
            areas.add(area)
    return list(areas)

# Processar cada JSON
for nome_arquivo in os.listdir(INPUT_DIR):
    if not nome_arquivo.endswith(".json"):
        continue

    caminho_entrada = os.path.join(INPUT_DIR, nome_arquivo)
    caminho_saida = os.path.join(OUTPUT_DIR, nome_arquivo)

    with open(caminho_entrada, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    biografia = dados.get("biografia", "")
    areas = identificar_areas(biografia, MAPEAMENTO)
    dados["areas_matematicas"] = areas

    with open(caminho_saida, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

print(f"✅ Processamento concluído. Resultados salvos em: {OUTPUT_DIR}")