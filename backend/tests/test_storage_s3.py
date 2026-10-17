"""Tests for S3 storage using a fake in-memory bucket.

No AWS account, internet or money needed. Each test switches STORAGE_BACKEND to "s3"
only while it runs; all other tests keep using local storage.
"""
import pytest
from botocore.exceptions import ClientError

from app.core.config import settings
from app.services import storage


class FakeBody:
    """Like the 'Body' boto3 returns: something with a .read() method."""

    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data


class FakeS3:
    """Just enough of boto3's S3 client for storage.py, keeping files in a dict."""

    def __init__(self):
        self.objects = {}  # (bucket, key) -> bytes
        self.last_put = {}  # the arguments of the last upload, to check them

    def put_object(self, Bucket, Key, Body, **kwargs):
        self.objects[(Bucket, Key)] = Body
        self.last_put = kwargs

    def get_object(self, Bucket, Key):
        if (Bucket, Key) not in self.objects:
            raise ClientError({"Error": {"Code": "NoSuchKey"}}, "GetObject")
        return {"Body": FakeBody(self.objects[(Bucket, Key)])}

    def delete_object(self, Bucket, Key):
        self.objects.pop((Bucket, Key), None)


@pytest.fixture
def fake_s3(monkeypatch):
    """Turn on S3 mode with the fake client, for one test only."""
    fake = FakeS3()
    monkeypatch.setattr(settings, "STORAGE_BACKEND", "s3")
    monkeypatch.setattr(settings, "S3_BUCKET", "test-bucket")
    monkeypatch.setattr(storage, "_s3_client", lambda: fake)
    return fake


def test_save_read_delete_in_s3(fake_s3):
    storage.save_file("cases/abc/file1", b"hello")
    assert fake_s3.objects[("test-bucket", "cases/abc/file1")] == b"hello"
    assert fake_s3.last_put["ServerSideEncryption"] == "AES256"

    assert storage.read_file("cases/abc/file1") == b"hello"

    storage.delete_file("cases/abc/file1")
    assert storage.read_file("cases/abc/file1") is None


def test_missing_file_in_s3_is_none(fake_s3):
    assert storage.read_file("cases/nope/missing") is None


def test_other_s3_errors_are_not_hidden(fake_s3, monkeypatch):
    def access_denied(Bucket, Key):
        raise ClientError({"Error": {"Code": "AccessDenied"}}, "GetObject")

    monkeypatch.setattr(fake_s3, "get_object", access_denied)
    with pytest.raises(ClientError):
        storage.read_file("cases/abc/file1")


def test_local_is_the_default():
    assert storage.using_s3() is False