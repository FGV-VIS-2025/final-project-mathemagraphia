<script>
  import { onMount } from 'svelte';
  import Home from './routes/Home.svelte';
  import Dashboard from './routes/Dashboard.svelte';

  let currentPage = 'home';

  // Atualiza a página com base no hash
  function updatePageFromHash() {
    const hash = window.location.hash.slice(1); // remove #
    currentPage = hash || 'home';
  }

  // Atualiza quando o hash mudar (ex: #dashboard)
  window.addEventListener('hashchange', updatePageFromHash);
  onMount(updatePageFromHash);

  function goTo(page) {
    window.location.hash = page; // altera URL e aciona hashchange
  }
</script>

{#if currentPage === 'home'}
  <Home on:navigate={(e) => goTo(e.detail)} />
{:else if currentPage === 'dashboard'}
  <Dashboard />
{:else}
  <h2>Página não encontrada</h2>
{/if}
