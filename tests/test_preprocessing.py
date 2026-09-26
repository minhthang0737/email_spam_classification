from app.ml.preprocessing import preprocess_text


def test_preprocess_lowercase_and_trim():
    result = preprocess_text("  Hello   WORLD  ")
    assert result == "hello world"


def test_preprocess_keeps_email_chars():
    result = preprocess_text("Win $5000! Contact us@mail.com")
    assert "@" in result
    assert "$" in result


def test_preprocess_preserves_vietnamese_diacritics():
    result = preprocess_text("  Khuyến mãi! Tài khoản của bạn  ")
    assert result == "khuyến mãi! tài khoản của bạn"


def test_preprocess_preserves_decomposed_vietnamese_diacritics():
    import unicodedata

    decomposed = unicodedata.normalize("NFD", "thư rác")
    assert preprocess_text(decomposed) == decomposed.lower()


def test_preprocess_none_returns_empty():
    assert preprocess_text(None) == ""
