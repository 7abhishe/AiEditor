/**
 * CodeGenie AI Editor — Root Application Component
 * Split-pane layout with Editor + Tabbed Sidebar (Chat / Search / Git).
 * Includes: Command Palette, Toast Notifications, Error Boundary, Keyboard Shortcuts.
 */

import { useState, useCallback, useRef, useEffect, lazy, Suspense } from 'react';
import EditorPanel from './components/EditorPanel.jsx';
import ChatPanel from './components/ChatPanel.jsx';
import StatusBar from './components/StatusBar.jsx';
import CommandPalette from './components/CommandPalette.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';
import { ToastProvider, useToast } from './components/ToastProvider.jsx';
import useChat from './hooks/useChat.js';
import { getApiKey, setApiKey, detectBugs, refactorCode, generateTests } from './services/api.js';

// Lazy-load heavy sidebar panels for better initial load
const GitPanel = lazy(() => import('./components/GitPanel.jsx'));
const SearchPanel = lazy(() => import('./components/SearchPanel.jsx'));

function AppInner() {
    const chat = useChat();
    const toast = useToast();
    const [showSidebar, setShowSidebar] = useState(true);
    const [sidebarTab, setSidebarTab] = useState('chat'); // 'chat' | 'search' | 'git'
    const [showSettings, setShowSettings] = useState(false);
    const [showPalette, setShowPalette] = useState(false);
    const [apiKeyInput, setApiKeyInput] = useState(getApiKey());
    const [sidebarWidth, setSidebarWidth] = useState(380);
    const [projectPath, setProjectPath] = useState('');
    const [editorInfo, setEditorInfo] = useState({ language: '', cursor: null });
    const isResizing = useRef(false);

    // ── Global Keyboard Shortcuts ──────────────────────────
    useEffect(() => {
        const handler = (e) => {
            const meta = e.metaKey || e.ctrlKey;

            // ⌘K — Command Palette
            if (meta && e.key === 'k') {
                e.preventDefault();
                setShowPalette(p => !p);
            }
            // ⌘B — Toggle Sidebar
            if (meta && e.key === 'b') {
                e.preventDefault();
                setShowSidebar(p => !p);
            }
            // ⌘⇧F — Semantic Search
            if (meta && e.shiftKey && e.key === 'F') {
                e.preventDefault();
                setShowSidebar(true);
                setSidebarTab('search');
            }
            // ⌘, — Settings
            if (meta && e.key === ',') {
                e.preventDefault();
                setShowSettings(p => !p);
            }
        };

        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, []);

    // ── Resize Handle ──────────────────────────────────────
    const handleMouseDown = useCallback((e) => {
        e.preventDefault();
        isResizing.current = true;
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';

        const startX = e.clientX;
        const startWidth = sidebarWidth;

        const onMouseMove = (moveEvent) => {
            if (!isResizing.current) return;
            const delta = startX - moveEvent.clientX;
            const newWidth = Math.min(700, Math.max(280, startWidth + delta));
            setSidebarWidth(newWidth);
        };

        const onMouseUp = () => {
            isResizing.current = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            window.removeEventListener('mousemove', onMouseMove);
            window.removeEventListener('mouseup', onMouseUp);
        };

        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
    }, [sidebarWidth]);

    // ── Command Palette Handler ────────────────────────────
    const handleCommand = useCallback((commandId) => {
        switch (commandId) {
            case 'toggle-sidebar':
                setShowSidebar(p => !p);
                break;
            case 'open-chat':
                setShowSidebar(true);
                setSidebarTab('chat');
                break;
            case 'open-search':
                setShowSidebar(true);
                setSidebarTab('search');
                break;
            case 'open-git':
                setShowSidebar(true);
                setSidebarTab('git');
                break;
            case 'settings':
                setShowSettings(true);
                break;
            case 'new-chat':
                chat.newConversation();
                toast.info('Started new conversation');
                break;
            case 'find-bugs':
            case 'refactor':
            case 'generate-tests':
            case 'explain-code':
                toast.info('Select code in the editor, then right-click to use this feature');
                break;
            case 'ai-commit':
                setShowSidebar(true);
                setSidebarTab('git');
                toast.info('Use the ✨ button in the Git panel to generate a commit message');
                break;
            default:
                toast.info(`Command: ${commandId}`);
        }
    }, [chat, toast]);

    // ── Editor Context Menu Handlers ───────────────────────
    const handleExplain = useCallback((code, language) => {
        setShowSidebar(true);
        setSidebarTab('chat');
        const prompt = language
            ? `Explain the following ${language} code:\n\`\`\`${language}\n${code}\n\`\`\``
            : `Explain the following code:\n\`\`\`\n${code}\n\`\`\``;
        chat.send(prompt);
    }, [chat]);

    const handleFindBugs = useCallback(async (code, language) => {
        setShowSidebar(true);
        setSidebarTab('chat');
        chat.addMessage('user', `🐛 Find bugs in this ${language || ''} code:\n\`\`\`${language}\n${code}\n\`\`\``);
        chat.setLoading(true);
        try {
            const result = await detectBugs(code, language);
            let response = `## 🐛 Bug Detection Results\n\n**${result.summary}**\n\n`;
            if (result.bugs.length > 0) {
                result.bugs.forEach((bug, i) => {
                    const icon = bug.severity === 'critical' ? '🔴' : bug.severity === 'error' ? '🟠' : bug.severity === 'warning' ? '🟡' : '🔵';
                    response += `### ${icon} ${i + 1}. ${bug.category} — Line ${bug.line}\n`;
                    response += `**Severity:** ${bug.severity}\n\n`;
                    response += `${bug.description}\n\n`;
                    response += `**Fix:** ${bug.suggestion}\n\n---\n\n`;
                });
                toast.warning(`Found ${result.bugs.length} bug(s)`);
            } else {
                response += '✅ No bugs detected! The code looks clean.\n';
                toast.success('No bugs found!');
            }
            chat.addMessage('assistant', response);
        } catch (err) {
            chat.addMessage('assistant', `❌ Error: ${err.message}`);
            toast.error('Bug detection failed');
        } finally {
            chat.setLoading(false);
        }
    }, [chat, toast]);

    const handleRefactor = useCallback(async (code, language) => {
        setShowSidebar(true);
        setSidebarTab('chat');
        chat.addMessage('user', `🔧 Refactor this ${language || ''} code:\n\`\`\`${language}\n${code}\n\`\`\``);
        chat.setLoading(true);
        try {
            const result = await refactorCode(code, language);
            let response = `## 🔧 Refactoring Suggestions\n\n**${result.summary}**\n\n`;
            if (result.suggestions.length > 0) {
                result.suggestions.forEach((s, i) => {
                    response += `### ${i + 1}. ${s.title}\n\n`;
                    response += `${s.description}\n\n`;
                    response += `**Before:**\n\`\`\`${language}\n${s.original_code}\n\`\`\`\n\n`;
                    response += `**After:**\n\`\`\`${language}\n${s.refactored_code}\n\`\`\`\n\n---\n\n`;
                });
                toast.success(`${result.suggestions.length} refactoring suggestion(s)`);
            } else {
                response += '✅ The code looks well-structured! No refactoring needed.\n';
                toast.success('Code looks great!');
            }
            chat.addMessage('assistant', response);
        } catch (err) {
            chat.addMessage('assistant', `❌ Error: ${err.message}`);
            toast.error('Refactoring failed');
        } finally {
            chat.setLoading(false);
        }
    }, [chat, toast]);

    const handleGenerateTests = useCallback(async (code, language) => {
        setShowSidebar(true);
        setSidebarTab('chat');
        chat.addMessage('user', `🧪 Generate tests for this ${language || ''} code:\n\`\`\`${language}\n${code}\n\`\`\``);
        chat.setLoading(true);
        try {
            const result = await generateTests(code, language);
            let response = `## 🧪 Generated Tests (${result.framework})\n\n`;
            response += `**${result.test_count} test cases generated**\n\n`;
            response += `\`\`\`${language}\n${result.test_code}\n\`\`\`\n`;
            chat.addMessage('assistant', response);
            toast.success(`Generated ${result.test_count} tests`);
        } catch (err) {
            chat.addMessage('assistant', `❌ Error: ${err.message}`);
            toast.error('Test generation failed');
        } finally {
            chat.setLoading(false);
        }
    }, [chat, toast]);

    const handleSaveSettings = () => {
        setApiKey(apiKeyInput);
        setShowSettings(false);
        toast.success('Settings saved');
    };

    // Editor info callback
    const handleEditorInfo = useCallback((info) => {
        setEditorInfo(info);
    }, []);

    return (
        <div className="app">
            {/* Title Bar */}
            <div className="app-titlebar">
                <h1>⚡ CodeGenie</h1>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: '4px', WebkitAppRegion: 'no-drag' }}>
                    <button className="icon-btn" onClick={() => setShowPalette(true)} title="Command Palette (⌘K)">
                        ⚡
                    </button>
                    <button className="icon-btn" onClick={() => setShowSettings(true)} title="Settings (⌘,)">
                        ⚙️
                    </button>
                    <button
                        className="icon-btn"
                        onClick={() => setShowSidebar(!showSidebar)}
                        title={showSidebar ? 'Hide Sidebar (⌘B)' : 'Show Sidebar (⌘B)'}
                    >
                        💬
                    </button>
                </div>
            </div>

            {/* Main Body */}
            <div className="app-body">
                <EditorPanel
                    onExplain={handleExplain}
                    onFindBugs={handleFindBugs}
                    onRefactor={handleRefactor}
                    onGenerateTests={handleGenerateTests}
                    onEditorInfo={handleEditorInfo}
                />
                {showSidebar && (
                    <>
                        <div
                            className="resize-handle"
                            onMouseDown={handleMouseDown}
                        />
                        <div className="sidebar-container" style={{ width: sidebarWidth }}>
                            {/* Sidebar Tabs */}
                            <div className="sidebar-tabs">
                                <button
                                    className={`sidebar-tab ${sidebarTab === 'chat' ? 'active' : ''}`}
                                    onClick={() => setSidebarTab('chat')}
                                >
                                    <span className="tab-icon">💬</span> Chat
                                </button>
                                <button
                                    className={`sidebar-tab ${sidebarTab === 'search' ? 'active' : ''}`}
                                    onClick={() => setSidebarTab('search')}
                                >
                                    <span className="tab-icon">🔍</span> Search
                                </button>
                                <button
                                    className={`sidebar-tab ${sidebarTab === 'git' ? 'active' : ''}`}
                                    onClick={() => setSidebarTab('git')}
                                >
                                    <span className="tab-icon">🔀</span> Git
                                </button>
                            </div>

                            {/* Tab Content */}
                            {sidebarTab === 'chat' && (
                                <ChatPanel
                                    chat={chat}
                                    onToggle={() => setShowSidebar(false)}
                                />
                            )}
                            <Suspense fallback={<div className="git-loading">Loading...</div>}>
                                {sidebarTab === 'search' && (
                                    <SearchPanel
                                        projectPath={projectPath}
                                        onClose={() => setShowSidebar(false)}
                                    />
                                )}
                                {sidebarTab === 'git' && (
                                    <GitPanel
                                        projectPath={projectPath}
                                        onClose={() => setShowSidebar(false)}
                                    />
                                )}
                            </Suspense>
                        </div>
                    </>
                )}
            </div>

            {/* Status Bar */}
            <StatusBar
                language={editorInfo.language}
                cursorPosition={editorInfo.cursor}
            />

            {/* Command Palette */}
            <CommandPalette
                isOpen={showPalette}
                onClose={() => setShowPalette(false)}
                onExecute={handleCommand}
            />

            {/* Settings Modal */}
            {showSettings && (
                <div className="modal-overlay" onClick={() => setShowSettings(false)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <h3>⚙️ Settings</h3>
                        <label>API Key</label>
                        <input
                            type="password"
                            value={apiKeyInput}
                            onChange={(e) => setApiKeyInput(e.target.value)}
                            placeholder="cg_your_api_key_here"
                        />
                        <label style={{ marginTop: '12px' }}>Project Path (for Git & Search)</label>
                        <input
                            type="text"
                            value={projectPath}
                            onChange={(e) => setProjectPath(e.target.value)}
                            placeholder="/path/to/your/project"
                        />
                        <p style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginBottom: '16px' }}>
                            Set the project root for Git and Semantic Search features.
                        </p>
                        <div className="btn-row">
                            <button className="btn btn-secondary" onClick={() => setShowSettings(false)}>
                                Cancel
                            </button>
                            <button className="btn btn-primary" onClick={handleSaveSettings}>
                                Save
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

// Root export with providers
export default function App() {
    return (
        <ErrorBoundary>
            <ToastProvider>
                <AppInner />
            </ToastProvider>
        </ErrorBoundary>
    );
}
