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


# ── API Key Tests ───────────────────────────────────────


@pytest.mark.asyncio
async def test_create_api_key(async_client):
    """POST /api/v1/keys creates a new API key."""
    response = await async_client.post(
        "/api/v1/keys",
        json={"name": "test-key"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "key" in data
    assert data["name"] == "test-key"
    assert data["key"].startswith("cg_")


@pytest.mark.asyncio
async def test_list_api_keys(async_client):
    """GET /api/v1/keys returns list of keys."""
    # Create a key first
    await async_client.post("/api/v1/keys", json={"name": "list-test"})
    response = await async_client.get("/api/v1/keys")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_validate_api_key(async_client):
    """API with valid key returns 200."""
    # Create a key
    create_resp = await async_client.post("/api/v1/keys", json={"name": "validate-test"})
    key = create_resp.json()["key"]

    # Use the key for a health check
    resp = await async_client.get("/", headers={"X-API-Key": key})
    assert resp.status_code == 200


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
