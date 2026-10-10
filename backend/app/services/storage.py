from pathlib import Path

# Always D:\lexflow\backend\uploads, no matter where uvicorn is started from
UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads"


def save_file(storage_key: str, content: bytes) -> None:
    file_path = UPLOAD_ROOT / storage_key
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(content)


def get_file_path(storage_key: str) -> Path:
    return UPLOAD_ROOT / storage_key


def delete_file(storage_key: str) -> None:
    file_path = get_file_path(storage_key)
    if file_path.exists():
        file_path.unlink()