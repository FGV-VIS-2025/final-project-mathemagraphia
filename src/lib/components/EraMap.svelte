<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import * as topojson from 'topojson-client';

  const MAP_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';
  const DATA_URL = 'data/mac_tutor_com_coords.json';

  let mapSvg;
  let graphContainer;
  let projection, path;
  let allPoints = [];
  let landFeatures = { type: 'FeatureCollection', features: [] };
  let citationsByDepth = {};
  let citationGraph = {};
  let citedMathematicians = [];
  let selectedPoint = null;

  let searchTerm = '';
  let suggestions = [];
  let showSuggestions = false;

  let citationDepth = 1;
  let maxDepth = 3;

  function extrairAno(dataStr) {
    const bc = dataStr?.match(/(\d+)\s*BC/i);
    if (bc) return -parseInt(bc[1]);
    const y = dataStr?.match(/(\d{3,4})/);
    return y ? +y[1] : null;
  }

  function slugify(name) {
    return name.toLowerCase()
      .normalize('NFD').replace(/\p{Diacritic}/gu, '')
      .replace(/\s+/g, '-').replace(/[^\w-]/g, '');
  }

  async function choosePoint(d) {
    selectedPoint = d;
    citedMathematicians = [];
    citationsByDepth = {};
    citationGraph = {};

    try {
      const res = await fetch(`MacTutorData/${slugify(d.nome_curto)}.json`);
      if (res.ok) {
        const detail = await res.json();
        selectedPoint = { ...selectedPoint, ...detail };
        if (detail.matematicos_citados_na_biografia) {
          citationsByDepth[1] = await getCitationsFromNames(detail.matematicos_citados_na_biografia);
          citationGraph[slugify(selectedPoint.nome_curto)] = citationsByDepth[1].map(m => slugify(m.nome_curto));
          await buildCitationTree();
          updateCitedMathematicians();
        }
      }
    } catch (e) {
      console.error(e);
    }
    drawMap();
    drawGraph();
  }

  async function getCitationsFromNames(citedNames) {
    if (!Array.isArray(citedNames)) return [];
    const norm = citedNames.map(n => n.toLowerCase());
    return allPoints.filter(p =>
      norm.some(n =>
        p.nome_curto.toLowerCase().includes(n) || p.nome_completo.toLowerCase().includes(n)
      )
    );
  }

  async function buildCitationTree() {
    for (let depth = 1; depth < maxDepth; depth++) {
      const nextDepth = depth + 1;
      const currentLevel = citationsByDepth[depth] || [];
      if (!currentLevel.length) break;
      let nextLevel = [];
      for (let m of currentLevel) {
        const slug = slugify(m.nome_curto);
        try {
          const res = await fetch(`MacTutorData/${slug}.json`);
          if (res.ok) {
            const detail = await res.json();
            if (detail.matematicos_citados_na_biografia) {
              const children = await getCitationsFromNames(detail.matematicos_citados_na_biografia);
              citationGraph[slug] = (citationGraph[slug]||[]).concat(children.map(c=>slugify(c.nome_curto)));
              nextLevel.push(...children);
            }
          }
        } catch {}
      }
      const prev = new Set([slugify(selectedPoint.nome_curto)]);
      for (let d=1; d<=depth; d++) citationsByDepth[d]?.forEach(m=>prev.add(slugify(m.nome_curto)));
      citationsByDepth[nextDepth] = nextLevel.filter(m=>!prev.has(slugify(m.nome_curto))).map(m=>m);
      if (!citationsByDepth[nextDepth].length) break;
    }
  }

  function updateCitedMathematicians() {
    citedMathematicians = [];
    for (let d=1; d<=citationDepth; d++) {
      if (citationsByDepth[d]) citedMathematicians.push(...citationsByDepth[d]);
    }
    citedMathematicians = Array.from(new Set(citedMathematicians));
  }

  function buildGraphData() {
    const nodesMap = new Map();
    const links = [];
    const rootSlug = slugify(selectedPoint.nome_curto);
    nodesMap.set(rootSlug, selectedPoint);
    for (let depth=1; depth<=citationDepth; depth++) {
      const parents = depth===1
        ? [slugify(selectedPoint.nome_curto)]
        : (citationsByDepth[depth-1]||[]).map(m=>slugify(m.nome_curto));
      for (let pSlug of parents) {
        const children = (citationGraph[pSlug]||[]);
        const valid = children.filter(cSlug =>
          (citationsByDepth[depth]||[]).some(m=>slugify(m.nome_curto)===cSlug)
        );
        for (let cSlug of valid) {
          const parent = allPoints.find(p=>slugify(p.nome_curto)===pSlug);
          const child = allPoints.find(p=>slugify(p.nome_curto)===cSlug);
          if (parent) nodesMap.set(pSlug,parent);
          if (child) nodesMap.set(cSlug,child);
          links.push({ source:pSlug, target:cSlug });
        }
      }
    }
    const nodes = Array.from(nodesMap.values()).map(d=>({id:slugify(d.nome_curto),data:d}));
    return {nodes,links};
  }

  function drawGraph() {
    d3.select(graphContainer).selectAll('*').remove();
    if (!selectedPoint) return;
    const {nodes,links} = buildGraphData();
    const width=700,height=700;
    const svg=d3.select(graphContainer).append('svg').attr('width',width).attr('height',height);
    svg.append('defs').append('marker').attr('id','arrow').attr('viewBox','-5 -5 10 10')
      .attr('refX',15).attr('refY',0).attr('markerWidth',6).attr('markerHeight',6)
      .attr('orient','auto').append('path').attr('d','M-5,-5L5,0L-5,5');
    const linkG=svg.append('g').attr('stroke','#999').attr('stroke-opacity',0.6)
      .selectAll('line').data(links).join('line').attr('marker-end','url(#arrow)');
    const nodeG=svg.append('g').selectAll('g').data(nodes).join('g')
      .call(d3.drag().on('start',dragstarted).on('drag',dragged).on('end',dragended));
    nodeG.append('circle').attr('r',d=>d.id===slugify(selectedPoint.nome_curto)?10:6)
      .attr('fill',d=>d.id===slugify(selectedPoint.nome_curto)?'#0ea5e9':'#38bdf8')
      .attr('stroke','#0c4a6e').on('click',(_,d)=>choosePoint(d.data));
    nodeG.append('text').text(d=>d.data.nome_curto).attr('x',12).attr('y',3)
      .style('font-size','10px').style('pointer-events','none');
    const sim=d3.forceSimulation(nodes)
      .force('link',d3.forceLink(links).id(d=>d.id).distance(100))
      .force('charge',d3.forceManyBody().strength(-200))
      .force('center',d3.forceCenter(width/2,height/2)).on('tick',ticked);
    function ticked(){linkG.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y)
      .attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
      nodeG.attr('transform',d=>`translate(${d.x},${d.y})`);
    }
    function dragstarted(e,d){if(!e.active) sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;}
    function dragged(e,d){d.fx=e.x;d.fy=e.y;}
    function dragended(e,d){if(!e.active) sim.alphaTarget(0);d.fx=null;d.fy=null;}
  }

  function drawMap() {
    const svg=d3.select(mapSvg);svg.selectAll('*').remove();svg.attr('viewBox',[0,0,800,450]);
    svg.append('defs').append('marker').attr('id','arrowhead').attr('viewBox','-0 -5 10 10')
      .attr('refX',10).attr('refY',0).attr('orient','auto')
      .append('path').attr('d','M0,-5L10,0L0,5').attr('fill','#0ea5e9');
    svg.append('path').datum(landFeatures).attr('fill','#e0f2fe').attr('stroke','#94a3b8').attr('d',path);
    for(let depth=1;depth<=citationDepth;depth++){const pts=citationsByDepth[depth]||[];const col=['#0ea5e9','#38bdf8','#7dd3fc'][depth-1]||'#0284c7';
      pts.forEach(d=>svg.append('path').datum({source:projection(selectedPoint.coords),target:projection(d.coords)})
        .attr('fill','none').attr('stroke',col).attr('stroke-width',1.5).attr('marker-end','url(#arrowhead)')
        .attr('d',l=>`M${l.source[0]},${l.source[1]}L${l.target[0]},${l.target[1]}`));}
    svg.append('g').selectAll('circle').data(allPoints).join('circle')
      .attr('r',d=>d===selectedPoint?7:4).attr('fill',d=>d===selectedPoint?'#0ea5e9':'#0284c7')
      .attr('stroke','#0c4a6e').attr('cx',d=>projection(d.coords)[0]).attr('cy',d=>projection(d.coords)[1])
      .style('cursor','pointer').on('click',(_,d)=>choosePoint(d));
  }

  onMount(async()=>{const world=await d3.json(MAP_URL);const countries=topojson.feature(world,world.objects.countries);
    landFeatures=countries;const raw=await d3.json(DATA_URL);allPoints=raw.map(d=>{const y=extrairAno(d.data_nascimento);const lat=parseFloat(d.lat_nasc);const lon=parseFloat(d.lon_nasc);
      if(y==null||isNaN(lat)||isNaN(lon)||y>=0) return null;return {...d,coords:[lon,lat],birthYear:y};}).filter(Boolean);
    const lons=allPoints.map(d=>d.coords[0]);const lats=allPoints.map(d=>d.coords[1]);const lonC=(Math.min(...lons)+Math.max(...lons))/2;const latC=(Math.min(...lats)+Math.max(...lats))/2;
    projection=d3.geoMercator().scale(300).center([lonC,latC]).translate([800/2,450/2]);path=d3.geoPath(projection);drawMap();});
</script>
<style>
  .map-section{padding:2rem;background:#f9fafb;}.map-and-search{display:flex;gap:1rem;}.map-wrapper{flex:4;background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.12);}
  .search-box{flex:1;min-width:250px;display:flex;flex-direction:column;}.search-box input{padding:12px;border:2px solid #e2e8f0;border-radius:8px;font-size:14px;margin-bottom:0.5rem;}
  .suggestions-list li{cursor:pointer;padding:0.4rem;border-bottom:1px solid #eee;} .depth-control{margin:1rem 0;padding:1rem;background:white;border-radius:8px;border:1px solid #e2e8f0;}
  .depth-slider{width:100%;}.depth-info{display:flex;justify-content:space-between;font-size:0.8rem;color:#64748b;margin-top:0.5rem;} .legend{display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:1rem;}
  .legend-item{display:flex;align-items:center;gap:0.25rem;font-size:0.8rem;} .legend-circle{width:12px;height:12px;border-radius:50%;border:1px solid #0c4a6e;} .info-container{background:white;border:1px solid #ccc;border-radius:8px;padding:1rem;font-size:0.9rem;}
  .graph-section{margin-top:2rem;padding:1rem;background:#f0f9ff;border-top:1px solid #cbd5e1;}
</style>

<section class="map-section"><div class="map-and-search"><div class="map-wrapper"><svg bind:this={mapSvg} width="800" height="450"></svg></div><div class="search-box">
  <input type="text" placeholder="Buscar matemático…" bind:value={searchTerm}
         on:input={()=>{suggestions=allPoints.filter(p=>p.nome_curto.toLowerCase().includes(searchTerm.toLowerCase())||p.nome_completo.toLowerCase().includes(searchTerm.toLowerCase())).slice(0,8);showSuggestions=true}}
         on:blur={()=>setTimeout(()=>showSuggestions=false,100)} />{#if showSuggestions&&suggestions.length}<ul class="suggestions-list">{#each suggestions as s}<li on:click={()=>choosePoint(s)}>{s.nome_curto}</li>{/each}</ul>{/if}
  <div class="depth-control"><label><strong>Profundidade de Citações:</strong></label>
    <input type="range" min="1" max={maxDepth} bind:value={citationDepth} on:input={()=>{updateCitedMathematicians();drawMap();drawGraph();}} class="depth-slider" />
    <div class="depth-info"><span>Nível {citationDepth}</span><span>{citedMathematicians.length} matemáticos</span></div>
    <div class="legend"><div class="legend-item"><div class="legend-circle" style="background-color:#0ea5e9"></div><span>Selecionado / Nível 1</span></div><div class="legend-item"><div class="legend-circle" style="background-color:#38bdf8"></div><span>Nível 2</span></div><div class="legend-item"><div class="legend-circle" style="background-color:#7dd3fc"></div><span>Nível 3</span></div></div>
  </div>
  <div class="info-container">{#if selectedPoint}<h3>{selectedPoint.nome_completo}</h3><p><strong>Nascimento:</strong> {selectedPoint.data_nascimento} — {selectedPoint.local_nascimento}</p>{#if selectedPoint.data_morte}<p><strong>Morte:</strong> {selectedPoint.data_morte} — {selectedPoint.local_morte}</p>{/if}<p><strong>Resumo:</strong> {selectedPoint.summary}</p><p><a href={selectedPoint.link} target="_blank">Mais sobre {selectedPoint.nome_curto}</a></p>{:else}<p>Clique em um ponto no mapa para ver detalhes.</p>{/if}</div>
</div></div></section><section class="graph-section" bind:this={graphContainer}></section>
