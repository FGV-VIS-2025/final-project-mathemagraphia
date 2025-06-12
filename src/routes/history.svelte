<script>
  import IntroGlobe from '../lib/components/IntroGlobe.svelte';
  import EraMap from '../lib/components/EraMap.svelte';
  import EuclidElements from '../lib/components/EuclidElements.svelte';
</script>

<main>
  <section id="intro">
    <IntroGlobe />
  </section>

  <section id="map">
    <EraMap />
  </section>

  <section id="euclid">
    <EuclidElements />
  </section>
</main>
