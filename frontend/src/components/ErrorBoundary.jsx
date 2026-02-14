/**
 * CodeGenie AI Editor — Error Boundary
 * Catches React runtime errors and shows a recovery screen.
 */

import { Component } from 'react';

export default class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        this.setState({ errorInfo });
        console.error('ErrorBoundary caught:', error, errorInfo);
    }

    handleReload = () => {
        window.location.reload();
    };

    handleDismiss = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
    };

    render() {
        if (this.state.hasError) {
            return (
                <div className="error-boundary">
                    <div className="error-boundary-content">
                        <div className="error-boundary-icon">💥</div>
                        <h2>Something went wrong</h2>
                        <p className="error-boundary-subtitle">
                            CodeGenie encountered an unexpected error. Your work has been preserved.
                        </p>
                        <div className="error-boundary-details">
                            <code>{this.state.error?.message || 'Unknown error'}</code>
                        </div>
                        <div className="error-boundary-actions">
                            <button className="btn btn-primary" onClick={this.handleReload}>
                                🔄 Reload Editor
                            </button>
                            <button className="btn btn-secondary" onClick={this.handleDismiss}>
                                Try to Continue
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
