<script>
  import { onMount, onDestroy } from "svelte";
  import * as d3 from "d3";
  import * as topojson from "topojson-client";

  const width = 400;
  const height = 400;

  let svgEl;
  let tooltipEl;

  const MAP_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";
  const DATA_URL = "public/data/biografias_coords.json";

  let projection;
  let pathGenerator;
  let allPoints = [];
  let landFeatures;

  // Animação
  const msPerRotation = 10000;  // 10 segundos por volta
  let timer;

  // Controle de tempo/pausa
  let startTime = 0;           
  let accumulated = 0;         
  let isPaused = false;        

  // Controle manual de rotação
  let manualRotation = 0;      

  // Filtragem por ano
  let minYear = 0;
  const currentYear = new Date().getFullYear();
  let thresholdYear = 0;
  let displayedPoints = [];

  function formatYear(y) {
    return y < 0 ? `${-y} BC` : `${y}`;
  }

  function showTooltip(event, d) {
    const bounds = svgEl.getBoundingClientRect();
    tooltipEl.innerHTML = `
      <strong>${d.nome_completo}</strong><br/>
      <em>${formatYear(d.birthYear)}</em><br/>
      <a href="${d.link}" target="_blank" rel="noopener">Ver biografia</a>
    `;
    tooltipEl.style.opacity = "1";
    tooltipEl.style.pointerEvents = "auto";
    tooltipEl.style.left = event.clientX - bounds.left + 10 + "px";
    tooltipEl.style.top = event.clientY - bounds.top - 28 + "px";
  }

  function hideTooltip() {
    tooltipEl.style.opacity = "0";
    tooltipEl.style.pointerEvents = "none";
    tooltipEl.innerHTML = "";
  }

  function updateDisplayed(elapsed) {
    const totalElapsed = accumulated + elapsed;
    const yearsFromStart = Math.floor(totalElapsed / 1000) * 20;
    thresholdYear = minYear + yearsFromStart;
    if (thresholdYear > currentYear) thresholdYear = currentYear;

    const angleBase = ((totalElapsed % msPerRotation) / msPerRotation) * 360;
    const totalAngle = angleBase + manualRotation;
    projection.rotate([-totalAngle, -20, 0]);

    const rot = projection.rotate();
    const centerLon = -rot[0];
    const centerLat = -rot[1];

    displayedPoints = allPoints.filter(d => {
      if (d.birthYear > thresholdYear) return false;
      const distance = d3.geoDistance(d.coords, [centerLon, centerLat]);
      return distance <= Math.PI / 2;
    });
  }

  function drawFrame(elapsed) {
    updateDisplayed(elapsed);
    const svg = d3.select(svgEl);
    svg.selectAll("path.land")
      .attr("d", pathGenerator(landFeatures));

    const pts = svg.selectAll("circle.point").data(displayedPoints, d => d.link);
    pts.join(
      enter =>
        enter.append("circle")
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
      update =>
        update
          .attr("cx", d => projection(d.coords)[0])
          .attr("cy", d => projection(d.coords)[1]),
      exit => exit.remove()
    );
  }

  function startAnimation() {
    isPaused = false;
    startTime = d3.now();
    timer = d3.timer(elapsed => {
      drawFrame(elapsed);
      if (thresholdYear >= currentYear) {
        stopAnimation();
      }
    });
  }

  function stopAnimation() {
    if (timer) timer.stop();
    accumulated += d3.now() - startTime;
    isPaused = true;
  }

  function togglePause() {
    if (isPaused) {
      startAnimation();
    } else {
      stopAnimation();
    }
  }

  function rotateManual(delta) {
    manualRotation = (manualRotation + delta) % 360;
    if (manualRotation < 0) manualRotation += 360;
    if (isPaused) {
      drawFrame(0);
    }
  }

  function resetAnimation() {
    if (timer) timer.stop();
    accumulated = 0;
    manualRotation = 0;
    thresholdYear = minYear;
    displayedPoints = [];
    isPaused = false;
    startAnimation();
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
      allPoints = raw.map(d => {
        let year = null;
        const yn = (d.ano_nascimento || "").trim();
        if (yn.endsWith("BC")) {
          const n = parseInt(yn.replace("BC", "").trim());
          year = isNaN(n) ? null : -n;
        } else {
          const n = parseInt(yn);
          year = isNaN(n) ? null : n;
        }
        if (
          d.coords_nascimento &&
          typeof d.coords_nascimento.lat === "number" &&
          typeof d.coords_nascimento.lon === "number" &&
          year !== null
        ) {
          return {
            nome_completo: d.nome_completo,
            link: d.link,
            coords: [d.coords_nascimento.lon, d.coords_nascimento.lat],
            birthYear: year
          };
        }
        return null;
      }).filter(d => d !== null);

      if (allPoints.length) {
        minYear = Math.min(...allPoints.map(d => d.birthYear));
        if (minYear > 0) minYear = 0;
      }
    } catch {
      allPoints = [];
      minYear = 0;
    }

    const svg = d3.select(svgEl);
    svg
      .append("circle")
      .attr("cx", width / 2)
      .attr("cy", height / 2)
      .attr("r", width / 2 - 5)
      .attr("fill", "#e0eaff");

    svg
      .append("path")
      .attr("class", "land")
      .attr("d", pathGenerator(landFeatures))
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
  .home-container {
    display: flex;
    height: 100vh;
  }

  .left-pane {
    width: 40%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #fafbff;
    padding: 1rem;
  }

    .right-pane {
    flex: 1;
    display: flex;
    align-items: flex-start;    /* substituído de center para flex-start */
    justify-content: center;
    padding: 2rem;
    background: #ffffff;
    /* opcional: adiciona um pouco de espaço extra no topo */
    padding-top: 0rem;
    }

  .globe-container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  svg {
    background: #fafbff;
    border-radius: 50%;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  }

  #tooltip {
    position: absolute;
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

  .controls {
    margin-top: 0.5rem;
    display: flex;
    gap: 0.5rem;
  }

  button {
    padding: 0.3rem 0.6rem;
    font-size: 0.9rem;
    cursor: pointer;
  }

  .label {
    margin-top: 0.5rem;
    font-size: 0.9rem;
    color: #444;
  }

  .intro-content {
    max-width: 600px;
    text-align: left;
    line-height: 1.5;
    color: #333;
  }

  .intro-content h1 {
    margin-bottom: 1rem;
    font-size: 2rem;
    color: #222;
  }

  .intro-content p {
    margin-bottom: 1rem;
  }

  :global(a) {
    color: steelblue;
    text-decoration: underline;
  }
</style>

<div class="home-container">
  <!-- Esquerda: Globo interativo -->
  <div class="left-pane">
    <div class="globe-container">
      <svg bind:this={svgEl} width={width} height={height}></svg>
      <div bind:this={tooltipEl} id="tooltip"></div>
      <div class="label">
        Mostrando até <strong>{formatYear(thresholdYear)}</strong>
      </div>
      <div class="controls">
        <button on:click={togglePause}>
          {isPaused ? "Retomar" : "Pausar"}
        </button>
        <button on:click={() => rotateManual(-10)}>◀ Girar 10°</button>
        <button on:click={() => rotateManual(10)}>Girar 10° ▶</button>
        <button on:click={resetAnimation}>Reiniciar</button>
      </div>
    </div>
  </div>

  <!-- Direita: Apresentação / Conteúdo -->
  <div class="right-pane">
    <div class="intro-content">
      <h1>Bem‐vindo ao MathemaGraphia!</h1>
      <p>
        Esse é um projeto que visa tornar o estudo e o interesse pela matemática
        (e tópicos que a envolvam) mais acessível e divertido através do uso de visualizações.
      </p>
      <p>
        Um de nossos objetivos é que o MathemaGraphia sirva como um acervo matemático
        e como uma galeria de visualizações. Em nossas visualizações, utilizamos dados de:
      </p>
      <ul>
        <li>
          <a href="https://mathshistory.st-andrews.ac.uk/" target="_blank" rel="noopener">
            mathshistory.st-andrews.ac.uk
          </a>
        </li>
        <li>
          <a href="https://web.archive.org/web/20200219183933/http://www.mat.uc.pt/~jaimecs/euclid/elem.html"
             target="_blank" rel="noopener">
            Arquivo de “Os Elementos” de Euclides
          </a>
        </li>
      </ul>
      <p>
        Na aba <strong>DataGraphs</strong>, separamos algumas visualizações que podem despertar
        o interesse do usuário em explorar diferentes combinações e parâmetros, como, por exemplo,
        um grafo de citações biográficas. Já na aba <strong>History</strong>, focamos num propósito
        mais voltado ao estudo e entendimento de marcos históricos, como o livro “Os Elementos” de Euclides.
      </p>
      <p>
        Esperamos que você se divirta enquanto explora esse mundo belo que a matemática nos proporcionou!
      </p>
      <br>
    </div>
  </div>
</div>
