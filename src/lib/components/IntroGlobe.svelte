<script>
  import { onMount, onDestroy } from "svelte";
  import * as d3 from "d3";
  import * as topojson from "topojson-client";

  const width = 400;
  const height = 400;
  const MAP_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";
  const DATA_URL = "data/mac_tutor_com_coords.json";

  let svgEl;
  let tooltipEl;

  let projection;
  let pathGenerator;
  let allPoints = [];
  let landFeatures;

  const msPerRotation = 7500;
  const ANGULAR_SPEED = 360 / msPerRotation;
  let rotationAngle = 0;
  let timer;
  let lastTime = 0;
  let isPaused = false;
  let manualOffset = 0;
  let minYear = 0;
  const currentYear = new Date().getFullYear();
  let thresholdYear = -1; // inicia mostrando apenas AC
  let displayedPoints = [];

  function extrairAno(dataStr) {
    if (!dataStr || typeof dataStr !== "string") return null;
    const bcMatch = dataStr.match(/(\d+)\s*BC/i);
    if (bcMatch) return -parseInt(bcMatch[1], 10);
    return null;
  }

  function formatYear(y) {
    return y < 0 ? `${-y} a.C.` : `${y}`;
  }

  function showTooltip(event, d) {
    tooltipEl.innerHTML = `
      <strong>${d.nome_completo}</strong><br/>
      <em>${formatYear(d.birthYear)}</em><br/>
      <a href="${d.link}" target="_blank" rel="noopener">Ver biografia</a>
    `;
    tooltipEl.style.opacity = "1";
    tooltipEl.style.pointerEvents = "auto";
    tooltipEl.style.left = event.clientX + 10 + "px";
    tooltipEl.style.top = event.clientY + 10 + "px";
  }

  function hideTooltip() {
    tooltipEl.style.opacity = "0";
    tooltipEl.style.pointerEvents = "none";
    tooltipEl.innerHTML = "";
  }

  function drawFrame() {
    projection.rotate([-rotationAngle + manualOffset, -20, 0]);
    const rot = projection.rotate();
    const centerLon = -rot[0];
    const centerLat = -rot[1];

    displayedPoints = allPoints.filter(d => {
      if (d.birthYear >= 0 || d.birthYear > thresholdYear) return false;
      const distance = d3.geoDistance(d.coords, [centerLon, centerLat]);
      return distance <= Math.PI / 2;
    });

    const svg = d3.select(svgEl);
    svg.selectAll("path.land").attr("d", pathGenerator(landFeatures));

    const pts = svg.select("g.points-group")
      .selectAll("circle.point")
      .data(displayedPoints, d => d.link);

    pts.join(
      enter => enter.append("circle")
        .attr("class", "point")
        .attr("r", 2)
        .attr("fill", "crimson")
        .attr("stroke", "#000")
        .attr("stroke-width", 0.3)
        .on("mouseover", (e, d) => showTooltip(e, d))
        .on("mouseout", hideTooltip)
        .on("click", (e, d) => window.open(d.link, "_blank"))
        .attr("cx", d => projection(d.coords)[0])
        .attr("cy", d => projection(d.coords)[1]),
      update => update
        .attr("cx", d => projection(d.coords)[0])
        .attr("cy", d => projection(d.coords)[1]),
      exit => exit.remove()
    );
  }

  function tick(now) {
    if (isPaused) return;
    const dt = now - lastTime;
    lastTime = now;
    rotationAngle = (rotationAngle + dt * ANGULAR_SPEED) % 360;
    drawFrame();
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

  function togglePause() {
    isPaused ? startAnimation() : stopAnimation();
  }

  function resetAnimation() {
    if (timer) timer.stop();
    rotationAngle = 0;
    manualOffset = 0;
    thresholdYear = minYear;
    displayedPoints = [];
    isPaused = false;
    startAnimation();
  }

  function rotateManual(delta) {
    manualOffset = (manualOffset + delta) % 360;
    drawFrame();
  }

  onMount(async () => {
    projection = d3.geoOrthographic()
      .scale(width / 2 - 10)
      .translate([width / 2, height / 2])
      .clipAngle(90);
    pathGenerator = d3.geoPath(projection);

    try {
      const world = await d3.json(MAP_URL);
      landFeatures = topojson.feature(world, world.objects.countries);
    } catch {
      landFeatures = { type: "FeatureCollection", features: [] };
    }

    try {
      const raw = await d3.json(DATA_URL);
      allPoints = raw
        .map(d => {
          const year = extrairAno(d.data_nascimento);
          const lat = parseFloat(d.lat_nasc);
          const lon = parseFloat(d.lon_nasc);
          if (year === null || isNaN(lat) || isNaN(lon)) return null;
          return {
            nome_completo: d.nome_completo,
            link: d.link,
            coords: [lon, lat],
            birthYear: year
          };
        })
        .filter(d => d !== null);

      if (allPoints.length) {
        minYear = Math.min(...allPoints.map(d => d.birthYear));
        thresholdYear = minYear;
      }
    } catch {
      allPoints = [];
    }

    const svg = d3.select(svgEl);
    svg.append("circle")
      .attr("cx", width / 2)
      .attr("cy", height / 2)
      .attr("r", width / 2 - 5)
      .attr("fill", "#e0eaff");

    svg.append("path")
      .attr("class", "land")
      .attr("fill", "#c0d8f0")
      .attr("stroke", "#888")
      .attr("stroke-width", 0.5);

    svg.append("g").attr("class", "points-group");

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
    justify-content: center;
    text-align: center;
  }

  svg {
    background: #fafbff;
    border-radius: 50%;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  }

  #tooltip {
    position: fixed;
    pointer-events: auto;
    background: white;
    padding: 4px 8px;
    border: 1px solid #666;
    border-radius: 4px;
    font-size: 0.8rem;
    opacity: 0;
    transition: opacity 0.2s;
    z-index: 10;
    font-family: sans-serif;
  }

  .label {
    margin-top: 1rem;
    font-size: 0.9rem;
    color: #444;
  }

  .controls {
    margin-top: 0.5rem;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
  }

  button {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
    cursor: pointer;
  }

  .intro-text {
    max-width: 600px;
    margin-top: 2rem;
    color: #333;
  }

  .intro-text h1 {
    font-size: 2rem;
    margin-bottom: 1rem;
  }
</style>

<div class="intro-section">
  <svg bind:this={svgEl} width={width} height={height}></svg>
  <div bind:this={tooltipEl} id="tooltip"></div>

  <div class="label">
    Mostrando até <strong>{formatYear(Math.floor(thresholdYear))}</strong>
  </div>

  <div class="controls">
    <button on:click={togglePause}>{isPaused ? "Retomar" : "Pausar"}</button>
    <button on:click={() => rotateManual(-15)}>◀ Girar 15°</button>
    <button on:click={() => rotateManual(15)}>Girar 15° ▶</button>
    <button on:click={resetAnimation}>Reiniciar</button>
  </div>

  <div class="intro-text">
    <h1>Bem-vindo à História da Matemática Antes de Cristo</h1>
    <p>
      Esta visualização interativa mostra os locais de nascimento de matemáticos antigos,
      rotacionando o globo enquanto avançamos no tempo até o ano 0.
    </p>
    <p>
      Explore os pioneiros do pensamento matemático e veja como suas ideias se espalharam por
      diferentes culturas e regiões da Antiguidade.
    </p>
  </div>
</div>
