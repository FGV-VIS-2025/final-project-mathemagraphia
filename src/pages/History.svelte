<script>
  // Se quiser deixar dinâmico:
  const cards = [
    { img: "exemplo1.jpg", title: "Guerra do Cálculo" },
    { img: "exemplo2.jpg", title: "Último Teorema de Fermat" },
    { img: "", title: "Outro conteúdo" }
  ];
</script>


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
    width: 200px;
    height: 200px;
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
    width: 80px;
    height: 80px;
    object-fit: cover;
    margin-bottom: 0.5rem;
  }
</style>


<div class="page">
  <div class="content">
    {#each cards as { img, title }}
      <div class="card">
        {#if img}
          <img src={img} alt={title} />
        {/if}
        <p>{title}</p>
      </div>
    {/each}
  </div>


</div>
