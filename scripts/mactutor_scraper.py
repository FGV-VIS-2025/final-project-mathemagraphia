import requests
from bs4 import BeautifulSoup
import csv
import re
from urllib.parse import urljoin
from pathlib import Path


def extrair_matematicos(base_url):
    print("Baixando página principal...")
    resp = requests.get(base_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.find_all("li")

    biografias = []

    for li in items:
        a = li.find("a")
        if not a:
            continue

        name = a.get_text(strip=True)
        href = a["href"]
        full_link = urljoin(base_url, href)

        texto = li.get_text(" ", strip=True)
        m = re.search(r"\(([^)]*?)\)", texto)
        if m:
            anos = m.group(1).split("-", 1)
            born = anos[0].strip()
            die = anos[1].strip() if len(anos) > 1 else ""
        else:
            born = ""
            die = ""

        biografias.append((name, born, die, full_link))

    return biografias


def salvar_csv(dados, path_csv):
    """Salva a lista de biografias em um arquivo CSV no caminho fornecido."""
    path_csv.parent.mkdir(parents=True, exist_ok=True)

    with open(path_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Born", "Die", "Link"])
        for linha in dados:
            writer.writerow(linha)

    print(f"Arquivo salvo em: {path_csv}")


def main():
    base_url = "https://mathshistory.st-andrews.ac.uk/Biographies/chronological/"
    destino = Path("public/matematicos.csv")

    biografias = extrair_matematicos(base_url)
    salvar_csv(biografias, destino)


if __name__ == "__main__":
    main()
