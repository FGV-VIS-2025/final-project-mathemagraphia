import os
import json
import pandas as pd
import numpy as np
folder_path = "classified_llm"

registros = []

if os.path.exists(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, encoding="utf-8") as f:
                    conteudo = json.load(f)
                    nome = conteudo.get("nome", filename.replace(".json", ""))
                    area_principal = conteudo.get("area_principal", "")
                    subareas = conteudo.get("subareas", [])
                    if subareas:
                        for sub in subareas:
                            subarea = sub.get("subarea", "")
                            especificas = ", ".join(sub.get("subareas_especificas", []))
                            registros.append({
                                "nome": nome,
                                "area_principal": area_principal,
                                "subarea": subarea,
                                "subareas_especificas": especificas
                            })
                    else:
                        registros.append({
                            "nome": nome,
                            "area_principal": area_principal,
                            "subarea": "",
                            "subareas_especificas": ""
                        })
            except Exception as e:
                registros.append({
                    "nome": filename.replace(".json", ""),
                    "area_principal": np.nan,
                    "subarea": "",
                    "subareas_especificas": str(e)
                })

    df_final = pd.DataFrame(registros)
    full_csv_path = "public/data/mathematicians_classified.csv"
    df_exploded = df_final.assign(
    specific_subareas=df_final["specific_subareas"].str.split(", ")
    ).explode("specific_subareas").reset_index(drop=True)

    df_exploded.to_csv(full_csv_path, index=False)
    result_path = full_csv_path
else:
    result_path = "Erro: Pasta 'classified_llm' não encontrada no ambiente."

result_path
