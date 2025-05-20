<script>
import { onMount, onDestroy } from 'svelte';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';

let containerEl;
let svgEl;
let tooltipEl;

const MAP_URL  = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';
const DATA_URL = 'data/biografias_com_coords.json';

// Declarações de variáveis no escopo do componente
let projection, path, g, svg;
let pontos = [];
let land;               // antes estava em window.land
let lastMouse = null;   // antes não existia
let fixedTooltip = false;
let isUserInteracting = false;
let rotation;
let autoRotateTimer = null;
let restartTimer    = null;

// Funções de desenho (sem alterações)
function drawSphere() {
  g.append('path')
    .datum({ type: 'Sphere' })
    .attr('d', path)
    .attr('fill', '#1d4ed8');
}

function drawLand() {
  g.append('path')
    .datum(land)            // agora usa a variável local `land`
    .attr('d', path)
    .attr('fill', '#eee')
    .attr('stroke', '#999');
}

// FUNÇÃO CORRIGIDA: Verifica se um ponto está visível na parte frontal do globo
function isPointVisible(coord) {
  // Obtém a rotação atual do globo
  const [lambda, phi] = projection.rotate();
  
  // Converte as coordenadas do ponto para radianos
  const pointLambda = coord[0] * Math.PI / 180;
  const pointPhi = coord[1] * Math.PI / 180;
  
  // Converte a rotação atual para radianos
  const lambdaR = lambda * Math.PI / 180;
  const phiR = phi * Math.PI / 180;
  
  // Calcula o cosseno do ângulo central entre o ponto e o centro da visualização
  // Usando a fórmula da distância angular na esfera
  const cosAngle = Math.sin(pointPhi) * Math.sin(-phiR) + 
                  Math.cos(pointPhi) * Math.cos(-phiR) * 
                  Math.cos(pointLambda - (-lambdaR));
  
  // O ponto é visível se o cosseno do ângulo for positivo
  // (isso significa que o ângulo está entre -90 e 90 graus)
  return cosAngle > 0;
}

function drawPoints() {
  const visible = pontos.filter(d => isPointVisible(d.coords));

  g.selectAll('circle')
    .data(visible, d => d.link)
    .join(
      enter => enter.append('circle')
        .attr('cx', d => projection(d.coords)[0])
        .attr('cy', d => projection(d.coords)[1])
        .attr('r', 0)
        .attr('fill', 'crimson')
        .attr('stroke', '#000')
        .attr('stroke-width', 0.5)
        .on('mouseover', (e, d) => {
          if (!fixedTooltip) {
            tooltipEl.innerHTML = `
              <strong>${d.nome_completo}</strong><br/>
              <a href="${d.link}" target="_blank">Ver biografia</a>
            `;
            tooltipEl.style.opacity = '1';
            tooltipEl.style.left = e.pageX + 10 + 'px';
            tooltipEl.style.top = e.pageY - 28 + 'px';
          }
        })
        .on('mouseout', () => {
          if (!fixedTooltip) tooltipEl.style.opacity = '0';
        })
        .on('click', () => {
          fixedTooltip = !fixedTooltip;
          if (!fixedTooltip) tooltipEl.style.opacity = '0';
        })
        .transition()
        .duration(300)
        .attr('r', 3),
      update => update
        .attr('cx', d => projection(d.coords)[0])
        .attr('cy', d => projection(d.coords)[1]),
      exit => exit.remove()
    );
}

// Re-render completo
function render() {
  g.selectAll('*').remove();
  drawSphere();
  drawLand();
  drawPoints();
}

function startAutoRotate() {
  if (autoRotateTimer) return;
  autoRotateTimer = setInterval(() => {
    if (!isUserInteracting) {
      rotation = projection.rotate();
      rotation[0] += 0.2;
      projection.rotate(rotation);
      render();
    }
  }, 30);
}

function stopAutoRotate() {
  isUserInteracting = true;
  clearTimeout(restartTimer);
  restartTimer = setTimeout(() => {
    isUserInteracting = false;
  }, 3000);
}

function resize() {
  const { width, height } = containerEl.getBoundingClientRect();

  svg
    .attr('viewBox', `0 0 ${width} ${height}`)
    .attr('preserveAspectRatio', 'xMidYMid meet');

  projection
    .translate([width / 2, height / 2])
    .scale((Math.min(width, height) / 2) * 0.9);

  path = d3.geoPath(projection);
  render();
}

onMount(async () => {
  svg = d3.select(svgEl);
  g   = svg.append('g');

  projection = d3.geoOrthographic().clipAngle(90);
  path       = d3.geoPath(projection);

  // Carrega e atribui a variável `land`
  const world = await d3.json(MAP_URL);
  land = topojson.feature(world, world.objects.countries);

  // Carrega os pontos
  const raw = await d3.json(DATA_URL);
  pontos = raw
    .filter(d => d.lat_nasc && d.lon_nasc)
    .map(d => ({ ...d, coords: [d.lon_nasc, d.lat_nasc] }));

  rotation = projection.rotate();

  const ro = new ResizeObserver(resize);
  ro.observe(containerEl);

  svg.call(
    d3.drag()
      .on('start', e => {
        stopAutoRotate();
        lastMouse = [e.x, e.y];
      })
      .on('drag', e => {
        if (!lastMouse) return;
        const [lx, ly] = lastMouse;
        const dx = e.x - lx, dy = e.y - ly;
        rotation = projection.rotate();
        projection.rotate([
          rotation[0] + dx * 0.25,
          rotation[1] - dy * 0.25
        ]);
        render();
        lastMouse = [e.x, e.y];
      })
      .on('end', () => {
        rotation = projection.rotate();
        lastMouse = null;
      })
  );

  onDestroy(() => {
    ro.disconnect();
    clearInterval(autoRotateTimer);
    clearTimeout(restartTimer);
  });

  resize();
  startAutoRotate();
});
</script>

<div class="map-wrapper">
  <div class="map-container" bind:this={containerEl}>
    <svg bind:this={svgEl}></svg>
    <div bind:this={tooltipEl} id="tooltip"></div>
  </div>
</div>


<style>
  .map-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;       /* ocupa a altura inteira da tela */
    background: #f5f5f5; /* cor de fundo opcional */
  }

  .map-container {
    width: 90vmin;        /* largura baseada na menor dimensão da tela */
    height: 90vmin;       /* altura igual para formar um quadrado */
    position: relative;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); /* borda suave */
    border-radius: 12px;
    overflow: hidden;
  }

  svg {
    width: 100%;
    height: 100%;
    background: radial-gradient(#fff, #e0e0e0);
    cursor: grab;
  }

  svg:active {
    cursor: grabbing;
  }

  #tooltip {
    position: absolute;
    top: 0;
    left: 0;
    background: white;
    padding: 6px 10px;
    border: 1px solid #999;
    border-radius: 4px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    font-size: 0.85rem;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s;
    z-index: 10;
  }
  :global(a) {
    color: steelblue;
    text-decoration: underline;
  }
</style>
