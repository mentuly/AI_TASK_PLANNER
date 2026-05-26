import pytest
from fastapi.testclient import TestClient

from site_F.main import app


@pytest.fixture
def client():
    return TestClient(app)
