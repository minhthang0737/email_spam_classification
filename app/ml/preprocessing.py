import re
import unicodedata


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

    # Keep letters and numbers from every language, including combining marks
    # used by decomposed Unicode text, plus common email characters.
    text = "".join(
        char if (
            char.isalnum()
            or char.isspace()
            or unicodedata.category(char).startswith("M")
            or char in "$%@.!?"
        ) else " "
        for char in text
    )

    # Chuẩn hóa whitespace lần cuối
    text = re.sub(r"\s+", " ", text).strip()

    return text
