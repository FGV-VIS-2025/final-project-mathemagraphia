<script>
import { onMount, onDestroy } from 'svelte';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';

let containerEl;
let svgEl;
let tooltipEl;

const MAP_URL  = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';
const DATA_URL = 'data/biografias_com_coords.json';

let projection, path, g, svg;
let pontos = [];
let land;

function drawLand() {
  g.append('path')
    .datum(land)
    .attr('d', path)
    .attr('fill', '#eee')
    .attr('stroke', '#999');
}

let fixedTooltipData = null;

function showTooltip(e, d) {
  const bounds = containerEl.getBoundingClientRect();
  tooltipEl.innerHTML = `
    <strong>${d.nome_completo}</strong><br/>
    <a href="${d.link}" target="_blank">Ver biografia</a>
  `;
  tooltipEl.style.opacity = '1';
  tooltipEl.style.pointerEvents = 'auto'; // reativa interatividade
  tooltipEl.style.left = (e.clientX - bounds.left + 10) + 'px';
  tooltipEl.style.top = (e.clientY - bounds.top - 28) + 'px';
}


function hideTooltip() {
  tooltipEl.style.opacity = '0';
  tooltipEl.style.pointerEvents = 'none';
  tooltipEl.innerHTML = ''; // opcional, se quiser remover conteúdo
}


function drawPoints() {
  g.selectAll('circle')
    .data(pontos, d => d.link)
    .join(
      enter => enter.append('circle')
        .attr('cx', d => projection(d.coords)[0])
        .attr('cy', d => projection(d.coords)[1])
        .attr('r', 0)
        .attr('fill', 'crimson')
        .attr('stroke', '#000')
        .attr('stroke-width', 0.5)
        .on('mouseover', (e, d) => {
          if (!fixedTooltipData) showTooltip(e, d);
        })
        .on('mouseout', () => {
          if (!fixedTooltipData) hideTooltip();
        })
        .on('click', (e, d) => {
          if (fixedTooltipData && fixedTooltipData.link === d.link) {
            fixedTooltipData = null;
            hideTooltip();
          } else {
            fixedTooltipData = d;
            showTooltip(e, d);
          }
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


function render() {
  g.selectAll('*').remove();
  drawLand();
  drawPoints();
}

function resize() {
  const { width, height } = containerEl.getBoundingClientRect();

  svg
    .attr('viewBox', `0 0 ${width} ${height}`)
    .attr('preserveAspectRatio', 'xMidYMid meet');

  projection
    .fitSize([width, height], land); // usa fitSize em vez de scale + translate

  path = d3.geoPath(projection);
  render();
}

  function handleClickOutside(e) {
    if (
      fixedTooltipData &&
      !tooltipEl.contains(e.target) &&
      !e.target.closest('circle')
    ) {
      fixedTooltipData = null;
      hideTooltip();
    }
  }

onMount(async () => {

  window.addEventListener('click', handleClickOutside);

  svg = d3.select(svgEl);
  g = svg.append('g');

  projection = d3.geoNaturalEarth1();
  path = d3.geoPath(projection);

  const world = await d3.json(MAP_URL);
  land = topojson.feature(world, world.objects.countries);

  const raw = await d3.json(DATA_URL);
  pontos = raw
    .filter(d => d.lat_nasc && d.lon_nasc)
    .map(d => ({ ...d, coords: [d.lon_nasc, d.lat_nasc] }));

  const ro = new ResizeObserver(resize);
  ro.observe(containerEl);

  onDestroy(() => {
    ro.disconnect();
    window.removeEventListener('click', handleClickOutside);
  });


  resize();
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
    height: 100vh;
    background: #f5f5f5;
  }

  .map-container {
    width: 90vw;
    height: 90vh;
    position: relative;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    border-radius: 12px;
    overflow: hidden;
  }

  svg {
    width: 100%;
    height: 100%;
    background: radial-gradient(#fff, #e0e0e0);
  }

  #tooltip {
    position: absolute;
    pointer-events: auto; /* permite cliques */
    background: white;
    padding: 6px 10px;
    border: 1px solid #999;
    border-radius: 4px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    font-size: 0.85rem;
    opacity: 0;
    transition: opacity 0.2s;
    z-index: 10;
  }


  :global(a) {
    color: steelblue;
    text-decoration: underline;
  }
</style>
