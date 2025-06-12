<script>
  import IntroGlobe from './lib/components/IntroGlobe.svelte';
  import EraMap from './lib/components/EraMap.svelte';
  import EuclidElements from './lib/components/EuclidElements.svelte';
</script>

<main>
  <IntroGlobe />
  <EraMap />
  <EuclidElements />
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    scroll-behavior: smooth;
  }
</style>
