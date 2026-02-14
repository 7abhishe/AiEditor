/**
 * CodeGenie AI Editor — Electron Preload Script
 * Exposes safe IPC methods to the renderer via contextBridge.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    // File operations
    openFile: () => ipcRenderer.invoke('dialog:openFile'),
    saveFile: (data) => ipcRenderer.invoke('file:save', data),
    readFile: (filePath) => ipcRenderer.invoke('file:read', filePath),

    // Listen for menu events
    onFileOpened: (callback) => {
        ipcRenderer.on('file:opened', (_event, data) => callback(data));
    },
    onMenuSave: (callback) => {
        ipcRenderer.on('menu:save', () => callback());
    },
});
