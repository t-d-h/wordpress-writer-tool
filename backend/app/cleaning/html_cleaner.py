from typing import Optional

from bs4 import BeautifulSoup


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

        soup = BeautifulSoup(html_content, "lxml")

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Get text
        text = soup.get_text()

        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = "\n".join(chunk for chunk in chunks if chunk)

        return text
