<script>
  // Aqui você pode importar stores, dados ou subcomponentes de D3/Svelte
  // Exemplo: import DataMap from './DataMap.svelte';
</script>

<section class="data-graph" id="data-graph">
  <div class="data-graph__inner">
    <h2>Data Graph</h2>
    <p>Insira aqui o seu componente de grafo/mapa interativo ou dashboard.</p>
    <!-- Por exemplo: <DataMap {algumProp} /> -->
  </div>
</section>

<style>
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

  @media (max-width: 1024px) {
    .data-graph {
      padding: 2rem;
    }
  }
</style>
