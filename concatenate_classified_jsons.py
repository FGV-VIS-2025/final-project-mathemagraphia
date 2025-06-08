import os
import json
import pandas as pd
import numpy as np


folder_path = "classified_llm"
output_path = "public/data/mathematicians_classified.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

records = []

if os.path.exists(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)
                    name = data.get("nome", filename.replace(".json", ""))
                    main_area = data.get("area_principal", "")
                    subareas = data.get("subareas", [])
                    if subareas:
                        for sub in subareas:
                            subarea = sub.get("subarea", "")
                            specifics = sub.get("subareas_especificas", [])
                            for specific in specifics:
                                records.append({
                                    "nome": name,
                                    "area_principal": main_area,
                                    "subarea": subarea,
                                    "subareas_especificas": specific.strip()
                                })
                    else:
                        records.append({
                            "nome": name,
                            "area_principal": main_area,
                            "subarea": "",
                            "subareas_especificas": ""
                        })
            except Exception as e:
                records.append({
                    "nome": filename.replace(".json", ""),
                    "area_principal": np.nan,
                    "subarea": "",
                    "subareas_especificas": str(e)
                })

    
    df_final = pd.DataFrame(records)

    
    df_final.to_csv(output_path, index=False)
    result_path = output_path
else:
    result_path = "Erro: Pasta 'classified_llm' não encontrada no ambiente."

print(result_path)
