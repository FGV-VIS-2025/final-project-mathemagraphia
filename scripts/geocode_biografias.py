import json
import requests
from pathlib import Path
from time import sleep
from tqdm import tqdm

# Caminhos relativos ao script
ROOT = Path(__file__).resolve().parent.parent
BIO_DIR = ROOT / "biografias_json"
DATA_DIR = ROOT / "data"
OUTPUT = DATA_DIR / "biografias_com_coords.json"
CACHE_FILE = DATA_DIR / "cache_coords.json"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {
    "User-Agent": "dimension/1.0 (dimensiondimensao@gmail.com)"
}

# Garante que a pasta data/ existe
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Carrega cache se existir
if CACHE_FILE.exists():
    with open(CACHE_FILE, encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

def geocode(local):
    if not local:
        return None
    if local in cache:
        return cache[local]

    params = {"q": local, "format": "json", "limit": 1}

    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS)
        data = resp.json()
        if data:
            coord = {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
            cache[local] = coord
            return coord
    except Exception as e:
        print(f"Erro ao geocodificar '{local}': {e}")

    return None

def dividir_em_batches(lista, tamanho):
    """Divide a lista em sublistas de tamanho especificado."""
    for i in range(0, len(lista), tamanho):
        yield lista[i:i + tamanho]

def processar_biografias(batch_size=500):
    saida = []

    # Carrega progresso anterior, se houver
    if OUTPUT.exists():
        with open(OUTPUT, encoding="utf-8") as f:
            saida = json.load(f)

    # Coleta nomes já processados para evitar repetir
    nomes_processados = {d["nome_completo"] for d in saida}
    arquivos = [arq for arq in sorted(BIO_DIR.glob("*.json")) if arq.stem not in nomes_processados]

    print(f"🔍 Total a processar: {len(arquivos)} biografias restantes")

    for lote in dividir_em_batches(arquivos, batch_size):
        for arq in tqdm(lote, desc=f"Batch ({len(lote)})"):
            with open(arq, encoding="utf-8") as f:
                dados = json.load(f)

            nome = dados.get("nome_completo", "")
            if nome in nomes_processados:
                continue  # já processado

            nasc = dados.get("lugar_nascimento", "")
            morte = dados.get("lugar_morte", "")

            loc_nasc = geocode(nasc)
            
            loc_morte = geocode(morte)
            
            registro = {
                "nome_completo": nome,
                "ano_nascimento": dados.get("ano_nascimento"),
                "ano_morte": dados.get("ano_morte"),
                "link": dados.get("link")
            }

            if loc_nasc:
                registro["lat_nasc"] = loc_nasc["lat"]
                registro["lon_nasc"] = loc_nasc["lon"]

            if loc_morte:
                registro["lat_morte"] = loc_morte["lat"]
                registro["lon_morte"] = loc_morte["lon"]

            if "lat_nasc" in registro or "lat_morte" in registro:
                saida.append(registro)
                nomes_processados.add(nome)

        # Salva após cada batch
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(saida, f, indent=2, ensure_ascii=False)

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)

        print(f"✅ Batch salvo. Total acumulado: {len(saida)} biografias\n")
        sleep(2)  # opcional entre batches

    print(f"🎉 Finalizado. Total: {len(saida)} biografias geocodificadas.")

if __name__ == "__main__":
    processar_biografias()

# 2040