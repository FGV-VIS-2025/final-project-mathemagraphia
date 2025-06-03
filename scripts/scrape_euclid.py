import requests
from bs4 import BeautifulSoup
import re
import json

urls = [
    "https://web.archive.org/web/20200217213511/http://www.mat.uc.pt/~jaimecs/euclid/1parte.html",
    "https://web.archive.org/web/20200202225227/http://www.mat.uc.pt/~jaimecs/euclid/2parte.html",
    "https://web.archive.org/web/20181107060410/http://www.mat.uc.pt/~jaimecs/euclid/3parte.html",
    "https://web.archive.org/web/20200202225600/http://www.mat.uc.pt/~jaimecs/euclid/4parte.html",
    "https://web.archive.org/web/20200202225445/http://www.mat.uc.pt/~jaimecs/euclid/5parte.html",
    "https://web.archive.org/web/20200202225519/http://www.mat.uc.pt/~jaimecs/euclid/6parte.html"
]

def extrair_proposicoes(url):
    res = requests.get(url)
    res.encoding = 'iso-8859-1'
    soup = BeautifulSoup(res.text, 'html.parser')

    proposicoes = []
    blocos = soup.find_all('p')

    prop_atual = None
    for p in blocos:
        texto = p.get_text(strip=True)
        if re.match(r"^PROP\. [IVXLCDM]+\.", texto):
            if prop_atual:
                proposicoes.append(prop_atual)
            prop_atual = {"titulo": texto, "conteudo": ""}
        elif prop_atual:
            prop_atual["conteudo"] += texto + "\n"

    if prop_atual:
        proposicoes.append(prop_atual)

    return proposicoes

todos = []
for url in urls:
    todos.extend(extrair_proposicoes(url))

with open("euclides_livro1.json", "w", encoding="utf-8") as f:
    json.dump(todos, f, ensure_ascii=False, indent=2)
