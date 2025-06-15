<script>
    import { onMount } from 'svelte';
    import * as d3 from 'd3';
    import { zoom as d3Zoom } from 'd3-zoom';
    import { tweened } from 'svelte/motion';
    import { cubicInOut } from 'svelte/easing';
  
    // Dimensions
    export let weierWidth = 900;
    export let weierHeight = 600;
    export let mandelWidth = 900;
    export let mandelHeight = 600;
  
    // Weierstrass parameters
    let amplitude = 1;
    let freq = 2;
    let terms = 20;
    let showAxes = true;
    let animateTerms = false;
    let weierTimer;
  
    // Mandelbrot parameters
    let maxIter = 200;
    let iterMin = 20;
    let iterMax = 500;
    let iterStep = 5;
    let animateIter = false;
    let iterDir = 1;
    let centerX = -0.5;
    let centerY = 0;
    let zoomLevel = 1;
  
    let weierContainer, mandelContainer;
    let svgW, gW;
    let iterTimer;
  
    const mandelConfig = { xMin: -2, xMax: 1, yMin: -1.5, yMax: 1.5 };
  
    function computeData(xMin, xMax, pts = weierWidth * 2, N = terms) {
      // compute normalization factor
      const norm = d3.range(0, N).reduce((s, n) => s + Math.pow(freq, -n), 0);
      return d3.range(xMin, xMax, (xMax - xMin) / pts).map(x => {
        let y = 0;
        for (let n = 0; n < N; n++) {
          y += Math.pow(freq, -n) * Math.cos(Math.pow(freq, n) * x);
        }
        return { x, y: (y * amplitude) / norm };
      });
    }
  
    function drawWeier() {
      const data = computeData(-Math.PI, Math.PI);
      const x0 = d3.scaleLinear().domain([-Math.PI, Math.PI]).range([0, weierWidth]);
      const y0 = d3.scaleLinear().domain(d3.extent(data, d => d.y)).range([weierHeight, 0]);
  
      // update axes
      if (showAxes) {
        gW.select('.x-axis').call(d3.axisBottom(x0).ticks(8));
        gW.select('.y-axis').call(d3.axisLeft(y0).ticks(6));
      } else {
        gW.selectAll('.x-axis, .y-axis').selectAll('*').remove();
      }
  
      const line = d3.line().x(d => x0(d.x)).y(d => y0(d.y));
      gW.select('.weier-path').datum(data).attr('d', line);
    }
  
    function drawPartialSums() {
      const checkpoints = 5;
      const step = Math.floor(terms / checkpoints) || 1;
      const color = d3.scaleOrdinal(d3.schemeCategory10);
  
      gW.selectAll('.partial-sum').remove();
      for (let i = step; i <= terms; i += step) {
        const ds = computeData(-Math.PI, Math.PI, weierWidth * 2, i);
        gW.append('path')
          .datum(ds)
          .attr('class', 'partial-sum')
          .attr('d', d3.line()
            .x(d => d3.scaleLinear().domain([-Math.PI, Math.PI]).range([0, weierWidth])(d.x))
            .y(d => d3.scaleLinear().domain(d3.extent(ds, d => d.y)).range([weierHeight, 0])(d.y))
          )
          .attr('stroke', color(i))
          .attr('fill', 'none')
          .attr('stroke-width', 1)
          .attr('opacity', 0.6);
      }
    }
  
    function drawMandelbrot() {
      const canvas = d3.select(mandelContainer)
        .selectAll('canvas').data([null])
        .join('canvas')
        .attr('width', mandelWidth)
        .attr('height', mandelHeight)
        .classed('mandel-canvas', true);
  
      const ctx = canvas.node().getContext('2d');
      const img = ctx.createImageData(mandelWidth, mandelHeight);
  
      const xRange = (mandelConfig.xMax - mandelConfig.xMin) / zoomLevel;
      const yRange = (mandelConfig.yMax - mandelConfig.yMin) / zoomLevel;
      const xMin = centerX - xRange / 2;
      const yMin = centerY - yRange / 2;
  
      for (let px = 0; px < mandelWidth; px++) {
        for (let py = 0; py < mandelHeight; py++) {
          const x0 = xMin + (px / mandelWidth) * xRange;
          const y0 = yMin + (py / mandelHeight) * yRange;
          let x = 0, y = 0, iter = 0;
          while (x*x + y*y <= 4 && iter < maxIter) {
            const xt = x*x - y*y + x0;
            y = 2*x*y + y0;
            x = xt;
            iter++;
          }
          const c = iter === maxIter ? 0 : 255 - Math.floor(255 * iter / maxIter);
          const idx = (py * mandelWidth + px) * 4;
          img.data[idx] = img.data[idx+1] = img.data[idx+2] = c;
          img.data[idx+3] = 255;
        }
      }
      ctx.putImageData(img, 0, 0);
    }
  
    function toggleIterAnim() {
      animateIter = !animateIter;
    }
  
    function toggleTermsAnim() {
      animateTerms = !animateTerms;
      if (animateTerms) {
        weierTimer = setInterval(() => {
          if (terms < 500) {
            terms += 5;
            drawWeier();
            drawPartialSums();
          } else {
            clearInterval(weierTimer);
            animateTerms = false;
          }
        }, 200);
      } else {
        clearInterval(weierTimer);
      }
    }
  
    onMount(() => {
      const margin = { top: 40, right: 20, bottom: 50, left: 60 };
      svgW = d3.select(weierContainer).append('svg')
        .attr('width', weierWidth + margin.left + margin.right)
        .attr('height', weierHeight + margin.top + margin.bottom)
        .style('background', '#fff')
        .style('box-shadow', '0 2px 8px rgba(0,0,0,0.1)')
        .call(d3Zoom()
          .scaleExtent([1, 100])
          .on('zoom', ({transform}) => {
            const zx = transform.rescaleX(d3.scaleLinear().domain([-Math.PI, Math.PI]).range([0, weierWidth]));
            const zy = transform.rescaleY(d3.scaleLinear().domain(d3.extent(computeData(-Math.PI, Math.PI), d=>d.y)).range([weierHeight, 0]));
            gW.select('.x-axis').call(d3.axisBottom(zx));
            gW.select('.y-axis').call(d3.axisLeft(zy));
            gW.select('.weier-path')
              .attr('d', d3.line()
                .x(d => transform.applyX(d3.scaleLinear().domain([-Math.PI, Math.PI]).range([0, weierWidth])(d.x)))
                .y(d => transform.applyY(d3.scaleLinear().domain(d3.extent(computeData(-Math.PI, Math.PI), d=>d.y)).range([weierHeight, 0])(d.y)))
                (computeData(-Math.PI, Math.PI))
              );
          })
        );
  
      svgW.append('text')
        .attr('x', margin.left)
        .attr('y', 24)
        .style('font-size', '1.3rem')
        .style('font-weight', '600')
        .text('Função de Weierstrass – Fractal (1872)');
  
      gW = svgW.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
      gW.append('g').attr('class', 'x-axis').attr('transform', `translate(0,${weierHeight})`);
      gW.append('g').attr('class', 'y-axis');
      gW.append('path').attr('class', 'weier-path').attr('fill', 'none').attr('stroke', '#007acc').attr('stroke-width', 2);
  
      drawWeier();
      drawPartialSums();
      drawMandelbrot();
  
      iterTimer = setInterval(() => {
        if (animateIter) {
          maxIter += iterDir * iterStep;
          if (maxIter >= iterMax || maxIter <= iterMin) iterDir *= -1;
          drawMandelbrot();
        }
      }, 500);
    });
  </script>
  
  <style>
    .container { max-width: 1000px; margin: auto; }
    .chart-block { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 2rem; }
    .chart-area { overflow: hidden; }
    .control-panel { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1rem; }
    .control-panel label { display: flex; flex-direction: column; font-size: 0.9rem; }
    canvas { width: 100%; height: auto; display: block; }
    button { padding: 0.4rem 1rem; border: none; background: #007acc; color: white; border-radius: 5px; cursor: pointer; font-weight: bold; }
  </style>
  
  <div class="container">
    <div class="chart-block">
      <div class="chart-area">
        <div bind:this={weierContainer}></div>
      </div>
      <div class="control-panel">
        <label>Amplitude
          <input type="range" min="0.1" max="5" step="0.1" bind:value={amplitude} on:input={() => { drawWeier(); drawPartialSums(); }} />
        </label>
        <label>Frequência
          <input type="range" min="2" max="8" step="1" bind:value={freq} on:input={() => { drawWeier(); drawPartialSums(); }} />
        </label>
        <label>Termos
          <input type="number" min="5" max="500" bind:value={terms} on:input={() => { drawWeier(); drawPartialSums(); }} />
        </label>
        <label>
          <input type="checkbox" bind:checked={showAxes} on:change={() => drawWeier()} />
          Mostrar Eixos
        </label>
        <button on:click={toggleTermsAnim}>
          {animateTerms ? 'Parar Animação' : 'Animação dos Termos'}
        </button>
      </div>
    </div>
  
    <div class="chart-block">
      <div class="chart-area">
        <div bind:this={mandelContainer}></div>
      </div>
      <div class="control-panel">
        <label>Iterações
          <input type="range" min="20" max="1000" step="1" bind:value={maxIter} on:input={() => drawMandelbrot()} />
        </label>
        <label>Centro X
          <input type="range" min="-2" max="2" step="0.01" bind:value={centerX} on:input={() => drawMandelbrot()} />
        </label>
        <label>Centro Y
          <input type="range" min="-2" max="2" step="0.01" bind:value={centerY} on:input={() => drawMandelbrot()} />
        </label>
        <label>Zoom
          <input type="range" min="1" max="10" step="0.1" bind:value={zoomLevel} on:input={() => drawMandelbrot()} />
        </label>
        <button on:click={toggleIterAnim}>
          {animateIter ? 'Parar Animação' : 'Animar Iterações'}
        </button>
      </div>
    </div>
  </div>
  