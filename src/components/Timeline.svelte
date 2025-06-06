<script>
  export let eras = [];

  /**
   * Ao clicar num marcador, rolamos até a seção desta era.
   */
  function goToEra(eraId) {
    const target = document.getElementById(eraId);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  }
</script>

<aside class="timeline">
  <div class="timeline__line"></div>
  {#each eras as era, idx}
    <button
      class="timeline__marker"
      data-label="{era.title}"
      style="top: calc((100% / {eras.length}) * {idx} + 1rem);"
      aria-label="Ir para {era.title}"
      on:click={() => goToEra(era.id)}
      tabindex="0"
    ></button>
  {/each}
</aside>

<style>
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
    left: 100%;
    margin-left: 8px;
    white-space: nowrap;
    background: #ffffff;
    color: #1e293b;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    font-size: 0.8rem;
  }

  @media (max-width: 1024px) {
    .timeline {
      display: none; /* opcionalmente ocultar em telas menores */
    }
  }
</style>
