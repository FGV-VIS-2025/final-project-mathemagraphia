<script>
  const eras = [
    { name: "BC - Before Crist", color: "#cbd5e1" },
    { name: "Before Calculos",  color: "#94a3b8" },
    { name: "ModernEra",        color: "#475569" }
  ];
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
    flex: 1; /* divide igualmente */
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 0.4rem;
    box-sizing: border-box;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  }

  .era-block:last-child {
    border-bottom: none;
  }
</style>

<div class="timeline">
  {#each eras as era}
    <div class="era-block" style="background:{era.color}">
      <div>{era.name}</div>
    </div>
  {/each}
</div>
