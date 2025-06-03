<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  function navigateTo(page) {
    dispatch('navigate', page);
  }
</script>

<nav class="navbar">
  <!-- Lado esquerdo: Logo + GitHub -->
  <div class="left-section">
    <button class="logo" on:click={() => navigateTo('home')}>Logo</button>
    <a class="github" href="https://github.com/FGV-VIS-2025/final-project-mathemagraphia" target="_blank">GitHub</a>
  </div>

  <!-- Lado direito: Navegação -->
  <div class="nav-links">
    <button on:click={() => navigateTo('people')}>Pessoas</button>
    <button on:click={() => navigateTo('history')}>Histórias</button>
    <button on:click={() => navigateTo('charts')}>DataGraphs</button>
  </div>
</nav>

<style>
  .navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background-color: #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    z-index: 1000;
  }

  .left-section {
    display: flex;
    align-items: center;
    gap: 2rem; /* espaço entre logo e GitHub */
  }

  .nav-links {
    display: flex;
    gap: 1rem;
  }

  button, a {
    background: none;
    border: none;
    font-size: 1rem;
    cursor: pointer;
    text-decoration: none;
    color: #333;
  }

  button:hover, a:hover {
    color: #0070f3;
  }

  .logo {
    font-weight: bold;
    font-size: 1.1rem;
  }

  .github {
    font-style: italic;
    color: #555;
  }
</style>
