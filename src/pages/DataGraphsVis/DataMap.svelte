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
      .attr("r", 3)
      .attr("fill", "crimson")
      .attr("stroke", "#000")
      .attr("stroke-width", 0.5)
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
    // Filtra todos os pontos até selectedYear (birthYear <= selectedYear)
    filteredPoints = allPoints.filter(d => d.birthYear <= selectedYear);
    drawPoints();
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
      // Extrai birthYear numérico de raw.ano_nascimento
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

      // Determina ano mínimo entre todos os birthYear
      if (allPoints.length) {
        minYear = Math.min(...allPoints.map(d => d.birthYear));
        selectedYear = currentYear;
      }
    } catch {
      allPoints = [];
    }
    
    const zoom = d3.zoom()
      .scaleExtent([0.5, 8])
      .on("zoom", (event) => {
        currentTransform = event.transform;
        zoomGroup.attr("transform", currentTransform);
      });

    d3.select(svgEl).call(zoom);

    // 3) Desenha mapa e pontos iniciais
    drawMap();
  });
</script>

<style>
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

  #tooltip {
    position: absolute;
    pointer-events: auto;
    background: white;
    padding: 6px 10px;
    border: 1px solid #999;
    border-radius: 4px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    font-size: 0.85rem;
    opacity: 0;
    transition: opacity 0.2s;
    z-index: 10;
    font-family: sans-serif;
  }

  .timeline-container {
    margin-top: 1rem;
    width: 80%;
    text-align: center;
  }

  input[type="range"] {
    width: 100%;
  }

  .year-label {
    margin-top: 0.5rem;
    font-weight: bold;
  }

  :global(a) {
    color: steelblue;
    text-decoration: underline;
  }
.map-container {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
}

.info-panel {
  width: 220px;
  min-height: 200px;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 1rem;
  font-family: sans-serif;
  font-size: 0.9rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.info-card {
  line-height: 1.4;
}

.info-card.muted {
  color: #666;
  font-style: italic;
}

.map-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.bio-scroll {
  max-height: 200px;
  overflow-y: auto;
  margin-top: 0.5rem;
  padding-right: 6px;
  white-space: pre-wrap;
  font-size: 0.75rem;
  line-height: 1.4;
}

.bio-scroll::-webkit-scrollbar {
  width: 6px;
}
.bio-scroll::-webkit-scrollbar-thumb {
  background-color: #ccc;
  border-radius: 3px;
}

</style>

<div class="map-container">
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

