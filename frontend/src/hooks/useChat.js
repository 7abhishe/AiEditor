/**
 * CodeGenie AI Editor — useChat Hook
 * Manages chat state: messages, conversation tracking, and API calls.
 */

import { useState, useCallback, useRef } from 'react';
import { sendMessage, getApiKey } from '../services/api.js';

export default function useChat() {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState(null);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = useCallback(() => {
        setTimeout(() => {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
    }, []);

    const send = useCallback(async (text, context = null) => {
        if (!text.trim() || isLoading) return;

        const userMessage = { role: 'user', content: text, id: Date.now() };
        setMessages(prev => [...prev, userMessage]);

        if (!getApiKey()) {
            const errorMsg = 'No API key set. Click the ⚙️ (settings) icon in the top right to configure your API key.';
            setError(errorMsg);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `⚠️ Error: ${errorMsg}`,
                id: Date.now() + 1,
                isError: true,
            }]);
            scrollToBottom();
            return;
        }

        setIsLoading(true);
        setError(null);
        scrollToBottom();

        try {
            const response = await sendMessage(text, conversationId, context);
            const assistantMessage = {
                role: 'assistant',
                content: response.response,
                model: response.model,
                id: Date.now() + 1,
            };
            setMessages(prev => [...prev, assistantMessage]);
            setConversationId(response.conversation_id);
            scrollToBottom();
        } catch (err) {
            setError(err.message);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `⚠️ Error: ${err.message}`,
                id: Date.now() + 1,
                isError: true,
            }]);
            scrollToBottom();
        } finally {
            setIsLoading(false);
        }
    }, [isLoading, conversationId, scrollToBottom]);

    const newConversation = useCallback(() => {
        setMessages([]);
        setConversationId(null);
        setError(null);
    }, []);

    const addMessage = useCallback((role, content) => {
        const msg = { role, content, id: Date.now() + Math.random() };
        setMessages(prev => [...prev, msg]);
        scrollToBottom();
    }, [scrollToBottom]);

    return {
        messages,
        isLoading,
        error,
        conversationId,
        send,
        newConversation,
        messagesEndRef,
        addMessage,
        setLoading: setIsLoading,
    };
}

