import re


def preprocess_text(text: str) -> str:
    """
    Chuẩn hóa nội dung email trước khi đưa vào TF-IDF.

    - Chuyển về lowercase
    - Chuẩn hóa whitespace
    - Loại bỏ một số ký tự đặc biệt
    """

    if text is None:
        return ""

    text = text.lower()

    # Chuẩn hóa whitespace
    text = re.sub(r"\s+", " ", text)

    # Giữ chữ, số và một số ký tự thường gặp trong email
    text = re.sub(r"[^a-z0-9$%@.!?\s]", " ", text)

    # Chuẩn hóa whitespace lần cuối
    text = re.sub(r"\s+", " ", text).strip()

    return text