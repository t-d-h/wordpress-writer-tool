import unittest
from src.validation.section_count import SectionCountValidator


class TestSectionCountValidator(unittest.TestCase):
    """Unit tests for SectionCountValidator."""

    def test_valid_within_range(self):
        validator = SectionCountValidator(min_sections=1, max_sections=5)
        result = validator.validate(["section1", "section2"])
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["section_count"], 2)

    def test_below_minimum(self):
        validator = SectionCountValidator(min_sections=3, max_sections=5)
        result = validator.validate(["section1"])
        self.assertFalse(result["is_valid"])
        self.assertIn("below minimum", result["errors"][0])

    def test_above_maximum(self):
        validator = SectionCountValidator(min_sections=1, max_sections=2)
        result = validator.validate(["section1", "section2", "section3"])
        self.assertFalse(result["is_valid"])
        self.assertIn("exceeds maximum", result["errors"][0])

    def test_no_maximum(self):
        validator = SectionCountValidator(min_sections=1, max_sections=None)
        result = validator.validate(["section1"] * 10)
        self.assertTrue(result["is_valid"])

    def test_exact_boundaries(self):
        validator = SectionCountValidator(min_sections=3, max_sections=3)
        result = validator.validate(["section1", "section2", "section3"])
        self.assertTrue(result["is_valid"])

    def test_empty_list(self):
        validator = SectionCountValidator(min_sections=0, max_sections=5)
        result = validator.validate([])
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["section_count"], 0)


if __name__ == "__main__":
    unittest.main()
