import asyncio
import json

import httpx
import pytest

from fastapi import APIRouter
from d_task_manage_svc.app import app

# Add a dummy route for testing purposes
router = APIRouter()

@router.get("/test-middleware")
async def test_middleware():
    return {"message": "success"}

app.include_router(router)


# Create a fake async client to mock httpx.AsyncClient
class FakeAsyncClient:
    def __init__(self, status_code):
        self.status_code = status_code

    async def get(self, url, headers):
        class FakeResponse:
            def __init__(self, status_code):
                self.status_code = status_code
        return FakeResponse(self.status_code)

    async def post(self, url, json):
        class FakeResponse:
            def __init__(self, status_code):
                self.status_code = status_code
        return FakeResponse(self.status_code)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


@pytest.fixture(autouse=True)
def override_async_client(monkeypatch):
    # This fixture can be overridden in tests if needed
    pass


@pytest.mark.asyncio
async def test_no_session_token(client):
    # No session_token header provided, should return 401
    response = client.get("/test-middleware")
    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "Session token is missing"


@pytest.mark.asyncio
async def test_invalid_session_token(monkeypatch, client):
    # Override AsyncClient to simulate an invalid token response using GET request
    def fake_async_client_invalid(*args, **kwargs):
        return FakeAsyncClient(status_code=401)
    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client_invalid)

    response = client.get("/test-middleware", headers={"session_token": "invalid_token"})
    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "Invalid or expired session token"


@pytest.mark.asyncio
async def test_valid_session_token(monkeypatch, client):
    # Override AsyncClient to simulate a valid token response using GET request
    def fake_async_client_valid(*args, **kwargs):
        return FakeAsyncClient(status_code=200)
    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client_valid)

    response = client.get("/test-middleware", headers={"session_token": "valid_token"})
    # Expect the request to pass through middleware and return success from the route
    assert response.status_code == 200
    data = response.json()
    assert data.get("message") == "success"
