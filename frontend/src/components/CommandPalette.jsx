/**
 * CodeGenie AI Editor — Command Palette
 * VS Code-style ⌘K command palette with fuzzy search.
 */

import { useState, useRef, useEffect, useMemo } from 'react';

const COMMANDS = [
    { id: 'open-file', label: 'Open File', icon: '📂', shortcut: '⌘O', group: 'File' },
    { id: 'save-file', label: 'Save File', icon: '💾', shortcut: '⌘S', group: 'File' },
    { id: 'toggle-sidebar', label: 'Toggle Sidebar', icon: '📐', shortcut: '⌘B', group: 'View' },
    { id: 'open-chat', label: 'Open Chat', icon: '💬', shortcut: '', group: 'View' },
    { id: 'open-search', label: 'Semantic Search', icon: '🔍', shortcut: '⌘⇧F', group: 'View' },
    { id: 'open-git', label: 'Source Control', icon: '🔀', shortcut: '', group: 'View' },
    { id: 'find-bugs', label: 'Find Bugs', icon: '🐛', shortcut: '', group: 'AI' },
    { id: 'refactor', label: 'Refactor Code', icon: '🔧', shortcut: '', group: 'AI' },
    { id: 'generate-tests', label: 'Generate Tests', icon: '🧪', shortcut: '', group: 'AI' },
    { id: 'explain-code', label: 'Explain Code', icon: '💡', shortcut: '', group: 'AI' },
    { id: 'ai-commit', label: 'AI Commit Message', icon: '✨', shortcut: '', group: 'Git' },
    { id: 'new-chat', label: 'New Conversation', icon: '🗒️', shortcut: '', group: 'Chat' },
    { id: 'settings', label: 'Open Settings', icon: '⚙️', shortcut: '⌘,', group: 'App' },
];

export default function CommandPalette({ isOpen, onClose, onExecute }) {
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const inputRef = useRef(null);
    const listRef = useRef(null);

    // Fuzzy filter
    const filtered = useMemo(() => {
        if (!query.trim()) return COMMANDS;
        const q = query.toLowerCase();
        return COMMANDS.filter(cmd =>
            cmd.label.toLowerCase().includes(q) ||
            cmd.group.toLowerCase().includes(q) ||
            cmd.id.includes(q)
        );
    }, [query]);

    // Focus input when opened
    useEffect(() => {
        if (isOpen) {
            setQuery('');
            setSelectedIndex(0);
            setTimeout(() => inputRef.current?.focus(), 50);
        }
    }, [isOpen]);

    // Keep selected item in view
    useEffect(() => {
        if (listRef.current) {
            const item = listRef.current.children[selectedIndex];
            if (item) item.scrollIntoView({ block: 'nearest' });
        }
    }, [selectedIndex]);

    const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
            onClose();
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex(i => Math.min(i + 1, filtered.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex(i => Math.max(i - 1, 0));
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (filtered[selectedIndex]) {
                onExecute(filtered[selectedIndex].id);
                onClose();
            }
        }
    };

    if (!isOpen) return null;

    // Group the filtered commands
    const groups = {};
    filtered.forEach(cmd => {
        if (!groups[cmd.group]) groups[cmd.group] = [];
        groups[cmd.group].push(cmd);
    });

    return (
        <div className="palette-overlay" onClick={onClose}>
            <div className="palette" onClick={(e) => e.stopPropagation()}>
                <div className="palette-input-wrapper">
                    <span className="palette-icon">⚡</span>
                    <input
                        ref={inputRef}
                        type="text"
                        className="palette-input"
                        value={query}
                        onChange={(e) => { setQuery(e.target.value); setSelectedIndex(0); }}
                        onKeyDown={handleKeyDown}
                        placeholder="Type a command..."
                    />
                    <kbd className="palette-kbd">ESC</kbd>
                </div>
                <div className="palette-list" ref={listRef}>
                    {filtered.length === 0 && (
                        <div className="palette-empty">No commands found</div>
                    )}
                    {Object.entries(groups).map(([group, cmds]) => (
                        <div key={group}>
                            <div className="palette-group">{group}</div>
                            {cmds.map((cmd) => {
                                const globalIdx = filtered.indexOf(cmd);
                                return (
                                    <div
                                        key={cmd.id}
                                        className={`palette-item ${globalIdx === selectedIndex ? 'selected' : ''}`}
                                        onClick={() => { onExecute(cmd.id); onClose(); }}
                                        onMouseEnter={() => setSelectedIndex(globalIdx)}
                                    >
                                        <span className="palette-item-icon">{cmd.icon}</span>
                                        <span className="palette-item-label">{cmd.label}</span>
                                        {cmd.shortcut && (
                                            <kbd className="palette-item-shortcut">{cmd.shortcut}</kbd>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
