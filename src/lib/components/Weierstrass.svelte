<script>
    import { onMount } from 'svelte';
    import * as d3 from 'd3';
  
    // Dimensions
    export let weierWidth = 800;
    export let weierHeight = 400;
    export let mandelWidth = 800;
    export let mandelHeight = 400;
  
    // Weierstrass parameters
    let amplitude = 1;
    let freq = 2;
    let terms = 20;
  
    // Mandelbrot parameters
    let maxIter = 200;
    let mandelConfig = { xMin: -2, xMax: 1, yMin: -1.5, yMax: 1.5 };
  
    let weierContainer, mandelContainer;
    let svgW, gW;
  
    function computeData(xMin, xMax, points = weierWidth) {
      return d3.range(xMin, xMax, (xMax - xMin) / points).map(x => {
        let y = 0;
        for (let n = 0; n < terms; n++) {
          y += Math.pow(freq, -n) * Math.cos(Math.pow(freq, n) * x);
        }
        return { x, y: y * amplitude };
      });
    }
  
    function drawWeier(transform) {
      const data = computeData(-Math.PI, Math.PI);
      const x = d3.scaleLinear().domain(d3.extent(data, d => d.x)).range([0, weierWidth]);
      const y = d3.scaleLinear().domain(d3.extent(data, d => d.y)).range([weierHeight, 0]);
      const tx = transform.rescaleX(x);
      const ty = transform.rescaleY(y);
  
      gW.select('.x-axis').call(d3.axisBottom(tx).ticks(6));
      gW.select('.y-axis').call(d3.axisLeft(ty).ticks(5));
  
      const line = d3.line()
        .x(d => tx(d.x))
        .y(d => ty(d.y));
  
      gW.select('.weier-path').datum(data).attr('d', line);
    }
  
    function drawMandelbrot(transform) {
      const canvas = d3.select(mandelContainer)
        .selectAll('canvas').data([null])
        .join('canvas')
          .attr('width', mandelWidth)
          .attr('height', mandelHeight)
          .classed('mandel-canvas', true);
  
      const ctx = canvas.node().getContext('2d');
      const img = ctx.createImageData(mandelWidth, mandelHeight);
      for (let px = 0; px < mandelWidth; px++) {
        for (let py = 0; py < mandelHeight; py++) {
          const x0 = mandelConfig.xMin + (px / mandelWidth) * (mandelConfig.xMax - mandelConfig.xMin);
          const y0 = mandelConfig.yMin + (py / mandelHeight) * (mandelConfig.yMax - mandelConfig.yMin);
          let x = 0, y = 0, iter = 0;
          while (x*x + y*y <= 4 && iter < maxIter) {
            const xt = x*x - y*y + x0;
            y = 2*x*y + y0;
            x = xt; iter++;
          }
          const c = iter === maxIter ? 0 : 255 - Math.floor(255 * iter / maxIter);
          const idx = (py * mandelWidth + px) * 4;
          img.data[idx] = img.data[idx+1] = img.data[idx+2] = c;
          img.data[idx+3] = 255;
        }
      }
      ctx.putImageData(img, 0, 0);
  
      if (transform) {
        d3.select(canvas.node()).style('transform', transform);
      }
    }
  
    onMount(() => {
      // Setup Weierstrass
      const margin = { top: 40, right: 20, bottom: 50, left: 60 };
      svgW = d3.select(weierContainer).append('svg')
        .attr('width', weierWidth + margin.left + margin.right)
        .attr('height', weierHeight + margin.top + margin.bottom)
        .style('background', '#fff').style('box-shadow', '0 2px 8px rgba(0,0,0,0.1)');
  
      svgW.append('text')
        .attr('x', margin.left)
        .attr('y', 24)
        .style('font-size', '1.2rem').style('font-weight', '600')
        .text('Precursora dos estudos de fractais (1872, século XIX)');
  
      gW = svgW.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
      gW.append('g').attr('class', 'x-axis').attr('transform', `translate(0,${weierHeight})`);
      gW.append('g').attr('class', 'y-axis');
      gW.append('path').attr('class', 'weier-path').attr('fill', 'none').attr('stroke', '#007acc').attr('stroke-width', 2);
  
      const zoomW = d3.zoom()
        .scaleExtent([1, 30])
        .translateExtent([[0,0],[weierWidth, weierHeight]])
        .on('zoom', e => drawWeier(e.transform));
      svgW.call(zoomW);
      drawWeier(d3.zoomIdentity);
  
      // Setup Mandelbrot
      drawMandelbrot();
      const canvas = d3.select(mandelContainer).select('canvas');
      const zoomM = d3.zoom()
        .scaleExtent([1, 20])
        .translateExtent([[0,0],[mandelWidth, mandelHeight]])
        .on('zoom', e => drawMandelbrot(e.transform));
      canvas.call(zoomM);
    });
  </script>
  
  <style>
    .container { max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; gap: 3rem; }
    .chart-block { background: #f9f9f9; padding: 1rem; border-radius: 8px; }
    .chart-title { font-size: 1.3rem; margin-bottom: 0.5rem; text-align: center; }
    .chart-controls { display: flex; justify-content: center; gap: 1.5rem; margin-top: 0.75rem; }
    .chart-controls label { display: flex; flex-direction: column; align-items: center; font-size: 0.9rem; }
    .chart-controls input { margin-top: 0.25rem; }
    canvas { display: block; margin: 0 auto; border-radius: 4px; }
  </style>
  
  <div class="container">
    <div class="chart-block">
      <div class="chart-title">Função de Weierstrass</div>
      <div bind:this={weierContainer}></div>
      <div class="chart-controls">
        <label>Amplitude<input type="range" min="0.1" max="5" step="0.1" bind:value={amplitude} on:input={e => drawWeier(d3.zoomIdentity)} /></label>
        <label>Freq<input type="range" min="2" max="8" step="1" bind:value={freq} on:input={e => drawWeier(d3.zoomIdentity)} /></label>
        <label>Terms<input type="number" min="5" max="200" bind:value={terms} on:input={e => drawWeier(d3.zoomIdentity)} /></label>
      </div>
    </div>
    <div class="chart-block">
      <div class="chart-title">Conjunto de Mandelbrot</div>
      <div bind:this={mandelContainer}></div>
      <div class="chart-controls">
        <label>Iterações<input type="number" min="20" max="1000" bind:value={maxIter} on:input={() => drawMandelbrot()} /></label>
      </div>
    </div>
  </div>
  