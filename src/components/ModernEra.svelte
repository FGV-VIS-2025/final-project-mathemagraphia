<script>
    import { onMount } from 'svelte';
    import * as d3 from 'd3';
  
    let container;
    const margin = { top: 60, right: 40, bottom: 60, left: 60 };
    let width, height, svg;
  
    let data = []; // { step, headsRatio: [], tailsRatio: [] }
    let counts = {};
    let intervalId;
    let running = false;
    const tossInterval = 200; // ms entre lançamentos
    const maxSteps = 500;      // número máximo de lançamentos
    let numCoins = 1;          // número de moedas a simular
  
    function setupChart() {
      width = container.clientWidth - margin.left - margin.right;
      height = container.clientHeight - margin.top - margin.bottom;
  
      d3.select(container).selectAll('*').remove();
  
      svg = d3.select(container)
        .append('svg')
          .attr('width', width + margin.left + margin.right)
          .attr('height', height + margin.top + margin.bottom)
        .append('g')
          .attr('transform', `translate(${margin.left},${margin.top})`);
  
      // Título corrigido
      svg.append('text')
        .attr('x', width / 2)
        .attr('y', -30)
        .attr('text-anchor', 'middle')
        .style('font-size', '1.2rem')
        .style('fill', 'black')
        .text('Simulação de lançamentos de moedas – proporção de Caras e Coroas');
  
      // Eixos
      svg.append('g').attr('class', 'x-axis').attr('transform', `translate(0, ${height})`);
      svg.append('g').attr('class', 'y-axis');
  
      // Linhas para cada moeda
      for (let i = 0; i < numCoins; i++) {
        svg.append('path')
          .attr('class', `line heads-${i}`)
          .attr('fill', 'none')
          .attr('stroke', 'steelblue')
          .attr('stroke-width', 2)
          .attr('stroke-dasharray', '');
        svg.append('path')
          .attr('class', `line tails-${i}`)
          .attr('fill', 'none')
          .attr('stroke', 'red')
          .attr('stroke-width', 2)
          .attr('stroke-dasharray', '4 4');
      }
  
      // Legenda
      const legend = svg.append('g')
        .attr('class', 'legend')
        .attr('transform', `translate(${width - 120},${-margin.top/2 + 10})`);
      const legendData = [
        { label: 'Caras', stroke: 'steelblue', dash: '' },
        { label: 'Coroas', stroke: 'red', dash: '4 4' },
      ];
      legendData.forEach((d, i) => {
        const g = legend.append('g').attr('transform', `translate(0, ${i * 20})`);
        g.append('line')
          .attr('x1', 0).attr('y1', 0)
          .attr('x2', 20).attr('y2', 0)
          .attr('stroke', d.stroke)
          .attr('stroke-width', 2)
          .attr('stroke-dasharray', d.dash);
        g.append('text')
          .attr('x', 25).attr('y', 5)
          .text(d.label)
          .style('font-size', '0.8rem')
          .style('fill', 'black');
      });
  
      // Texto de proporção atual
      svg.append('text')
        .attr('class', 'current-text')
        .attr('x', 0)
        .attr('y', height + 40)
        .style('font-size', '1rem')
        .style('fill', 'black');
  
      resetData();
      updateChart();
    }
  
    function resetData() {
      data = [];
      counts = {};
      for (let i = 0; i < numCoins; i++) {
        counts[i] = { heads: 0, tails: 0 };
      }
    }
  
    function updateChart() {
      const maxStep = data.length > 0 ? d3.max(data, d => d.step) : 1;
      const x = d3.scaleLinear().domain([1, maxStep]).range([0, width]);
      const y = d3.scaleLinear().domain([0, 1]).range([height, 0]);
  
      // Atualiza eixos
      svg.select('.x-axis')
        .call(d3.axisBottom(x).ticks(6).tickFormat(d3.format('d')))
        .selectAll('text').attr('fill', 'black');
      svg.select('.y-axis')
        .call(d3.axisLeft(y).ticks(5).tickFormat(d3.format('.0%')))
        .selectAll('text').attr('fill', 'black');
  
      // Atualiza linhas de cada moeda
      data.forEach((d, idx) => { d.stepIndex = idx + 1; });
      for (let i = 0; i < numCoins; i++) {
        const lineHeads = d3.line()
          .x(d => x(d.stepIndex))
          .y(d => y(d.headsRatio[i]));
        const lineTails = d3.line()
          .x(d => x(d.stepIndex))
          .y(d => y(d.tailsRatio[i]));
  
        svg.select(`.line.heads-${i}`)
          .datum(data)
          .attr('d', lineHeads);
        svg.select(`.line.tails-${i}`)
          .datum(data)
          .attr('d', lineTails);
      }
  
      // Atualiza texto de proporção atual
      if (data.length) {
        const latest = data[data.length - 1];
        if (numCoins === 1) {
          const heads = d3.format('.1%')(latest.headsRatio[0]);
          const tails = d3.format('.1%')(latest.tailsRatio[0]);
          svg.select('.current-text')
            .text(`Proporção atual – Caras: ${heads}, Coroas: ${tails}`);
        } else {
          const parts = [];
          for (let i = 0; i < numCoins; i++) {
            parts.push(
              `Moeda ${i + 1} – Caras: ${d3.format('.1%')(latest.headsRatio[i])}, ` +
              `Coroas: ${d3.format('.1%')(latest.tailsRatio[i])}`
            );
          }
          svg.select('.current-text')
            .text(parts.join(' | '));
        }
      }
    }
  
    function toss() {
      const step = (data.length ? data[data.length - 1].step : 0) + 1;
      const headsRatio = [], tailsRatio = [];
      for (let i = 0; i < numCoins; i++) {
        const isHead = Math.random() < 0.5;
        counts[i][isHead ? 'heads' : 'tails']++;
        headsRatio[i] = counts[i].heads / step;
        tailsRatio[i] = counts[i].tails / step;
      }
      data.push({ step, headsRatio, tailsRatio });
      updateChart();
      if (step >= maxSteps) stop();
    }
  
    function start() {
      if (running) return;
      running = true;
      intervalId = setInterval(toss, tossInterval);
    }
  
    function stop() {
      clearInterval(intervalId);
      running = false;
    }
  
    function reset() {
      stop();
      setupChart();
    }
  
    function changeNumCoins(e) {
      numCoins = +e.target.value;
      setupChart();
    }
  
    onMount(() => {
      setupChart();
      window.addEventListener('resize', setupChart);
      return () => window.removeEventListener('resize', setupChart);
    });
  </script>
  
  <div class="controls">
    <label style="color:black; margin-right:1rem;">
      Número de moedas:
      <select on:change={changeNumCoins}>
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="5">5</option>
      </select>
    </label>
    <button on:click={start} disabled={running}>Start</button>
    <button on:click={reset}>Reset</button>
  </div>
  <div bind:this={container} class="chart"></div>
  
  <style>
    .chart { width: 100%; height: 400px; }
    .controls { margin-bottom: 0.5rem; }
    button, select { margin-right: 0.5rem; padding: 0.4rem 0.8rem; }
    .axis path, .axis line, .axis text { stroke: black; fill: black; }
  </style>
  