import pytest
import httpx

from d_task_manage_svc.instruction_generator import generate_instructions


class DummyResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def raise_for_status(self):
        if self.status_code != 200:
            raise httpx.HTTPStatusError("Error", request=None, response=self)

    def json(self):
        return self._json_data


class DummyAsyncClient:
    async def post(self, url, json, timeout):
        return DummyResponse(200, {"instructions": ["Test instruction 1", "Test instruction 2"]})

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


@pytest.mark.asyncio
async def test_generate_instructions_success(monkeypatch):
    # Monkey-patch httpx.AsyncClient to use DummyAsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda *args, **kwargs: DummyAsyncClient())
    instructions = await generate_instructions("Test Task", "Task description")
    assert isinstance(instructions, list)
    assert "Test instruction 1" in instructions


class DummyAsyncClientFailure:
    async def post(self, url, json, timeout):
        raise httpx.RequestError("Simulated request error")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


@pytest.mark.asyncio
async def test_generate_instructions_failure(monkeypatch):
    # Monkey-patch httpx.AsyncClient to simulate a failure
    monkeypatch.setattr(httpx, "AsyncClient", lambda *args, **kwargs: DummyAsyncClientFailure())
    instructions = await generate_instructions("Test Task", "Task description")
    assert instructions is None
