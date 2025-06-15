<script>
  import { onMount } from 'svelte';
  import IntroGlobe from './lib/components/IntroGlobe.svelte';
  import EraMap from './lib/components/EraMap.svelte';
  import EuclidElements from './lib/components/EuclidElements.svelte';
  import Curves from './pages/Curves.svelte';
  import CoinSimulation from './lib/components/CoinSimulation.svelte';


  // Variável para referenciar o elemento <main>
  let mainElement;

  // onMount garante que o código só rode depois que o componente for montado no DOM
  onMount(() => {
    const euclidSection = document.getElementById('euclid-section');
    const curvesSection = document.getElementById('curves-section');
    
    if (!euclidSection || !curvesSection) return;

    const options = {
      root: null,
      threshold: 0.10
    };

    // Observador para a seção Euclid
    const euclidObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Ações quando a seção entra na tela
          mainElement.classList.add('show-columns');
          
          // Altera o fundo da página
          document.body.classList.add('euclid-bg-active');

        } else {
          // Ações quando a seção sai da tela
          mainElement.classList.remove('show-columns');
          
          // Remove a classe do fundo
          document.body.classList.remove('euclid-bg-active');
        }
      });
    }, options);

    // Observador para a seção de curvas
    const curvesObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Adiciona a classe de fundo azul
          document.body.classList.add('curves-bg-active');
        } else {
          // Remove a classe de fundo azul
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

  probObserver.observe(document.getElementById('probability-section'));


    euclidObserver.observe(euclidSection);
    curvesObserver.observe(curvesSection);
    
    return () => {
      euclidObserver.disconnect();
      curvesObserver.disconnect();
      probObserver.disconnect();

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
      dois milênios. É a era dos postulados, das provas rigorosas e da beleza da lógica pura.
    </p>
  </div>
  
  <div id="euclid-section">
    <EuclidElements />
  </div>

  <div class="interstitial-section">
    <h2>A Revolução das Curvas (Séc. XVII - XIX)</h2>
    <p>
      O Renascimento e a Revolução Científica abrem novos horizontes. Matemáticos como
      Descartes, Newton e Leibniz introduzem o cálculo e a geometria analítica,
      transformando curvas de meros objetos de contemplação em equações dinâmicas que
      descrevem o movimento dos planetas e a trajetória dos corpos.
    </p>
  </div>

  <div id="curves-section">
    <Curves />
  </div>
<!-- Seção intersticial para contextualizar a Era da Probabilidade -->
<div class="interstitial-section" id="probability-section">
  <h2>A Era da Probabilidade</h2>
  <p>
    Tudo começou nos salões de jogos de azar da Europa renascentista, onde a
    curiosidade sobre “dados e moedas” abriu caminho para cálculos rigorosos
    de chance. Esse interesse discreto se espalhou pelos séculos XVII e XVIII,
    alimentando o nascimento de métodos matemáticos que hoje fundamentam
    estatística, seguros e análise de risco.
  </p>
</div>

<div id="probability-simulation">
  <CoinSimulation />
</div>




</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    scroll-behavior: smooth;
    position: relative;
    z-index: 1;
    overflow-x: hidden;
  }

  main::before,
  main::after {
    content: '';
    position: fixed;
    top: 0;
    bottom: 0;
    width: 120px;
    z-index: 0;

    /* Altura exata da tela */
    background-repeat: repeat-y;
    background-size: 100% auto;

    /* Animação de slide + fade */
    opacity: 0;
    transition: transform 0.7s ease-out, opacity 0.5s ease-out;
  }

  main::before {
    left: 0;
    background-image: url('/src/assets/coluna-1.png');
    /* Posição inicial fora da tela (esquerda) */
    transform: translateX(-100%);
  }

  main::after {
    right: 0;
    background-image: url('/src/assets/coluna-4.png');
    /* Posição inicial fora da tela (direita) */
    transform: translateX(100%);
  }
  
  /* Estado final da animação, quando a classe é aplicada */
  :global(main.show-columns)::before,
  :global(main.show-columns)::after {
    opacity: 1;
    /* MUDANÇA 1: Traz as colunas para a posição final */
    transform: translateX(0);
  }

  /* --- Estilos para o fundo da página --- */

  :global(body) {
    background-color: #FFFFFF;
    transition: background-color 0.8s ease-in-out;
  }

  :global(body.euclid-bg-active) {
    /* Cor de papel antigo suave */
    background-color: #FAF0E6; /* Cor "Linen" */
  }

  :global(body.curves-bg-active) {
  background-color: #E6F0FA; /* Cor "AliceBlue" */
}

.interstitial-section {
  /* Cria o espaçamento vertical e horizontal entre as visualizações */
  padding: 20vh 10vw;

  /* Centraliza o conteúdo */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  
  /* Garante que ocupe a largura toda para centralizar corretamente */
  width: 100%;
  box-sizing: border-box;
}

.interstitial-section h2 {
  /* Fonte responsiva para o título */
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-family: 'Times New Roman', serif; /* Sugestão de fonte clássica */
  color: #333;
  margin-bottom: 1rem;
}

.interstitial-section p {
  /* Fonte responsiva para o parágrafo */
  font-size: clamp(1rem, 2.5vw, 1.2rem);
  color: #555;
  line-height: 1.6;

  /* Melhora a legibilidade limitando a largura da linha */
  max-width: 65ch;
}
</style>
