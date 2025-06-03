<script>
  import { onMount } from "svelte";
  import * as d3 from "d3";
  import * as topojson from "topojson-client";

  // Dimensões fixas do SVG
  const width = 800;
  const height = 450;

  let svgEl;
  // URLs dos dados
  const MAP_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";
  const DATA_URL = "public/data/biografias_coords.json";

  let projection;
  let path;
  let landFeatures;
  let allPoints = [];      // todos os pontos com birthYear
  let filteredPoints = []; // só os que satisfazem o filtro de ano
  let fixedTooltipData = null;
  let hoveredData = null;
  // Slider: vai de minYear até currentYear
  let minYear = 0;
  const currentYear = new Date().getFullYear();
  let selectedYear = currentYear;
  let zoomGroup; // o grupo <g> onde aplicamos zoom
  let currentTransform = d3.zoomIdentity;
  let scaleFactor = 1;
  let searchTerm = "";
  let suggestions = [];
  let showSuggestions = false;

  // Formata ano (ex: -280 => "280 BC", 1893 => "1893")
  function formatYear(y) {
    if (y < 0) return `${-y} BC`;
    return `${y}`;
  }

  function drawLand() {
    zoomGroup.append("g")
      .selectAll("path")
      .data(landFeatures.features)
      .join("path")
      .attr("d", path)
      .attr("fill", "#e0e0e0")
      .attr("stroke", "#888")
      .attr("stroke-width", 0.4);
  }

  function drawPoints() {
    zoomGroup.selectAll("circle.point").remove();

    zoomGroup.append("g")
      .selectAll("circle")
      .data(filteredPoints)
      .join("circle")
      .attr("class", "point")
      .attr("cx", d => projection(d.coords)[0])
      .attr("cy", d => projection(d.coords)[1])
      .attr("r", 3 / scaleFactor) // raio ajustado
      .attr("fill", "crimson")
      .attr("stroke", "#000")
      .attr("stroke-width", 0.5 / scaleFactor) // <-- borda ajustada
      .on("mouseover", (event, d) => {
        if (!fixedTooltipData) hoveredData = d;
      })
      .on("mouseout", () => {
        if (!fixedTooltipData) hoveredData = null;
      })
      .on("click", (event, d) => {
        if (fixedTooltipData && fixedTooltipData.link === d.link) {
          fixedTooltipData = null;
          hoveredData = null;
        } else {
          fixedTooltipData = d;
          hoveredData = d;
        }
      });
  }

  function updateFiltered() {
    filteredPoints = allPoints.filter(d => {
      const nome = d.nome_curto.toLowerCase() + " " + d.nome_completo.toLowerCase();
      return (
        d.birthYear <= selectedYear &&
        nome.includes(searchTerm.toLowerCase())
      );
    });

    drawPoints();
  }
  function onSearchInput() {
    const term = searchTerm.trim().toLowerCase();

    suggestions = allPoints.filter(p =>
      p.nome_curto.toLowerCase().includes(term) ||
      p.nome_completo.toLowerCase().includes(term)
    ).slice(0, 10); // limite de sugestões

    updateFiltered();
  }

  function selectSuggestion(person) {
    hoveredData = person;
    fixedTooltipData = person;
    searchTerm = person.nome_curto;
    suggestions = [];
    showSuggestions = false;

    // Centraliza o ponto no mapa (animando a projeção)
    const [x, y] = projection(person.coords);
    svgEl.scrollIntoView({ behavior: "smooth" });
  }

  function drawMap() {
    const svg = d3.select(svgEl);
    svg.selectAll("*").remove();
    zoomGroup = svg.append("g").attr("class", "zoom-group");
    zoomGroup.attr("transform", currentTransform);

    // Fundo
    svg.append("rect")
      .attr("width", width)
      .attr("height", height)
      .attr("fill", "#f0f0f0")
      .lower()  // Garante que fique atrás de tudo
      .on("click", () => {
        fixedTooltipData = null;
        hoveredData = null;
      });

    if (!landFeatures || !landFeatures.features.length) {
      svg.append("text")
        .attr("x", width / 2)
        .attr("y", height / 2)
        .attr("text-anchor", "middle")
        .attr("fill", "red")
        .style("font-size", "16px")
        .text("Erro: não foram carregadas features de país.");
      return;
    }

    drawLand();
    updateFiltered();
  }

onMount(async () => {
  // Configura projeção
  projection = d3.geoNaturalEarth1()
    .scale(150)
    .translate([width / 2, height / 2]);
  path = d3.geoPath(projection);

  // 1) Carrega TopoJSON
  try {
    const world = await d3.json(MAP_URL);
    landFeatures = topojson.feature(world, world.objects.countries);
  } catch {
    landFeatures = { features: [] };
  }

  // 2) Carrega dados de biografias
  try {
    const raw = await d3.json(DATA_URL);
    allPoints = raw
      .map(d => {
        let year = null;
        const yn = (d.ano_nascimento || "").trim();
        if (yn.endsWith("BC")) {
          const n = parseInt(yn.replace("BC", "").trim());
          year = isNaN(n) ? null : -n;
        } else {
          const n = parseInt(yn);
          year = isNaN(n) ? null : n;
        }

        if (
          d.coords_nascimento &&
          typeof d.coords_nascimento.lat === "number" &&
          typeof d.coords_nascimento.lon === "number" &&
          year !== null
        ) {
          return {
            nome_completo: d.nome_completo,
            nome_curto: d.nome_curto || d.nome_completo,
            pais_nascimento: d.lugar_nascimento || "Desconhecido",
            biografia: d.biografia || "",
            link: d.link,
            coords: [d.coords_nascimento.lon, d.coords_nascimento.lat],
            birthYear: year
          };
        }
        return null;
      })
      .filter(d => d !== null);

    if (allPoints.length) {
      minYear = Math.min(...allPoints.map(d => d.birthYear));
      selectedYear = currentYear;
    }
  } catch {
    allPoints = [];
  }

  // 3) Desenha mapa e pontos iniciais
  drawMap();

  // 4) Comportamento de zoom
  const zoom = d3.zoom()
    .scaleExtent([0.5, 8])
    .on("zoom", (event) => {
      currentTransform = event.transform;
      scaleFactor = currentTransform.k;

      // Aplica o zoom ao grupo todo
      zoomGroup.attr("transform", currentTransform);

      // Atualiza o raio dos círculos proporcionalmente ao zoom
      zoomGroup.selectAll("circle.point")
        .attr("r", 3 / scaleFactor)
        .attr("stroke-width", 0.5 / scaleFactor); // <-- ajusta borda dinamicamente
        // <-- ajusta o tamanho visual
    });

  d3.select(svgEl).call(zoom);

});

</script>

<style>.map-layout {
  display: flex;
  flex-direction: row;
  gap: 1.5rem;
  justify-content: center;
  padding: 1rem;
  flex-wrap: wrap;
}

.map-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 1rem;
}

svg {
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.info-panel {
  width: 280px;
  min-height: 300px;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 1rem;
  font-family: sans-serif;
  font-size: 0.95rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.info-card h2 {
  margin: 0;
  font-size: 1.2rem;
}

.info-card p {
  margin: 0.3rem 0;
}

.info-card.muted {
  color: #666;
  font-style: italic;
}

.bio-scroll {
  max-height: 320px;
  overflow-y: auto;
  margin-top: 0.5rem;
  padding-right: 6px;
  white-space: pre-wrap;
  font-size: 0.85rem;
  line-height: 1.5;
}

.bio-scroll::-webkit-scrollbar {
  width: 6px;
}
.bio-scroll::-webkit-scrollbar-thumb {
  background-color: #bbb;
  border-radius: 3px;
}

.timeline-container {
  margin-top: 1rem;
  width: 100%;
  text-align: center;
}

input[type="range"] {
  width: 100%;
  max-width: 600px;
}

.year-label {
  margin-top: 0.5rem;
  font-weight: bold;
}

.search-container {
  position: relative;
  margin: 1rem auto;
  width: 80%;
  max-width: 500px;
  text-align: center;
}

.search-container input {
  width: 100%;
  padding: 10px 12px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.suggestions-list {
  position: absolute;
  top: 0;
  left: 100%;
  margin-left: 0.5rem;
  background: white;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  max-height: 300px;
  overflow-y: auto;
  width: 250px;
  z-index: 1000;
  list-style: none;
  padding: 0;
}

.suggestions-list li {
  padding: 8px 12px;
  cursor: pointer;
}

.suggestions-list li:hover {
  background: #f0f0f0;
}

:global(a) {
  color: steelblue;
  text-decoration: underline;
}

</style>

<!-- Barra de busca centralizada -->
<div class="search-container">
  <input
    type="text"
    placeholder="Buscar por nome..."
    bind:value={searchTerm}
    on:input={onSearchInput}
    on:focus={() => showSuggestions = true}
    on:blur={() => setTimeout(() => showSuggestions = false, 100)}  
  />

  {#if showSuggestions && suggestions.length > 0}
    <ul class="suggestions-list">
      {#each suggestions as s}
        <li on:click={() => selectSuggestion(s)}>{s.nome_curto}</li>
      {/each}
    </ul>
  {/if}
</div>

<!-- Painel lateral e Mapa -->
<div class="map-layout">
  <!-- Lateral esquerda: painel -->
  <div class="info-panel">
    {#if hoveredData}
      <div class="info-card">
        <h2>{hoveredData.nome_curto}</h2>
        <p><strong>Nascimento:</strong> {formatYear(hoveredData.birthYear)}</p>
        <p><strong>Local:</strong> {hoveredData.pais_nascimento}</p>

        <div class="bio-scroll">
          <pre>{hoveredData.biografia}</pre>
        </div>

        <p style="margin-top: 0.5rem;">
          <a href={hoveredData.link} target="_blank" rel="noopener">
            Ver biografia completa
          </a>
        </p>
      </div>
    {:else}
      <div class="info-card muted">
        Passe o mouse sobre um ponto
      </div>
    {/if}
  </div>

  <!-- Centro: Mapa + Slider -->
  <div class="map-wrapper">
    <svg bind:this={svgEl} width={width} height={height}></svg>

    <div class="timeline-container">
      <input
        type="range"
        min={minYear}
        max={currentYear}
        bind:value={selectedYear}
        on:input={updateFiltered}
      />
      <div class="year-label">Ano selecionado: {formatYear(selectedYear)}</div>
      <div class="year-range">
        <small>{formatYear(minYear)} → {formatYear(currentYear)}</small>
      </div>
    </div>
  </div>
</div>
