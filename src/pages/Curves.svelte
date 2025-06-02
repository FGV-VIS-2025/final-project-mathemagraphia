<script>
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import { elasticOut } from 'svelte/easing';

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
        "Descreve o movimento de projéteis sob gravidade",
        "Antenas parabólicas usam esta propriedade para focar ondas",
        "Arquimedes estudou as propriedades das parábolas no século III a.C."
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
        "Aparece em fenômenos naturais como conchas e galáxias",
        "Usada em engrenagens mecânicas para movimento uniforme",
        "Arquimedes descreveu esta espiral em seu livro 'Sobre as Espirais'"
      ]
    }
  ];

  // Estado da aplicação
  let selectedCurve = curves[0];
  let params = {};
  let canvas;
  let ctx;
  let currentFact = 0;
  let visibleSection = 'graph';

  // Inicializa os parâmetros
  $: {
    if (selectedCurve) {
      params = {};
      selectedCurve.params.forEach(p => {
        params[p.name] = p.value;
      });
    }
  }

  // Desenha a curva quando os parâmetros mudam
  $: if (canvas && ctx && selectedCurve) {
    drawCurve();
    }

  onMount(() => {
    canvas = document.getElementById('graphCanvas');
    if (canvas && canvas.getContext) {
        ctx = canvas.getContext('2d');
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    return () => window.removeEventListener('resize', resizeCanvas);
    });

  function resizeCanvas() {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    drawCurve();
  }

  function drawCurve() {
    if (!ctx) return;
    
    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const scale = 50;
    
    ctx.clearRect(0, 0, width, height);
    
    // Desenha eixos
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 1;
    
    // Eixo X
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    ctx.lineTo(width, centerY);
    ctx.stroke();
    
    // Eixo Y
    ctx.beginPath();
    ctx.moveTo(centerX, 0);
    ctx.lineTo(centerX, height);
    ctx.stroke();
    
    // Desenha curva
    ctx.strokeStyle = '#3a86ff';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    if (selectedCurve.id === 3) {
      // Espiral (coordenadas polares)
      for (let theta = 0; theta < 10 * Math.PI; theta += 0.1) {
        const r = params.a + params.b * theta;
        const x = centerX + r * scale * Math.cos(theta);
        const y = centerY - r * scale * Math.sin(theta);
        
        if (theta === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
    } else {
      // Outras curvas (coordenadas cartesianas)
      for (let x = -10; x <= 10; x += 0.1) {
        let y;
        
        if (selectedCurve.id === 1) {
          // Senoide
          y = params.a * Math.sin(params.b * x + params.c);
        } else if (selectedCurve.id === 2) {
          // Parábola
          y = params.a * x * x + params.b * x + params.c;
        }
        
        const plotX = centerX + x * scale;
        const plotY = centerY - y * scale;
        
        if (x === -10) {
          ctx.moveTo(plotX, plotY);
        } else {
          ctx.lineTo(plotX, plotY);
        }
      }
    }
    
    ctx.stroke();
  }

  function nextFact() {
    currentFact = (currentFact + 1) % selectedCurve.facts.length;
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
    max-width: 1000px;
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
    transition: background-color 0.3s;
  }

  button:hover {
    background-color: #2667cc;
  }

  button.active {
    background-color: #1a4d8f;
  }

  .graph-container {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
  }

  canvas {
    width: 100%;
    height: 400px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 5px;
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
  }

  .value-display {
    font-size: 14px;
    color: #666;
  }

  .facts-section {
    background: white;
    border-radius: 10px;
    padding: 30px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .fact {
    font-size: 18px;
    line-height: 1.6;
    margin-bottom: 20px;
  }

  .nav-buttons {
    display: flex;
    justify-content: space-between;
    margin-top: 30px;
  }

  @media (max-width: 768px) {
    .curve-selector {
      flex-direction: column;
    }
    
    .params {
      grid-template-columns: 1fr;
    }
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
          visibleSection = 'graph';
        }}
      >
        {curve.name}
      </button>
    {/each}
  </div>

  {#if visibleSection === 'graph'}
    <div class="graph-container" in:fly={{ y: 50, duration: 500, easing: elasticOut }}>
      <h2>{selectedCurve.name}</h2>
      <p>Fórmula: {selectedCurve.formula}</p>
      
      <canvas id="graphCanvas"></canvas>
      
      <div class="params">
        {#each selectedCurve.params as param}
          <div class="param">
            <label for={param.name}>
              {param.desc} ({param.name} = {params[param.name].toFixed(1)})
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
      
      <button on:click={() => visibleSection = 'facts'}>
        Ver Curiosidades ↓
      </button>
    </div>
  {:else}
    <div class="facts-section" in:fly={{ y: 50, duration: 500, easing: elasticOut }}>
      <h2>Curiosidades sobre {selectedCurve.name}</h2>
      
      <div class="fact">
        {selectedCurve.facts[currentFact]}
      </div>
      
      <div class="nav-buttons">
        <button on:click={() => visibleSection = 'graph'}>
          ← Voltar ao Gráfico
        </button>
        <button on:click={nextFact}>
          Próxima Curiosidade →
        </button>
      </div>
    </div>
  {/if}
</div>