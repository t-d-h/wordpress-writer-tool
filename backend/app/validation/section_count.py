from typing import List, Dict, Any, Optional


class SectionCountValidator:
    """Validates the number of sections in a list."""

    def __init__(
        self, min_sections: Optional[int] = None, max_sections: Optional[int] = None
    ):
        self.min_sections = min_sections
        self.max_sections = max_sections

    def validate(self, sections: List[Any]) -> Dict[str, Any]:
        """Validates the number of sections.

        Args:
            sections: A list of sections.

        Returns:
            A dictionary containing validation result and section count.
        """
        section_count = len(sections)
        errors = self._build_error_messages(section_count)

        return {
            "is_valid": not errors,
            "section_count": section_count,
            "errors": errors,
        }

    def _build_error_messages(self, section_count: int) -> List[str]:
        """Build list of validation error messages."""
        errors = []
        if self.min_sections is not None and section_count < self.min_sections:
            errors.append(
                f"Section count of {section_count} is below minimum of {self.min_sections}."
            )
        if self.max_sections is not None and section_count > self.max_sections:
            errors.append(
                f"Section count of {section_count} exceeds maximum of {self.max_sections}."
            )
        return errors
