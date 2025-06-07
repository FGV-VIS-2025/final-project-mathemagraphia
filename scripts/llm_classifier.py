import json
import google.generativeai as genai
from dotenv import load_dotenv
import os
from time import sleep


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)


with open(os.path.join("scripts", "application.json"), encoding="utf-8") as f:
    tools = json.load(f)


model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=tools,
    generation_config={
        "temperature": 0.2
    }
)


def classify_area_and_subareas(bio_text, nome, citados):
    prompt = f"""
Você é um dos especialistas mais respeitados do mundo em história da matemática, Professor PhD na melhor universidade da Europa.

Com base na biografia a seguir, classifique a **área principal da matemática**, suas **subáreas** e **subáreas específicas** associadas ao trabalho do matemático.

Leve em consideração também os matemáticos citados na biografia, pois eles podem indicar o campo de estudo.

 Importante: **"Matemática" NÃO é uma área válida**. Seja específico. Exemplos válidos incluem: "Álgebra", "Análise", "Geometria", "Teoria dos Números", "Topologia","Probabilidade e Estatística", etc.

Exemplo esperado:
Área principal: Álgebra  
Subáreas:  
- subarea: Álgebra Linear  
  subareas_especificas: [Teoria de Módulos, Espaços Vetoriais]  
- subarea: Teoria de Grupos  
  subareas_especificas: [Grupos Finitos, Representações de Grupos]

Você é uma referência no assunto. Não alucine e não invente informações falsas. Se o texto não fornecer nenhuma informação, retorne -1.

O texto está na língua inglesa, todavia, retorne a sua classificação em **português** somente.

Nome do matemático: {nome}

Matemáticos citados: {', '.join(citados) if citados else 'nenhum'}

Biografia:
\"\"\"
{bio_text}
\"\"\"
    """
    while True:
        try:
            response = model.generate_content(prompt)
            parts = response.candidates[0].content.parts

            if not parts or not hasattr(parts[0], "function_call"):
                return {
                    "nome": nome,
                    "erro": "Resposta sem function_call (tool não ativada ou resposta em texto livre)"
                }

            call = parts[0].function_call
            if not call or not call.args:
                return {
                    "nome": nome,
                    "erro": "function_call sem argumentos retornados"
                }

            subareas_raw = call.args.get("subareas")
            if not isinstance(subareas_raw, list):
                return {
                    "nome": nome,
                    "erro": "subareas não retornadas corretamente"
                }

            subareas = [
                {
                    "subarea": str(sub["subarea"]),
                    "subareas_especificas": list(sub["subareas_especificas"])
                }
                for sub in subareas_raw
            ]

            return {
                "nome": nome,
                "area_principal": str(call.args["area_principal"]),
                "subareas": subareas
            }

        except Exception as e:
            if "429" in str(e):
                print(f"[429] Quota excedida para {nome}. Aguardando 10 segundos...")
                sleep(10)
            else:
                print(f"[ERRO] Falha ao classificar {nome}: {e}")
                return {
                    "nome": nome,
                    "erro": str(e)
                }
def main():
    pasta_entrada = os.path.join("public", "MacTutorData")
    pasta_saida = os.path.join("classified_llm")
    os.makedirs(pasta_saida, exist_ok=True)

    for filename in os.listdir(pasta_entrada):
        if filename.endswith(".json"):
            caminho = os.path.join(pasta_entrada, filename)
            try:
                with open(caminho, encoding="utf-8") as f:
                    bio = json.load(f)

                nome = bio.get("nome_completo", "Desconhecido")
                texto_biografia = bio.get("biografia", "")
                citados = bio.get("matematicos_citados_na_biografia", [])

                resultado = classify_area_and_subareas(texto_biografia, nome, citados)

                caminho_saida = os.path.join(pasta_saida, filename)
                with open(caminho_saida, "w", encoding="utf-8") as f_out:
                    json.dump(resultado, f_out, indent=2, ensure_ascii=False)

                print(f"Classificado: {filename}")

            except Exception as e:
                print(f"[ERRO] Falha ao processar {filename}: {e}")

if __name__ == "__main__":
    main()
