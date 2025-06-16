<script lang="ts">
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  // --- Parâmetros da Senoide ---
  const waveWidth = 120; // Largura do container da onda
  const amplitude = 40;  // Quão "larga" a onda é
  const frequency = 0.02;  // Quão "comprimida" a onda é
  const points = 500;    // Pontos para desenhar a curva (suavidade)

  let pathData: string = '';
  let fullHeight = 0;

  // onMount garante que o código só rode no navegador, onde 'window' existe
  onMount(() => {
    fullHeight = window.innerHeight;

    // Gera os dados para o atributo 'd' do SVG <path>
    const lineGenerator = d3.line()
      .x(d => d[0])
      .y(d => d[1])
      .curve(d3.curveBasis); // Usamos uma curva suave (basis)

    // Gera os pontos [x, y] da nossa onda
    const wavePoints = d3.range(points).map(i => {
      const y = (i / (points - 1)) * fullHeight; // Posição vertical de 0 até a altura da tela
      // O 'x' oscila baseado no seno da posição 'y'
      const x = (waveWidth / 2) + Math.sin(y * frequency) * amplitude;
      return [x, y];
    });

    pathData = lineGenerator(wavePoints);
  });
</script>

<div class="sine-wave-left">
  {#if pathData}
    <svg width={waveWidth} height={fullHeight} preserveAspectRatio="none">
      <path d={pathData} />
    </svg>
  {/if}
</div>

<div class="sine-wave-right">
  {#if pathData}
    <svg width={waveWidth} height={fullHeight} preserveAspectRatio="none">
      <path d={pathData} />
    </svg>
  {/if}
</div>

<style>
  .sine-wave-left, .sine-wave-right {
    position: fixed;
    top: 0;
    bottom: 0;
    z-index: 0; /* Fica atrás do conteúdo, como as colunas */
    opacity: 0;
    transition: transform 0.7s ease-out, opacity 0.5s ease-out;
    pointer-events: none; /* Impede que capture cliques */
  }

  .sine-wave-left {
    left: 0;
    transform: translateX(-100%);
  }

  .sine-wave-right {
    right: 0;
    transform: translateX(100%) scaleX(-1); /* Inverte a onda horizontalmente */
  }

  /*
    Esta é a regra mágica: quando 'main' tiver a classe 'show-sine-waves',
    as ondas se tornam visíveis.
  */
  :global(main.show-sine-waves) .sine-wave-left,
  :global(main.show-sine-waves) .sine-wave-right {
    opacity: 1;
    transform: translateX(0) scaleX(1);
    /* Para a onda da direita, o scaleX(1) anula o scaleX(-1) inicial */
  }
  
  :global(main.show-sine-waves) .sine-wave-right {
     transform: translateX(0) scaleX(-1);
  }

  path {
    fill: none;
    stroke: #0077b6; /* Uma cor azulada */
    stroke-width: 3px;
    stroke-opacity: 0.6;
  }
</style>