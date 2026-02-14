/**
 * CodeGenie AI Editor — Search Panel
 * Semantic code search powered by FAISS embeddings.
 */

import { useState, useCallback, useRef } from 'react';
import { semanticSearch } from '../services/api.js';

export default function SearchPanel({ projectPath, onClose, onOpenFile }) {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searched, setSearched] = useState(false);
    const debounceRef = useRef(null);

    const doSearch = useCallback(async (searchQuery) => {
        if (!searchQuery.trim()) {
            setResults([]);
            setSearched(false);
            return;
        }

        setLoading(true);
        setSearched(true);
        try {
            const res = await semanticSearch(searchQuery, 10, projectPath);
            // Group results by file
            const grouped = {};
            (res.results || []).forEach((r) => {
                const file = r.file_path || r.metadata?.file_path || 'unknown';
                if (!grouped[file]) grouped[file] = [];
                grouped[file].push(r);
            });
            setResults(Object.entries(grouped));
        } catch (e) {
            setResults([]);
        } finally {
            setLoading(false);
        }
    }, [projectPath]);

    const handleInput = (e) => {
        const val = e.target.value;
        setQuery(val);

        // Debounce search
        if (debounceRef.current) clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(() => doSearch(val), 400);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            if (debounceRef.current) clearTimeout(debounceRef.current);
            doSearch(query);
        }
    };

    return (
        <div className="search-panel">
            {/* Header */}
            <div className="search-header">
                <h3>🔍 Semantic Search</h3>
                <button className="icon-btn" onClick={onClose} title="Close">✕</button>
            </div>

            {/* Search Input */}
            <div className="search-input-area">
                <input
                    type="text"
                    value={query}
                    onChange={handleInput}
                    onKeyDown={handleKeyDown}
                    placeholder="Search by meaning... (e.g. 'database connection handler')"
                    autoFocus
                />
            </div>

            {/* Results */}
            <div className="search-results">
                {loading && (
                    <div className="search-empty">
                        <p>Searching...</p>
                    </div>
                )}

                {!loading && searched && results.length === 0 && (
                    <div className="search-empty">
                        <div style={{ fontSize: '24px', marginBottom: '8px' }}>🔍</div>
                        <p>No results found</p>
                        <p style={{ fontSize: '11px', marginTop: '4px' }}>
                            Make sure your project is indexed first
                        </p>
                    </div>
                )}

                {!loading && !searched && (
                    <div className="search-empty">
                        <div style={{ fontSize: '32px', marginBottom: '12px' }}>🔍</div>
                        <p>Search your codebase by meaning</p>
                        <p style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '4px' }}>
                            Powered by AI embeddings
                        </p>
                    </div>
                )}

                {!loading && results.map(([filePath, items]) => (
                    <div key={filePath} className="search-result-group">
                        <div className="search-result-file">
                            📄 {filePath.split('/').pop()}
                            <span style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginLeft: 'auto' }}>
                                {filePath}
                            </span>
                        </div>
                        {items.map((item, i) => (
                            <div
                                key={i}
                                className="search-result-item"
                                onClick={() => onOpenFile && onOpenFile(filePath, item.line_number)}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span>Line {item.line_number || item.metadata?.start_line || '?'}</span>
                                    <span className="search-result-score">
                                        {item.score ? `${(item.score * 100).toFixed(0)}% match` : ''}
                                    </span>
                                </div>
                                <div className="search-result-snippet">
                                    {item.content || item.text || ''}
                                </div>
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
}
