import os
import pytest
import httpx
import logging

from src.d_task_manage_svc.ai_agent import generate_ai_instructions


class DummyResponse:
    """A dummy response class to mimic httpx response objects."""
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError('Error', request=None, response=self)


class FakeAsyncClient:
    """A fake async client to simulate httpx.AsyncClient behavior."""
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def post(self, url, json, headers=None):
        return self.response


def fake_async_client_factory(response):
    """Factory to create a fake async client returning the given response."""
    def fake_async_client(*args, **kwargs):
        return FakeAsyncClient(response)
    return fake_async_client


@pytest.mark.asyncio
async def test_generate_ai_instructions_success(monkeypatch):
    """Test generating AI instructions with a valid response containing 3 instructions."""
    monkeypatch.setenv('GPT4O_API_URL', 'http://dummy-url')
    monkeypatch.setenv('GPT4O_API_TOKEN', 'dummy-token')
    # Prepare a valid dummy response with 3 instructions
    instructions = ["Instruction one.", "Instruction two.", "Instruction three."]
    dummy_response = DummyResponse(200, instructions)
    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client_factory(dummy_response))

    result = await generate_ai_instructions("Test Task", "Test Description")
    assert isinstance(result, list)
    assert len(result) == 3
    for instr in result:
        assert isinstance(instr, str) and instr.strip() != ""


@pytest.mark.asyncio
async def test_generate_ai_instructions_invalid_response(monkeypatch):
    """Test generating AI instructions when the API returns an invalid response format."""
    monkeypatch.setenv('GPT4O_API_URL', 'http://dummy-url')
    monkeypatch.setenv('GPT4O_API_TOKEN', 'dummy-token')
    # Dummy response with an invalid payload (not a list)
    dummy_response = DummyResponse(200, {"error": "Not a list"})
    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client_factory(dummy_response))

    result = await generate_ai_instructions("Test Task", "Test Description")
    assert result == []


@pytest.mark.asyncio
async def test_generate_ai_instructions_insufficient_instructions(monkeypatch):
    """Test generating AI instructions when less than 3 instructions are returned."""
    monkeypatch.setenv('GPT4O_API_URL', 'http://dummy-url')
    monkeypatch.setenv('GPT4O_API_TOKEN', 'dummy-token')
    # Dummy response with less than 3 instructions
    instructions = ["Only one instruction."]
    dummy_response = DummyResponse(200, instructions)
    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client_factory(dummy_response))

    result = await generate_ai_instructions("Test Task", "Test Description")
    assert result == []


@pytest.mark.asyncio
async def test_generate_ai_instructions_api_error(monkeypatch, caplog):
    """Test generating AI instructions when an API error occurs, ensuring error logging."""
    monkeypatch.setenv('GPT4O_API_URL', 'http://dummy-url')
    monkeypatch.setenv('GPT4O_API_TOKEN', 'dummy-token')

    # Simulate an exception during the API call
    async def fake_post(*args, **kwargs):
        raise httpx.HTTPError("API failure")

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, url, json, headers=None):
            return await fake_post()

    monkeypatch.setattr(httpx, "AsyncClient", lambda *args, **kwargs: FakeClient())

    with caplog.at_level(logging.ERROR):
        result = await generate_ai_instructions("Test Task", "Test Description")
        assert result == []
        assert "API failure" in caplog.text


@pytest.mark.asyncio
async def test_generate_ai_instructions_too_many_instructions(monkeypatch):
    """Test generating AI instructions when more than 10 instructions are returned by the API."""
    monkeypatch.setenv('GPT4O_API_URL', 'http://dummy-url')
    monkeypatch.setenv('GPT4O_API_TOKEN', 'dummy-token')
    # Create a list of 11 instructions
    instructions = [f"Instruction {i}." for i in range(1, 12)]
    dummy_response = DummyResponse(200, instructions)
    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client_factory(dummy_response))

    result = await generate_ai_instructions("Test Task", "Test Description")
    # Since number of instructions is >10, expecting an empty list
    assert result == []


@pytest.mark.asyncio
async def test_generate_ai_instructions_empty_input(monkeypatch):
    """Test generating AI instructions with empty string input for task title and description."""
    monkeypatch.setenv('GPT4O_API_URL', 'http://dummy-url')
    monkeypatch.setenv('GPT4O_API_TOKEN', 'dummy-token')

    # Even if the API would return valid instructions, empty input should preempt the call
    result = await generate_ai_instructions("", "Test Description")
    assert result == []

    result = await generate_ai_instructions("Test Task", "")
    assert result == []


@pytest.mark.asyncio
async def test_generate_ai_instructions_whitespace_input(monkeypatch):
    """Test generating AI instructions with whitespace-only input for task title and description."""
    monkeypatch.setenv('GPT4O_API_URL', 'http://dummy-url')
    monkeypatch.setenv('GPT4O_API_TOKEN', 'dummy-token')

    result = await generate_ai_instructions("   ", "Test Description")
    assert result == []

    result = await generate_ai_instructions("Test Task", "   ")
    assert result == []
