<!-- src/components/VizContainer.svelte -->
<script>
  import { onMount, afterUpdate, createEventDispatcher } from 'svelte';
  import * as d3 from 'd3';
  export let id;
  export let points = [];
  export let currentEra = null;
  const dispatch = createEventDispatcher();

  let container;

  onMount(draw);
  afterUpdate(draw);

  function draw() {
    if (id !== 1 || !container) return;
    const sel = d3.select(container);
    sel.selectAll('*').remove();

    // dimensões
    const W = container.clientWidth;
    const H = container.clientHeight;
    const margin = { top: 20, right: 20, bottom: 60, left: 40 };
    const innerW = W - margin.left - margin.right;
    const innerH = H - margin.top - margin.bottom;

    // domínio de anos
    let [startYear, endYear] = currentEra
      ? [...currentEra]
      : d3.extent(points, d => d.birthYear);
    if (startYear > endYear) [startYear, endYear] = [endYear, startYear];
    const isAncient = endYear <= 0;

    // piecewise tScale para BC
    function tScaleBC(rel) {
      const S15 = 1/15, S2 = 2/15, S4 = 4/15, S8 = 8/15;
      if (rel >= 800) {
        return ((1600 - rel) / 800) * S15;
      }
      if (rel >= 400) {
        return S15 + ((800 - rel) / 400) * S2;
      }
      if (rel >= 200) {
        return S15 + S2 + ((400 - rel) / 200) * S4;
      }
      return S15 + S2 + S4 + ((200 - rel) / 200) * S8;
    }

    // tScale geral
    const tScale = isAncient
      ? rel => tScaleBC(rel)
      : year => (year - startYear) / (endYear - startYear);

    // número de ciclos de seno
    const periods = isAncient ? 2 : 1;

    // curva (seno invertido para BC)
    const curve = d3.range(0, 1.001, 1/400).map(u => {
      const x = margin.left + innerW * u;
      let y = margin.top + innerH * 0.5;
      if (isAncient) {
        const amp = innerH * 0.3; // reduz amplitude para 30% da altura
        y -= amp * Math.sin(2 * Math.PI * periods * u);
      }
      return [x, y];
    });

    // SVG + curva
    const svg = sel.append('svg')
      .attr('width', W)
      .attr('height', H);
    svg.append('path')
      .datum(curve)
      .attr('d', d3.line().curve(d3.curveNatural))
      .attr('fill', 'none')
      .attr('stroke', isAncient ? '#d946ef' : '#999')
      .attr('stroke-width', 2);

    // prepara função de jitter vertical: ±1% de innerH
    const jitterAmt = innerH * 0.02;
    const jitter = d3.randomUniform(-jitterAmt, jitterAmt);

    // desenha pontos com jitter e tamanho reduzido
    svg.selectAll('circle')
      .data(points)
      .join('circle')
      .attr('cx', d => {
        if (isAncient) {
          const rel = 0 - d.birthYear;
          return margin.left + innerW * tScale(rel);
        } else {
          return margin.left + innerW * tScale(d.birthYear);
        }
      })
      .attr('cy', d => {
        let baseY = margin.top + innerH * 0.5;
        if (isAncient) {
          const rel = 0 - d.birthYear;
          const u   = tScale(rel);
          const amp = innerH * 0.3;
          baseY -= amp * Math.sin(2 * Math.PI * periods * u);
        }
        return baseY + jitter();
      })
      .attr('r', 4)
      .attr('fill', isAncient ? '#a855f7' : '#3b82f6')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .append('title')
      .text(d => `${d.nome_curto} (${d.birthYear < 0 ? `${-d.birthYear} BC` : d.birthYear})`);

    // desenha rótulos com jitter
    svg.selectAll('text')
      .data(points)
      .join('text')
      .attr('x', d => {
        if (isAncient) {
          const rel = 0 - d.birthYear;
          return margin.left + innerW * tScale(rel);
        } else {
          return margin.left + innerW * tScale(d.birthYear);
        }
      })
      .attr('y', d => {
        let baseY = margin.top + innerH * 0.5;
        if (isAncient) {
          const rel = 0 - d.birthYear;
          const u   = tScale(rel);
          const amp = innerH * 0.3;
          baseY -= amp * Math.sin(2 * Math.PI * periods * u);
        }
        return baseY + jitter() - 10;
      })
      .text(d => d.nome_curto)
      .attr('text-anchor', 'middle')
      .style('font-size', '11px')
      .style('fill', '#1e293b');

    // eixo de anos
    if (isAncient) {
      const ticks = [200, 400, 800, 1600];
      const yAxis = margin.top + innerH + 15;
      ticks.forEach(r => {
        const x = margin.left + innerW * tScale(r);
        svg.append('line')
          .attr('x1', x).attr('x2', x)
          .attr('y1', yAxis).attr('y2', yAxis + 6)
          .attr('stroke', '#333');
        svg.append('text')
          .attr('x', x)
          .attr('y', yAxis + 20)
          .text(`${r} BC`)
          .attr('text-anchor', 'middle')
          .style('font-size', '10px')
          .style('fill', '#333');
      });
    } else {
      const xScale = d3.scaleLinear()
        .domain([startYear, endYear])
        .range([margin.left, margin.left + innerW]);
      svg.append('g')
        .attr('transform', `translate(0, ${margin.top + innerH + 15})`)
        .call(d3.axisBottom(xScale).ticks(6)
          .tickFormat(y => y < 0 ? `${-y} BC` : y))
        .selectAll('text')
        .style('font-size', '10px');
    }
  }
</script>

<div class="viz" bind:this={container} on:click={() => dispatch('expand')} />

<style>
  .viz {
    width: 100%;
    height: 100%;
    overflow: auto;
    cursor: pointer;
  }
</style>