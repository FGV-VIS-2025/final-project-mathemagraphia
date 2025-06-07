<script>
  // --------------------------------------------------
  // Dados estáticos das eras (você pode trocar pelos seus)
  // --------------------------------------------------
  const eras = [
    {
      id: 'era-antiga',
      title: 'Era Antiga',
      subtitle: '300 a.C. – 500 d.C.',
      description:
        'Nesta era, surgiram os principais fundamentos da Geometria. Destaque para Euclides e Arquimedes.',
      mathematicians: [
        { name: 'Euclides', years: '300 a.C. – 265 a.C.' },
        { name: 'Arquimedes', years: '287 a.C. – 212 a.C.' },
        { name: 'Ptolomeu', years: '100 d.C. – 170 d.C.' }
      ]
    },
    {
      id: 'era-medieval',
      title: 'Era Medieval',
      subtitle: '500 d.C. – 1400 d.C.',
      description:
        'Período marcado pelo trabalho de matemáticos como Al-Khwarizmi (álgebra) e Fibonacci (números).',
      mathematicians: [
        { name: 'Al-Khwarizmi', years: '780 – 850' },
        { name: 'Fibonacci', years: '1170 – 1250' },
        { name: 'Omar Khayyam', years: '1048 – 1131' }
      ]
    },
    {
      id: 'renascenca',
      title: 'Renascença',
      subtitle: '1400 d.C. – 1600 d.C.',
      description:
        'Recuperação do saber clássico e novos avanços em Álgebra e Geometria Analítica. Destaque para Cardano e Tartaglia.',
      mathematicians: [
        { name: 'Cardano', years: '1501 – 1576' },
        { name: 'Tartaglia', years: '1500 – 1557' },
        { name: 'Viète', years: '1540 – 1603' }
      ]
    },
    {
      id: 'revolucao-cientifica',
      title: 'Revolução Científica',
      subtitle: '1600 d.C. – 1800 d.C.',
      description:
        'Burtilho de métodos analíticos. Destacam-se Descartes, Newton e Leibniz.',
      mathematicians: [
        { name: 'Descartes', years: '1596 – 1650' },
        { name: 'Newton', years: '1643 – 1727' },
        { name: 'Leibniz', years: '1646 – 1716' }
      ]
    }
  ];

  /**
   * Ao clicar em “Ver Visualização” dentro de uma seção de era,
   * por enquanto vamos rolar até a seção “#data-graph”. Se quiser
   * rolar para outra parte, ajuste o seletor dentro de scrollIntoView.
   */
  function scrollToVisualization() {
    const alvo = document.getElementById('data-graph');
    if (alvo) {
      alvo.scrollIntoView({ behavior: 'smooth' });
    }
  }
</script>

<!-- ====================================================================
   HEADER (Sticky) – exibe a navegação para subpáginas
   ==================================================================== -->
<header class="header">
  <nav class="nav">
    <div class="nav__logo">MathemaGraphia</div>
    <ul class="nav__links">
      <li><a href="/">Home</a></li>
      <li><a href="#eras">Eras</a></li>
      <li><a href="#mapa">Mapa</a></li>
      <li><a href="#biografias">Biografias</a></li>
      <li><a href="#sobre">Sobre</a></li>
    </ul>
  </nav>
</header>

<!-- ====================================================================
   CONTAINER PRINCIPAL – timeline + seções scrollables
   ==================================================================== -->
<div class="page-container">
  <!-- -------------------------------------------------------------------
     TIMELINE VERTICAL (Sticky)
     ------------------------------------------------------------------- -->
  <aside class="timeline">
    <div class="timeline__line"></div>

    {#each eras as era, idx}
      <button
        class="timeline__marker"
        data-label="{era.title}"
        style="top: calc((100% / {eras.length}) * {idx} + 1rem);" 
        aria-label="Ir para {era.title}"
        on:click={() => {
          // ao clicar, rola até a seção dessa era
          document.getElementById(era.id)?.scrollIntoView({ behavior: 'smooth' });
        }}
      ></button>
    {/each}
  </aside>

  <!-- -------------------------------------------------------------------
     AREA DE SEÇÕES – cada seção corresponde a uma era de 100vh
     ------------------------------------------------------------------- -->
  <main class="sections-wrapper">
    {#each eras as era, idx}
      <section class="era-section" id="{era.id}">
        <div class="era-content">
          <!-- Sidebar de Matemáticos -->
          <aside class="era-sidebar">
            <h3>Matemáticos</h3>
            <ul>
              {#each era.mathematicians as m}
                <li
                  tabindex="0"
                  aria-label="{m.name} ({m.years})"
                  on:click={() => {
                    // aqui você poderia abrir um modal, preencher dados no painel de detalhes etc.
                    alert(`Matemático selecionado: ${m.name} (${m.years})`);
                  }}
                >
                  {m.name} <span class="mat-years">({m.years})</span>
                </li>
              {/each}
            </ul>
          </aside>

          <!-- Conteúdo principal da era -->
          <div class="era-main">
            <h2 class="era-main__title">{era.title}</h2>
            <p class="era-main__subtitle">{era.subtitle}</p>
            <p class="era-main__description">{era.description}</p>
            <button class="btn-view" on:click={scrollToVisualization}>
              Ver Visualização
            </button>
          </div>
        </div>
      </section>
    {/each}

    <!-- -------------------------------------------------------------------
       SEÇÃO FINAL: Data Graph – a área de visualização de dados
       ------------------------------------------------------------------- -->
    <section class="data-graph" id="data-graph">
      <div class="data-graph__inner">
        <h2>Data Graph</h2>
        <p>Insira aqui o seu componente de grafo/mapa interativo ou dashboard.</p>
        <!-- Por exemplo:
             <DataMapComponent {someProp} />
        -->
      </div>
    </section>
  </main>
</div>

<!-- ====================================================================
   ESTILIZAÇÃO COMPLETA
   ==================================================================== -->
<style>
  /* ==========================
     VARIÁVEIS & RESET BÁSICO
     ========================== */
  :root {
    --header-height: 60px;
    --timeline-width: 60px;
    --marker-size: 14px;
    --section-height: 100vh; /* cada seção ocupa 100% da viewport */
  }

  *,
  *::before,
  *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  html,
  body {
    height: 100%;
    font-family: 'Roboto', sans-serif;
    scroll-behavior: smooth; /* rolagem suave */
  }

  /* ==========================
     HEADER & NAVEGAÇÃO
     ========================== */
  .header {
    position: sticky;
    top: 0;
    width: 100%;
    height: var(--header-height);
    background-color: #1e293b;
    display: flex;
    align-items: center;
    z-index: 100;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .nav {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1rem;
  }

  .nav__logo {
    font-size: 1.25rem;
    color: #f1f5f9;
    font-weight: bold;
  }

  .nav__links {
    display: flex;
    gap: 1rem;
    list-style: none;
  }

  .nav__links li a {
    color: #f1f5f9;
    text-decoration: none;
    font-size: 0.95rem;
    padding: 0.5rem;
    border-radius: 4px;
    transition: background 0.2s, color 0.2s;
  }

  .nav__links li a:hover,
  .nav__links li a:focus {
    background-color: #374151;
    color: #ffffff;
    outline: none;
  }

  /* ==========================
     LAYOUT PRINCIPAL: PAGE CONTAINER
     ========================== */
  .page-container {
    display: flex;
    width: 100%;
    margin-top: var(--header-height); /* empurra conteúdo abaixo do header */
  }

  /* ==========================
     TIMELINE VERTICAL (Sticky)
     ========================== */
  .timeline {
    position: sticky;
    top: var(--header-height);
    width: var(--timeline-width);
    min-width: var(--timeline-width);
    background-color: transparent;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 1rem;
    height: calc(100vh - var(--header-height));
    z-index: 50;
  }

  .timeline__line {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    width: 4px;
    height: calc(100% - 2rem);
    background-color: #3b82f6;
    top: 1rem;
    border-radius: 2px;
  }

  .timeline__marker {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    width: var(--marker-size);
    height: var(--marker-size);
    background-color: #ffffff;
    border: 2px solid #2563eb;
    border-radius: 50%;
    cursor: pointer;
    transition: transform 0.2s, background-color 0.2s;
  }

  .timeline__marker:hover,
  .timeline__marker:focus {
    transform: translateX(-50%) scale(1.3);
    background-color: #2563eb;
    outline: none;
  }

  .timeline__marker[data-label]:hover::after {
    content: attr(data-label);
    position: absolute;
    left: 100%; /* exibe o label à direita do marcador */
    margin-left: 8px;
    white-space: nowrap;
    background: #ffffff;
    color: #1e293b;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    font-size: 0.8rem;
  }

  /* ==========================
     SEÇÕES DE ERA (SCROLL VERTICAL)
     ========================== */
  .sections-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  /* Cada <section> ocupa 100vh */
  .era-section {
    position: relative;
    min-height: var(--section-height);
    padding: 2rem 2rem 2rem calc(var(--timeline-width) + 2rem);
    display: flex;
    align-items: center;
  }

  /* Fundo alternado para distinguir cada seção */
  .era-section:nth-of-type(odd) {
    background-color: #f3f4f6;
  }
  .era-section:nth-of-type(even) {
    background-color: #e5e7eb;
  }

  .era-content {
    display: flex;
    gap: 2rem;
    width: 100%;
  }

  /* Sidebar dentro de cada era */
  .era-sidebar {
    width: 25%;
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .era-sidebar h3 {
    margin-bottom: 0.5rem;
    font-size: 1rem;
    color: #1e293b;
  }

  .era-sidebar ul {
    list-style: none;
    margin-top: 0.5rem;
  }

  .era-sidebar ul li {
    margin-bottom: 0.5rem;
    cursor: pointer;
  }

  .era-sidebar ul li:focus,
  .era-sidebar ul li:hover {
    outline: none;
    background-color: #c7d2fe;
  }

  .era-sidebar ul li button {
    width: 100%;
    background: none;
    border: none;
    color: #1e293b;
    font-size: 0.9rem;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    text-align: left;
  }

  /* Conteúdo principal da era */
  .era-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 1rem;
  }

  .era-main__title {
    font-size: 1.75rem;
    color: #1e293b;
    margin-bottom: 0.5rem;
  }

  .era-main__subtitle {
    font-size: 1rem;
    color: #374151;
    margin-bottom: 1rem;
  }

  .era-main__description {
    font-size: 1rem;
    color: #374151;
    line-height: 1.6;
    margin-bottom: 1.5rem;
  }

  .btn-view {
    align-self: start;
    padding: 0.5rem 1rem;
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-view:hover,
  .btn-view:focus {
    background-color: #1e40af;
    outline: none;
  }

  /* ==========================
     SEÇÃO FINAL: DATA GRAPH
     ========================== */
  .data-graph {
    background-color: #f3f4f6;
    min-height: calc(100vh - var(--header-height));
    padding: 2rem 2rem 4rem calc(var(--timeline-width) + 2rem);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .data-graph__inner {
    width: 100%;
    max-width: 1000px;
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    text-align: center;
  }

  .data-graph__inner h2 {
    font-size: 1.75rem;
    color: #1e293b;
    margin-bottom: 1rem;
  }

  .data-graph__inner p {
    font-size: 1rem;
    color: #374151;
    line-height: 1.6;
  }

  /* ==========================
     RESPONSIVIDADE (MEDIA QUERIES)
     ========================== */
  @media (max-width: 1024px) {
    .era-content {
      flex-direction: column;
    }
    .era-sidebar {
      width: 100%;
      margin-bottom: 1rem;
    }
    .era-section {
      padding: 2rem;
    }
    .timeline {
      display: none; /* oculta timeline em telas menores */
    }
  }

  @media (max-width: 640px) {
    .nav__links {
      display: none; /* você pode substituir por um menu “hambúrguer” */
    }
  }
</style>
