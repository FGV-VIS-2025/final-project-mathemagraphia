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
  const citationDepth = 1;

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
          citedMathematicians = getCitations(detail.matematicos_citados_na_biografia, citationDepth);
        }
      }
    } catch (e) { console.error(e); }
    drawMap();
  }

  function getCitations(citedNames, depth) {
    if (!Array.isArray(citedNames) || depth <= 0) return [];
    const norm = citedNames.map(n => n.toLowerCase());
    let direct = allPoints.filter(p => norm.some(n =>
      p.nome_curto.toLowerCase().includes(n) ||
      p.nome_completo.toLowerCase().includes(n)
    ));
    let indirect = direct.flatMap(p => getCitations(p.matematicos_citados_na_biografia || [], depth - 1));
    return [...new Set([...direct, ...indirect])];
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

    svg.append("defs").append("marker")
      .attr("id", "arrowhead")
      .attr("viewBox", "-0 -5 10 10")
      .attr("refX", 10)
      .attr("refY", 0)
      .attr("orient", "auto")
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("xoverflow", "visible")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#0ea5e9");

    svg.append("path")
      .datum(landFeatures)
      .attr("fill", "#e0f2fe")
      .attr("stroke", "#94a3b8")
      .attr("d", path);

    // Draw arrows for citations
    if (selectedPoint && citedMathematicians.length > 0) {
      const source = projection(selectedPoint.coords);
      svg.append("g")
        .selectAll("path.link")
        .data(citedMathematicians)
        .join("path")
        .attr("class", "link")
        .attr("d", d => {
          const target = projection(d.coords);
          const dx = target[0] - source[0];
          const dy = target[1] - source[1];
          const dr = Math.sqrt(dx * dx + dy * dy) * 0.7;
          return `M${source[0]},${source[1]} A${dr},${dr} 0 0,1 ${target[0]},${target[1]}`;
        })
        .attr("fill", "none")
        .attr("stroke", "#0ea5e9")
        .attr("stroke-width", 1.5)
        .attr("marker-end", "url(#arrowhead)")
        .attr("opacity", 0.7);
    }

    svg.append("g")
      .selectAll("circle")
      .data(allPoints)
      .join("circle")
        .attr("r", d => d === selectedPoint ? 6 : citedMathematicians.includes(d) ? 4.5 : 3)
        .attr("fill", d => d === selectedPoint ? "#0ea5e9" : citedMathematicians.includes(d) ? "#38bdf8" : "#0284c7")
        .attr("stroke", "#0c4a6e")
        .attr("stroke-width", 0.7)
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
      if (y == null || isNaN(lat) || isNaN(lon) || y >= 0) return null;
      return { ...d, coords: [lon, lat], birthYear: y };
    }).filter(Boolean);

    const lons = allPoints.map(d => d.coords[0]);
    const lats = allPoints.map(d => d.coords[1]);
    const lonCenter = (Math.min(...lons) + Math.max(...lons)) / 2;
    const latCenter = (Math.min(...lats) + Math.max(...lats)) / 2;

    projection = d3.geoMercator()
      .scale(375)
      .center([lonCenter, latCenter])
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
