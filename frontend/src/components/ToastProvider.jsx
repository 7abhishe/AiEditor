/**
 * CodeGenie AI Editor — Toast Notification System
 * Stackable toasts with auto-dismiss and animations.
 */

import { createContext, useContext, useState, useCallback, useRef } from 'react';

const ToastContext = createContext(null);

let toastIdCounter = 0;

export function useToast() {
    const ctx = useContext(ToastContext);
    if (!ctx) throw new Error('useToast must be used within ToastProvider');
    return ctx;
}

export function ToastProvider({ children }) {
    const [toasts, setToasts] = useState([]);
    const timersRef = useRef({});

    const removeToast = useCallback((id) => {
        setToasts(prev => prev.filter(t => t.id !== id));
        if (timersRef.current[id]) {
            clearTimeout(timersRef.current[id]);
            delete timersRef.current[id];
        }
    }, []);

    const addToast = useCallback((message, type = 'info', duration = 4000) => {
        const id = ++toastIdCounter;
        const toast = { id, message, type, entering: true };

        setToasts(prev => [...prev, toast]);

        // Remove entering class after animation
        setTimeout(() => {
            setToasts(prev => prev.map(t => t.id === id ? { ...t, entering: false } : t));
        }, 50);

        // Auto-dismiss
        if (duration > 0) {
            timersRef.current[id] = setTimeout(() => removeToast(id), duration);
        }

        return id;
    }, [removeToast]);

    const toast = {
        info: (msg, dur) => addToast(msg, 'info', dur),
        success: (msg, dur) => addToast(msg, 'success', dur),
        error: (msg, dur) => addToast(msg, 'error', dur),
        warning: (msg, dur) => addToast(msg, 'warning', dur),
    };

    const icons = {
        info: 'ℹ️',
        success: '✅',
        error: '❌',
        warning: '⚠️',
    };

    return (
        <ToastContext.Provider value={toast}>
            {children}
            <div className="toast-container">
                {toasts.map((t) => (
                    <div
                        key={t.id}
                        className={`toast toast-${t.type} ${t.entering ? 'toast-enter' : ''}`}
                    >
                        <span className="toast-icon">{icons[t.type]}</span>
                        <span className="toast-message">{t.message}</span>
                        <button className="toast-close" onClick={() => removeToast(t.id)}>✕</button>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
}
