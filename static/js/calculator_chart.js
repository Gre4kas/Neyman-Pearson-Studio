// Глобальная функция инициализации графика Neyman-Pearson
window.initNPChart = function initNPChart(){
  const jsonNode = document.getElementById('plot-data');
  const canvasEl = document.getElementById('distributionsChart');
  if(!jsonNode || !canvasEl || !window.Chart){ return; }
  const rawPlotData = JSON.parse(jsonNode.textContent);
  const thresholdAttr = canvasEl.getAttribute('data-threshold');
  const threshold = thresholdAttr ? parseFloat(thresholdAttr) : null;
  const ctx = canvasEl.getContext('2d');

  if(window.neymanPearsonChart && typeof window.neymanPearsonChart.destroy === 'function'){
    try { window.neymanPearsonChart.destroy(); } catch(e){ console.warn(e); }
  }

  const drawThresholdPlugin = {
    id: 'drawThresholdPlugin',
    afterDraw(chart){
      if(threshold === null) return;
      const xScale = chart.scales.x; const yScale = chart.scales.y;
      if(!xScale||!yScale) return;
      if(threshold < xScale.min || threshold > xScale.max) return;
      const xPixel = xScale.getPixelForValue(threshold);
      const c = chart.ctx; c.save();
      c.strokeStyle='rgb(54,162,235)'; c.lineWidth=2; c.setLineDash([5,4]);
      c.beginPath(); c.moveTo(xPixel,yScale.top); c.lineTo(xPixel,yScale.bottom); c.stroke();
      c.fillStyle='rgb(54,162,235)'; c.font='13px sans-serif'; c.textAlign='left'; c.textBaseline='top';
      c.fillText('C = '+threshold.toFixed(4), xPixel+6, yScale.top+6); c.restore();
    }
  };

  window.neymanPearsonChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: rawPlotData.x,
      datasets: [
        {label:'H₀ PDF', data: rawPlotData.h0_pdf, borderColor:'rgb(75,192,192)', tension:0.08, pointRadius:0},
        {label:'H₁ PDF', data: rawPlotData.h1_pdf, borderColor:'rgb(255,99,132)', tension:0.08, pointRadius:0}
      ]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      interaction:{mode:'nearest', intersect:false},
      plugins:{ title:{display:true, text:'Плотности f₀ и f₁'}, legend:{position:'bottom'}, tooltip:{enabled:true}},
      scales:{
        x:{type:'linear', title:{display:true, text:'x'}},
        y:{title:{display:true, text:'Плотность'}, beginAtZero:true, suggestedMax: rawPlotData.max_pdf*1.15}
      }
    },
    plugins:[drawThresholdPlugin]
  });
};

// Автоматическая повторная инициализация после htmx swap
if(window.htmx){
  document.addEventListener('htmx:afterSwap', function(evt){
     if(evt.target && evt.target.id === 'results-container'){
       requestAnimationFrame(()=>{ if(typeof window.initNPChart === 'function'){ window.initNPChart(); } });
     }
  });
}
