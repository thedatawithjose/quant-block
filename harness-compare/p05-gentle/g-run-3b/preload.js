const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('kb', {
  listDocs: () => ipcRenderer.invoke('docs:list'),
  readDoc: (name) => ipcRenderer.invoke('docs:read', name),
  docInfo: (name) => ipcRenderer.invoke('docs:info', name),
  importDocs: () => ipcRenderer.invoke('docs:import'),
  getState: () => ipcRenderer.invoke('state:get'),
  selectDoc: (name) => ipcRenderer.invoke('state:select', name),
  indexStart: () => ipcRenderer.invoke('index:start'),
  indexStatus: () => ipcRenderer.invoke('index:status'),
  onIndexProgress: (cb) => ipcRenderer.on('index:progress', (_e, s) => cb(s)),
  askCited: (question) => ipcRenderer.invoke('qa:cited', question),
  ask: (name, question) => ipcRenderer.invoke('qa:ask', name, question),
});
