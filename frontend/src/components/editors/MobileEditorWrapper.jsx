/**
 * CodeGenie — Mobile Editor Wrapper  (CodeMirror 6)
 * Touch-friendly editor used on iOS/Android via Capacitor.
 * Supports the same languages as the Monaco editor.
 */

import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { java } from '@codemirror/lang-java';
import { html } from '@codemirror/lang-html';
import { css } from '@codemirror/lang-css';
import { json } from '@codemirror/lang-json';
import { markdown } from '@codemirror/lang-markdown';
import { useRef, useCallback } from 'react';

// Map Monaco language IDs → CodeMirror extensions
const LANG_EXTENSIONS = {
    javascript: javascript,
    typescript: () => javascript({ typescript: true }),
    python: python,
    java: java,
    html: html,
    css: css,
    scss: css,
    less: css,
    json: json,
    markdown: markdown,
};

export default function MobileEditorWrapper({
    language,
    value,
    onChange,
    onMount,
}) {
    const viewRef = useRef(null);

    const handleCreateEditor = useCallback((view) => {
        viewRef.current = view;
        // Provide a Monaco-compatible API subset for onMount
        if (onMount) {
            const editorLike = {
                getValue: () => view.state.doc.toString(),
                getModel: () => ({
                    getValueInRange: (range) => {
                        const from = range?.startColumn != null
                            ? view.state.doc.line(range.startLineNumber).from + range.startColumn - 1
                            : 0;
                        const to = range?.endColumn != null
                            ? view.state.doc.line(range.endLineNumber).from + range.endColumn - 1
                            : view.state.doc.length;
                        return view.state.sliceDoc(from, to);
                    },
                }),
                getSelection: () => {
                    const { from, to } = view.state.selection.main;
                    const fromLine = view.state.doc.lineAt(from);
                    const toLine = view.state.doc.lineAt(to);
                    return {
                        startLineNumber: fromLine.number,
                        startColumn: from - fromLine.from + 1,
                        endLineNumber: toLine.number,
                        endColumn: to - toLine.from + 1,
                    };
                },
                focus: () => view.focus(),
                onDidChangeCursorPosition: (cb) => {
                    // Simplified cursor tracking
                },
                addCommand: () => { },
                addAction: () => { },
            };
            onMount(editorLike, null);
        }
    }, [onMount]);

    // Build extensions array
    const extensions = [];
    const langFactory = LANG_EXTENSIONS[language];
    if (langFactory) {
        extensions.push(langFactory());
    } else {
        // Default to javascript for unknown languages
        extensions.push(javascript());
    }

    return (
        <CodeMirror
            value={value || ''}
            height="100%"
            theme="dark"
            extensions={extensions}
            onChange={(val) => onChange?.(val)}
            onCreateEditor={handleCreateEditor}
            basicSetup={{
                lineNumbers: true,
                highlightActiveLineGutter: true,
                highlightActiveLine: true,
                foldGutter: true,
                bracketMatching: true,
                autocompletion: true,
                closeBrackets: true,
                indentOnInput: true,
                tabSize: 2,
            }}
            style={{
                fontSize: '16px',
                fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                height: '100%',
            }}
        />
    );
}
