<!-- src/components/VizContainer.svelte -->
<script>
  import { onMount, afterUpdate, createEventDispatcher, onDestroy } from 'svelte';
  import * as d3 from 'd3';
  
  export let id;
  export let points = [];
  export let currentEra = null;
  export let expanded = false; // Nova prop para controlar o estado expandido
  const dispatch = createEventDispatcher();

  let container;
  let tooltip;
  let isDragging = false;
  let startX, scrollLeft;
  const zoomFactor = 4; // Fator de ampliação horizontal

  onMount(draw);
  afterUpdate(draw);

  function parseYear(str) {
    if (!str) return null;
    const bc = str.match(/(\d+)\s*BC$/i);
    if (bc) return -+bc[1];
    const fy = str.match(/(\d{4})/);
    if (fy) return +fy[1];
    return null;
  }

  function createTooltip() {
    d3.selectAll('.viz-tooltip').remove();
    
    tooltip = d3.select('body').append('div')
      .attr('class', 'viz-tooltip')
      .style('position', 'absolute')
      .style('background', 'rgba(0, 0, 0, 0.9)')
      .style('color', 'white')
      .style('padding', '8px 12px')
      .style('border-radius', '6px')
      .style('font-family', 'system-ui, -apple-system, sans-serif')
      .style('font-size', '12px')
      .style('box-shadow', '0 4px 12px rgba(0, 0, 0, 0.3)')
      .style('border', '1px solid rgba(255, 255, 255, 0.1)')
      .style('pointer-events', 'none')
      .style('opacity', 0)
      .style('z-index', 10000);

    return tooltip;
  }

  function draw() {
    if (id !== 1 || !container) return;
    const sel = d3.select(container);
    sel.selectAll('*').remove();

    // Tamanhos visíveis
    const visibleW = container.clientWidth;
    const visibleH = expanded ? container.clientHeight * 0.9 : container.clientHeight;
    
    // Tamanho do conteúdo (ampliado horizontalmente)
    const contentW = visibleW * zoomFactor;
    const contentH = visibleH;
    
    const margin = { top: 20, right: 20, bottom: 60, left: 40 };
    const innerW = contentW - margin.left - margin.right;
    const innerH = contentH - margin.top - margin.bottom;

    // Cria SVG principal com dimensões ampliadas
    const svg = sel.append('svg')
      .attr('width', contentW)
      .attr('height', contentH);

    let [startYear, endYear] = currentEra
      ? [...currentEra]
      : d3.extent(points, d => d.birthYear);
    if (startYear > endYear) [startYear, endYear] = [endYear, startYear];
    const isAncient = endYear <= 0;

    function tScaleBC(rel) {
      const S15 = 1/15, S2 = 2/15, S4 = 4/15, S8 = 8/15;
      if (rel >= 800) return ((1600 - rel) / 800) * S15;
      if (rel >= 400) return S15 + ((800 - rel) / 400) * S2;
      if (rel >= 200) return S15 + S2 + ((400 - rel) / 200) * S4;
      return S15 + S2 + S4 + ((200 - rel) / 200) * S8;
    }

    const tScale = isAncient
      ? rel => tScaleBC(rel)
      : year => (year - startYear) / (endYear - startYear);

    const periods = isAncient ? 2 : 1;

    const curvePts = d3.range(0, 1.001, 1/400).map(u => {
      const x = margin.left + innerW * u;
      let y = margin.top + innerH * 0.5;
      if (isAncient) {
        const amp = innerH * 0.3;
        y -= amp * Math.sin(2 * Math.PI * periods * u);
      }
      return { u, x, y };
    });

    svg.append('path')
      .datum(curvePts)
      .attr('d', d3.line().x(d => d.x).y(d => d.y).curve(d3.curveNatural))
      .attr('fill', 'none')
      .attr('stroke', isAncient ? '#d946ef' : '#999')
      .attr('stroke-width', 2);

    const jitterAmt = innerH * 0.02;
    const jitter = d3.randomUniform(-jitterAmt, jitterAmt);

    const currentTooltip = createTooltip();

    svg.selectAll('circle')
      .data(points)
      .join('circle')
      .attr('cx', d => {
        const rel = isAncient ? 0 - d.birthYear : d.birthYear - startYear;
        return margin.left + innerW * tScale(rel);
      })
      .attr('cy', d => {
        let baseY = margin.top + innerH * 0.5;
        if (isAncient) {
          const rel = 0 - d.birthYear;
          const u = tScale(rel);
          const amp = innerH * 0.3;
          baseY -= amp * Math.sin(2 * Math.PI * periods * u);
        }
        return baseY + jitter();
      })
      .attr('r', 4)
      .attr('fill', isAncient ? '#a855f7' : '#3b82f6')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .ease(d3.easeBackOut)
          .attr('r', 7)
          .attr('stroke-width', 2);

        svg.selectAll('path.highlight').remove();
        
        if (d.data_morte && d.data_morte !== 'N/A') {
          const deathYear = parseYear(d.data_morte);
          if (deathYear) {
            const birthRel = isAncient ? 0 - d.birthYear : d.birthYear - startYear;
            const deathRel = isAncient ? 0 - deathYear : deathYear - startYear;
            let uBirth = Math.max(0, Math.min(1, tScale(birthRel)));
            let uDeath = Math.max(0, Math.min(1, tScale(deathRel)));
            
            const [u0, u1] = uBirth < uDeath ? [uBirth, uDeath] : [uDeath, uBirth];
            const segment = curvePts.filter(pt => pt.u >= u0 && pt.u <= u1);
            
            if (segment.length > 1) {
              const pathElement = svg.append('path')
                .datum(segment)
                .attr('class', 'highlight')
                .attr('d', d3.line().x(pt => pt.x).y(pt => pt.y).curve(d3.curveNatural))
                .attr('fill', 'none')
                .attr('stroke', '#ef4444')
                .attr('stroke-width', 3)
                .attr('opacity', 0);

              pathElement.transition().duration(300).attr('opacity', 0.8);

              const totalLength = pathElement.node().getTotalLength();
              pathElement
                .attr('stroke-dasharray', totalLength + ' ' + totalLength)
                .attr('stroke-dashoffset', totalLength)
                .transition()
                .duration(800)
                .ease(d3.easeLinear)
                .attr('stroke-dashoffset', 0);
            }
          }
        }

        const birthText = d.birthYear < 0 ? Math.abs(d.birthYear) + ' BC' : d.birthYear;
        const deathText = d.data_morte || 'N/A';
        const name = d.nome_curto || d.name || 'Unknown';
        
        const containerRect = container.getBoundingClientRect();
        const isExpanded = containerRect.width > window.innerWidth * 0.8;
        
        let tooltipX, tooltipY;
        if (isExpanded) {
          tooltipX = event.clientX + 12;
          tooltipY = event.clientY - 10;
        } else {
          tooltipX = event.pageX + 12;
          tooltipY = event.pageY - 10;
        }
        
        currentTooltip.html(`
          <div style="font-weight: bold; margin-bottom: 4px; font-size: 13px;">${name}</div>
          <div style="font-size: 11px;">Born: ${birthText}</div>
          <div style="font-size: 11px;">Died: ${deathText}</div>
        `)
          .style('left', tooltipX + 'px')
          .style('top', tooltipY + 'px')
          .transition()
          .duration(200)
          .style('opacity', 1);
      })
      .on('mousemove', function(event) {
        const containerRect = container.getBoundingClientRect();
        const isExpanded = containerRect.width > window.innerWidth * 0.8;
        
        let tooltipX, tooltipY;
        if (isExpanded) {
          tooltipX = event.clientX + 12;
          tooltipY = event.clientY - 10;
        } else {
          tooltipX = event.pageX + 12;
          tooltipY = event.pageY - 10;
        }
        
        currentTooltip
          .style('left', tooltipX + 'px')
          .style('top', tooltipY + 'px');
      })
      .on('mouseout', function() {
        d3.select(this)
          .transition()
          .duration(200)
          .ease(d3.easeBackIn)
          .attr('r', 4)
          .attr('stroke-width', 1.5);

        svg.selectAll('path.highlight')
          .transition()
          .duration(200)
          .attr('opacity', 0)
          .remove();

        currentTooltip
          .transition()
          .duration(200)
          .style('opacity', 0);
      });

    if (isAncient) {
      const ticks = [200, 400, 800, 1600];
      const yAxis = margin.top + innerH + 15;
      ticks.forEach(r => {
        const x = margin.left + innerW * tScale(r);
        svg.append('line')
          .attr('x1', x).attr('x2', x)
          .attr('y1', yAxis).attr('y2', yAxis + 6)
          .attr('stroke', '#333');
        svg.append('text')
          .attr('x', x).attr('y', yAxis + 20)
          .text(`${r} BC`)
          .attr('text-anchor', 'middle')
          .style('font-size', '10px');
      });
    } else {
      const xScale = d3.scaleLinear()
        .domain([startYear, endYear])
        .range([margin.left, margin.left + innerW]);
      svg.append('g')
        .attr('transform', `translate(0, ${margin.top + innerH + 15})`)
        .call(d3.axisBottom(xScale).ticks(6).tickFormat(y => y < 0 ? `${-y} BC` : y))
        .selectAll('text').style('font-size', '10px');
    }

    return () => {
      if (currentTooltip) {
        currentTooltip.remove();
      }
    };
  }

  function handleWheel(e) {
    if (expanded) {
      // Só permite scroll horizontal quando expandido
      e.preventDefault();
      container.scrollLeft += e.deltaY * 0.5;
    }
    // Quando não expandido, permite o comportamento padrão de scroll vertical
  }

  function toggleExpand() {
    dispatch('expand');
  }

  onDestroy(() => {
    d3.selectAll('.viz-tooltip').remove();
  });
</script>

<div 
  class="viz-container" 
  bind:this={container}
  class:expanded
  on:wheel={handleWheel}
  on:click={toggleExpand}
  on:keydown={e => e.key === 'Enter' || e.key === ' ' ? toggleExpand() : null}
  tabindex="0"
  role="button"
  aria-label={expanded ? 'Contrair visualização' : 'Expandir visualização'}
>
</div>

<style>
  .viz-container {
    width: 100%;
    height: 50vh; /* Exatamente metade da tela */
    overflow-x: auto; /* Scroll horizontal */
    overflow-y: hidden; /* Esconde scroll vertical */
    cursor: pointer;
    position: relative;
    transition: height 0.3s ease;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    margin-bottom: 1rem;
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .viz-container.expanded {
    height: 90vh; /* Quase toda a tela quando expandido */
    cursor: grab;
  }

  .viz-container:active {
    cursor: grabbing;
  }

  /* Garante que o SVG não ultrapasse o container */
  .viz-container svg {
    display: block;
    max-height: 100%;
    width: auto;
  }

  /* Remove qualquer margem ou padding extra */
  .viz-container > * {
    margin: 0;
    padding: 0;
  }
</style>