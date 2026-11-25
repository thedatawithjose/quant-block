let selected = null;
const $ = (id) => document.getElementById(id);

async function select(name, li) {
  selected = name;
  document.querySelectorAll('#doc-list li').forEach((x) => x.classList.remove('sel'));
  li.classList.add('sel');
  window.kb.selectDoc(name);
  const info = await window.kb.docInfo(name);
  $('doc-meta').textContent =
    `Nombre: ${info.name} | Tamano: ${info.size} bytes | Modificado: ${new Date(info.mtime).toLocaleString()}`;
  $('doc-content').textContent = info.content;
}

async function refresh() {
  const names = await window.kb.listDocs();
  const ul = $('doc-list');
  ul.innerHTML = '';
  if (!names.length) {
    const li = document.createElement('li');
    li.textContent = '(sin documentos en data/docs)';
    ul.appendChild(li);
  }
  for (const n of names) {
    const li = document.createElement('li');
    li.textContent = n;
    if (n === selected) li.classList.add('sel');
    li.addEventListener('click', () => select(n, li));
    ul.appendChild(li);
  }
}

$('import').addEventListener('click', async () => {
  const r = await window.kb.importDocs();
  if (r.canceled) return;
  const parts = [`Importados: ${r.imported.length}`];
  if (r.renamed.length) parts.push(`Renombrados: ${r.renamed.map((x) => `${x.from} -> ${x.to}`).join(', ')}`);
  if (r.skipped.length) parts.push(`Omitidos: ${r.skipped.map((s) => `${s.file} (${s.reason})`).join(', ')}`);
  $('import-msg').textContent = parts.join('. ');
  await refresh();
  reindex();
});

function renderConversation(history) {
  const box = $('conversation');
  box.textContent = '';
  for (const t of history) {
    const d = document.createElement('div');
    d.className = 'turn';
    const q = document.createElement('div');
    q.className = 'q';
    q.textContent = t.q;
    const a = document.createElement('div');
    a.className = 'a';
    a.textContent = t.a;
    d.append(q, a);
    for (const c of t.citations) {
      const cd = document.createElement('div');
      cd.className = 'cite';
      const ref = document.createElement('div');
      ref.className = 'ref';
      ref.textContent = `${c.doc} ${c.chunkId}, linea ${c.line}` + (c.section ? ` (${c.section})` : '');
      const body = document.createElement('div');
      body.textContent = c.text;
      cd.append(ref, body);
      d.appendChild(cd);
    }
    box.appendChild(d);
  }
  $('answer').scrollTop = $('answer').scrollHeight;
}

$('ask').addEventListener('click', async () => {
  const question = $('question').value;
  if (!question.trim()) return;
  try {
    const r = await window.kb.convAsk(question);
    renderConversation(r.history);
    $('question').value = '';
  } catch (err) {
    $('answer').textContent = `Error: ${err && err.message ? err.message : err}`;
  }
});

$('new-conv').addEventListener('click', async () => {
  try {
    renderConversation(await window.kb.convClear());
  } catch (err) {
    $('answer').textContent = `Error: ${err && err.message ? err.message : err}`;
  }
});

function showIndex(s) {
  $('index-status').textContent =
    s.state === 'done' ? `Indexado: ${s.done}/${s.total} (listo, ${s.chunks} fragmentos)`
    : s.state === 'indexing' ? `Indexando: ${s.done}/${s.total}`
    : 'Sin indexar';
  const f = s.failed || [];
  $('index-failed').textContent = f.length ? `No se pudieron indexar: ${f.map((x) => `${x.doc} (${x.message})`).join(', ')}` : '';
}

async function reindex() {
  showIndex(await window.kb.indexStart());
}
window.kb.onIndexProgress(showIndex);

async function init() {
  const st = await window.kb.getState();
  selected = st.lastSelected;
  await refresh();
  const li = [...document.querySelectorAll('#doc-list li')].find((x) => x.textContent === selected);
  if (li) await select(selected, li); else selected = null;
  renderConversation(await window.kb.convGet());
  reindex();
}
init();
