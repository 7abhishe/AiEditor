/**
 * CodeGenie AI Editor — Git Panel
 * Shows git status, branches, commit history, and AI-powered commits.
 */

import { useState, useEffect, useCallback } from 'react';
import { gitStatus, gitLog, gitBranches, gitCommit, gitAiMessage, gitCheckout, gitDiff, gitStageFile } from '../services/api.js';

export default function GitPanel({ projectPath, onClose }) {
    const [tab, setTab] = useState('changes'); // 'changes' | 'log' | 'branches'
    const [files, setFiles] = useState([]);
    const [commits, setCommits] = useState([]);
    const [branches, setBranches] = useState([]);
    const [currentBranch, setCurrentBranch] = useState('');
    const [commitMsg, setCommitMsg] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [diffText, setDiffText] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);

    // Status icons
    const statusIcon = {
        modified: '✏️',
        added: '➕',
        deleted: '🗑️',
        untracked: '❓',
        renamed: '📝',
        staged: '✅',
    };

    const statusColor = {
        modified: '#e5c07b',
        added: '#98c379',
        deleted: '#e06c75',
        untracked: '#abb2bf',
        renamed: '#c678dd',
    };

    // Fetch data
    const refresh = useCallback(async () => {
        if (!projectPath) return;
        setLoading(true);
        setError('');
        try {
            const [statusRes, branchRes] = await Promise.all([
                gitStatus(projectPath),
                gitBranches(projectPath),
            ]);
            setFiles(statusRes.files || []);
            setBranches(branchRes.branches || []);
            setCurrentBranch(branchRes.current || '');
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, [projectPath]);

    const fetchLog = useCallback(async () => {
        if (!projectPath) return;
        setLoading(true);
        try {
            const res = await gitLog(20, projectPath);
            setCommits(res.commits || []);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, [projectPath]);

    useEffect(() => {
        refresh();
    }, [refresh]);

    useEffect(() => {
        if (tab === 'log') fetchLog();
    }, [tab, fetchLog]);

    // AI commit message
    const handleAiMessage = async () => {
        setLoading(true);
        try {
            const res = await gitAiMessage(projectPath);
            setCommitMsg(res.message);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    // Commit
    const handleCommit = async () => {
        if (!commitMsg.trim()) return;
        setLoading(true);
        try {
            await gitCommit(commitMsg, projectPath);
            setCommitMsg('');
            await refresh();
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    // Checkout branch
    const handleCheckout = async (branch) => {
        setLoading(true);
        try {
            await gitCheckout(branch, projectPath);
            await refresh();
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    // Show file diff
    const handleFileDiff = async (filePath) => {
        setSelectedFile(filePath === selectedFile ? null : filePath);
        if (filePath === selectedFile) {
            setDiffText('');
            return;
        }
        try {
            const res = await gitDiff(filePath, false, projectPath);
            setDiffText(res.diff || '(no diff available)');
        } catch (e) {
            setDiffText(`Error: ${e.message}`);
        }
    };

    // Stage/unstage
    const handleToggleStage = async (filePath, isStaged) => {
        try {
            await gitStageFile(filePath, isStaged ? 'unstage' : 'stage', projectPath);
            await refresh();
        } catch (e) {
            setError(e.message);
        }
    };

    if (!projectPath) {
        return (
            <div className="git-panel">
                <div className="git-header">
                    <h3>🔀 Source Control</h3>
                    <button className="icon-btn" onClick={onClose} title="Close">✕</button>
                </div>
                <div className="git-empty">
                    <div style={{ fontSize: '32px', marginBottom: '12px' }}>📂</div>
                    <p>Open a project folder to use Git</p>
                </div>
            </div>
        );
    }

    return (
        <div className="git-panel">
            {/* Header */}
            <div className="git-header">
                <h3>
                    🔀 Source Control
                    {currentBranch && <span className="git-branch-badge">{currentBranch}</span>}
                </h3>
                <div style={{ display: 'flex', gap: '4px' }}>
                    <button className="icon-btn" onClick={refresh} title="Refresh">🔄</button>
                    <button className="icon-btn" onClick={onClose} title="Close">✕</button>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className="git-error">
                    ⚠️ {error}
                    <button className="icon-btn" onClick={() => setError('')}>✕</button>
                </div>
            )}

            {/* Tabs */}
            <div className="git-tabs">
                <button
                    className={`git-tab ${tab === 'changes' ? 'active' : ''}`}
                    onClick={() => setTab('changes')}
                >
                    Changes {files.length > 0 && <span className="git-count">{files.length}</span>}
                </button>
                <button
                    className={`git-tab ${tab === 'log' ? 'active' : ''}`}
                    onClick={() => setTab('log')}
                >
                    History
                </button>
                <button
                    className={`git-tab ${tab === 'branches' ? 'active' : ''}`}
                    onClick={() => setTab('branches')}
                >
                    Branches
                </button>
            </div>

            {/* Tab Content */}
            <div className="git-content">
                {loading && <div className="git-loading">Loading...</div>}

                {/* Changes Tab */}
                {tab === 'changes' && !loading && (
                    <>
                        {/* Commit area */}
                        <div className="git-commit-area">
                            <div className="git-commit-input">
                                <input
                                    type="text"
                                    value={commitMsg}
                                    onChange={(e) => setCommitMsg(e.target.value)}
                                    placeholder="Commit message..."
                                    onKeyDown={(e) => e.key === 'Enter' && handleCommit()}
                                />
                                <button
                                    className="git-ai-btn"
                                    onClick={handleAiMessage}
                                    title="Generate AI commit message"
                                    disabled={loading}
                                >
                                    ✨
                                </button>
                            </div>
                            <button
                                className="git-commit-btn"
                                onClick={handleCommit}
                                disabled={!commitMsg.trim() || loading}
                            >
                                ✓ Commit
                            </button>
                        </div>

                        {/* File list */}
                        {files.length === 0 ? (
                            <div className="git-empty">
                                <p style={{ color: 'var(--text-tertiary)' }}>No changes detected</p>
                            </div>
                        ) : (
                            <div className="git-files">
                                {files.map((file) => (
                                    <div key={file.path} className="git-file-item">
                                        <div className="git-file-row" onClick={() => handleFileDiff(file.path)}>
                                            <span className="git-file-icon">{statusIcon[file.status] || '📄'}</span>
                                            <span className="git-file-name" title={file.path}>
                                                {file.path.split('/').pop()}
                                            </span>
                                            <span className="git-file-path" title={file.path}>
                                                {file.path.includes('/') ? file.path.substring(0, file.path.lastIndexOf('/')) : ''}
                                            </span>
                                            <span
                                                className="git-file-status"
                                                style={{ color: statusColor[file.status] || '#abb2bf' }}
                                            >
                                                {file.status[0].toUpperCase()}
                                            </span>
                                            <button
                                                className="git-stage-btn"
                                                onClick={(e) => { e.stopPropagation(); handleToggleStage(file.path, file.staged); }}
                                                title={file.staged ? 'Unstage' : 'Stage'}
                                            >
                                                {file.staged ? '−' : '+'}
                                            </button>
                                        </div>
                                        {selectedFile === file.path && (
                                            <div className="git-diff-preview">
                                                <pre>{diffText}</pre>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </>
                )}

                {/* Log Tab */}
                {tab === 'log' && !loading && (
                    <div className="git-log">
                        {commits.map((commit) => (
                            <div key={commit.hash} className="git-commit-item">
                                <div className="git-commit-msg">{commit.message}</div>
                                <div className="git-commit-meta">
                                    <span className="git-commit-hash">{commit.short_hash}</span>
                                    <span className="git-commit-author">{commit.author}</span>
                                    <span className="git-commit-date">{commit.date}</span>
                                </div>
                            </div>
                        ))}
                        {commits.length === 0 && (
                            <div className="git-empty"><p>No commits yet</p></div>
                        )}
                    </div>
                )}

                {/* Branches Tab */}
                {tab === 'branches' && !loading && (
                    <div className="git-branches">
                        {branches.map((branch) => (
                            <div
                                key={branch.name}
                                className={`git-branch-item ${branch.is_current ? 'current' : ''}`}
                                onClick={() => !branch.is_current && handleCheckout(branch.name)}
                            >
                                <span className="git-branch-icon">{branch.is_current ? '●' : '○'}</span>
                                <span className="git-branch-name">{branch.name}</span>
                                {branch.is_current && <span className="git-current-label">current</span>}
                            </div>
                        ))}
                        {branches.length === 0 && (
                            <div className="git-empty"><p>No branches found</p></div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
