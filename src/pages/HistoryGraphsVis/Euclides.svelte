<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  let nodes = [];
  let links = [];

  // Guarda o texto (conteúdo) da proposição selecionada
  let selectedTitle = "";
  // (Opcional) Guarda o ID/título da proposição selecionada
  let selectedId = "";

  function processar(rawData) {
    nodes = [];
    links = [];
    const mapa = new Map();

    // Mapeia número romano → título
    rawData.forEach(p => {
      const id = p.titulo.trim();
      const num = id.match(/PROP\. ([IVXLCDM]+)(?=\.)?/i)?.[1]?.toUpperCase();
      if (num) {
        mapa.set(num, id);
        nodes.push({ id, title: p.conteudo });
      }
    });

    const refRegex = /\(\s*(?:Prop|Pr|PROP)\.?\s+([IVXLCDM]+|\d+)(?:,\s*\d+)?\s*\)/gi;

    rawData.forEach(p => {
      const origem = p.titulo.trim();
      const matches = [...p.conteudo.matchAll(refRegex)];

      matches.forEach(([_, refNum]) => {
        const ref = isNaN(refNum)
          ? refNum.toUpperCase()
          : toRoman(parseInt(refNum));

        const destino = mapa.get(ref);
        if (destino) {
          links.push({ source: origem, target: destino });
        } else {
          console.warn(`⚠️ Referência não encontrada: Prop. ${ref} em ${origem}`);
        }
      });
    });

    console.log(`✅ Nós: ${nodes.length} | Arestas: ${links.length}`);
  }

  function toRoman(input) {
    const num = Number(input);
    if (!Number.isInteger(num) || num <= 0) return '';
    
    const values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1];
    const numerals = {
      1000: 'M', 900: 'CM', 500: 'D', 400: 'CD',
      100: 'C', 90: 'XC', 50: 'L', 40: 'XL',
      10: 'X', 9: 'IX', 5: 'V', 4: 'IV', 1: 'I'
    };
    
    let result = '';
    let n = num;
    
    for (const val of values) {
      while (n >= val) {
        result += numerals[val];
        n -= val;
      }
    }
    return result;
  }

  onMount(async () => {
    const base = import.meta.env.BASE_URL || '';
    const res = await fetch(`${base}data/euclides_livro1.json`);
    const raw = await res.json();
    processar(raw);

    const svg = d3.select('#svg')
      .attr('viewBox', [-500, -300, 1000, 600])
      .call(d3.zoom().on("zoom", ({ transform }) => {
        svg.select('g').attr('transform', transform);
      }));

    const g = svg.append('g');

    // Desenha arestas
    const link = g.append("g")
      .selectAll("line")
      .data(links)
      .enter().append("line")
      .attr("stroke", "#aaa");

    // Desenha nós e registra evento de clique
    const node = g.append("g")
      .selectAll("circle")
      .data(nodes)
      .enter().append("circle")
      .attr("r", 8)
      .attr("fill", "#69b3a2")
      .style("cursor", "pointer")
      .on("click", (event, d) => {
        // Ao clicar, preenche a sidebar com o texto da proposição
        selectedTitle = d.title;
        selectedId = d.id;
      })
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Exibe o rótulo de cada nó (pode ser ocultado se poluir muito)
    const label = g.append("g")
      .selectAll("text")
      .data(nodes)
      .enter().append("text")
      .text(d => d.id)
      .attr("x", 10)
      .attr("y", 4)
      .style("font-size", "10px")
      .style("pointer-events", "none"); // para que o texto não bloqueie cliques no círculo

    // Configuração da simulação de força
    const sim = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(0, 0))
      .on("tick", () => {
        link
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);
        node
          .attr("cx", d => d.x)
          .attr("cy", d => d.y);
        label
          .attr("x", d => d.x + 10)
          .attr("y", d => d.y + 4);
      });

    function dragstarted(event, d) {
      if (!event.active) sim.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) sim.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  });
</script>

<style>
  /* Container principal: sidebar à esquerda + grafo à direita */
  .container {
    display: flex;
    height: 100vh; /* ocupa toda a altura da janela */
  }

  /* Sidebar fixo à esquerda */
  .sidebar {
    width: 300px;
    min-width: 300px;
    max-width: 300px;
    padding: 16px;
    background: #f5f5f5;
    border-right: 1px solid #ddd;
    overflow-y: auto;
  }

  .sidebar h2 {
    margin-top: 0;
    font-size: 1.1rem;
    color: #333;
  }

  .sidebar p {
    white-space: pre-wrap;
    line-height: 1.4;
    font-size: 0.95rem;
    color: #444;
  }

  .sidebar .placeholder {
    color: #888;
    font-style: italic;
  }

  /* Área do grafo: ocupa o restante do espaço */
  .graph {
    flex: 1;
    position: relative; /* para o SVG ocupar 100% */
  }

  svg {
    width: 100%;
    height: 100%;
  }
</style>

<div class="container">
  <!-- Sidebar fixa -->
  <div class="sidebar">
    {#if selectedTitle}
      <h2>{selectedId}</h2>
      <p>{selectedTitle}</p>
    {:else}
      <p class="placeholder">Clique em um nó para ver o texto da proposição.</p>
    {/if}
  </div>

  <!-- Área do grafo -->
  <div class="graph">
    <svg id="svg"></svg>
  </div>
</div>
