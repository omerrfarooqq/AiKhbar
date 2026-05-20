"""Shared pytest fixtures."""
import os

# Ensure tests never accidentally hit production services.
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SCHEDULER_ENABLED", "false")

import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"
