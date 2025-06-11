<script>
  import { onMount, onDestroy, createEventDispatcher } from "svelte";
  import * as d3 from "d3";
  import * as topojson from "topojson-client";

  const dispatch = createEventDispatcher();

  const width = 400;
  const height = 400;

  let svgEl;
  let tooltipEl;

  const MAP_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";
  const DATA_URL = `${import.meta.env.BASE_URL}data/mac_tutor_com_coords.json`;

  let projection;
  let pathGenerator;
  let allPoints = [];
  let landFeatures;

  // Velocidade de rotação: uma volta completa (360°) em 7.5 segundos
  const msPerRotation = 7500;
  const ANGULAR_SPEED = 360 / msPerRotation; // graus por ms

  // Controla o ângulo atual de rotação (em graus)
  let rotationAngle = 0;

  // Estados do timer
  let timer;
  let lastTime = 0;
  let isPaused = false;

  // Deslocamento manual de rotação (quando o usuário clica nos botões)
  let manualOffset = 0;

  // Filtragem por ano
  let minYear = 0;
  const currentYear = new Date().getFullYear();
  let thresholdYear = 0;
  let displayedPoints = [];

  // Extrai o ano, incluindo datas BC como número negativo
  function extrairAno(dataStr) {
    if (!dataStr || typeof dataStr !== "string") return null;

    const bcMatch = dataStr.match(/(\d+)\s*BC/i);
    if (bcMatch) {
      return -parseInt(bcMatch[1], 10);
    }

    const fullDate = new Date(dataStr);
    if (!isNaN(fullDate.getTime())) {
      return fullDate.getFullYear();
    }

    const fallbackMatch = dataStr.match(/(\d{3,4})/);
    if (fallbackMatch) {
      return parseInt(fallbackMatch[1], 10);
    }

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
    // Usa event.clientX/Y e position: fixed no CSS
    tooltipEl.style.left = event.clientX + 10 + "px";
    tooltipEl.style.top = event.clientY + 10 + "px";
  }

  function hideTooltip() {
    tooltipEl.style.opacity = "0";
    tooltipEl.style.pointerEvents = "none";
    tooltipEl.innerHTML = "";
  }

  // Atualiza quais pontos estão visíveis com base em thresholdYear e rotação atual
  function drawFrame() {
    projection.rotate([ -rotationAngle + manualOffset, -20, 0 ]);

    const rot = projection.rotate();
    const centerLon = -rot[0];
    const centerLat = -rot[1];
    displayedPoints = allPoints.filter(d => {
      if (d.birthYear > thresholdYear) return false;
      const distance = d3.geoDistance(d.coords, [centerLon, centerLat]);
      return distance <= Math.PI / 2;
    });

    const svg = d3.select(svgEl);
    svg.selectAll("path.land")
      .attr("d", pathGenerator(landFeatures));

    const pts = svg
      .select("g.points-group")
      .selectAll("circle.point")
      .data(displayedPoints, d => d.link);

    pts.join(
      enter => enter
        .append("circle")
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

  /**
   * tick:
   *  - 'now' é o timestamp (em ms) fornecido por d3.timer
   *  - calcula dt = now - lastTime para saber quantos ms se passaram
   *  - atualiza rotationAngle a uma taxa constante (ANGULAR_SPEED)
   *  - decide a taxa de avanço de thresholdYear conforme o período histórico:
   *      → < –800: 500 anos/s
   *      → –800 ≤ tYear < 1400: 100 anos/s
   *      → 1400 ≤ tYear < 1800: 50 anos/s
   *      → ≥ 1800: 10 anos/s
   */
  function tick(now) {
    if (isPaused) return;

    const dt = now - lastTime;
    lastTime = now;

    // 1) rotação suave constante
    rotationAngle = (rotationAngle + dt * ANGULAR_SPEED) % 360;

    // 2) escolhe taxa de avanço de thresholdYear em anos/segundo
    let yrsPerSecond;
    if (thresholdYear < -800) {
      yrsPerSecond = 500;
    } else if (thresholdYear < 1400) {
      yrsPerSecond = 100;
    } else if (thresholdYear < 1800) {
      yrsPerSecond = 50;
    } else {
      yrsPerSecond = 10;
    }

    // 3) atualiza thresholdYear com base no dt
    thresholdYear += (dt / 1000) * yrsPerSecond;
    if (thresholdYear > currentYear) {
      thresholdYear = currentYear;
    }

    // 4) redesenha o frame
    drawFrame();

    // 5) se já chegou ao ano atual, interrompe o timer
    if (thresholdYear >= currentYear) {
      if (timer) timer.stop();
      isPaused = true;
    }
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
    if (isPaused) {
      startAnimation();
    } else {
      stopAnimation();
    }
  }

  function rotateManual(delta) {
    manualOffset = (manualOffset + delta) % 360;
    drawFrame();
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

  onMount(async () => {
    // Inicializa a projeção ortográfica e o path generator
    projection = d3.geoOrthographic()
      .scale(width / 2 - 10)
      .translate([width / 2, height / 2])
      .clipAngle(90);
    pathGenerator = d3.geoPath(projection);

    // Carrega os contornos dos países
    try {
      const world = await d3.json(MAP_URL);
      landFeatures = topojson.feature(world, world.objects.countries);
    } catch {
      landFeatures = { type: "FeatureCollection", features: [] };
    }

    // Carrega os dados dos matemáticos
    try {
      const raw = await d3.json(DATA_URL);

      allPoints = raw
        .map(d => {
          const year = extrairAno(d.data_nascimento);
          if (year === null) return null;

          const lat = parseFloat(d.lat_nasc);
          const lon = parseFloat(d.lon_nasc);
          if (isNaN(lat) || isNaN(lon)) return null;

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
      } else {
        minYear = 0;
      }

      // Começa exibindo só quem nasceu até minYear (geralmente antigíssimos, com year negativo)
      thresholdYear = minYear;
      displayedPoints = [];
    } catch {
      allPoints = [];
      minYear = 0;
      thresholdYear = 0;
      displayedPoints = [];
    }

    // Desenha o círculo do globo, o path dos países e o grupo de pontos
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

    // Inicia a animação (rotação + avanço de eras)
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
    position: relative;
  }

  .right-pane {
    flex: 1;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: 2rem;
    background: #ffffff;
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
    position: fixed;          /* mudou de absolute para fixed */
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
    /* removido qualquer offset estático: deixamos ele “flutuando” */
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
    margin-top: 1rem;
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

  .intro-content ul {
    margin-left: 1.5rem;
    margin-bottom: 1rem;
  }

  :global(a) {
    color: steelblue;
    text-decoration: underline;
  }

  @media (max-width: 768px) {
    .home-container {
      flex-direction: column;
    }

    .left-pane,
    .right-pane {
      width: 100%;
      padding: 1rem;
    }

    svg {
      width: 100%;
      height: auto;
    }
  }
</style>

<div class="home-container">
  <!-- Esquerda: Globo interativo -->
  <div class="left-pane">
    <div class="globe-container">
      <svg bind:this={svgEl} width={width} height={height}></svg>
      <div bind:this={tooltipEl} id="tooltip"></div>
      <div class="label">
        Mostrando até <strong>{formatYear(Math.floor(thresholdYear))}</strong>
      </div>
      <div class="controls">
        <button on:click={togglePause}>
          {isPaused ? "Retomar" : "Pausar"}
        </button>
        <button on:click={() => rotateManual(-15)}>◀ Girar 15°</button>
        <button on:click={() => rotateManual(15)}>Girar 15° ▶</button>
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
      <button on:click={() => dispatch('navigate', 'dashboard')}>
        Explorar visualizações
      </button>
      <button on:click={() => dispatch('navigate', 'curves')}>
        curvas
      </button>
    </div>
  </div>
</div>
