"""Text transformation and metric calculation service."""

from __future__ import annotations

import structlog

log = structlog.get_logger()


class TextService:
    """Service providing character/line calculation and string replacements."""

    @staticmethod
    def count_characters(text: str) -> int:
        """Calculate total character count of a given string.

        Args:
            text: Input string to measure.

        Returns:
            int: Total character count.
        """
        return len(text)

    @staticmethod
    def count_lines(text: str) -> int:
        """Calculate total line count of a given string.

        Args:
            text: Input string to measure.

        Returns:
            int: Total line count (0 for empty strings).
        """
        if not text:
            return 0
        return text.count("\n") + 1

    @staticmethod
    def replace_all(content: str, query: str, replacement: str) -> tuple[str, int]:
        """Replace all occurrences of query with replacement in target content.

        Args:
            content: Original text content.
            query: Target substring to search for.
            replacement: Replacement substring.

        Returns:
            tuple[str, int]: Modified text content and number of replacements made.
        """
        log.info(
            "replace_all_start",
            query_len=len(query),
            replacement_len=len(replacement),
        )
        if not query:
            return content, 0

        count = content.count(query)
        new_content = content.replace(query, replacement)
        log.info("replace_all_complete", count=count)
        return new_content, count
