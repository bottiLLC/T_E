"""Tests for TextService counting and replacement operations."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from t_e.services.text_service import TextService


@pytest.mark.parametrize(
    ("input_text", "expected_count"),
    [
        ("", 0),
        ("abc", 3),
        ("あいうえお", 5),
        ("a\nb\n", 4),
        ("🍎✨🐍", 3),
    ],
)
def test_count_characters_parametrized(input_text: str, expected_count: int) -> None:
    """Verify character count calculation across diverse input partitions."""
    # Arrange & Act
    actual_count = TextService.count_characters(input_text)

    # Assert
    assert actual_count == expected_count


@pytest.mark.parametrize(
    ("input_text", "expected_lines"),
    [
        ("", 0),
        ("hello", 1),
        ("hello\nworld", 2),
        ("a\nb\nc\n", 4),
        ("line1\r\nline2", 2),
    ],
)
def test_count_lines_parametrized(input_text: str, expected_lines: int) -> None:
    """Verify line count calculation including newline boundary cases."""
    # Arrange & Act
    actual_lines = TextService.count_lines(input_text)

    # Assert
    assert actual_lines == expected_lines


def test_replace_all_multiple_occurrences() -> None:
    """Verify replacing multiple occurrences of a target query string."""
    # Arrange
    content = "apple banana apple cherry apple"
    query = "apple"
    replacement = "orange"

    # Act
    new_content, count = TextService.replace_all(content, query, replacement)

    # Assert
    assert new_content == "orange banana orange cherry orange"
    assert count == 3


def test_replace_all_empty_query_returns_original() -> None:
    """Verify empty query string returns unchanged text without replacement."""
    # Arrange
    content = "some content"
    query = ""
    replacement = "replacement"

    # Act
    new_content, count = TextService.replace_all(content, query, replacement)

    # Assert
    assert new_content == content
    assert count == 0


@pytest.mark.fuzz
@given(content=st.text(), query=st.text(min_size=1), replacement=st.text())
def test_replace_all_fuzzing(content: str, query: str, replacement: str) -> None:
    """Fuzz testing verifying replace_all preserves invariants across arbitrary inputs."""
    # Arrange & Act
    new_content, count = TextService.replace_all(content, query, replacement)

    # Assert
    assert isinstance(new_content, str)
    assert isinstance(count, int)
    assert count == content.count(query)
    if count == 0:
        assert new_content == content
