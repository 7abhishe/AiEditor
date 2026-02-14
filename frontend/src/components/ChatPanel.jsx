/**
 * CodeGenie AI Editor — Chat Panel
 * AI chat sidebar with markdown rendering and conversation management.
 */

import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

export default function ChatPanel({ chat, onToggle, style }) {
    const [input, setInput] = useState('');
    const textareaRef = useRef(null);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = '20px';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [input]);

    const handleSubmit = () => {
        if (!input.trim() || chat.isLoading) return;
        chat.send(input.trim());
        setInput('');
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className="chat-panel" style={style}>
            {/* Header */}
            <div className="chat-header">
                <h2>
                    ✨ CodeGenie AI
                    <span className="badge">Gemini</span>
                </h2>
                <div style={{ display: 'flex', gap: '4px' }}>
                    <button className="icon-btn" onClick={chat.newConversation} title="New Conversation">
                        🗒️
                    </button>
                    <button className="icon-btn" onClick={onToggle} title="Close Chat">
                        ✕
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="chat-messages">
                {chat.messages.length === 0 && (
                    <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-tertiary)' }}>
                        <div style={{ fontSize: '32px', marginBottom: '12px' }}>✨</div>
                        <p style={{ fontSize: '14px', marginBottom: '8px' }}>Ask CodeGenie anything</p>
                        <p style={{ fontSize: '12px' }}>Code questions, debugging, refactoring, and more</p>
                    </div>
                )}

                {chat.messages.map((msg) => (
                    <div key={msg.id} className={`chat-message ${msg.role}`}>
                        <span className="role">{msg.role === 'user' ? 'You' : 'CodeGenie'}</span>
                        <div className="content">
                            {msg.role === 'assistant' ? (
                                <ReactMarkdown
                                    components={{
                                        code({ node, inline, className, children, ...props }) {
                                            const match = /language-(\w+)/.exec(className || '');
                                            return !inline && match ? (
                                                <SyntaxHighlighter
                                                    style={oneDark}
                                                    language={match[1]}
                                                    PreTag="div"
                                                    customStyle={{
                                                        background: '#0d1117',
                                                        border: '1px solid #30363d',
                                                        borderRadius: '8px',
                                                        fontSize: '12px',
                                                    }}
                                                    {...props}
                                                >
                                                    {String(children).replace(/\n$/, '')}
                                                </SyntaxHighlighter>
                                            ) : (
                                                <code className={className} {...props}>{children}</code>
                                            );
                                        },
                                    }}
                                >
                                    {msg.content}
                                </ReactMarkdown>
                            ) : (
                                msg.content
                            )}
                        </div>
                    </div>
                ))}

                {/* Typing indicator */}
                {chat.isLoading && (
                    <div className="chat-typing">
                        <div className="dots">
                            <div className="dot" />
                            <div className="dot" />
                            <div className="dot" />
                        </div>
                        <span>CodeGenie is thinking...</span>
                    </div>
                )}

                <div ref={chat.messagesEndRef} />
            </div>

            {/* Input */}
            <div className="chat-input-area">
                <div className="chat-input-wrapper">
                    <textarea
                        ref={textareaRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask CodeGenie..."
                        rows={1}
                    />
                    <button
                        className="chat-send-btn"
                        onClick={handleSubmit}
                        disabled={!input.trim() || chat.isLoading}
                    >
                        ▶
                    </button>
                </div>
            </div>
        </div>
    );
}
