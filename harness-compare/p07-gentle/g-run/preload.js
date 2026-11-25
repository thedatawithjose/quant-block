const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('kb', {
  listDocs: () => ipcRenderer.invoke('docs:list'),
  docInfo: (name) => ipcRenderer.invoke('docs:info', name),
  importDocs: () => ipcRenderer.invoke('docs:import'),
  getState: () => ipcRenderer.invoke('state:get'),
  selectDoc: (name) => ipcRenderer.invoke('state:select', name),
  indexStart: () => ipcRenderer.invoke('index:start'),
  onIndexProgress: (cb) => ipcRenderer.on('index:progress', (_e, s) => cb(s)),
  convGet: () => ipcRenderer.invoke('conv:get'),
  convAsk: (q) => ipcRenderer.invoke('conv:ask', q),
  convClear: () => ipcRenderer.invoke('conv:clear'),
  convExport: (range) => ipcRenderer.invoke('conv:export', range),
});
