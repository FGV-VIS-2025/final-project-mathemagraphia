import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
from time import sleep
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Configura log
logging.basicConfig(
    filename="classificador_erros.log",
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Carrega chave da API e configura
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Carrega tools
with open(os.path.join("scripts", "application.json"), encoding="utf-8") as f:
    tools = json.load(f)

# Instancia o modelo
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=tools,
    generation_config={"temperature": 0.2}
)

write_lock = Lock()

def classify_area_and_subareas(bio_text, nome, citados, max_retries=5):
    prompt = f"""
Você é um dos especialistas mais respeitados do mundo em história da matemática, Professor PhD na melhor universidade da Europa.

Com base na biografia a seguir, classifique a **área principal da matemática**, suas **subáreas** e **subáreas específicas** associadas ao trabalho do matemático.

Leve em consideração também os matemáticos citados na biografia, pois eles podem indicar o campo de estudo.

Importante: **"Matemática" NÃO é uma área válida**. Seja específico. Exemplos válidos incluem: "Álgebra", "Análise", "Geometria", "Teoria dos Números", "Topologia", "Probabilidade e Estatística", etc.

Exemplo esperado:
Área principal: Álgebra  
Subáreas:  
- subarea: Álgebra Linear  
  subareas_especificas: [Teoria de Módulos, Espaços Vetoriais]  
- subarea: Teoria de Grupos  
  subareas_especificas: [Grupos Finitos, Representações de Grupos]

Se não houver informação suficiente, retorne a área_principal como -1.

Nome do matemático: {nome}

Palavras Chave (Podem ser úteis para você): {', '.join(citados) if citados else 'nenhum'}

Biografia:
\"\"\"
{bio_text}
\"\"\"
    """
    for attempt in range(1, max_retries + 1):
        try:
            sleep(1.5)  # Evita ultrapassar o rate limit
            response = model.generate_content(prompt, safety_settings={})
            parts = response.candidates[0].content.parts

            if not parts or not hasattr(parts[0], "function_call"):
                return {"nome": nome, "erro": "Resposta sem function_call"}

            call = parts[0].function_call
            if not call or not call.args:
                return {"nome": nome, "erro": "function_call sem argumentos"}

            args = dict(call.args)
            subareas_raw = list(args.get("subareas", []))
            subareas = []

            for idx, sub in enumerate(subareas_raw):
                try:
                    sub_dict = dict(sub)
                    subarea_nome = str(sub_dict.get("subarea", ""))
                    subespec = list(sub_dict.get("subareas_especificas", []))
                    subareas.append({
                        "subarea": subarea_nome,
                        "subareas_especificas": subespec
                    })
                except Exception as e:
                    subareas.append({
                        "subarea": f"[ERRO no item {idx}]: {e}",
                        "subareas_especificas": []
                    })

            return {
                "nome": nome,
                "area_principal": str(args.get("area_principal", "")),
                "subareas": subareas
            }

        except Exception as e:
            msg = str(e)
            if "429" in msg:
                wait_time = 10 * attempt
                print(f"[429] Quota excedida para {nome}. Tentativa {attempt}/{max_retries}. Aguardando {wait_time}s...")
                sleep(wait_time)
            else:
                logging.warning(f"Erro ao classificar {nome}: {e}")
                return {"nome": nome, "erro": msg}

    return {"nome": nome, "erro": "Máximo de tentativas excedido"}

def process_file(filename, pasta_entrada, pasta_saida):
    if not filename.endswith(".json"):
        return

    caminho_saida = os.path.join(pasta_saida, filename)
    if os.path.exists(caminho_saida):
        print(f"{filename} já classificado. Pulando.")
        return

    try:
        with open(os.path.join(pasta_entrada, filename), encoding="utf-8") as f:
            bio = json.load(f)

        nome = bio.get("nome_completo", "Desconhecido")
        texto_biografia = bio.get("biografia", "")
        citados = bio.get("matematicos_citados_na_biografia", [])

        resultado = classify_area_and_subareas(texto_biografia, nome, citados)

        with write_lock:
            with open(caminho_saida, "w", encoding="utf-8") as f_out:
                json.dump(resultado, f_out, indent=2, ensure_ascii=False)

        print(f"Classificado com sucesso: {filename}")

    except Exception as e:
        logging.error(f"Erro ao processar {filename}: {e}")

def main():
    pasta_entrada = os.path.join("public", "MacTutorData")
    pasta_saida = os.path.join("classified_llm")
    os.makedirs(pasta_saida, exist_ok=True)

    arquivos = [f for f in os.listdir(pasta_entrada) if f.endswith(".json")]

    max_threads = 5
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [
            executor.submit(process_file, filename, pasta_entrada, pasta_saida)
            for filename in arquivos
        ]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Erro em thread: {e}")

if __name__ == "__main__":
    main()
