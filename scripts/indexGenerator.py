import os
import json
import unicodedata

PASTA = "public/biografias_json"
ARQUIVO_INDEX = os.path.join(PASTA, "index.json")

def normalizar_nome(nome):
    nome = nome.lower()
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode()
    return nome

dados_index = []

for nome_arquivo in os.listdir(PASTA):
    if not nome_arquivo.endswith(".json") or nome_arquivo == "index.json":
        continue

    slug = os.path.splitext(nome_arquivo)[0]

    try:
        with open(os.path.join(PASTA, nome_arquivo), "r", encoding="utf-8") as f:
            dados = json.load(f)

        nome_completo = dados.get("nome_completo", slug)
        nome_norm = normalizar_nome(nome_completo)

        dados_index.append({
            "slug": slug,
            "nome_completo": nome_completo,
            "nome_normalizado": nome_norm
        })

    except Exception as e:
        print(f"Erro ao processar {nome_arquivo}: {e}")

# Ordena pelo nome normalizado para manter consistência
dados_index.sort(key=lambda x: x["nome_normalizado"])

with open(ARQUIVO_INDEX, "w", encoding="utf-8") as f:
    json.dump(dados_index, f, ensure_ascii=False, indent=2)

print(f"index.json gerado com {len(dados_index)} nomes.")
