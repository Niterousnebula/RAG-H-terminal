def clean_text(text: str) -> str:
    """
    Basic cleanup for PDF text
    """
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text


def chunk_text(text: str, chunk_size=500, overlap=100):
    """
    Split text into overlapping chunks
    """
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start += (chunk_size - overlap)

    return chunks