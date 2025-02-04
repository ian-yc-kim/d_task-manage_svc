import os

def pytest_configure(config):
    """Configure pytest environment variables for AI agent tests."""
    os.environ.setdefault('GPT4O_API_URL', 'http://dummy-url')
    os.environ.setdefault('GPT4O_API_TOKEN', 'dummy-token')
