<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  const eras = [
    { name: "BC - Before Crist", range: [-1680, 0],     color: "#cbd5e1" },
    { name: "Before Calculos",  range: [0, 1800],       color: "#94a3b8" },
    { name: "ModernEra",        range: [1800, 2100],    color: "#475569" }
  ];

  function selectEra(era) {
    dispatch('selectEra', era.range);
  }
</script>

<style>
  .timeline {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    color: #fff;
    font-size: 0.65rem;
    font-weight: bold;
    overflow: hidden;
    border-right: 1px solid rgba(255, 255, 255, 0.15);
  }

  .era-block {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 0.4rem;
    cursor: pointer;
    box-sizing: border-box;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    transition: background 0.2s ease;
  }

  .era-block:hover {
    filter: brightness(1.15);
  }

  .era-block:last-child {
    border-bottom: none;
  }
</style>

<div class="timeline">
  {#each eras as era}
    <div
      class="era-block"
      style="background:{era.color}"
      on:click={() => selectEra(era)}
    >
      {era.name}
    </div>
  {/each}
</div>
