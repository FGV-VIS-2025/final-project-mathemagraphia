<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  let svgEl;
  let dadosBiografias = {};
  let nomesMatematicos = []; 
  let grafo = { nodes: [], links: [] };
  let raiz = '';
  let profundidade = 1;

  function extrairCitados(biografia, candidatos) {
    return candidatos.filter(nome =>
      new RegExp(`\\b${nome}\\b`, 'i').test(biografia)
    );
  }

  function construirGrafo(raiz, n) {
    const nodesMap = new Map();
    const visitados = new Set();
    let fronteira = [raiz];

    for (let nivel = 0; nivel < n; nivel++) {
      const novaFronteira = [];
      for (const nome of fronteira) {
        if (!dadosBiografias[nome] || visitados.has(nome)) continue;
        visitados.add(nome);
        const bio = dadosBiografias[nome];
        nodesMap.set(nome, bio);

        const citados = extrairCitados(bio.biografia, nomesMatematicos);
        bio.citados = citados;

        for (const citado of citados) {
          if (!visitados.has(citado)) novaFronteira.push(citado);
        }
      }
      fronteira = novaFronteira;
    }

    const nodes = [...nodesMap.keys()].map(id => ({ id }));
    const links = [];
    for (const [source, bio] of nodesMap.entries()) {
      for (const target of bio.citados || []) {
        if (nodesMap.has(target)) {
          links.push({ source, target });
        }
      }
    }

    grafo = { nodes, links };
    drawGraph();
  }

  function drawGraph() {
    const svg = d3.select(svgEl);
    svg.selectAll('*').remove();

    const width = svgEl.clientWidth;
    const height = svgEl.clientHeight;

    const simulation = d3.forceSimulation(grafo.nodes)
      .force('link', d3.forceLink(grafo.links).id(d => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg.append('g')
      .selectAll('line')
      .data(grafo.links)
      .enter().append('line')
      .attr('stroke', '#999');

    const node = svg.append('g')
      .selectAll('circle')
      .data(grafo.nodes)
      .enter().append('circle')
      .attr('r', 8)
      .attr('fill', '#69b3a2')
      .call(drag(simulation));

    const label = svg.append('g')
      .selectAll('text')
      .data(grafo.nodes)
      .enter().append('text')
      .text(d => d.id)
      .attr('font-size', '0.75rem')
      .attr('dx', 10)
      .attr('dy', 3);

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x).attr('cy', d => d.y);

      label
        .attr('x', d => d.x).attr('y', d => d.y);
    });

    function drag(simulation) {
      return d3.drag()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        });
    }
  }

  onMount(async () => {
    const index = await fetch('biografias_json/index.json').then(r => r.json());
    nomesMatematicos = index;

    for (const nome of nomesMatematicos) {
      const dados = await fetch(`biografias_json/${nome}.json`).then(r => r.json());
      dadosBiografias[nome] = dados;
    }

    raiz = nomesMatematicos[0];
    construirGrafo(raiz, profundidade);
  });

  $: if (raiz && profundidade) {
    construirGrafo(raiz, profundidade);
  }
</script>

<style>
  svg {
    width: 100%;
    height: 80vh;
    border: 1px solid #ccc;
  }
</style>

<h2>Grafo de Distâncias entre Matemáticos</h2>

<label>
  Matemático de origem:
  <select bind:value={raiz}>
    {#each nomesMatematicos as nome}
      <option value={nome}>{nome}</option>
    {/each}
  </select>
</label>

<label>
  Profundidade: {profundidade}
  <input type="range" min="1" max="4" bind:value={profundidade} />
</label>

<svg bind:this={svgEl}></svg>
