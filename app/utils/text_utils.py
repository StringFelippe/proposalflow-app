def extract_between_keywords(text: str, start: str, end: str) -> str:
    start_index = text.find(start)

    if start_index == -1:
        return ""

    start_index += len(start)
    end_index = text.find(end, start_index)

    if end_index == -1:
        return text[start_index:].strip()

    return text[start_index:end_index].strip()