import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem('cg_access_token'));
    const [isAuthenticated, setIsAuthenticated] = useState(!!token);

    useEffect(() => {
        if (token) {
            localStorage.setItem('cg_access_token', token);
            setIsAuthenticated(true);
        } else {
            localStorage.removeItem('cg_access_token');
            setIsAuthenticated(false);
        }
    }, [token]);

    const login = async (email, password) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://codegenie-backend-27y2.onrender.com'}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData.toString()
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `Login failed (${response.status})`);
        }

        const data = await response.json();
        setToken(data.access_token);
    };

    const signup = async (email, password) => {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://codegenie-backend-27y2.onrender.com'}/api/v1/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `Signup failed (${response.status})`);
        }

        // Auto-login after successful signup
        await login(email, password);
    };

    const logout = () => {
        setToken(null);
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, token, login, signup, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
