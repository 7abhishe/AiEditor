# 📖 API Documentation — CodeGenie AI Editor

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** Bearer JWT token (obtained via `/auth/login`)  
**Rate Limits:** Per-IP, see [SECURITY.md](SECURITY.md) for limits  

---

## Authentication

### POST `/auth/signup`
Register a new user account.

**Rate Limit:** 5/minute

```json
// Request
{
  "email": "user@example.com",
  "password": "StrongPass123!"
}

// Response (201)
{
  "id": "uuid",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2026-03-08T12:00:00"
}
```

### POST `/auth/login`
Get a JWT access token.

**Rate Limit:** 10/minute

```
// Request (form-urlencoded)
username=user@example.com&password=StrongPass123!

// Response (200)
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### POST `/auth/refresh`
Refresh an access token. Requires valid Bearer token.

```json
// Response (200)
{
  "access_token": "eyJhbGciOi... (new token)",
  "token_type": "bearer"
}
```

---

## AI Chat

### POST `/chat`
Send a message to Gemini AI with RAG-enhanced code context.

**Rate Limit:** 30/minute

```json
// Request
{
  "message": "How does the authentication middleware work?",
  "conversation_id": "uuid (optional)",
  "context": "optional additional context"
}

// Response (200)
{
  "response": "The authentication middleware uses JWT tokens...",
  "conversation_id": "uuid",
  "model": "gemini-3-flash-preview"
}
```

---

## Code Completion

### POST `/completion`
Get inline code completion.

**Rate Limit:** 30/minute

```json
// Request
{
  "prefix": "def fibonacci(n):\n    if n <= 1:\n        return n\n    ",
  "suffix": "",
  "language": "python"
}

// Response (200)
{
  "completion": "return fibonacci(n-1) + fibonacci(n-2)",
  "model": "gemini-3-flash-preview"
}
```

---

## Code Explanation

### POST `/explain`
Explain a code block.

**Rate Limit:** 30/minute

```json
// Request
{
  "code": "async def get_current_user(token: str = Depends(oauth2_scheme)):\n    ...",
  "language": "python"
}

// Response (200)
{
  "explanation": "This function is a FastAPI dependency that extracts and validates...",
  "model": "gemini-3-flash-preview"
}
```

---

## Refactoring

### POST `/refactor`
Get refactoring suggestions with before/after diffs.

**Rate Limit:** 30/minute

```json
// Request
{
  "code": "...",
  "language": "python",
  "focus": "readability"
}

// Response (200)
{
  "suggestions": [
    {
      "title": "Extract helper function",
      "description": "Reduces complexity",
      "original_code": "...",
      "refactored_code": "..."
    }
  ],
  "summary": "2 improvements suggested",
  "model": "gemini-3-flash-preview"
}
```

---

## Bug Detection

### POST `/bugs/detect`
Analyze code for bugs, security issues, and anti-patterns.

**Rate Limit:** 30/minute

```json
// Request
{
  "code": "...",
  "language": "python",
  "file_path": "app/main.py"
}

// Response (200)
{
  "bugs": [
    {
      "line": 42,
      "severity": "error",
      "category": "security",
      "description": "SQL injection risk",
      "suggestion": "Use parameterized queries"
    }
  ],
  "summary": "1 issue found",
  "model": "gemini-3-flash-preview"
}
```

---

## Test Generation

### POST `/tests/generate`
Generate unit tests for given code.

**Rate Limit:** 30/minute

```json
// Request
{
  "code": "def add(a, b): return a + b",
  "language": "python",
  "framework": "pytest"
}

// Response (200)
{
  "test_code": "def test_add_positive(): assert add(1, 2) == 3\n...",
  "framework": "pytest",
  "test_count": 5,
  "model": "gemini-3-flash-preview"
}
```

---

## Agent Mode

### POST `/agent/run`
Start an autonomous coding agent task (returns SSE stream).

**Rate Limit:** 15/minute

```json
// Request
{
  "goal": "Add input validation to the signup endpoint",
  "project_path": "/path/to/project",
  "context": "optional context"
}

// Response (SSE stream)
event: thinking
data: {"step": "Analyzing the signup endpoint..."}

event: action
data: {"step": "Adding Pydantic validation..."}

event: complete
data: {"result": "Done", "files_modified": 2}
```

---

## Repository Indexing

### POST `/index/start`
Index a project repository for RAG search.

```json
// Request
{
  "project_path": "/path/to/project",
  "file_extensions": [".py", ".js", ".ts"]
}
```

### GET `/index/status`
Get indexing status.

---

## Search

### POST `/search`
Semantic code search across the indexed repository.

```json
// Request
{
  "query": "authentication middleware",
  "top_k": 5
}

// Response (200)
{
  "results": [
    {
      "file_path": "app/core/auth.py",
      "content": "...",
      "score": 0.89
    }
  ]
}
```

---

## Git Operations

### GET `/git/project`
Get project git status.

### POST `/git/stage`
Stage files for commit.

### POST `/git/commit`
Create a git commit.

### POST `/git/ai-message`
Generate an AI commit message.

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error description"
}
```

| Status | Meaning |
|---|---|
| 400 | Bad request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (not your resource) |
| 413 | Payload too large (>1MB) |
| 422 | Validation error (Pydantic) |
| 429 | Rate limited |
| 500 | Internal server error |
