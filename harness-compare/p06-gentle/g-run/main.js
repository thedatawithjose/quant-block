const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('node:path');
const { ensureDocsDir, listDocs, readDoc, docInfo, importDocs } = require('./lib/docs');
const { loadState, saveState, recordImports, setLastSelected, setConversation } = require('./lib/state');
const { answer } = require('./lib/qa');
const { createIndexer } = require('./lib/indexer');
const { answerWithCitations } = require('./lib/cite');
const { askInConversation } = require('./lib/conversation');
const { createLogger } = require('./lib/logger');

let docsDir;
let state;
let indexer;
let log;

function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  win.webContents.on('context-menu', (_e, params) => {
    const items = [];
    if (params.isEditable) items.push({ role: 'cut' }, { role: 'copy' }, { role: 'paste' }, { type: 'separator' }, { role: 'selectAll' });
    else if (params.selectionText) items.push({ role: 'copy' }, { type: 'separator' }, { role: 'selectAll' });
    else items.push({ role: 'selectAll' });
    Menu.buildFromTemplate(items).popup({ window: win });
  });
  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
  return win;
}

app.whenReady().then(() => {
  log = createLogger({ file: path.join(__dirname, 'data', 'app.log') });
  docsDir = ensureDocsDir(__dirname);
  log.info('app.start', { docsDir });
  state = loadState(__dirname);
  ipcMain.handle('state:get', () => state);
  ipcMain.handle('state:select', (_e, name) => {
    state = setLastSelected(state, name);
    saveState(__dirname, state);
    return state;
  });
  ipcMain.handle('docs:list', () => listDocs(docsDir));
  ipcMain.handle('docs:read', (_e, name) => readDoc(docsDir, name));
  ipcMain.handle('docs:info', (_e, name) => docInfo(docsDir, name));
  ipcMain.handle('docs:import', async (e) => {
    const win = BrowserWindow.fromWebContents(e.sender);
    const r = await dialog.showOpenDialog(win, {
      properties: ['openFile', 'multiSelections'],
      filters: [{ name: 'Documentos', extensions: ['md', 'txt'] }],
    });
    if (r.canceled) return { imported: [], skipped: [], renamed: [], canceled: true };
    const res = importDocs(docsDir, r.filePaths);
    log.info('import.done', { imported: res.imported.length, skipped: res.skipped.length });
    if (res.records.length) { state = recordImports(state, res.records); saveState(__dirname, state); }
    return res;
  });
  ipcMain.handle('qa:ask', (_e, name, question) => {
    let text = null;
    if (name) { try { text = readDoc(docsDir, name); } catch { text = null; } }
    return answer(text, question);
  });
  indexer = createIndexer(docsDir, { file: path.join(__dirname, 'data', 'index.json'), logger: log });
  ipcMain.handle('index:start', (e) => indexer.start((s) => {
    if (!e.sender.isDestroyed()) e.sender.send('index:progress', s);
  }));
  ipcMain.handle('qa:cited', async (_e, question, opts) => {
    if (indexer.status().state !== 'done') await indexer.start();
    return answerWithCitations(indexer.get(), question, opts);
  });
  ipcMain.handle('conv:get', () => state.conversation);
  ipcMain.handle('conv:ask', async (_e, question) => {
    try {
      if (indexer.status().state !== 'done') await indexer.start();
      const { history, turn } = askInConversation(state.conversation, question, indexer.get());
      if (!turn) return { history, turn: null };
      state = setConversation(state, history);
      saveState(__dirname, state);
      log.info('conv.ask', { effectiveQuery: turn.effectiveQuery, turns: history.length, citations: turn.citations.length });
      return { history, turn };
    } catch (err) {
      log.error('conv.ask.failed', { err });
      throw err;
    }
  });
  ipcMain.handle('conv:clear', () => {
    const cleared = state.conversation.length;
    state = setConversation(state, []);
    saveState(__dirname, state);
    log.info('conv.clear', { cleared });
    return [];
  });
  ipcMain.handle('index:status', () => indexer.status());
  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
