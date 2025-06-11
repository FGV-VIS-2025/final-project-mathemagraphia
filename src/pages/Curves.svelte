<script>
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import { elasticOut } from 'svelte/easing';
  import * as d3 from 'd3';


  // Dados das curvas e curiosidades
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
        "Usada para modelar fenômenos periódicos como ondas sonoras",
        "A curva aparece naturalmente em muitos fenômenos físicos",
        "Leonhard Euler estabeleceu a relação entre funções trigonométricas e números complexos"
      ],
      description: "A curva senoidal é uma das funções mais importantes na matemática e física, descrevendo movimentos oscilatórios e ondulatórios. Ela é fundamental para entender fenômenos como ondas sonoras, luz e corrente alternada."
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
        "Descreve o movimento de projéteis sob gravidade",
        "Antenas parabólicas usam esta propriedade para focar ondas",
        "Arquimedes estudou as propriedades das parábolas no século III a.C."
      ],
      description: "As parábolas são curvas cônicas que aparecem em diversos contextos físicos, desde a trajetória de projéteis até a forma de espelhos e antenas. Suas propriedades de foco e diretriz são essenciais em óptica e engenharia."
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
        "Aparece em fenômenos naturais como conchas e galáxias",
        "Usada em engrenagens mecânicas para movimento uniforme",
        "Arquimedes descreveu esta espiral em seu livro 'Sobre as Espirais'"
      ],
      description: "A espiral de Arquimedes é uma curva que se expande uniformemente à medida que gira em torno de seu centro. Ela modela padrões naturais como conchas de moluscos e é usada em diversas aplicações tecnológicas."
    }
  ];

  // Estado da aplicação
  let selectedCurve = curves[0];
  let params = {};
  let svg;
  let currentFact = 0;
  let isAnimating = false;
  let width = 600;
  let height = 400;
  let margin = { top: 20, right: 20, bottom: 40, left: 50 };

  // Inicializa os parâmetros
  $: {
    if (selectedCurve) {
      params = {};
      selectedCurve.params.forEach(p => {
        params[p.name] = p.value;
      });
      updateChart();
    }
  }

  // Atualiza quando os parâmetros mudam
  $: if (selectedCurve) {
    updateChart();
  }

  onMount(() => {
    // Configura o SVG inicial
    svg = d3.select('#graph-container')
      .append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet');
    
    updateChart();
    
    // Atualiza dimensões quando a janela é redimensionada
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

  function updateChart(animate = false) {
    if (!svg || !selectedCurve) return;
    
    // Limpa o SVG
    svg.selectAll('*').remove();
    
    // Área útil do gráfico
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    
    // Cria grupo principal para o gráfico
    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Escalas
    const xScale = d3.scaleLinear()
      .domain([-10, 10])
      .range([0, innerWidth]);
      
    const yScale = d3.scaleLinear()
      .domain([-5, 5])
      .range([innerHeight, 0]);
    
    // Eixos
    const xAxis = d3.axisBottom(xScale)
      .ticks(10)
      .tickSize(-innerHeight)
      .tickPadding(10);
      
    const yAxis = d3.axisLeft(yScale)
      .ticks(10)
      .tickSize(-innerWidth)
      .tickPadding(10);
    
    // Adiciona eixos
    g.append('g')
      .attr('class', 'x axis')
      .attr('transform', `translate(0,${innerHeight / 2})`)
      .call(xAxis)
      .selectAll('line')
      .attr('stroke', '#eee');
      
    g.append('g')
      .attr('class', 'y axis')
      .attr('transform', `translate(${innerWidth / 2},0)`)
      .call(yAxis)
      .selectAll('line')
      .attr('stroke', '#eee');
    
    // Linha central dos eixos
    g.append('line')
      .attr('x1', 0)
      .attr('y1', innerHeight / 2)
      .attr('x2', innerWidth)
      .attr('y2', innerHeight / 2)
      .attr('stroke', '#ccc')
      .attr('stroke-width', 1);
      
    g.append('line')
      .attr('x1', innerWidth / 2)
      .attr('y1', 0)
      .attr('x2', innerWidth / 2)
      .attr('y2', innerHeight)
      .attr('stroke', '#ccc')
      .attr('stroke-width', 1);
    
    // Linha do gráfico
    if (selectedCurve.id === 3) {
      // Espiral de Arquimedes (coordenadas polares)
      const points = [];
      for (let theta = 0; theta < 10 * Math.PI; theta += 0.1) {
        const r = params.a + params.b * theta;
        const x = r * Math.cos(theta);
        const y = r * Math.sin(theta);
        points.push([x, y]);
      }
      
      const line = d3.line()
        .x(d => xScale(d[0]) - innerWidth / 2)
        .y(d => yScale(d[1]) - innerHeight / 2);
        
      g.append('path')
        .datum(points)
        .attr('class', 'line')
        .attr('d', line)
        .attr('stroke', '#3a86ff')
        .attr('stroke-width', 2)
        .attr('fill', 'none')
        .attr('transform', `translate(${innerWidth / 2},${innerHeight / 2})`);
    } else {
      // Funções cartesianas
      const points = [];
      for (let x = -10; x <= 10; x += 0.1) {
        let y;
        if (selectedCurve.id === 1) {
          y = params.a * Math.sin(params.b * x + params.c);
        } else if (selectedCurve.id === 2) {
          y = params.a * x * x + params.b * x + params.c;
        }
        points.push([x, y]);
      }
      
      const line = d3.line()
        .x(d => xScale(d[0]) - innerWidth / 2)
        .y(d => yScale(d[1]) - innerHeight / 2);
        
      g.append('path')
        .datum(points)
        .attr('class', 'line')
        .attr('d', line)
        .attr('stroke', '#3a86ff')
        .attr('stroke-width', 2)
        .attr('fill', 'none')
        .attr('transform', `translate(${innerWidth / 2},${innerHeight / 2})`);
    }
    
    // Animação de entrada
    if (animate) {
      svg.selectAll('.line')
        .attr('stroke-dasharray', function() {
          return this.getTotalLength();
        })
        .attr('stroke-dashoffset', function() {
          return this.getTotalLength();
        })
        .transition()
        .duration(1000)
        .ease(d3.easeCubicOut)
        .attr('stroke-dashoffset', 0);
    }
  }

  function nextFact() {
    currentFact = (currentFact + 1) % selectedCurve.facts.length;
  }

  function animateChart() {
    isAnimating = true;
    updateChart(true);
    setTimeout(() => isAnimating = false, 1000);
  }
</script>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8f9fa;
    color: #333;
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
</style>

<div class="container">
  <h1>Guia Interativo de Curvas Matemáticas</h1>
  
  <div class="curve-selector">
    {#each curves as curve}
      <button 
        class={selectedCurve.id === curve.id ? 'active' : ''}
        on:click={() => {
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
              {param.desc} ({param.name} = {params[param.name].toFixed(param.name === 'b' && selectedCurve.id === 3 ? 2 : 1)})
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
    </div>
  </div>
</div>