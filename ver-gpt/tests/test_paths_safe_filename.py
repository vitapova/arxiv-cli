from arxiv_cli.utils.paths import safe_filename


def test_safe_filename_basic():
    assert safe_filename("  hello world ") == "hello_world"


def test_safe_filename_strips_bad_chars():
    assert safe_filename("a/b:c") == "a_b_c"


def test_safe_filename_empty_fallback():
    assert safe_filename("   ") == "unknown"
