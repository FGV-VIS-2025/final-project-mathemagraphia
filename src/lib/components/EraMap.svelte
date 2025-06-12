<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import * as topojson from 'topojson-client';

  const MAP_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';
  const DATA_URL = 'data/mac_tutor_com_coords.json';

  let mapSvg;
  let projection, path;
  let landFeatures = { type: "FeatureCollection", features: [] };
  let allPoints = [], selected = null, cited = [];

  const width = 800, height = 450;
  let currentDepth = 1;

  function extrairAno(dataStr) {
    const bc = dataStr?.match(/(\d+)\s*BC/i);
    if (bc) return -parseInt(bc[1]);
    const y = dataStr?.match(/(\d{3,4})/);
    return y ? +y[1] : null;
  }

  function formatYear(y) {
    return y < 0 ? `${-y} a.C.` : `${y}`;
  }

  function drawMap() {
    const svg = d3.select(mapSvg);
    svg.selectAll('*').remove();

    svg.attr('viewBox', [0, 0, width, height]);

    svg.append("path")
      .datum(landFeatures)
      .attr("fill", "#e2e8f0")
      .attr("stroke", "#888")
      .attr("d", path);

    svg.append("g")
      .selectAll("circle")
      .data(allPoints)
      .join("circle")
        .attr("r", 3)
        .attr("fill", d => d === selected ? "crimson" : cited.includes(d) ? "gold" : "steelblue")
        .attr("stroke", "#000")
        .attr("stroke-width", 0.5)
        .attr("cx", d => projection(d.coords)[0])
        .attr("cy", d => projection(d.coords)[1])
        .style("cursor", "pointer")
        .on("click", (e, d) => {
          selected = d;
          cited = getCitations(d, currentDepth);
        });
  }

  function getCitations(base, depth) {
    if (!base?.cites || depth <= 0) return [];
    let direct = allPoints.filter(p => base.cites.includes(p.link));
    return [
      ...direct,
      ...direct.flatMap(p => getCitations(p, depth - 1))
    ];
  }

  onMount(async () => {
    projection = d3.geoMercator()
      .scale(120)
      .center([20, 30])
      .translate([width / 2, height / 2]);

    path = d3.geoPath(projection);

    const world = await d3.json(MAP_URL);
    const countries = topojson.feature(world, world.objects.countries);
    landFeatures = {
      type: "FeatureCollection",
      features: Array.isArray(countries.features) ? countries.features : []
    };

    const raw = await d3.json(DATA_URL);
    allPoints = raw.map(d => {
      const y = extrairAno(d.data_nascimento);
      const lat = parseFloat(d.lat_nasc);
      const lon = parseFloat(d.lon_nasc);
      if (y == null || isNaN(lat) || isNaN(lon) || y >= 0) return null;
      return {
        nome_completo: d.nome_completo,
        birthYear: y,
        coords: [lon, lat],
        link: d.link,
        cites: d.citations || []
      };
    }).filter(Boolean);

    drawMap();
  });
  $: if (selected) drawMap();
</script>

<style>
  .map-section {
    padding: 4rem 1rem;
    background: #f9fafb;
  }

  .map-and-sidebar {
    display: flex;
    flex-direction: row;
    gap: 2rem;
    justify-content: center;
    flex-wrap: wrap;
  }

  svg {
    background: white;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  }

  .sidebar {
    max-width: 300px;
    background: #fff;
    padding: 1rem;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 0.95rem;
    line-height: 1.4;
  }
</style>

<section class="map-section">
  <h2>Influência e Citações entre Matemáticos</h2>
  <div class="map-and-sidebar">
    <svg bind:this={mapSvg} width={width} height={height}></svg>
    <div class="sidebar">
      {#if selected}
        <h3>{selected.nome_completo}</h3>
        <p><em>{formatYear(selected.birthYear)}</em></p>
        <h4>Citações ({cited.length}):</h4>
        <ul>
          {#each cited as c}
            <li>{c.nome_completo} ({formatYear(c.birthYear)})</li>
          {/each}
        </ul>
      {/if}
    </div>
  </div>
</section>
