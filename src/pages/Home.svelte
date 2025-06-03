<script>
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';

  const sections = [
    {
      id: 1,
      title: "A Matemática Está em Tudo",
      content: "De simulações climáticas à segurança digital, a matemática está presente em todos os aspectos da nossa vida.",
      buttonText: "Descer" // botão transparente com seta para baixo indicando scroll
    },
    {
      id: 2,
      title: "Uma Linha do Tempo no Milenar",
      content: "Explore a história da matemática visualmente com o DataMap: veja onde e quando nasceram os grandes matemáticos.",
      page: "datamap",
      buttonText: "Explorar Mapa"
    },
    {
      id: 3,
      title: "Conexões Entre Gênios",
      content: "Com o DataGraph, descubra como os matemáticos se influenciaram ao longo dos séculos. Escolha um nome e veja suas conexões.",
      page: "datagraph",
      buttonText: "Ver Conexões"
    },
    {
      id: 4,
      title: "Histórias Matemáticas",
      content: "Mergulhe em temas fascinantes com visualizações sobre cálculo, infinitos, paradoxos e mais.",
      page: "stories",
      buttonText: "Explorar Temas"
    },
    {
      id: 5,
      title: "Biografias que Inspiram",
      content: "Conheça os matemáticos por trás das ideias: suas vidas, desafios e descobertas.",
      page: "people",
      buttonText: "Ver Biografias"
    },
    {
      id: 6,
      title: "Curvas Interativas",
      content: "Experimente curvas clássicas e entenda visualmente como funcionam equações famosas.",
      page: "charts",
      buttonText: "Explorar Curvas"
    },
    {
      id: 7,
      title: "A Jornada Está Só Começando",
      content: "A matemática é uma história viva. Explore, descubra e veja como ela continua moldando o mundo ao nosso redor.",
      buttonText: "Começar a Explorar"
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
  :global(body) {
    margin: 0;
    font-family: Arial, sans-serif;
    background-color: #f0f0f0;
    color: #333;
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