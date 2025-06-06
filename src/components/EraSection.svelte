<script>
  // Recebe um objeto “era” via prop
  export let era;

  /**
   * Se você quiser rolar diretamente do botão “Ver Visualização” desta era,
   * basta descomentar a função e, por exemplo, rolar até um ID específico.
   *
   * function scrollToEraVisualization() {
   *   const target = document.getElementById(`${era.id}-visual`);
   *   if (target) {
   *     target.scrollIntoView({ behavior: 'smooth' });
   *   }
   * }
   */
</script>

<section class="era-section" id="{era.id}">
  <div class="era-content">
    <!-- Sidebar de Matemáticos -->
    <aside class="era-sidebar">
      <h3>Matemáticos ( {era.title} )</h3>
      <ul>
        {#each era.mathematicians as m}
          <li
            tabindex="0"
            aria-label="{m.name} ({m.years})"
            on:click={() => {
              // Aqui, você pode disparar um modal, preencher um store ou navegar
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
      <button class="btn-view" on:click={() => {
        // Rola até o data‐graph genérico
        document.getElementById('data-graph')?.scrollIntoView({ behavior: 'smooth' });
      }}>
        Ver Visualização
      </button>
    </div>
  </div>
</section>

<style>
  .era-section {
    position: relative;
    min-height: var(--section-height);
    padding: 2rem 2rem 2rem calc(var(--timeline-width) + 2rem);
    display: flex;
    align-items: center;
  }

  /* Fundo alternado para cada seção (impar/par) */
  /* Essa lógica de nim-of-type deve ser herdada na ordem em que for montado */
  /* Caso queira cores fixas, pode colocar diretamente em cada instância */
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

  /* Sidebar interna de cada era */
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

  .era-sidebar ul li .mat-years {
    font-size: 0.8rem;
    color: #6b7280;
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
  }
</style>
