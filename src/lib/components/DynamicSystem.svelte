<script>
    import { onMount } from 'svelte';
    import * as d3 from 'd3';
  
    // Dimensions
    const width = 800;
    const height = 600;
  
    // Default parameters
    const defaultParams = {
      length1: 200,
      length2: 200,
      mass1: 10,
      mass2: 10,
      gravity: 1,
      dt: 0.02,
      a1: Math.PI / 4,
      a2: Math.PI / 3,
      stepsPerFrame: 3,
      maxTraj: 2000,
      delta: 0.01,
      maxPendulums: 5
    };
  
    // Controls
    let numPendulums = 1;
    let length1 = defaultParams.length1;
    let length2 = defaultParams.length2;
    let gravity = defaultParams.gravity;
    let dt = defaultParams.dt;
    let stepsPerFrame = defaultParams.stepsPerFrame;
    let maxTraj = defaultParams.maxTraj;
    let delta = defaultParams.delta;
  
    // State
    let pendulums = [];
    let svg;
    let rodsGroup;
    let trajLines = [];
    let bob1Circles = [];
    let bob2Circles = [];
  
    function initPendulums() {
      // Clear existing arrays
      pendulums = [];
      trajLines.forEach(d => d.remove());
      bob1Circles.forEach(d => d.remove());
      bob2Circles.forEach(d => d.remove());
      trajLines = [];
      bob1Circles = [];
      bob2Circles = [];
  
      for (let i = 0; i < numPendulums; i++) {
        const angleOffset = (i - (numPendulums - 1) / 2) * delta;
        pendulums.push({
          a1: defaultParams.a1 + angleOffset,
          a2: defaultParams.a2 + angleOffset,
          a1_v: 0,
          a2_v: 0,
          traj: [],
          color: d3.schemeCategory10[i % 10]
        });
        // create elements
        trajLines[i] = svg.append('path')
          .attr('fill', 'none')
          .attr('stroke', d3.schemeCategory10[i % 10])
          .attr('stroke-width', 1)
          .attr('opacity', 0.7);
        bob1Circles[i] = svg.append('circle')
          .attr('r', defaultParams.mass1)
          .attr('fill', d3.schemeCategory10[i % 10])
          .attr('opacity', 0.9);
        bob2Circles[i] = svg.append('circle')
          .attr('r', defaultParams.mass2)
          .attr('fill', d3.schemeCategory10[i % 10])
          .attr('opacity', 0.9);
      }
    }
  
    function step(p) {
      const m1 = defaultParams.mass1;
      const m2 = defaultParams.mass2;
      const l1 = length1;
      const l2 = length2;
      const g = gravity;
  
      // Equations
      const num1 = -g * (2 * m1 + m2) * Math.sin(p.a1);
      const num2 = -m2 * g * Math.sin(p.a1 - 2 * p.a2);
      const num3 = -2 * Math.sin(p.a1 - p.a2) * m2;
      const num4 = p.a2_v * p.a2_v * l2 + p.a1_v * p.a1_v * l1 * Math.cos(p.a1 - p.a2);
      const den1 = l1 * (2 * m1 + m2 - m2 * Math.cos(2 * p.a1 - 2 * p.a2));
      const a1_a = (num1 + num2 + num3 * num4) / den1;
  
      const num5 = 2 * Math.sin(p.a1 - p.a2);
      const num6 = p.a1_v * p.a1_v * l1 * (m1 + m2);
      const num7 = g * (m1 + m2) * Math.cos(p.a1);
      const num8 = p.a2_v * p.a2_v * l2 * m2 * Math.cos(p.a1 - p.a2);
      const den2 = l2 * (2 * m1 + m2 - m2 * Math.cos(2 * p.a1 - 2 * p.a2));
      const a2_a = (num5 * (num6 + num7 + num8)) / den2;
  
      p.a1_v += a1_a * dt;
      p.a2_v += a2_a * dt;
      p.a1 += p.a1_v * dt;
      p.a2 += p.a2_v * dt;
  
      const x1 = width/2 + l1 * Math.sin(p.a1);
      const y1 = 100 + l1 * Math.cos(p.a1);
      const x2 = x1 + l2 * Math.sin(p.a2);
      const y2 = y1 + l2 * Math.cos(p.a2);
  
      p.traj.push([x2, y2]);
      if (p.traj.length > maxTraj) p.traj.shift();
      return { x1, y1, x2, y2 };
    }
  
    // re-init on change
    $: if (svg && numPendulums) initPendulums();
  
    onMount(() => {
      svg = d3.select('#pendulum-svg')
        .attr('width', width)
        .attr('height', height)
        .style('background', '#fff');
  
      rodsGroup = svg.append('g');
      initPendulums();
  
      d3.timer(() => {
        rodsGroup.selectAll('*').remove();
        pendulums.forEach((p, i) => {
          let coords;
          for (let k = 0; k < stepsPerFrame; k++) coords = step(p);
          if (!coords) return;
          const { x1, y1, x2, y2 } = coords;
          // rods
          rodsGroup.append('line')
            .attr('x1', width/2).attr('y1', 100)
            .attr('x2', x1).attr('y2', y1)
            .attr('stroke', '#333').attr('stroke-width', 1);
          rodsGroup.append('line')
            .attr('x1', x1).attr('y1', y1)
            .attr('x2', x2).attr('y2', y2)
            .attr('stroke', '#333').attr('stroke-width', 1);
          // bobs
          bob1Circles[i].attr('cx', x1).attr('cy', y1);
          bob2Circles[i].attr('cx', x2).attr('cy', y2);
          // traj
          trajLines[i].attr('d', d3.line()(p.traj));
        });
      });
    });
  </script>
  
  <div style="width:800px;margin:auto;color:#222;font-family:sans-serif;">
    <h2>Experimento de Pêndulos Duplos Caóticos</h2>
    <p>
      Este experimento foi originalmente desenvolvido por físicos clássicos para estudar sistemas dinâmicos não-lineares.<br>
      Usado em laboratórios de mecânica, demonstra como pequenas diferenças nas condições iniciais levam a trajetórias divergentes.<br>
      Ajuste o número de pêndulos, parâmetros e observe cada par de discos coloridos começando equidistantes!
    </p>
    <svg id="pendulum-svg"></svg>
    <div style="margin:20px 0;display:flex;flex-wrap:wrap;justify-content:space-around;color:#222;">
      <div><label>Número de pêndulos: <input type="number" min="1" max={defaultParams.maxPendulums} bind:value={numPendulums} /></label></div>
      <div><label>Comprimento 1: <input type="range" min="50" max="300" bind:value={length1} /></label></div>
      <div><label>Comprimento 2: <input type="range" min="50" max="300" bind:value={length2} /></label></div>
      <div><label>Gravidade: <input type="range" min="0.1" max="10" step="0.1" bind:value={gravity} /></label></div>
      <div><label>Δt: <input type="range" min="0.001" max="0.05" step="0.001" bind:value={dt} /></label></div>
      <div><label>Passos/quadro: <input type="range" min="1" max="10" bind:value={stepsPerFrame} /></label></div>
      <div><label>Trajetória máx.: <input type="range" min="100" max="5000" step="100" bind:value={maxTraj} /></label></div>
      <div><label>Offset inicial: <input type="range" min="0.001" max="0.1" step="0.001" bind:value={delta} /></label></div>
    </div>
    <div style="text-align:center;">
      <button on:click={() => initPendulums()}>Definir Iniciais</button>
      <button on:click={() => initPendulums()} style="margin-left:10px;">Reiniciar</button>
    </div>
  </div>
  
  <style>
    input[type="range"], input[type="number"] { width:120px; margin:0 5px; }
    button { padding:6px 12px; font-size:14px; border-radius:4px; border:none; background:#0074d9; color:#fff; cursor:pointer; }
    button:hover { background:#005fa3; }
  </style>