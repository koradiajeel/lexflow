from pathlib import Path
UPLOAD_ROOT=Path("upload")

def save_file(storage_key:str,content:bytes)->None:
    Path=UPLOAD_ROOT / storage_key
    Path.parent.mkdir(parents=True,exist_ok=True)
    Path.write_bytes(content)

def get_file_path(Storage_key:str)->Path:
    return UPLOAD_ROOT / Storage_key

def get_file_path(storage_key:str)->Path:
    return UPLOAD_ROOT/storage_key

def delete_file(storage_key: str) -> None:
    path = get_file_path(storage_key)
    if path.exists():
        path.unlink()