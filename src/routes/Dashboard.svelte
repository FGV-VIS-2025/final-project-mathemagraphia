<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import * as topojson from 'topojson-client';

  import Timeline from '../components/Timeline.svelte';
  import VizContainer from '../components/VizContainer.svelte';
  import AncientEra from '../components/AncientEra.svelte';
  import FixedBar from '../components/FixedBar.svelte';

  let mapContainer;
  let allPoints = [], filteredPoints = [];
  let landFeatures = { type: 'FeatureCollection', features: [] };
  let selectedPoint = null;
  let detailData = null;
  let citedMathematicians = []; // Array para armazenar matemáticos citados

  let searchTerm = '';
  let suggestions = [];
  let showSuggestions = false;

  let svg, projection, path, zoomGroup;
  let currentTransform = d3.zoomIdentity;
  let scaleFactor = 1;

  // [{start, end}]
  let currentEra = null;

  let expanded = null;
  const expand = id => expanded = id;
  const closeModal = () => expanded = null;

  function parseYear(str) {
    if (!str) return null;
    const s = str.trim();
    const bc = s.match(/(\d+)\s*BC$/i);
    if (bc) return -+bc[1];
    const fy = s.match(/(\d{4})/);
    if (fy) return +fy[1];
    const any = s.match(/(\d+)/);
    if (any) return +any[1];
    return null;
  }

  function slugify(name) {
    return name.toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, '-').replace(/[^\w-]/g, '');
  }

  // Cache para matemáticos citados
  let citedCache = new Map();

  // Função otimizada para encontrar matemáticos citados
  function findCitedMathematicians(citedNames) {
    if (!citedNames || !Array.isArray(citedNames)) return [];
    
    const cacheKey = citedNames.join('|');
    if (citedCache.has(cacheKey)) {
      return citedCache.get(cacheKey);
    }
    
    const currentPoints = filteredPoints.length ? filteredPoints : allPoints;
    const cited = new Set(); // Usa Set para evitar duplicatas automaticamente
    
    // Pré-processa nomes para busca mais eficiente
    const normalizedCitedNames = citedNames.map(name => name.toLowerCase().trim());
    
    currentPoints.forEach(point => {
      const pointName = point.nome_curto.toLowerCase();
      const pointFullName = point.nome_completo.toLowerCase();
      const lastName = pointFullName.split(' ').pop();
      
      for (const searchName of normalizedCitedNames) {
        if (pointName.includes(searchName) || 
            searchName.includes(pointName) ||
            pointFullName.includes(searchName) ||
            searchName.includes(lastName)) {
          cited.add(point);
          break; // Para na primeira correspondência
        }
      }
    });
    
    const result = Array.from(cited);
    citedCache.set(cacheKey, result);
    return result;
  }

  async function loadData() {
    const base = import.meta.env.BASE_URL;
    const [world, raw] = await Promise.all([
      d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json'),
      d3.json(`${base}data/mac_tutor_com_coords.json`)
    ]);
    const worldFeatures = topojson.feature(world, world.objects.countries);
    landFeatures = { type: 'FeatureCollection', features: worldFeatures.features };

    allPoints = raw.map(d => {
      const year = parseYear(d.data_nascimento);
      if (year != null && typeof d.lat_nasc === 'number' && typeof d.lon_nasc === 'number') {
        return { ...d, coords: [d.lon_nasc, d.lat_nasc], birthYear: year };
      }
      return null;
    }).filter(d => d);
  }

  function initMap() {
    const { width, height } = mapContainer.getBoundingClientRect();
    svg = d3.select(mapContainer).append('svg').attr('width', width).attr('height', height);
    projection = d3.geoNaturalEarth1().scale(width/6.5).translate([width/2, height/2]);
    path = d3.geoPath(projection);
    const zoom = d3.zoom().scaleExtent([0.5,8]).on('zoom', e => {
      currentTransform = e.transform;
      scaleFactor = e.transform.k;
      zoomGroup.attr('transform', currentTransform);
      zoomGroup.selectAll('circle')
        .attr('r', d => getCircleRadius(d))
        .attr('stroke-width', 0.5/scaleFactor);
    });
    svg.call(zoom);
  }

  // Função para determinar o raio do círculo baseado no status
  function getCircleRadius(d) {
    if (d === selectedPoint) return 5/scaleFactor; // Ponto selecionado maior
    if (citedMathematicians.includes(d)) return 4/scaleFactor; // Citados médios
    return 3/scaleFactor; // Outros pontos normais
  }

  // Função para determinar a cor do círculo
  function getCircleColor(d) {
    if (d === selectedPoint) return 'orange'; // Ponto selecionado
    if (citedMathematicians.includes(d)) return '#4ade80'; // Citados em verde
    return 'crimson'; // Outros pontos
  }

  // Função para determinar a opacidade
  function getCircleOpacity(d) {
    if (!selectedPoint) return 1; // Se nenhum ponto selecionado, todos visíveis
    if (d === selectedPoint || citedMathematicians.includes(d)) return 1; // Selecionado e citados visíveis
    return 0.3; // Outros pontos mais transparentes
  }

  function drawMap() {
    // Evita redesenhar se não há mudanças significativas
    const currentPoints = filteredPoints.length ? filteredPoints : allPoints;
    
    svg.selectAll('*').remove();
    zoomGroup = svg.append('g').attr('transform', currentTransform);
    
    // Fundo clicável para deselecionar
    svg.append('rect').attr('width','100%').attr('height','100%')
      .attr('fill','#eef').lower().on('click', clearSelection);
    
    // Desenha os países (só uma vez)
    zoomGroup.append('g').selectAll('path')
      .data(landFeatures.features).join('path')
      .attr('d', path).attr('fill','#ddd').attr('stroke','#999');
    
    // Desenha linhas de conexão primeiro (atrás dos círculos)
    drawConnections();
    
    // Desenha os pontos dos matemáticos
    drawPoints(currentPoints);
  }

  function clearSelection() {
    selectedPoint = null; 
    detailData = null; 
    citedMathematicians = [];
    drawMap();
  }

  function drawConnections() {
    if (selectedPoint && citedMathematicians.length > 0) {
      const selectedCoords = projection(selectedPoint.coords);
      
      zoomGroup.append('g').selectAll('line')
        .data(citedMathematicians)
        .join('line')
        .attr('x1', selectedCoords[0])
        .attr('y1', selectedCoords[1])
        .attr('x2', d => projection(d.coords)[0])
        .attr('y2', d => projection(d.coords)[1])
        .attr('stroke', '#4ade80')
        .attr('stroke-width', 1.5/scaleFactor)
        .attr('stroke-dasharray', '5,5')
        .attr('opacity', 0.7);
    }
  }

  function drawPoints(currentPoints) {
    const circles = zoomGroup.append('g').selectAll('circle')
      .data(currentPoints)
      .join('circle')
      .attr('cx', d => projection(d.coords)[0])
      .attr('cy', d => projection(d.coords)[1])
      .attr('r', d => getCircleRadius(d))
      .attr('fill', d => getCircleColor(d))
      .attr('opacity', d => getCircleOpacity(d))
      .attr('stroke', d => getCircleStroke(d))
      .attr('stroke-width', d => getCircleStrokeWidth(d))
      .style('cursor','pointer')
      .on('click', handlePointClick)
      .on('mouseover', handleMouseOver)
      .on('mouseout', handleMouseOut);
  }

  function getCircleStroke(d) {
    if (d === selectedPoint) return '#000';
    if (citedMathematicians.includes(d)) return '#16a34a';
    return '#000';
  }

  function getCircleStrokeWidth(d) {
    return d === selectedPoint ? 2/scaleFactor : 0.5/scaleFactor;
  }

  function handlePointClick(e, d) {
    e.stopPropagation(); 
    choosePoint(d);
  }

  function handleMouseOver(e, d) {
    d3.select(this).attr('stroke-width', 2/scaleFactor);
  }

  function handleMouseOut(e, d) {
    d3.select(this).attr('stroke-width', getCircleStrokeWidth(d));
  }

  async function choosePoint(d) {
    selectedPoint = d; 
    detailData = null;
    citedMathematicians = []; // Reset das citações
    
    const slug = slugify(d.nome_curto);
    try { 
      const res = await fetch(`${import.meta.env.BASE_URL}MacTutorData/${slug}.json`);
      if (res.ok) {
        detailData = await res.json();
        
        // Encontra matemáticos citados na biografia
        if (detailData.matematicos_citados_na_biografia) {
          citedMathematicians = findCitedMathematicians(detailData.matematicos_citados_na_biografia);
          console.log(`Matemáticos citados para ${d.nome_curto}:`, citedMathematicians.map(m => m.nome_curto));
        }
      }
    } catch (error) {
      console.error('Erro ao carregar dados do matemático:', error);
    }
    
    drawMap();
  }

  function onSearch() {
    const term = searchTerm.trim().toLowerCase();
    suggestions = allPoints.filter(p =>
      p.nome_curto.toLowerCase().includes(term) ||
      p.nome_completo.toLowerCase().includes(term)
    ).slice(0,8);
  }

  function filterByEra([start,end]) {
    currentEra = [start,end];
    filteredPoints = allPoints.filter(p => p.birthYear >= start && p.birthYear < end);
    
    // Limpa seleção se o ponto selecionado não está na nova era
    if (selectedPoint && !filteredPoints.includes(selectedPoint)) {
      selectedPoint = null;
      detailData = null;
      citedMathematicians = [];
    }
    
    drawMap();
  }

  onMount(async () => {
    await loadData(); 
    initMap(); 
    drawMap();
    window.addEventListener('resize', () => { 
      d3.select(mapContainer).select('svg').remove(); 
      initMap(); 
      drawMap(); 
    });
  });
</script>

<div class="dashboard-layout">
  <aside class="sidebar">
    <Timeline on:selectEra={({ detail }) => filterByEra(detail)} />
  </aside>
  <main class="main-content">
    <section class="map-section"> 
      <div class="map-and-search">
        <div class="map-wrapper" bind:this={mapContainer}></div>
        <div class="search-box">
          <input type="text" placeholder="Buscar matemático…"
            bind:value={searchTerm}
            on:input={() => { onSearch(); showSuggestions = true }}
            on:blur={() => setTimeout(()=>showSuggestions=false,100)} />
          {#if showSuggestions && suggestions.length}
            <ul class="suggestions-list">
              {#each suggestions as s}<li on:click={()=>choosePoint(s)}>{s.nome_curto}</li>{/each}
            </ul>
          {/if}
          <div class="info-container">
            {#if detailData}
              <h3>{detailData.nome_curto}</h3>
              <p><strong>Nasceu:</strong> {detailData.data_nascimento}</p>
              <p><strong>Local:</strong> {detailData.local_nascimento}</p>
              <p><strong>Morreu:</strong> {detailData.data_morte}</p>
              <p><strong>Local:</strong> {detailData.local_morte}</p>
              <p>{detailData.summary}</p>
              
              {#if citedMathematicians.length > 0}
                <div class="cited-mathematicians">
                  <h4>Matemáticos citados na biografia:</h4>
                  <div class="cited-list">
                    {#each citedMathematicians as cited}
                      <span class="cited-tag" on:click={() => choosePoint(cited)}>
                        {cited.nome_curto}
                      </span>
                    {/each}
                  </div>
                </div>
              {/if}
              
              <p><a href={detailData.link} target="_blank">Biografia completa</a></p>
            {:else}
              <p class="info-placeholder">Clique em um ponto no mapa para ver detalhes aqui.</p>
            {/if}
          </div>
        </div>
      </div>
    </section>

    <section class="viz-section">
      <div class="viz-wrapper">
        <VizContainer
          id={1}
          {currentEra}
          points={filteredPoints}
          on:expand={()=>expand(1)} />
      </div>

      {#if currentEra && currentEra[0] < 0}
        <div class="viz-wrapper">
          <button class="expand-btn" on:click={()=>expand(2)}>⤢</button>
          <AncientEra />
        </div>
      {:else}
        <div class="viz-wrapper">
          <VizContainer id={2} />
        </div>
      {/if}
    </section>
  </main>
</div>

<FixedBar />

{#if expanded}
  <div class="modal-overlay" on:click={closeModal}>
    <div class="modal-window" on:click|stopPropagation>
      <button class="close-btn" on:click={closeModal}>×</button>
      {#if expanded === 1}
        <VizContainer id={1} {currentEra} points={filteredPoints} />
      {:else if expanded === 2}
        <AncientEra />
      {/if}
    </div>
  </div>
{/if}

<style>
  /* Estilos existentes mantidos */
  .viz-wrapper { position: relative; height: 100%; padding: 0; }
  .expand-btn {
    position: absolute; top: 8px; right: 8px;
    background: rgba(255,255,255,0.8); border: none; border-radius: 4px;
    cursor: pointer; font-size: 1.2rem; z-index: 10;
  }
  .modal-window { display: flex; flex-direction: column; height: 85vh; width: 90vw; max-width: 1200px; }
  .modal-window :global(.container) { flex: 1; height: auto; }

  :global(html, body) {
    margin: 0;
    padding: 0;
    height: 100%;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
      sans-serif;
  }

  .dashboard-layout {
    display: flex;
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    position: fixed;
    top: 0;
    left: 0;
  }

  .sidebar {
    width: 60px;
    min-width: 60px;
    background: transparent;
    border-right: 2px solid rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
    z-index: 10;
  }

  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 0.8rem;
    box-sizing: border-box;
    background: #f8fafc;
    overflow: hidden;
  }

  .map-section {
    flex: 0 0 45%;
    margin-bottom: 0.8rem;
    min-height: 300px;
  }

  .map-and-search {
    display: flex;
    height: 100%;
    gap: 1rem;
  }

  .map-wrapper {
    flex: 4;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: #fff;
  }

  .search-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 250px;
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

  .info-container {
    margin-top: 1rem;
    padding: 1rem;
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    min-height: 150px;
    max-height: 300px;
    overflow-y: auto;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }

  .info-container h3 {
    margin: 0 0 0.5rem;
    font-size: 1.1rem;
    color: #1e293b;
  }

  .info-container p {
    margin: 0.4rem 0;
    line-height: 1.4;
    color: #475569;
  }

  .info-container a {
    color: #667eea;
    text-decoration: none;
  }

  .info-container a:hover {
    text-decoration: underline;
  }

  .info-placeholder {
    color: #94a3b8;
    font-style: italic;
  }

  /* Novos estilos para matemáticos citados */
  .cited-mathematicians {
    margin: 1rem 0;
    padding: 0.75rem;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 6px;
  }

  .cited-mathematicians h4 {
    margin: 0 0 0.5rem;
    font-size: 0.9rem;
    color: #166534;
    font-weight: 600;
  }

  .cited-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .cited-tag {
    background: #4ade80;
    color: #fff;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .cited-tag:hover {
    background: #16a34a;
    transform: translateY(-1px);
  }

  .viz-section {
    flex: 1;
    display: flex;
    gap: 1rem;
    min-height: 0;
  }

  .viz-wrapper {
    flex: 1;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    padding: 1.2rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
    overflow: hidden;
    position: relative;
    overflow: visible;
  }

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

  .graph {
    flex: 1;
    position: relative;
    background: #fff;
    overflow: visible;
  }

  svg {
    width: 100%;
    height: 100%;
    overflow: visible;
  }
</style>