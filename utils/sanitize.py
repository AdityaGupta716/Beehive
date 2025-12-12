import bleach
from typing import Optional

def sanitize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return bleach.clean(
        value,
        tags=[],          # Remove ALL HTML tags
        attributes={},    # Remove inbuilt methods, etc.
        strip=True        # Strip the tags
    ).strip()
