/**
 * CodeGenie AI Editor — API Service
 * HTTP client for communicating with the FastAPI backend.
 */

const BASE_URL = 'http://localhost:8000';
let API_KEY = localStorage.getItem('codegenie_api_key') || '';

export function setApiKey(key) {
    API_KEY = key;
    localStorage.setItem('codegenie_api_key', key);
}

export function getApiKey() {
    return API_KEY;
}

async function request(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (API_KEY) {
        headers['X-API-Key'] = API_KEY;
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

// ── Chat ────────────────────────────────────────────────

export async function sendMessage(message, conversationId = null, context = null) {
    return request('/api/v1/chat', {
        method: 'POST',
        body: JSON.stringify({
            message,
            conversation_id: conversationId,
            context,
        }),
    });
}

// ── Code Completion ─────────────────────────────────────

export async function getCompletion(prefix, suffix = '', language = '') {
    return request('/api/v1/completion', {
        method: 'POST',
        body: JSON.stringify({ prefix, suffix, language }),
    });
}

// ── Code Explanation ────────────────────────────────────

export async function explainCode(code, language = '') {
    return request('/api/v1/explain', {
        method: 'POST',
        body: JSON.stringify({ code, language }),
    });
}

// ── API Key Management ──────────────────────────────────

export async function createApiKey(label = 'default') {
    const result = await request('/api/v1/auth/keys', {
        method: 'POST',
        body: JSON.stringify({ label }),
    });
    setApiKey(result.api_key);
    return result;
}

// ── Repository Indexing ─────────────────────────────────

export async function indexProject(projectPath) {
    return request('/api/v1/index/start', {
        method: 'POST',
        body: JSON.stringify({ project_path: projectPath }),
    });
}

export async function indexStatus() {
    return request('/api/v1/index/status');
}

export async function searchCode(query, topK = 5) {
    return request('/api/v1/index/search', {
        method: 'POST',
        body: JSON.stringify({ query, top_k: topK }),
    });
}

// ── Bug Detection ───────────────────────────────────────

export async function detectBugs(code, language = '') {
    return request('/api/v1/bugs/detect', {
        method: 'POST',
        body: JSON.stringify({ code, language }),
    });
}

// ── Refactoring ─────────────────────────────────────────

export async function refactorCode(code, language = '', focus = '') {
    return request('/api/v1/refactor', {
        method: 'POST',
        body: JSON.stringify({ code, language, focus }),
    });
}

// ── Test Generation ─────────────────────────────────────

export async function generateTests(code, language = '', framework = '') {
    return request('/api/v1/tests/generate', {
        method: 'POST',
        body: JSON.stringify({ code, language, framework }),
    });
}

// ── Git Integration ─────────────────────────────────────

export async function gitSetProject(projectPath) {
    return request('/api/v1/git/project', {
        method: 'POST',
        body: JSON.stringify({ project_path: projectPath }),
    });
}

export async function gitStatus(projectPath = null) {
    const params = projectPath ? `?project_path=${encodeURIComponent(projectPath)}` : '';
    return request(`/api/v1/git/status${params}`);
}

export async function gitDiff(filePath = null, staged = false, projectPath = null) {
    const params = new URLSearchParams();
    if (filePath) params.set('file_path', filePath);
    if (staged) params.set('staged', 'true');
    if (projectPath) params.set('project_path', projectPath);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return request(`/api/v1/git/diff${qs}`);
}

export async function gitLog(count = 20, projectPath = null) {
    const params = new URLSearchParams({ count: count.toString() });
    if (projectPath) params.set('project_path', projectPath);
    return request(`/api/v1/git/log?${params.toString()}`);
}

export async function gitBranches(projectPath = null) {
    const params = projectPath ? `?project_path=${encodeURIComponent(projectPath)}` : '';
    return request(`/api/v1/git/branches${params}`);
}

export async function gitCommit(message = null, projectPath = null) {
    const params = projectPath ? `?project_path=${encodeURIComponent(projectPath)}` : '';
    return request(`/api/v1/git/commit${params}`, {
        method: 'POST',
        body: JSON.stringify({ message }),
    });
}

export async function gitCheckout(branch, projectPath = null) {
    const params = projectPath ? `?project_path=${encodeURIComponent(projectPath)}` : '';
    return request(`/api/v1/git/checkout${params}`, {
        method: 'POST',
        body: JSON.stringify({ branch }),
    });
}

export async function gitAiMessage(projectPath = null) {
    const params = projectPath ? `?project_path=${encodeURIComponent(projectPath)}` : '';
    return request(`/api/v1/git/ai-message${params}`, { method: 'POST' });
}

export async function gitStageFile(filePath, action = 'stage', projectPath = null) {
    const params = projectPath ? `?project_path=${encodeURIComponent(projectPath)}` : '';
    return request(`/api/v1/git/stage${params}`, {
        method: 'POST',
        body: JSON.stringify({ file_path: filePath, action }),
    });
}

// ── Semantic Search ─────────────────────────────────────

export async function semanticSearch(query, topK = 10, projectPath = null) {
    return request('/api/v1/search', {
        method: 'POST',
        body: JSON.stringify({ query, top_k: topK, project_path: projectPath }),
    });
}

// ── Agent Mode ──────────────────────────────────────────

export async function runAgentSync(goal, projectPath, context = null) {
    return request('/api/v1/agent/run-sync', {
        method: 'POST',
        body: JSON.stringify({ goal, project_path: projectPath, context }),
    });
}

export function runAgentStream(goal, projectPath, context = null) {
    // Returns an EventSource-like interface for SSE
    const headers = { 'Content-Type': 'application/json' };
    if (API_KEY) headers['X-API-Key'] = API_KEY;

    return fetch(`${BASE_URL}/api/v1/agent/run`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ goal, project_path: projectPath, context }),
    });
}

export async function getAgentStatus(taskId) {
    return request(`/api/v1/agent/status/${taskId}`);
}

// ── Multi-file Refactoring ──────────────────────────────

export async function multiRefactor(instruction, files = [], projectPath = null, language = '') {
    return request('/api/v1/refactor/multi', {
        method: 'POST',
        body: JSON.stringify({ instruction, files, project_path: projectPath, language }),
    });
}

// ── Health Check ────────────────────────────────────────

export async function healthCheck() {
    return request('/');
}
