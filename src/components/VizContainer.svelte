<script>
  export let id;
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();
</script>

<div class="viz" on:click={() => dispatch('expand')}>
  <p>Visualização #{id}</p>
</div>

<style>
  .viz {
    width: 200px;
    height: 150px;
    background: #ccc;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }
</style>
