<script>
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';

  const sections = [
    {
      id: 1,
      title: "A Matemática Está em Tudo",
      content: "De simulações climáticas à segurança digital, a matemática permeia nosso mundo.",
      page: "curves",
      buttonText: "Ver Curvas"
    },
    {
      id: 2,
      title: "Uma Linha do Tempo Milenar",
      content: "Dos babilônios aos algoritmos modernos, cada época teve seus gênios e descobertas.",
      page: "history",
      buttonText: "Explorar História"
    },
    {
      id: 3,
      title: "A Guerra do Cálculo",
      content: "Newton e Leibniz protagonizaram uma das disputas mais influentes da ciência.",
      page: "people",
      buttonText: "Conhecer Matemáticos"
    },
    {
      id: 4,
      title: "Biografias que Inspiram",
      content: "Conheça matemáticos que desafiaram os limites do conhecimento humano.",
      page: "people",
      buttonText: "Ver Biografias"
    },
    {
      id: 5,
      title: "Explore Mais",
      content: "Continue navegando pelas seções para ver visualizações interativas e dados históricos.",
      page: "charts",
      buttonText: "Ver Gráficos"
    }
  ];

  let visibleSection = 1;
  let sectionElements = [];

  onMount(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY + window.innerHeight / 2;
      
      sectionElements.forEach((section, index) => {
        if (section) {
          const sectionTop = section.offsetTop;
          const sectionHeight = section.offsetHeight;
          
          if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            visibleSection = index + 1;
          }
        }
      });
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Atualiza a seção visível inicial

    return () => window.removeEventListener('scroll', handleScroll);
  });
</script>

<style>
  body {
    margin: 0;
    font-family: sans-serif;
    overflow-x: hidden;
  }

  .section {
    height: 75vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 2rem;
    box-sizing: border-box;
  }

  h1 {
    font-size: clamp(2rem, 5vw, 3rem);
    margin-bottom: 1rem;
  }

  p {
    font-size: clamp(1.2rem, 3vw, 1.5rem);
    max-width: min(90%, 600px);
    margin: 0 auto;
  }
</style>

<div>
  {#each sections as section (section.id)}
    <div class="section" bind:this={sectionElements[section.id - 1]}>
      {#if visibleSection === section.id}
        <h1 in:fly={{ y: 100, duration: 600 }}>
          {section.title}
        </h1>
        <p in:fly={{ y: 100, duration: 600, delay: 200 }}>
          {section.content}
        </p>
      {/if}
    </div>
  {/each}
</div>