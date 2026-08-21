from app.ml.preprocessing import preprocess_text


def test_preprocess_lowercase_and_trim():
    result = preprocess_text("  Hello   WORLD  ")
    assert result == "hello world"


def test_preprocess_keeps_email_chars():
    result = preprocess_text("Win $5000! Contact us@mail.com")
    assert "@" in result
    assert "$" in result


def test_preprocess_none_returns_empty():
    assert preprocess_text(None) == ""
