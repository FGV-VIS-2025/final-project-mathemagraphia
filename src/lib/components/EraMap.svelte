<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import * as topojson from 'topojson-client';

  const MAP_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';
  const DATA_URL = 'data/mac_tutor_com_coords.json';

  let mapSvg;
  let projection, path;
  let allPoints = [], citedMathematicians = [], selectedPoint = null;
  let landFeatures = { type: "FeatureCollection", features: [] };

  let searchTerm = '', suggestions = [], showSuggestions = false;

  function extrairAno(dataStr) {
    const bc = dataStr?.match(/(\d+)\s*BC/i);
    if (bc) return -parseInt(bc[1]);
    const y = dataStr?.match(/(\d{3,4})/);
    return y ? +y[1] : null;
  }

  function formatYear(y) {
    return y < 0 ? `${-y} a.C.` : `${y}`;
  }

  function slugify(name) {
    return name.toLowerCase()
      .normalize('NFD').replace(/\p{Diacritic}/gu, '')
      .replace(/\s+/g, '-').replace(/[^\w-]/g, '');
  }

  async function choosePoint(d) {
    selectedPoint = d;
    citedMathematicians = [];
    try {
      const res = await fetch(`MacTutorData/${slugify(d.nome_curto)}.json`);
      if (res.ok) {
        const detail = await res.json();
        selectedPoint = { ...selectedPoint, ...detail };
        if (detail.matematicos_citados_na_biografia) {
          citedMathematicians = findCitedMathematicians(detail.matematicos_citados_na_biografia);
        }
      }
    } catch (e) { console.error(e); }
    drawMap();
  }

  function findCitedMathematicians(names) {
    if (!Array.isArray(names)) return [];
    const norm = names.map(n => n.toLowerCase());
    return allPoints.filter(p => norm.some(n =>
      p.nome_curto.toLowerCase().includes(n) ||
      p.nome_completo.toLowerCase().includes(n)
    ));
  }

  function onSearch() {
    const term = searchTerm.trim().toLowerCase();
    suggestions = allPoints.filter(p =>
      p.nome_curto.toLowerCase().includes(term) ||
      p.nome_completo.toLowerCase().includes(term)
    ).slice(0, 8);
  }

  function drawMap() {
    const svg = d3.select(mapSvg);
    svg.selectAll('*').remove();

    svg.attr('viewBox', [0, 0, 800, 450]);

    svg.append("path")
      .datum(landFeatures)
      .attr("fill", "#e2e8f0")
      .attr("stroke", "#888")
      .attr("d", path);

    svg.append("g")
      .selectAll("circle")
      .data(allPoints)
      .join("circle")
        .attr("r", d => d === selectedPoint ? 5 : citedMathematicians.includes(d) ? 4 : 3)
        .attr("fill", d => d === selectedPoint ? "orange" : citedMathematicians.includes(d) ? "#4ade80" : "crimson")
        .attr("stroke", "#000")
        .attr("stroke-width", 0.5)
        .attr("cx", d => projection(d.coords)[0])
        .attr("cy", d => projection(d.coords)[1])
        .style("cursor", "pointer")
        .on("click", (e, d) => choosePoint(d));
  }

  onMount(async () => {
    const world = await d3.json(MAP_URL);
    const countries = topojson.feature(world, world.objects.countries);
    landFeatures = countries;

    const raw = await d3.json(DATA_URL);
    allPoints = raw.map(d => {
      const y = extrairAno(d.data_nascimento);
      const lat = parseFloat(d.lat_nasc);
      const lon = parseFloat(d.lon_nasc);
      if (y == null || isNaN(lat) || isNaN(lon)) return null;
      return { ...d, coords: [lon, lat], birthYear: y };
    }).filter(Boolean);

    projection = d3.geoMercator()
      .scale(300)
      .center([0, 20])
      .translate([800 / 2, 450 / 2]);

    path = d3.geoPath(projection);
    drawMap();
  });
</script>

<style>
  .map-section {
    padding: 2rem;
    background: #f9fafb;
  }
  .map-and-search {
    display: flex;
    gap: 1rem;
  }
  .map-wrapper {
    flex: 4;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
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
    margin-bottom: 0.5rem;
  }
  .suggestions-list li {
    cursor: pointer;
    padding: 0.4rem;
    border-bottom: 1px solid #eee;
  }
  .info-container {
    background: white;
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 1rem;
    font-size: 0.9rem;
  }
  .cited-tag {
    background: #4ade80;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    margin-right: 0.3rem;
    cursor: pointer;
    font-size: 0.8rem;
  }
</style>

<section class="map-section">
  <div class="map-and-search">
    <div class="map-wrapper">
      <svg bind:this={mapSvg} width="800" height="450"></svg>
    </div>
    <div class="search-box">
      <input type="text" placeholder="Buscar matemático…"
             bind:value={searchTerm}
             on:input={() => { onSearch(); showSuggestions = true }}
             on:blur={() => setTimeout(() => showSuggestions = false, 100)} />
      {#if showSuggestions && suggestions.length}
        <ul class="suggestions-list">
          {#each suggestions as s}
            <li on:click={() => choosePoint(s)}>{s.nome_curto}</li>
          {/each}
        </ul>
      {/if}

      <div class="info-container">
        {#if selectedPoint}
          <h3>{selectedPoint.nome_completo}</h3>
          <p><strong>Nascimento:</strong> {selectedPoint.data_nascimento} — {selectedPoint.local_nascimento}</p>
          {#if selectedPoint.data_morte}
            <p><strong>Morte:</strong> {selectedPoint.data_morte} — {selectedPoint.local_morte}</p>
          {/if}
          <p><strong>Resumo:</strong> {selectedPoint.summary}</p>
          <p><strong>Biografia:</strong><br>{selectedPoint.biografia}</p>
          <p><a href={selectedPoint.link} target="_blank">Mais sobre {selectedPoint.nome_curto}</a></p>
          {#if citedMathematicians.length > 0}
            <h4>Citados na biografia:</h4>
            <div>
              {#each citedMathematicians as c}
                <span class="cited-tag" on:click={() => choosePoint(c)}>{c.nome_curto}</span>
              {/each}
            </div>
          {/if}
        {:else}
          <p class="info-placeholder">Clique em um ponto no mapa para ver detalhes.</p>
        {/if}
      </div>
    </div>
  </div>
</section>
