import bleach

def sanitize_text(value: str) -> str:
    if not value:
        return ""
    return bleach.clean(
        value,
        tags=[],          # Remove ALL HTML tags
        attributes={},    # Remove inbuilt methods, etc.
        strip=True        # Strip the tags
    ).strip()
