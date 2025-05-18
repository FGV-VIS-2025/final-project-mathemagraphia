# MathemaGraphia 
**Objetivo**: Facilitar e aumentar a acessibilidade da matemática através de visualizações 

Dados de referencia: https://mathshistory.st-andrews.ac.uk/

Material de estudo recomendado:
* [Linha do Tempo Interativa da Matemática](https://museualterdata.com.br/linha-do-tempo/)
* [Linha do Tempo da História do Cálculo – Lights Crystal](https://museualterdata.com.br/linha-do-tempo/)
* [História do Cálculo Diferencial – Quarto 707](https://www.quarto707.com.br/diario-de-estudos/historia-do-calculo-diferencial/)
* [Quem inventou o cálculo diferencial e integral](https://www.youtube.com/watch?v=2lYTt5vjMfg&t=108s)
* [A guerra do cálculo - Jason Socrates Bardi](https://g.co/kgs/RVVVQb8)

## Informações gerais

### Issues 
Busco realizar uma comunicação de "versões" através dos Issues, sendo o Issue https://github.com/FGV-VIS-2025/final-project-mathemagraphia/issues/1 destinado para as explicações das alterações e adições que são realizadas na Branch Main

Além disso, para as tarefas mais modulares incentivo o mesmo uso dos Issues com a tag de `CommitExplain`

### Relatório 0.0.1

* 1.1: GitHub Pages
* 1.2: Extração dos dados:

#### 1.1 GitHub Pages
Escolhemos um desing simples e acessível para a página, onde temos uma *Navegation Bar* no topo contendo conteiners para cada tipo de visualização. 
As visualizações serão especificadas nas seções ( A fazer ) 

#### 1.2 Extração dos dados
Os dados foram extraidos do site https://mathshistory.st-andrews.ac.uk/ através de Web Scraping pelas files `scripts/mactutor_scraper.py` e `scripts/biography_scraper.py` sendo o primeiro gerando um `.csv` com os matemáticos e seus respectivos links para as biografias, e o segundo utiliza do primeiro para gerar `.json` de cada matemático contendo campos como local e data de nascimento e falecimento juntamente a biografia 
