import os
import json

OUTPUT_DIR = "public/biografias_com_areas"

vazios = 0
total = 0

for filename in os.listdir(OUTPUT_DIR):
    if not filename.endswith(".json"):
        continue

    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total += 1
    if not data.get("math_areas"):
        vazios += 1

print(f"Total de arquivos analisados: {total}")
print(f"Arquivos com 'math_areas' vazio: {vazios}")
print(f"Com área(s) detectada(s): {total - vazios}")