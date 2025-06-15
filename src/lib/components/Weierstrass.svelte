<script>
    import { onMount } from 'svelte';
    import * as d3 from 'd3';
  
    export let width = 800;
    export let height = 400;
    let amplitude = 1;
    let freq = 2;
    let terms = 20;
    let animationSpeed = 2000; // ms per zoom cycle
  
    let container;
    let rootSvg, plotGroup, xScale, yScale, line, path;
  
    // Generate Weierstrass data on [xMin, xMax]
    function computeData(xMin, xMax, points = 1000) {
      const xs = d3.range(xMin, xMax, (xMax - xMin) / points);
      return xs.map(x => {
        let y = 0;
        for (let n = 0; n < terms; n++) {
          y += Math.pow(freq, -n) * Math.cos(Math.pow(freq, n) * x);
        }
        return { x, y: y * amplitude };
      });
    }
  
    function draw() {
      const data = computeData(-Math.PI, Math.PI);
      xScale.domain(d3.extent(data, d => d.x));
      yScale.domain(d3.extent(data, d => d.y));
  
      plotGroup.select('.x-axis')
        .call(d3.axisBottom(xScale).ticks(10));
      plotGroup.select('.y-axis')
        .call(d3.axisLeft(yScale).ticks(6));
  
      path.datum(data)
        .attr('d', line);
    }
  
    onMount(() => {
      // Create SVG and group
      rootSvg = d3.select(container)
        .append('svg')
          .attr('width', width)
          .attr('height', height);
  
      plotGroup = rootSvg.append('g')
        .attr('transform', 'translate(50, 20)');
  
      // Scales
      xScale = d3.scaleLinear().range([0, width - 70]);
      yScale = d3.scaleLinear().range([height - 60, 0]);
  
      // Axes groups
      plotGroup.append('g').attr('class', 'x-axis')
        .attr('transform', `translate(0, ${height - 60})`);
      plotGroup.append('g').attr('class', 'y-axis');
  
      // Line generator
      line = d3.line()
        .x(d => xScale(d.x))
        .y(d => yScale(d.y));
  
      // Path
      path = plotGroup.append('path')
        .attr('class', 'weierstrass-line')
        .attr('fill', 'none')
        .attr('stroke', 'steelblue')
        .attr('stroke-width', 1.5);
  
      // Zoom behavior
      const zoom = d3.zoom()
        .scaleExtent([1, 100])
        .on('zoom', event => {
          plotGroup.attr('transform', event.transform);
        });
  
      rootSvg.call(zoom);
  
      draw();
  
      // Animate zoom in & out
      let direction = 1;
      d3.interval(elapsed => {
        const t = (elapsed % animationSpeed) / animationSpeed;
        const k = 1 + direction * (100 - 1) * t;
        rootSvg.transition().duration(100)
          .call(zoom.scaleTo, k);
        if (t >= 0.99) direction *= -1;
      }, 100);
    });
  </script>
  
  <div class="controls">
    <label>
      Amplitude:
      <input type="range" min="0.1" max="5" step="0.1" bind:value={amplitude} on:input={draw} />
    </label>
    <label>
      Frequency:
      <input type="range" min="2" max="10" step="1" bind:value={freq} on:input={draw} />
    </label>
    <label>
      Terms:
      <input type="number" min="5" max="100" bind:value={terms} on:input={draw} />
    </label>
    <label>
      Zoom Cycle (ms):
      <input type="number" min="500" step="100" bind:value={animationSpeed} />
    </label>
    <button on:click={draw}>Redraw</button>
  </div>
  
  <div bind:this={container} class="chart" style="width:{width}px; height:{height}px; border:1px solid #ccc;"></div>
  
  <style>
    .controls {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }
    label {
      font-size: 0.9rem;
    }
    input {
      margin-left: 0.3rem;
    }
    .weierstrass-line {
      pointer-events: none;
    }
  </style>
  