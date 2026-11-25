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

function div(cls, text) {
  const d = document.createElement('div');
  d.className = cls;
  d.textContent = text;
  return d;
}

function renderConversation(history) {
  const box = $('answer');
  box.innerHTML = '';
  for (const t of history) {
    const turn = document.createElement('div');
    turn.className = 'turn';
    turn.appendChild(div('q', `Pregunta: ${t.q}`));
    if (t.effectiveQuery !== t.q) turn.appendChild(div('eq', `Consulta efectiva: ${t.effectiveQuery}`));
    turn.appendChild(div('a', t.a));
    for (const c of t.citations) {
      const d = document.createElement('div');
      d.className = 'cite';
      d.append(div('ref', `${c.doc} - ${c.chunkId} - linea ${c.line}`), div('', c.text));
      turn.appendChild(d);
    }
    box.appendChild(turn);
  }
  box.scrollTop = box.scrollHeight;
}

let asking = false;
$('ask').addEventListener('click', async () => {
  const value = $('question').value;
  if (asking || !value.trim()) return;
  asking = true;
  $('ask-msg').textContent = '';
  try {
    const r = await window.kb.convAsk(value);
    renderConversation(r.history);
    if (r.turn) $('question').value = '';
    else $('ask-msg').textContent = 'No hay respuesta: escribe una pregunta con palabras e indexa documentos.';
  } catch (err) {
    $('ask-msg').textContent = `Error al preguntar: ${err && err.message ? err.message : err}`;
  } finally {
    asking = false;
  }
});

$('new-conv').addEventListener('click', async () => {
  renderConversation(await window.kb.convClear());
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
  renderConversation(await window.kb.convGet());
  reindex();
}
init();
