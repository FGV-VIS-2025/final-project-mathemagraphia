<script>
  import Navbar from './Navbar.svelte';
  import Home from './pages/Home.svelte';
  import People from './pages/People.svelte';
  import History from './pages/History.svelte';
  import Charts from './pages/Charts.svelte';

  let currentPage = 'home';

  function goTo(page) {
    currentPage = page;
  }
</script>

<Navbar on:navigate={(e) => goTo(e.detail)} />

<div class="content">
  {#if currentPage === 'home'}
    <Home />
  {:else if currentPage === 'people'}
    <People />
  {:else if currentPage === 'history'}
    <History />
  {:else if currentPage === 'charts'}
    <Charts />
  {/if}
</div>

<style>
  .content {
    margin-top: 60px; /* igual à altura da navbar */
    padding: 2rem;
  }
</style>
