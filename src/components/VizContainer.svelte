<script>
  export let id;
  export let points = [];
  export let currentEra = null;

  import { createEventDispatcher, onMount, afterUpdate } from 'svelte';
  import * as d3 from 'd3';
  const dispatch = createEventDispatcher();

  let container;

  onMount(draw);
  afterUpdate(draw);

  function draw() {
    if (id !== 1 || !container) return;

    // limpa visual anterior
    d3.select(container).selectAll("*").remove();

    const margin = { top: 20, bottom: 20, left: 40, right: 20 };
    const width = 280;
    const height = points.length * 30 + margin.top + margin.bottom;

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const y = d3.scalePoint()
      .domain(points.map(d => d.nome_curto))
      .range([margin.top, height - margin.bottom])
      .padding(0.5);

    // linha vertical
    svg.append('line')
      .attr('x1', margin.left)
      .attr('x2', margin.left)
      .attr('y1', margin.top)
      .attr('y2', height - margin.bottom)
      .attr('stroke', '#999')
      .attr('stroke-width', 2);

    // pontos na timeline
    svg.selectAll('circle')
      .data(points)
      .join('circle')
      .attr('cx', margin.left)
      .attr('cy', d => y(d.nome_curto))
      .attr('r', 6)
      .attr('fill', '#3b82f6');

    // labels
    svg.selectAll('text')
      .data(points)
      .join('text')
      .attr('x', margin.left + 12)
      .attr('y', d => y(d.nome_curto) + 4)
      .text(d => d.nome_curto)
      .style('font-size', '12px')
      .style('fill', '#1e293b');
  }
</script>

<div class="viz" bind:this={container} on:click={() => dispatch('expand')} />

<style>
  .viz {
    width: 100%;
    height: 100%;
    overflow-y: auto;
    cursor: pointer;
  }
</style>
