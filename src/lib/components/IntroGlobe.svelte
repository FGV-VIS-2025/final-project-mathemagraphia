<script>
  import { onMount, onDestroy } from 'svelte';
  import * as d3 from 'd3';
  import * as topojson from 'topojson-client';

  const MAP_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";
  const DATA_URL = "data/mac_tutor_com_coords.json";

  const width = 300;
  const height = 300;
  const START_YEAR = -1700;
  const END_YEAR = 2025;
  const ANGULAR_SPEED = 360 / 7500;

  let globeLeft, globeRight, tooltipEl;
  let projection1, projection2, path1, path2;
  let landFeatures = { type: "FeatureCollection", features: [] };
  let allPoints = [], displayedPoints = [];
  let rotationAngle = 0, thresholdYear = START_YEAR;

  let timer, lastTime = 0;
  let isPaused = false;

  function extrairAno(dataStr) {
    const bc = dataStr?.match(/(\d+)\s*BC/i);
    if (bc) return -parseInt(bc[1]);
    const y = dataStr?.match(/(\d{3,4})/);
    return y ? +y[1] : null;
  }

  function formatYear(y) {
    return y < 0 ? `${-y} a.C.` : `${y}`;
  }

  function drawGlobe(svg, projection, path) {
    svg.selectAll('*').remove();

    svg.append("circle")
      .attr("cx", width / 2)
      .attr("cy", height / 2)
      .attr("r", width / 2 - 5)
      .attr("fill", "#e0eaff");

    svg.append("path")
      .attr("class", "land")
      .attr("d", path(landFeatures))
      .attr("fill", "#c0d8f0")
      .attr("stroke", "#888")
      .attr("stroke-width", 0.5);

    const visiblePoints = allPoints.filter(d => {
      if (d.birthYear > thresholdYear) return false;
      const center = projection.invert([width / 2, height / 2]);
      const dist = d3.geoDistance(d.coords, center);
      return dist <= Math.PI / 2;
    });

    svg.append("g")
      .selectAll("circle")
      .data(visiblePoints)
      .join("circle")
        .attr("r", 2)
        .attr("fill", "crimson")
        .attr("stroke", "#000")
        .attr("stroke-width", 0.3)
        .attr("cx", d => projection(d.coords)[0])
        .attr("cy", d => projection(d.coords)[1])
        .on("mouseover", (e, d) => {
          tooltipEl.innerHTML = `<strong>${d.nome_completo}</strong><br/><em>${formatYear(d.birthYear)}</em>`;
          tooltipEl.style.opacity = 1;
          tooltipEl.style.left = `${e.clientX + 10}px`;
          tooltipEl.style.top = `${e.clientY + 10}px`;
        })
        .on("mouseout", () => {
          tooltipEl.style.opacity = 0;
        });
  }

  function draw() {
    projection1.rotate([-rotationAngle, -20, 0]);
    projection2.rotate([-rotationAngle + 180, -20, 0]);
    drawGlobe(d3.select(globeLeft), projection1, path1);
    drawGlobe(d3.select(globeRight), projection2, path2);
  }

  function tick(now) {
    if (isPaused) return;
    const dt = now - lastTime;
    lastTime = now;
    rotationAngle = (rotationAngle + dt * ANGULAR_SPEED) % 360;

    let rate = thresholdYear < -800 ? 500 : thresholdYear < 1400 ? 100 : thresholdYear < 1800 ? 50 : 10;
    thresholdYear += (dt / 1000) * rate;
    if (thresholdYear > END_YEAR) {
      thresholdYear = END_YEAR;
      stopAnimation();
    }

    draw();
  }

  function startAnimation() {
    if (timer) timer.stop();
    isPaused = false;
    lastTime = d3.now();
    timer = d3.timer(tick);
  }

  function stopAnimation() {
    if (timer) timer.stop();
    isPaused = true;
  }

  function reset() {
    stopAnimation();
    rotationAngle = 0;
    thresholdYear = START_YEAR;
    draw();
    requestAnimationFrame(() => {
      lastTime = d3.now();
      startAnimation();
    });
  }

  onMount(async () => {
    projection1 = d3.geoOrthographic().scale(width / 2 - 10).translate([width / 2, height / 2]).clipAngle(90);
    projection2 = d3.geoOrthographic().scale(width / 2 - 10).translate([width / 2, height / 2]).clipAngle(90);
    path1 = d3.geoPath(projection1);
    path2 = d3.geoPath(projection2);

    const world = await d3.json(MAP_URL);
    if (world && world.objects && world.objects.countries) {
      const countries = topojson.feature(world, world.objects.countries);
      landFeatures = {
        type: "FeatureCollection",
        features: Array.isArray(countries.features) ? countries.features : []
      };
    }

    const raw = await d3.json(DATA_URL);
    allPoints = raw.map(d => {
      const y = extrairAno(d.data_nascimento);
      const lat = parseFloat(d.lat_nasc);
      const lon = parseFloat(d.lon_nasc);
      if (y == null || isNaN(lat) || isNaN(lon)) return null;
      return { nome_completo: d.nome_completo, birthYear: y, coords: [lon, lat], link: d.link };
    }).filter(Boolean);

    startAnimation();
  });

  onDestroy(() => {
    if (timer) timer.stop();
  });
</script>


<style>
  .intro-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 3rem 1rem;
    background: #f8fafc;
    text-align: center;
  }

  .intro-text {
    max-width: 700px;
    margin-bottom: 2rem;
  }

  .intro-text h1 {
    font-size: 2rem;
    margin-bottom: 1rem;
  }

  .intro-text p {
    color: #333;
    margin: 0.5rem 0;
  }

  .double-globe {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 2rem;
  }

  svg {
    background: #fff;
    border-radius: 50%;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  }

  .label {
    text-align: center;
    font-size: 1rem;
    margin-top: 1rem;
  }

  .controls {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1rem;
  }

  button {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
    cursor: pointer;
  }

  #tooltip {
    position: fixed;
    background: white;
    border: 1px solid #ccc;
    padding: 6px 8px;
    font-size: 0.8rem;
    border-radius: 4px;
    pointer-events: none;
    opacity: 0;
    z-index: 100;
    transition: opacity 0.2s;
  }
</style>

<div class="intro-section">
  <div class="intro-text">
    <h1>Bem-vindo à História da Matemática</h1>
    <p>
      Esta visualização interativa mostra os locais de nascimento de matemáticos
      desde <strong>1700 a.C.</strong> até os tempos modernos.
    </p>
    <p>
      À esquerda, vemos uma face do globo. À direita, a face oposta. 
      Isso permite observar simultaneamente contribuições do oriente e do ocidente,
      ou comparar civilizações que coexistiram sem contato.
    </p>
  </div>

  <div class="double-globe">
    <svg bind:this={globeLeft} width={width} height={height}></svg>
    <svg bind:this={globeRight} width={width} height={height}></svg>
    <div bind:this={tooltipEl} id="tooltip"></div>
  </div>

  <div class="label">Mostrando até <strong>{formatYear(Math.floor(thresholdYear))}</strong></div>

  <div class="controls">
    <button on:click={() => isPaused ? startAnimation() : stopAnimation()}>
      {isPaused ? 'Retomar' : 'Pausar'}
    </button>
    <button on:click={reset}>Reiniciar</button>
  </div>
</div>
