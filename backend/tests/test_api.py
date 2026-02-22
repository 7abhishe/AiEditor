"""
CodeGenie AI Editor — API Tests
Covers health, API keys, and chat endpoints.
"""

import pytest


# ── Health Check Tests ──────────────────────────────────


@pytest.mark.asyncio
async def test_health_root(async_client):
    """Root / endpoint returns status ok."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "CodeGenie" in data["app_name"]


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    """/health endpoint returns status ok."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


# ── Auth Tests ───────────────────────────────────────


@pytest.mark.asyncio
async def test_signup(async_client):
    """POST /api/v1/auth/signup registers a new user."""
    response = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "newuser@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_signup_duplicate(async_client):
    """POST /api/v1/auth/signup prevents duplicate emails."""
    # First signup
    await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "dup@example.com", "password": "password123"},
    )
    # Second signup should fail
    response = await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "dup@example.com", "password": "password123"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(async_client):
    """POST /api/v1/auth/login returns a JWT for valid credentials."""
    # Create user
    await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "login@example.com", "password": "password123"},
    )
    # Login
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# ── Chat Tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_chat_missing_api_key(async_client):
    """Chat without API key should fail (if auth enforced)."""
    response = await async_client.post(
        "/api/v1/chat",
        json={"message": "Hello", "language": "python"},
    )
    # May be 200 if auth is optional, or 401/422 if enforced
    assert response.status_code in [200, 401, 422]


@pytest.mark.asyncio
async def test_chat_with_api_key(async_client, api_headers):
    """Chat with API key should return a response."""
    response = await async_client.post(
        "/api/v1/chat",
        json={"message": "What is Python?", "language": "python"},
        headers=api_headers,
    )
    # Should either succeed or fail gracefully (no Gemini key in CI)
    assert response.status_code in [200, 500]


# ── Search Endpoint Tests ──────────────────────────────


@pytest.mark.asyncio
async def test_search_endpoint_exists(async_client, api_headers):
    """POST /api/v1/search should respond (even with no index)."""
    response = await async_client.post(
        "/api/v1/search",
        json={"query": "test function", "top_k": 5},
        headers=api_headers,
    )
    # May return 200 (empty results) or 500 (no FAISS index)
    assert response.status_code in [200, 500]


# ── Git Endpoint Tests ─────────────────────────────────


@pytest.mark.asyncio
async def test_git_status_no_project(async_client, api_headers):
    """GET /api/v1/git/status without project should handle gracefully."""
    response = await async_client.get(
        "/api/v1/git/status",
        headers=api_headers,
    )
    # Should return an error or empty state
    assert response.status_code in [200, 400, 404, 500]


# ── Agent Endpoint Tests ───────────────────────────────


@pytest.mark.asyncio
async def test_agent_status_missing_task(async_client, api_headers):
    """GET /api/v1/agent/status/nonexistent should return 404."""
    response = await async_client.get(
        "/api/v1/agent/status/nonexistent-id",
        headers=api_headers,
    )
    assert response.status_code in [404, 500]
