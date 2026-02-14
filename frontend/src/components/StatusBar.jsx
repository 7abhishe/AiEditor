/**
 * CodeGenie AI Editor — Status Bar
 * Shows connection status, language, cursor position.
 */

import { useState, useEffect } from 'react';
import { healthCheck } from '../services/api.js';

export default function StatusBar({ language, cursorPosition }) {
    const [connected, setConnected] = useState(false);

    useEffect(() => {
        const check = async () => {
            try {
                await healthCheck();
                setConnected(true);
            } catch {
                setConnected(false);
            }
        };

        check();
        const interval = setInterval(check, 10000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="status-bar">
            <div className="left">
                <div className="status-item">
                    <span className={`status-dot ${connected ? 'connected' : 'disconnected'}`} />
                    <span>{connected ? 'Backend Connected' : 'Backend Offline'}</span>
                </div>
            </div>
            <div className="right">
                {language && (
                    <div className="status-item">
                        <span>{language}</span>
                    </div>
                )}
                {cursorPosition && (
                    <div className="status-item">
                        <span>Ln {cursorPosition.line}, Col {cursorPosition.column}</span>
                    </div>
                )}
                <div className="status-item">
                    <span>CodeGenie v0.1.0</span>
                </div>
            </div>
        </div>
    );
}
