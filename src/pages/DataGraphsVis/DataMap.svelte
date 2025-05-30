<script>
  import { onMount, onDestroy } from 'svelte';
  import * as d3 from 'd3';
  import * as topojson from 'topojson-client';

  let containerEl, svgEl, tooltipEl;
  let projection, path, g, svg;
  let land;

  const MAP_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';
  const DATA_URL = 'data/biografias_com_coords.json';

  let raw = [];
  let pontos = [];

  let seculoAtual = 17;
  let playing = false;
  let intervaloAnimacao = null;
  let fixedTooltipData = null;

  function drawLand() {
    g.append('path')
      .datum(land)
      .attr('d', path)
      .attr('fill', '#eaeaea')
      .attr('stroke', '#aaa')
      .attr('stroke-width', 0.5);

    // ❌ Removido: nomes dos países
  }

  function showTooltip(e, d) {
  const bounds = containerEl.getBoundingClientRect();
  tooltipEl.innerHTML = `
    <strong>${d.nome_completo}</strong><br/>
    <span><strong>País:</strong> ${d.pais || 'Desconhecido'}</span><br/>
    <span><strong>Nasc.:</strong> ${d.ano_nascimento || 'Desconhecido'}</span><br/>
    <a href="${d.link}" target="_blank">Ver biografia</a>
  `;
  tooltipEl.style.opacity = '1';
  tooltipEl.style.pointerEvents = 'auto';
  tooltipEl.style.left = (e.clientX - bounds.left + 10) + 'px';
  tooltipEl.style.top = (e.clientY - bounds.top - 28) + 'px';
}

  function hideTooltip() {
    tooltipEl.style.opacity = '0';
    tooltipEl.style.pointerEvents = 'none';
    tooltipEl.innerHTML = '';
  }

  function drawPoints() {
    g.selectAll('circle').remove();

    g.selectAll('circle')
      .data(pontos, d => d.link)
      .enter()
      .append('circle')
      .attr('cx', d => projection(d.coords)[0])
      .attr('cy', d => projection(d.coords)[1])
      .attr('r', 4)
      .attr('fill', '#d62828')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1)
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
      });
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

    projection.fitSize([width, height], land);
    path = d3.geoPath(projection);
    render();
  }

  function atualizarPontosFiltrados() {
    const maxAno = seculoAtual * 100;

    pontos = raw
      .filter(d =>
        d.lat_nasc != null &&
        d.lon_nasc != null &&
        !isNaN(+d.ano_nascimento) &&
        +d.ano_nascimento <= maxAno
      )
      .map(d => ({
        ...d,
        ano_nasc: +d.ano_nascimento,
        coords: [d.lon_nasc, d.lat_nasc]
      }));

    drawPoints();
  }

  function togglePlay() {
    playing = !playing;
    if (playing) {
      intervaloAnimacao = setInterval(() => {
        seculoAtual++;
        if (seculoAtual > 21) {
          clearInterval(intervaloAnimacao);
          playing = false;
          return;
        }
        atualizarPontosFiltrados();
      }, 800);
    } else {
      clearInterval(intervaloAnimacao);
    }
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

    raw = await d3.json(DATA_URL);
    atualizarPontosFiltrados();

    // ✅ Zoom e pan
    svg.call(
      d3.zoom()
        .scaleExtent([1, 8])
        .on('zoom', ({ transform }) => {
          g.attr('transform', transform);
        })
    );

    const ro = new ResizeObserver(resize);
    ro.observe(containerEl);

    onDestroy(() => {
      ro.disconnect();
      clearInterval(intervaloAnimacao);
      window.removeEventListener('click', handleClickOutside);
    });

    resize();
  });
</script>

<!-- MAPA -->
<div class="map-wrapper">
  <div class="map-container" bind:this={containerEl}>
    <svg bind:this={svgEl}></svg>
    <div bind:this={tooltipEl} id="tooltip"></div>
  </div>
</div>

<!-- CONTROLES -->
<div class="controls">
  <label>
    Século:
    <input type="range" min="9" max="21" bind:value={seculoAtual} on:input={atualizarPontosFiltrados} />
    <span>{seculoAtual}º</span>
  </label>
  <button class="play-button" on:click={togglePlay}>
    {playing ? '⏸ Pausar' : '▶️ Play'}
  </button>
</div>

<!-- ESTILO -->
<style>
  .map-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 85vh;
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
    background: linear-gradient(to bottom, #f0f4f8, #d9e2ec);
  }

  #tooltip {
    position: absolute;
    pointer-events: auto;
    background: white;
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 6px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    font-size: 0.85rem;
    opacity: 0;
    transition: opacity 0.2s ease;
    z-index: 10;
  }

  .controls {
    text-align: center;
    margin-top: 18px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  .controls label {
    font-size: 1rem;
    margin-right: 1rem;
  }

  .controls input[type="range"] {
    vertical-align: middle;
    accent-color: steelblue;
  }

  .play-button {
    background-color: steelblue;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 8px 20px;
    font-size: 1rem;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    transition: background-color 0.2s;
  }

  .play-button:hover {
    background-color: #336699;
  }

  :global(a) {
    color: steelblue;
    text-decoration: underline;
  }
</style>
