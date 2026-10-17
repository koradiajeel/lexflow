"""Where uploaded document files are kept.

STORAGE_BACKEND in .env decides:
- "local" (default): files in backend/uploads/<storage_key>
- "s3": files in the Amazon S3 bucket S3_BUCKET, under the same <storage_key>

The rest of the app only calls save_file / read_file / delete_file,
so it doesn't need to know which one is in use.
"""
from functools import lru_cache
from pathlib import Path

from app.core.config import settings

# Always D:\lexflow\backend\uploads, no matter where uvicorn is started from
UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads"

def using_s3()->bool:
    return settings.STORAGE_BACKEND.strip().lower()=="s3"

@lru_cache
def _s3_client():
    """One shared connection to S3, created the first time it's needed."""
    import boto3

    if not settings.S3_BUCKET:
        raise RuntimeError("STORAGE_BACKEND is 's3' but S3_BUCKET is not set in .env")
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,   
    )

def save_file(storage_key:str,content:bytes)->None:
    if using_s3():
        _s3_client().put_object(
            Bucket=settings.S3_BUCKET,
            Key=storage_key,     # ✅ capital K,
            Body=content,
            ServerSideEncryption="AES256",  # encrypted on Amazon's disks
        )
        return
    file_path=UPLOAD_ROOT / storage_key
    file_path.parent.mkdir(parents=True,exist_ok=True)
    file_path.write_bytes(content)

def read_file(storage_key:str)->bytes |None:
    """The file's bytes, or None if it isn't in storage."""
    if using_s3():
        from botocore.exceptions import ClientError

        try:
            obj = _s3_client().get_object(Bucket=settings.S3_BUCKET, Key=storage_key)
        except ClientError as err:
            if err.response.get("Error",{}).get("Code")in("NoSuchKey","404"):
                return None
            raise
        return obj["Body"].read()
    file_path = UPLOAD_ROOT / storage_key
    return file_path.read_bytes() if file_path.exists() else None

def delete_file(storage_key: str) -> None:
    if using_s3():
        _s3_client().delete_object(Bucket=settings.S3_BUCKET, Key=storage_key)
        return

    file_path = UPLOAD_ROOT / storage_key
    if file_path.exists():
        file_path.unlink()