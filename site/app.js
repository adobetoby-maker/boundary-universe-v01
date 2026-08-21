fetch('data.json').then(r=>r.json()).then(d=>{
  document.getElementById('metrics').innerHTML = `
    <div class="metric"><b>${d.book1.words.toLocaleString()}</b><span>BOOK ONE WORDS</span></div>
    <div class="metric"><b>${d.book1.chapters}</b><span>CHAPTERS</span></div>
    <div class="metric"><b>${d.book1.audio_hours}</b><span>EST. AUDIO HOURS</span></div>`;
  document.getElementById('trilogy').innerHTML=d.trilogy.map((x,i)=>`
    <article class="card"><div class="num">0${i+1}</div><h3>${x.title}</h3><p>${x.role}</p><div class="status">${x.status}</div></article>`).join('');
  document.getElementById('chapters').innerHTML=d.chapters.map(c=>`
    <article class="chapter"><div class="n">${String(c.n).padStart(2,'0')}</div><h4>${c.title}</h4><small>${c.words.toLocaleString()} words</small><p>${c.summary}</p></article>`).join('');
});
