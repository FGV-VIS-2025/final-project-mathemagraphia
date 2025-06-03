<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  let svgEl;
  let dadosBiografias = {};
  let matematicos = [];
  let mapaMatematicos = new Map();
  let grafo = { nodes: [], links: [] };
  let raiz = '';
  let profundidade = 1;
  let simulation;

  // Nova variável para manter o texto digitado na busca
  let buscaNome = '';
  let selecionado = null; // armazena matemático atual

  function normalizar(texto) {
    return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  }

  function extrairCitados(biografia, matematicos) {
    const bioNorm = normalizar(biografia);
    return matematicos
      .filter(m => bioNorm.includes(m.nome_normalizado))
      .map(m => m.slug);
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
        nodesMap.set(nome, { ...bio, nivel });

        const citados = extrairCitados(bio.biografia, matematicos);
        bio.citados = citados;

        for (const citado of citados) {
          if (!visitados.has(citado)) novaFronteira.push(citado);
        }
      }
      fronteira = novaFronteira;
    }

    const nodes = [...nodesMap.entries()].map(([id, bio]) => ({
      id,
      nivel: bio.nivel
    }));

    const links = [];
    const linkSet = new Set();

    for (const [source, bio] of nodesMap.entries()) {
      for (const target of bio.citados || []) {
        if (nodesMap.has(target)) {
          const linkId = `${source}->${target}`;
          if (!linkSet.has(linkId) && source !== target) {
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

    if (simulation) simulation.stop();

    simulation = d3.forceSimulation(grafo.nodes)
      .force('link', d3.forceLink(grafo.links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(20))
      .on('end', () => simulation.stop());

    const container = svg.append('g').attr('class', 'container');

    const link = container.append('g')
      .attr('stroke-width', 1.5)
      .selectAll('line')
      .data(grafo.links)
      .enter().append('line')
      .attr('stroke', '#888')
      .attr('marker-end', 'url(#seta-cinza)');
    
    const node = container.append('g')
      .selectAll('circle')
      .data(grafo.nodes)
      .enter().append('circle')
      .attr('r', 8)
      .attr('fill', d => d.id === raiz ? '#f39c12' : '#69b3a2')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .call(drag(simulation))
      .on('mouseover', (event, d) => {
        selecionado = mapaMatematicos.get(d.id);
      })
      .on('click', (event, d) => {
        selecionado = mapaMatematicos.get(d.id); // Fixa ao clicar também
      })


    const label = container.append('g')
      .selectAll('text')
      .data(grafo.nodes)
      .enter().append('text')
      .text(d => mapaMatematicos.get(d.id)?.nome_completo ?? d.id)
      .attr('font-size', '0.75rem')
      .attr('dx', 12)
      .attr('dy', 4)
      .attr('pointer-events', 'none');

    
    

    simulation.on('tick', () => {
      link
        .attr('x1', d => isFinite(d.source?.x) ? d.source.x : 0)
        .attr('y1', d => isFinite(d.source?.y) ? d.source.y : 0)
        .attr('x2', d => isFinite(d.target?.x) ? d.target.x : 0)
        .attr('y2', d => isFinite(d.target?.y) ? d.target.y : 0);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });
    
    function drag(sim) {
      return d3.drag()
        .on('start', (event, d) => {
          if (!event.active) sim.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) sim.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        });
    }

    const zoomBehavior = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', event => container.attr('transform', event.transform));

    svg.call(zoomBehavior);
  }


  onMount(async () => {
    const index = await fetch('biografias_json/index.json').then(r => r.json());
    matematicos = index;
    mapaMatematicos = new Map(index.map(m => [m.slug, m]));

    for (const m of matematicos) {
      const dados = await fetch(`biografias_json/${m.slug}.json`).then(r => r.json());
      dadosBiografias[m.slug] = dados;
    }

    // Defina um valor inicial para raiz e exiba o grafo
    raiz = matematicos[0].slug;
    construirGrafo(raiz, profundidade);
  });

  // Quando **apenas** raiz ou profundidade mudam, reconstrói o grafo
  $: if (raiz && profundidade) {
    construirGrafo(raiz, profundidade);
  }

  // Quando o usuário seleciona um nome no datalist, buscamos o slug correspondente
  function aoSelecionarNome() {
    const encontrado = matematicos.find(m => m.nome_completo === buscaNome);
    if (encontrado) {
      raiz = encontrado.slug;
      // Limpa a busca para não ficar texto antigo no campo
      buscaNome = '';
    }
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

/* Remova o “select,” pois não existe mais <select> */
  input {
    margin-left: 10px;
  }

  /* Estilização extra para a lista suspensa do datalist (caso queira ajustar) */
  input {
    padding: 4px 8px;
    font-size: 1rem;
    width: 40%;
  }
  svg {
    cursor: grab; /* Mostra que dá para arrastar (pan) */
  }

  svg:active {
    cursor: grabbing; /* Enquanto arrasta, muda o cursor */
  }
.painel-infos {
  position: absolute;
  left: 1rem;
  top: 7rem;
  width: 280px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 1rem;
  font-family: Arial, sans-serif;
  font-size: 0.9rem;
  box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
  z-index: 100;
  max-height: 70vh;
  overflow-y: auto;
}

.painel-infos h3 {
  margin-top: 0;
  font-size: 1.1rem;
  color: #333;
}

</style>

<h2>Grafo de Distâncias entre Matemáticos</h2>

<div class="painel-infos">
  {#if selecionado}
    <h3>{selecionado.nome_completo}</h3>
    <p><strong>Nascimento:</strong> {selecionado.nascimento}</p>
    {#if selecionado.falecimento}
      <p><strong>Falecimento:</strong> {selecionado.falecimento}</p>
    {/if}
    <p><strong>Slug:</strong> {selecionado.slug}</p>
    <p><strong>Biografia:</strong> {dadosBiografias[selecionado.slug]?.biografia.slice(0, 300)}…</p>
    <button on:click={() => selecionado = null}>Fechar</button>
  {:else}
    <p>🧠 Passe o mouse sobre um nó<br>ou clique para fixar.</p>
  {/if}
</div>

<!-- 1) Campo de busca com autocompletar -->
<label>
  Buscar Matemático:
  <input
    list="listaMatematicos"
    bind:value={buscaNome}
    on:change={aoSelecionarNome}
    placeholder="Digite parte do nome e selecione…" />
  <datalist id="listaMatematicos">
    {#each matematicos as m}
      <option value="{m.nome_completo}"></option>
    {/each}
  </datalist>
</label>

<!-- 2) Slider de Profundidade (permanece igual ao original) -->
<label>
  Profundidade: {profundidade}
  <input type="range" min="1" max="4" bind:value={profundidade} />
</label>

<!-- 3) Área do SVG para desenhar o grafo -->
<svg bind:this={svgEl}></svg>
