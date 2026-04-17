from typing import List, Dict, Any, Optional

from app.validation.word_count import WordCountValidator
from app.validation.section_count import SectionCountValidator


class ContentValidationService:
    """Service for validating post content."""

    def __init__(
        self,
        min_words: Optional[int] = None,
        max_words: Optional[int] = None,
        min_sections: Optional[int] = None,
        max_sections: Optional[int] = None,
    ):
        self.word_count_validator = WordCountValidator(
            min_words=min_words, max_words=max_words
        )
        self.section_count_validator = SectionCountValidator(
            min_sections=min_sections, max_sections=max_sections
        )

    def validate(self, html_content: str, sections: List[Any]) -> Dict[str, Any]:
        """Validate post content.

        Args:
            html_content: The HTML content of the post.
            sections: A list of sections.

        Returns:
            A dictionary containing the validation results.
        """
        word_count_result = self.word_count_validator.validate(html_content)
        section_count_result = self.section_count_validator.validate(sections)

        is_valid = word_count_result["is_valid"] and section_count_result["is_valid"]

        return {
            "is_valid": is_valid,
            "word_count": word_count_result,
            "section_count": section_count_result,
        }
