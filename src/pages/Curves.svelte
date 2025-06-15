<script>
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import { elasticOut } from 'svelte/easing';
  import * as d3 from 'd3';

  // Dados das curvas e curiosidades (ATUALIZADO)
  const curves = [
    {
      id: 1,
      name: "Senoide",
      formula: "y = a·sin(b·x + c)",
      params: [
        { name: "a", value: 1, min: 0.1, max: 3, step: 0.1, desc: "Amplitude" },
        { name: "b", value: 1, min: 0.1, max: 3, step: 0.1, desc: "Frequência" },
        { name: "c", value: 0, min: -3, max: 3, step: 0.1, desc: "Fase" }
      ],
      facts: [
        "Fundamental na acústica - descreve a vibração de cordas e ondas sonoras",
        "Essencial em engenharia elétrica para representar corrente alternada",
        "A forma senoidal aparece no movimento dos pêndulos e em sistemas massa-mola"
      ],
      description: "A curva senoidal é a representação gráfica da função seno, uma das funções trigonométricas mais importantes. Ela descreve fenômenos periódicos e oscilatórios, sendo fundamental na física, engenharia e processamento de sinais.",
      creators: [
        "Hiparco de Niceia (190-120 a.C.) - Pai da trigonometria",
        "Leonhard Euler (1707-1783) - Formalizou a relação com números complexos",
        "Joseph Fourier (1768-1830) - Demonstrou que qualquer função periódica pode ser representada por senoides"
      ]
    },
    {
      id: 2,
      name: "Parábola",
      formula: "y = a·x² + b·x + c",
      params: [
        { name: "a", value: 0.5, min: -2, max: 2, step: 0.1, desc: "Abertura" },
        { name: "b", value: 0, min: -3, max: 3, step: 0.1, desc: "Inclinação" },
        { name: "c", value: 0, min: -5, max: 5, step: 0.1, desc: "Deslocamento vertical" }
      ],
      facts: [
        "Trajetória de projéteis sob ação da gravidade (desprezando resistência do ar)",
        "Forma ideal para concentrar ondas eletromagnéticas em antenas parabólicas",
        "A propriedade focal é usada em faróis, telescópios e fornos solares"
      ],
      description: "Curva cônica definida como o lugar geométrico dos pontos equidistantes de um ponto fixo (foco) e uma reta fixa (diretriz). Suas propriedades ópticas e mecânicas a tornam essencial em diversas aplicações tecnológicas.",
      creators: [
        "Menaechmus (380-320 a.C.) - Primeiro a estudar as cônicas",
        "Apollonius de Perga (262-190 a.C.) - Sistematizou o estudo das cônicas",
        "Galileu Galilei (1564-1642) - Demonstrou que projéteis seguem trajetórias parabólicas"
      ]
    },
    {
      id: 3,
      name: "Espiral de Arquimedes",
      formula: "r = a + b·θ",
      params: [
        { name: "a", value: 0, min: 0, max: 2, step: 0.1, desc: "Raio inicial" },
        { name: "b", value: 0.1, min: 0, max: 0.5, step: 0.01, desc: "Taxa de expansão" }
      ],
      facts: [
        "Padrão encontrado em conchas de moluscos como o náutilo",
        "Usada em gramofones antigos para mover a agulha uniformemente",
        "Aplicações modernas incluem compressores scroll e bombas de vácuo"
      ],
      description: "Espiral que se expande linearmente com o ângulo, mantendo distância constante entre voltas consecutivas. Modela diversos fenômenos naturais e tem aplicações em engenharia mecânica.",
      creators: [
        "Arquimedes de Siracusa (287-212 a.C.) - Descreveu a espiral em seu trabalho 'Sobre as Espirais'",
        "Jacob Bernoulli (1654-1705) - Estudou espirais logarítmicas relacionadas"
      ]
    },
    {
      id: 4,
      name: "Catenária",
      formula: "y = a·cosh(x/a)",
      params: [
        { name: "a", value: 2, min: 0.5, max: 5, step: 0.1, desc: "Parâmetro de tensão" }
      ],
      facts: [
        "Forma assumida por uma corrente ou cabo suspenso por suas extremidades",
        "Arcos catenários são estruturalmente estáveis, usados em arquitetura",
        "O Gateway Arch em St. Louis é uma catenária invertida"
      ],
      description: "Curva formada por uma corrente flexível suspensa por seus extremos e sujeita apenas à gravidade. Difere da parábola e possui propriedades mecânicas únicas que a tornam ideal para pontes suspensas e arcos arquitetônicos.",
      creators: [
        "Galileu Galilei (1564-1642) - Primeiro a estudar o problema",
        "Christiaan Huygens (1629-1695) - Derivação matemática correta",
        "Robert Hooke (1635-1703) - Descobriu a relação com arcos invertidos"
      ]
    },
    {
      id: 5,
      name: "Lemniscata de Bernoulli",
      formula: "r² = a²·cos(2θ)",
      params: [
        { name: "a", value: 4, min: 1, max: 5, step: 0.1, desc: "Tamanho da curva" }
      ],
      facts: [
        "Tem a forma do símbolo do infinito (∞)",
        "Casos especiais aparecem no estudo de campos magnéticos",
        "Usada em óptica para descrever certas aberrações de lentes"
      ],
      description: "Curva em forma de oito ou símbolo de infinito, que representa o lugar geométrico dos pontos cujo produto das distâncias a dois focos fixos é constante. Nota: a fórmula polar é usada para a plotagem.",
      creators: [
        "Jacob Bernoulli (1654-1705) - Primeira descrição detalhada",
        "Giovanni Cassini (1625-1712) - Estudou curvas relacionadas (ovais de Cassini)"
      ]
    },
    {
      id: 6,
      name: "Cardioide",
      formula: "r = a(1 + cosθ)",
      params: [
        { name: "a", value: 2, min: 1, max: 4, step: 0.1, desc: "Tamanho da curva" }
      ],
      facts: [
        "Forma de um coração (daí o nome)",
        "Padrão de irradiação de certas antenas direcionais",
        "Aparece na caústica formada por luz refletida em uma xícara circular"
      ],
      description: "Curva epicicloide especial que se assemelha a um coração. Formada pelo traço de um ponto em um círculo que rola sem deslizar em torno de outro círculo de mesmo raio. Tem aplicações em acústica e óptica.",
      creators: [
        "Johannes Kepler (1571-1630) - Primeiras investigações",
        "Louis Carré (1663-1711) - Estudos detalhados da curva",
        "Philippe de La Hire (1640-1718) - Propriedades geométricas"
      ]
    },
    {
      id: 7,
      name: "Curva de Bézier (Quadrática)",
      formula: "B(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂",
      params: [
        { name: "P0x", value: -8, min: -10, max: 10, step: 0.5, desc: "P₀ X" },
        { name: "P0y", value: -4, min: -5, max: 5, step: 0.5, desc: "P₀ Y" },
        { name: "P1x", value: 0, min: -10, max: 10, step: 0.5, desc: "P₁ X (Controle)" },
        { name: "P1y", value: 4, min: -5, max: 5, step: 0.5, desc: "P₁ Y (Controle)" },
        { name: "P2x", value: 8, min: -10, max: 10, step: 0.5, desc: "P₂ X" },
        { name: "P2y", value: -3, min: -5, max: 5, step: 0.5, desc: "P₂ Y" }
      ],
      facts: [
        "Fundamental em design gráfico e animação por computador",
        "Usada para definir o contorno de fontes (letras)",
        "Permite controle preciso de curvas suaves com poucos pontos de controle",
        "Base para a maioria dos softwares de ilustração vetorial como Adobe Illustrator e Inkscape"
      ],
      description: "Curva paramétrica amplamente utilizada em computação gráfica. Definida por pontos de controle que ditam sua forma. Esta é uma Bézier quadrática, definida por um ponto inicial (P₀), um ponto final (P₂) e um ponto de controle (P₁).",
      creators: [
        "Pierre Bézier (1910-1999) - Engenheiro da Renault, popularizou seu uso para design automotivo",
        "Paul de Casteljau (1930-2022) - Desenvolveu um algoritmo similar na Citroën, de forma independente"
      ]
    },
    {
      id: 8,
      name: "Hipocicloide",
      formula: "x = (a-b)cosθ + b·cos((a-b)/b·θ)",
      params: [
        { name: "a", value: 5, min: 2, max: 10, step: 0.1, desc: "Raio Fixo (a)" },
        { name: "b", value: 2, min: 0.5, max: 5, step: 0.1, desc: "Raio Rolante (b)" }
      ],
      facts: [
        "Quando a razão a/b é um inteiro, a curva se fecha e tem 'a/b' pontas (cúspides).",
        "Se a/b = 4, forma-se uma Astroide. Se a/b = 3, uma Deltoide.",
        "Inspirou o design do brinquedo Espirógrafo (Spirograph).",
        "Usada em engenharia mecânica para criar engrenagens planetárias."
      ],
      description: "Curva traçada por um ponto fixo em um círculo (raio b) que rola por dentro de outro círculo fixo (raio a). Produz uma variedade de curvas em forma de estrela, dependendo da razão entre os raios.",
      creators: [
        "Albrecht Dürer (1471-1528) - Descreveu métodos para desenhar curvas semelhantes",
        "Ole Rømer (1644-1710) - Fez estudos aplicados em astronomia e engrenagens"
      ]
    }
  ];

  // --- NENHUMA MUDANÇA DAQUI ATÉ A FUNÇÃO updateChart ---
  
  let selectedCurve = curves[0];
  let params = {};
  let svg;
  let currentFact = 0;
  let isAnimating = false;
  let width = 600;
  let height = 400;
  let margin = { top: 20, right: 20, bottom: 40, left: 50 };

  $: {
    if (selectedCurve) {
      params = {};
      selectedCurve.params.forEach(p => {
        params[p.name] = p.value;
      });
      updateChart();
    }
  }

  $: if (selectedCurve) {
    updateChart();
  }

  onMount(() => {
    svg = d3.select('#graph-container')
      .append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet');
    
    updateChart();
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  });

  function handleResize() {
    const container = document.getElementById('graph-container');
    if (container) {
      width = container.clientWidth;
      height = container.clientHeight;
      updateChart();
    }
  }

  // --- FUNÇÃO updateChart TOTALMENTE ATUALIZADA ---
  
  function updateChart(animate = false) {
    if (!svg || !selectedCurve) return;
    
    svg.selectAll('*').remove();
    
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Escalas
    const xScale = d3.scaleLinear()
      .domain([-20, 20])
      .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
      .domain([-10, 10])
      .range([innerHeight, 0]);

    const xAxis = d3.axisBottom(xScale)
      .ticks(10)
      .tickSize(-innerHeight)  // cobre toda a altura
      .tickPadding(10);

    const yAxis = d3.axisLeft(yScale)
      .ticks(10)
      .tickSize(-innerWidth)   // cobre toda a largura
      .tickPadding(10);
    
    // Adiciona eixos no local exato de x=0 e y=0
    g.append('g')
      .attr('class', 'x axis')
      .attr('transform', `translate(0, ${yScale(0)})`) // Posiciona na altura certa para y=0
      .call(xAxis);
      
    g.append('g')
      .attr('class', 'y axis')
      .attr('transform', `translate(${xScale(0)}, 0)`) // Posiciona na largura certa para x=0
      .call(yAxis);

    // Esconde a linha principal escura da "borda" dos eixos
    g.selectAll('.axis .domain').style('stroke', 'none');

    // Deixa as linhas da grade (os ticks) com uma cor cinza bem clara
    g.selectAll('.axis .tick line').style('stroke', '#e9e9e9');

    // Deixa os números dos eixos com uma cor mais suave
    g.selectAll('.axis .tick text').style('fill', '#aaa');

    // Lógica de Geração de Pontos
    const lineGenerator = d3.line()
        .x(d => xScale(d[0]))
        .y(d => yScale(d[1]));

    let pathsData = [];
    
    switch (selectedCurve.id) {
        case 1: // Senoide
        case 2: // Parábola
        case 4: // Catenária
            {
                const points = [];
                for (let x = -20; x <= 20; x += 0.1) {
                    let y;
                    if (selectedCurve.id === 1) {
                        y = params.a * Math.sin(params.b * x + params.c);
                    } else if (selectedCurve.id === 2) {
                        y = params.a * x * x + params.b * x + params.c;
                    } else if (selectedCurve.id === 4) {
                        y = params.a * Math.cosh(x / params.a);
                    }
                    if (Math.abs(y) < 10) points.push([x, y]);
                }
                pathsData.push(points);
                break;
            }
        
        case 3: // Espiral de Arquimedes
        case 6: // Cardioide
            {
                const points = [];
                const maxTheta = selectedCurve.id === 6 ? 2 * Math.PI : 10 * Math.PI;
                for (let theta = 0; theta <= maxTheta; theta += 0.02) {
                    let r;
                    if (selectedCurve.id === 3) {
                        r = params.a + params.b * theta;
                    } else { // Cardioide
                        r = params.a * (1 + Math.cos(theta));
                    }
                    points.push([r * Math.cos(theta), r * Math.sin(theta)]);
                }
                pathsData.push(points);
                break;
            }

        case 5: // Lemniscata de Bernoulli
            {
              // Precisamos de dois arrays, um para cada laço da curva
              const lobe1 = [];
              const lobe2 = [];

              // 1. Calcula os pontos para o laço direito (ângulos entre -45° e 45°)
              for (let theta = -Math.PI / 4; theta <= Math.PI / 4; theta += 0.01) {
                  // A fórmula r = a * sqrt(cos(2θ)) só funciona quando cos(2θ) é positivo
                  const r = params.a * Math.sqrt(Math.cos(2 * theta));
                  lobe1.push([r * Math.cos(theta), r * Math.sin(theta)]);
              }

              // 2. Calcula os pontos para o laço esquerdo (ângulos entre 135° e 225°)
              for (let theta = 3 * Math.PI / 4; theta <= 5 * Math.PI / 4; theta += 0.01) {
                  const r = params.a * Math.sqrt(Math.cos(2 * theta));
                  lobe2.push([r * Math.cos(theta), r * Math.sin(theta)]);
              }

              // 3. Adiciona AMBOS os laços para serem desenhados como caminhos separados
              pathsData.push(lobe1, lobe2);
              break;
          }

        case 7: // Curva de Bézier
            {
                const p0 = {x: params.P0x, y: params.P0y};
                const p1 = {x: params.P1x, y: params.P1y};
                const p2 = {x: params.P2x, y: params.P2y};
                
                const points = [];
                for (let t = 0; t <= 1; t += 0.01) {
                    const x = (1 - t) * (1 - t) * p0.x + 2 * (1 - t) * t * p1.x + t * t * p2.x;
                    const y = (1 - t) * (1 - t) * p0.y + 2 * (1 - t) * t * p1.y + t * t * p2.y;
                    points.push([x,y]);
                }
                pathsData.push(points);
                
                // Desenhar pontos de controle e linhas
                g.append('line').attr('x1', xScale(p0.x)).attr('y1', yScale(p0.y)).attr('x2', xScale(p1.x)).attr('y2', yScale(p1.y)).attr('stroke', 'rgba(255,0,0,0.5)').attr('stroke-dasharray', '4');
                g.append('line').attr('x1', xScale(p1.x)).attr('y1', yScale(p1.y)).attr('x2', xScale(p2.x)).attr('y2', yScale(p2.y)).attr('stroke', 'rgba(255,0,0,0.5)').attr('stroke-dasharray', '4');
                [p0, p1, p2].forEach(p => {
                    g.append('circle').attr('cx', xScale(p.x)).attr('cy', yScale(p.y)).attr('r', 5).attr('fill', p === p1 ? 'red' : 'black');
                });
                break;
            }

        case 8: // Hipocicloide
            {
                const points = [];
                const {a, b} = params;
                // Para fechar a curva, theta precisa ir até 2*PI * (denominador da fração a/b simplificada)
                // Usar 20*PI é uma aproximação segura para a maioria dos casos.
                for (let theta = 0; theta <= 20 * Math.PI; theta += 0.02) {
                    const x = (a - b) * Math.cos(theta) + b * Math.cos(theta * (a - b) / b);
                    const y = (a - b) * Math.sin(theta) - b * Math.sin(theta * (a - b) / b);
                    points.push([x,y]);
                }
                pathsData.push(points);
                break;
            }
    }

    // Desenho dos caminhos
    g.selectAll('path.line')
      .data(pathsData)
      .enter()
      .append('path')
      .attr('class', 'line')
      .attr('d', lineGenerator)
      .attr('stroke', '#3a86ff')
      .attr('stroke-width', 2)
      .attr('fill', 'none');

    // Animação (sem alterações)
    if (animate) {
      svg.selectAll('path.line')
        .attr('stroke-dasharray', function() { return this.getTotalLength(); })
        .attr('stroke-dashoffset', function() { return this.getTotalLength(); })
        .transition()
        .duration(1500)
        .ease(d3.easeCubicOut)
        .attr('stroke-dashoffset', 0);
    }
  }

  function getParamPrecision(param) {
      const stepStr = param.step.toString();
      if (stepStr.includes('.')) {
          return stepStr.split('.')[1].length;
      }
      return 0;
  }

  function nextFact() {
    currentFact = (currentFact + 1) % selectedCurve.facts.length;
  }

  function animateChart() {
    isAnimating = true;
    updateChart(true);
    setTimeout(() => isAnimating = false, 1500);
  }
</script>

<style>
  :global(html) {
  scroll-behavior: smooth;
  }

  :global(body) {
    margin: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8f9fa;
    color: #333;
    overflow-y: auto;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }

  h1, h2 {
    color: #2b2d42;
  }

  .curve-selector {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
  }

  button {
    background-color: #3a86ff;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s;
  }

  button:hover {
    background-color: #2667cc;
  }

  button.active {
    background-color: #1a4d8f;
  }

  .content-wrapper {
    display: flex;
    gap: 30px;
    margin-top: 20px;
  }

  .graph-section {
    flex: 1;
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  #graph-container {
    width: 100%;
    height: 400px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-bottom: 20px;
  }

  .params {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
    margin: 20px 0;
  }

  .param {
    margin-bottom: 10px;
  }

  label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
  }

  input[type="range"] {
    width: 100%;
    transition: box-shadow 0.3s ease;
  }
  
  input[type="range"]:active {
    box-shadow: 0 0 0 2px #3a86ff33;
  }

  .value-display {
    font-size: 14px;
    color: #666;
  }

  .info-section {
    flex: 1;
    background: white;
    border-radius: 10px;
    padding: 30px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .description {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 30px;
  }

  .facts-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 15px;
    color: #2b2d42;
  }

  .fact {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 15px;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 5px;
  }

  .next-fact-btn {
    margin-top: 10px;
  }

  .update-btn {
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  .update-btn:after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: rgba(255,255,255,0.2);
    transition: all 0.3s ease;
  }

  .update-btn:hover:after {
    left: 100%;
  }

  @media (max-width: 768px) {
    .content-wrapper {
      flex-direction: column;
    }
    
    .curve-selector {
      flex-direction: column;
    }
    
    .params {
      grid-template-columns: 1fr;
    }
  }

  /* Estilos para os eixos do D3 */
  .axis text {
    font-size: 12px;
    fill: #666;
  }

  .axis path,
  .axis line {
    fill: none;
    stroke: #ccc;
    shape-rendering: crispEdges;
  }

  /*criadores das curvas*/
.creators-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.creators-section ul {
  list-style-type: '→ ';
  padding-left: 20px;
  margin: 0;
  color: #555;
}

.creators-section li {
  margin-bottom: 8px;
  font-size: 15px;
  line-height: 1.5;
}
</style>

<div class="container">
  <h1>Guia Interativo de Curvas Matemáticas</h1>
  
  <div class="curve-selector">
    {#each curves as curve}
      <button 
        class={selectedCurve.id === curve.id ? 'active' : ''}
        on:click={() => {
          window.scrollTo(0, 0);
          selectedCurve = curve;
          currentFact = 0;
          animateChart();
        }}
      >
        {curve.name}
      </button>
    {/each}
  </div>

  <div class="content-wrapper">
    <!-- Seção do gráfico (esquerda) -->
    <div class="graph-section">
      <h2>{selectedCurve.name}</h2>
      <p>Fórmula: {selectedCurve.formula}</p>
      
      <div id="graph-container"></div>
      
      <div class="params">
        {#each selectedCurve.params as param}
          <div class="param">
            <label for={param.name}>
              {param.desc} ({param.name} = {params[param.name].toFixed(getParamPrecision(param))})
            </label>
            <input
              type="range"
              id={param.name}
              bind:value={params[param.name]}
              min={param.min}
              max={param.max}
              step={param.step}
            />
            <div class="value-display">
              Min: {param.min} | Max: {param.max}
            </div>
          </div>
        {/each}
      </div>

      <button class="update-btn" on:click={animateChart} disabled={isAnimating}>
        {isAnimating ? 'Animando...' : 'Animar Gráfico'}
      </button>
    </div>
    
    <!-- Seção de informações (direita) -->
    <div class="info-section">
      <h2>Sobre a {selectedCurve.name}</h2>
      
      <div class="description">
        {selectedCurve.description}
      </div>
      
      <div class="facts-title">Curiosidades:</div>
      
      <div class="fact" transition:fade>
        {selectedCurve.facts[currentFact]}
      </div>
      
      <button class="next-fact-btn" on:click={nextFact}>
        Próxima Curiosidade →
      </button>

      <div class="creators-section">
            <div class="facts-title">Principais Nomes:</div>
            <ul>
                {#each selectedCurve.creators as creator}
                    <li>{creator}</li>
                {/each}
            </ul>
      </div>
    </div>
  </div>
</div>