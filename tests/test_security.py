from services.security import safe_filename, safe_path, validate_http_url


def test_safe_filename_and_path(tmp_path):
    name = safe_filename("../secret/evil?.mp3")
    assert "/" not in name and "\\" not in name and ".." not in name
    assert str(safe_path(str(tmp_path), name)).startswith(str(tmp_path))


def test_url_validation():
    assert validate_http_url("https://www.youtube.com/watch?v=x")
    assert not validate_http_url("file:///etc/passwd")
