<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  const cards = [
    { img: "icons/EuclidesGPT.png", title: "Euclides", page: "euclides" }
  ];

  function goTo(page) {
    dispatch("navigate", page);
  }
</script>

<div class="page">
  <div class="content">
    {#each cards as { img, title, page }}
      <div
        class="card"
        role="button"
        tabindex="0"
        on:click={() => goTo(page)}
        on:keydown={(e) => e.key === 'Enter' && goTo(page)}
      >
        {#if img}
          <img src={img} alt={title} />
        {/if}
        <p>{title}</p>
      </div>
    {/each}
  </div>
</div>


<style>
  :global(body) {
    margin: 0;
    font-family: sans-serif;
  }

  .page {
    display: flex;
    justify-content: center;
    padding: 2rem;
  }

  .content {
    display: flex;
    flex-wrap: wrap;
    gap: 2rem;
  }

  .card {
    width: 180px;
    height: 180px;
    background-color: #e4e4e4;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    border-radius: 8px;
    box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, background-color 0.2s ease;
    cursor: pointer;
    outline: none;
  }

  .card:hover,
  .card:focus {
    transform: scale(1.05);
    background-color: #dcdcdc;
  }

.card img {
  width: 100%;
  height: auto;
  max-height: 140px;
  object-fit: contain;
  padding: 0.5rem;
}

</style>
