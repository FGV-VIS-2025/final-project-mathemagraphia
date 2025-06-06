<script>
  // --------------------------------------------------
  // Definição do array de eras.
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
        { name: 'Arquimedes', years: '287 a.C. – 212 d.C.' },
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
        'Marco de métodos analíticos. Destacam-se Descartes, Newton e Leibniz.',
      mathematicians: [
        { name: 'Descartes', years: '1596 – 1650' },
        { name: 'Newton', years: '1643 – 1727' },
        { name: 'Leibniz', years: '1646 – 1716' }
      ]
    }
  ];

  import Header from './components/Header.svelte';
  import Timeline from './components/Timeline.svelte';
  import EraSection from './components/EraSection.svelte';
  import DataGraph from './components/DataGraph.svelte';
</script>

<!-- Header fixo -->
<Header />

<!-- Timeline fixa sobrepondo à esquerda -->
<Timeline {eras} />

<!-- Conteúdo principal: cada seção ocupa toda a largura (100vw) -->
<main class="sections-wrapper">
  {#each eras as era}
    <EraSection {era} />
  {/each}

  <DataGraph />
</main>

<style>
  /* ==========================
     RESET BÁSICO E HTML/BODY A 100% SEM PADDING
     ========================== */
  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  html, body, #app {
    width: 100%;
    height: 100%;
    font-family: 'Roboto', sans-serif;
    scroll-behavior: smooth;
    overflow-x: hidden; /* evita rolagem horizontal */
  }

  /* ==========================
     VARIÁVEIS GLOBAIS
     ========================== */
  :root {
    --header-height: 60px;
    --timeline-width: 60px;
    --marker-size: 14px;
    --section-height: 100vh;
  }

  /* ==========================
     .sections-wrapper: cada seção ocupa 100vh e 100vw
     ========================== */
  .sections-wrapper {
    margin-top: var(--header-height); /* abaixo do Header */
  }

  @media (max-width: 1024px) {
    .sections-wrapper {
      margin-top: var(--header-height);
    }
  }
</style>
