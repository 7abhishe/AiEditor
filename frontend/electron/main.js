/**
 * CodeGenie AI Editor — Electron Main Process
 * Creates the main window, file dialogs, and menu.
 */

import { app, BrowserWindow, dialog, ipcMain, Menu } from 'electron';
import { readFile, writeFile } from 'fs/promises';
import path from 'path';

let mainWindow;

const isDev = !app.isPackaged;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 900,
        minHeight: 600,
        title: 'CodeGenie AI Editor',
        backgroundColor: '#0d1117',
        titleBarStyle: 'hiddenInset',
        trafficLightPosition: { x: 15, y: 15 },
        webPreferences: {
            preload: path.join(import.meta.dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
        },
    });

    if (isDev) {
        mainWindow.loadURL('http://localhost:5173');
    } else {
        mainWindow.loadFile(path.join(import.meta.dirname, '../dist/index.html'));
    }

    // Build menu
    const menuTemplate = [
        {
            label: 'File',
            submenu: [
                {
                    label: 'Open File',
                    accelerator: 'CmdOrCtrl+O',
                    click: () => handleOpenFile(),
                },
                {
                    label: 'Save',
                    accelerator: 'CmdOrCtrl+S',
                    click: () => mainWindow.webContents.send('menu:save'),
                },
                { type: 'separator' },
                { role: 'quit' },
            ],
        },
        {
            label: 'Edit',
            submenu: [
                { role: 'undo' },
                { role: 'redo' },
                { type: 'separator' },
                { role: 'cut' },
                { role: 'copy' },
                { role: 'paste' },
                { role: 'selectAll' },
            ],
        },
        {
            label: 'View',
            submenu: [
                { role: 'reload' },
                { role: 'toggleDevTools' },
                { type: 'separator' },
                { role: 'resetZoom' },
                { role: 'zoomIn' },
                { role: 'zoomOut' },
                { type: 'separator' },
                { role: 'togglefullscreen' },
            ],
        },
    ];

    if (process.platform === 'darwin') {
        menuTemplate.unshift({
            label: app.getName(),
            submenu: [
                { role: 'about' },
                { type: 'separator' },
                { role: 'services' },
                { type: 'separator' },
                { role: 'hide' },
                { role: 'hideOthers' },
                { role: 'unhide' },
                { type: 'separator' },
                { role: 'quit' },
            ],
        });
    }

    Menu.setApplicationMenu(Menu.buildFromTemplate(menuTemplate));
}

// ── IPC Handlers ──────────────────────────────────────

async function handleOpenFile() {
    const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [
            { name: 'Code Files', extensions: ['js', 'jsx', 'ts', 'tsx', 'py', 'java', 'c', 'cpp', 'go', 'rs', 'html', 'css', 'json', 'md', 'txt', 'yaml', 'yml', 'toml', 'xml', 'sql', 'sh', 'bash'] },
            { name: 'All Files', extensions: ['*'] },
        ],
    });

    if (canceled || filePaths.length === 0) return null;

    const filePath = filePaths[0];
    const content = await readFile(filePath, 'utf-8');
    const fileName = path.basename(filePath);
    const ext = path.extname(filePath).slice(1);

    mainWindow.webContents.send('file:opened', { filePath, fileName, content, ext });
    return { filePath, fileName, content, ext };
}

ipcMain.handle('dialog:openFile', handleOpenFile);

ipcMain.handle('file:save', async (_event, { filePath, content }) => {
    await writeFile(filePath, content, 'utf-8');
    return true;
});

ipcMain.handle('file:read', async (_event, filePath) => {
    const content = await readFile(filePath, 'utf-8');
    const fileName = path.basename(filePath);
    const ext = path.extname(filePath).slice(1);
    return { filePath, fileName, content, ext };
});

// ── App Lifecycle ─────────────────────────────────────

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
