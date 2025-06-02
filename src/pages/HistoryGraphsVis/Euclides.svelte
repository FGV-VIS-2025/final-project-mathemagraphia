<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  let nodes = [];
  let links = [];
  let selectedTitle = "";
  let selectedId = "";

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

  function fromRoman(str) {
    const map = { I:1, V:5, X:10, L:50, C:100, D:500, M:1000 };
    let sum = 0;
    for (let i = 0; i < str.length; i++) {
      const curr = map[str[i]];
      const next = map[str[i+1]];
      if (next && next > curr) {
        sum += next - curr;
        i++;
      } else {
        sum += curr;
      }
    }
    return sum;
  }

  function processar(rawData) {
    nodes = [];
    links = [];
    const mapa = new Map();

    rawData.forEach(p => {
      const id = p.titulo.trim();
      const matchNum = id.match(/^[Pp][Rr][Oo][Pp]\.\s*([IVXLCDM]+)\b/i);
      if (matchNum) {
        const num = matchNum[1].toUpperCase();
        if (!mapa.has(num)) {
          mapa.set(num, id);
          nodes.push({ id, title: p.conteudo });
        }
      }
    });

    const refRegex = /\(\s*(?:Prop|PR|Pr|PROP)\.?\s*([IVXLCDM]+|\d+)[^)]*\)/gi;
    rawData.forEach(p => {
      const origem = p.titulo.trim();
      const matches = [...p.conteudo.matchAll(refRegex)];
      matches.forEach(([fullMatch, rawNum]) => {
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

  // Função que recebe os nós de origem (src) e destino (tgt),
  // e retorna a string "d" de um <path> SVG do tipo arco (A …).
  function gerarArc(src, tgt) {
    // 1) Coords cartesianas
    const x1 = src.x;
    const y1 = src.y;
    const x2 = tgt.x;
    const y2 = tgt.y;

    // 2) Parâmetros polares de cada nó
    const r1 = src.r;
    const r2 = tgt.r;
    const θ1 = src.theta;
    const θ2 = tgt.theta;

    // 3) Escolhe um raio intermediário para o arco:
    const deslocamento = 20; // você pode ajustar para "levantar" mais/menos o arco
    const rArc = (r1 + r2) / 2 + deslocamento;

    // 4) Calcula flags do SVG (large-arc-flag e sweep-flag)
    const dθ = Math.abs(θ2 - θ1);
    const largeArcFlag = dθ > Math.PI ? 1 : 0;
    const sweepFlag = θ2 > θ1 ? 1 : 0;

    // 5) Monta a string do path
    return `
      M ${x1} ${y1}
      A ${rArc} ${rArc} 0 ${largeArcFlag} ${sweepFlag} ${x2} ${y2}
    `;
  }

  onMount(async () => {
    const base = import.meta.env.BASE_URL || "";
    const res = await fetch(`${base}data/euclides_livro1.json`);
    const raw = await res.json();

    // Normaliza “(Pr. N, 1)” e “(Pr N 1)”
    raw.forEach(p => {
      p.conteudo = p.conteudo.replace(
        /\(\s*Pr\.?\s*(\d+)\s*,\s*1\s*\)/gi,
        "(Prop. $1)"
      );
      p.conteudo = p.conteudo.replace(
        /\(\s*Pr\.?\s*(\d+)\s+1\s*\)/gi,
        "(Prop. $1)"
      );
    });

    processar(raw);

    // Mapa auxiliar (id → node) e extrai d.num
    const nodeById = new Map();
    nodes.forEach(d => {
      const m = d.id.match(/([IVXLCDM]+)/);
      d.num = m ? fromRoman(m[1]) : 0;
      nodeById.set(d.id, d);
    });

    // 1) Ordena nodes por d.num (Prop I, II, III, …)
    nodes.sort((a, b) => a.num - b.num);

    // 2) Parâmetros da espiral
    const viewWidth = 1000;
    const viewHeight = 600;
    const maxRadius = Math.min(viewWidth, viewHeight) / 2 - 40;
    const N = nodes.length;
    const scale = maxRadius / Math.sqrt(N - 1);
    const goldenAngle = Math.PI * (3 - Math.sqrt(5)); // ≈ 2.39996

    // 3) Atribui r, θ, x e y a cada nó
    nodes.forEach((d, i) => {
      const r = scale * Math.sqrt(i);
      const θ = i * goldenAngle;
      d.r = r;
      d.theta = θ;
      d.x = r * Math.cos(θ);
      d.y = r * Math.sin(θ);
    });

    // 4) Monta o SVG e o grupo principal
    const svg = d3
      .select("#svg")
      .attr("viewBox", [-500, -300, 1000, 600])
      .call(
        d3
          .zoom()
          .on("zoom", ({ transform }) => {
            svg.select("g").attr("transform", transform);
          })
      );

    // 5) Definição do marcador de seta (igual antes)
    svg
      .append("defs")
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

    // 6) ---- Desenha as arestas como arcos manuais (SVG "A" comandos) ----
    g.append("g")
      .attr("class", "links")
      .selectAll("path")
      .data(links)
      .enter()
      .append("path")
      .attr("class", "link")
      .attr("d", link => {
        const src = nodeById.get(link.source);
        const tgt = nodeById.get(link.target);
        return gerarArc(src, tgt);
      })
      .attr("fill", "none")
      .attr("stroke", "#999")
      .attr("stroke-width", 1.2)
      .attr("stroke-opacity", 0.7)
      .attr("marker-end", "url(#arrow)");

    // 7) Desenha os nós (círculos)
    const nodeSel = g
      .append("g")
      .attr("class", "nodes")
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("cx", d => d.x)
      .attr("cy", d => d.y)
      .attr("r", 6)
      .attr("fill", "#4f7cac")
      .style("cursor", "pointer")
      .on("click", (_, d) => {
        // Atualiza sidebar
        selectedTitle = d.title;
        selectedId = d.id;

        // Destaca só as arestas que tocam esse nó
        g.selectAll("path.link")
          .attr("stroke-opacity", link =>
            link.source === d.id || link.target === d.id ? 1 : 0.1
          );
      });

    // 8) Rótulos (id) ao lado de cada nó
    g.append("g")
      .attr("class", "labels")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .text(d => d.id)
      .attr("x", d => d.x + 8)
      .attr("y", d => d.y + 3)
      .style("font-size", "9px")
      .style("fill", "#333")
      .style("pointer-events", "none");

    // 9) Clique fora reseta arestas e limpa sidebar
    svg.on("click", (event) => {
      if (event.target.tagName !== "circle") {
        g.selectAll("path.link").attr("stroke-opacity", 0.7);
        selectedTitle = "";
        selectedId = "";
      }
    });
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
