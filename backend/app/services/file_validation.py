import io
import zipfile

# The first bytes every real file of that type starts with
SIGNATURES = {
    "application/pdf": [b"%PDF-"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/jpeg": [b"\xff\xd8\xff"],
    "application/msword": [b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"],  # old .doc
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [b"PK\x03\x04"],  # .docx is a zip
}

DOCX_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def content_matches_type(content: bytes, content_type: str) -> bool:
    """True if the file's real bytes match the type the browser claimed."""
    signatures = SIGNATURES.get(content_type)
    if not signatures:
        return False

    if not any(content.startswith(sig) for sig in signatures):
        return False

    # A .docx is a zip file, but so is any .zip. Make sure it's really a Word file.
    if content_type == DOCX_TYPE:
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                return "word/document.xml" in zf.namelist()
        except zipfile.BadZipFile:
            return False

    return True