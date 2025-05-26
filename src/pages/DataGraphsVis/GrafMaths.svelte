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
    
    // Usar Set para evitar links duplicados
    const linkSet = new Set();

    for (const [source, bio] of nodesMap.entries()) {
      for (const target of bio.citados || []) {
        if (nodesMap.has(target)) {
          // Criar identificador único para o link
          const linkId = `${source}->${target}`;
          
          // Só adicionar se não existir
          if (!linkSet.has(linkId)) {
            linkSet.add(linkId);
            links.push({ source, target });
          }
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

    // Marcador de seta cinza
    const defs = svg.append('defs');
    
    defs.append('marker')
      .attr('id', 'seta-cinza')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 15) // Aumentei um pouco para ficar mais afastado do nó
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .attr('markerUnits', 'strokeWidth')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#888');

    const simulation = d3.forceSimulation(grafo.nodes)
      .force('link', d3.forceLink(grafo.links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(20)); // Evitar sobreposição

    const link = svg.append('g')
      .attr('stroke-width', 1.5)
      .selectAll('line')
      .data(grafo.links)
      .enter().append('line')
      .attr('stroke', '#888')
      .attr('marker-end', 'url(#seta-cinza)');

    const node = svg.append('g')
      .selectAll('circle')
      .data(grafo.nodes)
      .enter().append('circle')
      .attr('r', 8)
      .attr('fill', d => d.id === raiz ? '#f39c12' : '#69b3a2')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .call(drag(simulation));

    const label = svg.append('g')
      .selectAll('text')
      .data(grafo.nodes)
      .enter().append('text')
      .text(d => d.id)
      .attr('font-size', '0.75rem')
      .attr('font-family', 'Arial, sans-serif')
      .attr('dx', 12)
      .attr('dy', 4)
      .attr('pointer-events', 'none'); // Evita interferência no drag

    simulation.on('tick', () => {
      // Usar linhas retas ao invés de curvas para evitar confusão visual
      link
        .attr('x1', d => {
          // Calcular posição na borda do círculo
          const dx = d.target.x - d.source.x;
          const dy = d.target.y - d.source.y;
          const length = Math.sqrt(dx * dx + dy * dy);
          return d.source.x + (dx / length) * 10; // 10 é o raio + margem
        })
        .attr('y1', d => {
          const dx = d.target.x - d.source.x;
          const dy = d.target.y - d.source.y;
          const length = Math.sqrt(dx * dx + dy * dy);
          return d.source.y + (dy / length) * 10;
        })
        .attr('x2', d => {
          const dx = d.target.x - d.source.x;
          const dy = d.target.y - d.source.y;
          const length = Math.sqrt(dx * dx + dy * dy);
          return d.target.x - (dx / length) * 10; // Para na borda do círculo
        })
        .attr('y2', d => {
          const dx = d.target.x - d.source.x;
          const dy = d.target.y - d.source.y;
          const length = Math.sqrt(dx * dx + dy * dy);
          return d.target.y - (dy / length) * 10;
        });

      node.attr('cx', d => d.x).attr('cy', d => d.y);
      label.attr('x', d => d.x).attr('y', d => d.y);
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
  
  label {
    display: block;
    margin: 10px 0;
    font-family: Arial, sans-serif;
  }
  
  select, input {
    margin-left: 10px;
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