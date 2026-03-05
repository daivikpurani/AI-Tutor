"""
Prompt and input guards to reduce prompt injection and avoid leaking internal instructions.
- Detects high-risk injection patterns in user input
- Delimits user content so the model treats it as data, not instructions
- Normalizes input to reduce injection surface
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Phrases that often indicate prompt injection (lowercased for matching)
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|responses?)",
    r"disregard\s+(all\s+)?(previous|above|prior)\s+(instructions?|responses?)",
    r"forget\s+(all\s+)?(previous|above|prior)\s+(instructions?|responses?)",
    r"you\s+are\s+now",
    r"new\s+instructions?\s*:",
    r"system\s*:\s*",
    r"assistant\s*:\s*",
    r"\[system\]",
    r"\[instruction\]",
    r"<\|?system\|?>",
    r"<\|?user\|?>",
    r"<\|?assistant\|?>",
    r"repeat\s+(the\s+)?(above|previous)\s+(instructions?|prompt)",
    r"reveal\s+(your\s+)?(instructions?|prompt|system\s+prompt)",
    r"print\s+(your\s+)?(instructions?|prompt|system\s+prompt)",
    r"output\s+(your\s+)?(instructions?|prompt)",
    r"what\s+are\s+your\s+instructions",
    r"show\s+(me\s+)?(your\s+)?(full\s+)?(system\s+)?prompt",
    r"###\s*instruction",
    r"---\s*instruction",
]

# Compiled for reuse
_INJECTION_RE = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

# Delimiters for wrapping user content so the model treats it as data
USER_QUESTION_START = "<<<USER_QUESTION>>>"
USER_QUESTION_END = "<<<END_USER_QUESTION>>>"


def detect_injection(text: str) -> Tuple[bool, str]:
    """
    Check if text contains likely prompt-injection patterns.

    Returns:
        (True, matched_phrase) if injection detected, (False, "") otherwise.
    """
    if not text or not text.strip():
        return False, ""
    lowered = text.strip().lower()
    for regex in _INJECTION_RE:
        m = regex.search(lowered)
        if m:
            return True, m.group(0)
    return False, ""


def sanitize_user_message(text: str, max_length: int = 2000) -> str:
    """
    Normalize user message for safer inclusion in prompts:
    - Strip leading/trailing whitespace
    - Collapse excessive newlines and control characters
    - Truncate to max_length
    Does NOT strip injection phrases (use detect_injection for that).
    """
    if not text:
        return ""
    # Remove null bytes and other control chars
    cleaned = "".join(c for c in text if c == "\n" or ord(c) >= 32)
    # Collapse many newlines to at most two
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = cleaned.strip()
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length] + "..."
    return cleaned


def wrap_user_question(query: str) -> str:
    """
    Wrap the user's question in clear delimiters so the model
    treats everything inside as the user message, not as instructions.
    """
    sanitized = sanitize_user_message(query)
    return f"{USER_QUESTION_START}\n{sanitized}\n{USER_QUESTION_END}"
