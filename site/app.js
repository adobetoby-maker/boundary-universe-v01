fetch('data.json').then(r=>r.json()).then(d=>{
  const u = d.universe || {};
  document.getElementById('metrics').innerHTML = `
    <div class="metric"><b>${(u.total_words||0).toLocaleString()}</b><span>UNIVERSE WORDS</span></div>
    <div class="metric"><b>${u.books_complete||0}</b><span>BOOKS COMPLETE</span></div>
    <div class="metric"><b>${u.books_in_progress||0}</b><span>IN PROGRESS</span></div>
    <div class="metric"><b>${u.books_planned||0}</b><span>PLANNED</span></div>`;
  const sc = s => s==='Complete with Audio'?'status-done':s==='Written'?'status-written':s==='In Progress'?'status-wip':'status-planned';
  document.getElementById('books').innerHTML=(d.books||[]).map(b=>`
    <article class="card">
      <div class="num">${b.series.split('—')[0].trim()}</div>
      <h3>${b.title}</h3><p class="eyebrow">${b.series}</p>
      <p>${b.description}</p>
      <div class="book-stats">
        ${b.words?`<span>${b.words.toLocaleString()} words</span>`:`<span>${b.chapters_written}/${b.chapters_total} chapters</span>`}
        ${b.audio_hours?`<span>${b.audio_hours}h audio</span>`:''}
      </div>
      <div class="status ${sc(b.status)}">${b.status}</div>
    </article>`).join('');
  document.getElementById('trilogy').innerHTML=(d.trilogy||[]).map((x,i)=>`
    <article class="card"><div class="num">0${i+1}</div><h3>${x.title}</h3><p>${x.role}</p><div class="status">${x.status}</div></article>`).join('');
  document.getElementById('chapters').innerHTML=(d.chapters||[]).map(c=>`
    <article class="chapter"><div class="n">${String(c.n).padStart(2,'0')}</div><h4>${c.title}</h4><small>${c.words.toLocaleString()} words</small><p>${c.summary}</p></article>`).join('');
});
