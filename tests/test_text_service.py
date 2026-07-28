import pytest
from hypothesis import given
from hypothesis import strategies as st

from t_e.services.text_service import TextService


def test_count_characters() -> None:
    assert TextService.count_characters("") == 0
    assert TextService.count_characters("abc") == 3
    assert TextService.count_characters("あいうえお") == 5
    assert TextService.count_characters("a\nb\n") == 4


def test_count_lines() -> None:
    assert TextService.count_lines("") == 0
    assert TextService.count_lines("hello") == 1
    assert TextService.count_lines("hello\nworld") == 2
    assert TextService.count_lines("a\nb\nc\n") == 4


def test_replace_all() -> None:
    content = "apple banana apple cherry apple"
    new_content, count = TextService.replace_all(content, "apple", "orange")

    assert new_content == "orange banana orange cherry orange"
    assert count == 3


def test_replace_all_empty_query() -> None:
    content = "some content"
    new_content, count = TextService.replace_all(content, "", "replacement")

    assert new_content == content
    assert count == 0


@pytest.mark.fuzz
@given(content=st.text(), query=st.text(min_size=1), replacement=st.text())
def test_replace_all_fuzzing(content: str, query: str, replacement: str) -> None:
    new_content, count = TextService.replace_all(content, query, replacement)

    assert isinstance(new_content, str)
    assert isinstance(count, int)
    assert count == content.count(query)
    if count == 0:
        assert new_content == content
