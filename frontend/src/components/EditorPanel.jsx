/**
 * CodeGenie AI Editor — Editor Panel
 * Monaco Editor with file tabs, open/save, and context menu.
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import Editor from '@monaco-editor/react';

// Map file extensions to Monaco language IDs
const LANG_MAP = {
    js: 'javascript', jsx: 'javascript', ts: 'typescript', tsx: 'typescript',
    py: 'python', java: 'java', c: 'c', cpp: 'cpp', cs: 'csharp',
    go: 'go', rs: 'rust', rb: 'ruby', php: 'php', swift: 'swift',
    html: 'html', css: 'css', scss: 'scss', less: 'less',
    json: 'json', md: 'markdown', yaml: 'yaml', yml: 'yaml',
    xml: 'xml', sql: 'sql', sh: 'shell', bash: 'shell',
    toml: 'ini', txt: 'plaintext', dockerfile: 'dockerfile',
};

function getLanguage(ext) {
    return LANG_MAP[ext?.toLowerCase()] || 'plaintext';
}

export default function EditorPanel({ onExplain, onFindBugs, onRefactor, onGenerateTests, onEditorInfo }) {
    const [tabs, setTabs] = useState([]);
    const [activeTab, setActiveTab] = useState(null);
    const editorRef = useRef(null);
    const monacoRef = useRef(null);

    // Listen for file opened from Electron menu
    useEffect(() => {
        if (window.electronAPI) {
            window.electronAPI.onFileOpened((fileData) => {
                openFileTab(fileData);
            });
            window.electronAPI.onMenuSave(() => {
                handleSave();
            });
        }
    }, []);

    const openFileTab = useCallback((fileData) => {
        const { filePath, fileName, content, ext } = fileData;

        // Check if tab already open
        const existingIndex = tabs.findIndex(t => t.filePath === filePath);
        if (existingIndex !== -1) {
            setActiveTab(existingIndex);
            return;
        }

        const newTab = {
            filePath,
            fileName,
            content,
            language: getLanguage(ext),
            isDirty: false,
        };

        setTabs(prev => [...prev, newTab]);
        setActiveTab(tabs.length);
    }, [tabs]);

    const handleOpenFile = async () => {
        if (window.electronAPI) {
            await window.electronAPI.openFile();
        }
    };

    const handleSave = async () => {
        if (activeTab === null || !tabs[activeTab]) return;
        const tab = tabs[activeTab];

        if (window.electronAPI && tab.filePath) {
            const content = editorRef.current?.getValue() || tab.content;
            await window.electronAPI.saveFile({ filePath: tab.filePath, content });
            setTabs(prev => prev.map((t, i) =>
                i === activeTab ? { ...t, isDirty: false, content } : t
            ));
        }
    };

    const handleCloseTab = (index, e) => {
        e?.stopPropagation();
        const newTabs = tabs.filter((_, i) => i !== index);
        setTabs(newTabs);

        if (activeTab === index) {
            setActiveTab(newTabs.length > 0 ? Math.max(0, index - 1) : null);
        } else if (activeTab > index) {
            setActiveTab(activeTab - 1);
        }
    };

    const handleEditorChange = (value) => {
        if (activeTab !== null) {
            setTabs(prev => prev.map((t, i) =>
                i === activeTab ? { ...t, content: value, isDirty: true } : t
            ));
        }
    };

    const handleEditorMount = (editor, monaco) => {
        editorRef.current = editor;
        monacoRef.current = monaco;

        // Cmd+S / Ctrl+S
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
            handleSave();
        });

        // Right-click context menu: Explain with CodeGenie
        editor.addAction({
            id: 'codegenie.explain',
            label: '✨ Explain with CodeGenie',
            contextMenuGroupId: '9_codegenie',
            contextMenuOrder: 1,
            run: (ed) => {
                const selection = ed.getModel().getValueInRange(ed.getSelection());
                if (selection && onExplain) {
                    const lang = tabs[activeTab]?.language || '';
                    onExplain(selection, lang);
                }
            },
        });

        // Right-click context menu: Find Bugs
        editor.addAction({
            id: 'codegenie.findBugs',
            label: '🐛 Find Bugs with CodeGenie',
            contextMenuGroupId: '9_codegenie',
            contextMenuOrder: 2,
            run: (ed) => {
                const selection = ed.getModel().getValueInRange(ed.getSelection());
                if (selection && onFindBugs) {
                    const lang = tabs[activeTab]?.language || '';
                    onFindBugs(selection, lang);
                }
            },
        });

        // Right-click context menu: Refactor
        editor.addAction({
            id: 'codegenie.refactor',
            label: '🔧 Refactor with CodeGenie',
            contextMenuGroupId: '9_codegenie',
            contextMenuOrder: 3,
            run: (ed) => {
                const selection = ed.getModel().getValueInRange(ed.getSelection());
                if (selection && onRefactor) {
                    const lang = tabs[activeTab]?.language || '';
                    onRefactor(selection, lang);
                }
            },
        });

        // Right-click context menu: Generate Tests
        editor.addAction({
            id: 'codegenie.generateTests',
            label: '🧪 Generate Tests with CodeGenie',
            contextMenuGroupId: '9_codegenie',
            contextMenuOrder: 4,
            run: (ed) => {
                const selection = ed.getModel().getValueInRange(ed.getSelection());
                if (selection && onGenerateTests) {
                    const lang = tabs[activeTab]?.language || '';
                    onGenerateTests(selection, lang);
                }
            },
        });

        // Emit cursor position & language on change
        editor.onDidChangeCursorPosition((e) => {
            if (onEditorInfo) {
                const lang = tabs[activeTab]?.language || '';
                onEditorInfo({ language: lang, cursor: { line: e.position.lineNumber, column: e.position.column } });
            }
        });

        // Focus the editor
        editor.focus();
    };

    const currentTab = activeTab !== null ? tabs[activeTab] : null;

    return (
        <div className="editor-panel">
            {/* Tabs */}
            <div className="editor-tabs">
                {tabs.map((tab, index) => (
                    <button
                        key={tab.filePath || index}
                        className={`editor-tab ${index === activeTab ? 'active' : ''}`}
                        onClick={() => setActiveTab(index)}
                    >
                        <span>{tab.isDirty ? '● ' : ''}{tab.fileName}</span>
                        <span className="close-btn" onClick={(e) => handleCloseTab(index, e)}>×</span>
                    </button>
                ))}
            </div>

            {/* Editor or Empty State */}
            {currentTab ? (
                <div className="editor-container">
                    <Editor
                        height="100%"
                        language={currentTab.language}
                        value={currentTab.content}
                        theme="vs-dark"
                        onChange={handleEditorChange}
                        onMount={handleEditorMount}
                        options={{
                            fontSize: 14,
                            fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                            fontLigatures: true,
                            minimap: { enabled: true, scale: 1 },
                            scrollBeyondLastLine: false,
                            wordWrap: 'off',
                            lineNumbers: 'on',
                            renderLineHighlight: 'all',
                            cursorBlinking: 'smooth',
                            cursorSmoothCaretAnimation: 'on',
                            smoothScrolling: true,
                            padding: { top: 10 },
                            bracketPairColorization: { enabled: true },
                            guides: { bracketPairs: 'active' },
                            suggest: { showWords: true },
                            tabSize: 2,
                        }}
                    />
                </div>
            ) : (
                <div className="editor-empty">
                    <div className="logo">⚡</div>
                    <h2 style={{ fontSize: '18px', fontWeight: 600 }}>CodeGenie AI Editor</h2>
                    <p>Open a file to start editing</p>
                    <p>
                        <kbd>⌘O</kbd> to open a file
                    </p>
                    <button
                        className="icon-btn"
                        style={{ width: 'auto', padding: '8px 16px', fontSize: '13px', gap: '6px', display: 'flex' }}
                        onClick={handleOpenFile}
                    >
                        📂 Open File
                    </button>
                </div>
            )}
        </div>
    );
}
