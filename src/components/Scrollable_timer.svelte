<script>
  import { onMount } from 'svelte';

  export let startYear;
  export let endYear;
  export let scrollDuration = 200;
  export let pauseAtEnd = 0;

  let currentYear = startYear;
  let trackElement; // A única coisa que ainda precisamos é a referência ao elemento
  let y = 0; // A posição do scroll da janela

  onMount(() => {});

  $: {
    //Apenas executamos se o elemento já existe na página
    if (trackElement) {
      //PEGAMOS A POSIÇÃO E ALTURA ATUALIZADAS EM TEMPO REAL, A CADA SCROLL
      const currentTrackTop = trackElement.getBoundingClientRect().top + y;
      const currentTrackHeight = trackElement.offsetHeight;

      if (currentTrackHeight > 0) {
        const viewportCenter = y + window.innerHeight / 2;
        const scrollIntoTrack = viewportCenter - currentTrackTop;
        const animationHeight = currentTrackHeight * (1 - pauseAtEnd);

        let progress = 0;
        if (animationHeight > 0) {
          progress = scrollIntoTrack / animationHeight;
        }
        const clampedProgress = Math.max(0, Math.min(1, progress));

        currentYear = startYear + clampedProgress * (endYear - startYear);
      }
    }
  }
</script>

<svelte:window bind:scrollY={y} />

<div
  class="timer-track"
  style="height: {scrollDuration}vh;"
  bind:this={trackElement}
>
  <div class="timer-display-sticky-wrapper">
    <div class="timer-value">
      {Math.round(currentYear)}
    </div>
    <div class="timeline-bar-container">
      <div
        class="timeline-bar-progress"
        style="width: {Math.max(0, Math.min(100, ((currentYear - startYear) / (endYear - startYear)) * 100))}%"
      ></div>
    </div>
  </div>
</div>

<style>
  .timer-track {
    position: relative;
    width: 100%;
    z-index: 2;
    margin: 40vh 0;
  }

  .timer-display-sticky-wrapper {
    position: sticky;
    top: 50vh;
    transform: translateY(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 150px;
  }

  .timer-value {
    font-family: 'Courier New', Courier, monospace;
    font-size: clamp(3rem, 12vw, 6rem);
    font-weight: 800;
    color: #2c2c2c;
    text-shadow: 0px 3px 10px rgba(0, 0, 0, 0.4);
  }

  .timeline-bar-container {
    width: 80%;
    max-width: 450px;
    height: 10px;
    background-color: #d1d1d1;
    border-radius: 5px;
    margin-top: 2rem;
    overflow: hidden;
    box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.2);
  }

  .timeline-bar-progress {
    height: 100%;
    background-color: #2c2c2c;
    border-radius: 5px;
  }
</style>