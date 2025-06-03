import json
import requests
from pathlib import Path
from time import sleep
from urllib.parse import urlencode
from tqdm import tqdm

# Caminhos relativos ao script
ROOT = Path(__file__).resolve().parent
BIO_DIR = ROOT / "biografias_json"
DATA_DIR = ROOT / "public" / "data"
CACHE_FILE = DATA_DIR / "cache_coords_.json"
OUTPUT_FILE = DATA_DIR / "biografias_coords.json"

# Nominatim
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {
    "User-Agent": "dimension/1.0 (dimensiondimensao@gmail.com)"
}

# Tamanho de cada lote
BATCH_SIZE = 50

# Garante que o diretório de saída existe
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Carrega cache se existir
if CACHE_FILE.exists():
    with open(CACHE_FILE, encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

def geocode(endereco: str):
    """
    Retorna dict { 'lat': <float>, 'lon': <float> } ou None se não encontrado.
    Usa cache para não repetir consultas.
    """
    if not endereco:
        return None

    if endereco in cache:
        return cache[endereco]

    params = {
        "q": endereco,
        "format": "json",
        "limit": 1
    }
    url = f"{NOMINATIM_URL}?{urlencode(params)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        resultados = resp.json()
        if resultados:
            lat = float(resultados[0]["lat"])
            lon = float(resultados[0]["lon"])
            coords = {"lat": lat, "lon": lon}
        else:
            coords = None
    except Exception as e:
        print(f"[Erro de rede ou parsing] ao geocodificar '{endereco}': {e}")
        coords = None

    cache[endereco] = coords
    return coords

def main():
    arquivos = list(BIO_DIR.glob("*.json"))
    if not arquivos:
        print(f"⚠️ Nenhum arquivo JSON encontrado em {BIO_DIR}")
        return

    dados_unificados = []
    total_files = len(arquivos)

    # Itera em batches de 50 arquivos
    for batch_start in range(0, total_files, BATCH_SIZE):
        batch = arquivos[batch_start : batch_start + BATCH_SIZE]
        batch_index = batch_start // BATCH_SIZE + 1
        num_batches = (total_files + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"\nIniciando processamento do lote {batch_index}/{num_batches} "
              f"({len(batch)} arquivos)...")

        for arquivo in tqdm(batch, desc=f"Batch {batch_index}/{num_batches}"):
            try:
                with open(arquivo, encoding="utf-8") as f:
                    entry = json.load(f)
            except Exception as e:
                print(f"[{arquivo.name}] ERRO ao ler/parsear JSON: {e}")
                continue

            # Extrai campo 'lugar_nascimento', tratando None
            lugar_raw = entry.get("lugar_nascimento")
            if lugar_raw is None:
                lugar = ""
            else:
                lugar = str(lugar_raw).strip()

            try:
                coords = geocode(lugar)
            except Exception as e:
                print(f"[{arquivo.name}] ERRO inesperado no geocode: {e}")
                coords = None

            entry["coords_nascimento"] = coords
            dados_unificados.append(entry)

        # Após cada lote, salva cache e JSON parcial
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f_cache:
                json.dump(cache, f_cache, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Erro ao salvar cache após batch {batch_index}] {e}")

        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
                json.dump(dados_unificados, f_out, ensure_ascii=False, indent=2)
            print(f"Lote {batch_index} concluído e salvo parcialmente em {OUTPUT_FILE}")
        except Exception as e:
            print(f"[Erro ao salvar JSON parcial após batch {batch_index}] {e}")

    print("\nTodos os lotes processados. Arquivo final disponível em:")
    print(f"  {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
