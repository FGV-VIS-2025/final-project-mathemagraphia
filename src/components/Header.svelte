<script>
  // Não há props. Este componente simplesmente renderiza o header sticky.
</script>

<header class="header">
  <nav class="nav">
    <div class="nav__logo">MathemaGraphia</div>
    <ul class="nav__links">
      <li><a href="/">Home</a></li>
      <li><a href="#eras">Eras</a></li>
      <li><a href="#mapa">Mapa</a></li>
      <li><a href="#biografias">Biografias</a></li>
      <li><a href="#sobre">Sobre</a></li>
    </ul>
  </nav>
</header>

<style>
  .header {
    position: sticky;
    top: 0;
    width: 100%;
    height: var(--header-height);
    background-color: #1e293b;
    display: flex;
    align-items: center;
    z-index: 100;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .nav {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1rem;
  }

  .nav__logo {
    font-size: 1.25rem;
    color: #f1f5f9;
    font-weight: bold;
  }

  .nav__links {
    display: flex;
    gap: 1rem;
    list-style: none;
  }

  .nav__links li a {
    color: #f1f5f9;
    text-decoration: none;
    font-size: 0.95rem;
    padding: 0.5rem;
    border-radius: 4px;
    transition: background 0.2s, color 0.2s;
  }

  .nav__links li a:hover,
  .nav__links li a:focus {
    background-color: #374151;
    color: #ffffff;
    outline: none;
  }

  @media (max-width: 640px) {
    .nav__links {
      display: none; /* você pode implementar um menu hambúrguer aqui */
    }
  }
</style>
