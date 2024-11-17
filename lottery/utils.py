def truncate(text: str, *, max: int) -> str:
    if len(text) <= max:
        return text
    truncated: str = text[: max - 3]
    return truncated + "..."
