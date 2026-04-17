import re
from typing import Optional


class HtmlCleaningService:
    """Service for cleaning HTML content."""

    @staticmethod
    def clean_html(html_content: Optional[str]) -> str:
        """Clean HTML content by removing tags, scripts, styles, and comments.

        Args:
            html_content: Input HTML content as a string.

        Returns:
            Cleaned text content. Returns an empty string for empty/None input.
        """
        if not html_content or not html_content.strip():
            return ""

        # Remove script and style elements
        text_only = re.sub(
            r"<(script|style)[^>]*>.*?</\1>", " ", html_content, flags=re.DOTALL
        )
        # Remove HTML comments
        text_only = re.sub(r"<!--.*?-->", " ", text_only, flags=re.DOTALL)
        # Remove all other HTML tags
        text_only = re.sub(r"<[^>]+>", " ", text_only)
        # Remove HTML entities
        text_only = re.sub(r"&\w+;", " ", text_only)
        # Replace multiple spaces with a single space
        text_only = re.sub(r"\s+", " ", text_only).strip()

        return text_only
