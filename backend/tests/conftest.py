"""Settings for every test: never use real cloud services, whatever .env says."""
import pytest

from app.core.config import settings


@pytest.fixture(autouse=True)
def safe_test_settings(monkeypatch):
    # Files go to local disk, not the real S3 bucket.
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "local")
    # No SMTP login = real emails can't be sent by accident.
    monkeypatch.setattr(settings, "SMTP_USER", "")
    monkeypatch.setattr(settings, "SMTP_PASSWORD", "")
