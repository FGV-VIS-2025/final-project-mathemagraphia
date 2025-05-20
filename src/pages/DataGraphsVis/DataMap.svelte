<script lang="ts">
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import * as topojson from 'topojson-client';
  
  let svgEl: SVGSVGElement;

  const MAP_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';
  const DATA_URL = "data/biografias_com_coords.json";

onMount(async () => {
  const width = 1000;
  const height = 600;

  console.log("🔧 Inicializando mapa...");

  const svg = d3.select(svgEl)
    .attr('width', width)
    .attr('height', height);

  const projection = d3.geoNaturalEarth1()
    .scale(160)
    .translate([width / 2, height / 2]);

  const path = d3.geoPath().projection(projection);

  // Carrega mapa
  const world = await d3.json(MAP_URL);
  console.log("🌍 Mapa carregado:", world);

  const countries = topojson.feature(world, world.objects.countries).features;

  svg.append('g')
    .selectAll('path')
    .data(countries)
    .join('path')
    .attr('d', path)
    .attr('fill', '#eee')
    .attr('stroke', '#999')
    .attr('stroke-width', 0.5);

  // Carrega dados das biografias
  const raw = await d3.json(DATA_URL);
  console.log("📦 Biografias carregadas:", raw.length);

  const pontos = raw.flatMap((d: any) => {
    const result = [];
    if (d.lat_nasc && d.lon_nasc) {
      result.push({
        ...d,
        tipo: 'nascimento',
        coords: [d.lon_nasc, d.lat_nasc]
      });
    }
    if (d.lat_morte && d.lon_morte) {
      result.push({
        ...d,
        tipo: 'morte',
        coords: [d.lon_morte, d.lat_morte]
      });
    }
    return result;
  });

  console.log("📍 Pontos a desenhar:", pontos.length, pontos.slice(0, 5));

  const color = d3.scaleOrdinal()
    .domain(['nascimento', 'morte'])
    .range(['steelblue', 'crimson']);

  svg.append('g')
    .selectAll('circle')
    .data(pontos)
    .join('circle')
    .attr('cx', d => {
      const pos = projection(d.coords);
      if (!pos) console.warn("⚠️ Ponto fora da projeção:", d);
      return pos ? pos[0] : 0;
    })
    .attr('cy', d => {
      const pos = projection(d.coords);
      return pos ? pos[1] : 0;
    })
    .attr('r', 3)
    .attr('fill', d => color(d.tipo))
    .attr('opacity', 0.7);
});

</script>

<svg bind:this={svgEl}></svg>

<style>
  svg {
    width: 100%;
    height: auto;
    background-color: #f9f9f9;
  }

  :global(a) {
    color: steelblue;
    text-decoration: underline;
  }
</style>
