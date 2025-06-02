<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  let nodes = [];
  let links = [];
  let selectedTitle = "";
  let selectedId = "";

  function processar(rawData) {
    nodes = [];
    links = [];
    const mapa = new Map();

    // 1) Monta mapa “número romano → título completo”, mas sem repetições
    rawData.forEach(p => {
      const id = p.titulo.trim();
      // Regex mais robusta: só Prop. + romanos no início
      const matchNum = id.match(/^[Pp][Rr][Oo][Pp]\.\s*([IVXLCDM]+)\b/i);
      if (matchNum) {
        const num = matchNum[1].toUpperCase();
        // só adiciona se ainda não existir esse numeral no mapa
        if (!mapa.has(num)) {
          mapa.set(num, id);
          nodes.push({ id, title: p.conteudo });
        }
      }
    });

    // 2) Regex para capturar qualquer “(Prop. N…)” ou “(Pr N…)” no conteúdo
    const refRegex = /\(\s*(?:Prop|PR|Pr|PROP)\.?\s*([IVXLCDM]+|\d+)[^)]*\)/gi;

    rawData.forEach(p => {
      const origem = p.titulo.trim();
      const matches = [...p.conteudo.matchAll(refRegex)];
      matches.forEach(([fullMatch, rawNum]) => {
        // Se vier número arábico, converte para romano
        const ref = isNaN(rawNum)
          ? rawNum.toUpperCase()
          : toRoman(parseInt(rawNum, 10));
        if (mapa.has(ref)) {
          const destino = mapa.get(ref);
          links.push({ source: origem, target: destino });
        }
      });
    });
  }

  function toRoman(input) {
    const num = Number(input);
    if (!Number.isInteger(num) || num <= 0) return "";
    const values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1];
    const numerals = {
      1000: "M", 900: "CM", 500: "D", 400: "CD",
      100: "C", 90: "XC", 50: "L", 40: "XL",
      10: "X", 9: "IX", 5: "V", 4: "IV", 1: "I"
    };
    let result = "";
    let n = num;
    for (const v of values) {
      while (n >= v) {
        result += numerals[v];
        n -= v;
      }
    }
    return result;
  }

  onMount(async () => {
    const base = import.meta.env.BASE_URL || "";
    const res = await fetch(`${base}data/euclides_livro1.json`);
    const raw = await res.json();

    // ──────────── Pré-processamento ────────────
    raw.forEach(p => {
      // Normaliza “(Pr. N, 1)” para “(Prop. N)”
      p.conteudo = p.conteudo.replace(
        /\(\s*Pr\.?\s*(\d+)\s*,\s*1\s*\)/gi,
        "(Prop. $1)"
      );
      // E também pega “(Pr N 1)” sem vírgula
      p.conteudo = p.conteudo.replace(
        /\(\s*Pr\.?\s*(\d+)\s+1\s*\)/gi,
        "(Prop. $1)"
      );
    });
    // ────────────────────────────────────────────

    // DEBUG opcional: conferir se há títulos duplicados
    const titulos = raw.map(p => p.titulo.trim());
    const repetidos = titulos.filter((t, i) => titulos.indexOf(t) !== i);
    console.log("→ possíveis títulos duplicados:", repetidos);

    processar(raw);

    // DEBUG: confira que “PROP. XVIII. THEOR.” aparece só UMA vez em nodes
    console.log("→ nodes:", nodes.map(d => d.id));
    console.log("→ links:", links);

    // ─────── Mon­tagem do SVG e força ───────
    const svg = d3.select("#svg")
      .attr("viewBox", [-500, -300, 1000, 600])
      .call(d3.zoom().on("zoom", ({ transform }) => {
        svg.select("g").attr("transform", transform);
      }));

    svg.append("defs")
      .append("marker")
        .attr("id", "arrow")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
      .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", "#999");

    const g = svg.append("g");
    const sim = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(80))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(0, 0));

    const link = g.append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(links)
      .enter().append("line")
      .attr("stroke", "#999")
      .attr("stroke-width", 1.2)
      .attr("marker-end", "url(#arrow)");

    const node = g.append("g")
      .attr("class", "nodes")
      .selectAll("circle")
      .data(nodes)
      .enter().append("circle")
      .attr("r", 6)
      .attr("fill", "#4f7cac")
      .style("cursor", "pointer")
      .on("click", (_, d) => {
        selectedTitle = d.title;
        selectedId = d.id;
      })
      .call(d3.drag()
        .on("start", (event, d) => {
          if (!event.active) sim.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) sim.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
      );

    const label = g.append("g")
      .attr("class", "labels")
      .selectAll("text")
      .data(nodes)
      .enter().append("text")
      .text(d => d.id)
      .attr("x", 8)
      .attr("y", 3)
      .style("font-size", "9px")
      .style("fill", "#333")
      .style("pointer-events", "none");

    sim.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      label
        .attr("x", d => d.x + 8)
        .attr("y", d => d.y + 3);
    });
    // ────────────────────────────────────────────
  });
</script>

<style>
  .container {
    display: flex;
    height: 100vh;
    font-family: Arial, sans-serif;
  }
  .sidebar {
    width: 300px;
    background: #fafafa;
    border-right: 1px solid #ddd;
    display: flex;
    flex-direction: column;
  }
  .sidebar-header {
    padding: 16px;
    background: #4f7cac;
    color: white;
    font-size: 1.1rem;
    font-weight: bold;
    border-bottom: 1px solid #3b5a7a;
  }
  .sidebar-content {
    flex: 1;
    overflow-y: auto;
    padding: 12px 16px;
  }
  .sidebar-content p {
    margin-bottom: 1rem;
    white-space: pre-line;
    line-height: 1.5;
    font-size: 0.95rem;
    color: #333;
  }
  .placeholder {
    color: #777;
    font-style: italic;
    text-align: center;
    margin-top: 2rem;
  }
  .graph {
    flex: 1;
    position: relative;
    background: #ffffff;
  }
  svg {
    width: 100%;
    height: 100%;
  }
</style>

<div class="container">
  <div class="sidebar">
    <div class="sidebar-header">
      {#if selectedId}
        {selectedId}
      {:else}
        Informação
      {/if}
    </div>
    <div class="sidebar-content">
      {#if selectedTitle}
        {#each selectedTitle.split("\n\n") as paragraph}
          <p>{paragraph.trim()}</p>
        {/each}
      {:else}
        <p class="placeholder">
          Clique em um nó para ver o texto completo da proposição.
        </p>
      {/if}
    </div>
  </div>
  <div class="graph">
    <svg id="svg"></svg>
  </div>
</div>
