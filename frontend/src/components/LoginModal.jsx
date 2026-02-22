import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useAuth } from '../store/AuthContext';
import { useToast } from './ToastProvider';
import './LoginModal.css';

/* ── Floating Particle Background ────────────────────── */
function FloatingParticles() {
    const particles = useMemo(() =>
        Array.from({ length: 30 }, (_, i) => ({
            id: i,
            size: Math.random() * 4 + 2,
            x: Math.random() * 100,
            y: Math.random() * 100,
            duration: Math.random() * 20 + 15,
            delay: Math.random() * -20,
            opacity: Math.random() * 0.4 + 0.1,
        })), []
    );

    return (
        <div className="auth-particles">
            {particles.map(p => (
                <div
                    key={p.id}
                    className="auth-particle"
                    style={{
                        width: p.size,
                        height: p.size,
                        left: `${p.x}%`,
                        top: `${p.y}%`,
                        animationDuration: `${p.duration}s`,
                        animationDelay: `${p.delay}s`,
                        opacity: p.opacity,
                    }}
                />
            ))}
        </div>
    );
}

/* ── Password Strength Bar ───────────────────────────── */
function PasswordStrength({ password }) {
    const getStrength = (pw) => {
        if (!pw) return { level: 0, label: '', color: '' };
        let score = 0;
        if (pw.length >= 6) score++;
        if (pw.length >= 10) score++;
        if (/[A-Z]/.test(pw)) score++;
        if (/[0-9]/.test(pw)) score++;
        if (/[^A-Za-z0-9]/.test(pw)) score++;

        if (score <= 1) return { level: 1, label: 'Weak', color: '#ef4444' };
        if (score <= 2) return { level: 2, label: 'Fair', color: '#f59e0b' };
        if (score <= 3) return { level: 3, label: 'Good', color: '#10b981' };
        return { level: 4, label: 'Strong', color: '#06d6a0' };
    };

    const strength = getStrength(password);
    if (!password) return null;

    return (
        <div className="password-strength">
            <div className="strength-bars">
                {[1, 2, 3, 4].map(i => (
                    <div
                        key={i}
                        className={`strength-bar ${i <= strength.level ? 'active' : ''}`}
                        style={{ backgroundColor: i <= strength.level ? strength.color : undefined }}
                    />
                ))}
            </div>
            <span className="strength-label" style={{ color: strength.color }}>
                {strength.label}
            </span>
        </div>
    );
}

/* ── Animated Input Field ────────────────────────────── */
function AnimatedInput({ label, icon, type, value, onChange, placeholder, disabled, required, minLength, autoFocus }) {
    const [focused, setFocused] = useState(false);
    const hasValue = value && value.length > 0;

    return (
        <div className={`animated-input-group ${focused ? 'focused' : ''} ${hasValue ? 'has-value' : ''}`}>
            <div className="input-icon">{icon}</div>
            <input
                type={type}
                value={value}
                onChange={onChange}
                disabled={disabled}
                required={required}
                minLength={minLength}
                autoFocus={autoFocus}
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                placeholder={focused ? placeholder : ''}
            />
            <label className="floating-label">{label}</label>
            <div className="input-highlight" />
        </div>
    );
}

/* ── Main Login Modal ────────────────────────────────── */
export default function LoginModal() {
    const { login, signup } = useAuth();
    const toast = useToast();

    const [isLoginView, setIsLoginView] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [isTransitioning, setIsTransitioning] = useState(false);
    const formRef = useRef(null);

    const toggleView = () => {
        setIsTransitioning(true);
        setTimeout(() => {
            setIsLoginView(prev => !prev);
            setEmail('');
            setPassword('');
            setConfirmPassword('');
            setTimeout(() => setIsTransitioning(false), 50);
        }, 250);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!email || !password) {
            toast.warning('Please fill in all fields');
            return;
        }

        if (!isLoginView && password !== confirmPassword) {
            toast.error('Passwords do not match');
            return;
        }

        if (!isLoginView && password.length < 6) {
            toast.warning('Password must be at least 6 characters');
            return;
        }

        setIsLoading(true);
        try {
            if (isLoginView) {
                await login(email, password);
                toast.success('Welcome back! 🚀');
            } else {
                await signup(email, password);
                toast.success('Account created! Welcome aboard! 🎉');
            }
        } catch (err) {
            toast.error(err.message || 'Authentication failed');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="auth-overlay">
            <FloatingParticles />

            {/* Animated gradient orbs */}
            <div className="auth-orb auth-orb-1" />
            <div className="auth-orb auth-orb-2" />
            <div className="auth-orb auth-orb-3" />

            <div className={`auth-card ${isTransitioning ? 'transitioning' : ''}`}>
                {/* Glowing border effect */}
                <div className="auth-card-glow" />

                {/* Logo & Branding */}
                <div className="auth-brand">
                    <div className="auth-logo">
                        <div className="auth-logo-icon">
                            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                                <path d="M16 2L3 9v14l13 7 13-7V9L16 2z" fill="url(#logoGrad)" opacity="0.15" />
                                <path d="M16 2L3 9v14l13 7 13-7V9L16 2z" stroke="url(#logoGrad)" strokeWidth="1.5" fill="none" />
                                <path d="M10 16l4 4 8-8" stroke="url(#logoGrad)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                <defs>
                                    <linearGradient id="logoGrad" x1="0" y1="0" x2="32" y2="32">
                                        <stop stopColor="#818cf8" />
                                        <stop offset="1" stopColor="#06b6d4" />
                                    </linearGradient>
                                </defs>
                            </svg>
                        </div>
                        <h1 className="auth-title">CodeGenie</h1>
                    </div>
                    <p className="auth-subtitle">
                        {isLoginView
                            ? 'Welcome back! Sign in to continue.'
                            : 'Join CodeGenie and start building.'}
                    </p>
                </div>

                {/* Form */}
                <form ref={formRef} onSubmit={handleSubmit} className="auth-form">
                    <AnimatedInput
                        label="Email Address"
                        icon="✉️"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="you@example.com"
                        disabled={isLoading}
                        required
                        autoFocus
                    />

                    <div className="password-field-wrapper">
                        <AnimatedInput
                            label="Password"
                            icon="🔒"
                            type={showPassword ? 'text' : 'password'}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter your password"
                            disabled={isLoading}
                            required
                            minLength={6}
                        />
                        <button
                            type="button"
                            className="password-toggle"
                            onClick={() => setShowPassword(!showPassword)}
                            tabIndex={-1}
                        >
                            {showPassword ? '🙈' : '👁️'}
                        </button>
                    </div>

                    {!isLoginView && (
                        <>
                            <PasswordStrength password={password} />
                            <AnimatedInput
                                label="Confirm Password"
                                icon="🔐"
                                type={showPassword ? 'text' : 'password'}
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                placeholder="Confirm your password"
                                disabled={isLoading}
                                required
                                minLength={6}
                            />
                        </>
                    )}

                    <button
                        type="submit"
                        className={`auth-submit-btn ${isLoading ? 'loading' : ''}`}
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <div className="btn-loader">
                                <div className="spinner" />
                                <span>Please wait...</span>
                            </div>
                        ) : (
                            <span className="btn-content">
                                <span>{isLoginView ? 'Sign In' : 'Create Account'}</span>
                                <span className="btn-arrow">→</span>
                            </span>
                        )}
                    </button>
                </form>

                {/* Divider */}
                <div className="auth-divider">
                    <span>or</span>
                </div>

                {/* Toggle View */}
                <div className="auth-toggle">
                    <p>
                        {isLoginView ? "Don't have an account?" : 'Already have an account?'}
                    </p>
                    <button
                        type="button"
                        className="auth-toggle-btn"
                        onClick={toggleView}
                        disabled={isLoading}
                    >
                        {isLoginView ? 'Create Account' : 'Sign In Instead'}
                    </button>
                </div>

                {/* Footer */}
                <div className="auth-footer">
                    <p>By continuing, you agree to CodeGenie's Terms of Service.</p>
                </div>
            </div>
        </div>
    );
}
