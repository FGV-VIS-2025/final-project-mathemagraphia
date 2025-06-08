<!-- src/components/VizContainer.svelte -->
<script>
  import { onMount, afterUpdate, createEventDispatcher } from 'svelte';
  import * as d3 from 'd3';
  export let id;
  export let points = [];
  export let currentEra = null;
  const dispatch = createEventDispatcher();

  let container;
  let tooltip;

  onMount(draw);
  afterUpdate(draw);

  // função para extrair ano de string, incluindo BC
  function parseYear(str) {
    if (!str) return null;
    const bc = str.match(/(\d+)\s*BC$/i);
    if (bc) return -+bc[1];
    const fy = str.match(/(\d{4})/);
    if (fy) return +fy[1];
    return null;
  }

  function createTooltip() {
    // Remove tooltip existente
    d3.selectAll('.viz-tooltip').remove();
    
    // Cria novo tooltip
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
      .style('z-index', 10000); // Z-index alto para aparecer sobre elementos ampliados

    return tooltip;
  }

  function draw() {
    if (id !== 1 || !container) return;
    const sel = d3.select(container);
    sel.selectAll('*').remove();

    const W = container.clientWidth;
    const H = container.clientHeight;
    const margin = { top: 20, right: 20, bottom: 60, left: 40 };
    const innerW = W - margin.left - margin.right;
    const innerH = H - margin.top - margin.bottom;

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

    const svg = sel.append('svg').attr('width', W).attr('height', H);
    svg.append('path')
      .datum(curvePts)
      .attr('d', d3.line().x(d => d.x).y(d => d.y).curve(d3.curveNatural))
      .attr('fill', 'none')
      .attr('stroke', isAncient ? '#d946ef' : '#999')
      .attr('stroke-width', 2);

    const jitterAmt = innerH * 0.02;
    const jitter = d3.randomUniform(-jitterAmt, jitterAmt);

    // Cria tooltip para esta instância
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
        // Animação de aumento do ponto
        d3.select(this)
          .transition()
          .duration(200)
          .ease(d3.easeBackOut)
          .attr('r', 7)
          .attr('stroke-width', 2);

        // Remove highlight existente
        svg.selectAll('path.highlight').remove();
        
        // Calcula caminho da vida se temos data de morte
        if (d.data_morte && d.data_morte !== 'N/A') {
          const deathYear = parseYear(d.data_morte);
          if (deathYear) {
            const birthRel = isAncient ? 0 - d.birthYear : d.birthYear - startYear;
            const deathRel = isAncient ? 0 - deathYear : deathYear - startYear;
            let uBirth = Math.max(0, Math.min(1, tScale(birthRel)));
            let uDeath = Math.max(0, Math.min(1, tScale(deathRel)));
            
            // Garante ordem correta
            const [u0, u1] = uBirth < uDeath ? [uBirth, uDeath] : [uDeath, uBirth];
            const segment = curvePts.filter(pt => pt.u >= u0 && pt.u <= u1);
            
            // Desenha caminho da vida
            if (segment.length > 1) {
              const pathElement = svg.append('path')
                .datum(segment)
                .attr('class', 'highlight')
                .attr('d', d3.line().x(pt => pt.x).y(pt => pt.y).curve(d3.curveNatural))
                .attr('fill', 'none')
                .attr('stroke', '#ef4444')
                .attr('stroke-width', 3)
                .attr('opacity', 0);

              // Animação de aparição
              pathElement.transition().duration(300).attr('opacity', 0.8);

              // Efeito de desenhar o caminho
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

        // Tooltip melhorado
        const birthText = d.birthYear < 0 ? Math.abs(d.birthYear) + ' BC' : d.birthYear;
        const deathText = d.data_morte || 'N/A';
        const name = d.nome_curto || d.name || 'Unknown';
        
        // Calcula posição relativa ao container se estiver ampliado
        const containerRect = container.getBoundingClientRect();
        const isExpanded = containerRect.width > window.innerWidth * 0.8; // Detecta se está ampliado
        
        let tooltipX, tooltipY;
        if (isExpanded) {
          // Se ampliado, usa posição relativa ao viewport
          tooltipX = event.clientX + 12;
          tooltipY = event.clientY - 10;
        } else {
          // Se não ampliado, usa pageX/pageY normal
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
        // Animação de diminuir o ponto
        d3.select(this)
          .transition()
          .duration(200)
          .ease(d3.easeBackIn)
          .attr('r', 4)
          .attr('stroke-width', 1.5);

        // Remove highlight com animação
        svg.selectAll('path.highlight')
          .transition()
          .duration(200)
          .attr('opacity', 0)
          .remove();

        // Esconde tooltip
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

    // Cleanup function
    return () => {
      if (currentTooltip) {
        currentTooltip.remove();
      }
    };
  }

  // Cleanup quando o componente for destruído
  import { onDestroy } from 'svelte';
  onDestroy(() => {
    d3.selectAll('.viz-tooltip').remove();
  });
</script>

<div class="viz" bind:this={container} on:click={() => dispatch('expand')} />

<style>
  .viz { 
    width: 100%; 
    height: 100%; 
    overflow: auto; 
    cursor: pointer; 
  }
</style>