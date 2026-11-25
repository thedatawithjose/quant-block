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
  if (r.skipped.length) parts.push(`Omitidos: ${r.skipped.map((s) => `${s.file} (${s.reason})`).join(', ')}`);
  $('import-msg').textContent = parts.join('. ');
  await refresh();
  reindex();
});

function renderConv(history) {
  const box = $('conversation');
  box.innerHTML = '';
  for (const t of history) {
    const turn = document.createElement('div');
    turn.className = 'turn';
    const q = document.createElement('div');
    q.className = 'q';
    q.textContent = t.q;
    const a = document.createElement('div');
    a.className = 'a';
    a.textContent = t.a;
    turn.append(q, a);
    for (const c of t.citations) {
      const d = document.createElement('div');
      d.className = 'cite';
      const ref = document.createElement('div');
      ref.className = 'ref';
      ref.textContent = `${c.doc} - ${c.chunkId} - linea ${c.line}`;
      const body = document.createElement('div');
      body.textContent = c.text;
      d.append(ref, body);
      turn.appendChild(d);
    }
    box.appendChild(turn);
  }
  box.scrollTop = box.scrollHeight;
}

$('ask').addEventListener('click', async () => {
  const question = $('question').value;
  if (!question.trim()) return;
  const r = await window.kb.convAsk(question);
  $('question').value = '';
  renderConv(r.history);
});

$('conv-clear').addEventListener('click', async () => {
  renderConv(await window.kb.convClear());
});

function showIndex(s) {
  $('index-status').textContent =
    s.state === 'done' ? `Indexado: ${s.done}/${s.total} (listo, ${s.chunks} fragmentos)`
    : s.state === 'indexing' ? `Indexando: ${s.done}/${s.total}`
    : 'Sin indexar';
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
  renderConv(await window.kb.convGet());
  reindex();
}
init();
