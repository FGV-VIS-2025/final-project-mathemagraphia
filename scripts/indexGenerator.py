import os
import json

# Caminho da pasta onde estão os arquivos .json
PASTA = "public/biografias_json"

# Lista de arquivos que terminam com .json, ignorando o index.json se já existir
nomes = [
    os.path.splitext(f)[0]
    for f in os.listdir(PASTA)
    if f.endswith(".json") and f != "index.json"
]

# Gera arquivo index.json
with open(os.path.join(PASTA, "index.json"), "w", encoding="utf-8") as f:
    json.dump(sorted(nomes), f, ensure_ascii=False, indent=2)

print(f"index.json gerado com {len(nomes)} nomes.")
