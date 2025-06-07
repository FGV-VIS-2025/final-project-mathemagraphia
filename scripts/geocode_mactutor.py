import json
import requests
from pathlib import Path
from time import sleep, time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import math
import unicodedata
import re

# ----------------------------------------------------------------------
# CONFIGURAÇÃO GERAL
# ----------------------------------------------------------------------
ROOT         = Path(__file__).resolve().parent.parent
MAC_DIR      = ROOT / "public" / "MacTutorData"
DATA_DIR     = ROOT / "public" / "data"
OUTPUT       = DATA_DIR / "mac_tutor_com_coords.json"
CACHE_FILE   = DATA_DIR / "cache_coords.json"
LOG_FALHAS   = DATA_DIR / "macutor_geocode_falhas.log"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS       = {"User-Agent": "dimension/1.0 (dimensiondimensao@gmail.com)"}

# Após medir o tempo médio de geocodificação (HTTP + parsing),
# ajuste 'media_tempos' (em segundos). Exemplo: 1.8
media_tempos = 1.8
MAX_WORKERS  = math.ceil(media_tempos / 1.0)  # → 2 threads para 1.8s médio

# Salvar saída + cache a cada N registros novos
SAVE_INTERVAL = 50

# Locks para proteger uso de cache e rate limiter
cache_lock   = threading.Lock()
request_lock = threading.Lock()

# Timestamp da última requisição ao Nominatim
last_request_time = 0.0

# Garante existência da pasta de dados
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
# CARREGA CACHE SE EXISTIR
# ----------------------------------------------------------------------
if CACHE_FILE.exists():
    with open(CACHE_FILE, encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

# ----------------------------------------------------------------------
# NORMALIZAÇÃO DE STRINGS (remove acentos, lower-case, trim)
# ----------------------------------------------------------------------
def normalizar_string(s: str) -> str:
    s = s.strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.lower()

# ----------------------------------------------------------------------
# PREPROCESSAMENTO PARA CASOS “(now ...)”
# ----------------------------------------------------------------------
def preprocess_local(local: str) -> str:
    """
    Ajusta strings que contenham "(now ...)".
    Exemplo:
      "Barcelona (now Spain)" -> "barcelona, spain"
      "Lódz, Russian Empire (now Poland)" -> "lodz, poland"
      "Waldenburg, Germany (now Wałbrzych, Poland)" -> "wałbrzych, poland"
    Se não houver "(now ...)", retorna string normalizada.
    """
    if not local:
        return ""
    s = normalizar_string(local)
    m = re.search(r'\(now\s*([^)]+)\)', s)
    if m:
        conteudo = m.group(1).strip()  # ex: "spain", "poland", "wałbrzych, poland"
        if "," in conteudo:
            return conteudo  # já no formato "cidade, país"
        partes = [p.strip() for p in s.split(",") if p.strip()]
        if partes:
            cidade = partes[0]  # ex: "lodz"
            return f"{cidade}, {conteudo}"
    return s

# ----------------------------------------------------------------------
# GEOCODIFICAÇÃO COM RATE LIMIT (1 requisição/segundo no público)
# ----------------------------------------------------------------------
def geocode_limitado(local: str, session: requests.Session) -> dict | None:
    global last_request_time

    if not local:
        return None

    with cache_lock:
        if local in cache:
            return cache[local]

    with request_lock:
        agora = time()
        delta = agora - last_request_time
        if delta < 0.5:
            sleep(0.5 - delta)

        try:
            resp = session.get(
                NOMINATIM_URL,
                params={"q": local, "format": "json", "limit": 1},
                headers=HEADERS,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            if data:
                coord = {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
                with cache_lock:
                    cache[local] = coord
                last_request_time = time()
                return coord
        except Exception as e:
            print(f"⚠️ Erro ao geocodificar '{local}': {e}")
            last_request_time = time()
            return None

    return None

# ----------------------------------------------------------------------
# GEOCODIFICAÇÃO COM “FALLBACKS” (várias tentativas)
# ----------------------------------------------------------------------
def geocode_com_fallbacks(local_bruto: str, session: requests.Session) -> dict | None:
    if not local_bruto:
        return None

    s0 = local_bruto  # já passou por preprocess_local antes
    # 1) Tentativa direta
    coord = geocode_limitado(s0, session)
    if coord:
        return coord

    # 2) Se tiver vírgula, tenta apenas últimos 2 pedaços
    if "," in s0:
        partes = [p.strip() for p in s0.split(",") if p.strip()]
        if len(partes) >= 2:
            tent2 = f"{partes[-2]}, {partes[-1]}"
            coord = geocode_limitado(tent2, session)
            if coord:
                return coord

    # 3) Tenta só o último componente após vírgula
    if "," in s0:
        partes = [p.strip() for p in s0.split(",") if p.strip()]
        tent3 = partes[-1]
        if tent3:
            coord = geocode_limitado(tent3, session)
            if coord:
                return coord

    # 4) Tenta só o token final (palavra depois de espaço ou hífen)
    tokens = re.split(r"[\s\-]+", s0)
    if tokens:
        tent4 = tokens[-1]
        if tent4:
            coord = geocode_limitado(tent4, session)
            if coord:
                return coord

    return None

# ----------------------------------------------------------------------
# REGISTRA FALHAS EM LOG PARA REVISÃO MANUAL
# ----------------------------------------------------------------------
def anotar_falha(nome: str, local: str):
    with open(LOG_FALHAS, "a", encoding="utf-8") as f:
        f.write(f"{nome}  |  \"{local}\"\n")

# ----------------------------------------------------------------------
# PROCESSA UM ÚNICO ARQUIVO DE MAC TUTOR DATA
# ----------------------------------------------------------------------
def processar_arquivo(arq_path: Path, nomes_processados: set, session: requests.Session):
    try:
        dados = json.loads(arq_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"⚠️ Falha ao ler '{arq_path.name}': {e}")
        return None

    nome = dados.get("nome_completo") or ""
    if (not nome) or (nome in nomes_processados):
        return None

    raw_nasc  = dados.get("local_nascimento") or ""
    raw_morte = dados.get("local_morte") or ""

    # 1) Preprocessa para remover "(now ...)"
    local_nasc  = preprocess_local(raw_nasc)
    local_morte = preprocess_local(raw_morte)

    # 2) Geocodifica com fallbacks
    coord_nasc  = geocode_com_fallbacks(local_nasc, session)
    if coord_nasc is None and local_nasc:
        anotar_falha(nome, local_nasc)

    coord_morte = geocode_com_fallbacks(local_morte, session)
    if coord_morte is None and local_morte:
        anotar_falha(nome, local_morte)

    # 3) Se encontrarmos ao menos uma coordenada, monta registro
    if (coord_nasc is not None) or (coord_morte is not None):
        registro = {
            "nome_completo":   nome,
            "nome_curto":      dados.get("nome_curto", ""),
            "link":            dados.get("link", ""),
            "data_nascimento": dados.get("data_nascimento", ""),
            "data_morte":      dados.get("data_morte", ""),
        }
        if coord_nasc:
            registro["lat_nasc"] = coord_nasc["lat"]
            registro["lon_nasc"] = coord_nasc["lon"]
        if coord_morte:
            registro["lat_morte"] = coord_morte["lat"]
            registro["lon_morte"] = coord_morte["lon"]
        return registro

    return None

# ----------------------------------------------------------------------
# LOOP PRINCIPAL: THREADS + SALVAMENTO A CADA 50 NOVOS REGISTROS
# ----------------------------------------------------------------------
def processar_mactutor_threaded_com_fallbacks():
    # 1) Carrega saída parcial, se existir
    if OUTPUT.exists():
        with open(OUTPUT, encoding="utf-8") as f:
            saida = json.load(f)
    else:
        saida = []

    nomes_processados = { e["nome_completo"] for e in saida }
    todos_arquivos    = sorted(MAC_DIR.glob("*.json"))
    total_arquivos    = len(todos_arquivos)
    print(f"🔍 Total: {total_arquivos} arquivos em MacTutorData")
    print(f"✅ Já processados: {len(nomes_processados)}")

    session = requests.Session()
    novos_contados = 0  # contagem desde o último save

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futuros = {
            executor.submit(processar_arquivo, arq, nomes_processados, session): arq
            for arq in todos_arquivos
        }

        with tqdm(total=total_arquivos, unit="arquivo") as pbar:
            for futuro in as_completed(futuros):
                arq = futuros[futuro]
                try:
                    registro = futuro.result()
                except Exception as e:
                    print(f"⚠️ Erro ao processar '{arq.name}': {e}")
                    pbar.update(1)
                    continue

                if registro:
                    saida.append(registro)
                    nomes_processados.add(registro["nome_completo"])
                    novos_contados += 1

                pbar.update(1)

                # 2) Quando atingir SAVE_INTERVAL, salva saída + cache
                if novos_contados >= SAVE_INTERVAL:
                    with open(OUTPUT, "w", encoding="utf-8") as f_out:
                        json.dump(saida, f_out, indent=2, ensure_ascii=False)
                    with cache_lock:
                        with open(CACHE_FILE, "w", encoding="utf-8") as f_cache:
                            json.dump(cache, f_cache, indent=2, ensure_ascii=False)
                    print(f"\n✅ Salvou {novos_contados} novos registros. Total agora: {len(saida)}")
                    novos_contados = 0

    # 3) Se restarem registros não salvos, grava novamente
    if novos_contados > 0:
        with open(OUTPUT, "w", encoding="utf-8") as f_out:
            json.dump(saida, f_out, indent=2, ensure_ascii=False)
        with cache_lock:
            with open(CACHE_FILE, "w", encoding="utf-8") as f_cache:
                json.dump(cache, f_cache, indent=2, ensure_ascii=False)
        print(f"\n✅ Salvou os últimos {novos_contados} registros restantes.")

    print(f"\n🎉 Concluído! Total de biografias geocodificadas: {len(saida)}.")

# ----------------------------------------------------------------------
# EXECUTA
# ----------------------------------------------------------------------
if __name__ == "__main__":
    processar_mactutor_threaded_com_fallbacks()
