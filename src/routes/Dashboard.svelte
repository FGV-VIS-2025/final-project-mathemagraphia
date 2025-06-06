<script>
  import FixedBar from '../components/FixedBar.svelte';
  import VizContainer from '../components/VizContainer.svelte';

  let expanded = null;

  function expand(id) {
    expanded = id;
  }

  function closeModal() {
    expanded = null;
  }
</script>

<!-- MAPA -->
<div class="map-section">
  <!-- Substituir com visualização real -->
  <div class="map-placeholder">[Mapa Interativo Aqui]</div>
</div>

<!-- VISUALIZAÇÕES -->
<div class="viz-grid">
  {#each [1, 2, 3, 4] as id}
    <VizContainer {id} on:expand={() => expand(id)} />
  {/each}
</div>

<FixedBar />

<!-- MODAL EXPANDIDO -->
{#if expanded}
  <div class="modal-overlay" on:click={closeModal}>
    <div class="modal-window" on:click|stopPropagation>
      <button on:click={closeModal}>X</button>
      <p>Visualização expandida #{expanded}</p>
    </div>
  </div>
{/if}

<style>
  .map-section {
    height: 40vh;
    background: #eef;
  }

  .viz-grid {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    flex-wrap: wrap;
  }

  .modal-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .modal-window {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    width: 80vw;
    height: 80vh;
    overflow: auto;
  }
</style>
