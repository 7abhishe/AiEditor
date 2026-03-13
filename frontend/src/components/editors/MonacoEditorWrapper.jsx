/**
 * CodeGenie — Monaco Editor Wrapper
 * Used on Desktop and Web. Wraps @monaco-editor/react with CodeGenie's options.
 */

import Editor from '@monaco-editor/react';

export default function MonacoEditorWrapper({
    language,
    value,
    theme,
    onChange,
    onMount,
    options,
}) {
    return (
        <Editor
            height="100%"
            language={language}
            value={value}
            theme={theme || 'vs-dark'}
            onChange={onChange}
            onMount={onMount}
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
                ...options,
            }}
        />
    );
}
