import json
import google.generativeai as genai
from dotenv import load_dotenv
import os

with open(os.path.join("scripts", "application.json"), encoding="utf-8") as f:
    tools = json.load(f)

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    #usei o 1.5 flash, no futuro da pra ver outros modelos comof fica
    model_name="gemini-1.5-flash",
    tools=tools
)

def classify_area_and_subareas(bio_text, nome):
    prompt = f"""
Você é um dos especialistas mais respeitados do mundo em história da matemática, Professor PhD na melhor universidade da Europa.

Com base na biografia a seguir, classifique a área principal da matemática, suas subáreas e sub-áreas específicas associadas ao trabalho do matemático.

Você é uma referência no assunto. Não alucine e não invente informações falsas. Se o texto não fornecer nenhuma informação, retorne -1.

Retorne exclusivamente chamando a função `classificar_area_hierarquica`.

Biografia de {nome}:
\"\"\"
{bio_text}
\"\"\"
"""
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
