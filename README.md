# MathemaGraphia 

Contribuição dos Membros:

*Henrique Borges*, Colaborou em: Mapa Principal, Grafo de Postulados de Euclides, Scraping, Grafo de relacionamento entre matemáticos.

*Antonio Brych*, Colaborou em:  Função de Weierstrass, Mandelbrot Set, Pêndulo Duplo, sistema de lançamentos de moedas, escrita do relatório (LaTeX) e confecção de poster.

*Gerardo Mikael*: Colaborou em: Scraping, Front-End, acabamento do projeto, confeccção do Poster, revisão do relatório (LaTeX), Página de Curvas (Renascimento), edição de vídeos para apresentação.

### Favor ler nosso paper em 'viz.pdf'




**Objetivo**: Facilitar e aumentar a acessibilidade da matemática através de visualizações 

Dados de referencia: https://mathshistory.st-andrews.ac.uk/

Material de estudo recomendado:
* [Linha do Tempo Interativa da Matemática](https://museualterdata.com.br/linha-do-tempo/)
* [Linha do Tempo da História do Cálculo – Lights Crystal](https://museualterdata.com.br/linha-do-tempo/)
* [História do Cálculo Diferencial – Quarto 707](https://www.quarto707.com.br/diario-de-estudos/historia-do-calculo-diferencial/)
* [Quem inventou o cálculo diferencial e integral](https://www.youtube.com/watch?v=2lYTt5vjMfg&t=108s)
* [A guerra do cálculo - Jason Socrates Bardi](https://g.co/kgs/RVVVQb8)

### Veja o vídeo com os features da visualização
* [Apresentação da visualização](https://youtu.be/ZyIX5cwXGBs)
* [Teaser da visualização](https://youtu.be/SAWYmIhrNfY)

## Informações gerais

#### 1.2 Extração dos dados
Os dados foram extraidos do site https://mathshistory.st-andrews.ac.uk/ através de Web Scraping pelas files `scripts/mactutor_scraper.py` e `scripts/biography_scraper.py` sendo o primeiro gerando um `.csv` com os matemáticos e seus respectivos links para as biografias, e o segundo utiliza do primeiro para gerar `.json` de cada matemático contendo campos como local e data de nascimento e falecimento juntamente a biografia 
