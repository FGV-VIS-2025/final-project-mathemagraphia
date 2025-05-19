<script>
  import Navbar from './Navbar.svelte';
  import Home from './pages/Home.svelte';
  import People from './pages/People.svelte';
  import History from './pages/History.svelte';
  import Charts from './pages/Charts.svelte';
  import DataMap from './pages/DataGraphsVis/DataMap.svelte';
  import GrafMaths from './pages/DataGraphsVis/GrafMaths.svelte';
  let currentPage = 'home';

function goTo(page) {
  console.log("Navegando para:", page);
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
    <Charts on:navigate={(e) => goTo(e.detail)} />
  {:else if currentPage === 'datamap'}
    <DataMap />
  {:else if currentPage === 'grafmaths'}
    <GrafMaths />
  {/if}
</div>

<style>
  .content {
    margin-top: 60px; /* igual à altura da navbar */
    padding: 2rem;
  }
</style>
