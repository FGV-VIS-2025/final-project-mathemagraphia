<script>
  // Se quiser deixar dinâmico:
  const cards = [
    { img: "exemplo1.jpg", title: "MostRelevants" },
  ];
</script>

<style>
  :global(body) {
    margin: 0;
    font-family: sans-serif;
  }

  .page {
    display: flex;
  }

  .navbar {
    width: 200px;
    background-color: #f0f0f0;
    padding: 1rem;
    height: 100vh;
    position: fixed;
    right: 0;
    top: 0;
  }

  .content {
    margin-right: 200px;
    padding: 2rem;
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
  }

  .card img {
    width: 80px;
    height: 80px;
    object-fit: cover;
    margin-bottom: 0.5rem;
  }

  .navbar ul {
    padding: 0;
    list-style: none;
  }

  .navbar li {
    margin-bottom: 1rem;
  }

  .navbar a {
    text-decoration: none;
    color: #333;
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
