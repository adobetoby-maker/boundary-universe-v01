const escapeHtml = value => value
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

const renderInline = value => escapeHtml(value)
  .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  .replace(/\*([^*]+)\*/g, '<em>$1</em>');

const renderProse = markdown => markdown
  .trim()
  .split(/\n\s*\n/)
  .map(paragraph => `<p>${renderInline(paragraph.replace(/\s*\n\s*/g, ' '))}</p>`)
  .join('');

const chapterId = new URLSearchParams(window.location.search).get('id');

fetch('data.json')
  .then(response => {
    if (!response.ok) throw new Error('The library catalog could not be loaded.');
    return response.json();
  })
  .then(data => {
    const preview = (data.previews || []).find(item =>
      (item.chapters || []).some(chapter => chapter.id === chapterId));
    const chapter = preview && preview.chapters.find(item => item.id === chapterId);
    if (!preview || !chapter) throw new Error('That reading preview was not found.');

    document.title = `${chapter.title} — ${preview.title}`;
    document.getElementById('reader-series').textContent = preview.series;
    document.getElementById('reader-book').textContent = preview.title;
    document.getElementById('reader-chapter').textContent = `Chapter ${chapter.n} — ${chapter.title}`;
    document.getElementById('reader-meta').innerHTML =
      `<span>${chapter.words.toLocaleString()} words</span><span>${escapeHtml(preview.status)}</span>`;
    return fetch(chapter.path);
  })
  .then(response => {
    if (!response.ok) throw new Error('The chapter file could not be loaded.');
    return response.text();
  })
  .then(markdown => {
    document.getElementById('reader-copy').innerHTML = renderProse(markdown);
  })
  .catch(error => {
    document.getElementById('reader-copy').innerHTML =
      `<p class="reader-error">${escapeHtml(error.message)}</p>`;
  });
