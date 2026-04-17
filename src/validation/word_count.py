import re
from typing import Optional


class WordCountService:
    """Service for counting words in cleaned HTML content."""

    @staticmethod
    def count_words(html_content: Optional[str]) -> int:
        """Count words in HTML content after stripping HTML tags.

        Args:
            html_content: Input HTML content as a string.

        Returns:
            Integer word count. Returns 0 for empty/None input.
        """
        if not html_content or not html_content.strip():
            return 0

        text_only = re.sub(r"<[^>]+>", " ", html_content)
        text_only = re.sub(
            r"<(script|style)[^>]*>.*?</\\1>", " ", text_only, flags=re.DOTALL
        )
        text_only = re.sub(
            r"<(script|style)[^>]*>.*?</\1>", " ", text_only, flags=re.DOTALL
        )
        text_only = re.sub(r"&\w+;", " ", text_only)
        words = [word for word in text_only.split() if word]

        return len(words)


class WordCountValidator:
    """Validator that checks content meets word count requirements."""

    def __init__(self, min_words: int = 0, max_words: Optional[int] = None):
        """Initialize validator with word count thresholds.

        Args:
            min_words: Minimum required word count.
            max_words: Maximum allowed word count (optional).
        """
        self.min_words = min_words
        self.max_words = max_words

    def validate(self, html_content: str) -> dict:
        """Validate HTML content against word count requirements.

        Args:
            html_content: Input HTML content to validate.

        Returns:
            Dictionary containing validation result and word count metrics.
        """
        self.word_count = WordCountService.count_words(html_content)

        meets_min = self.word_count >= self.min_words
        meets_max = self.max_words is None or self.word_count <= self.max_words

        is_valid = meets_min and meets_max

        return {
            "is_valid": is_valid,
            "word_count": self.word_count,
            "min_words": self.min_words,
            "max_words": self.max_words,
            "meets_min": meets_min,
            "meets_max": meets_max,
            "errors": self._build_errors(meets_min, meets_max),
        }

    def _build_errors(self, meets_min: bool, meets_max: bool) -> list:
        """Build list of validation error messages."""
        errors = []
        if not meets_min:
            errors.append(
                f"Word count {self.word_count} is below minimum {self.min_words}."
            )
        if not meets_max:
            errors.append(
                f"Word count {self.word_count} exceeds maximum {self.max_words}."
            )
        return errors
