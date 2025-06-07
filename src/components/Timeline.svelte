<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  const eras = [
    { name: "BC – Before Crist",  range: [-1680, 0],    color: "#a855f7" },
    { name: "Before Calculos",    range: [0, 1800],     color: "#3b82f6" },
    { name: "ModernEra",          range: [1800, new Date().getFullYear()], color: "#facc15" }
  ];

  function selectEra(era) {
    dispatch("selectEra", era.range);
  }
</script>

<style>
  .timeline {
    position: relative;
    width: 100%;
    height: 100%;
  }

  /* linha vertical central */
  .timeline::before {
    content: "";
    position: absolute;
    top: 0; bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 2px;
    background: #ccc;
  }

  .circle {
    position: absolute;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: var(--color);
    border: 2px solid white;
    box-shadow: 0 0 0 2px var(--color);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .circle:hover {
    transform: translate(-50%, -50%) scale(1.3);
    box-shadow: 0 0 0 4px var(--color);
  }
</style>

<div class="timeline">
  {#each eras as era, idx}
    <!-- calcula o top em (idx + 0.5)/3 * 100% -->
    <div
      class="circle"
      title={era.name}
      style="
        --color: {era.color};
        top: {((idx + 0.5) / eras.length) * 100}%;
      "
      on:click={() => selectEra(era)}
    />
  {/each}
</div>
