import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
with open(os.path.join("scripts", "application.json"), encoding="utf-8") as f:
    tools = json.load(f)

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    #usei o 1.5 flash, no futuro da pra ver outros modelos comof fica
    model_name="gemini-1.5-pro",
    tools=tools
)

def classify_area_and_subareas(bio_text, nome):
    prompt = f"""..."""  # seu prompt

    while True:
        try:
            response = model.generate_content(prompt)
            call = response.candidates[0].content.parts[0].function_call
            subareas = [
                {
                    "subarea": str(sub["subarea"]),
                    "subareas_especificas": list(sub["subareas_especificas"])
                }
                for sub in call.args["subareas"]
            ]
            return {
                "nome": nome,
                "area_principal": str(call.args["area_principal"]),
                "subareas": subareas
            }
        except Exception as e:
            if "429" in str(e):
                print(f"[429] Quota excedida para {nome}. Aguardando 30 segundos...")
                time.sleep(30)
            else:
                raise e

def main():
    with open(os.path.join("public", "data", "bios.json"), encoding="utf-8") as f:
        biografias = json.load(f)

    resultados = []

    for bio in biografias[:4]:
        nome = bio["nome_completo"]
        texto_biografia = bio["biografia"]
        try:
            resultado = classify_area_and_subareas(texto_biografia, nome)
            resultados.append(resultado)
            print(f"\n=== {nome} ===")
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Erro ao classificar {nome}: {e}")

    with open("resultados_classificados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
