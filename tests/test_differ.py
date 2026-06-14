from src.differ import compute_diff


def test_identical_content_returns_none():
    content = "<html><body>Hello</body></html>"
    assert compute_diff(content, content) is None


def test_different_content_returns_diff():
    previous = "<html><body>Old content</body></html>"
    current = "<html><body>New content</body></html>"
    result = compute_diff(previous, current)
    assert result is not None
    assert "Old content" in result
    assert "New content" in result


def test_empty_to_content():
    result = compute_diff("", "<html><body>New</body></html>")
    assert result is not None


def test_content_to_empty():
    result = compute_diff("<html><body>Old</body></html>", "")
    assert result is not None
