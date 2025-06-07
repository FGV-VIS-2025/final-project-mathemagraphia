<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import * as topojson from 'topojson-client';

  import Timeline from '../components/Timeline.svelte';
  import VizContainer from '../components/VizContainer.svelte';
  import FixedBar from '../components/FixedBar.svelte';

  // Referência ao container do mapa
  let mapContainer;

  // Dados para o mapa
  let allPoints = [];
  let landFeatures = { type: 'FeatureCollection', features: [] };

  // Busca/autocomplete
  let searchTerm = '';
  let suggestions = [];
  let showSuggestions = false;
  let detailData = null;

  // Zoom/pan
  let svg, projection, path, zoomGroup;
  let currentTransform = d3.zoomIdentity;
  let scaleFactor = 1;

  // Modal de visualização expandida
  let expanded = null;
  function expand(id)   { expanded = id; }
  function closeModal() { expanded = null; }

  // Slugify para carregar JSON detalhado
  function slugify(name) {
    return name
      .toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, '-')
      .replace(/[^\w-]/g, '');
  }

  // Carrega TopoJSON e coords
  async function loadData() {
    const MAP_URL   = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';
    const COORDS_URL= 'public/data/mac_tutor_com_coords.json';

    const [world, raw] = await Promise.all([
      d3.json(MAP_URL),
      d3.json(COORDS_URL)
    ]);

    // Garantindo que sempre temos um FeatureCollection
    const worldFeatures = topojson.feature(world, world.objects.countries);
    landFeatures = {
      type: 'FeatureCollection',
      features: worldFeatures.features || [worldFeatures]
    };

    allPoints = raw
      .filter(d => typeof d.lat_nasc === 'number' && typeof d.lon_nasc === 'number')
      .map(d => ({
        nome_completo: d.nome_completo,
        nome_curto:    d.nome_curto,
        link:          d.link,
        coords:        [d.lon_nasc, d.lat_nasc]
      }));
  }

  // Inicializa SVG, projeção e zoom
  function initMap() {
    const { width, height } = mapContainer.getBoundingClientRect();

    svg = d3.select(mapContainer)
      .append('svg')
      .attr('width',  width)
      .attr('height', height);

    projection = d3.geoNaturalEarth1()
      .scale(width / 6.5)
      .translate([width/2, height/2]);

    path = d3.geoPath(projection);

    // zoom/pan
    const zoom = d3.zoom()
      .scaleExtent([0.5, 8])
      .on('zoom', (e) => {
        currentTransform = e.transform;
        scaleFactor      = e.transform.k;
        zoomGroup.attr('transform', currentTransform);
        zoomGroup.selectAll('circle')
          .attr('r',            3 / scaleFactor)
          .attr('stroke-width', 0.5 / scaleFactor);
      });

    svg.call(zoom);
  }

  // Desenha mapa e marcadores
  function drawMap() {
    svg.selectAll('*').remove();
    zoomGroup = svg.append('g')
      .attr('transform', currentTransform);

    // fundo clicável para limpar seleção
    svg.append('rect')
      .attr('width', '100%').attr('height','100%')
      .attr('fill', '#eef').lower()
      .on('click', () => detailData = null);

    // países
    zoomGroup.append('g')
      .selectAll('path')
      .data(landFeatures.features)
      .join('path')
      .attr('d',      path)
      .attr('fill',   '#ddd')
      .attr('stroke', '#999');

    // marcadores
    zoomGroup.append('g')
      .selectAll('circle')
      .data(allPoints)
      .join('circle')
      .attr('cx',     d => projection(d.coords)[0])
      .attr('cy',     d => projection(d.coords)[1])
      .attr('r',      3 / scaleFactor)
      .attr('fill',   'crimson')
      .attr('stroke', '#000')
      .attr('stroke-width', 0.5 / scaleFactor)
      .on('click', (_, d) => choosePoint(d));
  }

  // Quando escolhe um ponto
  async function choosePoint(d) {
    detailData = null;
    // carrega JSON detalhado
    const slug = slugify(d.nome_curto);
    try {
      detailData = await fetch(`/MacTutorData/${slug}.json`)
        .then(r => r.ok ? r.json() : null);
    } catch {
      detailData = null;
    }
    // centra o ponto
    const [x,y] = projection(d.coords);
    svg.transition().duration(600)
      .call(d3.zoom().translateTo, x, y);
  }

  // Autocomplete
  function onSearch() {
    const term = searchTerm.trim().toLowerCase();
    suggestions = allPoints
      .filter(p =>
        p.nome_curto.toLowerCase().includes(term) ||
        p.nome_completo.toLowerCase().includes(term)
      )
      .slice(0, 8);
  }

  onMount(async () => {
    await loadData();
    initMap();
    drawMap();
    window.addEventListener('resize', () => {
      // redesenha ao redimensionar
      d3.select(mapContainer).select('svg').remove();
      initMap();
      drawMap();
    });
  });
</script>

<div class="dashboard-layout">
  <!-- sidebar timeline - agora mais estreita e colada à esquerda -->
  <aside class="sidebar">
    <Timeline />
  </aside>

  <main class="main-content">
    <!-- mapa + busca -->
    <section class="map-section">
      <div class="map-and-search">
        <div class="map-wrapper" bind:this={mapContainer}></div>
        <div class="search-box">
          <input
            type="text"
            placeholder="Buscar matemático…"
            bind:value={searchTerm}
            on:input={() => { onSearch(); showSuggestions = true; }}
            on:blur={() => setTimeout(() => showSuggestions = false, 100)}
          />

          {#if showSuggestions && suggestions.length}
            <ul class="suggestions-list">
              {#each suggestions as s}
                <li on:click={() => choosePoint(s)}>
                  {s.nome_curto}
                </li>
              {/each}
            </ul>
          {/if}

          {#if detailData}
            <div class="detail-panel">
              <h2>{detailData.nome_completo}</h2>
              <p><strong>Nasceu:</strong> {detailData.data_nascimento}</p>
              <p><strong>Local:</strong>  {detailData.local_nascimento}</p>
              <p><strong>Morreu:</strong> {detailData.data_morte}</p>
              <p><strong>Local:</strong>  {detailData.local_morte}</p>
              <p>{detailData.summary}</p>
              <p><a href={detailData.link} target="_blank">Biografia completa</a></p>
            </div>
          {/if}
        </div>
      </div>
    </section>

    <!-- duas visualizações com mais espaço -->
    <section class="viz-section">
      {#each [1,2] as id}
        <div class="viz-wrapper">
          <VizContainer {id} on:expand={() => expand(id)} />
        </div>
      {/each}
    </section>
  </main>
</div>

<FixedBar />

{#if expanded}
  <div class="modal-overlay" on:click={closeModal}>
    <div class="modal-window" on:click|stopPropagation>
      <button on:click={closeModal}>×</button>
      <p>Visualização expandida #{expanded}</p>
    </div>
  </div>
{/if}

<style>
  /* Reset global para ocupar toda a página */
  :global(html, body) {
    margin: 0;
    padding: 0;
    height: 100%;
    overflow: hidden; /* Evita scroll na página */
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  /* Container principal ocupa 100% da viewport */
  .dashboard-layout {
    display: flex;
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    position: fixed; /* Garante que ocupe toda a tela */
    top: 0;
    left: 0;
  }

  /* Sidebar mais estreita e sem padding */
  .sidebar {
    width: 60px; /* Ainda mais estreita */
    min-width: 60px; /* Evita que diminua demais */
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-right: 2px solid rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
    z-index: 10;
  }

  /* Conteúdo principal maximizado */
  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 0.8rem;
    box-sizing: border-box;
    background: #f8fafc;
    overflow: hidden; /* Evita scroll interno */
  }

  /* Seção do mapa com altura otimizada */
  .map-section {
    flex: 0 0 45%; /* Aumentado para 45% */
    margin-bottom: 0.8rem;
    min-height: 300px; /* Altura mínima */
  }

  /* Layout do mapa e busca */
  .map-and-search {
    display: flex;
    height: 100%;
    gap: 1rem;
  }

  /* Mapa com proporção maior */
  .map-wrapper {
    flex: 4; /* Proporção 4:1 em vez de 5:1 */
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: #fff;
  }

  /* Caixa de busca otimizada */
  .search-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 250px; /* Largura mínima */
  }

  .search-box input {
    padding: 12px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    transition: border-color 0.2s ease;
    background: #fff;
  }

  .search-box input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  /* Sugestões melhoradas */
  .suggestions-list {
    list-style: none;
    padding: 0;
    margin: 0.5rem 0;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    max-height: 150px;
    overflow-y: auto;
    background: #fff;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 100;
  }

  .suggestions-list li {
    padding: 10px 12px;
    cursor: pointer;
    border-bottom: 1px solid #f1f5f9;
    transition: background-color 0.2s ease;
  }

  .suggestions-list li:hover {
    background: #f8fafc;
  }

  .suggestions-list li:last-child {
    border-bottom: none;
  }

  /* Painel de detalhes melhorado */
  .detail-panel {
    margin-top: 1rem;
    padding: 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    background: #fff;
    overflow-y: auto;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    max-height: calc(100% - 200px); /* Limita altura */
  }

  .detail-panel h2 {
    margin: 0 0 1rem;
    font-size: 1.2rem;
    color: #1e293b;
    font-weight: 600;
  }

  .detail-panel p {
    margin: 0.5rem 0;
    line-height: 1.5;
    color: #475569;
  }

  .detail-panel strong {
    color: #1e293b;
  }

  .detail-panel a {
    color: #667eea;
    text-decoration: none;
    font-weight: 500;
  }

  .detail-panel a:hover {
    text-decoration: underline;
  }

  /* Seção das visualizações maximizada */
  .viz-section {
    flex: 1; /* Ocupa todo o espaço restante */
    display: flex;
    gap: 1rem;
    min-height: 0; /* Permite flexbox funcionar corretamente */
  }

  .viz-wrapper {
    flex: 1;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    padding: 1.2rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
    overflow: hidden; /* Evita conteúdo vazando */
  }

  /* Modal melhorado */
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    backdrop-filter: blur(4px);
  }

  .modal-window {
    position: relative;
    background: #fff;
    padding: 2rem;
    border-radius: 16px;
    width: 90vw;
    height: 85vh;
    max-width: 1200px;
    overflow: auto;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  }

  .modal-window button {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: #f1f5f9;
    border: none;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    font-size: 1.4rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s ease;
  }

  .modal-window button:hover {
    background: #e2e8f0;
  }

  /* Responsividade */
  @media (max-width: 768px) {
    .sidebar {
      width: 50px;
      min-width: 50px;
    }
    
    .map-and-search {
      flex-direction: column;
      gap: 0.5rem;
    }
    
    .map-wrapper {
      flex: none;
      height: 60%;
    }
    
    .search-box {
      flex: none;
      height: 40%;
      min-width: auto;
    }
    
    .viz-section {
      flex-direction: column;
    }
  }
</style>