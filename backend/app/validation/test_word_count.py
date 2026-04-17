import unittest
from app.validation.word_count import WordCountService, WordCountValidator


class TestWordCountService(unittest.TestCase):
    """Unit tests for WordCountService."""

    def test_empty_string_returns_zero(self):
        self.assertEqual(WordCountService.count_words(""), 0)

    def test_none_returns_zero(self):
        self.assertEqual(WordCountService.count_words(None), 0)

    def test_whitespace_only_returns_zero(self):
        self.assertEqual(WordCountService.count_words("   "), 0)

    def test_simple_text_count(self):
        self.assertEqual(WordCountService.count_words("hello world"), 2)

    def test_text_with_html_tags(self):
        html = "<p>hello <strong>world</strong></p>"
        self.assertEqual(WordCountService.count_words(html), 2)

    def test_html_with_attributes(self):
        html = '<a href="https://example.com">link</a> text'
        self.assertEqual(WordCountService.count_words(html), 2)

    def test_numeric_words(self):
        self.assertEqual(WordCountService.count_words("123 456 789"), 3)

    def test_with_complex_html(self):
        html = """
        <div>
            <h1>Title</h1>
            <p>This is a paragraph with <strong>bold</strong> and <i>italic</i> text.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <style>
                .red { color: red; }
            </style>
            <script>
                console.log("This should not be counted");
            </script>
            <!-- This is a comment -->
        </div>
        """
        self.assertEqual(WordCountService.count_words(html), 13)


class TestWordCountValidator(unittest.TestCase):
    """Unit tests for WordCountValidator."""

    def test_valid_within_range(self):
        validator = WordCountValidator(min_words=1, max_words=100)
        result = validator.validate("hello world")
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["word_count"], 2)

    def test_below_minimum(self):
        validator = WordCountValidator(min_words=5, max_words=100)
        result = validator.validate("hi")
        self.assertFalse(result["is_valid"])
        self.assertIn("below minimum", result["errors"][0])

    def test_above_maximum(self):
        validator = WordCountValidator(min_words=0, max_words=5)
        long_text = " ".join([f"word{i}" for i in range(10)])
        result = validator.validate(long_text)
        self.assertFalse(result["is_valid"])
        self.assertIn("exceeds maximum", result["errors"][0])

    def test_no_maximum(self):
        validator = WordCountValidator(min_words=1, max_words=None)
        long_text = " ".join([f"word{i}" for i in range(100)])
        result = validator.validate(long_text)
        self.assertTrue(result["is_valid"])

    def test_exact_boundaries(self):
        validator = WordCountValidator(min_words=3, max_words=3)
        result = validator.validate("one two three")
        self.assertTrue(result["is_valid"])

    def test_empty_content(self):
        validator = WordCountValidator(min_words=0, max_words=10)
        result = validator.validate("")
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["word_count"], 0)


if __name__ == "__main__":
    unittest.main()
