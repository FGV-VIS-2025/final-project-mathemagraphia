<script>
  export let id;
  export let showEuclidesPlot = false;

  import { createEventDispatcher } from 'svelte';
  import EuclidesChart from '../routes/Euclides.svelte';

  const dispatch = createEventDispatcher();
</script>

<div class="viz" on:click={() => dispatch('expand')}>
  {#if showEuclidesPlot}
    <EuclidesChart />
  {:else}
    <p>Visualização #{id}</p>
  {/if}
</div>

<style>
  .viz {
    width: 100%;
    height: 100%;
    background: #f0f0f0;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: 8px;
    padding: 1rem;
    box-sizing: border-box;
  }

  .viz p {
    color: #666;
    font-style: italic;
  }
</style>
