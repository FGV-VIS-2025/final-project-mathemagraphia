<script>
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
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
  let canvas;
  let ctx;
  let currentFact = 0;
  let needsUpdate = false;
  let isAnimating = false;
  let animationFrameId = null;

  // Inicializa os parâmetros
  $: {
    if (selectedCurve) {
      params = {};
      selectedCurve.params.forEach(p => {
        params[p.name] = p.value;
      });
      needsUpdate = true;
    }
  }


  function updateCanvas() {
    if (isAnimating) return;
    drawCurve(true); // Força animação
      }

    $: if (canvas && ctx && selectedCurve && !isAnimating) {
      drawCurve(); // Atualização automática sem animação
    }


  onMount(() => {
    // Correção para o problema do getContext
    canvas = document.getElementById('graphCanvas');
    if (canvas) {
      ctx = canvas.getContext('2d');
      resizeCanvas();
      window.addEventListener('resize', resizeCanvas);
    }
    return () => window.removeEventListener('resize', resizeCanvas);
  });

  function resizeCanvas() {
    if (!canvas) return;
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    needsUpdate = true;
    drawCurve();
  }

  function drawCurve(animate = false) {
  if (!ctx || !canvas) return;
  
  // Cancela qualquer animação pendente
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  
  const width = canvas.width;
  const height = canvas.height;
  
  if (animate) {
    // Animação de fade out
    let opacity = 1;
    const fadeOut = () => {
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
      ctx.fillRect(0, 0, width, height);
      drawCompleteCurve(opacity);
      
      opacity -= 0.05;
      if (opacity > 0) {
        animationFrameId = requestAnimationFrame(fadeOut);
      } else {
        // Quando fade out completa, faz fade in
        drawCompleteCurve(0);
        fadeIn();
      }
    };
    
    // Animação de fade in
    let fadeInOpacity = 0;
    const fadeIn = () => {
      ctx.clearRect(0, 0, width, height);
      drawCompleteCurve(1);
      ctx.fillStyle = `rgba(255, 255, 255, ${1 - fadeInOpacity})`;
      ctx.fillRect(0, 0, width, height);
      
      fadeInOpacity += 0.05;
      if (fadeInOpacity < 1) {
        animationFrameId = requestAnimationFrame(fadeIn);
      } else {
        // Animação completa
        animationFrameId = null;
        isAnimating = false;
      }
    };
    
    isAnimating = true;
    fadeOut();
  } else {
    // Redesenho normal sem animação
    ctx.clearRect(0, 0, width, height);
    drawCompleteCurve(1);
  }
}

function drawCompleteCurve(opacity = 1) {
  const width = canvas.width;
  const height = canvas.height;
  const centerX = width / 2;
  const centerY = height / 2;
  const scale = 50;
  
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
  
  // Marcadores e valores dos eixos (mesmo código anterior)
  // ... (manter o código de marcação dos eixos)
  
  // Desenha curva com opacidade
  ctx.strokeStyle = `rgba(58, 134, 255, ${opacity})`;
  ctx.lineWidth = 3;
  ctx.beginPath();
  
  if (selectedCurve.id === 3) {
    // Espiral (código mantido)
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
    // Outras curvas (código mantido)
    for (let x = -10; x <= 10; x += 0.1) {
      let y;
      
      if (selectedCurve.id === 1) {
        y = params.a * Math.sin(params.b * x + params.c);
      } else if (selectedCurve.id === 2) {
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
    transition: background-color 0.3s;
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

  input[type="range"] {
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

  .graph-container {
    position: relative;
    transition: opacity 0.5s ease;
  }
  
  .graph-container.animating {
    opacity: 0.5;
  }
  
  .update-btn {
    transition: transform 0.3s ease;
  }
  
  .update-btn:active {
    transform: scale(0.95);
  }

  .canvas-container {
  position: relative;
  width: 100%;
  height: 400px;
}

#graphCanvas {
  width: 100%;
  height: 100%;
  display: block;
  background: white;
  border: 1px solid #ddd;
  border-radius: 5px;
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
      
      <div class="graph-container" class:animating={isAnimating}>
        <canvas id="graphCanvas"></canvas>
      </div>
      
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

      <button class="update-btn" on:click={updateCanvas}>
        {isAnimating ? 'Atualizando...' : 'Atualizar Gráfico'}
      </button>
    </div>
    
    <!-- Seção de informações (direita) -->
    <div class="info-section">
      <h2>Sobre a {selectedCurve.name}</h2>
      
      <div class="description">
        {selectedCurve.description}
      </div>
      
      <div class="facts-title">Curiosidades:</div>
      
      <div class="fact">
        {selectedCurve.facts[currentFact]}
      </div>
      
      <button class="next-fact-btn" on:click={nextFact}>
        Próxima Curiosidade →
      </button>
    </div>
  </div>
</div>