<script>
  import { onMount } from 'svelte';
  import IntroGlobe from './lib/components/IntroGlobe.svelte';
  import EraMap from './lib/components/EraMap.svelte';
  import EuclidElements from './lib/components/EuclidElements.svelte';
  import Curves from './pages/Curves.svelte';
  import CoinSimulation from './lib/components/CoinSimulation.svelte';
  import WeierstrassPlot from './lib/components/Weierstrass.svelte';
  import DynamicSystem from './lib/components/DynamicSystem.svelte';

  import ScrollableTimer from './components/Scrollable_timer.svelte';
  import LateralSineWaves from './components/Lateral_waves.svelte';

  let mainElement;

  onMount(() => {
    const euclidSection = document.getElementById('euclid-section');
    const curvesSection = document.getElementById('curves-section');
    if (!euclidSection || !curvesSection) return;

    const options = { root: null, threshold: 0.10 };

    const euclidObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          mainElement.classList.add('show-columns');
          document.body.classList.add('euclid-bg-active');
        } else {
          mainElement.classList.remove('show-columns');
          document.body.classList.remove('euclid-bg-active');
        }
      });
    }, options);

    const curvesObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          document.body.classList.add('curves-bg-active');
        } else {
          document.body.classList.remove('curves-bg-active');
        }
      });
    }, options);

    const probObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          document.body.classList.add('prob-bg-active');
        } else {
          document.body.classList.remove('prob-bg-active');
        }
      });
    }, { root: null, threshold: 0.1 });

    const weierstrassObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          document.body.classList.add('weierstrass-bg-active');
        } else {
          document.body.classList.remove('weierstrass-bg-active');
        }
      });
    }, { threshold: 0.1 });

    euclidObserver.observe(euclidSection);
    curvesObserver.observe(curvesSection);
    probObserver.observe(document.getElementById('probability-section'));
    weierstrassObserver.observe(document.getElementById('weierstrass-section'));

    return () => {
      euclidObserver.disconnect();
      curvesObserver.disconnect();
      probObserver.disconnect();
      weierstrassObserver.disconnect();
    };
  });
</script>

<main bind:this={mainElement}>
  <IntroGlobe />
  <EraMap />

  <div class="interstitial-section">
    <h2>Era Antiga (c. 300 a.C.)</h2>
    <p>
      A geometria floresce com Euclides de Alexandria. Seus "Elementos" estabelecem os
      fundamentos da geometria que seriam a base do pensamento matemático por mais de
      dois milênios.
    </p>
  </div>

  <div id="euclid-section">
    <EuclidElements />
    <ScrollableTimer startYear={-300} endYear={1637} scrollDuration={150} />
  </div>
  

  <div class="interstitial-section">
    <h2>A Revolução das Curvas (Séc. XVII - XIX)</h2>
    <p>
      Matemáticos como Descartes, Newton e Leibniz introduzem o cálculo e a geometria
      analítica, transformando curvas em equações dinâmicas.
    </p>
  </div>

  <div id="curves-section">
    <Curves />
    <ScrollableTimer startYear={1637} endYear={1812} scrollDuration={150} />
  </div>


  <div class="interstitial-section" id="probability-section">
    <h2>A Era da Probabilidade</h2>
    <p>
      Curiosidade sobre dados e moedas levou ao nascimento dos métodos que hoje fundamentam
      estatística, seguros e análise de risco.
    </p>
  </div>

  <div id="probability-simulation">
    <CoinSimulation />
    <ScrollableTimer startYear={1812} endYear={1872} scrollDuration={100} />
  </div>

  <div class="interstitial-section" id="weierstrass-section">
    <h2>Desenvolvimento da Análise Real e Geometria Fractal</h2>
    <p>
      Weierstrass foi um grande matemático do séc. XIX que fez diversas contribuições a Análise Real.
      A função que leva o seu nome é contínua em todos os pontos, mas não diferenciável em nenhum,
      antecipando conceitos de Geometria Fractal.
    </p>
  </div>

  <div id="weierstrass-plot">
    <WeierstrassPlot width={800} height={300} />
    <ScrollableTimer startYear={1872} endYear={1963} scrollDuration={200} />
  </div>

  <!-- Nova seção: Sistemas Dinâmicos -->
  <div class="interstitial-section" id="dynamic-intro">
    <h2>Sistemas Dinâmicos</h2>
    <p>
      Sistemas Dinâmicos estudam como estados evoluem no tempo segundo regras matemáticas.
      Modelos como o Atrator de Lorenz revelam comportamentos complexos e sensíveis às condições iniciais.
    </p>
  </div>

  <div id="dynamic-visualization">
    <DynamicSystem />
  </div>
</main>

<style>
  main { display: flex; flex-direction: column; scroll-behavior: smooth; position: relative; z-index: 1;}
  main::before, main::after { content: ''; position: fixed; top: 0; bottom: 0; width: 120px; z-index: 0; background-repeat: repeat-y; background-size: 100% auto; opacity: 0; transition: transform 0.7s ease-out, opacity 0.5s ease-out; }
  main::before { left: 0; background-image: url('/src/assets/coluna-1.png'); transform: translateX(-100%); }
  main::after { right: 0; background-image: url('/src/assets/coluna-4.png'); transform: translateX(100%); }
  :global(main.show-columns)::before, :global(main.show-columns)::after { opacity: 1; transform: translateX(0); }
  :global(body) { background-color: #FFFFFF; transition: background-color 0.8s ease-in-out; }
  :global(body.euclid-bg-active) { background-color: #FAF0E6; }
  :global(body.curves-bg-active) { background-color: #E6F0FA; }
  .interstitial-section { padding: 20vh 10vw; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; width: 100%; box-sizing: border-box; }
  .interstitial-section h2 { font-size: clamp(2rem, 5vw, 3.5rem); font-family: 'Times New Roman', serif; color: #333; margin-bottom: 1rem; }
  .interstitial-section p { font-size: clamp(1rem, 2.5vw, 1.2rem); color: #555; line-height: 1.6; max-width: 65ch; }
</style>
