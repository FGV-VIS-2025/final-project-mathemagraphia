<script>
    import { onMount } from 'svelte';
    import * as d3 from 'd3';
  
    // Dimensions
    const width = 800;
    const height = 600;
  
    // Default parameters
    const default = {
      length1: 200,
      length2: 200,
      mass1: 20,
      mass2: 20,
      gravity: 1,
      dt: 0.02,
      a1: Math.PI / 4,
      a2: Math.PI / 3
    };
  
    // State variables
    let length1 = default.length1;
    let length2 = default.length2;
    let mass1 = default.mass1;
    let mass2 = default.mass2;
    let gravity = default.gravity;
    let dt = default.dt;
    let a1 = default.a1;
    let a2 = default.a2;
    let a1_v = 0;
    let a2_v = 0;
    let traj = [];
  
    // For selecting initial angles
    let initA1 = default.a1;
    let initA2 = default.a2;
  
    let svg, rods, bob1, bob2, trajLine;
  
    function stepPendulum() {
      const m1 = mass1;
      const m2 = mass2;
      const l1 = length1;
      const l2 = length2;
      const g = gravity;
  
      const num1 = -g * (2 * m1 + m2) * Math.sin(a1);
      const num2 = -m2 * g * Math.sin(a1 - 2 * a2);
      const num3 = -2 * Math.sin(a1 - a2) * m2;
      const num4 = a2_v * a2_v * l2 + a1_v * a1_v * l1 * Math.cos(a1 - a2);
      const den1 = l1 * (2 * m1 + m2 - m2 * Math.cos(2 * a1 - 2 * a2));
      const a1_a = (num1 + num2 + num3 * num4) / den1;
  
      const num5 = 2 * Math.sin(a1 - a2);
      const num6 = a1_v * a1_v * l1 * (m1 + m2);
      const num7 = g * (m1 + m2) * Math.cos(a1);
      const num8 = a2_v * a2_v * l2 * m2 * Math.cos(a1 - a2);
      const den2 = l2 * (2 * m1 + m2 - m2 * Math.cos(2 * a1 - 2 * a2));
      const a2_a = (num5 * (num6 + num7 + num8)) / den2;
  
      a1_v += a1_a * dt;
      a2_v += a2_a * dt;
      a1 += a1_v * dt;
      a2 += a2_v * dt;
  
      const x1 = width/2 + l1 * Math.sin(a1);
      const y1 = 100 + l1 * Math.cos(a1);
      const x2 = x1 + l2 * Math.sin(a2);
      const y2 = y1 + l2 * Math.cos(a2);
  
      traj.push([x2, y2]);
      if (traj.length > 1000) traj.shift();
    }
  
    function resetSimulation() {
      a1 = default.a1;
      a2 = default.a2;
      a1_v = 0;
      a2_v = 0;
      traj = [];
    }
  
    function setInitial() {
      a1 = +initA1;
      a2 = +initA2;
      a1_v = 0;
      a2_v = 0;
      traj = [];
    }
  
    onMount(() => {
      svg = d3.select('#pendulum-svg')
        .attr('width', width)
        .attr('height', height)
        .style('background', '#f0f0f0');
  
      rods = svg.append('g');
      bob1 = svg.append('circle').attr('r', mass1).attr('fill', '#ff4136');
      bob2 = svg.append('circle').attr('r', mass2).attr('fill', '#0074d9');
      trajLine = svg.append('path')
        .attr('fill', 'none')
        .attr('stroke', '#002f4b')
        .attr('stroke-width', 1)
        .attr('opacity', 0.7);
  
      d3.timer(() => {
        stepPendulum();
  
        const x1 = width/2 + length1 * Math.sin(a1);
        const y1 = 100 + length1 * Math.cos(a1);
        const x2 = x1 + length2 * Math.sin(a2);
        const y2 = y1 + length2 * Math.cos(a2);
  
        rods.selectAll('line').remove();
        rods.append('line')
          .attr('x1', width/2).attr('y1', 100)
          .attr('x2', x1).attr('y2', y1)
          .attr('stroke', '#333').attr('stroke-width', 2);
        rods.append('line')
          .attr('x1', x1).attr('y1', y1)
          .attr('x2', x2).attr('y2', y2)
          .attr('stroke', '#333').attr('stroke-width', 2);
  
        bob1.attr('cx', x1).attr('cy', y1);
        bob2.attr('cx', x2).attr('cy', y2);
  
        trajLine.attr('d', d3.line()(traj));
      });
    });
  </script>
  
  <div style="width: 800px; margin: auto; text-align: center;">
    <h2>Simulação Interativa do Pêndulo Duplo</h2>
    <svg id="pendulum-svg"></svg>
    <div style="margin-top: 20px; display: flex; justify-content: space-around; flex-wrap: wrap;">
      <div>
        <label>Comprimento 1: <input type="range" min="50" max="300" bind:value={length1} /></label>
      </div>
      <div>
        <label>Comprimento 2: <input type="range" min="50" max="300" bind:value={length2} /></label>
      </div>
      <div>
        <label>Gravidade: <input type="range" min="0.1" max="5" step="0.1" bind:value={gravity} /></label>
      </div>
      <div>
        <label>Velocidade (dt): <input type="range" min="0.005" max="0.1" step="0.005" bind:value={dt} /></label>
      </div>
      <div>
        <label>Ângulo Inicial 1: <input type="range" min="0" max="6.283" step="0.01" bind:value={initA1} /></label>
      </div>
      <div>
        <label>Ângulo Inicial 2: <input type="range" min="0" max="6.283" step="0.01" bind:value={initA2} /></label>
      </div>
    </div>
    <div style="margin-top: 20px;">
      <button on:click={setInitial}>Definir Posição Inicial</button>
      <button on:click={resetSimulation} style="margin-left:10px;">Reiniciar</button>
    </div>
  </div>
  
  <style>
    input[type="range"] { width: 150px; }
    h2 { font-family: sans-serif; margin-bottom: 10px; }
    button { padding: 6px 12px; font-size: 14px; border-radius: 4px; border: none; background: #0074d9; color: #fff; cursor: pointer; }
    button:hover { background: #005fa3; }
  </style>
  