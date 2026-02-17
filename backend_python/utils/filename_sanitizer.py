"""
Filename sanitization for secure file uploads.
Strips path components, removes control characters, and validates extensions.
"""

import os
import re
from typing import List


# Unsafe characters for filenames (Windows + Unix)
UNSAFE_FILENAME_CHARS = re.compile(r'[<>:"|?*\x00-\x1f]')
MAX_FILENAME_LENGTH = 255


def sanitize_filename(filename: str, allowed_extensions: List[str], require_extension: bool = True) -> str:
    """
    Sanitize a filename for safe storage and use.

    - Strips path components (e.g. ../, ./)
    - Removes control characters and null bytes
    - Replaces unsafe chars (<>:"|?*)
    - Limits length to 255 characters
    - Validates extension against allowed_extensions (case-insensitive)
    - If require_extension and extension invalid/empty, raises ValueError

    Args:
        filename: Raw filename from client
        allowed_extensions: List of allowed extensions e.g. [".txt", ".pdf"]
        require_extension: If True, raise when extension not in allowed list

    Returns:
        Sanitized filename

    Raises:
        ValueError: If filename is empty after sanitization or extension invalid when required
    """
    if not filename or not isinstance(filename, str):
        raise ValueError("Filename cannot be empty")

    # Strip path components
    name = os.path.basename(filename.strip())

    # Remove control characters and null bytes
    name = "".join(c for c in name if ord(c) >= 32 and ord(c) != 127)

    # Replace unsafe characters with underscore
    name = UNSAFE_FILENAME_CHARS.sub("_", name)

    # Collapse multiple underscores and strip leading/trailing
    name = re.sub(r"_+", "_", name).strip("_.")

    # Limit length (keep extension)
    if len(name) > MAX_FILENAME_LENGTH:
        base, ext = os.path.splitext(name)
        max_base = MAX_FILENAME_LENGTH - len(ext)
        if max_base < 1:
            ext = ""
            max_base = MAX_FILENAME_LENGTH
        name = base[:max_base] + ext

    if not name:
        raise ValueError("Filename is empty after sanitization")

    # Normalize extension for validation
    ext = os.path.splitext(name)[1].lower()
    allowed_lower = [e.lower() if e.startswith(".") else f".{e.lower()}" for e in allowed_extensions]

    if require_extension:
        if not ext or ext not in allowed_lower:
            # If no extension, append .txt if allowed
            if ".txt" in allowed_lower and not ext:
                name = name.rstrip(".") + ".txt"
            else:
                raise ValueError(f"File type not allowed. Allowed: {', '.join(allowed_lower)}")

    return name
