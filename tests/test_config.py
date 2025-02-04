import importlib
import os

import pytest

def test_config_with_env(monkeypatch):
    # Set the environment variable and reload the config module
    monkeypatch.setenv("DEMO_SERVICE_URL", "http://custom-service:9000")
    import d_task_manage_svc.config as config_module
    importlib.reload(config_module)
    assert config_module.DEMO_SERVICE_URL == "http://custom-service:9000"


def test_config_default(monkeypatch):
    # Ensure the environment variable is unset and reload the config module
    monkeypatch.delenv("DEMO_SERVICE_URL", raising=False)
    import d_task_manage_svc.config as config_module
    importlib.reload(config_module)
    assert config_module.DEMO_SERVICE_URL == "localhost:8001"
