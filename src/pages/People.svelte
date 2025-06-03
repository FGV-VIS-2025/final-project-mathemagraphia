<script>
  const desenvolvedores = [
    {
      nome: "Henrique Borges",
      github: "https://github.com/HenriqueBorges6",
      foto: "icons/Henrique_Borges1.jpg"
    }
  ];
</script>

<style>
  .team-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 2rem;
    padding: 2rem;
  }

    .profile-card img {
    width: 140px;
    height: 140px;
    object-fit: contain;
    border-radius: 50%;
    background: #f0f0f0; /* fundo claro para áreas vazias */
    margin-bottom: 1rem;
    }

  .profile-card:hover {
    transform: scale(1.03);
  }

  .profile-card img {
    width: 100px;
    height: 100px;
    object-fit: cover;
    border-radius: 50%;
    margin-bottom: 1rem;
  }

  .nome {
    font-size: 1.2rem;
    font-weight: bold;
  }

  .funcao {
    font-size: 0.95rem;
    color: #555;
    margin-bottom: 0.5rem;
  }

  .bio {
    font-size: 0.85rem;
    color: #444;
    margin-bottom: 0.8rem;
  }

  .github-link {
    color: #24292e;
    font-weight: bold;
    text-decoration: none;
  }

  .github-link:hover {
    text-decoration: underline;
  }
</style>

<div class="team-container">
  {#each desenvolvedores as dev}
    <div class="profile-card">
      <img src={dev.foto} alt={"Foto de " + dev.nome} />
      <div class="nome">{dev.nome}</div>
      <div class="funcao">{dev.funcao}</div>
      <div class="bio">{dev.bio}</div>
      <a class="github-link" href={dev.github} target="_blank" rel="noopener noreferrer">
        GitHub
      </a>
    </div>
  {/each}
</div>
