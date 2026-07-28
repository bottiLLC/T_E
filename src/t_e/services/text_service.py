
import structlog

log = structlog.get_logger()


class TextService:
    @staticmethod
    def count_characters(text: str) -> int:
        return len(text)

    @staticmethod
    def count_lines(text: str) -> int:
        if not text:
            return 0
        return text.count("\n") + 1

    @staticmethod
    def replace_all(content: str, query: str, replacement: str) -> tuple[str, int]:
        log.info("replace_all_start", query_len=len(query), replacement_len=len(replacement))
        if not query:
            return content, 0

        count = content.count(query)
        new_content = content.replace(query, replacement)
        log.info("replace_all_complete", count=count)
        return new_content, count
